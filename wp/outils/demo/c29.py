"""C29: bounded local pure/native acceptance, unique fictitious demo."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'production/C-29'
OUT.mkdir(exist_ok=True)
BLOCK = "// C29 — projection en lecture seule, aucun connecteur.\nrequire_once __DIR__ . '/ContactBrevoRegles.php';\nrequire_once __DIR__ . '/ContactBrevo.php';\nContactBrevo::register();\n\n"
FILES = ['plugins/imagine-site/'+n for n in ['ContactBrevoRegles.php','ContactBrevo.php','imagine-site.php']]

def save(label, data):
    with (OUT/(label+'.json')).open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def docker(*args):
    return subprocess.run(['wsl.exe','-d','Ubuntu','--','docker',*args],capture_output=True,encoding='utf-8')

def pure(label):
    r = docker('run','--rm','--pull','never','--network','none','--read-only',
        '--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly',
        '--entrypoint','php','imagine-tests-t01:1','/repo/wp/tests/demo/c29-pure.php')
    save(label, {'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    print(r.stdout,r.stderr)
    return r.returncode

if __name__ == '__main__':
    if sys.argv[1]=='pure': raise SystemExit(pure(sys.argv[2]))
    if sys.argv[1]=='inspect':
        r=docker('run','--rm','--pull','never','--network','none','--read-only','--entrypoint','php','imagine-tests-t01:1','-r','echo getcwd(),PHP_EOL; foreach(["/opt","/opt/t01"] as $p){if(is_dir($p)){echo $p,":",implode(",",array_diff(scandir($p),[".",".."])),PHP_EOL;}}')
        print(r.stdout,r.stderr)
