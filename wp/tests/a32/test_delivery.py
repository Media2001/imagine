"""A32 packet control tests; synthetic receipts are boundary doubles only."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCRATCH = Path.home() / 'AppData/Local/hermes/cache/scratch'


def delivery():
    spec = importlib.util.spec_from_file_location('a32_test_delivery', HERE / 'delivery.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class DeliveryTests(unittest.TestCase):
    def test_duplicate_json_is_refused(self):
        m = delivery()
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            path = Path(name) / 'double.json'
            path.write_text('{"exit_code":0,"exit_code":1}', encoding='utf-8')
            with self.assertRaises(ValueError):
                m.read(path)

    def test_python_only_cannot_be_native_evidence(self):
        m = delivery()
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            path = Path(name)
            (path / 'windows-matrix.json').write_text(json.dumps({'scope': 'python_only', 'exit_code': 0, 'sources_stable': True}), encoding='utf-8')
            self.assertFalse(m.local_valid(path))

    def test_shared_document_contract_is_line_based(self):
        m = delivery()
        contract = (ROOT / 'production/A-32/readme-contract.txt').read_bytes().splitlines(keepends=True)
        shared = (ROOT / 'wp/outils/bascule/README.md').read_bytes().splitlines(keepends=True)
        local = (ROOT / 'wp/outils/bascule/tournee/README.md').read_bytes().splitlines(keepends=True)
        for line in contract:
            self.assertEqual(shared.count(line), 1)
            self.assertEqual([value.rstrip(b'\r\n') for value in local].count(line.rstrip(b'\r\n')), 1)
        self.assertNotIn('wp/outils/bascule/README.md', m.sources())
        self.assertIn('wp/outils/bascule/tournee/README.md', m.sources())

    def test_correction_evidence_requires_new_native_cases(self):
        m = delivery()
        self.assertTrue({'environment_absent', 'define_in_string', 'define_in_comment'}.issubset(m.GUARD_CASES))
        self.assertEqual(m.CLOCK_CASES, ('current', 'later', 'year_before', 'equality', 'year_after'))

    def test_common_readme_current_list_and_gate_recursive_sources(self):
        import ast
        shared = (ROOT / 'wp/outils/bascule/README.md').read_text(encoding='utf-8')
        local = (ROOT / 'wp/outils/bascule/tournee/README.md').read_text(encoding='utf-8')
        self.assertIn('La liste courante des quinze outils et leur ordre sont définis dans `tournee/outils.jsonl`', shared)
        self.assertNotIn("L'ancienne section du README commun n'est pas réécrite", local)
        tree = ast.parse((HERE / 'gates.py').read_text(encoding='utf-8'))
        roots = next(ast.literal_eval(n.value) for n in ast.walk(tree)
                     if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'roots' for t in n.targets))
        self.assertIn('wp/outils/bascule', roots)

    def test_exclusions_are_disjoint_and_keep_unclosed_tools_out(self):
        m = delivery()
        excluded = m.read(ROOT / 'wp/outils/bascule/tournee/exclusions.json')
        self.assertTrue({'A13', 'A14', 'A29', 'A30', 'A31'}.issubset(excluded))
        self.assertFalse(set(m.TOOLS).intersection(excluded))
        for lot in ('A26', 'A27'):
            lines = (ROOT / 'wp/outils/bascule/tournee/outils.jsonl').read_text(encoding='utf-8').splitlines()
            self.assertEqual(sum(json.loads(line)['lot'] == lot for line in lines), 1)


if __name__ == '__main__':
    unittest.main()
