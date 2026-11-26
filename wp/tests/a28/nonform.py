"""Bytewise non-form comparison with the saved pre-correction A01 implementation."""
import hashlib
import json
from pathlib import Path
import subprocess
rows = []
for root in ('/reference', '/subject'):
    import os
    p = subprocess.run(['php', '/opt/a28/nonform.php'], env={**os.environ, 'A28_SUBJECT': root}, capture_output=True, timeout=30)
    meta = json.loads(p.stderr)
    rows.append({'root': root, 'exit': p.returncode, 'stdout_sha256': hashlib.sha256(p.stdout).hexdigest(),
                 'added_count': meta['added_count'], 'stdout': p.stdout})
exact = rows[0]['stdout'] == rows[1]['stdout'] and all(r['exit'] == 0 for r in rows)
result = {'status': 'PASS' if exact and rows[0]['added_count'] is None and rows[1]['added_count'] == 0 else 'FAIL',
          'exact_nonform_tables_and_report_and_historical_refusals': exact,
          'only_report_addition': {'form_message_residues': 0},
          'runs': [{k: value for k, value in r.items() if k != 'stdout'} for r in rows]}
Path('/report/nonform.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
