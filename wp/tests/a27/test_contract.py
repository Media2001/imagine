"""Bind the owned adapters to their read-only native-bank contracts."""
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'wp/outils/bascule/a27'
spec = importlib.util.spec_from_file_location('a27_report_contract', TOOLS / 'report.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class ContractTests(unittest.TestCase):
    def test_living_states_identical_to_a20(self):
        a20 = (ROOT / 'wp/outils/bascule/a20/Inventory.php').read_text(encoding='utf-8')
        own = (TOOLS / 'Analysis.php').read_text(encoding='utf-8')
        expected = re.search(r"'subscription_status'\s*=>\s*\[([^]]+)\]", a20).group(1)
        actual = re.search(r'const LIVE\s*=\s*\[([^]]+)\]', own).group(1)
        self.assertEqual(re.findall(r"'([^']+)'", actual), re.findall(r"'([^']+)'", expected))

    def test_php_and_python_gateway_vocabularies_match(self):
        own = (TOOLS / 'Analysis.php').read_text(encoding='utf-8')
        allowed = re.search(r'const GATEWAYS\s*=\s*\[([^]]+)\]', own, re.S).group(1)
        self.assertEqual(set(re.findall(r"'([^']+)'", allowed)) | {'aucune', 'autre'}, set(r.GATEWAYS))

    def test_all_php_refusals_are_allowlisted(self):
        allowed = set(json.loads((TOOLS / 'refusals.json').read_text(encoding='utf-8')))
        for file in list(TOOLS.glob('*.php')) + [TOOLS / 'inventorier-paiements']:
            for code in re.findall(r"(?:RuntimeException\(|\?\s*|:\s*)'([A-Z][A-Z0-9_]+)'", file.read_text(encoding='utf-8')):
                if code.startswith('A27_'):
                    self.assertIn(code, allowed, file.name)
        self.assertTrue(all(re.fullmatch(r'A(?:27|02|11|12)_[A-Z_]+', code) for code in allowed))

    def test_readme_ten_standard_lines_and_two_parent_lines(self):
        text = (TOOLS / 'README.md').read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'^(\d+)\. ', text, re.M), [str(i) for i in range(1, 11)])
        lines = (ROOT / 'production/A-27/readme-ajout.txt').read_bytes().splitlines(keepends=True)
        self.assertEqual(len(lines), 2)
        self.assertTrue(all(line.endswith(b'\n') for line in lines))
        self.assertEqual(sum(line.startswith('python3 wp/outils/bascule/a27/confine.py ') for line in text.splitlines()), 1)

    def test_dependencies_are_used_without_alternate_guard(self):
        inventory = (TOOLS / 'Inventory.php').read_text(encoding='utf-8')
        launcher = (TOOLS / 'confine.py').read_text(encoding='utf-8')
        self.assertIn('SubscriptionCoherence\\Inventory::paymentReference($sub)', inventory)
        self.assertIn("HERE.parent / 'stream_guard.py'", launcher)
        self.assertIn('guard.supervise(', launcher)
        self.assertIn('report.complete_report(staged_output, audit)', launcher)
        self.assertNotIn('subprocess.Popen', launcher)
        self.assertNotIn('subprocess.run', launcher)
        for file in TOOLS.glob('*.php'):
            text = file.read_text(encoding='utf-8')
            self.assertNotRegex(text, r'\b(?:wp_remote_(?:get|post|request)|curl_exec|fsockopen|payment_complete|process_payment)\s*\(')


if __name__ == '__main__':
    unittest.main()
