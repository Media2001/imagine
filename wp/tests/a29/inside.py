"""Parent-only synthetic classic/HPOS bank; private streams stay in RAM."""
import importlib.util
import hashlib
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
SUCCESS = 'A29_OK taches.json taches.md\n'
UNKNOWN = 'inconnu après neutralisation'
CLOCK = '2026-11-26T12:00:00+00:00'


def cmd(args, check=True, env=None, data=None, timeout=240):
    p = subprocess.run(args, input=data, capture_output=True, text=True, encoding='utf-8', errors='strict',
                       timeout=timeout, env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                                             'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})
    if check and p.returncode:
        known = ('A29_SEED_REPETITIONS', 'A29_SEED_CUSTOMER', 'A29_SEED_SUBSCRIPTION',
                 'A29_SEED_STORE', 'A29_SEED_ACTION', 'A29_SEED_NATIVE_READBACK',
                 'A29_SEED_COUNTS', 'A29_SEED_SQL_COUNTS')
        payload = p.stdout + p.stderr
        diagnostic = {'scope': 'closed_fictitious_setup_failure_not_acceptance', 'exit_code': p.returncode,
                      'stage': 'seed' if '/opt/a29/seed.php' in args else 'other_setup',
                      'known_codes': [key for key in known if key in payload]}
        index = len(list(OUT.glob('closed-setup-error-*.json')))
        (OUT / ('closed-setup-error-' + str(index) + '.json')).write_text(
            json.dumps(diagnostic, indent=2) + '\n', encoding='utf-8')
        raise RuntimeError('A29_FIXTURE_COMMAND_FAILED')
    return p


b.cmd = cmd
original_check = b.check


def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {k: detail[k] for k in ['versions', 'hpos', 'subscriptions', 'rules', 'restriction_real']}
    return original_check(name, ok, detail)


b.check = check


def inventory(site, output, audit, *extra):
    return cmd(['python3', '/subject/a29/confine.py', '--wp-path=' + str(site), '--audit=' + str(audit),
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
    # WP-CLI already defines ABSPATH; only the writable oracle config is adapted.
    writable = writable.replace("define('ABSPATH', __DIR__.'/');", "if (!defined('ABSPATH')) { define('ABSPATH', __DIR__.'/'); }")
    (site / 'wp-config.php').write_text(writable, encoding='utf-8')
    try:
        q = b.wp(site, ['eval-file', '/opt/a29/seed.php', '--use-include'], env={'A29_REPETITIONS': str(repeats)})
        b.check(site.name + ':native_seed_' + str(repeats), q.stdout == 'A29_SEED_OK\n' and not q.stderr)
        rows = b.sql('a02_' + site.name,
                     'SELECT status,COUNT(*) AS n FROM wp_actionscheduler_actions GROUP BY status ORDER BY status').stdout.splitlines()[1:]
        observed = {}
        for line in rows:
            status, number = line.split('\t')
            if status not in {'pending', 'failed'}:
                raise RuntimeError('A29_FIXTURE_SCHEDULER_EXTRA_STATUS')
            observed[status] = int(number)
        expected = {'pending': 12 * repeats, 'failed': repeats}
        receipt = {'scope': 'native_seed_after_php_shutdown', 'counts': observed, 'expected': expected,
                   'exit_code': int(observed != expected)}
        if observed != expected:
            planned = {'woocommerce_scheduled_subscription_payment', 'woocommerce_scheduled_subscription_payment_retry',
                       'woocommerce_scheduled_subscription_expiration', 'A29_UNKNOWN_ACTIVE_PRIVATE_CANARY',
                       'A29_UNKNOWN_ORPHAN_PRIVATE_CANARY'}
            helpers = {'action_scheduler/migration_hook': 'native_migration',
                       'action_scheduler/ensure_recurring_actions': 'native_ensure_recurring'}
            hooks = b.sql('a02_' + site.name,
                          "SELECT hook FROM wp_actionscheduler_actions WHERE status='pending'").stdout.splitlines()[1:]
            receipt['closed_extra_followups'] = [helpers.get(hook, 'unqualified_native_followup')
                                                for hook in hooks if hook not in planned]
            extra = set(hook for hook in hooks if hook not in planned)
            receipt['extra_followup_sha256'] = sorted(hashlib.sha256(hook.encode('utf-8')).hexdigest() for hook in extra)
            matched = []
            for owner in ('woocommerce', 'woocommerce-subscriptions'):
                root = site / 'wp-content/plugins' / owner
                for source_file in root.rglob('*.php'):
                    source = source_file.read_text(encoding='utf-8', errors='replace')
                    for hook in extra:
                        literal = "'" + hook + "'"
                        position = source.find(literal)
                        if position < 0:
                            continue
                        functions = re.findall(r'function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', source[:position])
                        line_index = source.count('\n', 0, position)
                        excerpt = '\n'.join(source.splitlines()[max(0, line_index - 5):line_index + 20]).replace(hook, '<NATIVE_HELPER>')
                        excerpt = re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", "'<LITERAL>'", excerpt)
                        matched.append({'owner': owner, 'source_sha256': hashlib.sha256(source_file.read_bytes()).hexdigest(),
                                        'method': functions[-1] if functions else 'class_constant',
                                        'hook_sha256': hashlib.sha256(hook.encode('utf-8')).hexdigest(),
                                        'public_source_excerpt_literals_masked': excerpt[:4000]})
            receipt['public_native_source_matches'] = matched
        (OUT / (site.name + '-seed-shutdown-' + str(repeats) + '.json')).write_text(
            json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        b.check(site.name + ':native_seed_after_shutdown_' + str(repeats), observed == expected)
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')


def pool(n):
    return {'groups': [], 'autres': n}


def expected_counts(repeats):
    if repeats == 1:
        return {'pending': {'groups': [{'family': 'renouvellement', 'count': 9}], 'autres': 6},
                'overdue': pool(2), 'failed': pool(1), 'renewal_weeks': pool(7),
                'other_tasks': 'moins de cinq', 'other_active_extensions': 'attribution indéterminée'}
    return {'pending': {'groups': [{'family': family, 'count': n} for family, n in [
                ('autre', 10), ('email', 5), ('entretien_wordpress', 5), ('fin_abonnement', 5),
                ('nouvelle_tentative', 5), ('renouvellement', 45)]], 'autres': 0},
            'overdue': {'groups': [{'family': 'entretien_wordpress', 'count': 5},
                                  {'family': 'renouvellement', 'count': 5}], 'autres': 0},
            'failed': {'groups': [{'family': 'renouvellement', 'count': 5}], 'autres': 0},
            'renewal_weeks': {'groups': [{'week': week, 'count': n} for week, n in [(1, 10), (2, 15), (3, 5), (8, 5)]], 'autres': 0},
            'other_tasks': 10, 'other_active_extensions': 'attribution indéterminée'}


def run_storage(storage):
    site, db, _ = b.install(storage)
    (OUT / (storage + '-seed.json')).unlink()
    # The pristine fixture is in AS migration mode (HybridStore). Qualify the
    # supported native DBStore explicitly through its installed factory filter;
    # never run a migration job and never weaken the subject's store refusal.
    datastore_mu = site / 'wp-content/mu-plugins/a29-datastore.php'
    dbstore_fixture = "<?php\nadd_filter('action_scheduler_store_class', static fn(): string => 'ActionScheduler_DBStore', 0);\n"
    datastore_mu.write_text(dbstore_fixture, encoding='utf-8')
    q = cmd(['php', '/opt/a29/standard.php', str(site)], check=False)
    b.check(storage + ':installed_standard_before_subject', q.returncode == 0 and q.stdout == q.stderr == '')
    cfg = (site / 'wp-config.php').read_text(encoding='utf-8')
    plugin = site / 'wp-content/plugins/a29-inconnu/a29-inconnu.php'
    plugin.parent.mkdir()
    plugin.write_text("<?php\n/* Plugin Name: Extension fictive A29 */\n"
                      "add_action('A29_UNKNOWN_ACTIVE_PRIVATE_CANARY', static function(){throw new RuntimeException('A29_ACTION_EXECUTED_PRIVATE_CANARY');});\n"
                      "add_action('woocommerce_scheduled_subscription_payment', static function(){throw new RuntimeException('A29_RENEWAL_EXECUTED_PRIVATE_CANARY');});\n", encoding='utf-8')
    seed(site, cfg)
    mu = site / 'wp-content/mu-plugins/a29-probe.php'
    base_mu = '''<?php
if (getenv('A29_CONFINED') === '1') {
    global $wpdb;
    require_once ABSPATH.'wp-includes/pluggable.php';
    add_action('plugins_loaded', static function () {
        if (as_enqueue_async_action('a29_forbidden') !== 0
            || as_schedule_single_action(time()+9999,'a29_forbidden') !== 0
            || as_schedule_recurring_action(time()+9999,3600,'a29_forbidden') !== 0
            || as_schedule_cron_action(time()+9999,'* * * * *','a29_forbidden') !== 0) {
            throw new RuntimeException('A29_AS_PRIVATE_CANARY');
        }
    }, PHP_INT_MAX);
    if ($wpdb->query('UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @mysqli_query($wpdb->dbh,'UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @file_put_contents(ABSPATH.'forbidden','NO') !== false
        || wp_mail('fictif@example.org','A29_MAIL_PRIVATE_CANARY','A29_MAIL_PRIVATE_CANARY') !== false
        || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
        || wp_schedule_single_event(time()+9999,'a29_forbidden') !== false
        || function_exists('mail') || function_exists('exec')) {
        throw new RuntimeException('A29_EARLY_GUARD_PRIVATE_CANARY');
    }
    echo 'A29_BUFFERED_PRIVATE_CANARY';
}
'''
    mu.write_text(base_mu, encoding='utf-8')
    audit = audit_at(site, OUT / (storage + '-audit'))
    before, files = b.fingerprint(db), b.files(site)
    (OUT / (storage + '-db-before.json')).write_text(json.dumps(before), encoding='utf-8')
    dest = OUT / (storage + '-tasks')
    p = inventory(site, dest, audit)
    b.check(storage + ':confined_success', (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, ''))
    d = json.loads((dest / 'taches.json').read_text(encoding='utf-8'))
    b.check(storage + ':exact_wpcron_as_pending_overdue_failed_weeks', d['counts'] == expected_counts(1))
    b.check(storage + ':no_action_callback_executed', p.returncode == 0)
    b.check(storage + ':native_storage_and_audit_clock', d['storage'] == storage and d['as_of_utc'] == CLOCK)
    payload = p.stdout + p.stderr + ''.join(f.read_text(encoding='utf-8') for f in dest.iterdir())
    b.check(storage + ':private_hooks_arguments_ids_dates_absent', not re.search(r'CANARY|@|subscription_id|/scratch|a29-fictif|2027-03', payload))
    b.check(storage + ':private_permissions', dest.stat().st_mode & 0o777 == 0o700
            and all(f.stat().st_mode & 0o777 == 0o600 for f in dest.iterdir()))
    repeat = OUT / (storage + '-repeat')
    p = inventory(site, repeat, audit)
    b.check(storage + ':replay_identical', (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, '')
            and {f.name: f.read_bytes() for f in repeat.iterdir()} == {f.name: f.read_bytes() for f in dest.iterdir()})
    # Real native HybridStore remains unsupported: reading its query API can
    # migrate actions. Refuse it rather than guessing that DB tables are complete.
    hybrid_before = b.fingerprint(db)
    datastore_mu.write_text('<?php\n// Native default store: no fixture override.\n', encoding='utf-8')
    try:
        hybrid_files = b.files(site)
        unsupported = OUT / (storage + '-hybrid-refused')
        q = inventory(site, unsupported, audit)
        b.check(storage + ':native_hybrid_store_refused',
                (q.returncode, q.stdout, q.stderr) == (1, '', 'A29_STORE_UNSUPPORTED\n') and not unsupported.exists())
        b.check(storage + ':native_hybrid_refusal_database_files_unchanged',
                hybrid_before == b.fingerprint(db) and hybrid_files == b.files(site))
    finally:
        datastore_mu.write_text(dbstore_fixture, encoding='utf-8')
    line = next(x for x in Path('/subject/a29/README.md').read_text(encoding='utf-8').splitlines()
                if x.startswith('python3 wp/outils/bascule/a29/confine.py '))
    documented = OUT / (storage + '-documented')
    substitutions = {'wp/outils/bascule/a29/confine.py': '/subject/a29/confine.py',
                     '--wp-path=/copie-verifiee': '--wp-path=' + str(site),
                     '--audit=/hors-web/audit-date/audit.json': '--audit=' + str(audit),
                     '--output=/hors-web/taches-date': '--output=' + str(documented)}
    command = [substitutions.get(x, x) for x in shlex.split(line)]
    p = cmd(command, check=False)
    b.check(storage + ':documented_command_literal', len(command) == 5 and (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, '')
            and (documented / 'taches.json').read_bytes() == (dest / 'taches.json').read_bytes())
    for label, path in [('exists', dest), ('site', site / 'forbidden'), ('repo', Path('/subject/forbidden')),
                        ('ancestor', site.parent / 'forbidden'), ('root', Path('/forbidden'))]:
        p = inventory(site, path, audit)
        b.check(storage + ':guard_' + label, p.returncode == 1 and p.stdout == ''
                and re.fullmatch(r'A(?:29|12)_[A-Z_]+\n', p.stderr) is not None
                and (path == dest or not path.exists()))
    raw = cmd(['php', '/subject/a29/inventorier-taches', '--wp-path=' + str(site),
               '--audit=' + str(audit), '--output=/report/raw-' + storage], check=False)
    b.check(storage + ':unconfined_php_refused', (raw.returncode, raw.stdout, raw.stderr) == (1, '', 'A29_CONFINEMENT_REQUIRED\n'))
    target = "foreach ($_SERVER['argv'] as $arg) { if (str_starts_with($arg,'--output=')) { $dir=substr($arg,9); } }"
    coherent = "$p=$dir.'/taches.json';$d=json_decode(file_get_contents($p),true);$d['counts']['pending']['autres']=7;$j=json_encode($d,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES).\"\\n\";file_put_contents($p,$j);$m=file_get_contents($dir.'/taches.md');$pos=strpos($m,'```json');file_put_contents($dir.'/taches.md',substr($m,0,$pos).'```json'.\"\\n\".$j.\"```\\n\");"
    cases = [
        ('direct_stdout', "fwrite(STDOUT,'A29_STDOUT_PRIVATE_CANARY');", 'A29_PROCESS_OUTPUT_INVALID'),
        ('direct_stderr', "fwrite(STDERR,'A29_STDERR_PRIVATE_CANARY');", 'A29_PROCESS_OUTPUT_INVALID'),
        ('display_exit', "echo 'A29_DISPLAY_PRIVATE_CANARY'; exit(0);", 'A29_PROCESS_OUTPUT_INVALID'),
        ('silent_exit', 'exit(0);', 'A29_PROCESS_OUTPUT_INVALID'),
        ('shutdown_stdout', "register_shutdown_function(function(){fwrite(STDOUT,'A29_SHUTDOWN_PRIVATE_CANARY');});", 'A29_PROCESS_OUTPUT_INVALID'),
        ('shutdown_stderr', "register_shutdown_function(function(){fwrite(STDERR,'A29_SHUTDOWN_PRIVATE_CANARY');});", 'A29_PROCESS_OUTPUT_INVALID'),
        ('shutdown_display', "register_shutdown_function(function(){echo 'A29_SHUTDOWN_PRIVATE_CANARY';});", 'A29_PROCESS_OUTPUT_INVALID'),
        ('invalid_utf8', 'fwrite(STDERR,chr(255));', 'A29_PROCESS_OUTPUT_INVALID'),
        ('oversize', "fwrite(STDOUT,str_repeat('A29_PRIVATE_CANARY',8192));", 'A29_PROCESS_OUTPUT_INVALID'),
        ('exception', "throw new RuntimeException('A29_EXCEPTION_PRIVATE_CANARY');", 'A29_INVENTORY_FAILED'),
        ('forged_success', 'fwrite(STDOUT,"A29_OK taches.json taches.md\\n"); exit(0);', 'A29_PROCESS_OUTPUT_INVALID'),
        ('shutdown_invalid_json', "register_shutdown_function(function(){" + target + " file_put_contents($dir.'/taches.json','{');});", 'A29_REPORT_INVALID'),
        ('shutdown_json_canary', "register_shutdown_function(function(){" + target + " $p=$dir.'/taches.json';$d=json_decode(file_get_contents($p),true);$d['private']='A29_JSON_PRIVATE_CANARY';file_put_contents($p,json_encode($d));});", 'A29_REPORT_INVALID'),
        ('shutdown_markdown', "register_shutdown_function(function(){" + target + " file_put_contents($dir.'/taches.md','A29_MARKDOWN_PRIVATE_CANARY',FILE_APPEND);});", 'A29_REPORT_INVALID'),
        ('shutdown_extra_file', "register_shutdown_function(function(){" + target + " file_put_contents($dir.'/extra.txt','A29_FILE_PRIVATE_CANARY');});", 'A29_REPORT_INVALID'),
        ('shutdown_partial', "register_shutdown_function(function(){" + target + " unlink($dir.'/taches.md');});", 'A29_REPORT_INVALID'),
        ('shutdown_valid_counts_and_markdown', "register_shutdown_function(function(){" + target + coherent + "});", 'A29_REPORT_INVALID'),
    ]
    fence_spec = importlib.util.spec_from_file_location('a29_native_fence', '/subject/a12/confine.py')
    fence = importlib.util.module_from_spec(fence_spec)
    fence_spec.loader.exec_module(fence)
    witnesses = {'direct_stdout', 'direct_stderr', 'display_exit', 'shutdown_stdout', 'shutdown_stderr',
                 'shutdown_display', 'oversize', 'shutdown_json_canary', 'shutdown_markdown', 'shutdown_extra_file',
                 'shutdown_valid_counts_and_markdown'}
    try:
        for label, statement, want in cases:
            mu.write_text("<?php if (getenv('A29_CONFINED') === '1') {" + statement + '}\n' + base_mu[5:], encoding='utf-8')
            out = OUT / (storage + '-' + label)
            p = inventory(site, out, audit)
            b.check(storage + ':closed_channel_' + label, (p.returncode, p.stdout, p.stderr) == (1, '', want + '\n') and not out.exists())
            b.check(storage + ':discarded_channel_' + label, not list(OUT.glob('.a29-private-*'))
                    and not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
            if label in witnesses:
                # Deliberately omit the stream/publication guardian only in this
                # disposable fixture. Observe raw evidence in RAM, then destroy it.
                with tempfile.TemporaryDirectory(prefix='a29-witness-', dir='/scratch') as temporary:
                    stage = Path(temporary)
                    (stage / 'audit').mkdir()
                    shutil.copyfile(audit, stage / 'audit/audit.json')
                    command = ['php', '-d', 'display_errors=0', '-d', 'log_errors=0', '-d',
                               'disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',
                               '/subject/a29/inventorier-taches', '--wp-path=' + str(site),
                               '--audit=' + str(stage / 'audit/audit.json'), '--output=' + str(stage / 'result')]
                    witness = subprocess.run(command, capture_output=True, timeout=120,
                                             env={**os.environ, 'A29_CONFINED': '1'},
                                             preexec_fn=lambda: fence.confine(stage))
                    observed = b'CANARY' in witness.stdout + witness.stderr or any(
                        b'CANARY' in f.read_bytes() for f in (stage / 'result').rglob('*') if f.is_file())
                    if label == 'shutdown_valid_counts_and_markdown':
                        schema_spec = importlib.util.spec_from_file_location('a29_native_witness_schema', '/subject/a29/report.py')
                        schema = importlib.util.module_from_spec(schema_spec)
                        schema_spec.loader.exec_module(schema)
                        observed = (json.loads((stage / 'result/taches.json').read_bytes())['counts']['pending']['autres'] == 7
                                    and schema.complete_report(stage / 'result', stage / 'audit/audit.json'))
                        b.check(storage + ':shutdown_mutation_still_valid_json_markdown', observed)
                    b.check(storage + ':mutation_witness_' + label, observed)
    finally:
        mu.write_text(base_mu, encoding='utf-8')
    bad = OUT / (storage + '-bad-audit')
    bad.mkdir()
    for label, want in [('schema', 'A29_AUDIT_GUARD'), ('clock', 'A29_CLOCK_INVALID'), ('storage', 'A29_AUDIT_STORAGE_MISMATCH')]:
        photo = json.loads(audit.read_text(encoding='utf-8'))
        if label == 'schema':
            photo['schema'] = 'A29_AUDIT_PRIVATE_CANARY'
        elif label == 'clock':
            photo['generated_at_utc'] = 'A29_CLOCK_PRIVATE_CANARY'
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
    clone = 'a29_' + storage + '_test'
    b.sql('mysql', 'CREATE DATABASE ' + clone)
    dump = cmd(['mariadb-dump', '--socket=' + b.SOCKET, '-uroot', db]).stdout
    cmd(['mariadb', '--socket=' + b.SOCKET, '-uroot', clone], data=dump)
    q = cmd(['php', '/opt/a29/neutralise.php'], env={'A29_DB': clone})
    provenance = json.loads(q.stdout)
    (OUT / (storage + '-neutralisation.json')).write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    b.check(storage + ':actual_import_erases_cron_cancels_pending_deletes_failed', not q.stderr and provenance == {
            'neutraliser_and_anonymiser_executed': True, 'before': {'cron': 3, 'pending': 12, 'failed': 1},
            'after': {'cron': 0, 'pending': 0, 'failed': 0, 'canceled': 12}, 'marker_count': 1})
    b.sql('mysql', "GRANT SELECT ON " + clone + ".* TO 'a02_" + storage + "'@'localhost'")
    (site / 'wp-config.php').write_text(cfg.replace("define('DB_NAME', '" + db + "')", "define('DB_NAME', '" + clone + "')"), encoding='utf-8')
    try:
        n_before, n_files = b.fingerprint(clone), b.files(site)
        n_audit = audit_at(site, OUT / (storage + '-neutral-audit'))
        out = OUT / (storage + '-neutral')
        p = inventory(site, out, n_audit)
        b.check(storage + ':neutral_success', (p.returncode, p.stdout, p.stderr) == (0, SUCCESS, ''))
        data = json.loads((out / 'taches.json').read_text(encoding='utf-8'))
        b.check(storage + ':neutral_all_unknown_no_useful_number', data['neutralisation'] == UNKNOWN
                and data['counts'] == dict.fromkeys(['pending', 'overdue', 'failed', 'renewal_weeks',
                                                    'other_tasks', 'other_active_extensions'], UNKNOWN))
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
    data = json.loads((out / 'taches.json').read_text(encoding='utf-8'))
    b.check(storage + ':five_exact_families_utc_boundaries', data['counts'] == expected_counts(5))
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
