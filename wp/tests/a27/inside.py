"""Parent-only synthetic classic/HPOS bank; private streams stay in RAM."""
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
spec = importlib.util.spec_from_file_location('a02_fixture', '/opt/a02/inside.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OUT = Path('/report')
SUCCESS = 'A27_OK paiements.json paiements.md\n'
UNKNOWN = 'inconnu après neutralisation'
CLOCK = '2026-11-26T12:00:00+00:00'


def cmd(args, check=True, env=None, data=None, timeout=240):
    p = subprocess.run(args, input=data, capture_output=True, text=True, encoding='utf-8', errors='strict',
                       timeout=timeout, env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                                             'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})
    if check and p.returncode:
        raise RuntimeError('A27_FIXTURE_COMMAND_FAILED')
    return p


b.cmd = cmd
original_check = b.check


def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {k: detail[k] for k in ['versions', 'hpos', 'subscriptions', 'rules', 'restriction_real']}
    return original_check(name, ok, detail)


b.check = check


def inventory(site, output, audit, *extra):
    return cmd(['python3', '/subject/a27/confine.py', '--wp-path=' + str(site), '--audit=' + str(audit),
                '--output=' + str(output), *extra], check=False)


def audit_at(site, output):
    b.check(output.name + ':audit', b.audit(site, output).returncode == 0)
    audit = output / 'audit.json'
    d = json.loads(audit.read_text(encoding='utf-8'))
    d['generated_at_utc'] = CLOCK  # Explicit synthetic audit-clock oracle, not a live-time assertion.
    audit.write_text(json.dumps(d, ensure_ascii=False, indent=4) + '\n', encoding='utf-8')
    return audit


def seed(site, cfg, repeats=1):
    writable = cfg.replace("define('DB_USER', 'a02_" + site.name + "')", "define('DB_USER', 'root')").split(
        "\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site / 'wp-config.php').write_text(writable, encoding='utf-8')
    try:
        q = b.wp(site, ['eval-file', '/opt/a27/seed.php', '--use-include'], env={'A27_REPETITIONS': str(repeats)})
        b.check(site.name + ':native_seed_' + str(repeats), q.stdout == 'A27_SEED_OK\n' and not q.stderr)
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')


def pool(n):
    return {'groups': [], 'autres': n}


def run_storage(storage):
    site, db, _ = b.install(storage)
    (OUT / (storage + '-seed.json')).unlink()
    q = cmd(['php', '/opt/a27/standard.php', str(site)], check=False)
    b.check(storage + ':installed_standard_before_subject', q.returncode == 0 and q.stdout == q.stderr == '')
    cfg = (site / 'wp-config.php').read_text(encoding='utf-8')
    seed(site, cfg)
    mu = site / 'wp-content/mu-plugins/a27-probe.php'
    base_mu = '''<?php
if (getenv('A27_CONFINED') === '1') {
    global $wpdb;
    require_once ABSPATH.'wp-includes/pluggable.php';
    add_action('plugins_loaded', static function () {
        if (as_enqueue_async_action('a27_forbidden') !== 0
            || as_schedule_single_action(time()+9999,'a27_forbidden') !== 0
            || as_schedule_recurring_action(time()+9999,3600,'a27_forbidden') !== 0
            || as_schedule_cron_action(time()+9999,'* * * * *','a27_forbidden') !== 0) {
            throw new RuntimeException('A27_AS_PRIVATE_CANARY');
        }
    }, PHP_INT_MAX);
    if ($wpdb->query('UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @mysqli_query($wpdb->dbh,'UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @file_put_contents(ABSPATH.'forbidden','NO') !== false
        || wp_mail('fictif@example.org','A27_MAIL_PRIVATE_CANARY','A27_MAIL_PRIVATE_CANARY') !== false
        || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
        || wp_schedule_single_event(time()+9999,'a27_forbidden') !== false
        || function_exists('mail') || function_exists('exec')) {
        throw new RuntimeException('A27_EARLY_GUARD_PRIVATE_CANARY');
    }
    echo 'A27_BUFFERED_PRIVATE_CANARY';
}
'''
    mu.write_text(base_mu, encoding='utf-8')
    audit = audit_at(site, OUT / (storage + '-audit'))
    before, files = b.fingerprint(db), b.files(site)
    (OUT / (storage + '-db-before.json')).write_text(json.dumps(before), encoding='utf-8')
    dest = OUT / (storage + '-payments')
    p = inventory(site, dest, audit)
    b.check(storage + ':confined_success', (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, ''))
    d = json.loads((dest / 'paiements.json').read_text(encoding='utf-8'))
    expected = {'automatic': pool(6), 'cards': pool(3), 'relations': pool(4)}
    b.check(storage + ':six_exact_native_cases', d['counts'] == expected)
    b.check(storage + ':native_storage_and_audit_clock', d['storage'] == storage and d['as_of_utc'] == CLOCK)
    payload = p.stdout + p.stderr + ''.join(f.read_text(encoding='utf-8') for f in dest.iterdir())
    b.check(storage + ':private_references_accounts_dates_absent', not re.search(r'CANARY|@|4242|/scratch|a27-fictif|2027-03', payload))
    b.check(storage + ':private_permissions', dest.stat().st_mode & 0o777 == 0o700
            and all(f.stat().st_mode & 0o777 == 0o600 for f in dest.iterdir()))
    repeat = OUT / (storage + '-repeat')
    p = inventory(site, repeat, audit)
    b.check(storage + ':replay_identical', (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, '')
            and {f.name: f.read_bytes() for f in repeat.iterdir()} == {f.name: f.read_bytes() for f in dest.iterdir()})
    line = next(x for x in Path('/subject/a27/README.md').read_text(encoding='utf-8').splitlines()
                if x.startswith('python3 wp/outils/bascule/a27/confine.py '))
    documented = OUT / (storage + '-documented')
    substitutions = {'wp/outils/bascule/a27/confine.py': '/subject/a27/confine.py',
                     '--wp-path=/copie-verifiee': '--wp-path=' + str(site),
                     '--audit=/hors-web/audit-date/audit.json': '--audit=' + str(audit),
                     '--output=/hors-web/paiements-date': '--output=' + str(documented)}
    command = [substitutions.get(x, x) for x in shlex.split(line)]
    p = cmd(command, check=False)
    b.check(storage + ':documented_command_literal', len(command) == 5 and (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, '')
            and (documented / 'paiements.json').read_bytes() == (dest / 'paiements.json').read_bytes())
    for label, path in [('exists', dest), ('site', site / 'forbidden'), ('repo', Path('/subject/forbidden')),
                        ('ancestor', site.parent / 'forbidden'), ('root', Path('/forbidden'))]:
        p = inventory(site, path, audit)
        b.check(storage + ':guard_' + label, p.returncode == 1 and p.stdout == ''
                and re.fullmatch(r'A(?:27|12)_[A-Z_]+\n', p.stderr) is not None
                and (path == dest or not path.exists()))
    raw = cmd(['php', '/subject/a27/inventorier-paiements', '--wp-path=' + str(site),
               '--audit=' + str(audit), '--output=/report/raw-' + storage], check=False)
    b.check(storage + ':unconfined_php_refused', (raw.returncode, raw.stdout, raw.stderr) == (1, '', 'A27_CONFINEMENT_REQUIRED\n'))
    target = "foreach ($_SERVER['argv'] as $arg) { if (str_starts_with($arg,'--output=')) { $dir=substr($arg,9); } }"
    cases = [
        ('direct_stdout', "fwrite(STDOUT,'A27_STDOUT_PRIVATE_CANARY');", 'A27_PROCESS_OUTPUT_INVALID'),
        ('direct_stderr', "fwrite(STDERR,'A27_STDERR_PRIVATE_CANARY');", 'A27_PROCESS_OUTPUT_INVALID'),
        ('display_exit', "echo 'A27_DISPLAY_PRIVATE_CANARY'; exit(0);", 'A27_PROCESS_OUTPUT_INVALID'),
        ('silent_exit', 'exit(0);', 'A27_PROCESS_OUTPUT_INVALID'),
        ('shutdown_stdout', "register_shutdown_function(function(){fwrite(STDOUT,'A27_SHUTDOWN_PRIVATE_CANARY');});", 'A27_PROCESS_OUTPUT_INVALID'),
        ('shutdown_stderr', "register_shutdown_function(function(){fwrite(STDERR,'A27_SHUTDOWN_PRIVATE_CANARY');});", 'A27_PROCESS_OUTPUT_INVALID'),
        ('shutdown_display', "register_shutdown_function(function(){echo 'A27_SHUTDOWN_PRIVATE_CANARY';});", 'A27_PROCESS_OUTPUT_INVALID'),
        ('invalid_utf8', 'fwrite(STDERR,chr(255));', 'A27_PROCESS_OUTPUT_INVALID'),
        ('oversize', "fwrite(STDOUT,str_repeat('A27_PRIVATE_CANARY',8192));", 'A27_PROCESS_OUTPUT_INVALID'),
        ('exception', "throw new RuntimeException('A27_EXCEPTION_PRIVATE_CANARY');", 'A27_INVENTORY_FAILED'),
        ('forged_success', 'fwrite(STDOUT,"A27_OK paiements.json paiements.md\\n"); exit(0);', 'A27_REPORT_INVALID'),
        ('shutdown_invalid_json', "register_shutdown_function(function(){" + target + " file_put_contents($dir.'/paiements.json','{');});", 'A27_REPORT_INVALID'),
        ('shutdown_json_canary', "register_shutdown_function(function(){" + target + " $p=$dir.'/paiements.json';$d=json_decode(file_get_contents($p),true);$d['private']='A27_JSON_PRIVATE_CANARY';file_put_contents($p,json_encode($d));});", 'A27_REPORT_INVALID'),
        ('shutdown_markdown', "register_shutdown_function(function(){" + target + " file_put_contents($dir.'/paiements.md','A27_MARKDOWN_PRIVATE_CANARY',FILE_APPEND);});", 'A27_REPORT_INVALID'),
        ('shutdown_extra_file', "register_shutdown_function(function(){" + target + " file_put_contents($dir.'/extra.txt','A27_FILE_PRIVATE_CANARY');});", 'A27_REPORT_INVALID'),
        ('shutdown_partial', "register_shutdown_function(function(){" + target + " unlink($dir.'/paiements.md');});", 'A27_REPORT_INVALID'),
    ]
    try:
        for label, statement, want in cases:
            mu.write_text("<?php if (getenv('A27_CONFINED') === '1') {" + statement + '}\n' + base_mu[5:], encoding='utf-8')
            out = OUT / (storage + '-' + label)
            p = inventory(site, out, audit)
            b.check(storage + ':closed_channel_' + label, (p.returncode, p.stdout, p.stderr) == (1, '', want + '\n') and not out.exists())
            b.check(storage + ':discarded_channel_' + label, not list(OUT.glob('.a27-private-*'))
                    and not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
    finally:
        mu.write_text(base_mu, encoding='utf-8')
    bad = OUT / (storage + '-bad-audit')
    bad.mkdir()
    for label, want in [('schema', 'A27_AUDIT_GUARD'), ('clock', 'A27_CLOCK_INVALID'), ('storage', 'A27_AUDIT_STORAGE_MISMATCH')]:
        photo = json.loads(audit.read_text(encoding='utf-8'))
        if label == 'schema':
            photo['schema'] = 'A27_AUDIT_PRIVATE_CANARY'
        elif label == 'clock':
            photo['generated_at_utc'] = 'A27_CLOCK_PRIVATE_CANARY'
        else:
            photo['sections']['commerce']['order_storage'] = 'hpos' if storage == 'classic' else 'classic'
        (bad / 'audit.json').write_text(json.dumps(photo), encoding='utf-8')
        out = OUT / (storage + '-bad-' + label)
        p = inventory(site, out, bad / 'audit.json')
        b.check(storage + ':audit_refusal_' + label, (p.returncode, p.stdout, p.stderr) == (1, '', want + '\n') and not out.exists())
    shutil.rmtree(bad)
    after = b.fingerprint(db)
    (OUT / (storage + '-db-after.json')).write_text(json.dumps(after), encoding='utf-8')
    final_files = b.files(site)
    (OUT / (storage + '-files.json')).write_text(json.dumps({'before': files, 'after': final_files}), encoding='utf-8')
    b.check(storage + ':all_tables_scheduler_unchanged', before == after)
    b.check(storage + ':site_files_unchanged', files == final_files)
    b.check(storage + ':config_never_executed', not Path('/scratch/a02-bootstrap-trap').exists())
    # Cross the actual unchanged import engine on a separate fictional DB clone.
    clone = 'a27_' + storage + '_test'
    b.sql('mysql', 'CREATE DATABASE ' + clone)
    dump = cmd(['mariadb-dump', '--socket=' + b.SOCKET, '-uroot', db]).stdout
    cmd(['mariadb', '--socket=' + b.SOCKET, '-uroot', clone], data=dump)
    q = cmd(['php', '/opt/a27/neutralise.php'], env={'A27_DB': clone})
    provenance = json.loads(q.stdout)
    (OUT / (storage + '-neutralisation.json')).write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    b.check(storage + ':actual_import_purges_tokens', provenance == {'neutraliser_and_anonymiser_executed': True,
            'tokens_before': 6, 'tokens_after': 0, 'tokenmeta_after': 0, 'marker_count': 1})
    b.sql('mysql', "GRANT SELECT ON " + clone + ".* TO 'a02_" + storage + "'@'localhost'")
    (site / 'wp-config.php').write_text(cfg.replace("define('DB_NAME', '" + db + "')", "define('DB_NAME', '" + clone + "')"), encoding='utf-8')
    try:
        n_before, n_files = b.fingerprint(clone), b.files(site)
        n_audit = audit_at(site, OUT / (storage + '-neutral-audit'))
        out = OUT / (storage + '-neutral')
        p = inventory(site, out, n_audit)
        b.check(storage + ':neutral_success', (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, ''))
        data = json.loads((out / 'paiements.json').read_text(encoding='utf-8'))
        b.check(storage + ':neutral_all_unknown_no_useful_number', data['neutralisation'] == UNKNOWN
                and data['counts'] == dict.fromkeys(['automatic', 'cards', 'relations'], UNKNOWN))
        n_after = b.fingerprint(clone)
        for suffix, value in [('before', n_before), ('after', n_after)]:
            (OUT / (storage + '-neutral-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
        b.check(storage + ':neutral_db_files_unchanged', n_before == n_after and n_files == b.files(site))
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    seed(site, cfg, 5)
    five_before, five_files = b.fingerprint(db), b.files(site)
    five_audit = audit_at(site, OUT / (storage + '-five-audit'))
    out = OUT / (storage + '-five')
    p = inventory(site, out, five_audit)
    b.check(storage + ':five_success', (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, ''))
    data = json.loads((out / 'paiements.json').read_text(encoding='utf-8'))
    expected_five = {
        'automatic': {'groups': [{'gateway': 'paypal', 'type': 'accord_paypal', 'count': 5},
                                 {'gateway': 'stripe', 'type': 'carte', 'count': 15},
                                 {'gateway': 'stripe', 'type': 'illisible', 'count': 5},
                                 {'gateway': 'stripe_sepa', 'type': 'mandat_sepa', 'count': 5}], 'autres': 0},
        'cards': {'groups': [{'gateway': 'stripe', 'expiry': 'expired', 'count': 5},
                             {'gateway': 'stripe', 'expiry': 'within_six_months', 'count': 10}], 'autres': 0},
        'relations': {'groups': [{'gateway': 'autre', 'metric': 'accounts_multiple_tokens', 'count': 5},
                                 {'gateway': 'paypal', 'metric': 'subscriptions_unlinked', 'count': 5},
                                 {'gateway': 'stripe', 'metric': 'subscriptions_unlinked', 'count': 5},
                                 {'gateway': 'stripe', 'metric': 'tokens_without_living_subscription', 'count': 5}], 'autres': 0}}
    b.check(storage + ':five_exact_gateway_type_expiry_relations', data['counts'] == expected_five)
    five_after = b.fingerprint(db)
    for suffix, value in [('before', five_before), ('after', five_after)]:
        (OUT / (storage + '-five-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
    b.check(storage + ':five_db_files_unchanged', five_before == five_after and five_files == b.files(site))
    b.check(storage + ':all_retained_files_clean', not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))


b.run_storage = run_storage
if __name__ == '__main__':
    sys.exit(b.main())
