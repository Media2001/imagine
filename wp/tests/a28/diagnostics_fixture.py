"""Run the unchanged A01 PDO diagnostic suite on a fresh synthetic SQL duplicate."""
import json
from pathlib import Path
import sys
sys.path.insert(0, '/opt/court')
import inside
process = None
result = {'status': 'FAIL'}
code = 1
try:
    process = inside.database_start()
    sql = b"CREATE DATABASE imagine_ai1wm_fixture; USE imagine_ai1wm_fixture; CREATE TABLE wp_options (option_name varchar(191) PRIMARY KEY, option_value text, autoload varchar(20)); INSERT INTO wp_options VALUES ('home','https://fiction.invalid','yes');"
    inside.command(['mariadb', '--socket=/scratch/mariadb.sock', '--user=root'], data=sql)
    p = inside.command(['php', '/checkout/wp/tests/a01-court/test_diagnostics.php'], check=False)
    result = {'status': 'PASS' if p.returncode == 0 and not p.stderr else 'FAIL', 'exit': p.returncode,
              'assertions': json.loads(p.stdout).get('assertions', 0) if p.returncode == 0 else 0,
              'stderr_empty': not p.stderr}
    sys.stdout.buffer.write(p.stdout)
    sys.stderr.buffer.write(p.stderr)
    code = 0 if result['status'] == 'PASS' else 1
finally:
    if process:
        inside.command(['mariadb-admin', '--socket=/scratch/mariadb.sock', '--user=root', 'shutdown'], check=False)
        process.wait(timeout=30)
    Path('/report/a01-diagnostics.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
raise SystemExit(code)
