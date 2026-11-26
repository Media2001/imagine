"""Run the complete A20 Windows UTF-8/cp1252 matrix into a fresh scratch folder."""
import argparse,importlib.util,json,os,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
    if sys.platform!='win32':raise RuntimeError('A20_WINDOWS_REQUIRED')
    out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    rows=[]
    probe="import sys,locale,json; print(json.dumps({'platform':sys.platform,'executable':sys.executable,'version':sys.version,'version_info':list(sys.version_info[:3]),'stdout':sys.stdout.encoding,'stderr':sys.stderr.encoding,'locale':locale.getencoding(),'preferred':locale.getpreferredencoding(False),'utf8_mode':sys.flags.utf8_mode}))"
    def execute(command,env,encoding,log):
        p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding=encoding,errors='strict',timeout=1800)
        log.write_text(p.stdout+p.stderr,encoding='utf-8')
        rows.append({'command':command,'console':encoding,'exit_code':p.returncode})
        return p
    for console,encoding,mode in [('utf8','utf-8','1'),('cp1252','cp1252','0')]:
        folder=out/console;folder.mkdir()
        env={**os.environ,'PYTHONIOENCODING':encoding,'PYTHONUTF8':mode,'PYTHONDONTWRITEBYTECODE':'1',
            'TMPDIR':'C:/Users/Ced/AppData/Local/hermes/cache/scratch'}
        p=subprocess.run([sys.executable,'-B','-c',probe],env=env,capture_output=True,text=True,encoding=encoding,errors='strict',timeout=30)
        if p.returncode:raise RuntimeError('A20_ENVIRONMENT_PROBE_FAILED')
        (folder/'environment.json').write_text(json.dumps(json.loads(p.stdout),indent=2)+'\n',encoding='utf-8')
        execute([sys.executable,'-B','-m','unittest','discover','-s','wp/tests/a20','-p','test_*.py','-v'],env,encoding,folder/'launcher-tests.log')
        execute([sys.executable,'-B','wp/tests/a20/run.py','--output='+str(folder/'native')],env,encoding,folder/'runner-console.log')
    env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'}
    execute([sys.executable,'-B','wp/tests/a20/style.py','--output='+str(out/'style')],env,'utf-8',out/'style-console.log')
    spec=importlib.util.spec_from_file_location('runner',HERE/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    (out/'sources.json').write_text(json.dumps(r.manifest(r.OWN),indent=2)+'\n',encoding='utf-8')
    (out/'candidate.json').write_text(json.dumps({'status':'CANDIDAT_GATE_PARENT','parent_preparation':'pending','parent_global_T01':'pending','readiness_claimed':False},indent=2)+'\n',encoding='utf-8')
    receipt={'rows':rows,'exit_code':int(any(row['exit_code']!=0 for row in rows))}
    (out/'windows-matrix.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2));return receipt['exit_code']
if __name__=='__main__':sys.exit(main())
