"""Offline B01 validation in a fresh venv; no global or NUC install.
Requires local `uv`; wheels and complete hash-locked requirements are in validation/.
"""
from pathlib import Path
import sys, subprocess, tempfile, json, os
ROOT=Path(__file__).resolve().parents[2]
PROOF=ROOT/'production/B-01'
envdir=Path(tempfile.mkdtemp(prefix='imagine-b01-',dir=os.environ['TMPDIR']))
envpython=envdir/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
commands=[]
env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTHONNOUSERSITE']='1'
def run(args):
    result=subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding='utf-8',env=env)
    commands.append({'command':[str(a) for a in args],'code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    (PROOF/'tests/isolated-environment.json').write_text(json.dumps({'environment':str(envdir),'commands':commands},ensure_ascii=False,indent=2),encoding='utf-8')
    if result.returncode: raise RuntimeError(result.stdout+result.stderr)
    return result.stdout
run(['uv','venv','--python',sys.executable,envdir])
run(['uv','pip','install','--python',envpython,'--no-index','--find-links',PROOF/'validation','--require-hashes','-r',PROOF/'validation/requirements.lock'])
run(['uv','pip','check','--python',envpython])
for name in ['test_b01_theme.py','b01-corrections.py']:
    run([envpython,'-I',ROOT/'wp/tests/demo'/name])
code="""import sys,json,importlib.metadata as m
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from b01_html import validate_html
import html5lib,bs4,six,soupsieve,typing_extensions,webencodings
modules=[html5lib,bs4,six,soupsieve,typing_extensions,webencodings]
assert sys.prefix!=sys.base_prefix
assert all(Path(sys.prefix).resolve() in Path(x.__file__).resolve().parents for x in modules)
files=sorted(Path(sys.argv[2]).glob('*.html'))
errors={f.name:validate_html(f.read_text(encoding='utf-8')) for f in files}
assert files and not any(errors.values()),errors
print(json.dumps({'python':sys.version,'prefix':sys.prefix,'base_prefix':sys.base_prefix,'system_packages':False,'packages':{x.__name__:x.__file__ for x in modules},'versions':{n:m.version(n) for n in ['beautifulsoup4','html5lib','six','soupsieve','typing_extensions','webencodings']},'html_pages':len(files),'html_errors':sum(map(len,errors.values()))},indent=2))
"""
print(run([envpython,'-I','-c',code,ROOT/'wp/tests/demo',PROOF/'http']))
print('Fresh offline environment and six Python tests: PASS')
