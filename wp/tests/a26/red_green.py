"""Container-only RED/GREEN witness. Always restores the exact owned source."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

subject = Path('/subject/a26/Analysis.php')
original = subject.read_bytes()
needle = b'return self::UNKNOWN;'
assert original.count(needle) == 1
checks = []
try:
    subject.write_bytes(original.replace(needle, b'return self::emptyCounts();'))
    p = subprocess.run(['php', '/opt/a26/unit.php'], capture_output=True, timeout=60)
    red = json.loads(Path('/report/unit.json').read_text())
    Path('/report/unit.json').rename('/report/red-unit.json')
    checks.append({'check': 'neutralisation_mutant_red', 'status': 'PASS' if p.returncode != 0 and any(
        row['check'] == 'neutral_content_unknown_possible_whole_value_scrub' and row['status'] == 'FAIL' for row in red['checks']) else 'FAIL'})
finally:
    subject.write_bytes(original)
checks.append({'check': 'owned_source_restored_exactly', 'status': 'PASS' if subject.read_bytes() == original else 'FAIL'})
p = subprocess.run(['php', '/opt/a26/unit.php'], capture_output=True, timeout=60)
green = json.loads(Path('/report/unit.json').read_text())
checks.append({'check': 'final_source_green', 'status': 'PASS' if p.returncode == 0 and green['exit_code'] == 0 and all(
    row['status'] == 'PASS' for row in green['checks']) else 'FAIL'})
result = {'suite': 'A26-PHP-RED-GREEN', 'source_sha256': hashlib.sha256(original).hexdigest(), 'checks': checks,
          'exit_code': int(any(row['status'] != 'PASS' for row in checks))}
Path('/report/red-green.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
sys.exit(result['exit_code'])
