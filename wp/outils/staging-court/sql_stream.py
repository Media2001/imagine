"""Bounded SQL framing/validation; never resynchronise inside a literal."""
import re
from archive import Refusal
from table_policy import Policy
from sql_compat import compatible_tokens, unwrap_setting, mode_statement

INSERT_HEAD = re.compile(rb"\s*(?:(?:--|\#)[^\n]*\n\s*)*INSERT\s+INTO\s+`([A-Za-z0-9_]+)`\s*", re.I)
SKIP_MARK = re.compile(rb"['\"`\\;#/-]")
HEX = re.compile(r"(?:0[xX][0-9a-fA-F]+|[xX]'(?:[0-9a-fA-F]{2})*')")
BINARY = re.compile(r"_binary\s*('(?:[^'\\]|\\.|'')*')", re.I | re.S)


def binary_hex(literal):
    raw = literal[1:-1].encode('utf-8', 'surrogateescape').replace(b"''", b"'")
    escapes = {b'0':b'\0', b'n':b'\n', b'r':b'\r', b't':b'\t', b'b':b'\b', b'Z':b'\x1a'}
    raw = re.sub(rb'\\(.)', lambda m: escapes.get(m[1], m[1]) if m[1] not in (b'%', b'_') else b'\\'+m[1], raw, flags=re.S)
    return '0x'+raw.hex() if raw else "X''"

MAX_STATEMENT = 64 * 1024**2
MARK = re.compile(rb"[;'\"`#]|--|/\*")
QUOTED = {ord("'"): re.compile(rb"'(?:[^'\\]+|\\.|'')*'", re.S),
          ord('"'): re.compile(rb'"(?:[^"\\]+|\\.|"")*"', re.S),
          ord('`'): re.compile(rb'`[^`]*`')}


class Framer:
    def __init__(self, consume, limit=MAX_STATEMENT):
        self.consume, self.limit = consume, limit
        self.buffer = b''
        self.position = 0
        self.peak = 0
        self.owner = getattr(consume, '__self__', None)
        self.skipping = False
        self.quote = None
        self.escape = False
        self.outside_dash = False

    def discard(self, data):
        # Lexical framing only: no decoding, value grammar, scanning or retention.
        if self.outside_dash and data:
            self.outside_dash = False
            if data.startswith(b'-'): raise Refusal('SQL_INSERT_FRAMING')
        at = 0
        while at < len(data):
            if self.escape:
                self.escape = False
                at += 1
                continue
            match = SKIP_MARK.search(data, at)
            if match is None:
                return b''
            c = match.group()
            at = match.end()
            if self.quote:
                if c == b'\\': self.escape = True
                elif c == self.quote: self.quote = None
            elif c in (b"'", b'"', b'`'):
                self.quote = c
            elif c == b';':
                self.skipping = False
                return data[at:]
            elif c == b'-':
                if data[at:at+1] == b'-': raise Refusal('SQL_INSERT_FRAMING')
                self.outside_dash = at == len(data)
            elif c in (b'#', b'/'):
                # Exported VALUES contain no SQL comments. Keep an ambiguous
                # framing closed, rather than resynchronising inside a comment.
                raise Refusal('SQL_INSERT_FRAMING')
        return b''

    def feed(self, data):
        if self.skipping:
            data = self.discard(data)
        self.buffer += data
        while True:
            head = INSERT_HEAD.match(self.buffer)
            if head and self.owner and hasattr(self.owner, 'skip_insert') and self.owner.skip_insert(head[1].decode()):
                self.skipping = True
                self.quote = None
                self.escape = False
                self.buffer = self.discard(self.buffer[head.end():])
                self.position = 0
                if self.skipping: break
                continue
            match = MARK.search(self.buffer, self.position)
            if match is None:
                # Keep one byte for a delimiter split across feed boundaries.
                self.position = max(0, len(self.buffer) - 1)
                break
            pos, token = match.start(), match.group()
            if token == b';':
                end = match.end()
                if end > self.limit:
                    raise Refusal('SQL_STATEMENT_LIMIT')
                self.consume(self.buffer[:end])
                self.buffer = self.buffer[end:]
                self.position = 0
            elif token in (b"'", b'"', b'`'):
                quoted = QUOTED[token[0]].match(self.buffer, pos)
                if quoted is None:
                    self.position = pos
                    break
                # A closing quote at a chunk boundary might be a doubled quote.
                if quoted.end() == len(self.buffer):
                    self.position = pos
                    break
                self.position = quoted.end()
            elif token in (b'#', b'--'):
                end = self.buffer.find(b'\n', pos)
                if end < 0:
                    self.position = pos
                    break
                self.position = end + 1
            else:
                end = self.buffer.find(b'*/', pos + 2)
                if end < 0:
                    self.position = pos
                    break
                # Block/executable comments are refused by closed grammar.
                self.position = end + 2
        self.peak = max(self.peak, len(self.buffer))
        if len(self.buffer) > self.limit:
            raise Refusal('SQL_STATEMENT_LIMIT')

    def finish(self):
        # Only whitespace/ordinary line comments may follow the final ';'.
        tail = re.sub(rb'(?:--|#)[^\n]*(?:\n|$)', b'', self.buffer)
        if self.skipping or tail.strip():
            raise Refusal('SQL_TERMINATOR')


def canonical(tokens):
    values = [v.upper() if k == 'word' else v.replace('\r', r'\r').replace('\n', r'\n').replace('\0', r'\0') if k=='string' else v for k, v in tokens]
    statement = ' '.join(values)
    if values[:2] == ['CREATE', 'TABLE']:
        statement = re.sub(r'(\) ENGINE = (?:INNODB|MYISAM|ARIA|MEMORY)) AUTO_INCREMENT = ([0-9]+) (DEFAULT CHARSET = [A-Z0-9_]+(?: COLLATE = [A-Z0-9_]+)?)$', r'\1 \3 AUTO_INCREMENT = \2', statement)
    return statement + ';\n'


class Validator:
    """Retain schema identifiers/DDL only, never rows or whole-dump tokens."""
    def __init__(self, module, findings=None, sink=None, decisions=None, schema_only=False, prefix=None):
        self.module, self.findings, self.sink = module, findings, sink
        self.schemas, self.engines, self.inserts = {}, {}, set()
        self.option_names = set()
        self.prefix = prefix
        self.schema_only = schema_only
        self.transaction = False
        self.statements = self.bytes = 0
        self.skipped_inserts = 0
        self.compatibility = []
        self.source_sql_mode = None
        from diagnosis import catalogue
        self.policy = Policy(catalogue(), decisions)

    def inferred_prefix(self, table):
        if self.prefix: return self.prefix
        for kind in sorted(self.policy.known, key=len, reverse=True):
            if table.endswith('_' + kind): return table[:-len(kind)]
        return None

    def skip_insert(self, table):
        if not self.schema_only:
            if table not in self.schemas: return False
            decision, _ = self.policy.resolve(table, self.inferred_prefix(table))
            if decision.get('action') != 'vider': return False
        self.inserts.add(table)
        self.skipped_inserts += 1
        self.statements += 1
        return True

    def error(self, code, **schema):
        if self.findings is None:
            raise Refusal(code, schema or getattr(self, 'current_coordinate', None))
        self.findings.add(code, **schema)

    def statement(self, payload):
        self.bytes += len(payload); self.statements += 1
        payload = unwrap_setting(payload)
        from diagnostics import statement_coordinate
        self.current_coordinate = statement_coordinate(payload[:4096])
        if re.match(rb'\s*(?:CREATE\s+(?:DEFINER|VIEW|TRIGGER|PROCEDURE|FUNCTION|EVENT)|DELIMITER)\b', payload, re.I):
            self.error('SQL_EXECUTABLE_OBJECT_REFUSED')
            return
        text = payload.decode('utf-8', 'surrogateescape')
        tokens, pos = [], 0
        while pos < len(text):
            binary = BINARY.match(text, pos)
            if binary:
                tokens.append(('hex', binary_hex(binary[1])))
                pos = binary.end()
                continue
            hexadecimal = HEX.match(text, pos)
            if hexadecimal:
                tokens.append(('hex', hexadecimal[0]))
                pos = hexadecimal.end()
                continue
            match = re.compile(self.module.TOKEN.pattern.replace(r"[^'\\]", r"[^'\\]+"), re.S).match(text, pos)
            if not match:
                self.error('SQL_GRAMMAR')
                if self.findings:
                    self.findings.add('SQL_ANALYSIS_PARTIAL', blocking=False)
                return
            if match.lastgroup not in ('space', 'comment') and match.group() != ';':
                value = match.group()
                if match.lastgroup == 'string' and any(0xDC80 <= ord(c) <= 0xDCFF for c in value):
                    tokens.append(('hex', binary_hex(value)))
                else:
                    tokens.append((match.lastgroup, value))
            pos = match.end()
        if not tokens:
            return
        tokens, changes = compatible_tokens(tokens)
        for change in changes:
            if change not in self.compatibility: self.compatibility.append(change)
        values = [v.upper() if k == 'word' else v for k, v in tokens]
        sql = canonical(tokens)
        mode = mode_statement(tokens)
        if mode is not None:
            self.source_sql_mode = mode
            if self.sink: self.sink.write(sql.encode())
            return
        if values in (['START', 'TRANSACTION'], ['COMMIT']):
            starting = values == ['START', 'TRANSACTION']
            if starting == self.transaction:
                self.error('SQL_TRANSACTION')
            self.transaction = starting
            if self.sink:
                self.sink.write(sql.encode())
            return
        try:
            # Legacy closed grammar validates statement structure using inert
            # stand-ins only for the literal forms already lexed above.
            checked = canonical([('string', "'BLOB'") if k in ('hex','string') else (k, v) for k, v in tokens])
            if values[:2] == ['CREATE','TABLE']:
                self.module.CREATE_WORDS.update({'GENERATED','ALWAYS','AS','STORED','VIRTUAL','PERSISTENT','CHECK','JSON_VALID'})
                # Closed storage option; retain actual syntax in output while
                # adapting the older shared parser's suffix only in memory.
                checked = re.sub(r' ROW_FORMAT = (?:DYNAMIC|COMPACT|REDUNDANT|COMPRESSED|FIXED|DEFAULT)(?=\s*;)', '', checked)
            self.module.sql_plan(checked.encode(), table_engines={'INNODB', 'MYISAM', 'ARIA', 'MEMORY'})
        except self.module.Refusal as exc:
            if str(exc) not in ('SQL_PREFIX', 'SQL_TABLE'):
                table_at = 1 if values[0] == 'UPDATE' else 2
                schema = {'table': tokens[table_at][1][1:-1], 'columns': []} if len(tokens) > table_at and tokens[table_at][0] == 'id' else {}
                self.error(str(exc), **schema)
                return
        except (IndexError, ValueError):
            self.error('SQL_GRAMMAR'); return
        if values[:2] == ['CREATE', 'TABLE']:
            table = tokens[2][1][1:-1]
            if table in self.schemas:
                self.error('SQL_TABLE', table=table, columns=[])
            columns, depth, beginning = [], 0, False
            for kind, value in tokens[3:]:
                if value == '(':
                    depth += 1
                    if depth == 1: beginning = True
                elif value == ')':
                    depth -= 1
                    if depth == 0: break
                elif value == ',' and depth == 1:
                    beginning = True
                elif depth == 1 and beginning:
                    if kind == 'id': columns.append(value[1:-1])
                    beginning = False
            self.schemas[table] = columns
            if table.endswith('_options'):
                self.prefix = table[:-7]
            match = re.search(r'\bENGINE = ([A-Z0-9_]+)', sql)
            self.engines[table] = match[1] if match else None
        elif values[:2] == ['INSERT', 'INTO']:
            table = tokens[2][1][1:-1]
            self.inserts.add(table)
            columns = []
            if len(tokens) > 3 and tokens[3][1] == '(':
                for kind, value in tokens[4:]:
                    if value == ')': break
                    if kind == 'id': columns.append(value[1:-1])
            active = columns or self.schemas.get(table, [])
            at = next((i for i, t in enumerate(tokens) if t[0] == 'word' and t[1].upper() == 'VALUES'), len(tokens))
            row = None
            for kind, value in tokens[at + 1:]:
                if value == '(':
                    row = []
                elif value == ')' and row is not None:
                    if len(row) != len(active):
                        self.error('SQL_INSERT_COLUMN_COUNT', table=table, columns=active)
                    if table.endswith('_options') and 'option_name' in active:
                        i = active.index('option_name')
                        if i < len(row):
                            key = row[i]
                            if key in self.option_names:
                                self.error('OPTION_DUPLIQUEE', table=table, columns=['option_name'])
                            self.option_names.add(key)
                    row = None
                elif row is not None and kind in ('string', 'number', 'word', 'hex'):
                    row.append(value[1:-1].replace("''", "'") if kind == 'string' else value)
            if self.findings:
                from diagnosis import DANGER
                for kind, value in tokens:
                    if kind == 'string' and DANGER.search(value.encode('utf-8', 'surrogateescape')):
                        self.findings.add('SOURCE_SECRET_NEUTRALISABLE', blocking=False, table=table, columns=active)
        if self.sink:
            self.sink.write(sql.encode())

    def finish(self):
        if self.transaction:
            self.error('SQL_TRANSACTION')
        prefixes = [t[:-7] for t in self.schemas if t.endswith('_options')]
        self.prefix = prefixes[0] if len(prefixes) == 1 else None
        if not self.prefix or any(not t.startswith(self.prefix) for t in self.schemas):
            self.error('SQL_PREFIX')
        for table in self.inserts - self.schemas.keys():
            self.error('SQL_TABLE', table=table, columns=[])
        decisions = {table: self.policy.resolve(table, self.prefix)[0] for table in self.schemas
                     if (table[len(self.prefix):] if self.prefix else '') not in self.policy.known}
        return {'prefix': self.prefix, 'table_engines': self.engines, 'statements_count': self.statements,
                'compatibility':self.compatibility, 'source_sql_mode':self.source_sql_mode,
                'table_decisions': decisions, 'skipped_inserts': self.skipped_inserts,
                'table_policy_version': self.policy.data['version']}


def validate_file(path, module, destination, decisions=None):
    # First pass retains schema only and skips EVERY row lexically. The exact
    # options prefix is therefore known before choosing which INSERTs to keep,
    # even if a preceding unknown table happens to end in a catalogue suffix.
    with open(path, 'rb') as source:
        schema = Validator(module, schema_only=True)
        frame = Framer(schema.statement)
        while data := source.read(1024 * 1024): frame.feed(data)
        frame.finish()
        prefix = schema.finish()['prefix']
    with open(path, 'rb') as source, open(destination, 'xb') as sink:
        validator = Validator(module, sink=sink, decisions=decisions, prefix=prefix)
        framer = Framer(validator.statement)
        while data := source.read(1024 * 1024):
            framer.feed(data)
        framer.finish()
        plan = validator.finish()
        from sql_diagnostic import check_schema
        check_schema(validator, None)
        return plan
