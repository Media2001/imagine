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

    def test_common_readme_current_list_and_closed_sources(self):
        m = delivery()
        shared = (ROOT / 'wp/outils/bascule/README.md').read_text(encoding='utf-8')
        local = (ROOT / 'wp/outils/bascule/tournee/README.md').read_text(encoding='utf-8')
        self.assertIn('La liste courante des quinze outils et leur ordre sont définis dans `tournee/outils.jsonl`', shared)
        self.assertNotIn("L'ancienne section du README commun n'est pas réécrite", local)
        roots = m.read(ROOT / 'production/A-32/source-roots.json')
        self.assertEqual(set(roots), {'matrix', 'gates'})
        tool_roots = {'wp/outils/bascule/' + tool.lower() for tool in m.TOOLS}
        required = tool_roots | {'wp/outils/bascule/tournee', 'wp/tests/a32',
                                'wp/outils/bascule/stream_guard.py', 'wp/outils/bascule/stream_refusals.json',
                                'wp/outils/staging', 'wp/outils/staging-court'}
        for group in roots.values():
            self.assertTrue(required.issubset(group))
            self.assertNotIn('wp/outils/bascule', group)
            for neighbour in ('a29', 'a30', 'a31', 'a33', 'a34'):
                self.assertNotIn('wp/outils/bascule/' + neighbour, group)
        sources = m.sources()
        self.assertFalse(any(key.startswith(('wp/outils/bascule/a33/', 'wp/outils/bascule/a34/')) for key in sources))
        self.assertIn('wp/outils/bascule/a27/Inventory.php', sources)

    def test_gates_cannot_choose_their_own_dependency_roots(self):
        m = delivery()
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            folder = Path(name)
            (folder / 'source-roots.json').write_text('[]', encoding='utf-8')
            (folder / 'sources.json').write_text('{}', encoding='utf-8')
            (folder / 'commands.json').write_text('[]', encoding='utf-8')
            (folder / 'result.json').write_text('{"exit_code":0,"sources_stable":true}', encoding='utf-8')
            self.assertFalse(m.gates_valid(folder))

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
