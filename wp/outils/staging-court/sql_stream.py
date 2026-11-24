"""Bounded SQL framing/validation; never resynchronise inside a literal."""
import re
from archive import Refusal

MAX_STATEMENT = 16 * 1024**2
MARK = re.compile(rb"[;'\"`#]|--|/\*")
QUOTED = {ord("'"): re.compile(rb"'(?:[^'\\]|\\.|'')*'"),
          ord('"'): re.compile(rb'"(?:[^"\\]|\\.|"")*"'),
          ord('`'): re.compile(rb'`[^`]*`')}


class Framer:
    def __init__(self, consume, limit=MAX_STATEMENT):
        self.consume, self.limit = consume, limit
        self.buffer = b''
        self.position = 0
        self.peak = 0

    def feed(self, data):
        self.buffer += data
        while True:
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
        if tail.strip():
            raise Refusal('SQL_TERMINATOR')


def canonical(tokens):
    values = [v.upper() if k == 'word' else v for k, v in tokens]
    statement = ' '.join(values)
    if values[:2] == ['CREATE', 'TABLE']:
        statement = re.sub(r'(\) ENGINE = (?:INNODB|MYISAM|ARIA|MEMORY)) AUTO_INCREMENT = ([0-9]+) (DEFAULT CHARSET = [A-Z0-9_]+(?: COLLATE = [A-Z0-9_]+)?)$', r'\1 \3 AUTO_INCREMENT = \2', statement)
    return statement + ';\n'


class Validator:
    """Retain schema identifiers/DDL only, never rows or whole-dump tokens."""
    def __init__(self, module, findings=None, sink=None):
        self.module, self.findings, self.sink = module, findings, sink
        self.schemas, self.engines, self.inserts = {}, {}, set()
        self.option_names = set()
        self.prefix = None
        self.transaction = False
        self.statements = self.bytes = 0

    def error(self, code, **schema):
        if self.findings is None:
            raise Refusal(code)
        self.findings.add(code, **schema)

    def statement(self, payload):
        self.bytes += len(payload); self.statements += 1
        try:
            text = payload.decode('utf-8', 'strict')
        except UnicodeError:
            self.error('SQL_ENCODING'); return
        tokens, pos = [], 0
        while pos < len(text):
            match = self.module.TOKEN.match(text, pos)
            if not match:
                self.error('SQL_GRAMMAR')
                if self.findings:
                    self.findings.add('SQL_ANALYSIS_PARTIAL', blocking=False)
                return
            if match.lastgroup not in ('space', 'comment') and match.group() != ';':
                tokens.append((match.lastgroup, match.group()))
            pos = match.end()
        if not tokens:
            return
        values = [v.upper() if k == 'word' else v for k, v in tokens]
        sql = canonical(tokens)
        if values in (['START', 'TRANSACTION'], ['COMMIT']):
            starting = values == ['START', 'TRANSACTION']
            if starting == self.transaction:
                self.error('SQL_TRANSACTION')
            self.transaction = starting
            if self.sink:
                self.sink.write(sql.encode())
            return
        try:
            self.module.sql_plan(sql.encode(), table_engines={'INNODB', 'MYISAM', 'ARIA', 'MEMORY'})
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
                elif row is not None and kind in ('string', 'number', 'word'):
                    row.append(value[1:-1].replace("''", "'") if kind == 'string' else value)
            if self.findings:
                from diagnosis import DANGER
                for kind, value in tokens:
                    if kind == 'string' and DANGER.search(value.encode()):
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
        return {'prefix': self.prefix, 'table_engines': self.engines, 'statements_count': self.statements}


def validate_file(path, module, destination):
    with open(path, 'rb') as source, open(destination, 'xb') as sink:
        validator = Validator(module, sink=sink)
        framer = Framer(validator.statement)
        while data := source.read(1024 * 1024):
            framer.feed(data)
        framer.finish()
        return validator.finish()
