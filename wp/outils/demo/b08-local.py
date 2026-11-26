"""Tests B08 isolés, sans site ni réseau."""
import sys
sys.dont_write_bytecode = True
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/B-08'
PROOF.mkdir(exist_ok=True)
cmd = ['wsl.exe','-d','Ubuntu','--','docker','run','--rm','--pull','never','--network','none','--read-only','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777','--entrypoint','php','imagine-tests-t01:1','/repo/wp/tests/demo/b08-horslive.php']
if len(sys.argv) > 2:
    cmd.append(sys.argv[2])
p = subprocess.run(cmd, capture_output=True, encoding='utf-8')
path = PROOF / (sys.argv[1] + '.log')
assert not path.exists(), path
path.write_text(p.stdout + p.stderr, encoding='utf-8')
print(p.stdout + p.stderr)
raise SystemExit(p.returncode)
