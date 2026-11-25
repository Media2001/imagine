"""A-13 : preuves CLI hors dépôt, données exclusivement fictives."""
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / 'wp/outils/bascule/controler-export'
CONFIG = ROOT / 'wp/outils/bascule/a13/correspondance.exemple.json'
FIXTURES = ROOT / 'wp/tests/fixtures'
SCRATCH = Path(os.environ.get('TMPDIR', tempfile.gettempdir()))


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='a13-test-', dir=SCRATCH)
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)

    def run_cli(self, fixture='a13-export-propre-fictif.csv', content=None, config=None, extra=()):
        source = self.work / 'export.csv'
        source.write_bytes((FIXTURES / fixture).read_bytes() if content is None else content)
        mapping = CONFIG
        if config is not None:
            mapping = self.work / 'correspondance.json'
            mapping.write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
        result = subprocess.run(
            [sys.executable, str(TOOL), str(source), '--correspondance', str(mapping),
             '--au', '2026-11-25', *extra], capture_output=True, encoding='utf-8',
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'},
            timeout=20,
        )
        return result, source

    def summary(self, source):
        return source.with_name(source.stem + '.controle-resume.txt').read_text(encoding='utf-8')

    def rejects(self, source):
        path = source.with_name(source.stem + '.controle-rejets.csv')
        return list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8')), delimiter=';'))

    def test_clean_file_returns_zero_and_thirty_clean_rows(self):
        result, source = self.run_cli()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn('Lignes contrôlées : 30', self.summary(source))
        self.assertIn('Lignes sans défaut : 30', self.summary(source))
        self.assertEqual([], self.rejects(source))
        self.assertEqual('', result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
