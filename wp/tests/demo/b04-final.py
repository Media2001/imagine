"""B04 final verification; no Git, queue, locks, reseed or shared plugin writes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
s=importlib.util.spec_from_file_location('w',HERE/'b04-work.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
w.guard()
python=sys.executable
commands=[
 [python,str(HERE/'b04-work.py'),'php','final'],
 [python,str(HERE/'b04-fixture-test.py'),'final'],
 [python,str(HERE/'b04-undated-test.py'),'native-guard-final'],
 [python,str(HERE/'b04-http.py'),'final'],
 [python,str(HERE/'b04-catalogue-test.py'),'final'],
 [python,str(HERE/'b04-queries.py')],
 [python,str(HERE/'b04-safety.py')],
 [python,str(HERE/'b04-regression.py')],
]
runs=[]
for i,command in enumerate(commands):
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=300)
    (w.PROOF/('final-run-%02d.log'%i)).write_text(result.stdout+result.stderr,encoding='utf-8')
    runs.append({'script':str(Path(command[1]).relative_to(ROOT)),'args':command[2:],'exit':result.returncode})
    print(json.dumps(runs[-1]),flush=True)
    if result.returncode:raise SystemExit(result.returncode)
# Browser package exists in the installed Hermes 3.11 runtime, not in the
# requested Python 3.14 QA venv. Reuse it; no package/runtime installation.
browser_python=Path('C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe')
code="import sys,runpy;sys.path.append('C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Lib/site-packages');runpy.run_path('wp/tests/demo/b04-browser.py',run_name='__main__')"
r=subprocess.run([str(browser_python),'-c',code],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=300)
(w.PROOF/'final-browser.log').write_text(r.stdout+r.stderr,encoding='utf-8');runs.append({'script':'b04-browser.py','exit':r.returncode,'runtime':'existing Hermes Python 3.11 + Playwright'})
if r.returncode:raise SystemExit(r.returncode)
r=subprocess.run([python,str(HERE/'b04-preservation.py'),'final'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=180)
(w.PROOF/'final-preservation.log').write_text(r.stdout+r.stderr,encoding='utf-8');runs.append({'script':'b04-preservation.py','exit':r.returncode})
if r.returncode:raise SystemExit(r.returncode)
expected={'themes/imagine/'+p:w.digest(ROOT/'wp/themes/imagine'/p) for p in w.FILES}
actual=w.readback(list(expected));assert actual==expected
# Count current receipts, not red/historical evidence or repeated earlier passes.
receipt_names=['php-final','fixture-final','undated-native-guard-final','http-final','catalogue-final','queries-20','safety','browser']
suites={name:json.loads((w.PROOF/(name+'.json')).read_text(encoding='utf-8')) for name in receipt_names}
assert all(not s['failures'] and s['total']==len(s['checks']) for s in suites.values())
reg=json.loads((w.PROOF/'regressions.json').read_text(encoding='utf-8'))
counts={name:s['total'] for name,s in suites.items()}
counts.update(B03_HTTP=reg['B03_HTTP']['total'],B03_PHP=reg['B03_PHP']['total'],local_contracts=reg['local_contracts']['total'])
result={'scope':'imagine-test-demo','at':datetime.now(timezone.utc).isoformat(),'runs':runs,'counts':counts,'total':sum(counts.values()),'failures':[],
    'theme_source_sha256':expected,'theme_readback_sha256':actual,'queries_20':suites['queries-20']['measurements'],'sources':{},'status':'GREEN'}
for path in sorted([p for p in HERE.glob('b04*') if p.is_file()]+[p for p in (ROOT/'wp/outils/demo').glob('b04*') if p.is_file()]):
    result['sources'][path.relative_to(ROOT).as_posix()]=w.digest(path)
(w.PROOF/'verification-finale.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'total':result['total'],'counts':counts,'failures':[],'source_readback_exact':expected==actual}),flush=True)
