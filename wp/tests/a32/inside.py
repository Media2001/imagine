"""Actual whole-tour classic/HPOS exercise. Doubles are limited and named."""
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

sys.dont_write_bytecode = True


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


b = load('fixture', '/opt/a02/inside.py')
m = load('tournee', '/subject/wp/outils/bascule/tournee/tournee.py')
OUT = Path('/report')
BASE = Path('/subject/wp/outils/bascule')
ORIGINAL = b.check


def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {k: detail[k] for k in ('versions', 'hpos', 'subscriptions', 'rules', 'restriction_real')}
    return ORIGINAL(name, ok, detail)


b.check = check
b.audit = lambda site, out: b.cmd(['php', str(BASE / 'audit'), '--wp-path=' + str(site), '--output=' + str(out)], check=False)


def tour(site, audit, mapping, out):
    line = next(x for x in (BASE / 'README.md').read_text(encoding='utf-8').splitlines()
                if x.startswith('python3 wp/outils/bascule/tournee/tournee.py '))
    args = shlex.split(line)
    replacements = {'wp/outils/bascule/tournee/tournee.py': str(BASE / 'tournee/tournee.py'),
                    '--wp-path=/copie-verifiee': '--wp-path=' + str(site),
                    '--audit=/hors-web/audit-date/audit.json': '--audit=' + str(audit),
                    '--correspondance=/hors-web/correspondance.json': '--correspondance=' + str(mapping),
                    '--output=/hors-web/tournee-date': '--output=' + str(out)}
    args = [replacements.get(x, x) for x in args]
    p = subprocess.run(args, capture_output=True, timeout=1200,
                       env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': 'utf-8'})
    return p, args


def run_storage(storage):
    site, db, _ = b.install(storage)
    (OUT / (storage + '-seed.json')).unlink()
    cfg = (site / 'wp-config.php').read_text()
    writable = cfg.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site / 'wp-config.php').write_text(writable)
    try:
        seeded = b.wp(site, ['eval-file', '/opt/a32/seed16.php', '--use-include'])
        check(storage + ':native_editorial_seed', 'A16_JSON=' in seeded.stdout)
    finally:
        (site / 'wp-config.php').write_text(cfg)
    registry = site / 'wp-content/mu-plugins/a32-registry.php'
    registry.write_text("<?php register_post_type('a16_numero',['public'=>false]); register_post_type('a16_article',['public'=>false]); register_taxonomy('a16_theme','a16_article'); register_taxonomy('a16_issue','a16_article');")
    audit = OUT / (storage + '-audit')
    check(storage + ':audit_ready', b.audit(site, audit).returncode == 0)
    mapping = BASE / 'a16/correspondance.exemple.json'
    before, files_before = b.fingerprint(db), b.files(site)
    private_before = b.files(Path('/scratch/a16-private'))
    dest = OUT / (storage + '-complete')
    p, args = tour(site, audit / 'audit.json', mapping, dest)
    doc = json.loads((dest / 'bilan.json').read_text())
    check(storage + ':documented_command_exact_complete', p.returncode == 0 and p.stdout == b'A32_COMPLETE bilan.json bilan.md\n' and not p.stderr
          and doc['tournee'] == 'complète' and [r['outil'] for r in doc['outils']] == [e['lot'] for e in m.entries()]
          and all(r['statut'] == 'réussi' for r in doc['outils']), {'exit': p.returncode, 'rows': doc['outils']})
    (OUT / (storage + '-command.json')).write_text(json.dumps({'command': args, 'exit_code': p.returncode,
                                                              'per_tool_commands': [m.command(e, site, audit / 'audit.json', mapping, Path(r['rapport'])) for e, r in zip(m.entries(), doc['outils'])]}, indent=2))
    check(storage + ':whole_nominal_db_files_immutable', before == b.fingerprint(db) and files_before == b.files(site)
          and private_before == b.files(Path('/scratch/a16-private')))
    # Deliberately named boundary doubles: A10 refusal / A11 exit 255 only.
    guard = load('a32_native_guard', BASE / 'stream_guard.py')
    calls = []
    mixed = OUT / (storage + '-named-doubles')
    def double_executor(command):
        index = len(calls)
        calls.append(command)
        if index == 0:
            return 1, b'', b'A10_AUDIT_GUARD\n'
        if index == 1:
            return 255, b'A32_DOUBLE_PRIVATE_CANARY', b'A32_DOUBLE_PRIVATE_CANARY'
        return guard.supervise(command, {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, OUT, None, timeout=180)
    code = m.run(site, audit / 'audit.json', mapping, mixed, double_executor)
    mixed_doc = json.loads((mixed / 'bilan.json').read_text())
    check(storage + ':named_doubles_continue_every_remaining_real_tool', code == 1 and len(calls) == len(m.entries())
          and [r['statut'] for r in mixed_doc['outils']] == ['refusé', 'en échec'] + ['réussi'] * (len(m.entries()) - 2)
          and mixed_doc['outils'][0]['code'] == 'A10_AUDIT_GUARD' and mixed_doc['outils'][1]['sortie'] == 255)
    (OUT / (storage + '-doubles.json')).write_text(json.dumps({'declared_doubles': {'A10': 'refusal', 'A11': 'exit255'},
                                                             'exit_code': code, 'commands': calls}, indent=2))
    # Each channel is real site code. A10 is SQL-only and never loads these callbacks.
    cases = {
        'stdout': "fwrite(STDOUT,'A32_STREAM_PRIVATE_CANARY');",
        'stderr': "fwrite(STDERR,'A32_STREAM_PRIVATE_CANARY');",
        'early_exit': "echo 'A32_STREAM_PRIVATE_CANARY'; exit(0);",
        'silent_exit': 'exit(0);',
        'shutdown_stdout': "register_shutdown_function(static function(){fwrite(STDOUT,'A32_STREAM_PRIVATE_CANARY');});",
        'shutdown_stderr': "register_shutdown_function(static function(){fwrite(STDERR,'A32_STREAM_PRIVATE_CANARY');});",
        'report': "register_shutdown_function(static function(){foreach($GLOBALS['argv'] as $a){if(str_starts_with($a,'--output=')){foreach(glob(substr($a,9).'/*.json') as $f){$v=json_decode(file_get_contents($f),true);$v['private']='A32_REPORT_PRIVATE_CANARY';file_put_contents($f,json_encode($v));}}}});",
    }
    hostile = site / 'wp-content/mu-plugins/000-a32-hostile.php'
    channel_rows = []
    try:
        for label, statement in cases.items():
            hostile.write_text('<?php ' + statement)
            channel_before, channel_files = b.fingerprint(db), b.files(site)
            target = OUT / (storage + '-channel-' + label)
            q, _ = tour(site, audit / 'audit.json', mapping, target)
            data = json.loads((target / 'bilan.json').read_text())
            good = (q.returncode == 1 and q.stdout == b'A32_COMPLETE bilan.json bilan.md\n' and not q.stderr
                    and data['tournee'] == 'complète' and data['outils'][0]['statut'] == 'réussi'
                    and all(r['statut'] != 'réussi' for r in data['outils'][1:]))
            clean = not any(b'A32_' + suffix in f.read_bytes() for suffix in (b'STREAM_PRIVATE_CANARY', b'REPORT_PRIVATE_CANARY', b'DOUBLE_PRIVATE_CANARY')
                            for f in OUT.rglob('*') if f.is_file())
            immutable = channel_before == b.fingerprint(db) and channel_files == b.files(site)
            check(storage + ':whole_tour_channel:' + label, good and clean and immutable,
                  {'closed': good, 'no_canary_retained': clean, 'db_files_immutable': immutable})
            channel_rows.append({'channel': label, 'per_tool': data['outils'], 'exit_code': q.returncode, 'clean': clean, 'immutable': immutable})
    finally:
        hostile.unlink(missing_ok=True)
    # Each tool's own staging check, no tour-side replacement or bypass.
    (site / 'wp-config.php').write_text(cfg.replace("'staging'", "'production'"))
    try:
        unverified_before, unverified_files = b.fingerprint(db), b.files(site)
        target = OUT / (storage + '-unverified')
        q, _ = tour(site, audit / 'audit.json', mapping, target)
        d = json.loads((target / 'bilan.json').read_text())
        check(storage + ':every_tool_checks_site', q.returncode == 1 and len(d['outils']) == len(m.entries())
              and all(r['statut'] != 'réussi' for r in d['outils'])
              and unverified_before == b.fingerprint(db) and unverified_files == b.files(site), d['outils'])
    finally:
        (site / 'wp-config.php').write_text(cfg)
    after, files_after = b.fingerprint(db), b.files(site)
    check(storage + ':whole_tour_all_tables_scheduler_files_immutable', before == after and files_before == files_after
          and private_before == b.files(Path('/scratch/a16-private')))
    check(storage + ':config_never_executed', not Path('/scratch/a02-bootstrap-trap').exists())
    for filename, value in [(storage + '-fingerprints.json', {'before': before, 'after': after, 'files_before': files_before, 'files_after': files_after}),
                            (storage + '-channels.json', channel_rows)]:
        (OUT / filename).write_text(json.dumps(value, indent=2) + '\n')


b.run_storage = run_storage
if __name__ == '__main__':
    sys.exit(b.main())
