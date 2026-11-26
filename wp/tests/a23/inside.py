"""Native synthetic A23 path; private canaries never enter receipts."""
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
    mu = site / 'wp-content/mu-plugins/a23-probe.php'
    base_mu = '''<?php
if (getenv('A23_CONFINED') === '1') {
    global $wpdb;
    require_once ABSPATH.'wp-includes/pluggable.php';
    add_filter('check_password', function () { throw new RuntimeException('A23_PASSWORD_TRIAL_PRIVATE_CANARY'); }, -999999);
    add_filter('authenticate', function () { throw new RuntimeException('A23_LOGIN_TRIAL_PRIVATE_CANARY'); }, -999999);
    if ($wpdb->query('UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @mysqli_query($wpdb->dbh, 'UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @file_put_contents(ABSPATH.'forbidden', 'NO') !== false
        || wp_mail('fictif@example.org', 'A23_MAIL_PRIVATE_CANARY', 'A23_MAIL_PRIVATE_CANARY') !== false
        || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
        || wp_schedule_single_event(time()+9999, 'a23_forbidden') !== false
        || function_exists('mail') || function_exists('exec')) {
        throw new RuntimeException('A23_EARLY_GUARD_PRIVATE_CANARY');
    }
    echo 'A23_DISPLAY_PRIVATE_CANARY';
}
'''
    mu.write_text(base_mu, encoding='utf-8')
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
    b.check(storage + ':private_report_permissions', dest.stat().st_mode & 0o777 == 0o700
            and all(f.stat().st_mode & 0o777 == 0o600 for f in dest.iterdir()))
    repeat = OUT / (storage + '-repeat')
    q = inventory(site, repeat, audit / 'audit.json')
    b.check(storage + ':replay_identical', q.returncode == 0 and
            {f.name: f.read_bytes() for f in dest.iterdir()} == {f.name: f.read_bytes() for f in repeat.iterdir()})
    line = next(x for x in Path('/subject/a23/README.md').read_text(encoding='utf-8').splitlines()
                if x.startswith('python3 wp/outils/bascule/a23/confine.py '))
    documented = OUT / (storage + '-documented')
    replacements = {'wp/outils/bascule/a23/confine.py': '/subject/a23/confine.py',
                    '--wp-path=/copie-verifiee': '--wp-path=' + str(site),
                    '--audit=/hors-web/audit-date/audit.json': '--audit=' + str(audit / 'audit.json'),
                    '--output=/hors-web/comptes-date': '--output=' + str(documented)}
    command = [replacements.get(x, x) for x in shlex.split(line)]
    q = cmd(command, check=False)
    b.check(storage + ':documented_only_given_arguments', len(command) == 5 and q.returncode == 0
            and q.stdout == 'A23_OK comptes.json comptes.md\n' and q.stderr == ''
            and (documented / 'comptes.json').read_bytes() == (dest / 'comptes.json').read_bytes())
    for label, path in [('exists', dest), ('site', site / 'forbidden'), ('repo', Path('/subject/forbidden')),
                        ('ancestor', site.parent / 'forbidden'), ('root', Path('/forbidden'))]:
        q = inventory(site, path, audit / 'audit.json')
        b.check(storage + ':guard:' + label, q.returncode == 1 and q.stdout == ''
                and re.fullmatch(r'A(?:23|12)_[A-Z_]+\n', q.stderr) is not None
                and (path == dest or not path.exists()))
    raw = cmd(['php', '/subject/a23/inventorier-comptes', '--wp-path=' + str(site),
               '--audit=' + str(audit / 'audit.json'), '--output=/report/' + storage + '-raw'], check=False)
    b.check(storage + ':unconfined_php_refused', (raw.returncode, raw.stdout, raw.stderr)
            == (1, '', 'A23_CONFINEMENT_REQUIRED\n'))
    for directory in (False, True):
        link = site / ('A23_SITE_PERSON_PRIVATE_CANARY_' + str(directory))
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
        dropin.write_text('<?php die("A23_DROPIN_PRIVATE_CANARY");', encoding='utf-8')
        try:
            out = OUT / (storage + '-dropin-' + str(i))
            q = inventory(site, out, audit / 'audit.json')
            want = 'A11_DROPIN_UNSUPPORTED ' + json.dumps({'file': name}, separators=(',', ':')) + '\n'
            b.check(storage + ':closed_dropin:' + str(i), (q.returncode, q.stdout, q.stderr)
                    == (1, '', want) and not out.exists())
        finally:
            dropin.unlink()
    for label, statement in [('define', "define('A23_CONFIG_PRIVATE_CANARY', 'A23_VALUE_PRIVATE_CANARY');"),
                             ('const', "const A23_CONFIG_PRIVATE_CANARY = 'A23_VALUE_PRIVATE_CANARY';")]:
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
                and (out / 'comptes.json').read_bytes() == (dest / 'comptes.json').read_bytes()
                and before == b.fingerprint(db))
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    bad = OUT / (storage + '-bad-audit')
    bad.mkdir()
    try:
        for label, photo, want in [('schema', {'schema': 'A23_AUDIT_PRIVATE_CANARY'}, 'A23_AUDIT_GUARD'),
                                  ('storage', json.loads((audit / 'audit.json').read_text()), 'A23_AUDIT_STORAGE_MISMATCH')]:
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
        ('direct_stdout', "fwrite(STDOUT, 'A23_STDOUT_PRIVATE_CANARY');", 'A23_PROCESS_OUTPUT_INVALID', True),
        ('direct_stderr', "fwrite(STDERR, 'A23_STDERR_PRIVATE_CANARY');", 'A23_PROCESS_OUTPUT_INVALID', True),
        ('display_early_exit', "echo 'A23_EXIT_PRIVATE_CANARY'; exit(0);", 'A23_PROCESS_OUTPUT_INVALID', True),
        ('silent_early_exit', 'exit(0);', 'A23_PROCESS_OUTPUT_INVALID', False),
        ('shutdown_stdout', "register_shutdown_function(function () { fwrite(STDOUT, 'A23_SHUTDOWN_PRIVATE_CANARY'); });", 'A23_PROCESS_OUTPUT_INVALID', True),
        ('shutdown_stderr', "register_shutdown_function(function () { fwrite(STDERR, 'A23_SHUTDOWN_PRIVATE_CANARY'); });", 'A23_PROCESS_OUTPUT_INVALID', False),
        ('shutdown_display', "register_shutdown_function(function () { echo 'A23_SHUTDOWN_PRIVATE_CANARY'; });", 'A23_PROCESS_OUTPUT_INVALID', False),
        ('invalid_utf8', 'fwrite(STDERR, chr(255));', 'A23_PROCESS_OUTPUT_INVALID', False),
        ('oversize_output', "fwrite(STDOUT, str_repeat('A23_PRIVATE_CANARY', 8192));", 'A23_PROCESS_OUTPUT_INVALID', False),
        ('plugin_exception', "throw new RuntimeException('A23_PERSON_PATH_PRIVATE_CANARY');", 'A23_INVENTORY_FAILED', False),
        ('forged_success', 'fwrite(STDOUT, "A23_OK comptes.json comptes.md\\n"); exit(0);', 'A23_REPORT_INVALID', False),
        ('shutdown_invalid_json', "register_shutdown_function(function () { " + target + " file_put_contents($dir.'/comptes.json', '{'); });", 'A23_REPORT_INVALID', False),
        ('shutdown_extra_string', "register_shutdown_function(function () { " + target + " $p=$dir.'/comptes.json'; $d=json_decode(file_get_contents($p),true); $d['private']='A23_JSON_PRIVATE_CANARY'; file_put_contents($p,json_encode($d)); });", 'A23_REPORT_INVALID', False),
        ('shutdown_markdown', "register_shutdown_function(function () { " + target + " file_put_contents($dir.'/comptes.md', 'A23_MARKDOWN_PRIVATE_CANARY', FILE_APPEND); });", 'A23_REPORT_INVALID', False),
        ('shutdown_extra_file', "register_shutdown_function(function () { " + target + " file_put_contents($dir.'/extra.txt', 'A23_EXTRA_PRIVATE_CANARY'); });", 'A23_REPORT_INVALID', False),
        ('shutdown_partial', "register_shutdown_function(function () { " + target + " unlink($dir.'/comptes.md'); });", 'A23_REPORT_INVALID', False),
    ]
    # Mutation witness: same PHP, arguments and Landlock; deliberately omit the
    # shared guardian. Raw streams are observed only in RAM, never persisted.
    fence_spec = importlib.util.spec_from_file_location('fence', '/subject/a12/confine.py')
    fence = importlib.util.module_from_spec(fence_spec)
    fence_spec.loader.exec_module(fence)
    try:
        for label, statement, want, witness in cases:
            mu.write_text("<?php if (getenv('A23_CONFINED') === '1') { " + statement + ' }\n' + base_mu[5:], encoding='utf-8')
            out = OUT / (storage + '-' + label)
            q = inventory(site, out, audit / 'audit.json')
            b.check(storage + ':closed_channel:' + label, (q.returncode, q.stdout, q.stderr)
                    == (1, '', want + '\n') and not out.exists())
            b.check(storage + ':no_retained_payload:' + label, not list(OUT.glob('.a23-private-*'))
                    and not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
            if witness:
                with tempfile.TemporaryDirectory(prefix='a23-mutation-', dir='/scratch') as tmp:
                    stage = Path(tmp)
                    (stage / 'audit').mkdir()
                    shutil.copyfile(audit / 'audit.json', stage / 'audit/audit.json')
                    command = ['php', '-d', 'display_errors=0', '-d', 'log_errors=0', '-d',
                               'disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',
                               '/subject/a23/inventorier-comptes', '--wp-path=' + str(site),
                               '--audit=' + str(stage / 'audit/audit.json'), '--output=' + str(stage / 'out')]
                    mutant = subprocess.run(command, capture_output=True, timeout=120,
                                            env={**os.environ, 'A23_CONFINED': '1', 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'},
                                            preexec_fn=lambda: fence.confine(stage))
                    b.check(storage + ':mutation_without_guard_detected:' + label, b'CANARY' in mutant.stdout + mutant.stderr)
    finally:
        mu.write_text(base_mu, encoding='utf-8')
    after = b.fingerprint(db)
    (OUT / (storage + '-db-after.json')).write_text(json.dumps(after), encoding='utf-8')
    b.check(storage + ':all_tables_and_scheduler_identical', before == after)
    b.check(storage + ':site_files_identical', files == b.files(site))
    b.check(storage + ':config_never_executed', not Path('/scratch/a02-bootstrap-trap').exists())
    # A cloned fictitious DB crosses the unchanged import engine, not just a marker toggle.
    clone = 'a23_' + storage + '_test'
    b.sql('mysql', 'CREATE DATABASE ' + clone)
    dump = cmd(['mariadb-dump', '--socket=' + b.SOCKET, '-uroot', db]).stdout
    cmd(['mariadb', '--socket=' + b.SOCKET, '-uroot', clone], data=dump)
    phase = cmd(['php', '/opt/a23/neutralise.php'], env={'A23_DB': clone})
    provenance = json.loads(phase.stdout)
    (OUT / (storage + '-neutralisation.json')).write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    b.check(storage + ':actual_import_replaces_three_fields', provenance['neutraliser_and_anonymiser_executed'] is True
            and provenance['marker_count'] == 1 and provenance['before_accounts'] >= 32
            and all(v == provenance['before_accounts'] for v in provenance['changed'].values()))
    b.sql('mysql', "GRANT SELECT ON " + clone + ".* TO 'a02_" + storage + "'@'localhost'")
    (site / 'wp-config.php').write_text(cfg.replace("define('DB_NAME', '" + db + "')",
                                                  "define('DB_NAME', '" + clone + "')"), encoding='utf-8')
    try:
        clone_before, clone_files = b.fingerprint(clone), b.files(site)
        neutral_audit = OUT / (storage + '-neutralised-audit')
        b.check(storage + ':neutralised_audit', b.audit(site, neutral_audit).returncode == 0)
        neutral = OUT / (storage + '-neutralised')
        q = inventory(site, neutral, neutral_audit / 'audit.json')
        b.check(storage + ':neutralised_success', q.returncode == 0 and q.stderr == '')
        n = json.loads((neutral / 'comptes.json').read_text(encoding='utf-8'))
        b.check(storage + ':six_unknown_blocks_never_zero', n['neutralisation'] == 'inconnu après neutralisation'
                and all(n['counts'][scope][key] == 'inconnu après neutralisation'
                        for scope in ('readers', 'live_readers') for key in ('families', 'emails', 'logins')))
        b.check(storage + ':useful_counts_preserved_after_import', n['counts']['readers']['accounts'] == 32
                and n['counts']['live_readers']['accounts'] == 20
                and n['counts']['without_commerce'] == expected['without_commerce'])
        clone_after = b.fingerprint(clone)
        for suffix, value in [('before', clone_before), ('after', clone_after)]:
            (OUT / (storage + '-neutralised-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
        b.check(storage + ':neutralised_all_tables_files_identical', clone_before == clone_after and clone_files == b.files(site))
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    b.check(storage + ':all_output_artifacts_clean', not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))


b.run_storage = run_storage
if __name__ == '__main__':
    sys.exit(b.main())
