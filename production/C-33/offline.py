"""Suite C33 dans l'image existante, dépôt RO, aucun réseau."""
import sys
sys.dont_write_bytecode = True
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'production/C-33'
name = sys.argv[1]
assert name.endswith('-V2') and not (OUT/(name+'.json')).exists()
script = '''set -eu
cp -a /repo/wp/plugins /tmp/plugins
cp -a /opt/t01/imagine-site/vendor /tmp/plugins/imagine-site/vendor
cd /tmp/plugins/imagine-site
php vendor/bin/phpunit --configuration phpunit.xml --fail-on-warning --fail-on-risky --fail-on-deprecation --fail-on-skipped --fail-on-incomplete --do-not-cache-result --colors=never --filter ComptesPublics
'''
command = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--tmpfs', '/tmp:rw,exec,nosuid,size=512m', '--mount', 'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly', '--entrypoint', 'sh', 'imagine-tests-t01:1', '-c', script]
r = subprocess.run(command, cwd=ROOT, capture_output=True, encoding='utf-8')
with (OUT/(name+'.log')).open('x', encoding='utf-8') as f:
    f.write(r.stdout+r.stderr)
with (OUT/(name+'.json')).open('x', encoding='utf-8') as f:
    json.dump({'scope': 'offline-network-none', 'exit': r.returncode, 'command': command, 'log': name+'.log'}, f, indent=2)
print(r.stdout+r.stderr)
raise SystemExit(r.returncode)
