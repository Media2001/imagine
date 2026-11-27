"""T03 local contract tests. Boundary doubles only: NOT a native replay."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('t03_paquets', HERE / 'paquets.py')
paquets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(paquets)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='t03-contract-', dir=os.environ.get('TMPDIR'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.lot = self.root / 'production/A-22'
        self.lot.mkdir(parents=True)
        (self.lot / 'verify.py').write_text('# Never executed on host.\n', encoding='utf-8')
        self.execute = Mock(side_effect=AssertionError('Undeclared verifier was launched'))

    def declare(self, **changes):
        value = {'schema': 1, 'entrypoint': 'verify.py', 'requires': [],
                 'logs': ['production/A-22/preuves/final/native.stdout.log'],
                 'controls': ['exact_packet_inventory_and_hashes', 'PACKAGE_DRIFT']}
        value.update(changes)
        (self.lot / 'rejeu.json').write_text(json.dumps(value), encoding='utf-8')
        return value

    def test_missing_declared_log_is_outside_not_failed(self):
        self.declare()
        result = paquets.replay(self.root, execute=self.execute)
        self.assertEqual(result, {'verified': 0, 'failures': [], 'excluded': [
            {'lot': 'A-22', 'reason': 'journaux absents'}]})
        self.execute.assert_not_called()

    def test_invalid_declaration_is_closed_and_never_executed(self):
        for changes in ({'schema': True}, {'extra': 'secret'}, {'entrypoint': '../run.py'},
                        {'requires': ['wsl']}, {'logs': ['../../secret.log']},
                        {'logs': ['production/A-23/private.log']},
                        {'controls': ['secret /path']}, {'controls': ['PACKAGE_DRIFT', 'PACKAGE_DRIFT']}):
            with self.subTest(changes=changes):
                self.declare(**changes)
                result = paquets.replay(self.root, execute=self.execute)
                self.assertEqual(result['failures'], [{'lot': 'A-22', 'control': 'DECLARATION_INVALID'}])
                self.execute.assert_not_called()

    def test_unsupported_requirements_are_outside_with_fixed_reason(self):
        for requirement, reason in [('docker', 'Docker requis'), ('network', 'reseau requis'),
                                    ('repository-write', 'ecriture depot requise'), ('arguments', 'argument requis')]:
            self.declare(requires=[requirement])
            result = paquets.replay(self.root, execute=self.execute)
            self.assertEqual(result['excluded'], [{'lot': 'A-22', 'reason': reason}])
            self.execute.assert_not_called()

    def test_undeclared_verifier_is_outside_without_execution(self):
        result = paquets.replay(self.root, execute=self.execute)
        self.assertEqual(result, {'verified': 0, 'failures': [], 'excluded': [
            {'lot': 'A-22', 'reason': 'declaration absente'}]})
        self.execute.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
