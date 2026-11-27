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
import tempfile

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('a02_fixture', '/opt/a02/inside.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OUT = Path('/report')
SUCCESS = 'A31_OK commandes.json commandes.md\n'
UNKNOWN = 'inconnu après neutralisation'
from expected import expected
CLOCK = '2026-11-26T12:00:00+00:00'


def cmd(args, check=True, env=None, data=None, timeout=240):
    p = subprocess.run(args, input=data, capture_output=True, text=True, encoding='utf-8', errors='strict',
                       timeout=timeout, env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                                             'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})
    if check and p.returncode:
        raise RuntimeError('A31_FIXTURE_COMMAND_FAILED')
    return p


b.cmd = cmd
original_check = b.check


def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {k: detail[k] for k in ['versions', 'hpos', 'subscriptions', 'rules', 'restriction_real']}
    return original_check(name, ok, detail)


b.check = check


def inventory(site, output, audit, *extra):
    return cmd(['python3', '/subject/a31/confine.py', '--wp-path=' + str(site), '--audit=' + str(audit),
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
    writable = writable.replace("define('ABSPATH', __DIR__.'/');", "if (!defined('ABSPATH')) { define('ABSPATH', __DIR__.'/'); }")
    (site / 'wp-config.php').write_text(writable, encoding='utf-8')
    try:
        q = b.wp(site, ['eval-file', '/opt/a31/seed.php', '--use-include'], env={'A31_REPETITIONS': str(repeats)})
        b.check(site.name + ':native_seed_' + str(repeats), q.stdout == 'A31_SEED_OK\n' and not q.stderr)
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')


def pool(n):
    return {'groups': [], 'autres': n}


def run_storage(storage):
    site, db, _ = b.install(storage)
    (OUT / (storage + '-seed.json')).unlink()
    q = cmd(['php', '/opt/a31/standard.php', str(site)], check=False)
    b.check(storage + ':installed_standard_before_subject', q.returncode == 0 and q.stdout == q.stderr == '')
    cfg = (site / 'wp-config.php').read_text(encoding='utf-8')
    seed(site, cfg)
    mu = site / 'wp-content/mu-plugins/a31-probe.php'
    base_mu = '''<?php
if (getenv('A31_CONFINED') === '1') {
    global $wpdb;
    require_once ABSPATH.'wp-includes/pluggable.php';
    add_action('plugins_loaded', static function () {
        if (as_enqueue_async_action('a31_forbidden') !== 0
            || as_schedule_single_action(time()+9999,'a31_forbidden') !== 0
            || as_schedule_recurring_action(time()+9999,3600,'a31_forbidden') !== 0
            || as_schedule_cron_action(time()+9999,'* * * * *','a31_forbidden') !== 0) {
            throw new RuntimeException('A31_AS_PRIVATE_CANARY');
        }
    }, PHP_INT_MAX);
    if ($wpdb->query('UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @mysqli_query($wpdb->dbh,'UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @file_put_contents(ABSPATH.'forbidden','NO') !== false
        || wp_mail('fictif@example.org','A31_MAIL_PRIVATE_CANARY','A31_MAIL_PRIVATE_CANARY') !== false
        || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
        || wp_schedule_single_event(time()+9999,'a31_forbidden') !== false
        || function_exists('mail') || function_exists('exec')) {
        throw new RuntimeException('A31_EARLY_GUARD_PRIVATE_CANARY');
    }
    echo 'A31_BUFFERED_PRIVATE_CANARY';
}
'''
    mu.write_text(base_mu, encoding='utf-8')
    audit = audit_at(site, OUT / (storage + '-audit'))
    before, files = b.fingerprint(db), b.files(site)
    (OUT / (storage + '-db-before.json')).write_text(json.dumps(before), encoding='utf-8')
    dest = OUT / (storage + '-history')
    p = inventory(site, dest, audit)
    b.check(storage + ':confined_success', (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, ''))
    d = json.loads((dest / 'commandes.json').read_text(encoding='utf-8'))
    b.check(storage + ':ten_exact_native_cases', d['counts'] == expected(1))
    b.check(storage + ':native_storage_no_fine_date', d['storage'] == storage and 'as_of_utc' not in d)
    payload = p.stdout + p.stderr + ''.join(f.read_text(encoding='utf-8') for f in dest.iterdir())
    b.check(storage + ':private_references_accounts_dates_absent', not re.search(r'CANARY|a31canary|@|97[.]31|9[.]31|/scratch|a31-fictif|2020-06|987654321', payload))
    b.check(storage + ':private_permissions', dest.stat().st_mode & 0o777 == 0o700
            and all(f.stat().st_mode & 0o777 == 0o600 for f in dest.iterdir()))
    repeat = OUT / (storage + '-repeat')
    p = inventory(site, repeat, audit)
    b.check(storage + ':replay_identical', (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, '')
            and {f.name: f.read_bytes() for f in repeat.iterdir()} == {f.name: f.read_bytes() for f in dest.iterdir()})
    line = next(x for x in Path('/subject/a31/README.md').read_text(encoding='utf-8').splitlines()
                if x.startswith('python3 wp/outils/bascule/a31/confine.py '))
    documented = OUT / (storage + '-documented')
    substitutions = {'wp/outils/bascule/a31/confine.py': '/subject/a31/confine.py',
                     '--wp-path=/copie-verifiee': '--wp-path=' + str(site),
                     '--audit=/hors-web/audit-date/audit.json': '--audit=' + str(audit),
                     '--output=/hors-web/commandes-date': '--output=' + str(documented)}
    command = [substitutions.get(x, x) for x in shlex.split(line)]
    p = cmd(command, check=False)
    b.check(storage + ':documented_command_literal', len(command) == 5 and (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, '')
            and (documented / 'commandes.json').read_bytes() == (dest / 'commandes.json').read_bytes())
    for label, path in [('exists', dest), ('site', site / 'forbidden'), ('repo', Path('/subject/forbidden')),
                        ('ancestor', site.parent / 'forbidden'), ('root', Path('/forbidden'))]:
        p = inventory(site, path, audit)
        b.check(storage + ':guard_' + label, p.returncode == 1 and p.stdout == ''
                and re.fullmatch(r'A(?:31|12)_[A-Z_]+\n', p.stderr) is not None
                and (path == dest or not path.exists()))
    raw = cmd(['php', '/subject/a31/inventorier-commandes', '--wp-path=' + str(site),
               '--audit=' + str(audit), '--output=/report/raw-' + storage], check=False)
    b.check(storage + ':unconfined_php_refused', (raw.returncode, raw.stdout, raw.stderr) == (1, '', 'A31_CONFINEMENT_REQUIRED\n'))
    target = "foreach ($_SERVER['argv'] as $arg) { if (str_starts_with($arg,'--output=')) { $dir=substr($arg,9); } }"
    coherent = "$p=$dir.'/commandes.json';$d=json_decode(file_get_contents($p),true);$d['counts']['natures']['autres']=7;$j=json_encode($d,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES).\"\\n\";file_put_contents($p,$j);$m=file_get_contents($dir.'/commandes.md');$pos=strpos($m,'```json');file_put_contents($dir.'/commandes.md',substr($m,0,$pos).'```json'.\"\\n\".$j.\"```\\n\");"
    cases = [
        ('direct_stdout', "fwrite(STDOUT,'A31_STDOUT_PRIVATE_CANARY');", 'A31_PROCESS_OUTPUT_INVALID'),
        ('direct_stderr', "fwrite(STDERR,'A31_STDERR_PRIVATE_CANARY');", 'A31_PROCESS_OUTPUT_INVALID'),
        ('display_exit', "echo 'A31_DISPLAY_PRIVATE_CANARY'; exit(0);", 'A31_PROCESS_OUTPUT_INVALID'),
        ('silent_exit', 'exit(0);', 'A31_PROCESS_OUTPUT_INVALID'),
        ('shutdown_stdout', "register_shutdown_function(function(){fwrite(STDOUT,'A31_SHUTDOWN_PRIVATE_CANARY');});", 'A31_PROCESS_OUTPUT_INVALID'),
        ('shutdown_stderr', "register_shutdown_function(function(){fwrite(STDERR,'A31_SHUTDOWN_PRIVATE_CANARY');});", 'A31_PROCESS_OUTPUT_INVALID'),
        ('shutdown_display', "register_shutdown_function(function(){echo 'A31_SHUTDOWN_PRIVATE_CANARY';});", 'A31_PROCESS_OUTPUT_INVALID'),
        ('invalid_utf8', 'fwrite(STDERR,chr(255));', 'A31_PROCESS_OUTPUT_INVALID'),
        ('oversize', "fwrite(STDOUT,str_repeat('A31_PRIVATE_CANARY',8192));", 'A31_PROCESS_OUTPUT_INVALID'),
        ('exception', "throw new RuntimeException('A31_EXCEPTION_PRIVATE_CANARY');", 'A31_INVENTORY_FAILED'),
        ('forged_success', 'fwrite(STDOUT,"A31_OK commandes.json commandes.md\\n"); exit(0);', 'A31_PROCESS_OUTPUT_INVALID'),
        ('shutdown_invalid_json', "register_shutdown_function(function(){" + target + " file_put_contents($dir.'/commandes.json','{');});", 'A31_REPORT_INVALID'),
        ('shutdown_json_canary', "register_shutdown_function(function(){" + target + " $p=$dir.'/commandes.json';$d=json_decode(file_get_contents($p),true);$d['private']='A31_JSON_PRIVATE_CANARY';file_put_contents($p,json_encode($d));});", 'A31_REPORT_INVALID'),
        ('shutdown_markdown', "register_shutdown_function(function(){" + target + " file_put_contents($dir.'/commandes.md','A31_MARKDOWN_PRIVATE_CANARY',FILE_APPEND);});", 'A31_REPORT_INVALID'),
        ('shutdown_extra_file', "register_shutdown_function(function(){" + target + " file_put_contents($dir.'/extra.txt','A31_FILE_PRIVATE_CANARY');});", 'A31_REPORT_INVALID'),
        ('shutdown_partial', "register_shutdown_function(function(){" + target + " unlink($dir.'/commandes.md');});", 'A31_REPORT_INVALID'),
        ('shutdown_valid_counts_and_markdown', "register_shutdown_function(function(){" + target + coherent + "});", 'A31_REPORT_INVALID'),
    ]
    fence_spec = importlib.util.spec_from_file_location('a31_native_fence', '/subject/a12/confine.py')
    fence = importlib.util.module_from_spec(fence_spec)
    fence_spec.loader.exec_module(fence)
    witnesses = {'direct_stdout', 'direct_stderr', 'display_exit', 'shutdown_stdout', 'shutdown_stderr',
                 'shutdown_display', 'oversize', 'shutdown_json_canary', 'shutdown_markdown', 'shutdown_extra_file',
                 'shutdown_valid_counts_and_markdown'}
    try:
        for label, statement, want in cases:
            mu.write_text("<?php if (getenv('A31_CONFINED') === '1') {" + statement + '}\n' + base_mu[5:], encoding='utf-8')
            out = OUT / (storage + '-' + label)
            p = inventory(site, out, audit)
            b.check(storage + ':closed_channel_' + label, (p.returncode, p.stdout, p.stderr) == (1, '', want + '\n') and not out.exists())
            b.check(storage + ':discarded_channel_' + label, not list(OUT.glob('.a31-private-*'))
                    and not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
            if label in witnesses:
                # Deliberately omit the stream/publication guardian only in this
                # disposable fixture. Observe raw evidence in RAM, then destroy it.
                with tempfile.TemporaryDirectory(prefix='a31-witness-', dir='/scratch') as temporary:
                    stage = Path(temporary)
                    (stage / 'audit').mkdir()
                    shutil.copyfile(audit, stage / 'audit/audit.json')
                    command = ['php', '-d', 'display_errors=0', '-d', 'log_errors=0', '-d',
                               'disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',
                               '/subject/a31/inventorier-commandes', '--wp-path=' + str(site),
                               '--audit=' + str(stage / 'audit/audit.json'), '--output=' + str(stage / 'result')]
                    witness = subprocess.run(command, capture_output=True, timeout=120,
                                             env={**os.environ, 'A31_CONFINED': '1'},
                                             preexec_fn=lambda: fence.confine(stage))
                    observed = b'CANARY' in witness.stdout + witness.stderr or any(
                        b'CANARY' in f.read_bytes() for f in (stage / 'result').rglob('*') if f.is_file())
                    if label == 'shutdown_valid_counts_and_markdown':
                        observed = json.loads((stage / 'result/commandes.json').read_bytes())['counts']['natures']['autres'] == 7
                    b.check(storage + ':mutation_witness_' + label, observed)
    finally:
        mu.write_text(base_mu, encoding='utf-8')
    bad = OUT / (storage + '-bad-audit')
    bad.mkdir()
    for label, want in [('schema', 'A31_AUDIT_GUARD'), ('storage', 'A31_AUDIT_STORAGE_MISMATCH')]:
        photo = json.loads(audit.read_text(encoding='utf-8'))
        if label == 'schema':
            photo['schema'] = 'A31_AUDIT_PRIVATE_CANARY'
        elif label == 'clock':
            photo['generated_at_utc'] = 'A31_CLOCK_PRIVATE_CANARY'
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
    clone = 'a31_' + storage + '_test'
    b.sql('mysql', 'CREATE DATABASE ' + clone)
    dump = cmd(['mariadb-dump', '--socket=' + b.SOCKET, '-uroot', db]).stdout
    cmd(['mariadb', '--socket=' + b.SOCKET, '-uroot', clone], data=dump)
    q = cmd(['php', '/opt/a31/neutralise.php'], env={'A31_DB': clone, 'A31_STORAGE': storage})
    provenance = json.loads(q.stdout)
    (OUT / (storage + '-neutralisation.json')).write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    b.check(storage + ':actual_import_changes_extension_not_structure',
            provenance['neutraliser_and_anonymiser_executed'] is True
            and provenance['extension_relation_before'] == 1 and provenance['extension_relation_after'] == 0
            and provenance['renewal_relation_before'] == provenance['renewal_relation_after'] == 2
            and provenance['structure_before_sha256'] == provenance['structure_after_sha256']
            and provenance['marker_count'] == 1)
    b.sql('mysql', "GRANT SELECT ON " + clone + ".* TO 'a02_" + storage + "'@'localhost'")
    (site / 'wp-config.php').write_text(cfg.replace("define('DB_NAME', '" + db + "')", "define('DB_NAME', '" + clone + "')"), encoding='utf-8')
    try:
        n_before, n_files = b.fingerprint(clone), b.files(site)
        n_audit = audit_at(site, OUT / (storage + '-neutral-audit'))
        out = OUT / (storage + '-neutral')
        p = inventory(site, out, n_audit)
        b.check(storage + ':neutral_success', (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, ''))
        data = json.loads((out / 'commandes.json').read_text(encoding='utf-8'))
        neutral_expected = expected(1)
        neutral_expected.update(dict.fromkeys(['natures'], UNKNOWN))
        b.check(storage + ':neutral_exact_partial_unknown', data['neutralisation'] == UNKNOWN
                and data['counts'] == neutral_expected)
        n_after = b.fingerprint(clone)
        n_final_files = b.files(site)
        (OUT / (storage + '-neutral-files.json')).write_text(json.dumps({'before': n_files, 'after': n_final_files}), encoding='utf-8')
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
    data = json.loads((out / 'commandes.json').read_text(encoding='utf-8'))
    b.check(storage + ':five_exact_year_status_nature_relations', data['counts'] == expected(5))
    five_after = b.fingerprint(db)
    five_final_files = b.files(site)
    (OUT / (storage + '-five-files.json')).write_text(json.dumps({'before': five_files, 'after': five_final_files}), encoding='utf-8')
    for suffix, value in [('before', five_before), ('after', five_after)]:
        (OUT / (storage + '-five-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
    b.check(storage + ':five_db_files_unchanged', five_before == five_after and five_files == b.files(site))
    b.check(storage + ':all_retained_files_clean', not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))


b.run_storage = run_storage
if __name__ == '__main__':
    sys.exit(b.main())
