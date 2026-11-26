"""Syntax checks executed exclusively in the disposable PHP runner."""
import hashlib
import json
from pathlib import Path
import subprocess
paths = sorted(set(Path('/subject').rglob('*.php')) | set(Path('/opt/a28').glob('*.php')))
checks = []
for path in paths:
    p = subprocess.run(['php', '-n', '-l', str(path)], capture_output=True, timeout=30)
    checks.append({'file': str(path), 'exit': p.returncode, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                   'ok': p.returncode == 0 and not p.stderr and p.stdout.startswith(b'No syntax errors detected')})
result = {'status': 'PASS' if checks and all(c['ok'] for c in checks) else 'FAIL', 'checks': checks}
Path('/report/a28-lint.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({'status': result['status'], 'files': len(checks)}))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
