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
        self.assertEqual([e['lot'] for e in entries], ['A10', 'A11', 'A12', 'A15', 'A16', 'A17', 'A18', 'A19', 'A20', 'A21', 'A23', 'A24', 'A25', 'A26', 'A27'])
        for entry in entries:
            self.assertIn(entry['command'], m.documented_commands(ROOT / entry['readme']))
            argv = m.command(entry, Path('/operator/site'), Path('/operator/report/audit/audit.json'), Path('/operator/map.json'), Path('/operator/report/out'))
            import shlex
            documented = shlex.split(entry['command'])
            self.assertEqual(len(argv), len(documented))
            self.assertEqual([x.split('=')[0] for x in argv[2:]], [x.split('=')[0] for x in documented[2:]])

    def test_verified_marker_required_before_any_tool_or_output(self):
        m = load()
        scratch = Path.home() / 'AppData/Local/hermes/cache/scratch'
        with tempfile.TemporaryDirectory(dir=scratch, prefix='a32-guard-') as tmp:
            root = Path(tmp)
            site = root / 'PRIVATE_SITE_CANARY'
            site.mkdir()
            config = site / 'wp-config.php'
            config.write_text("<?php define('WP_ENVIRONMENT_TYPE', 'staging');", encoding='utf-8')
            marker = site / '.imagine-staging-verified.json'
            valid = {'status': 'verified', 'offline_verified': True, 'runtime_probe_passed': True}
            reports = root / 'reports'
            reports.mkdir()
            audit = reports / 'audit'
            audit.mkdir()
            (audit / 'audit.json').write_text('{}', encoding='utf-8')
            mapping = root / 'map.json'
            mapping.write_text('{}', encoding='utf-8')
            invalid = [None, b'PRIVATE_MARKER_CANARY', b'[]', b'null', b'{}',
                       json.dumps({**valid, 'status': 'production'}).encode(),
                       json.dumps({**valid, 'offline_verified': 1}).encode(),
                       json.dumps({**valid, 'runtime_probe_passed': False}).encode()]
            called = []
            for i, value in enumerate(invalid):
                with self.subTest(marker=i):
                    if value is not None:
                        marker.write_bytes(value)
                    else:
                        marker.unlink(missing_ok=True)
                    before = {p.relative_to(site).as_posix(): p.read_bytes() for p in site.rglob('*') if p.is_file()}
                    target = reports / ('tour-' + str(i))
                    with self.assertRaisesRegex(RuntimeError, '^A32_NOT_VERIFIED$'):
                        m.run(site, audit / 'audit.json', mapping, target, lambda args: called.append(args))
                    self.assertFalse(target.exists())
                    self.assertEqual(called, [])
                    self.assertEqual(before, {p.relative_to(site).as_posix(): p.read_bytes() for p in site.rglob('*') if p.is_file()})
            marker.write_text(json.dumps(valid), encoding='utf-8')
            for text in ["<?php define('WP_ENVIRONMENT_TYPE', 'production');", "<?php define('WP_ENVIRONMENT_TYPE', getenv('PRIVATE_CANARY'));", '<?php // no environment']:
                config.write_text(text, encoding='utf-8')
                with self.subTest(config=text):
                    with self.assertRaisesRegex(RuntimeError, '^A32_NOT_VERIFIED$'):
                        m.run(site, audit / 'audit.json', mapping, reports / 'production', lambda args: called.append(args))
                    self.assertEqual(called, [])
                    self.assertFalse((reports / 'production').exists())

    def test_cli_refusal_never_echoes_site_or_marker(self):
        import subprocess
        import hashlib
        m = load()
        scratch = Path.home() / 'AppData/Local/hermes/cache/scratch'
        with tempfile.TemporaryDirectory(dir=scratch, prefix='a32-cli-') as tmp:
            root = Path(tmp)
            site = root / 'PRIVATE_PATH_CANARY'
            site.mkdir()
            config = site / 'wp-config.php'
            config.write_text("<?php define('WP_ENVIRONMENT_TYPE', 'staging');", encoding='utf-8')
            marker = site / '.imagine-staging-verified.json'
            target = root / 'must-not-exist'
            command = [sys.executable, '-B', str(ROOT / 'wp/outils/bascule/tournee/tournee.py'),
                       '--wp-path=' + str(site), '--audit=' + str(root / 'absent.json'),
                       '--correspondance=' + str(root / 'absent-map.json'), '--output=' + str(target)]
            valid = {'status': 'verified', 'offline_verified': True, 'runtime_probe_passed': True}
            for value, environment in [(None, 'staging'), (b'PRIVATE_MARKER_CANARY', 'staging'),
                                       (json.dumps(valid).encode(), 'production')]:
                marker.unlink(missing_ok=True)
                if value is not None:
                    marker.write_bytes(value)
                before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in site.iterdir()}
                env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'WP_ENVIRONMENT_TYPE': environment, 'PYTHONDONTWRITEBYTECODE': '1'}
                env.pop('TMPDIR', None)
                p = subprocess.run(command, env=env, capture_output=True, timeout=30)
                self.assertEqual((p.returncode, p.stdout, p.stderr), (1, b'', b'A32_NOT_VERIFIED\n'))
                self.assertFalse(target.exists())
                self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in site.iterdir()})

    def test_new_closed_tool_refusals_remain_refusals(self):
        m = load()
        for entry in m.entries()[-2:]:
            codes = json.loads((ROOT / ('wp/outils/bascule/' + entry['lot'].lower() + '/refusals.json')).read_text(encoding='utf-8'))
            for code in codes:
                with self.subTest(tool=entry['lot'], code=code):
                    row = m.classify(entry, 1, b'', (code + '\n').encode('ascii'), Path('/absent'))
                    self.assertEqual(row['statut'], 'refusé')
                    self.assertEqual(row['code'], code)

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
            (site / 'wp-config.php').write_text("<?php define('WP_ENVIRONMENT_TYPE', 'staging');", encoding='utf-8')
            (site / '.imagine-staging-verified.json').write_text(json.dumps({'status': 'verified', 'offline_verified': True, 'runtime_probe_passed': True}), encoding='utf-8')
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
            self.assertEqual(data['tournee'], 'partielle')
            self.assertEqual([r['statut'] for r in data['outils'][:2]], ['refusé', 'en échec'])
            self.assertNotIn('PRIVATE_CANARY', (target / 'bilan.json').read_text())
            self.assertNotIn('987654321', (target / 'bilan.md').read_text())


if __name__ == '__main__':
    unittest.main()
