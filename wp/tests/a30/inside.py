"""Parent-only native fixture entry. Do not run on a host or a real site."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
from cases import CHANNELS, EXPECTED_LINES, five_issues_bytes
spec = importlib.util.spec_from_file_location('fixture', '/opt/a02/inside.py')
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
OUT = Path('/report')
FIX = Path('/opt/a30/fixtures')


def cmd(args, check=True, env=None, data=None, timeout=240):
    p = subprocess.run(args, input=data, capture_output=True, text=True, encoding='utf-8', errors='strict',
                       timeout=timeout, env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                                             'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})
    if check and p.returncode:
        raise RuntimeError('A30_FIXTURE_COMMAND_FAILED')
    return p


b.cmd = cmd
original_check = b.check


def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {k: detail[k] for k in ['versions', 'hpos', 'subscriptions', 'rules', 'restriction_real']}
    return original_check(name, ok, detail)


b.check = check


def outputs(source):
    return [source.with_name(source.stem + suffix) for suffix in ('.a30-resume.json', '.a30-lignes.json')]


def invoke(site, source, types, audit):
    return cmd(['python3', '/subject/a30/confine.py', '--wp-path=' + str(site), '--fichier=' + str(source),
                '--correspondance=/subject/a13/correspondance.exemple.json', '--types=' + str(types),
                '--audit=' + str(audit), '--au=2026-11-25'], check=False)


def run_storage(storage):
    site, db, _ = b.install(storage)
    (OUT / (storage + '-seed.json')).unlink()
    cfg = (site / 'wp-config.php').read_text(encoding='utf-8')
    writable = cfg.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')").split(
        "\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site / 'wp-config.php').write_text(writable, encoding='utf-8')
    try:
        seed = b.wp(site, ['eval-file', '/opt/a30/seed.php', '--use-include'])
        match = re.search(r'^A30_PRODUCT=([0-9]+)$', seed.stdout, re.M)
        b.check(storage + ':native_seed', match is not None and not seed.stderr)
        product = int(match[1])
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    work = Path('/scratch/input-' + storage); work.mkdir()
    types = work / 'types.json'
    config = json.loads(Path('/subject/a30/types.exemple.json').read_text(encoding='utf-8'))
    config['types'] = {'papier': product}
    types.write_text(json.dumps(config), encoding='utf-8')
    clean = (FIX / 'a13-export-propre-fictif.csv').read_bytes()
    five = five_issues_bytes(clean)
    mu = site / 'wp-content/mu-plugins/a30-probe.php'
    base_mu = '''<?php
if (getenv('A30_CONFINED') === '1') {
    global $wpdb;
    if ($wpdb->query('UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @mysqli_query($wpdb->dbh, 'UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @file_put_contents(ABSPATH.'a30-forbidden', 'NO') !== false
        || wp_mail('fictif@example.org', 'A30_MAIL_PRIVATE_CANARY', 'A30_MAIL_PRIVATE_CANARY') !== false
        || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
        || wp_schedule_single_event(time()+9999, 'a30_forbidden') !== false
        || function_exists('mail') || function_exists('exec')) {
        throw new RuntimeException('A30_EARLY_GUARD_PRIVATE_CANARY');
    }
    add_action('plugins_loaded', static function () {
        if (as_enqueue_async_action('a30_forbidden') !== 0
            || as_schedule_single_action(time()+9999, 'a30_forbidden') !== 0
            || as_schedule_recurring_action(time()+9999, 3600, 'a30_forbidden') !== 0
            || as_schedule_cron_action(time()+9999, '* * * * *', 'a30_forbidden') !== 0) {
            throw new RuntimeException('A30_AS_GUARD_PRIVATE_CANARY');
        }
    }, PHP_INT_MAX);
    echo 'A30_DISPLAY_PRIVATE_CANARY';
}
'''
    mu.write_text(base_mu, encoding='utf-8')
    audit = OUT / (storage + '-audit')
    b.check(storage + ':audit_success', b.audit(site, audit).returncode == 0)
    before, files = b.fingerprint(db), b.files(site)
    (OUT / (storage + '-db-before.json')).write_text(json.dumps(before), encoding='utf-8')
    source = work / 'five.csv'; source.write_bytes(five)
    p = invoke(site, source, types, audit / 'audit.json')
    b.check(storage + ':confined_success', (p.returncode, p.stdout, p.stderr) == (1, 'A30_OK\n', ''))
    summary, lines = [json.loads(path.read_text(encoding='utf-8')) for path in outputs(source)]
    b.check(storage + ':five_issues_exact_lines', lines['issues'] == EXPECTED_LINES and lines['rapprochement_inconnu'] == [])
    b.check(storage + ':counts_k5', summary['total'] == 25 and summary['storage'] == storage
            and summary['issues'] == {'groups': [{'key': key, 'count': 5} for key in sorted(EXPECTED_LINES)], 'autres': 0}
            and summary['products'] == {'groups': [{'key': 0, 'count': 5}, {'key': product, 'count': 20}], 'autres': 0}
            and summary['payments'] == {'groups': [{'key': 'virement', 'count': 25}], 'autres': 0})
    b.check(storage + ':no_private_values', not re.search(r'CANARY|@|/scratch|a13-fictif|Licorne|type-a-decider',
            p.stdout + p.stderr + ''.join(path.read_text(encoding='utf-8') for path in outputs(source))))
    result_dir = OUT / (storage + '-five'); result_dir.mkdir()
    for path, name in zip(outputs(source), ('summary.json', 'lines.json')):
        shutil.copyfile(path, result_dir / name)
    b.check(storage + ':input_immutable', source.read_bytes() == five)
    repeated = work / 'repeat.csv'; repeated.write_bytes(five)
    q = invoke(site, repeated, types, audit / 'audit.json')
    b.check(storage + ':replay_identical', q.returncode == 1 and q.stdout == 'A30_OK\n' and not q.stderr
            and [p.read_bytes() for p in outputs(source)] == [p.read_bytes() for p in outputs(repeated)])
    q = invoke(site, source, types, audit / 'audit.json')
    b.check(storage + ':existing_output_refused', (q.returncode, q.stdout, q.stderr) == (1, '', 'A30_OUTPUT_EXISTS\n'))
    # Run the complete documented line with substitutions for its external placeholders only.
    line = next(x for x in Path('/subject/a30/README.md').read_text(encoding='utf-8').splitlines()
                if x.startswith('python3 wp/outils/bascule/a30/confine.py '))
    documented = work / 'documented.csv'; documented.write_bytes(five)
    replacements = {'wp/outils/bascule/a30/confine.py': '/subject/a30/confine.py',
                    '--wp-path=/copie-verifiee': '--wp-path=' + str(site),
                    '--fichier=/hors-web/export.csv': '--fichier=' + str(documented),
                    '--correspondance=wp/outils/bascule/a13/correspondance.exemple.json': '--correspondance=/subject/a13/correspondance.exemple.json',
                    '--types=/hors-web/types.json': '--types=' + str(types),
                    '--audit=/hors-web/audit-date/audit.json': '--audit=' + str(audit / 'audit.json')}
    q = cmd([replacements.get(x, x) for x in shlex.split(line)], check=False)
    b.check(storage + ':documented_command', (q.returncode, q.stdout, q.stderr) == (1, 'A30_OK\n', '')
            and [p.read_bytes() for p in outputs(source)] == [p.read_bytes() for p in outputs(documented)])
    for label, data in [('clean', clean), ('dirty', (FIX / 'a13-export-defauts-fictif.csv').read_bytes()),
                        ('iban', (FIX / 'a13-export-iban-fictif.csv').read_bytes()),
                        ('encoding', clean.decode('utf-8').encode('cp1252'))]:
        path = work / (label + '.csv'); path.write_bytes(data)
        q = invoke(site, path, types, audit / 'audit.json')
        if label in ('iban', 'encoding'):
            reference = cmd(['python3', '/subject/controler-export', str(path),
                             '--correspondance=/subject/a13/correspondance.exemple.json', '--au=2026-11-25'], check=False)
            b.check(storage + ':a13_exact_refusal:' + label, (q.returncode, q.stdout, q.stderr)
                    == (reference.returncode, reference.stdout, reference.stderr)
                    and q.returncode == 2 and not any(p.exists() for p in outputs(path))
                    and 'ZZ00' not in q.stdout + q.stderr)
        else:
            b.check(storage + ':a13_fixture:' + label, q.returncode == (0 if label == 'clean' else 1)
                    and q.stdout == 'A30_OK\n' and q.stderr == '')
            result = json.loads(outputs(path)[1].read_text(encoding='utf-8'))
            expected = [] if label == 'clean' else [2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]
            b.check(storage + ':a13_exact_lines:' + label, result['issues']['refuse_a13'] == expected)
        b.check(storage + ':input_immutable:' + label, path.read_bytes() == data)
    for label, statement in CHANNELS.items():
        mu.write_text("<?php if (getenv('A30_CONFINED') === '1') { " + statement + ' }\n' + base_mu[5:], encoding='utf-8')
        path = work / (label + '.csv'); path.write_bytes(five)
        try:
            q = invoke(site, path, types, audit / 'audit.json')
            expected = 'A30_REPORT_INVALID' if label == 'shutdown_extra_file' else 'A30_PROCESS_OUTPUT_INVALID'
            b.check(storage + ':closed_channel:' + label, (q.returncode, q.stdout, q.stderr) == (1, '', expected + '\n')
                    and not any(p.exists() for p in outputs(path)))
            b.check(storage + ':no_retained_payload:' + label, not list(work.glob('.a30-private-*'))
                    and not any(b'CANARY' in p.read_bytes() for p in OUT.rglob('*') if p.is_file()))
        finally:
            mu.write_text(base_mu, encoding='utf-8')
    after = b.fingerprint(db)
    (OUT / (storage + '-db-after.json')).write_text(json.dumps(after), encoding='utf-8')
    final_files = b.files(site)
    (OUT / (storage + '-files.json')).write_text(json.dumps({'before': files, 'after': final_files}), encoding='utf-8')
    b.check(storage + ':all_sql_tables_identical', before == after)
    b.check(storage + ':site_files_identical', files == final_files)
    b.check(storage + ':config_never_executed', not Path('/scratch/a02-bootstrap-trap').exists())
    # Clone only the synthetic DB, then execute the parent's frozen import engine.
    clone = 'a30_' + storage + '_test'
    b.sql('mysql', 'CREATE DATABASE ' + clone)
    dump = cmd(['mariadb-dump', '--socket=' + b.SOCKET, '-uroot', db]).stdout
    cmd(['mariadb', '--socket=' + b.SOCKET, '-uroot', clone], data=dump)
    phase = cmd(['php', '/opt/a30/neutralise.php'], env={'A30_DB': clone})
    provenance = json.loads(phase.stdout)
    (OUT / (storage + '-neutralisation.json')).write_text(json.dumps(provenance), encoding='utf-8')
    b.check(storage + ':actual_neutralisation', not phase.stderr and provenance == {
        'engine_executed': True, 'marker_count': 1, 'matching_emails_before': 5, 'matching_emails_after': 0})
    b.sql('mysql', "GRANT SELECT ON " + clone + ".* TO 'a02_" + storage + "'@'localhost'")
    (site / 'wp-config.php').write_text(cfg.replace("define('DB_NAME', '" + db + "')", "define('DB_NAME', '" + clone + "')"), encoding='utf-8')
    try:
        neutral_before, neutral_files = b.fingerprint(clone), b.files(site)
        n_audit = OUT / (storage + '-neutral-audit')
        b.check(storage + ':neutral_audit', b.audit(site, n_audit).returncode == 0)
        path = work / 'neutral.csv'; path.write_bytes(five)
        q = invoke(site, path, types, n_audit / 'audit.json')
        b.check(storage + ':neutral_success', (q.returncode, q.stdout, q.stderr) == (1, 'A30_OK\n', ''))
        summary, lines = [json.loads(p.read_text(encoding='utf-8')) for p in outputs(path)]
        b.check(storage + ':neutral_unknown_never_zero', summary['accounts'] == 'inconnu après neutralisation'
                and lines['issues']['compte_existant'] == lines['issues']['compte_a_creer'] == 'inconnu après neutralisation'
                and lines['rapprochement_inconnu'] == list(range(2, 12)))
        n_dir = OUT / (storage + '-neutral'); n_dir.mkdir()
        for p, name in zip(outputs(path), ('summary.json', 'lines.json')):
            shutil.copyfile(p, n_dir / name)
        neutral_after = b.fingerprint(clone)
        for suffix, value in [('before', neutral_before), ('after', neutral_after)]:
            (OUT / (storage + '-neutral-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
        b.check(storage + ':neutral_sql_files_identical', neutral_before == neutral_after and neutral_files == b.files(site))
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')


b.run_storage = run_storage
if __name__ == '__main__':
    sys.exit(b.main())
