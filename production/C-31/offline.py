"""Suite du seul paquet imagine-site, image existante, aucune préparation ni rejeu global."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'production/C-31'
name = sys.argv[1]
assert name.endswith('-V2') and not (OUT / (name + '.json')).exists()
all_tests = '--all' in sys.argv[2:]
script = '''set -eu
cp -a /repo/wp/plugins /tmp/plugins
cp -a /opt/t01/imagine-site/vendor /tmp/plugins/imagine-site/vendor
cd /tmp/plugins/imagine-site
php vendor/bin/phpunit --configuration phpunit.xml --fail-on-warning --fail-on-risky --fail-on-deprecation --fail-on-skipped --fail-on-incomplete --do-not-cache-result --colors=never --log-junit /tmp/c31.xml %s
''' % ('' if all_tests else '--filter DomainesRefuses')
command = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--tmpfs', '/tmp:rw,exec,nosuid,size=512m', '--mount', 'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly', '--entrypoint', 'sh', 'imagine-tests-t01:1', '-c', script]
r = subprocess.run(command, cwd=ROOT, capture_output=True, encoding='utf-8')
(OUT / (name + '.log')).write_text(r.stdout + r.stderr, encoding='utf-8')
sources = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for pattern in ['wp/plugins/imagine-site/DomainesRefuses*.php', 'wp/plugins/imagine-site/tests/DomainesRefuses*.php'] for p in ROOT.glob(pattern)}
(OUT / (name + '.json')).write_text(json.dumps({'scope': 'offline-network-none', 'exit': r.returncode, 'command': command, 'sources': sources, 'log': name + '.log'}, ensure_ascii=False, indent=2), encoding='utf-8')
print(r.stdout + r.stderr)
raise SystemExit(r.returncode)
