"""Streaming schema-only SQL diagnostic on the existing closed grammar."""
from archive import Refusal
from sql_stream import Framer, Validator


class SQLAnalysis:
    def __init__(self, findings, decisions, schema_only=False, prefix=None):
        from diagnosis import parser_module
        self.findings, self.decisions = findings, decisions
        self.validator = Validator(parser_module(), findings=findings, decisions=decisions, schema_only=schema_only, prefix=prefix)
        self.framer = Framer(self.validator.statement)
        self.failed = False

    def feed(self, data):
        if self.failed: return
        try:
            self.framer.feed(data)
        except Refusal as exc:
            self.findings.add(str(exc)); self.failed = True
            self.findings.add('SQL_ANALYSIS_PARTIAL', blocking=False)

    def finish(self):
        f, v = self.findings, self.validator
        if not self.failed:
            try: self.framer.finish()
            except Refusal as exc: f.add(str(exc))
        v.finish()
        if not v.schema_only:
            check_schema(v, f)
        self.table_summary, self.unclassified = v.policy.summary(v.schemas, v.prefix)


def check_schema(v, f):
        from diagnosis import PERSONAL
        def error(code, **schema):
            if f is None: raise Refusal(code)
            f.add(code, **schema)
        prefix = v.prefix
        known = v.policy.known
        for table, columns in v.schemas.items():
            kind = table[len(prefix):] if prefix and table.startswith(prefix) else ''
            decision, family = v.policy.resolve(table, prefix)
            if kind not in known:
                if f:
                    f.add('TABLE_STRUCTURE_SEULE' if decision.get('action') == 'vider' else 'TABLE_DECISION_EXPLICITE', blocking=False, table=table, columns=columns)
                personal = [c for c in columns if PERSONAL.search(c)]
                if personal and decision.get('action') == 'garder':
                    error('TABLE_PERSONNELLE_A_TRANCHER', table=table, columns=personal)
            else:
                extra = [c for c in columns if c not in known[kind]]
                if extra and f: f.add('COLONNES_INCONNUES_CONSERVEES', blocking=False, table=table, columns=extra)
            if f and v.engines.get(table) != 'INNODB':
                f.add('NON_INNODB_TABLE', blocking=False, table=table, columns=columns)
        if prefix and f:
            for kind in ('options', 'users', 'usermeta', 'posts', 'postmeta', 'comments'):
                if prefix + kind not in v.schemas:
                    f.add('SCHEMA_INCOMPLET', table=prefix + kind, columns=[])
            for key in ('home', 'siteurl'):
                if key not in v.option_names:
                    f.add('URL_ABSENTE', table=prefix + 'options', columns=['option_name','option_value'])
        for table, decision in v.policy.decisions.items():
            valid = (table in v.schemas and (not prefix or table[len(prefix):] not in known)
                     and isinstance(decision, dict) and not set(decision) - {'action','columns'}
                     and decision.get('action') in ('garder','vider','anonymiser'))
            if valid and decision['action'] == 'anonymiser':
                cols = decision.get('columns')
                valid = isinstance(cols, list) and bool(cols) and all(isinstance(c,str) and c in v.schemas[table] for c in cols)
            elif valid: valid = 'columns' not in decision
            if not valid: error('DECISION_INVALIDE')
