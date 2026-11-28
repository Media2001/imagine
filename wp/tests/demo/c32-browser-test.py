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


class BrowserWiringTest(unittest.TestCase):
    def test_real_strict_exit_fails_for_a_cookie_and_passes_without(self):
        import ast
        tree = ast.parse((ROOT/'wp/outils/demo/c32-browser.py').read_text(encoding='utf-8'))
        strict = tree.body[-1]
        self.assertIsInstance(strict, ast.If)
        self.assertEqual('strict_mode', strict.test.id)
        code = compile(ast.Module(body=[strict], type_ignores=[]), 'c32-browser strict exit', 'exec')
        with self.assertRaises(AssertionError):
            exec(code, {'strict_mode': True, 'checks': {policy.STRICT_CHECK: False}, 'policy': policy})
        exec(code, {'strict_mode': True, 'checks': {policy.STRICT_CHECK: True}, 'policy': policy})
        exec(code, {'strict_mode': False, 'checks': {policy.STRICT_CHECK: False}, 'policy': policy})

    def test_real_cleanup_calls_the_safe_policy(self):
        import ast
        tree = ast.parse((ROOT/'wp/outils/demo/c32-browser.py').read_text(encoding='utf-8'))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id=='policy' and n.func.attr=='restore_sessions']
        self.assertEqual(1, len(calls))
        self.assertEqual('knownkeys', calls[0].args[2].id)
        self.assertEqual('replace_session', calls[0].args[3].id)


class ReceptionTest(unittest.TestCase):
    """Fixtures de lecteur uniquement ; aucune preuve navigateur synthétisée sur disque."""
    @staticmethod
    def receipt(with_native):
        import hashlib
        import json
        sys.path.insert(0, str(ROOT/'production/C-32'))
        import reception_c32 as reader
        extension_path = ROOT/'production/C-26/mutations-livraison-extension.json'
        extension = json.loads(extension_path.read_text(encoding='utf-8'))
        public = {'fixture': {'article_path':'/article/', 'issue_path':'/numeros/un/', 'term_path':'/theme/', 'posts':[{'path':'/article/'}], 'issues':[{'slug':'un'}]}, 'pages':{'cookies':{'path':'/gestion-des-cookies/'}}}
        paths = policy.public_paths(public['fixture'], public['pages'], extension)
        rows = [{'kind':'lecture', 'path':p, 'status':200, 'header_names':[], 'browser':[{'name':n} for n in policy.READING_NATIVE] if with_native else [], 'unknown':[], 'zero_cookie_expected':True, 'zero_cookie_pass':not with_native} for p in paths]
        checks = {'page_liste_unique':True, 'page_texte_vide':True, 'connexion_liste_fermee':True, 'connexion_native_reussie':True, 'mutation_header_mutation_detectee':True, 'mutation_script_mutation_detectee':True, 'aucun_tiers':True, policy.STRICT_CHECK:not with_native, 'lecture_ecart_natif_borne':True, 'couverture_publique_identique':True}
        for i in range(1,len(paths)+1):
            checks.update({'lecture_'+str(i)+'_'+s:True for s in ['200','liste_fermee','etanche','ecart_natif_borne']})
        for i,kind in enumerate(['code','panier','langue'],len(paths)+1):
            checks.update({kind+'_'+str(i)+'_'+s:True for s in ['200','liste_fermee','etanche']})
            checks[kind+'_cookies_natifs_observes']=True
        rows += [{'kind':kind, 'status':200, 'unknown':['c32_sonde_hors_liste'] if kind.startswith('mutation_') else []} for kind in ['code','panier','langue','connexion','mutation_header','mutation_script']]
        data = {'sources':reader.owner.sources(reader.owner), 'c26_extension_sha256':hashlib.sha256(extension_path.read_bytes()).hexdigest(), 'public_inventory':public, 'rows':rows, 'public_coverage':policy.coverage(paths,paths), 'checks':checks, 'inventory_checks':[k for k in checks if k!=policy.STRICT_CHECK], 'total':len(checks), 'reading':policy.reading_verdict(rows), 'zero_cookie_reading':not with_native, 'verdicts':{'inventory':'PASS','strict_zero_cookie':'FAIL' if with_native else 'PASS'}, 'error':None, 'restored':True, 'sessions_restored':True, 'probe_removed':True, 'external':[], 'sessions_cleanup':{'restored':True,'foreign_changes':0,'write_conflicts':0,'owned_remaining':0}}
        return reader,data

    def test_final_reader_accepts_both_real_strict_outcomes(self):
        for with_native in [False,True]:
            reader,data=self.receipt(with_native)
            self.assertEqual(not with_native,reader.verify_browser(data)['strict_pass'])

    def test_same_page_count_does_not_hide_missing_url(self):
        reader,data=self.receipt(True)
        next(r for r in data['rows'] if r.get('path')=='/notre-cooperative/')['path']='/autre-page/'
        with self.assertRaises(AssertionError):
            reader.verify_browser(data)

    def test_listed_cart_cookie_in_reading_is_rejected(self):
        reader,data=self.receipt(True)
        data['rows'][0]['header_names']=['woocommerce_cart_hash']
        data['rows'][0]['zero_cookie_pass']=False
        data['reading']=policy.reading_verdict(data['rows'])
        with self.assertRaises(AssertionError):
            reader.verify_browser(data)

    def test_stale_strict_fail_cannot_be_accepted_when_cookies_disappear(self):
        reader,data=self.receipt(False)
        data['checks'][policy.STRICT_CHECK]=False
        data['zero_cookie_reading']=False
        data['verdicts']['strict_zero_cookie']='FAIL'
        with self.assertRaises(AssertionError):
            reader.verify_browser(data)

    def test_concurrent_session_cannot_be_reported_as_restored(self):
        reader,data=self.receipt(True)
        data['sessions_cleanup']['foreign_changes']=1
        with self.assertRaises(AssertionError):
            reader.verify_browser(data)

    def test_no_check_can_be_silently_dropped(self):
        reader,data=self.receipt(True)
        del data['checks']['lecture_1_ecart_natif_borne']
        with self.assertRaises(AssertionError):
            reader.verify_browser(data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
