"""Synthetic-only tests; never contact the shared Docker daemon."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from api import config, models


class SubscriptionGateTest(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parent.parent / '.synthetic-test-scratch'
        scratch.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix='synthetic-subscriptions-', dir=scratch)
        self.root = Path(self.tmp.name)
        self.db = patch.object(config, 'DB_PATH', self.root / 'dashboard.db')
        self.db.start()
        models.init_db()

    def tearDown(self):
        self.db.stop()
        self.tmp.cleanup()

    def test_unverified_profile_cannot_gain_access_by_changing_runtime_status(self):
        from api import subscriptions
        for status in ('creating', 'imported', 'running', 'stopped', 'error', 'verified'):
            with self.subTest(status=status):
                with self.assertRaises(subscriptions.QuarantineError):
                    subscriptions.require_verified({'profile': 'subscriptions', 'status': status,
                                                    'verification_state': 'imported'})
        subscriptions.require_verified({'profile': 'subscriptions', 'verification_state': 'verified'})
        subscriptions.require_verified({'profile': 'sandbox', 'status': 'creating'})


class RecordingEngine:
    def __init__(self, fail=None, version='6.9.1'):
        self.events = []
        self.fail = fail
        self.version = version

    def local_image(self, value):
        self.events.append(('image', value))

    def compose(self, path, *args):
        document = json.loads(path.read_text())
        self.events.append(('compose', document, args))

    def worker(self, image, mounts, executable, request):
        from api import subscriptions as s
        stage = request['stage']
        self.events.append(('worker', stage, mounts, executable, dict(request)))
        if stage == self.fail:
            raise s.QuarantineError('Échec synthétique')
        result = {'protocol': s.PROTOCOL, 'stage': stage, 'ok': True}
        if stage == 'verifier':
            result.update(wordpress_version=self.version,
                          checks={name: True for name in s.REQUIRED_CHECKS})
        if stage == 'novamira':
            result.update(fresh=True, active=True)
        return result


class OfflinePipelineTest(SubscriptionGateTest):
    def prepare(self, fail=None, version='6.9.1'):
        from api import subscriptions as s
        nas = patch.object(config, 'NAS_HOST', 'staging.invalid')
        nas.start()
        self.addCleanup(nas.stop)
        self.engine = RecordingEngine(fail, version)
        self.workflow = self.root / 'workflow'
        for name in s.SCRIPTS.values():
            p = self.workflow / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('<?php // synthetic fixture, never real data')
        self.archive = self.root / 'synthetic.wpress'
        self.archive.write_text('synthetic-only')
        self.sites = patch.object(config, 'SITES_DIR', self.root / 'sites')
        self.host = patch.object(config, 'HOST_SITES_DIR', self.root / 'sites')
        self.sites.start()
        self.host.start()
        self.addCleanup(self.sites.stop)
        self.addCleanup(self.host.stop)
        return s

    def run_import(self, **kw):
        from api import subscriptions as s
        return s.create_offline(name='invented fixture', archive=self.archive,
                                workflow=self.workflow, production_url='https://production.invalid',
                                staging_url='http://staging.invalid:8099', port=8099,
                                worker_image='sha256:' + '1' * 64,
                                db_image='sha256:' + '2' * 64,
                                nginx_image='sha256:' + '3' * 64,
                                admin_password='synthetic-password-only', engine=self.engine, **kw)

    def test_success_never_declares_web_before_all_checks_and_installs_fresh_novamira(self):
        s = self.prepare()
        site = self.run_import()
        self.assertEqual(site['verification_state'], 'verified')
        self.assertEqual(site['status'], 'verified')
        stages = [e[1] for e in self.engine.events if e[0] == 'worker']
        self.assertEqual(stages, ['importer', 'neutraliser', 'anonymiser', 'verifier',
                                  'bascule', 'verifier', 'novamira', 'verifier'])
        documents = [e[1] for e in self.engine.events if e[0] == 'compose']
        self.assertTrue(documents)
        for doc in documents:
            self.assertEqual(set(doc['services']), {'db'})
            self.assertEqual(doc['services']['db']['network_mode'], 'none')
            self.assertNotIn('ports', doc['services']['db'])
        runtime = json.loads((config.SITES_DIR / site['slug'] / 'verified-compose.json').read_text())
        self.assertEqual(runtime['services']['wp']['network_mode'], 'none')
        self.assertEqual(runtime['services']['wp']['user'], '33:33')
        self.assertNotIn('ports', runtime['services']['wp'])
        self.assertEqual(runtime['services']['wp']['restart'], 'no')
        self.assertEqual(runtime['services']['nginx']['ports'], ['8099:80'])
        self.assertTrue(runtime['networks']['verified-web']['internal'])
        self.assertNotIn('synthetic-password-only', json.dumps(site))
        self.assertTrue((config.SITES_DIR / site['slug'] / 'verified-compose.json').exists())

    def test_failed_verifier_leaves_imported_and_no_runtime_compose(self):
        s = self.prepare(fail='verifier')
        with self.assertRaises(s.QuarantineError):
            self.run_import()
        site = models.list_sites()[0]
        self.assertEqual(site['verification_state'], 'imported')
        self.assertEqual(site['status'], 'imported')
        self.assertFalse((config.SITES_DIR / site['slug'] / 'verified-compose.json').exists())
        self.assertNotIn('novamira', [e[1] for e in self.engine.events if e[0] == 'worker'])

    def test_final_verifier_regression_after_novamira_does_not_publish(self):
        s = self.prepare()
        original = self.engine.worker
        calls = []
        def worker(image, mounts, executable, request):
            report = original(image, mounts, executable, request)
            if request['stage'] == 'verifier':
                calls.append(1)
                if len(calls) == 3:
                    report['checks']['mail_blocked'] = False
            return report
        self.engine.worker = worker
        with self.assertRaises(s.QuarantineError):
            self.run_import()
        site = models.list_sites()[0]
        self.assertEqual(site['verification_state'], 'imported')
        self.assertFalse((config.SITES_DIR / site['slug'] / 'verified-compose.json').exists())
        self.assertFalse(s.public_report(site)['checks']['mail_blocked'])

    def test_bascule_failure_prevents_novamira_and_publication(self):
        s = self.prepare(fail='bascule')
        with self.assertRaises(s.QuarantineError):
            self.run_import()
        self.assertNotIn('novamira', [e[1] for e in self.engine.events if e[0] == 'worker'])
        self.assertEqual(models.list_sites()[0]['verification_state'], 'imported')

    def test_importer_failure_remains_quarantined_not_imported(self):
        s = self.prepare(fail='importer')
        with self.assertRaises(s.QuarantineError):
            self.run_import()
        self.assertEqual(models.list_sites()[0]['verification_state'], 'quarantined')
        self.assertEqual([e[1] for e in self.engine.events if e[0] == 'worker'], ['importer'])

    def test_missing_boolean_report_field_is_failure_not_success(self):
        s = self.prepare()
        with self.assertRaises(s.QuarantineError):
            s._valid_report({'protocol': s.PROTOCOL, 'stage': 'verifier', 'ok': True,
                             'wordpress_version': '6.9', 'checks': {}}, 'verifier')
        with self.assertRaises(s.QuarantineError):
            s._valid_report({'protocol': s.PROTOCOL, 'stage': 'novamira', 'ok': True,
                             'fresh': False, 'active': True}, 'novamira')

    def test_input_archive_only_visible_during_import_and_repository_root_never_mounted(self):
        self.prepare()
        self.run_import()
        for event in self.engine.events:
            if event[0] != 'worker':
                continue
            stage, mounts = event[1], event[2]
            targets = [target for _, target, _ in mounts]
            self.assertEqual('/input/source.wpress' in targets, stage == 'importer')
            self.assertNotIn('/workflow', targets)
            self.assertIn('/workflow/wp/outils/staging', targets)
            self.assertEqual('admin' in event[4], stage == 'anonymiser')

    def test_old_wordpress_refuses_novamira_and_bascule(self):
        s = self.prepare(version='6.8.9')
        with self.assertRaises(s.QuarantineError):
            self.run_import()
        stages = [e[1] for e in self.engine.events if e[0] == 'worker']
        self.assertNotIn('novamira', stages)
        self.assertNotIn('bascule', stages)
        self.assertEqual(models.list_sites()[0]['verification_state'], 'imported')


class GuardRoutesTest(SubscriptionGateTest):
    def make_site(self):
        site = dict(slug='synthetic-locked', name='Synthetic', profile='subscriptions',
                    port=8098, php_version='8.3', status='imported', wp_admin_user='fixture',
                    wp_admin_password='', db_password='synthetic', db_root_password='synthetic',
                    created_at=models.now_iso())
        models.insert_site(site)
        models.set_verification(site['slug'], 'imported')
        return models.get_site(site['slug'])

    def test_historical_orchestrator_entrypoints_are_guarded_before_docker_or_files(self):
        from api import orchestrator as o, subscriptions as s
        site = self.make_site()
        cases = [('start_site', (site['slug'],)), ('stop_site', (site['slug'],)),
                 ('destroy_site', (site['slug'],)), ('adopt_mcp', (site['slug'],)),
                 ('_wp', (site['slug'], 'eval', 'die;')),
                 ('_compose', (site['slug'], 'up', '-d')),
                 ('change_php_version', (site['slug'], '8.4')),
                 ('clone_site', (site['slug'], 'Synthetic clone')),
                 ('run_clone_task', ('unrelated-synthetic-source', site['slug'])),
                 ('_do_clone', ({'profile': 'sandbox'}, site)),
                 ('run_import_wpress_task', (site['slug'], self.root / 'absent.wpress')),
                 ('_do_import_wpress', (site, self.root / 'absent.wpress')),
                 ('_render_compose', (site,)), ('run_create_task', (site['slug'],)),
                 ('_provision_site', (site,)), ('list_admins', (site['slug'],)),
                 ('magic_login_url', (site['slug'], 1)), ('export_wpress', (site['slug'],)),
                 ('mcp_connection', (site,)), ('read_theme_file', (site['slug'], 'index.php')),
                 ('write_theme_file', (site['slug'], 'index.php', 'synthetic')),
                 ('create_mcp_credentials', (site,)), ('provision_mcp', (site,)),
                 ('resolve_mcp_admin_user', (site,)), ('validate_mcp_connection', (site,))]
        with patch('subprocess.run', side_effect=AssertionError('Docker must not run')):
            for name, args in cases:
                with self.subTest(name=name), self.assertRaises(s.QuarantineError):
                    getattr(o, name)(*args)
        self.assertEqual(models.get_site(site['slug'])['status'], 'imported')

    def test_middleware_blocks_every_non_metadata_route_before_handler(self):
        import asyncio
        from api.subscription_guards import MutationGuard
        site = self.make_site()
        reached = []
        async def app(scope, receive, send):
            reached.append(scope['path'])
        for method, suffix in [('POST', 'start'), ('POST', 'stop'), ('POST', 'mcp-adopt'),
                               ('POST', 'php-version'), ('POST', 'clone'), ('GET', 'admins'),
                               ('POST', 'admin-login'), ('GET', 'logs'), ('POST', 'export'),
                               ('GET', 'exports'), ('GET', 'export/download/test.wpress'),
                               ('GET', 'mcp-connection'), ('PUT', 'notes'), ('PUT', 'mcp-path'),
                               ('GET', 'future-route'), ('DELETE', '')]:
            sent = []
            async def send(message):
                sent.append(message)
            scope = dict(type='http', method=method, path='/api/sites/' + site['slug'] + '/' + suffix)
            asyncio.run(MutationGuard(app)(scope, None, send))
            self.assertEqual(sent[0]['status'], 423, suffix)
        self.assertFalse(reached)
        scope = dict(type='http', method='GET', path='/api/sites/' + site['slug'])
        asyncio.run(MutationGuard(app)(scope, None, send))
        self.assertEqual(reached, [scope['path']])

    def test_keyword_clone_target_cannot_bypass_persisted_gate(self):
        from api import orchestrator as o, subscriptions as s
        site = self.make_site()
        with self.assertRaises(s.QuarantineError):
            o._do_clone(source={'profile': 'sandbox'}, new_site=site)

    def test_stale_or_forged_site_dictionary_cannot_bypass_persisted_gate(self):
        from api import orchestrator as o, subscriptions as s
        site = self.make_site()
        with self.assertRaises(s.QuarantineError):
            o.mcp_connection(dict(site, profile='sandbox', verification_state='verified'))

    def test_other_profiles_use_exact_original_transport(self):
        from api import orchestrator as o
        with patch.object(models, 'get_site', return_value={'profile': 'sandbox'}), \
             patch.object(o, '_run', return_value='synthetic-result') as run:
            self.assertEqual(o._wp('synthetic-sandbox', 'core', 'version'), 'synthetic-result')
            wrapped = run.call_args
            run.reset_mock()
            self.assertEqual(o._wp.__wrapped__('synthetic-sandbox', 'core', 'version'), 'synthetic-result')
            self.assertEqual(run.call_args, wrapped)

    def test_metadata_response_suppresses_urls_for_unverified_copy(self):
        import ast
        from types import SimpleNamespace
        from api import orchestrator
        source = ast.parse((Path(__file__).parent / 'main.py').read_text())
        fn = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == '_to_response')
        env = dict(config=config, orchestrator=orchestrator, SiteResponse=lambda **kw: kw,
                   subscriptions=__import__('api.subscriptions', fromlist=['subscriptions']))
        exec(compile(ast.Module(body=[fn], type_ignores=[]), '<actual _to_response>', 'exec'), env)
        site = self.make_site()
        response = env['_to_response'](site)
        self.assertEqual(response['url'], '')
        self.assertEqual(response['admin_url'], '')
        self.assertIsNone(response['wp_admin_user'])

    def test_verification_state_survives_stop_and_cannot_be_overridden_by_status(self):
        from api import subscriptions as s
        site = self.make_site()
        models.update_status(site['slug'], 'verified')
        with self.assertRaises(s.QuarantineError):
            s.guard_slug(site['slug'])
        models.set_verification(site['slug'], 'verified')
        models.update_status(site['slug'], 'stopped')
        s.guard_slug(site['slug'])
        models.init_db()
        self.assertEqual(models.get_site(site['slug'])['verification_state'], 'verified')


class EngineIsolationTest(SubscriptionGateTest):
    def test_worker_transport_has_no_ports_network_or_secret_in_argv(self):
        from api.subscription_runtime import Engine
        from api import subscriptions as s
        import subprocess
        request = {'slug': 'synthetic', 'stage': 'anonymiser', 'protocol': s.PROTOCOL,
                   'admin': {'password': 'synthetic-secret'}}
        result = subprocess.CompletedProcess([], 0, json.dumps({'protocol': s.PROTOCOL,
                                                               'stage': 'anonymiser', 'ok': True}))
        with patch('subprocess.run', return_value=result) as run:
            Engine().worker('sha256:' + '1' * 64, [(self.root, '/workflow', True)],
                            '/workflow/wp/outils/staging/anonymiser', request)
        call = run.call_args
        argv = call.args[0]
        self.assertIn('--network=none', argv)
        self.assertIn('--pull=never', argv)
        self.assertIn('--read-only', argv)
        self.assertIn('--cap-drop=ALL', argv)
        self.assertNotIn('synthetic-secret', ' '.join(argv))
        self.assertIn('synthetic-secret', call.kwargs['input'])
        self.assertFalse(any('docker.sock' in arg for arg in argv))
        self.assertFalse(any(arg in ('-p', '--publish', '--network=host') for arg in argv))

    def test_operator_cli_only_prints_public_outcome(self):
        from api import subscription_operator as cli
        import io
        with patch.object(cli, 'read_password', return_value='synthetic-password'), \
             patch.object(cli.models, 'init_db'), \
             patch.object(cli.subscriptions, 'create_offline', return_value={
                 'slug': 'synthetic', 'status': 'verified', 'verification_state': 'verified',
                 'wp_admin_password': 'never-print'}) as create, \
             patch('sys.stdout', new_callable=io.StringIO) as stdout:
            code = cli.main(['--name', 'Synthetic', '--archive', 'synthetic.wpress',
                             '--workflow', 'synthetic-workflow', '--production-url', 'https://production.invalid',
                             '--port', '8099', '--worker-image', 'sha256:' + '1' * 64,
                             '--db-image', 'sha256:' + '2' * 64, '--nginx-image', 'sha256:' + '3' * 64])
        self.assertEqual(code, 0)
        self.assertNotIn('never-print', stdout.getvalue())
        self.assertNotIn('synthetic-password', stdout.getvalue())
        self.assertFalse(any(e[0] == 'compose' and 'nginx' in e[1]['services'] for e in getattr(self, 'engine', RecordingEngine()).events))

    def test_worker_failure_never_echoes_stdout_or_stderr(self):
        from api.subscription_runtime import Engine
        from api import subscriptions as s
        import subprocess
        with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 1, 'PII', 'PII')):
            with self.assertRaises(s.QuarantineError) as ctx:
                Engine()._execute(['synthetic-only'])
        self.assertNotIn('PII', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
