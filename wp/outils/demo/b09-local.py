"""B09 PHPUnit hors réseau ; aucune écriture sur le site."""
import sys
sys.dont_write_bytecode = True
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
cmd = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--user', '65534:65534', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--mount', 'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly', '--tmpfs', '/tmp:rw,nosuid,nodev,size=512m,mode=1777', '--entrypoint', 'php', 'imagine-tests-t01:1', '/repo/wp/tests/demo/b09-horslive.php']
if len(sys.argv) > 2:
    cmd.append(sys.argv[2])
p = subprocess.run(cmd, capture_output=True, encoding='utf-8')
text = p.stdout + p.stderr
out = ROOT / 'production/B-09' / (sys.argv[1] + '.log')
out.parent.mkdir(exist_ok=True)
assert not out.exists(), out
out.write_text(text, encoding='utf-8')
print(text)
raise SystemExit(p.returncode)
