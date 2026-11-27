"""A32 contracts: exact documented argv and closed orchestration."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]


def load():
    path = ROOT / 'wp/outils/bascule/tournee/tournee.py'
    spec = importlib.util.spec_from_file_location('tournee', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TourneeTests(unittest.TestCase):
    def test_exact_commands_and_closed_inventory(self):
        self.assertTrue((ROOT / 'wp/outils/bascule/tournee/tournee.py').is_file(), 'A32 implementation absent')
        m = load()
        entries = m.entries()
        self.assertEqual([e['lot'] for e in entries], ['A10', 'A11', 'A12', 'A15', 'A16', 'A17', 'A18', 'A19', 'A20', 'A21', 'A23', 'A24', 'A25'])
        for entry in entries:
            self.assertIn(entry['command'], m.documented_commands(ROOT / entry['readme']))
            argv = m.command(entry, Path('/operator/site'), Path('/operator/report/audit/audit.json'), Path('/operator/map.json'), Path('/operator/report/out'))
            import shlex
            documented = shlex.split(entry['command'])
            self.assertEqual(len(argv), len(documented))
            self.assertEqual([x.split('=')[0] for x in argv[2:]], [x.split('=')[0] for x in documented[2:]])

    def test_refusal_allowlist_and_no_site_value(self):
        m = load()
        e = m.entries()[0]
        p = Path('/absent')
        for code, out, err in [(1, b'', b'A10_AUDIT_GUARD\n'), (1, b'', b'A10_PRIVATE_CANARY\n'), (0, b'', b''), (255, b'', b'A10_AUDIT_GUARD\n')]:
            row = m.classify(e, code, out, err, p)
            self.assertEqual(row['statut'], 'refusé' if err == b'A10_AUDIT_GUARD\n' and code == 1 else 'en échec')
            self.assertNotIn('CANARY', json.dumps(row))
            if row['statut'] == 'en échec':
                self.assertIs(type(row['sortie']), int)

    def test_continue_and_partial_not_complete(self):
        m = load()
        scratch = Path(os.environ.get('TMPDIR', str(Path.home() / 'AppData/Local/hermes/cache/scratch')))
        with tempfile.TemporaryDirectory(dir=scratch, prefix='a32-unittest-') as tmp:
            root = Path(tmp)
            site = root / 'site'
            site.mkdir()
            reports = root / 'reports'
            reports.mkdir()
            audit = reports / 'audit'
            audit.mkdir()
            (audit / 'audit.json').write_text('{}')
            mapping = root / 'map.json'
            mapping.write_text('{}')
            called = []
            target = reports / 'tour'
            def execute(args):
                called.append(args)
                state = json.loads((target / 'bilan.json').read_text())
                self.assertEqual(state['tournee'], 'partielle')
                if len(called) == 1:
                    return 1, b'', b'A10_AUDIT_GUARD\n'
                if len(called) == 2:
                    return 255, b'PERSON_PRIVATE_CANARY', b'PERSON_PRIVATE_CANARY'
                e = m.entries()[len(called) - 1]
                out = Path(next(x.split('=', 1)[1] for x in args if x.startswith('--output=')))
                out.mkdir()
                for f in e['files']:
                    (out / f).write_text('PRIVATE_CANARY 987654321')
                return 0, e['success'].encode(), b''
            self.assertEqual(m.run(site, audit / 'audit.json', mapping, target, execute), 1)
            self.assertEqual(len(called), len(m.entries()))
            data = json.loads((target / 'bilan.json').read_text())
            self.assertEqual(data['tournee'], 'complète')
            self.assertEqual([r['statut'] for r in data['outils'][:2]], ['refusé', 'en échec'])
            self.assertNotIn('PRIVATE_CANARY', (target / 'bilan.json').read_text())
            self.assertNotIn('987654321', (target / 'bilan.md').read_text())


if __name__ == '__main__':
    unittest.main()
