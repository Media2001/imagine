"""Real A24 classic/HPOS fixture. Raw canaries stay in RAM only."""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('a24_fixture', '/opt/a02/inside.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OUT = Path('/report')


def cmd(args, check=True, env=None, data=None, timeout=240):
    p = subprocess.run(args, input=data, capture_output=True, text=True, encoding='utf-8', errors='strict',
                       timeout=timeout, env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                                             'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})
    if check and p.returncode:
        raise RuntimeError('A24_FIXTURE_COMMAND_FAILED')
    return p


b.cmd = cmd
original = b.check


def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {key: detail[key] for key in ['versions', 'hpos', 'subscriptions', 'rules', 'restriction_real']}
    return original(name, ok, detail)


b.check = check


def inventory(site, output, audit, *extra):
    return cmd(['python3', '/subject/a24/confine.py', '--wp-path=' + str(site),
                '--audit=' + str(audit), '--output=' + str(output), *extra], check=False)


def run_storage(storage):
    site, db, _ = b.install(storage)
    (OUT / (storage + '-seed.json')).unlink()
    cfg = (site / 'wp-config.php').read_text(encoding='utf-8')
    writable = cfg.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')").split(
        "\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site / 'wp-config.php').write_text(writable, encoding='utf-8')
    try:
        p = b.wp(site, ['eval-file', '/opt/a24/seed.php', '--use-include'])
        b.check(storage + ':native_seed', 'A24_SEED_OK' in p.stdout)
        b.wp(site, ['eval-file', '/opt/a24/standard.php', '--use-include'])
        standard = json.loads((OUT / (storage + '-standard.json')).read_text())
        b.check(storage + ':native_standard', standard['exit_code'] == 0 and len(standard['checks']) == 7)
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    spec = importlib.util.spec_from_file_location('a24_extensions', '/opt/a24/extended.py')
    extended = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extended)
    base_mu = Path('/opt/a24/guards.php').read_text(encoding='utf-8')
    (site / 'wp-content/mu-plugins/a24-probe.php').write_text(base_mu, encoding='utf-8')
    (site / 'a24-write-canary').write_bytes(b'SYNTHETIC_UNCHANGED')
    audit = OUT / (storage + '-audit')
    b.check(storage + ':audit_success', b.audit(site, audit).returncode == 0)
    before, files = b.fingerprint(db), b.files(site)
    (OUT / (storage + '-db-before.json')).write_text(json.dumps(before), encoding='utf-8')
    dest = OUT / (storage + '-addresses')
    p = inventory(site, dest, audit / 'audit.json')
    b.check(storage + ':confined_success', (p.returncode, p.stdout, p.stderr)
            == (0, 'A24_OK expedition.json expedition.md\n', ''))
    d = json.loads((dest / 'expedition.json').read_text(encoding='utf-8'))
    b.check(storage + ':twelve_live_subscriptions', d['counts']['overall']['subscriptions'] == 12)
    extended.exercise(b, cmd, inventory, site, db, storage, audit / 'audit.json', dest, cfg, base_mu, before, files)
    after = b.fingerprint(db)
    (OUT / (storage + '-db-after.json')).write_text(json.dumps(after), encoding='utf-8')
    b.check(storage + ':all_tables_and_scheduler_identical', before == after)
    b.check(storage + ':site_files_identical', files == b.files(site))


b.run_storage = run_storage
if __name__ == '__main__':
    sys.exit(b.main())
