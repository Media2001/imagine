"""Rejeu PHPUnit B07 ciblé, conteneur hors réseau ; reçus immuables."""
import sys
sys.dont_write_bytecode = True
import subprocess, json, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
def run(label, mutation=''):
    target = ROOT/'production/B-07'/label
    assert not target.exists()
    cmd = ['wsl.exe','-d','Ubuntu','--','docker','run','--rm','--pull','never','--network','none','--read-only','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777','--entrypoint','php','imagine-tests-t01:1','/repo/wp/tests/demo/b07-horslive.php']
    if mutation: cmd.append(mutation)
    p = subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
    target.write_text(p.stdout+p.stderr,encoding='utf-8')
    print(p.stdout+p.stderr)
    print('B07 EXIT',p.returncode)
    return p.returncode
if __name__ == '__main__':
    raise SystemExit(run(*sys.argv[1:]))
