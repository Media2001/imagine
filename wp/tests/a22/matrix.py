"""Run closed native banks twice on Windows; never prepare the global image."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
LOTS=['A02','A03','A10','A11','A12','A14','A15','A16','A17','A18','A19']
DIRS={'A02':'a02-audit','A03':'a03-non-regression',**{x:x.lower() for x in LOTS if x not in {'A02','A03'}}}
NO_PYTHON=['A03','A11']
PYTHON_LOTS=[lot for lot in LOTS if lot not in NO_PYTHON]+['A22']


def sources():
    paths=['wp/tests/a22','wp/outils/bascule/stream_guard.py','wp/outils/bascule/stream_refusals.json',
           'wp/outils/bascule/stream_bridge.php','wp/outils/bascule/non-regression','wp/outils/bascule/audit',
           'wp/outils/bascule/inventorier-codes','wp/outils/bascule/rapprocher-contacts','wp/outils/bascule/controler-export',
           'wp/outils/staging','wp/plugins/imagine-non-regression',
           'wp/outils/bascule/a20/confine.py','wp/outils/bascule/a21/confine.py']
    paths+=['wp/tests/'+DIRS[x] for x in LOTS]
    paths+=['wp/outils/bascule/a'+str(x).zfill(2) for x in [3,10,11,12,13,14,15,16,17,18,19]]
    files=[]
    for name in paths:
        p=ROOT/name
        if not p.exists():raise RuntimeError('A22_SOURCE_ROOT_MISSING')
        files.extend([p] if p.is_file() else [f for f in p.rglob('*') if f.is_file()])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files)) if '__pycache__' not in p.parts and p!=ROOT/'wp/tests/a02-audit/README.md'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();out=a.output.resolve()
    assert sys.platform=='win32' and not out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False)
    initial=sources();rows=[]
    absent={lot:not any((ROOT/'wp/tests'/DIRS[lot]).rglob('test_*.py')) for lot in NO_PYTHON}
    assert all(absent.values()),'A22_PYTHON_BANK_APPLICABILITY_CHANGED'
    probe="import sys,locale,json; print(json.dumps({'platform':sys.platform,'executable':sys.executable,'version':sys.version,'version_info':list(sys.version_info[:3]),'stdout':sys.stdout.encoding,'stderr':sys.stderr.encoding,'locale':locale.getencoding(),'preferred':locale.getpreferredencoding(False),'utf8_mode':sys.flags.utf8_mode}))"
    for console,encoding,mode in [('utf8','utf-8','1'),('cp1252','cp1252','0')]:
        folder=out/console;folder.mkdir()
        env={**os.environ,'PYTHONIOENCODING':encoding,'PYTHONUTF8':mode,'PYTHONDONTWRITEBYTECODE':'1',
             'TMPDIR':'C:/Users/Ced/AppData/Local/hermes/cache/scratch'}
        def execute(label,command,timeout=1800):
            p=subprocess.run(command,env=env,cwd=ROOT,capture_output=True,text=True,encoding=encoding,errors='strict',timeout=timeout)
            (folder/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
            return {'label':label,'command':command,'encoding':encoding,'console':console,'exit_code':p.returncode}
        p=subprocess.run([sys.executable,'-B','-c',probe],env=env,capture_output=True,text=True,encoding=encoding,timeout=30)
        assert p.returncode==0
        (folder/'environment.json').write_text(json.dumps(json.loads(p.stdout),indent=2)+'\n',encoding='utf-8')
        for lot in PYTHON_LOTS:
            directory=DIRS[lot] if lot!='A22' else 'a22'
            rows.append(execute(lot+'-python',[sys.executable,'-B','-m','unittest','discover','-s','wp/tests/'+directory,'-p','test_*.py','-v'],120))
        def replay(lot):
            return execute(lot+'-native',[sys.executable,'-B','wp/tests/a22/run.py','--lot='+lot,'--output='+str(folder/lot)],1800)
        with ThreadPoolExecutor(max_workers=3) as pool:rows.extend(pool.map(replay,LOTS))
    stable=initial==sources()
    receipt={'rows':rows,'sources_stable':stable,'python_not_applicable':absent,
             'exit_code':int(not stable or any(row['exit_code']!=0 for row in rows))}
    (out/'sources.json').write_text(json.dumps(initial,indent=2)+'\n',encoding='utf-8')
    (out/'windows-matrix.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2));return receipt['exit_code']

if __name__=='__main__':sys.exit(main())
