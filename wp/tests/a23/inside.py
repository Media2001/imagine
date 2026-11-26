"""Native synthetic A23 path; private canaries never enter receipts."""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('fixture', '/opt/a02/inside.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OUT = Path('/report')


def cmd(args, check=True, env=None, data=None, timeout=240):
    p = subprocess.run(args, input=data, capture_output=True, text=True, encoding='utf-8', errors='strict',
                       timeout=timeout, env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                                             'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})
    if check and p.returncode:
        raise RuntimeError('A23_FIXTURE_COMMAND_FAILED')
    return p


b.cmd = cmd
original = b.check


def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {k: detail[k] for k in ['versions', 'hpos', 'subscriptions', 'rules', 'restriction_real']}
    return original(name, ok, detail)


b.check = check


def inventory(site, out, audit, *extra):
    return cmd(['python3', '/subject/a23/confine.py', '--wp-path=' + str(site),
                '--audit=' + str(audit), '--output=' + str(out), *extra], check=False)


def group(*pairs, autres=0):
    return {'groups': [{'label': label, 'accounts': n} for label, n in pairs], 'autres': autres}


def run_storage(storage):
    site, db, _ = b.install(storage)
    (OUT / (storage + '-seed.json')).unlink()
    cfg = (site / 'wp-config.php').read_text(encoding='utf-8')
    writable = cfg.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')").split(
        "\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site / 'wp-config.php').write_text(writable, encoding='utf-8')
    try:
        p = b.wp(site, ['eval-file', '/opt/a23/seed.php', '--use-include'])
        b.check(storage + ':native_seed', 'A23_SEED_OK' in p.stdout)
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    audit = OUT / (storage + '-audit')
    b.check(storage + ':audit_success', b.audit(site, audit).returncode == 0)
    before = b.fingerprint(db)
    files = b.files(site)
    (OUT / (storage + '-db-before.json')).write_text(json.dumps(before), encoding='utf-8')
    dest = OUT / (storage + '-accounts')
    p = inventory(site, dest, audit / 'audit.json')
    b.check(storage + ':confined_success', p.returncode == 0 and p.stdout == 'A23_OK comptes.json comptes.md\n' and p.stderr == '')
    d = json.loads((dest / 'comptes.json').read_text(encoding='utf-8'))
    expected = {
        'readers': {'accounts': 32,
                    'families': group(('phpass', 10), ('wordpress_bcrypt', 20), autres=2),
                    'emails': group(('email_empty', 5), ('email_malformed', 5), ('email_shared_case_insensitive', 11)),
                    'logins': group(('login_equals_email', 10), ('login_case_collision', 10))},
        'live_readers': {'accounts': 20, 'families': group(('phpass', 10), ('wordpress_bcrypt', 10)),
                         'emails': group(('email_empty', 5), ('email_malformed', 5), ('email_shared_case_insensitive', 10)),
                         'logins': group(('login_equals_email', 5), ('login_case_collision', 5))},
        'without_commerce': group(autres=3),
    }
    for key, value in expected.items():
        b.check(storage + ':exact:' + key, d['counts'][key] == value, {'actual': d['counts'][key], 'expected': value})
    payload = p.stdout + p.stderr + ''.join(f.read_text(encoding='utf-8') for f in dest.iterdir())
    b.check(storage + ':all_private_values_absent', not re.search(r'CANARY|@|/scratch|user_pass|user_email|user_login|a23-fictif|a02-admin', payload))
    after = b.fingerprint(db)
    (OUT / (storage + '-db-after.json')).write_text(json.dumps(after), encoding='utf-8')
    b.check(storage + ':all_tables_and_scheduler_identical', before == after)
    b.check(storage + ':site_files_identical', files == b.files(site))


b.run_storage = run_storage
if __name__ == '__main__':
    sys.exit(b.main())
