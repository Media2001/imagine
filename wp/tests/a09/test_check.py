"""A09 contract tests. HTTP tests use loopback in a network=none runner."""
import importlib.util
import pathlib
import sys
import tempfile
import unittest
sys.dont_write_bytecode = True
REPO = pathlib.Path(__file__).resolve().parents[3]


def subject():
    path = REPO/'wp/outils/bascule/a09/check.py'
    if not path.is_file():
        raise AssertionError('A09 implementation missing')
    spec = importlib.util.spec_from_file_location('a09_check', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PlanTest(unittest.TestCase):
    def test_valid_three_column_plan(self):
        m = subject()
        with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as tmp:
            path = pathlib.Path(tmp)/'plan.csv'
            path.write_text('ancienne,cible,code\n/ancien-fictif,/nouveau-fictif,301\n', encoding='utf8')
            self.assertEqual(m.load_plan(path), [{'line': 2, 'ancienne': '/ancien-fictif', 'cible': '/nouveau-fictif', 'code': 301}])


class InvalidPlanTest(unittest.TestCase):
    def test_every_row_validated_strictly_with_repository_boundary(self):
        m = subject()
        bad = [
            'ancienne,cible,code\n/a,/b,301\n/a,/b,301\n',
            'ancienne,cible,code\n/a,/b,301\n/a,/c,302\n',
            'ancienne,cible,code\n/a,/a,301\n',
            'ancienne,cible,code\n/%61,/a,301\n',
            'ancienne,cible,code\nhttps://example.org/a,/b,301\n',
            'ancienne,cible,code\n/a,https://example.org/b,301\n',
            'ancienne,cible,code\n//example.org/a,/b,301\n',
            'ancienne,cible,code\n/a,//example.org/b,301\n',
            'ancienne,cible,code\n/a,/b,200\n',
            'ancienne,cible,code\n/a,/b,0301\n',
            'ancienne,cible,code\n/a,/b,301,extra\n',
            'ancienne,cible,code\n/a,/b\n',
            'source,target,status\n/a,/b,301\n',
            'ancienne,cible,code\n',
            'ancienne,cible,code\n/a#fragment,/b,301\n',
            'ancienne,cible,code\n/../a,/b,301\n',
            'ancienne,cible,code\n/%2E%2e/a,/b,301\n',
            'ancienne,cible,code\n/%2fexample.org,/b,301\n',
            'ancienne,cible,code\n/a,/b%0d%0aX,301\n',
            'ancienne,cible,code\n/a,/bad%,301\n',
            'ancienne,cible,code\n/a,/b\\evil,301\n',
            'ancienne,cible,code\n/a,/b,301\n\n',
            'ancienne,cible,code\n/a,/b,301\n/%61,/c,301\n',
        ]
        with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as tmp:
            path = pathlib.Path(tmp)/'plan.csv'
            for content in bad:
                with self.subTest(content=content):
                    path.write_text(content, encoding='utf8')
                    with self.assertRaisesRegex(ValueError, 'A09_PLAN'):
                        m.load_plan(path)
            path.write_text('ancienne,cible,code\n/a,/b,301\n', encoding='utf8')
            link = pathlib.Path(tmp)/'link.csv'
            link.symlink_to(path)
            with self.assertRaisesRegex(ValueError, 'A09_PLAN'):
                m.load_plan(link)
        with tempfile.TemporaryDirectory() as tmp:
            outside = pathlib.Path(tmp)/'plan.csv'
            outside.write_text('ancienne,cible,code\n/a,/b,301\n', encoding='utf8')
            with self.assertRaisesRegex(ValueError, 'A09_PLAN'):
                m.load_plan(outside)


class SiteTest(unittest.TestCase):
    def test_declared_origin_requires_all_native_verified_staging_guards(self):
        import json
        import shutil
        m = subject()
        with tempfile.TemporaryDirectory() as tmp:
            site = pathlib.Path(tmp)/'site'
            site.mkdir()
            native = site/'.imagine-staging-verified.json'
            declaration = site/'.imagine-a09-http.json'
            marker = {'status': 'verified', 'offline_verified': True, 'runtime_probe_passed': True, 'site': 'a09-fiction'}
            decl = {'schema': 'imagine-a09-http-v1', 'kind': 'test', 'base_url': 'http://127.0.0.1:12345'}
            native.write_text(json.dumps(marker))
            declaration.write_text(json.dumps(decl))
            safety = site/'wp-content/mu-plugins/000-imagine-staging-safety.php'
            safety.parent.mkdir(parents=True)
            shutil.copyfile(REPO/'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php', safety)
            self.assertEqual(m.authorize_site(site, decl['base_url']), decl['base_url'])
            for key, bad in [('status', 'production'), ('offline_verified', False), ('runtime_probe_passed', 1)]:
                native.write_text(json.dumps({**marker, key: bad}))
                with self.assertRaisesRegex(ValueError, 'A09_NOT_VERIFIED'):
                    m.authorize_site(site, decl['base_url'])
            native.write_text(json.dumps(marker))
            for url in ['https://127.0.0.1:12345', 'http://127.0.0.1:12346', 'http://example.org']:
                with self.assertRaisesRegex(ValueError, 'A09_DECLARATION'):
                    m.authorize_site(site, url)
            for url in ['http://user:pass@example.org', 'file:///tmp/site', 'http://example.org/x', 'http://example.org?x=1', 'http://example.org#fragment']:
                with self.assertRaises(ValueError):
                    m.authorize_site(site, url)
            declaration.write_text(json.dumps({**decl, 'kind': 'production'}))
            with self.assertRaisesRegex(ValueError, 'A09_DECLARATION'):
                m.authorize_site(site, decl['base_url'])
            declaration.write_text(json.dumps(decl))
            safety.write_text('tampered synthetic fixture')
            with self.assertRaisesRegex(ValueError, 'A09_SAFETY_BYTES'):
                m.authorize_site(site, decl['base_url'])


class OriginStrictTest(unittest.TestCase):
    def test_port_zero_and_even_empty_userinfo_are_not_repaired(self):
        m = subject()
        for value in ['http://example.org:0', 'http://@example.org', 'http://user@example.org']:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    m.origin(value)


if __name__ == '__main__':
    unittest.main()
