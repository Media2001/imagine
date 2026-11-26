"""Windows-compatible launcher and contract tests; no PHP host execution."""
import importlib.util,os,subprocess,sys,unittest
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
class LauncherTest(unittest.TestCase):
    def invoke(self,*args):
        return subprocess.run([sys.executable,'-B',str(ROOT/'wp/outils/bascule/a20/confine.py'),*args],
            env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'},
            capture_output=True,text=True,encoding='utf-8',errors='strict',timeout=30)
    def refusal(self,expected,*args):
        p=self.invoke(*args);self.assertEqual((p.returncode,p.stdout,p.stderr),(1,'',expected+'\n'))
    def test_required_arguments(self):
        self.refusal('A20_USAGE')
    def test_unknown_private_argument(self):
        self.refusal('A20_USAGE','--nom=été-漢-A20_PRIVATE_CANARY')
    def test_duplicate_argument(self):
        self.refusal('A20_USAGE','--output=x','--output=y')
    def test_empty_argument(self):
        self.refusal('A20_USAGE','--wp-path=')
    def test_only_documented_three_paths_reach_validation(self):
        p=ROOT/'wp/tests/a20/A20_NONEXISTENT_SITE';self.assertFalse(p.exists())
        self.refusal('A20_CONFINEMENT_FAILED','--wp-path='+str(p),'--audit='+str(p/'audit.json'),'--output='+str(p/'out'))
    def test_shared_contract_exact_two_lines(self):
        lines=(ROOT/'production/A-20/readme-ajout.txt').read_text(encoding='utf-8').splitlines()
        shared=(ROOT/'wp/tests/a02-audit/README.md').read_text(encoding='utf-8').splitlines()
        local=(ROOT/'wp/outils/bascule/a20/README.md').read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(lines),2)
        for line in lines:self.assertEqual(shared.count(line),1)
        command=lines[0].split(' : ',1)[1]
        self.assertIn(command,local)
    def test_no_native_dependency_in_pure_rules(self):
        text=(ROOT/'wp/outils/bascule/a20/Analysis.php').read_text(encoding='utf-8')
        for token in ['wpdb','wc_get','get_option','file_put_contents','PDO','WC_Subscription']:
            self.assertNotIn(token,text)
    def test_runner_fixed_scope_and_no_site_or_archive(self):
        spec=importlib.util.spec_from_file_location('a20_run',ROOT/'wp/tests/a20/run.py')
        run=importlib.util.module_from_spec(spec);spec.loader.exec_module(run)
        self.assertEqual(run.OWN,['wp/tests/a20','wp/outils/bascule/a20'])
        text=(ROOT/'wp/tests/a20/run.py').read_text(encoding='utf-8')
        self.assertNotIn("add_argument('--wp-path'",text);self.assertNotIn("add_argument('--archive'",text)
if __name__=='__main__':unittest.main()
