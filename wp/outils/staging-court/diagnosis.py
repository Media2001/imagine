"""Diagnostic opérateur inerte : une lecture de l'archive, aucune extraction."""
import importlib.util
import json
from pathlib import Path
import re
from archive import Findings, Refusal, audit
from core_source import select_version, numeric

HERE = Path(__file__).resolve().parent
DANGER = re.compile(rb'[spr]k_(?:live|test)_|whsec_|xkeysib[-_]|(?<![a-z0-9])(?:cus|pm|src|seti|pi|ch|tok|ba)_[a-z0-9_-]+|(?<![a-z0-9])[BI]-[A-Z0-9]{6,}', re.I)
SENSITIVE_VALUE = re.compile(rb'''(?:secret(?:_key)?|api_?key|password|smtp_pass|access_token|refresh_token|client_secret|consumer_secret|authorization)[\s'"]*(?:=>|[:=,])[\s]*['"][^'"\r\n]+''', re.I)
PERSONAL = re.compile(r'email|e_mail|phone|telephone|mobile|name|nom|address|adresse|(?:^|_)ip(?:$|_)|ip_address|(?:^|_)(?:company|city|postcode|state|vat|tax_id|company_number|business_number|siret|iban|bic|nickname|user_agent|customer_note|order_key|cart_hash|shipping_packages)(?:$|_)', re.I)


def parser_module():
    path = HERE.parent / 'staging-wp-integration/worker/worker.py'
    if not path.is_file():
        path = HERE / 'legacy_importer.py'
    spec = importlib.util.spec_from_file_location('a01_diagnostic_sql', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.CREATE_WORDS.update({'ON', 'UPDATE', 'UTF8MB3_GENERAL_CI'})
    return module


def catalogue():
    text = (HERE.parent / 'staging/schema.php').read_text(encoding='utf-8')
    return {key: value.split() for key, value in re.findall(r"^\s*'([a-z0-9_]+)' => '([A-Za-z0-9_ ]+)',?$", text, re.M)}


def sql_diagnosis(payload, findings, decisions):
    """Tokenise literals without executing SQL; validate every framed statement.

    Schema identifiers come only from CREATE tokens, never string contents.
    Original-source secrets are not claimed to be post-neutralisation residue.
    """
    if payload is None:
        findings.add('SQL_UNAVAILABLE')
        return
    try:
        text = payload.decode('utf-8', 'strict')
    except UnicodeError:
        findings.add('SQL_ENCODING')
        return
    module = parser_module()
    groups, group, position = [], [], 0
    while position < len(text):
        match = module.TOKEN.match(text, position)
        if match is None:
            findings.add('SQL_GRAMMAR')
            # Broken grammar cannot authorise anything. Continue only at the
            # next explicit delimiter, and report that SQL coverage is partial.
            findings.add('SQL_ANALYSIS_PARTIAL', blocking=False)
            end = text.find(';', position)
            if end < 0:
                break
            position = end + 1
            group = []
            continue
        position = match.end()
        if match.lastgroup in ('space', 'comment'):
            continue
        if match.group() == ';':
            if group:
                groups.append(group)
            group = []
        else:
            group.append((match.lastgroup, match.group()))
    if group:
        findings.add('SQL_TERMINATOR')
        groups.append(group)
    schemas, engines, inserts, canonical = {}, {}, [], []
    bad_statement = False
    for tokens in groups:
        values = [value.upper() if kind == 'word' else value for kind, value in tokens]
        statement = ' '.join(values)
        if values[:2] == ['CREATE', 'TABLE']:
            statement = re.sub(r'(\) ENGINE = (?:INNODB|MYISAM|ARIA|MEMORY)) AUTO_INCREMENT = ([0-9]+) (DEFAULT CHARSET = [A-Z0-9_]+(?: COLLATE = [A-Z0-9_]+)?)$', r'\1 \3 AUTO_INCREMENT = \2', statement)
        canonical.append(statement)
        try:
            module.sql_plan((statement + ';').encode(), table_engines={'INNODB', 'MYISAM', 'ARIA', 'MEMORY'})
        except module.Refusal as error:
            if str(error) not in ('SQL_PREFIX', 'SQL_TABLE'):
                findings.add(str(error))
                bad_statement = True
        except (IndexError, ValueError):
            findings.add('SQL_GRAMMAR')
            bad_statement = True
        if len(tokens) < 3 or tokens[2][0] != 'id':
            continue
        table = tokens[2][1][1:-1]
        if values[:2] == ['CREATE', 'TABLE']:
            columns, depth, column_start = [], 0, False
            for kind, value in tokens[3:]:
                if value == '(':
                    depth += 1
                    if depth == 1:
                        column_start = True
                elif value == ')':
                    depth -= 1
                    if depth == 0:
                        break
                elif value == ',' and depth == 1:
                    column_start = True
                elif depth == 1 and column_start:
                    if kind == 'id':
                        columns.append(value[1:-1])
                    column_start = False
            if table in schemas:
                findings.add('SQL_TABLE', table=table, columns=columns)
            schemas[table] = columns
            match = re.search(r'\bENGINE = ([A-Z0-9_]+)', statement)
            if match:
                engines[table] = match[1]
        elif values[:2] == ['INSERT', 'INTO']:
            columns = []
            if len(tokens) > 3 and tokens[3][1] == '(':
                for kind, value in tokens[4:]:
                    if value == ')':
                        break
                    if kind == 'id':
                        columns.append(value[1:-1])
            inserts.append((table, columns, tokens))
    prefixes = [table[:-7] for table in schemas if table.endswith('_options')]
    prefix = prefixes[0] if len(prefixes) == 1 else None
    if prefix is None or not prefix or any(not table.startswith(prefix) for table in schemas):
        findings.add('SQL_PREFIX')
    if not bad_statement:
        try:
            module.sql_plan((';\n'.join(canonical) + ';').encode(), table_engines={'INNODB', 'MYISAM', 'ARIA', 'MEMORY'})
        except module.Refusal as error:
            if str(error) not in findings.rules:
                findings.add(str(error))
        except (IndexError, ValueError):
            findings.add('SQL_GRAMMAR')
    known = catalogue()
    for table, columns in schemas.items():
        kind = table[len(prefix):] if prefix and table.startswith(prefix) else ''
        if kind not in known:
            findings.add('TABLE_INCONNUE_CONSERVEE', blocking=False, table=table, columns=columns)
            personal = [c for c in columns if PERSONAL.search(c)]
            if personal and table not in decisions:
                findings.add('TABLE_PERSONNELLE_A_TRANCHER', table=table, columns=personal)
        else:
            extra = [c for c in columns if c not in known[kind]]
            if extra:
                findings.add('COLONNES_INCONNUES_CONSERVEES', blocking=False, table=table, columns=extra)
        if engines.get(table) != 'INNODB':
            findings.add('NON_INNODB_TABLE', blocking=False, table=table, columns=columns)
    if prefix:
        for kind in ('options', 'users', 'usermeta', 'posts', 'postmeta', 'comments'):
            if prefix + kind not in schemas:
                findings.add('SCHEMA_INCOMPLET', table=prefix + kind, columns=[])
    for table, decision in decisions.items():
        valid = (table in schemas and (not prefix or table[len(prefix):] not in known)
                 and isinstance(decision, dict) and not set(decision) - {'action', 'columns'}
                 and decision.get('action') in ('garder', 'vider', 'anonymiser'))
        if valid and decision['action'] == 'anonymiser':
            cols = decision.get('columns')
            valid = isinstance(cols, list) and bool(cols) and all(isinstance(c, str) and c in schemas[table] for c in cols)
        elif valid:
            valid = 'columns' not in decision
        if not valid:
            findings.add('DECISION_INVALIDE')
    option_names = set()
    for table, columns, tokens in inserts:
        if table not in schemas:
            findings.add('SQL_TABLE', table=table, columns=columns)
        active_columns = columns or schemas.get(table, [])
        # Parse only literal rows already admitted by the closed grammar.
        values_at = next((i for i, token in enumerate(tokens) if token[0] == 'word' and token[1].upper() == 'VALUES'), len(tokens))
        row = None
        for kind, value in tokens[values_at + 1:]:
            if value == '(':
                row = []
            elif value == ')' and row is not None:
                if len(row) != len(active_columns):
                    findings.add('SQL_INSERT_COLUMN_COUNT', table=table, columns=active_columns)
                if prefix and table == prefix + 'options' and 'option_name' in active_columns:
                    index = active_columns.index('option_name')
                    if index < len(row):
                        key = row[index]
                        if key in option_names:
                            findings.add('OPTION_DUPLIQUEE', table=table, columns=['option_name'])
                        option_names.add(key)
                row = None
            elif row is not None and kind in ('string', 'number', 'word'):
                if kind == 'string':
                    value = re.sub(r'\\\\(.)', lambda m: {'n':'\n', 'r':'\r', 't':'\t', '0':'\0', 'b':'\b', 'Z':'\x1a'}.get(m[1], m[1]), value[1:-1].replace("''", "'"), flags=re.S)
                row.append(value)
        # Count source literals, never emit them. Table/column schema only.
        for kind, value in tokens:
            if kind == 'string' and DANGER.search(value.encode()):
                findings.add('SOURCE_SECRET_NEUTRALISABLE', blocking=False, table=table, columns=columns or schemas.get(table, []))
    if prefix and prefix + 'options' in schemas:
        for name in ('home', 'siteurl'):
            if name not in option_names:
                findings.add('URL_ABSENTE', table=prefix + 'options', columns=['option_name', 'option_value'])


def diagnose(stream, expected='6.9.1', decisions=None, php='8.2'):
    findings = Findings()
    if decisions is None:
        decisions = {}
    if not isinstance(decisions, dict):
        findings.add('DECISIONS_REFUSED')
        decisions = {}
    # Only current entry's bounded prefix/tail are retained; no file payloads.
    tail, head, dangerous = b'', b'', False
    plugins = []
    def observe(relative, data, final):
        nonlocal tail, head, dangerous
        if not final:
            dangerous |= bool(DANGER.search(tail + data) or SENSITIVE_VALUE.search(tail + data))
            tail = (tail + data)[-256:]
            head = (head + data[:8192])[:8192]
            return
        if dangerous and relative != 'database.sql':
            findings.add('SECRET_OU_IDENTIFIANT', relative)
        if relative.startswith('plugins/') and relative.endswith('.php'):
            plugins.append((relative, head.decode('utf-8', 'replace').replace('\r', '\n')))
        tail, head, dangerous = b'', b'', False
    scan = audit(stream, retain_sql=True, on_chunk=observe)
    # Preserve traversal order and precise original counts from the archive pass.
    archive_rules = scan['report']['rules']
    findings.rules = {**{r['code']: r for r in archive_rules}, **findings.rules}
    version = None
    expected_valid = isinstance(expected, str) and re.fullmatch(r'[0-9]+\.[0-9]+(?:\.[0-9]+)?', expected)
    if not expected_valid:
        findings.add('EXPECTED_CORE_VERSION_REFUSED')
    try:
        version = select_version(scan['package'])
        if expected_valid and version != expected:
            findings.add('SOURCE_EXPECTED_CORE_VERSION_MISMATCH')
    except Refusal as error:
        findings.add(str(error))
    except (AttributeError, IndexError, RecursionError):
        findings.add('SOURCE_CORE_METADATA_REFUSED')
    if scan['package'] is not None:
        try:
            metadata = json.loads(scan['package'])
            if isinstance(metadata, dict) and any(key in metadata for key in ('Multisite', 'Network')):
                findings.add('MULTISITE_METADATA_REVIEW_REQUIRED', blocking=False)
        except (ValueError, TypeError, RecursionError):
            pass
    sql_diagnosis(scan['sql'], findings, decisions)
    for relative, header in plugins:
        prefix = r'^(?:[ \t]*<\?php)?[ \t\/*#@]*'
        if not re.search(prefix + 'Plugin Name:', header, re.M | re.I):
            continue
        for field, current, code in [('Requires at least', version, 'PLUGIN_REQUIRES_NEWER_WORDPRESS'),
                                     ('Requires PHP', php, 'PLUGIN_REQUIRES_NEWER_PHP')]:
            match = re.search(prefix + field + r':[ \t]*([0-9]+\.[0-9]+(?:\.[0-9]+)?)[ \t]*(?:\*/)?[ \t]*$', header, re.M | re.I)
            if match and current and numeric(match[1]) > numeric(current):
                findings.add(code, relative, blocking=False)
    report = findings.report(scan['report']['entries'], scan['report']['complete'])
    report.update(mode='diagnose', core_versions={'source':version,'expected':expected if expected_valid else None}, read_only=True, created_sites=[], downloads=0, extracted_files=0,
                  status='REFUSED' if report['blockers'] else 'NO_STATIC_BLOCKER',
                  full_staging_ready=False,
                  deferred_checks=['TARGET_FILESYSTEM_CASE_PROBE_BEFORE_RESTORE', 'PUBLIC_CORE_AVAILABILITY_AND_EXACT_VERSION',
                                   'DATABASE_ENGINE_AND_CONSTRAINT_RUNTIME', 'POST_NEUTRALISATION_RESIDUE',
                                   'PLUGIN_BOOTSTRAP_AND_NATIVE_RUNTIME', 'PUBLICATION_AND_HTTP_PROBE'])
    return report


def diagnose_path(path, expected='6.9.1', decisions_path=None, php='8.2'):
    try:
        source = Path(path)
        if source.is_symlink() or not source.is_file() or source.suffix.lower() != '.wpress':
            raise Refusal('ARCHIVE_SOURCE_REFUSED')
        decisions = None
        if decisions_path:
            try:
                decisions = json.loads(Path(decisions_path).read_text(encoding='utf-8'))
            except (ValueError, OSError):
                decisions = []  # diagnosed, never copied into output
        with source.open('rb') as stream:
            return diagnose(stream, expected, decisions, php)
    except (OSError, Refusal):
        findings = Findings()
        findings.add('ARCHIVE_SOURCE_REFUSED')
        result = findings.report(complete=False)
        result.update(mode='diagnose', read_only=True, created_sites=[], downloads=0, extracted_files=0,
                      status='REFUSED', full_staging_ready=False)
        return result
