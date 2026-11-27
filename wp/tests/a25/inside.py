"""Native synthetic A25 path; private canaries never enter receipts."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import shlex
import subprocess
import sys
import tempfile

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
        raise RuntimeError('A25_FIXTURE_COMMAND_FAILED')
    return p


b.cmd = cmd
original = b.check


def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {k: detail[k] for k in ['versions', 'hpos', 'subscriptions', 'rules', 'restriction_real']}
    return original(name, ok, detail)


b.check = check


def inventory(site, out, audit, *extra):
    return cmd(['python3', '/subject/a25/confine.py', '--wp-path=' + str(site),
                '--audit=' + str(audit), '--output=' + str(out), *extra], check=False)


def group(*pairs, autres=0):
    return {'groups': [], 'autres': autres}


def run_storage(storage):
    site, db, _ = b.install(storage)
    (OUT / (storage + '-seed.json')).unlink()
    cfg = (site / 'wp-config.php').read_text(encoding='utf-8')
    writable = cfg.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')").split(
        "\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site / 'wp-config.php').write_text(writable, encoding='utf-8')
    try:
        p = b.wp(site, ['eval-file', '/opt/a25/seed.php', '--use-include'])
        b.check(storage + ':native_seed', 'A25_SEED_OK' in p.stdout)
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    mu = site / 'wp-content/mu-plugins/a25-probe.php'
    base_mu = '''<?php
if (getenv('A25_CONFINED') === '1') {
    global $wpdb;
    require_once ABSPATH.'wp-includes/pluggable.php';
    add_filter('check_password', function () { throw new RuntimeException('A25_PASSWORD_TRIAL_PRIVATE_CANARY'); }, -999999);
    add_filter('authenticate', function () { throw new RuntimeException('A25_LOGIN_TRIAL_PRIVATE_CANARY'); }, -999999);
    add_action('plugins_loaded', static function () {
        if (as_enqueue_async_action('a25_forbidden') !== 0
            || as_schedule_single_action(time()+9999, 'a25_forbidden') !== 0
            || as_schedule_recurring_action(time()+9999, 3600, 'a25_forbidden') !== 0
            || as_schedule_cron_action(time()+9999, '* * * * *', 'a25_forbidden') !== 0) {
            throw new RuntimeException('A25_AS_GUARD_PRIVATE_CANARY');
        }
    }, PHP_INT_MAX);
    if ($wpdb->query('UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @mysqli_query($wpdb->dbh, 'UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @file_put_contents(ABSPATH.'forbidden', 'NO') !== false
        || wp_mail('fictif@example.org', 'A25_MAIL_PRIVATE_CANARY', 'A25_MAIL_PRIVATE_CANARY') !== false
        || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
        || wp_schedule_single_event(time()+9999, 'a25_forbidden') !== false
        || function_exists('mail') || function_exists('exec')) {
        throw new RuntimeException('A25_EARLY_GUARD_PRIVATE_CANARY');
    }
    echo 'A25_DISPLAY_PRIVATE_CANARY';
}
'''
    mu.write_text(base_mu, encoding='utf-8')
    audit = OUT / (storage + '-audit')
    b.check(storage + ':audit_success', b.audit(site, audit).returncode == 0)
    before = b.fingerprint(db)
    files = b.files(site)
    (OUT / (storage + '-db-before.json')).write_text(json.dumps(before), encoding='utf-8')
    dest = OUT / (storage + '-visitors')
    p = inventory(site, dest, audit / 'audit.json')
    b.check(storage + ':confined_success', p.returncode == 0 and p.stdout == 'A25_OK visiteurs.json visiteurs.md\n' and p.stderr == '')
    d = json.loads((dest / 'visiteurs.json').read_text(encoding='utf-8'))
    expected = {'comments': {'all': group(autres=3), 'email': group(autres=2),
                              'ip': group(autres=2), 'account': group(autres=1)},
                'forms': {'groups': [{'year': 2022, 'state': 'autre', 'count': 5}], 'autres': 4},
                'guests': group(autres=2)}
    b.check(storage + ':exact_native_counts', d['counts'] == expected)
    b.check(storage + ':closed_form_adapter_and_other', d['forms'] == {
        'listed_extensions': ['Fluent Forms'], 'other_tables': 2, 'coverage': 'heuristique bornée',
        'clear_messages_after_import': True,
        'clear_messages_after_import_label': 'avertissement éditorial permanent, non mesuré sur la copie inspectée'})
    b.check(storage + ':submission_pk_five_child_excluded', d['counts']['forms'] == expected['forms']
            and int(b.sql(db, 'SELECT COUNT(*) FROM wp_a25_submission_entries').stdout.splitlines()[-1]) == 5
            and int(b.sql(db, 'SELECT COUNT(*) FROM wp_a25_submission_details').stdout.splitlines()[-1]) == 10)
    payload = p.stdout + p.stderr + ''.join(f.read_text(encoding='utf-8') for f in dest.iterdir())
    b.check(storage + ':all_private_values_absent', not re.search(r'CANARY|@|/scratch|a25_unknown|a25-fictif|a02-admin|192\.0\.2', payload))
    b.check(storage + ':private_report_permissions', dest.stat().st_mode & 0o777 == 0o700
            and all(f.stat().st_mode & 0o777 == 0o600 for f in dest.iterdir()))
    repeat = OUT / (storage + '-repeat')
    q = inventory(site, repeat, audit / 'audit.json')
    b.check(storage + ':replay_identical', q.returncode == 0 and
            {f.name: f.read_bytes() for f in dest.iterdir()} == {f.name: f.read_bytes() for f in repeat.iterdir()})
    line = next(x for x in Path('/subject/a25/README.md').read_text(encoding='utf-8').splitlines()
                if x.startswith('python3 wp/outils/bascule/a25/confine.py '))
    documented = OUT / (storage + '-documented')
    replacements = {'wp/outils/bascule/a25/confine.py': '/subject/a25/confine.py',
                    '--wp-path=/copie-verifiee': '--wp-path=' + str(site),
                    '--audit=/hors-web/audit-date/audit.json': '--audit=' + str(audit / 'audit.json'),
                    '--output=/hors-web/visiteurs-date': '--output=' + str(documented)}
    command = [replacements.get(x, x) for x in shlex.split(line)]
    q = cmd(command, check=False)
    b.check(storage + ':documented_only_given_arguments', len(command) == 5 and q.returncode == 0
            and q.stdout == 'A25_OK visiteurs.json visiteurs.md\n' and q.stderr == ''
            and (documented / 'visiteurs.json').read_bytes() == (dest / 'visiteurs.json').read_bytes())
    for label, path in [('exists', dest), ('site', site / 'forbidden'), ('repo', Path('/subject/forbidden')),
                        ('ancestor', site.parent / 'forbidden'), ('root', Path('/forbidden'))]:
        q = inventory(site, path, audit / 'audit.json')
        b.check(storage + ':guard:' + label, q.returncode == 1 and q.stdout == ''
                and re.fullmatch(r'A(?:25|12)_[A-Z_]+\n', q.stderr) is not None
                and (path == dest or not path.exists()))
    raw = cmd(['php', '/subject/a25/inventorier-visiteurs', '--wp-path=' + str(site),
               '--audit=' + str(audit / 'audit.json'), '--output=/report/' + storage + '-raw'], check=False)
    b.check(storage + ':unconfined_php_refused', (raw.returncode, raw.stdout, raw.stderr)
            == (1, '', 'A25_CONFINEMENT_REQUIRED\n'))
    for directory in (False, True):
        link = site / ('A25_SITE_PERSON_PRIVATE_CANARY_' + str(directory))
        link.symlink_to(site / 'wp-content' if directory else site / 'wp-config.php', target_is_directory=directory)
        try:
            out = OUT / (storage + '-symlink-' + str(directory))
            q = inventory(site, out, audit / 'audit.json')
            b.check(storage + ':symlink_closed:' + str(directory), (q.returncode, q.stdout, q.stderr)
                    == (1, '', 'A11_SYMLINK_UNSUPPORTED\n') and not out.exists())
        finally:
            link.unlink()
    for i, name in enumerate(('wp-content/db.php', 'wp-content/object-cache.php', 'wp-content/advanced-cache.php',
                              'wp-content/sunrise.php', 'wordfence-waf.php', '.user.ini')):
        dropin = site / name
        dropin.write_text('<?php die("A25_DROPIN_PRIVATE_CANARY");', encoding='utf-8')
        try:
            out = OUT / (storage + '-dropin-' + str(i))
            q = inventory(site, out, audit / 'audit.json')
            want = 'A11_DROPIN_UNSUPPORTED ' + json.dumps({'file': name}, separators=(',', ':')) + '\n'
            b.check(storage + ':closed_dropin:' + str(i), (q.returncode, q.stdout, q.stderr)
                    == (1, '', want) and not out.exists())
        finally:
            dropin.unlink()
    for label, statement in [('define', "define('A25_CONFIG_PRIVATE_CANARY', 'A25_VALUE_PRIVATE_CANARY');"),
                             ('const', "const A25_CONFIG_PRIVATE_CANARY = 'A25_VALUE_PRIVATE_CANARY';")]:
        (site / 'wp-config.php').write_text(cfg + '\n' + statement + '\n', encoding='utf-8')
        try:
            out = OUT / (storage + '-config-' + label)
            q = inventory(site, out, audit / 'audit.json')
            b.check(storage + ':config_closed:' + label, (q.returncode, q.stdout, q.stderr)
                    == (1, '', 'A11_CONFIG_OVERRIDE_UNSUPPORTED\n') and not out.exists())
        finally:
            (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    (site / 'wp-config.php').write_text(cfg.replace("define('DB_USER', 'a02_" + storage + "')",
                                                  "define('DB_USER', 'root')"), encoding='utf-8')
    try:
        out = OUT / (storage + '-root-readonly')
        q = inventory(site, out, audit / 'audit.json')
        b.check(storage + ':transaction_readonly_even_root', q.returncode == 0
                and (out / 'visiteurs.json').read_bytes() == (dest / 'visiteurs.json').read_bytes()
                and before == b.fingerprint(db))
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    bad = OUT / (storage + '-bad-audit')
    bad.mkdir()
    try:
        for label, photo, want in [('schema', {'schema': 'A25_AUDIT_PRIVATE_CANARY'}, 'A25_AUDIT_GUARD'),
                                  ('storage', json.loads((audit / 'audit.json').read_text()), 'A25_AUDIT_STORAGE_MISMATCH')]:
            if label == 'storage':
                photo['sections']['commerce']['order_storage'] = 'hpos' if storage == 'classic' else 'classic'
            (bad / 'audit.json').write_text(json.dumps(photo), encoding='utf-8')
            out = OUT / (storage + '-bad-' + label)
            q = inventory(site, out, bad / 'audit.json')
            b.check(storage + ':audit_guard:' + label, (q.returncode, q.stdout, q.stderr)
                    == (1, '', want + '\n') and not out.exists())
    finally:
        (bad / 'audit.json').unlink()
        bad.rmdir()
    target = "foreach ($_SERVER['argv'] as $arg) { if (str_starts_with($arg, '--output=')) { $dir=substr($arg,9); } }"
    cases = [
        ('direct_stdout', "fwrite(STDOUT, 'A25_STDOUT_PRIVATE_CANARY');", 'A25_PROCESS_OUTPUT_INVALID', True),
        ('direct_stderr', "fwrite(STDERR, 'A25_STDERR_PRIVATE_CANARY');", 'A25_PROCESS_OUTPUT_INVALID', True),
        ('display_early_exit', "echo 'A25_EXIT_PRIVATE_CANARY'; exit(0);", 'A25_PROCESS_OUTPUT_INVALID', True),
        ('silent_early_exit', 'exit(0);', 'A25_PROCESS_OUTPUT_INVALID', False),
        ('shutdown_stdout', "register_shutdown_function(function () { fwrite(STDOUT, 'A25_SHUTDOWN_PRIVATE_CANARY'); });", 'A25_PROCESS_OUTPUT_INVALID', True),
        ('shutdown_stderr', "register_shutdown_function(function () { fwrite(STDERR, 'A25_SHUTDOWN_PRIVATE_CANARY'); });", 'A25_PROCESS_OUTPUT_INVALID', True),
        ('shutdown_display', "register_shutdown_function(function () { echo 'A25_SHUTDOWN_PRIVATE_CANARY'; });", 'A25_PROCESS_OUTPUT_INVALID', True),
        ('invalid_utf8', 'fwrite(STDERR, chr(255));', 'A25_PROCESS_OUTPUT_INVALID', False),
        ('oversize_output', "fwrite(STDOUT, str_repeat('A25_PRIVATE_CANARY', 8192));", 'A25_PROCESS_OUTPUT_INVALID', True),
        ('plugin_exception', "throw new RuntimeException('A25_PERSON_PATH_PRIVATE_CANARY');", 'A25_INVENTORY_FAILED', False),
        ('forged_success', 'fwrite(STDOUT, "A25_OK visiteurs.json visiteurs.md\\n"); exit(0);', 'A25_REPORT_INVALID', False),
        ('shutdown_invalid_json', "register_shutdown_function(function () { " + target + " file_put_contents($dir.'/visiteurs.json', '{'); });", 'A25_REPORT_INVALID', False),
        ('shutdown_extra_string', "register_shutdown_function(function () { " + target + " $p=$dir.'/visiteurs.json'; $d=json_decode(file_get_contents($p),true); $d['private']='A25_JSON_PRIVATE_CANARY'; file_put_contents($p,json_encode($d)); });", 'A25_REPORT_INVALID', False),
        ('shutdown_markdown', "register_shutdown_function(function () { " + target + " file_put_contents($dir.'/visiteurs.md', 'A25_MARKDOWN_PRIVATE_CANARY', FILE_APPEND); });", 'A25_REPORT_INVALID', False),
        ('shutdown_extra_file', "register_shutdown_function(function () { " + target + " file_put_contents($dir.'/extra.txt', 'A25_EXTRA_PRIVATE_CANARY'); });", 'A25_REPORT_INVALID', False),
        ('shutdown_partial', "register_shutdown_function(function () { " + target + " unlink($dir.'/visiteurs.md'); });", 'A25_REPORT_INVALID', False),
    ]
    # Mutation witness: same PHP, arguments and Landlock; deliberately omit the
    # shared guardian. Raw streams are observed only in RAM, never persisted.
    fence_spec = importlib.util.spec_from_file_location('fence', '/subject/a12/confine.py')
    fence = importlib.util.module_from_spec(fence_spec)
    fence_spec.loader.exec_module(fence)
    try:
        for label, statement, want, witness in cases:
            mu.write_text("<?php if (getenv('A25_CONFINED') === '1') { " + statement + ' }\n' + base_mu[5:], encoding='utf-8')
            out = OUT / (storage + '-' + label)
            q = inventory(site, out, audit / 'audit.json')
            b.check(storage + ':closed_channel:' + label, (q.returncode, q.stdout, q.stderr)
                    == (1, '', want + '\n') and not out.exists())
            b.check(storage + ':no_retained_payload:' + label, not list(OUT.glob('.a25-private-*'))
                    and not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
            if witness:
                with tempfile.TemporaryDirectory(prefix='a25-mutation-', dir='/scratch') as tmp:
                    stage = Path(tmp)
                    (stage / 'audit').mkdir()
                    shutil.copyfile(audit / 'audit.json', stage / 'audit/audit.json')
                    command = ['php', '-d', 'display_errors=0', '-d', 'log_errors=0', '-d',
                               'disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',
                               '/subject/a25/inventorier-visiteurs', '--wp-path=' + str(site),
                               '--audit=' + str(stage / 'audit/audit.json'), '--output=' + str(stage / 'out')]
                    mutant = subprocess.run(command, capture_output=True, timeout=120,
                                            env={**os.environ, 'A25_CONFINED': '1', 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'},
                                            preexec_fn=lambda: fence.confine(stage))
                    b.check(storage + ':mutation_without_guard_detected:' + label, b'CANARY' in mutant.stdout + mutant.stderr)
    finally:
        mu.write_text(base_mu, encoding='utf-8')
    after = b.fingerprint(db)
    (OUT / (storage + '-db-after.json')).write_text(json.dumps(after), encoding='utf-8')
    b.check(storage + ':all_tables_and_scheduler_identical', before == after)
    final_files = b.files(site)
    (OUT / (storage + '-files.json')).write_text(json.dumps({'before': files, 'after': final_files}), encoding='utf-8')
    b.check(storage + ':site_files_identical', files == final_files)
    b.check(storage + ':config_never_executed', not Path('/scratch/a02-bootstrap-trap').exists())
    # A cloned fictitious DB crosses the unchanged import engine, not just a marker toggle.
    clone = 'a25_' + storage + '_test'
    b.sql('mysql', 'CREATE DATABASE ' + clone)
    dump = cmd(['mariadb-dump', '--socket=' + b.SOCKET, '-uroot', db]).stdout
    cmd(['mariadb', '--socket=' + b.SOCKET, '-uroot', clone], data=dump)
    red_before = b.fingerprint(clone)
    red_keep = cmd(['php', '/opt/a25/neutralise-keep-red.php'], check=False, env={'A25_DB': clone})
    b.check(storage + ':actual_old_keep_refused_red',
            (red_keep.returncode, red_keep.stdout, red_keep.stderr) == (1, 'A25_OLD_KEEP_REFUSED\n', ''))
    b.check(storage + ':old_keep_refusal_database_unchanged', red_before == b.fingerprint(clone))
    (OUT / (storage + '-old-keep-red.json')).write_text(json.dumps({
        'scope': 'disposable_old_keep_request_against_current_import', 'exit_code': red_keep.returncode,
        'closed_refusal': red_keep.stdout == 'A25_OLD_KEEP_REFUSED\n' and not red_keep.stderr,
        'database_unchanged': red_before == b.fingerprint(clone)}), encoding='utf-8')
    phase = cmd(['php', '/opt/a25/neutralise.php'], env={'A25_DB': clone})
    provenance = json.loads(phase.stdout)
    (OUT / (storage + '-neutralisation.json')).write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    b.check(storage + ':actual_import_comments_anonymised',
            provenance['neutraliser_and_anonymiser_executed'] is True and provenance['marker_count'] == 1
            and provenance['comments_before'] == provenance['comments_after'] == 3
            and provenance['emails_before'] == 2 and provenance['emails_after'] == 3
            and provenance['ip_before'] == 2 and provenance['ip_after'] == 0
            and provenance['guest_orders_preserved'])
    b.check(storage + ':actual_import_known_forms_purged',
            provenance['known_messages_before'] == 2 and provenance['known_messages_after'] == 0)
    b.check(storage + ':actual_import_unknown_forms_kept_separately',
            provenance['unknown_messages_before'] == 2 and provenance['unknown_message_preserved']
            and provenance['submission_pk_messages_preserved'] and provenance['submission_child_rows_preserved']
            and provenance['guest_orders_preserved'])
    b.sql('mysql', "GRANT SELECT ON " + clone + ".* TO 'a02_" + storage + "'@'localhost'")
    (site / 'wp-config.php').write_text(cfg.replace("define('DB_NAME', '" + db + "')",
                                                  "define('DB_NAME', '" + clone + "')"), encoding='utf-8')
    try:
        clone_before, clone_files = b.fingerprint(clone), b.files(site)
        neutral_audit = OUT / (storage + '-neutralised-audit')
        b.check(storage + ':neutralised_audit', b.audit(site, neutral_audit).returncode == 0)
        neutral = OUT / (storage + '-neutralised')
        q = inventory(site, neutral, neutral_audit / 'audit.json')
        b.check(storage + ':neutralised_success', q.returncode == 0 and q.stderr == '',
                {'exit': q.returncode, 'code': q.stderr.strip() if re.fullmatch(r'A(?:25|11|12|02)_[A-Z_]+\n', q.stderr) else 'NON_CODE'})
        n = json.loads((neutral / 'visiteurs.json').read_text(encoding='utf-8'))
        b.check(storage + ':neutral_unknown_never_zero', n['neutralisation'] == 'inconnu après neutralisation'
                and n['counts']['comments']['email'] == 'inconnu après neutralisation'
                and n['counts']['comments']['ip'] == 'inconnu après neutralisation'
                and n['counts']['forms'] == 'inconnu après neutralisation')
        b.check(storage + ':unchanged_native_counts_after_import', n['counts']['comments']['all'] == expected['comments']['all']
                and n['counts']['comments']['account'] == expected['comments']['account']
                and n['counts']['guests'] == expected['guests'])
        clone_after = b.fingerprint(clone)
        for suffix, value in [('before', clone_before), ('after', clone_after)]:
            (OUT / (storage + '-neutralised-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
        b.check(storage + ':neutralised_all_tables_files_identical', clone_before == clone_after and clone_files == b.files(site))
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    # A second native variant proves disclosure at exactly five and the UTC boundary.
    writable = cfg.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')").split(
        "\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site / 'wp-config.php').write_text(writable, encoding='utf-8')
    try:
        b.check(storage + ':five_native_seed', 'A25_FIVE_OK' in b.wp(site, ['eval-file', '/opt/a25/seed-five.php', '--use-include']).stdout)
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    five_before, five_files = b.fingerprint(db), b.files(site)
    five_audit = OUT / (storage + '-five-audit')
    b.check(storage + ':five_audit', b.audit(site, five_audit).returncode == 0)
    five_out = OUT / (storage + '-five')
    q = inventory(site, five_out, five_audit / 'audit.json')
    b.check(storage + ':five_confined_success', q.returncode == 0 and q.stderr == '')
    five = json.loads((five_out / 'visiteurs.json').read_text(encoding='utf-8'))
    b.check(storage + ':five_native_year_state_utc', five['counts']['comments']['all'] == {
        'groups': [{'year': 1999, 'state': '1', 'count': 5}], 'autres': 3})
    b.check(storage + ':five_native_form_year', five['counts']['forms'] == {
        'groups': [{'year': 1999, 'state': 'Fluent Forms', 'count': 5},
                   {'year': 2022, 'state': 'autre', 'count': 5}], 'autres': 4})
    b.check(storage + ':five_native_guests_year', five['counts']['guests'] == {
        'groups': [{'year': 1999, 'state': 'guest', 'count': 5}], 'autres': 2})
    five_after = b.fingerprint(db)
    for suffix, value in [('before', five_before), ('after', five_after)]:
        (OUT / (storage + '-five-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
    b.check(storage + ':five_tables_files_identical', five_before == five_after and five_files == b.files(site))
    # No known extension store: this is a legitimate observed result, not a refusal.
    b.sql(db, 'DROP TABLE wp_fluentform_submissions')
    absent_before, absent_files = b.fingerprint(db), b.files(site)
    absent_audit = OUT / (storage + '-absent-audit')
    b.check(storage + ':absent_audit', b.audit(site, absent_audit).returncode == 0)
    absent_out = OUT / (storage + '-absent')
    q = inventory(site, absent_out, absent_audit / 'audit.json')
    b.check(storage + ':absent_confined_success', q.returncode == 0 and q.stderr == '')
    absent = json.loads((absent_out / 'visiteurs.json').read_text(encoding='utf-8'))
    b.check(storage + ':absent_known_extension_explicit', absent['forms']['listed_extensions'] == []
            and absent['forms']['other_tables'] == 2 and absent['counts']['forms'] == {
                'groups': [{'year': 2022, 'state': 'autre', 'count': 5}], 'autres': 2})
    absent_after = b.fingerprint(db)
    for suffix, value in [('before', absent_before), ('after', absent_after)]:
        (OUT / (storage + '-absent-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
    b.check(storage + ':absent_tables_files_identical', absent_before == absent_after and absent_files == b.files(site))
    b.sql(db, 'CREATE TABLE wp_a25_nodate_entries (id int PRIMARY KEY,form_id int,fields longtext) ENGINE=InnoDB')
    b.sql(db, "INSERT INTO wp_a25_nodate_entries VALUES (1,1,'opaque'),(2,1,'opaque'),(3,1,'opaque'),(4,1,'opaque'),(5,1,'opaque')")
    nodate_before, nodate_files = b.fingerprint(db), b.files(site)
    nodate_audit = OUT / (storage + '-nodate-audit')
    b.check(storage + ':nodate_audit', b.audit(site, nodate_audit).returncode == 0)
    nodate_out = OUT / (storage + '-nodate')
    q = inventory(site, nodate_out, nodate_audit / 'audit.json')
    b.check(storage + ':nodate_confined_success', q.returncode == 0 and q.stderr == '')
    nodate = json.loads((nodate_out / 'visiteurs.json').read_text(encoding='utf-8'))
    b.check(storage + ':nodate_closed_zero_not_invented_year', nodate['counts']['forms'] == {
        'groups': [{'year': 0, 'state': 'autre', 'count': 5},
                   {'year': 2022, 'state': 'autre', 'count': 5}], 'autres': 2})
    nodate_after = b.fingerprint(db)
    for suffix, value in [('before', nodate_before), ('after', nodate_after)]:
        (OUT / (storage + '-nodate-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
    b.check(storage + ':nodate_tables_files_identical', nodate_before == nodate_after and nodate_files == b.files(site))
    # Isolate the counterexample: only the submission-PK parent and its ten detail rows remain.
    b.sql(db, 'DROP TABLE wp_a25_unknown_entries, wp_a25_nodate_entries')
    pk_before, pk_files = b.fingerprint(db), b.files(site)
    pk_audit = OUT / (storage + '-pk-only-audit')
    b.check(storage + ':pk_only_audit', b.audit(site, pk_audit).returncode == 0)
    pk_out = OUT / (storage + '-pk-only')
    q = inventory(site, pk_out, pk_audit / 'audit.json')
    b.check(storage + ':pk_only_confined_success', q.returncode == 0 and q.stderr == '')
    pk = json.loads((pk_out / 'visiteurs.json').read_text(encoding='utf-8'))
    b.check(storage + ':pk_only_no_silent_zero_or_child_double_count', pk['forms']['listed_extensions'] == []
            and pk['forms']['other_tables'] == 1 and pk['forms']['coverage'] == 'heuristique bornée'
            and pk['counts']['forms'] == {'groups': [{'year': 2022, 'state': 'autre', 'count': 5}], 'autres': 0})
    pk_after = b.fingerprint(db)
    for suffix, value in [('before', pk_before), ('after', pk_after)]:
        (OUT / (storage + '-pk-only-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
    b.check(storage + ':pk_only_tables_files_identical', pk_before == pk_after and pk_files == b.files(site))
    # Missing primary role: presence is known, a complete numeric message total is not.
    b.sql(db, 'CREATE TABLE wp_a25_ambiguous_entries (submission_id bigint,form_id int,response longtext,created_at datetime) ENGINE=InnoDB')
    b.sql(db, "INSERT INTO wp_a25_ambiguous_entries VALUES (1,1,'A25_AMBIGUOUS_PRIVATE_CANARY','2021-01-01'),"
          "(2,1,'opaque','2021-01-01'),(3,1,'opaque','2021-01-01'),(4,1,'opaque','2021-01-01'),(5,1,'opaque','2021-01-01')")
    ambiguous_before, ambiguous_files = b.fingerprint(db), b.files(site)
    ambiguous_audit = OUT / (storage + '-ambiguous-audit')
    b.check(storage + ':ambiguous_audit', b.audit(site, ambiguous_audit).returncode == 0)
    ambiguous_out = OUT / (storage + '-ambiguous')
    q = inventory(site, ambiguous_out, ambiguous_audit / 'audit.json')
    b.check(storage + ':ambiguous_confined_success', q.returncode == 0 and q.stderr == '')
    ambiguous = json.loads((ambiguous_out / 'visiteurs.json').read_text(encoding='utf-8'))
    b.check(storage + ':ambiguous_coverage_never_zero', ambiguous['forms']['coverage'] == 'couverture indéterminée'
            and ambiguous['counts']['forms'] == 'couverture indéterminée' and ambiguous['forms']['other_tables'] == 1)
    ambiguous_after = b.fingerprint(db)
    for suffix, value in [('before', ambiguous_before), ('after', ambiguous_after)]:
        (OUT / (storage + '-ambiguous-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
    b.check(storage + ':ambiguous_tables_files_identical', ambiguous_before == ambiguous_after
            and ambiguous_files == b.files(site))
    b.check(storage + ':all_output_artifacts_clean', not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))


b.run_storage = run_storage
if __name__ == '__main__':
    sys.exit(b.main())
