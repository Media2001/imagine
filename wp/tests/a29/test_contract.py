"""Closed vocabulary, documented arguments and honest prepared-bank contracts."""
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'wp/outils/bascule/a29'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class ContractTests(unittest.TestCase):
    def test_php_python_closed_families_match(self):
        report = module('a29_contract_report', TOOLS / 'report.py')
        php = (TOOLS / 'Analysis.php').read_text(encoding='utf-8')
        found = re.search(r'const FAMILIES\s*=\s*\[([^]]+)\]', php, re.S).group(1)
        self.assertEqual(tuple(re.findall(r"'([^']+)'", found)), report.FAMILIES)
        counts = re.search(r'const COUNTS\s*=\s*\[([^]]+)\]', php, re.S).group(1)
        self.assertEqual(tuple(re.findall(r"'([^']+)'", counts)), report.COUNTS)

    def test_all_php_refusals_are_allowlisted(self):
        allowed = set(json.loads((TOOLS / 'refusals.json').read_text(encoding='utf-8')))
        for file in list(TOOLS.glob('*.php')) + [TOOLS / 'inventorier-taches']:
            for code in re.findall(r"(?:RuntimeException\(|\?\s*|:\s*)'([A-Z][A-Z0-9_]+)'", file.read_text(encoding='utf-8')):
                if code.startswith('A29_'):
                    self.assertIn(code, allowed, file.name)
        self.assertTrue(all(re.fullmatch(r'A(?:29|02|11|12)_[A-Z_]+', code) for code in allowed))

    def test_ten_standard_lines_two_exact_parent_lines(self):
        text = (TOOLS / 'README.md').read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'^(\d+)\. ', text, re.M), [str(i) for i in range(1, 11)])
        lines = (ROOT / 'production/A-29/readme-ajout.txt').read_bytes().splitlines(keepends=True)
        self.assertEqual(len(lines), 2)
        self.assertTrue(all(line.endswith(b'\n') for line in lines))
        commands = [line for line in text.splitlines() if line.startswith('python3 wp/outils/bascule/a29/confine.py ')]
        self.assertEqual(commands, ['python3 wp/outils/bascule/a29/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/taches-date'])

    def test_existing_guard_and_fence_are_reused(self):
        launcher = (TOOLS / 'confine.py').read_text(encoding='utf-8')
        self.assertIn("HERE.parent / 'stream_guard.py'", launcher)
        self.assertIn("HERE.parent / 'a12/confine.py'", launcher)
        self.assertIn('guard.supervise(', launcher)
        self.assertIn('report.complete_report(staged_output, audit)', launcher)
        self.assertIn('report.final_binding(stdout, staged_output)', launcher)
        self.assertNotIn('subprocess.Popen', launcher)
        self.assertNotIn('subprocess.run', launcher)

    def test_no_action_or_outgoing_api_in_subject(self):
        for file in list(TOOLS.glob('*.php')) + [TOOLS / 'inventorier-taches']:
            self.assertNotRegex(file.read_text(encoding='utf-8'),
                r'\b(?:do_action|wp_cron|spawn_cron|wp_remote_(?:get|post|request)|curl_exec|fsockopen|process_payment|as_schedule_single_action|as_enqueue_async_action)\s*\(')
        inventory = (TOOLS / 'Inventory.php').read_text(encoding='utf-8')
        self.assertIn("unserialize($raw, ['allowed_classes' => false])", inventory)
        self.assertIn('SELECT hook,status,scheduled_date_gmt', inventory)
        self.assertNotRegex(inventory, r'SELECT[^\n]*(?:action_id|group_id|args|schedule,)')
        self.assertIn("WHERE option_name='imagine_staging_disabled_plugins'", inventory)

    def test_native_banks_are_prepared_not_optional(self):
        folder = ROOT / 'wp/tests/a29'
        for name in ('unit.php', 'seed.php', 'neutralise.php', 'standard.php', 'inside.py', 'run.py', 'matrix.py', 'style.py', 'verify.py', 'seal.py'):
            self.assertTrue((folder / name).is_file(), name)
        native = (folder / 'inside.py').read_text(encoding='utf-8')
        for name in ('shutdown_valid_counts_and_markdown', 'documented_command_literal',
                     'all_tables_scheduler_unchanged', 'site_files_unchanged',
                     'actual_import_erases_cron_cancels_pending_deletes_failed'):
            self.assertIn(name, native)
        runner = (folder / 'run.py').read_text(encoding='utf-8')
        self.assertIn("required=True)", runner)
        self.assertIn("'preparation'", (folder / 'gates.py').read_text(encoding='utf-8'))

    def test_attribution_never_guesses_extension_from_callback_or_name(self):
        analysis = (TOOLS / 'Analysis.php').read_text(encoding='utf-8')
        self.assertIn("$other ? 'attribution indéterminée' : 0", analysis)
        self.assertNotIn('ReflectionFunction', analysis)
        self.assertNotIn('ReflectionMethod', analysis)
        self.assertNotIn('str_starts_with($hook', analysis)
        self.assertNotIn("'woocommerce_scheduled_subscription_trial_end' => 'fin_abonnement'", analysis)


if __name__ == '__main__':
    unittest.main()
