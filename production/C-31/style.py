"""PHPCS PSR-12 ciblé sur les fichiers corrigés, image existante et réseau absent."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'production/C-31'
label = sys.argv[1]
assert not (OUT / (label + '.json')).exists()
files = ['plugins/imagine-site/DomainesRefuses.php', 'plugins/imagine-site/DomainesRefusesRegles.php', 'tests/demo/c31-runtime.php']
command = ['wsl.exe','-d','Ubuntu','--','docker','run','--rm','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,nosuid,size=64m','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--entrypoint','php','imagine-tests-t01:1','/opt/t01/imagine-site/vendor/bin/phpcs','--standard=PSR12','--warning-severity=0','-s',*['/repo/wp/' + n for n in files]]
r = subprocess.run(command, cwd=ROOT, capture_output=True, encoding='utf-8')
(OUT / (label + '.log')).write_text(r.stdout + r.stderr, encoding='utf-8')
(OUT / (label + '.json')).write_text(json.dumps({'exit':r.returncode,'command':command,'sources':{'wp/' + n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in files},'log':label+'.log','warning_severity':0},ensure_ascii=False,indent=2), encoding='utf-8')
print(json.dumps({'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}))
raise SystemExit(r.returncode)
