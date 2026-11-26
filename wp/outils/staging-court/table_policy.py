"""Versioned schema policy; known form messages cannot be retained by a decision."""
import fnmatch
import json
from pathlib import Path
from archive import Refusal


def load():
    try:
        data = json.loads(Path(__file__).with_name('politique-tables.json').read_text(encoding='utf-8'))
        assert data['version'] == 1 and data['default'] == 'vider'
        assert all(set(r) == {'pattern', 'action'} and isinstance(r['pattern'], str)
                   and r['action'] == 'vider' for r in data['families'])
        return data
    except (OSError, ValueError, KeyError, TypeError, AssertionError):
        raise Refusal('TABLE_POLICY_REFUSED') from None


class Policy:
    def __init__(self, known, decisions=None):
        self.data = load()
        self.known = known
        self.decisions = decisions or {}
        try:
            forms = json.loads((Path(__file__).resolve().parent.parent / 'staging/form-policy.json').read_text(encoding='utf-8'))
            assert forms['version'] == 1 and set(forms) == {'version', 'tables', 'post_types'}
            assert isinstance(forms['tables'], list) and forms['tables']
            assert all(isinstance(t, str) and t.isascii() and t.replace('_', '').isalnum() for t in forms['tables'])
            self.form_tables = forms['tables']
        except (OSError, ValueError, KeyError, TypeError, AssertionError):
            raise Refusal('TABLE_POLICY_REFUSED') from None

    def resolve(self, table, prefix):
        kind = table[len(prefix):] if prefix and table.startswith(prefix) else ''
        if kind in self.form_tables:
            if table in self.decisions and self.decisions[table] != {'action': 'vider'}:
                raise Refusal('FORM_MESSAGES_DECISION_REFUSED', {'table': kind})
            return {'action': 'vider'}, 'formulaires'
        family = next((r['pattern'] for r in self.data['families'] if fnmatch.fnmatchcase(kind, r['pattern'])), None)
        if table in self.decisions:
            value = self.decisions[table]
            valid_action = isinstance(value, dict) and value.get('action') in ('garder', 'vider', 'anonymiser')
            return value if valid_action else {'action':None}, family or ('catalogue' if kind in self.known else 'hors-famille')
        if family:
            return {'action':'vider'}, family
        if kind in self.known:
            return {'action':'garder'}, 'catalogue'
        return {'action':'vider'}, 'hors-famille'

    def summary(self, schemas, prefix):
        from diagnosis import PERSONAL
        grouped, other = {}, []
        for table in sorted(schemas):
            decision, family = self.resolve(table, prefix)
            action = 'catalogue' if family == 'catalogue' and table not in self.decisions else {
                'vider':'videe', 'garder':'gardee', 'anonymiser':'anonymisee'}.get(decision.get('action'), 'a-trancher')
            if family != 'catalogue' and decision.get('action') == 'garder' and any(PERSONAL.search(c) for c in schemas[table]):
                action = 'a-trancher'
            key = (family, action)
            grouped[key] = grouped.get(key, 0) + 1
            if family == 'hors-famille': other.append(table)
        return [{'family':family, 'action':action, 'count':count} for (family,action),count in sorted(grouped.items())], other
