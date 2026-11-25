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
                stdout = json.dumps({'anormal':0,'changes':[{'class':'attendu'},{'class':'attendu'}]}) if tool=='comparer' else 'BASE_VALUE_CANARY'
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


class BoundaryTest(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name);self.site=self.root/'site';self.site.mkdir()
        self.args=['--wp-path='+str(self.site),'--state='+str(self.root/'state')]
        for key in ['update-plan','clean-plan','config','backup']:
            path=self.root/key;path.write_text('{}');self.args.append('--'+key+'='+str(path))
        self.module=subject();self.calls=[];self.compare_code=0;self.log_errors=0
        self.compare={'attendu':0,'anormal':0,'changes':[]}

    def fake(self,command,**kw):
        import json
        from types import SimpleNamespace
        self.calls.append(command)
        for argument in command:
            if argument.startswith('--output='):
                path=pathlib.Path(argument.split('=',1)[1]);path.mkdir()
                (path/('audit.json' if command[1].endswith('/audit') else 'non-regression.json')).write_text(json.dumps({'php_log':{'checked':True,'errors':self.log_errors}}))
        compare=command[1].endswith('/comparer')
        return SimpleNamespace(returncode=self.compare_code if compare else 0,stdout=json.dumps(self.compare) if compare else '',stderr='')

    def execute(self,extra=()):
        return self.module.main(self.args+list(extra),runner=self.fake)

    def test_changed_input_refuses_before_call(self):
        self.assertEqual(self.execute(),75)
        (self.root/'config').write_text('{"changed":true}')
        self.assertEqual(self.execute(['--mutations-ready']),1)
        self.assertEqual(len(self.calls),2)
        self.assertIn('A08_IDENTITY_CHANGED',(self.root/'state/rapport.md').read_text())
        self.assertIn('ARRÊT',(self.root/'state/rapport.md').read_text())

    def test_child_symlink_in_state_refused_without_native_call(self):
        state=self.root/'state';state.mkdir()
        sentinel=self.root/'sentinel';sentinel.write_text('intact')
        (state/'audit-1-stdout.log').symlink_to(sentinel)
        self.assertEqual(self.execute(),1)
        self.assertEqual(self.calls,[])
        self.assertEqual(sentinel.read_text(),'intact')

    def test_changed_completed_proof_refuses_before_call(self):
        self.assertEqual(self.execute(),75)
        (self.root/'state/avant-1/non-regression.json').write_text('{}')
        self.assertEqual(self.execute(['--mutations-ready']),1)
        self.assertEqual(len(self.calls),2)

    def test_site_output_refused(self):
        self.args[1]='--state='+str(self.site/'unsafe')
        self.assertEqual(self.execute(),1);self.assertEqual(self.calls,[])
        self.assertFalse((self.site/'unsafe').exists())

    def test_native_anomaly_code_two_never_requalified(self):
        import json
        self.compare_code=2;self.compare={'attendu':0,'anormal':1,'changes':[{'class':'anormal'}]}
        self.assertEqual(self.execute(['--mutations-ready','--reception-ready']),2)
        state=json.loads((self.root/'state/etat.json').read_text())
        self.assertNotIn('comparaison',state['done'])
        self.assertIn('anormaux : 1',(self.root/'state/rapport.md').read_text())
        self.assertEqual(len(self.calls),6)

    def test_nonzero_child_with_plausible_json_never_success(self):
        self.compare_code=1
        self.assertEqual(self.execute(['--mutations-ready','--reception-ready']),1)
        self.assertIn('ARRÊT : comparaison',(self.root/'state/rapport.md').read_text())

    def test_dirty_php_log_blocks_before_mutations(self):
        self.log_errors=1
        self.assertEqual(self.execute(['--mutations-ready','--reception-ready']),1)
        self.assertEqual(len(self.calls),2)
        self.assertIn('ARRÊT : avant',(self.root/'state/rapport.md').read_text())

    def test_missing_native_executable_is_durable_refusal(self):
        def missing(*args,**kw):raise FileNotFoundError('PRIVATE_CANARY')
        self.assertEqual(self.module.main(self.args,runner=missing),1)
        text=(self.root/'state/rapport.md').read_text()
        self.assertIn('ARRÊT : audit',text);self.assertNotIn('PRIVATE_CANARY',text)

    def test_no_new_pass_until_complete(self):
        self.assertEqual(self.execute(['--new-pass']),1);self.assertEqual(self.calls,[])

    def test_site_lock_cannot_be_bypassed_by_other_state(self):
        import fcntl
        import hashlib
        path=pathlib.Path('/tmp')/('imagine-a08-'+hashlib.sha256(str(self.site.resolve()).encode()).hexdigest()+'.lock')
        with open(path,'a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.assertEqual(self.execute(),1);self.assertEqual(self.calls,[])

    def test_dependency_closure_refuses_external_code_but_ignores_other_lots(self):
        import shutil
        base=self.root/'copy/wp/outils/bascule'
        shutil.copytree('/subject',base)
        shutil.copytree('/plugins',self.root/'copy/wp/plugins')
        shutil.copytree('/staging',self.root/'copy/wp/outils/staging')
        self.module.__file__=str(base/'a08/sequence.py')
        self.assertEqual(self.execute(),75)
        for relative in ['a09/check.py','a10/Inventory.php','inventorier-codes','README.md']:
            p=base/relative;p.parent.mkdir(exist_ok=True);p.write_text('unrelated')
        self.assertEqual(self.execute(),75)
        for relative in ['plugins/imagine-non-regression/src/Report.php',
                         'plugins/imagine-non-regression/src/PhpLog.php',
                         'plugins/imagine-non-regression/src/Policy.php',
                         'outils/staging/runtime-probe.php',
                         'outils/staging/mu-plugins/000-imagine-staging-safety.php']:
            p=self.root/'copy/wp'/relative;before=p.read_bytes();p.write_bytes(before+b'\n')
            count=len(self.calls)
            self.assertEqual(self.execute(['--mutations-ready']),1,relative)
            self.assertEqual(len(self.calls),count)
            self.assertIn('A08_IDENTITY_CHANGED',(self.root/'state/rapport.md').read_text())
            p.write_bytes(before)

    def test_missing_input_after_success_replaces_stale_report(self):
        self.assertEqual(self.execute(['--mutations-ready','--reception-ready']),0)
        (self.root/'config').unlink();count=len(self.calls)
        self.assertEqual(self.execute(),1)
        self.assertEqual(len(self.calls),count)
        self.assertIn('ARRÊT',(self.root/'state/rapport.md').read_text())
        self.assertNotIn('Statut : TERMINÉ',(self.root/'state/rapport.md').read_text())

    def test_incomplete_new_pass_refreshes_report(self):
        self.assertEqual(self.execute(),75)
        self.assertEqual(self.execute(['--new-pass']),1)
        self.assertIn('A08_PASS_NOT_COMPLETE',(self.root/'state/rapport.md').read_text())

    def test_concurrent_refusal_leaves_report_and_warns_stderr(self):
        import contextlib,fcntl,io
        self.assertEqual(self.execute(),75)
        p=self.root/'state/rapport.md';before=p.read_bytes();stderr=io.StringIO()
        with open(self.root/'state/sequence.lock','a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(self.execute(),1)
        self.assertEqual(p.read_bytes(),before)
        self.assertIn('A08_REPORT_NOT_UPDATED',stderr.getvalue())
        self.assertIn('ne décrit pas cette tentative',stderr.getvalue())

    def test_unreadable_checkpoint_reports_without_erasing_failure(self):
        self.assertEqual(self.execute(),75)
        p=self.root/'state/etat.json';p.write_text('invalid')
        self.assertEqual(self.execute(),1)
        self.assertEqual(p.read_text(),'invalid')
        self.assertIn('ARRÊT',(self.root/'state/rapport.md').read_text())

    def test_missing_fcntl_stable_no_traceback(self):
        import builtins,contextlib,io
        from unittest.mock import patch
        original=builtins.__import__
        def importing(name,*args,**kwargs):
            if name=='fcntl':raise ImportError('PRIVATE_CANARY')
            return original(name,*args,**kwargs)
        stderr=io.StringIO()
        with patch('builtins.__import__',side_effect=importing),contextlib.redirect_stderr(stderr):
            self.assertEqual(self.execute(),1)
        self.assertIn('A08_LINUX_REQUIRED',stderr.getvalue())
        self.assertNotIn('PRIVATE_CANARY',stderr.getvalue())
        self.assertNotIn('Traceback',stderr.getvalue())

    def test_pass_reports_retain_first_comparison_and_attributed_durations(self):
        import json
        self.compare_code=3;self.compare={'anormal':0,'changes':[{'class':'attendu'}]*4}
        self.assertEqual(self.execute(['--mutations-ready','--reception-ready']),0)
        self.compare_code=0;self.compare={'anormal':0,'changes':[]}
        self.assertEqual(self.execute(['--new-pass','--mutations-ready','--reception-ready']),0)
        cp=json.loads((self.root/'state/etat.json').read_text())
        self.assertEqual([r['pass'] for r in cp['attempts']],[1]*6+[2]*6)
        text=(self.root/'state/rapport.md').read_text()
        for token in ['Passage 1','Passage 2','attendus : 4','attendus : 0','cumulées dans ce passage']:
            self.assertIn(token,text)
        self.assertEqual(len(list((self.root/'state').glob('rapport*.md'))),1)

    def test_go_attestations_forwarded_separately(self):
        commands=self.module.commands(pathlib.Path('/subject'),self.site,self.root/'state',self.root/'config',self.root/'update-plan',self.root/'clean-plan',self.root/'backup',pathlib.Path('/go-a04'),pathlib.Path('/go-a05'),1)
        self.assertIn('--go=/go-a04',commands['mise-a-jour'])
        self.assertNotIn('--go=/go-a05',commands['mise-a-jour'])
        self.assertIn('--go=/go-a05',commands['nettoyage'])


if __name__ == '__main__':
    unittest.main()
