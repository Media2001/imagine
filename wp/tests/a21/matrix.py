"""Real Windows console matrix, with explicit child encodings and new scratch output."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PROBE="import json,locale,sys; print(json.dumps({'executable':sys.executable,'version':sys.version,'version_info':list(sys.version_info[:3]),'platform':sys.platform,'stdout':sys.stdout.encoding,'stderr':sys.stderr.encoding,'locale':locale.getencoding(),'preferred':locale.getpreferredencoding(False),'utf8_mode':sys.flags.utf8_mode}))"

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    out=args.output.resolve()
    assert sys.platform=='win32' and not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False,parents=True)
    rows=[]
    for console,encoding,utf8 in [('cp1252','cp1252','0'),('utf8','utf-8','1')]:
        env={**os.environ,'PYTHONIOENCODING':encoding,'PYTHONUTF8':utf8,'PYTHONDONTWRITEBYTECODE':'1',
             'TMPDIR':'C:/Users/Ced/AppData/Local/hermes/cache/scratch'}
        def run(label,arguments,timeout):
            command=[sys.executable,'-B',*arguments]
            p=subprocess.run(command,env=env,text=True,encoding=encoding,capture_output=True,timeout=timeout,cwd=ROOT)
            (out/(console+'-'+label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
            rows.append({'console':console,'label':label,'command':command,'child_encoding':encoding,'exit_code':p.returncode})
            return p
        probe=run('environment',['-c',PROBE],30)
        (out/(console+'-environment.json')).write_text(json.dumps(json.loads(probe.stdout),indent=2)+'\n',encoding='utf-8')
        run('python-tests',['-m','unittest','discover','-s','wp/tests/a21','-p','test_*.py'],90)
        run('native',['wp/tests/a22/run.py','--lot=A21','--output='+str(out/(console+'-native'))],1800)
    receipt={'rows':rows,'exit_code':int(any(r['exit_code']!=0 for r in rows))}
    (out/'windows-matrix.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))
    return receipt['exit_code']
if __name__=='__main__':
    sys.exit(main())
