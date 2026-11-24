"""Streaming schema-only SQL diagnostic on the existing closed grammar."""
from archive import Refusal
from sql_stream import Framer, Validator


class SQLAnalysis:
    def __init__(self, findings, decisions):
        from diagnosis import parser_module
        self.findings, self.decisions = findings, decisions
        self.validator = Validator(parser_module(), findings=findings)
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
        from diagnosis import catalogue, PERSONAL
        f, v = self.findings, self.validator
        if not self.failed:
            try: self.framer.finish()
            except Refusal as exc: f.add(str(exc))
        v.finish()
        prefix = v.prefix
        known = catalogue()
        for table, columns in v.schemas.items():
            kind = table[len(prefix):] if prefix and table.startswith(prefix) else ''
            if kind not in known:
                f.add('TABLE_INCONNUE_CONSERVEE', blocking=False, table=table, columns=columns)
                personal = [c for c in columns if PERSONAL.search(c)]
                if personal and table not in self.decisions:
                    f.add('TABLE_PERSONNELLE_A_TRANCHER', table=table, columns=personal)
            else:
                extra = [c for c in columns if c not in known[kind]]
                if extra: f.add('COLONNES_INCONNUES_CONSERVEES', blocking=False, table=table, columns=extra)
            if v.engines.get(table) != 'INNODB':
                f.add('NON_INNODB_TABLE', blocking=False, table=table, columns=columns)
        if prefix:
            for kind in ('options', 'users', 'usermeta', 'posts', 'postmeta', 'comments'):
                if prefix + kind not in v.schemas:
                    f.add('SCHEMA_INCOMPLET', table=prefix + kind, columns=[])
            for key in ('home', 'siteurl'):
                if key not in v.option_names:
                    f.add('URL_ABSENTE', table=prefix + 'options', columns=['option_name','option_value'])
        for table, decision in self.decisions.items():
            valid = (table in v.schemas and (not prefix or table[len(prefix):] not in known)
                     and isinstance(decision, dict) and not set(decision) - {'action','columns'}
                     and decision.get('action') in ('garder','vider','anonymiser'))
            if valid and decision['action'] == 'anonymiser':
                cols = decision.get('columns')
                valid = isinstance(cols, list) and bool(cols) and all(isinstance(c,str) and c in v.schemas[table] for c in cols)
            elif valid: valid = 'columns' not in decision
            if not valid: f.add('DECISION_INVALIDE')
