"""Disposable, synthetic HTTP only. Never touches demo/staging API or real sites."""
import csv
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest

REPO = pathlib.Path(__file__).resolve().parents[3]


class HttpFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.events = []
        self.routes = {}
        events, routes = self.events, self.routes
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                events.append({'method': self.command, 'path': self.path, 'at': time.monotonic(), 'port': self.server.server_port})
                status, location, delay = routes.get(self.path, (404, None, 0))
                time.sleep(delay)
                try:
                    self.send_response(status)
                    if location is not None:
                        for value in (location if isinstance(location, list) else [location]):
                            self.send_header('Location', value)
                    self.send_header('Content-Length', '0')
                    self.end_headers()
                except (BrokenPipeError, ConnectionResetError):
                    pass
            def log_message(self, *args):
                pass
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.daemon_threads = True
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        def stop():
            self.server.shutdown()
            self.server.server_close()
            thread.join(timeout=2)
        self.addCleanup(stop)
        self.base = 'http://127.0.0.1:'+str(self.server.server_port)
        self.site = self.root/'site'
        self.site.mkdir()
        (self.site/'.imagine-staging-verified.json').write_text(json.dumps({'status': 'verified', 'offline_verified': True, 'runtime_probe_passed': True, 'site': 'a09-fiction'}))
        (self.site/'.imagine-a09-http.json').write_text(json.dumps({'schema': 'imagine-a09-http-v1', 'kind': 'test', 'base_url': self.base}))
        safety = self.site/'wp-content/mu-plugins/000-imagine-staging-safety.php'
        safety.parent.mkdir(parents=True)
        shutil.copyfile(REPO/'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php', safety)
        self.before = self.fingerprint()

    def fingerprint(self):
        return {p.relative_to(self.site).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.site.rglob('*') if p.is_file()}

    def run_cli(self, name, rows, extra=None, raw=None):
        tool = REPO/'wp/outils/bascule/tester-redirections'
        self.assertTrue(tool.is_file(), 'A09 CLI missing')
        plan = self.root/(name+'.csv')
        if raw is not None:
            plan.write_text(raw)
        else:
            with plan.open('w', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(['ancienne', 'cible', 'code'])
                writer.writerows(rows)
        out = pathlib.Path('/report')/name
        command = [sys.executable, '-B', str(tool), '--wp-path='+str(self.site), '--base-url='+self.base, '--plan='+str(plan), '--output='+str(out), '--interval=0.1', '--timeout=0.15']+(extra or [])
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        (pathlib.Path('/report')/(name+'-cli.json')).write_text(json.dumps({'command': command, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'events': self.events, 'site_unchanged': self.before == self.fingerprint()}, indent=2)+'\n')
        self.assertEqual(self.before, self.fingerprint(), 'checker wrote to site')
        return result, out


class ConformHttpTest(HttpFixture):
    def test_one_hop_good_code_target_and_200_with_limited_gets(self):
        self.routes.update({'/ancien-fictif': (301, '/nouveau-fictif', 0), '/nouveau-fictif': (200, None, 0)})
        result, out = self.run_cli('conforme', [('/ancien-fictif', '/nouveau-fictif', 301)])
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((out/'rapport.json').read_text())
        self.assertEqual(report['nonconformes'], 0)
        self.assertEqual(report['rows'][0]['issues'], [])
        self.assertEqual(report['rows'][0]['hops'], 1)
        self.assertEqual([(e['method'], e['path']) for e in self.events], [('GET', '/ancien-fictif'), ('GET', '/nouveau-fictif')])
        self.assertGreaterEqual(self.events[1]['at']-self.events[0]['at'], 0.09)
        self.assertIn('CONFORME', (out/'rapport.md').read_text())
        with (out/'nonconformes.csv').open() as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 0)
        self.assertIn('CONFORME', result.stdout)


class DefectHttpTest(HttpFixture):
    def assert_defect(self, name, routes, expected, paths=None):
        self.routes.update(routes)
        result, out = self.run_cli(name, [('/depart', '/attendu', 301), ('/ok', '/fin', 301)])
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads((out/'rapport.json').read_text())
        self.assertEqual(report['total'], 2)
        self.assertEqual(report['nonconformes'], 1)
        self.assertIn(expected, report['rows'][0]['issues'])
        self.assertEqual(report['rows'][1]['issues'], [])
        with (out/'nonconformes.csv').open(encoding='utf-8-sig') as stream:
            csv_rows = list(csv.DictReader(stream))
        self.assertEqual(len(csv_rows), 1)
        self.assertIn(expected, csv_rows[0]['issues'])
        self.assertIn(expected, result.stdout)
        if paths is not None:
            self.assertEqual([e['path'] for e in self.events], paths+['/ok', '/fin'])

    def setUp(self):
        super().setUp()
        self.routes.update({'/ok': (301, '/fin', 0), '/fin': (200, None, 0)})

    def test_wrong_code_is_nonconform_and_remaining_rows_are_checked(self):
        self.assert_defect('mauvais-code', {'/depart': (302, '/attendu', 0), '/attendu': (200, None, 0)}, 'mauvais_code', ['/depart', '/attendu'])

    def test_wrong_target_is_nonconform(self):
        self.assert_defect('mauvaise-cible', {'/depart': (301, '/autre', 0), '/autre': (200, None, 0)}, 'mauvaise_cible', ['/depart', '/autre'])

    def test_target_404_is_nonconform(self):
        self.assert_defect('cible-404', {'/depart': (301, '/attendu', 0), '/attendu': (404, None, 0)}, 'cible_non_200', ['/depart', '/attendu'])

    def test_target_503_is_nonconform(self):
        self.assert_defect('cible-503', {'/depart': (301, '/attendu', 0), '/attendu': (503, None, 0)}, 'cible_non_200', ['/depart', '/attendu'])

    def test_timeout_is_nonconform(self):
        self.assert_defect('timeout', {'/depart': (301, '/attendu', 0), '/attendu': (200, None, 0.4)}, 'delai_depasse', ['/depart', '/attendu'])

    def test_source_200_is_not_a_redirect(self):
        self.assert_defect('source-200', {'/depart': (200, None, 0)}, 'mauvais_code', ['/depart'])

    def test_missing_location_is_nonconform(self):
        self.assert_defect('sans-location', {'/depart': (301, None, 0)}, 'redirection_invalide', ['/depart'])

    def test_multiple_locations_are_not_guessed(self):
        self.assert_defect('double-location', {'/depart': (301, ['/attendu', '/autre'], 0)}, 'redirection_invalide', ['/depart'])


class ChainHttpTest(HttpFixture):
    def test_chain_loop_and_jump_limit_are_distinct_and_bounded(self):
        self.routes.update({'/chaine': (301, '/intermediaire', 0), '/intermediaire': (302, '/final', 0), '/final': (200, None, 0),
                            '/boucle': (301, '/boucle-b', 0), '/boucle-b': (301, '/boucle', 0), '/auto': (301, '/auto', 0)})
        self.routes.update({'/long'+str(i): (301, '/long'+str(i+1), 0) for i in range(20)})
        result, out = self.run_cli('chaines-boucles', [('/chaine', '/final', 301), ('/boucle', '/boucle-b', 301), ('/auto', '/final', 301), ('/long0', '/final', 301)])
        self.assertEqual(result.returncode, 1, result.stderr)
        rows = json.loads((out/'rapport.json').read_text())['rows']
        self.assertIn('chaine', rows[0]['issues'])
        self.assertEqual(rows[0]['hops'], 2)
        self.assertEqual(rows[0]['final_status'], 200)
        self.assertIn('boucle', rows[1]['issues'])
        self.assertIn('boucle', rows[2]['issues'])
        self.assertIn('limite_sauts', rows[3]['issues'])
        paths = [e['path'] for e in self.events]
        self.assertEqual(paths[:6], ['/chaine', '/intermediaire', '/final', '/boucle', '/boucle-b', '/auto'])
        self.assertEqual(paths[6:], ['/long'+str(i) for i in range(9)])

    def test_external_first_and_later_locations_never_reach_other_origin(self):
        trap = ThreadingHTTPServer(('127.0.0.1', 0), self.server.RequestHandlerClass)
        trap.daemon_threads = True
        thread = threading.Thread(target=trap.serve_forever, daemon=True)
        thread.start()
        def stop():
            trap.shutdown()
            trap.server_close()
            thread.join(timeout=2)
        self.addCleanup(stop)
        external = 'http://127.0.0.1:'+str(trap.server_port)+'/never-visit'
        self.routes.update({'/externe': (301, external, 0), '/plus-tard': (301, '/hop', 0), '/hop': (302, external, 0),
                            '/protocole': (301, external.removeprefix('http:'), 0), '/schema': (301, 'mailto:nobody@example.org', 0)})
        result, out = self.run_cli('externes', [('/externe', '/final', 301), ('/plus-tard', '/hop', 301), ('/protocole', '/final', 301), ('/schema', '/final', 301)])
        self.assertEqual(result.returncode, 1, result.stderr)
        rows = json.loads((out/'rapport.json').read_text())['rows']
        for row in rows:
            self.assertIn('cible_externe', row['issues'])
        self.assertIn('chaine', rows[1]['issues'])
        self.assertFalse(any(e['port'] == trap.server_port for e in self.events), 'external trap was visited')
        self.assertEqual([e['path'] for e in self.events], ['/externe', '/plus-tard', '/hop', '/protocole', '/schema'])
        (pathlib.Path('/report')/'external-trap.json').write_text(json.dumps({'listening_origin': external, 'received_requests': [e for e in self.events if e['port'] == trap.server_port], 'tested_origin': self.base}, indent=2)+'\n')

