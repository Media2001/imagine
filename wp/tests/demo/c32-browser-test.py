"""Régressions C32, hors réseau et sans import du transport/site."""
import sys
sys.dont_write_bytecode = True
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('policy', ROOT/'wp/outils/demo/c32_browser_policy.py')
policy = importlib.util.module_from_spec(spec)
if spec.loader is not None and Path(spec.origin).exists():
    spec.loader.exec_module(policy)


class CookieReadingTest(unittest.TestCase):
    def test_strict_refuses_native_but_inventory_accepts_it(self):
        row = {'kind': 'lecture', 'path': '/', 'header_names': [], 'browser': [{'name': n} for n in policy.READING_NATIVE]}
        verdict = policy.reading_verdict([row])
        self.assertFalse(verdict['strict_pass'])
        self.assertTrue(verdict['inventory_pass'])
        self.assertEqual(1, verdict['pages'])

    def test_strict_passes_when_cookies_disappear(self):
        row = {'kind': 'lecture', 'path': '/', 'header_names': [], 'browser': []}
        self.assertTrue(policy.reading_verdict([row])['strict_pass'])

    def test_empty_observation_is_not_a_pass(self):
        self.assertFalse(policy.reading_verdict([])['strict_pass'])
        self.assertFalse(policy.reading_verdict([])['inventory_pass'])

    def test_each_listed_non_reading_cookie_is_refused(self):
        for name in ['woocommerce_cart_hash', 'woocommerce_items_in_cart', 'wp_woocommerce_session_'+'a'*32, 'wordpress_test_cookie', 'wordpress_'+'a'*32, 'wordpress_logged_in_'+'a'*32, 'wp_lang', 'sbjs_intrus']:
            for channel in ['header_names', 'browser']:
                with self.subTest(name=name, channel=channel):
                    row = {'kind': 'lecture', 'path': '/', 'header_names': [], 'browser': []}
                    row[channel] = [name] if channel == 'header_names' else [{'name': name}]
                    verdict = policy.reading_verdict([row])
                    self.assertFalse(verdict['strict_pass'])
                    self.assertFalse(verdict['inventory_pass'])


class PublicPathsTest(unittest.TestCase):
    def test_c26_extension_is_covered_by_url_identity(self):
        import json
        extension = json.loads((ROOT/'production/C-26/mutations-livraison-extension.json').read_text(encoding='utf-8'))
        fixture = {'article_path': '/article/', 'issue_path': '/numeros/un/', 'term_path': '/theme/', 'posts': [{'path': '/article/'}], 'issues': [{'slug': 'un'}]}
        paths = policy.public_paths(fixture, {'cookies': {'path': '/gestion-des-cookies/'}}, extension)
        expected = {x['path'] for group in ['pages', 'events'] for x in extension[group]}
        self.assertTrue(expected)
        self.assertTrue(expected <= set(paths))
        self.assertEqual(len(paths), len(set(paths)))
        mutant = [p for p in paths if p != '/notre-cooperative/'] + ['/autre-page/']
        self.assertEqual(len(paths), len(mutant))
        self.assertFalse(policy.coverage(mutant, paths)['pass'])
        self.assertEqual(['/notre-cooperative/'], policy.coverage(mutant, paths)['missing'])

    def test_empty_c26_inventory_is_rejected(self):
        with self.assertRaises(ValueError):
            policy.public_paths({}, {}, {'pages': [], 'events': []})


class SessionCleanupTest(unittest.TestCase):
    @staticmethod
    def row(key, value='initial'):
        return {'session_key': key, 'session_value': value, 'session_expiry': '123', 'session_id': key}

    def test_concurrent_foreign_guest_is_preserved_and_not_success(self):
        own = self.row('guest-owned', 'test')
        foreign = self.row('guest-foreign', 'concurrent')
        state = {r['session_key']: r for r in [own, foreign]}
        touched = []
        def replace(key, expected, previous):
            touched.append(key)
            state.pop(key, None)
            if previous is not None:
                state[key] = previous
            return True
        result = policy.restore_sessions([], list(state.values()), {'guest-owned'}, replace, lambda: list(state.values()))
        self.assertEqual(['guest-owned'], touched)
        self.assertEqual({'guest-foreign': foreign}, state)
        self.assertFalse(result['restored'])
        self.assertEqual(1, result['foreign_changes'])

    def test_only_known_guest_and_temporary_account_are_restored(self):
        old = self.row('guest-owned')
        foreign = self.row('persistent-foreign')
        state = {'guest-owned': self.row('guest-owned', 'changed'), '4711': self.row('4711'), 'persistent-foreign': foreign}
        def replace(key, expected, previous):
            self.assertEqual(expected, state.get(key))
            state.pop(key, None)
            if previous is not None:
                state[key] = previous
            return True
        result = policy.restore_sessions([old, foreign], list(state.values()), {'guest-owned', '4711'}, replace, lambda: list(state.values()))
        self.assertTrue(result['restored'])
        self.assertEqual({'guest-owned': old, 'persistent-foreign': foreign}, state)

    def test_missing_owned_preimage_is_reinserted(self):
        old = self.row('guest-owned')
        state = {}
        def replace(key, expected, previous):
            self.assertIsNone(expected)
            state[key] = previous
            return True
        result = policy.restore_sessions([old], [], {'guest-owned'}, replace, lambda: list(state.values()))
        self.assertTrue(result['restored'])
        self.assertEqual(old, state['guest-owned'])

    def test_changed_or_missing_foreign_session_is_not_touched(self):
        for current in [[], [self.row('foreign', 'concurrent change')]]:
            with self.subTest(current=current):
                result = policy.restore_sessions([self.row('foreign')], current, set(), lambda *args: self.fail('Foreign write'), lambda: current)
                self.assertFalse(result['restored'])
                self.assertEqual(1, result['foreign_changes'])

    def test_compare_and_swap_conflict_is_not_success(self):
        current = [self.row('guest-owned')]
        result = policy.restore_sessions([], current, {'guest-owned'}, lambda *args: False, lambda: current)
        self.assertFalse(result['restored'])
        self.assertEqual(1, result['write_conflicts'])

    def test_foreign_arrival_during_cleanup_is_detected(self):
        result = policy.restore_sessions([], [], set(), lambda *args: self.fail('Unexpected write'), lambda: [self.row('late-foreign')])
        self.assertFalse(result['restored'])
        self.assertEqual(1, result['foreign_changes'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
