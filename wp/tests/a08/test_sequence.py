"""Contract tests: doubles cover orchestration only, never native proof."""
import importlib.util
import pathlib
import sys
import unittest
sys.dont_write_bytecode = True


def subject():
    path = pathlib.Path('/subject/a08/sequence.py')
    if not path.exists():
        raise AssertionError('A08 implementation missing')
    spec = importlib.util.spec_from_file_location('sequence', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SequenceTest(unittest.TestCase):
    def test_exact_existing_tools_order_and_no_guard_overrides(self):
        m = subject()
        commands = m.commands(pathlib.Path('/subject'), pathlib.Path('/site'), pathlib.Path('/work'),
                              pathlib.Path('/settings'), pathlib.Path('/update'), pathlib.Path('/clean'),
                              pathlib.Path('/backup'), None, None, 1)
        self.assertEqual(list(commands), ['audit', 'avant', 'mise-a-jour', 'nettoyage', 'apres', 'comparaison'])
        self.assertEqual(commands['audit'], ['php', '/subject/audit', '--wp-path=/site', '--output=/work/audit-1'])
        self.assertIn('--state=/work/a04', commands['mise-a-jour'])
        self.assertIn('--state=/work/a05', commands['nettoyage'])
        self.assertIn('/work/avant-1/non-regression.json', commands['comparaison'])
        self.assertNotIn('--renewal-test', str(commands))
        self.assertNotIn('--skip', str(commands))


class ExecutionTest(unittest.TestCase):
    def test_refusal_stops_and_resume_keeps_completed_evidence(self):
        import json
        import tempfile
        from types import SimpleNamespace
        m = subject()
        self.assertTrue(callable(getattr(m, 'main', None)), 'A08 orchestration missing')
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            site = root/'site'
            site.mkdir()
            args = ['--wp-path='+str(site), '--state='+str(root/'state')]
            for key in ['update-plan', 'clean-plan', 'config', 'backup']:
                p = root/key
                p.write_text('{}')
                args.append('--'+key+'='+str(p))
            calls = []
            refusal = [True]
            def runner(command, **kwargs):
                tool = pathlib.Path(command[2] if command[0]=='python3' else command[1]).name
                calls.append(tool)
                rc = 0
                if tool == 'mettre-a-jour' and refusal[0]:
                    rc = 1
                    refusal[0] = False
                for arg in command:
                    if arg.startswith('--output='):
                        out = pathlib.Path(arg.split('=',1)[1]); out.mkdir()
                        filename = 'audit.json' if tool=='audit' else 'non-regression.json'
                        (out/filename).write_text(json.dumps({'php_log':{'checked':True,'errors':0},'private':'BASE_VALUE_CANARY'}))
                stdout = json.dumps({'attendu':2,'anormal':0,'changes':[{'class':'attendu'}]}) if tool=='comparer' else 'BASE_VALUE_CANARY'
                return SimpleNamespace(returncode=3 if tool=='comparer' else rc, stdout=stdout, stderr='A04_MAINTENANCE\n' if rc else '')
            self.assertEqual(m.main(args, runner=runner),75)
            self.assertEqual(calls,['audit','non-regression'])
            self.assertEqual(m.main(args+['--mutations-ready'], runner=runner),1)
            self.assertEqual(calls[-1],'mettre-a-jour')
            checkpoint = json.loads((root/'state/etat.json').read_text())
            self.assertEqual(list(checkpoint['done']),['audit','avant'])
            self.assertEqual(m.main(args+['--mutations-ready'], runner=runner),75)
            self.assertEqual(calls[-2:],['mettre-a-jour','nettoyer'])
            self.assertEqual(m.main(args+['--reception-ready'], runner=runner),0)
            self.assertEqual(calls.count('audit'),1)
            self.assertEqual(calls.count('nettoyer'),1)
            report = (root/'state/rapport.md').read_text()
            self.assertNotIn('BASE_VALUE_CANARY',report)
            self.assertIn('attendus : 2',report)
            self.assertIn('anormaux : 0',report)
            self.assertIn('mise-a-jour',report)
            self.assertIn('Durée',report)
            self.assertEqual(m.main(args, runner=runner),0)
            self.assertEqual(len(calls),7)
            self.assertEqual(m.main(args+['--new-pass'], runner=runner),75)
            self.assertEqual(calls[-2:],['audit','non-regression'])
            self.assertEqual(m.main(args+['--mutations-ready'], runner=runner),75)
            self.assertEqual(m.main(args+['--reception-ready'], runner=runner),0)
            self.assertEqual(len(calls),13)
            self.assertEqual(len(json.loads((root/'state/etat.json').read_text())['passes']),1)


class GuardTest(unittest.TestCase):
    def test_malformed_comparison_has_durable_stop_report(self):
        import json
        import tempfile
        from types import SimpleNamespace
        m = subject()
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp); (root/'site').mkdir()
            args = ['--wp-path='+str(root/'site'),'--state='+str(root/'state'),'--mutations-ready','--reception-ready']
            for key in ['update-plan','clean-plan','config','backup']:
                (root/key).write_text('{}'); args.append('--'+key+'='+str(root/key))
            def fake(command, **kw):
                for arg in command:
                    if arg.startswith('--output='):
                        p = pathlib.Path(arg.split('=',1)[1]); p.mkdir()
                        (p/('audit.json' if command[1].endswith('/audit') else 'non-regression.json')).write_text(json.dumps({'php_log':{'checked':True,'errors':0}}))
                return SimpleNamespace(returncode=0,stdout='not json',stderr='')
            self.assertEqual(m.main(args,runner=fake),1)
            self.assertIn('ARRÊT : comparaison',(root/'state/rapport.md').read_text())
            self.assertEqual(json.loads((root/'state/comparaison-1-receipt.json').read_text())['exit'],0)


if __name__ == '__main__':
    unittest.main()
