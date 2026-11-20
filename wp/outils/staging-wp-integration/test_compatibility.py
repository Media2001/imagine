"""Synthetic orchestration/worker contract checks; no tool checkout or daemon.

The transport and dashboard storage below are test doubles, NOT an E2E receipt.
"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent

def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value

worker = load('worker', HERE / 'worker/worker.py')
native = load('a01_native_runtime', HERE / 'worker/runtime.py')
PKG = 'a01_synthetic_api'
pkg = types.ModuleType(PKG)
pkg.__path__ = [str(HERE / 'overlay/api')]
sys.modules[PKG] = pkg
config = types.ModuleType(PKG + '.config')
models = types.ModuleType(PKG + '.models')
orch = types.ModuleType(PKG + '.orchestrator')
sys.modules[config.__name__] = config
sys.modules[models.__name__] = models
sys.modules[orch.__name__] = orch
subscriptions = load(PKG + '.subscriptions', HERE / 'overlay/api/subscriptions.py')

class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='a01-contract-')
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        config.SITES_DIR = config.HOST_SITES_DIR = root / 'sites'
        config.NAS_HOST = 'staging.invalid'
        self.records = {}
        models.get_site = lambda slug: self.records.get(slug)
        models.used_ports = lambda: []
        models.now_iso = lambda: '2026-11-20T00:00:00+00:00'
        models.insert_site = lambda site: self.records.update({site['slug']: dict(site)})
        models.set_verification = lambda slug, state: self.records[slug].update(verification_state=state)
        models.update_status = lambda slug, state, *args: self.records[slug].update(status=state)
        models.log_site = lambda *args: None
        orch.slugify = lambda name: 'synthetic-contract'
        self.workflow = root / 'workflow'
        for relative in subscriptions.SCRIPTS.values():
            file = self.workflow / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('synthetic source marker; never executed')
        self.archive = root / 'synthetic.wpress'
        self.archive.write_bytes(b'SYNTHETIC-NEVER-IMPORTED')
        self.events = []
        owner = self
        class Engine:
            def local_image(self, image):
                pass
            def compose(self, path, *args):
                owner.events.append(('compose', json.loads(path.read_text())))
            def worker(self, image, mounts, executable, request):
                native.validate(request, request['stage'])
                owner.events.append(('worker', executable, request))
                r = dict(protocol=subscriptions.PROTOCOL, stage=request['stage'], ok=True)
                if request['stage'] == 'verifier':
                    r.update(wordpress_version='6.9', checks={k: True for k in subscriptions.REQUIRED_CHECKS})
                    r.update(warnings=['TABLE_INCONNUE_CONSERVEE'], unknown_tables=[
                        dict(name='wp_synthetic', columns=['id', 'email'], rows=1,
                             personal_columns=['email'], decision={'action': 'garder'}, private_value='DO-NOT-EXPOSE')])
                if request['stage'] == 'novamira':
                    r.update(fresh=True, active=True)
                return r
        self.engine = Engine()

    def run_import(self, **kwargs):
        return subscriptions.create_offline(name='Synthetic', archive=self.archive, workflow=self.workflow,
            production_url='https://production.invalid', staging_url='http://staging.invalid:8099', port=8099,
            worker_image='sha256:' + '1' * 64, db_image='sha256:' + '2' * 64,
            nginx_image='sha256:' + '3' * 64, admin_password='SYNTHETIC-EPHEMERAL-NOT-REAL', engine=self.engine, **kwargs)

    def test_generated_requests_pass_the_actual_worker_validator(self):
        site = self.run_import()
        self.assertEqual(site['verification_state'], 'verified')
        calls = [e for e in self.events if e[0] == 'worker']
        self.assertEqual([e[2]['stage'] for e in calls],
            ['importer', 'neutraliser', 'anonymiser', 'verifier', 'bascule', 'verifier', 'novamira', 'verifier'])
        for _, executable, r in calls:
            self.assertEqual(executable, '/opt/staging/' + r['stage'])
            self.assertEqual('admin' in r, r['stage'] == 'anonymiser')
        manifest = json.loads((config.SITES_DIR / site['slug'] / 'offline-compose.json').read_text())
        self.assertEqual(manifest['services']['db']['environment']['MARIADB_DATABASE'], 'wordpress_staging')
        self.assertEqual(set(manifest['services']), {'db'})

    def test_unknown_tables_check_is_mandatory_for_publication(self):
        report = dict(protocol=subscriptions.PROTOCOL, stage='verifier', ok=True, wordpress_version='6.9',
            checks={k: True for k in subscriptions.REQUIRED_CHECKS})
        report['checks'].pop('unknown_tables_resolved', None)
        with self.assertRaises(subscriptions.QuarantineError):
            subscriptions._valid_report(report, 'verifier')

    def test_safe_schema_report_reaches_operator_without_row_values(self):
        site = self.run_import()
        report = subscriptions.public_report(site)
        self.assertEqual(report.get('warnings'), ['TABLE_INCONNUE_CONSERVEE'])
        self.assertEqual(report.get('unknown_tables', [])[0]['columns'], ['id', 'email'])
        self.assertNotIn('DO-NOT-EXPOSE', json.dumps(report))

    def test_operator_decisions_reach_the_worker_unchanged(self):
        decisions = {'wp_synthetic': {'action': 'anonymiser', 'columns': ['email']}}
        self.run_import(table_decisions=decisions)
        for event in self.events:
            if event[0] == 'worker':
                self.assertEqual(event[2]['table_decisions'], decisions)

    def test_worker_does_not_require_a_missing_subscriptions_plugin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'wp-includes').mkdir()
            (root / 'wp-includes/version.php').write_text("<?php $wp_version = '6.9';")
            state = dict(prefix='wp_', phases=['importer', 'neutraliser', 'anonymiser'], files={})
            with patch.object(native, 'ROOT', root), patch.object(native, 'load', return_value=state), \
                 patch.object(native, 'inventory', return_value={}), patch.object(native, 'save'), \
                 patch.object(native, 'assets', return_value={}), patch.object(native, 'digest', return_value='0' * 64), \
                 patch.object(native, 'run_php', return_value={'ok': True, 'issues': [], 'warnings': []}):
                state['files']['wp-content/mu-plugins/000-imagine-staging-safety.php'] = '0' * 64
                with patch.object(native, 'inventory', return_value=state['files']):
                    report = native.adapt({'stage': 'verifier'})
            self.assertTrue(report['checks']['unknown_tables_resolved'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
