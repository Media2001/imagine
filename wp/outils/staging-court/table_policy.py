"""Versioned schema-name policy. Exact operator decisions always win."""
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

    def resolve(self, table, prefix):
        kind = table[len(prefix):] if prefix and table.startswith(prefix) else ''
        family = next((r['pattern'] for r in self.data['families'] if fnmatch.fnmatchcase(kind, r['pattern'])), None)
        if table in self.decisions:
            value = self.decisions[table]
            return value if isinstance(value, dict) else {'action':None}, family or ('catalogue' if kind in self.known else 'hors-famille')
        if family:
            return {'action':'vider'}, family
        if kind in self.known:
            return {'action':'garder'}, 'catalogue'
        return {'action':'vider'}, 'hors-famille'

    def summary(self, schemas, prefix):
        grouped, other = {}, []
        for table in sorted(schemas):
            decision, family = self.resolve(table, prefix)
            action = 'catalogue' if family == 'catalogue' and table not in self.decisions else {
                'vider':'videe', 'garder':'gardee', 'anonymiser':'anonymisee'}.get(decision.get('action'), 'a-trancher')
            key = (family, action)
            grouped[key] = grouped.get(key, 0) + 1
            if family == 'hors-famille': other.append(table)
        return [{'family':family, 'action':action, 'count':count} for (family,action),count in sorted(grouped.items())], other
