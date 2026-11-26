"""Native synthetic A26 bank. Only the parent runs this inside its isolated runner."""
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
spec = importlib.util.spec_from_file_location('fixture', '/opt/a02/inside.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OUT = Path('/report')
UNKNOWN = 'inconnu après neutralisation'


def cmd(args, check=True, env=None, data=None, timeout=240):
    p = subprocess.run(args, input=data, capture_output=True, text=True, encoding='utf-8', errors='strict',
                       timeout=timeout, env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                                             'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})
    if check and p.returncode:
        raise RuntimeError('A26_FIXTURE_COMMAND_FAILED')
    return p


b.cmd = cmd
original_check = b.check


def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {k: detail[k] for k in ['versions', 'hpos', 'subscriptions', 'rules', 'restriction_real']}
    return original_check(name, ok, detail)


b.check = check


def inventory(site, out, audit, *extra):
    return cmd(['python3', '/subject/a26/confine.py', '--wp-path=' + str(site),
                '--audit=' + str(audit), '--output=' + str(out), *extra], check=False)


def exact_counts(**overrides):
    keys = ('youtube', 'vimeo', 'dailymotion', 'soundcloud', 'spotify', 'mixcloud', 'google_maps',
            'openstreetmap', 'facebook', 'instagram', 'twitter', 'tiktok', 'autre')
    return {key: overrides.get(key, 0) for key in keys}


def report_bytes(folder):
    return {f.name: f.read_bytes() for f in folder.iterdir()}


def run_storage(storage):
    site, db, _ = b.install(storage)
    (OUT / (storage + '-seed.json')).unlink()
    cfg = (site / 'wp-config.php').read_text(encoding='utf-8')
    writable = cfg.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')").split(
        "\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site / 'wp-config.php').write_text(writable, encoding='utf-8')
    try:
        p = b.wp(site, ['eval-file', '/opt/a26/seed.php', '--use-include'])
        b.check(storage + ':native_seed', 'A26_SEED_OK' in p.stdout)
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    mu = site / 'wp-content/mu-plugins/a26-probe.php'
    base_mu = '''<?php
if (getenv('A26_CONFINED') === '1') {
    global $wpdb;
    require_once ABSPATH.'wp-includes/pluggable.php';
    add_action('plugins_loaded', static function () {
        if (as_enqueue_async_action('a26_forbidden') !== 0
            || as_schedule_single_action(time()+9999, 'a26_forbidden') !== 0
            || as_schedule_recurring_action(time()+9999, 3600, 'a26_forbidden') !== 0
            || as_schedule_cron_action(time()+9999, '* * * * *', 'a26_forbidden') !== 0) {
            throw new RuntimeException('A26_AS_PRIVATE_CANARY');
        }
    }, PHP_INT_MAX);
    if ($wpdb->query('UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @mysqli_query($wpdb->dbh, 'UPDATE wp_users SET ID=ID WHERE 1=0') !== false
        || @file_put_contents(ABSPATH.'forbidden', 'NO') !== false
        || @file_put_contents('/report/forbidden', 'NO') !== false
        || wp_mail('fictif@example.org', 'A26_MAIL_PRIVATE_CANARY', 'A26_MAIL_PRIVATE_CANARY') !== false
        || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
        || wp_schedule_single_event(time()+9999, 'a26_forbidden') !== false
        || function_exists('mail') || function_exists('exec')) {
        throw new RuntimeException('A26_EARLY_GUARD_PRIVATE_CANARY');
    }
    add_shortcode('embed', static function () { throw new RuntimeException('A26_RENDER_PRIVATE_CANARY'); });
    add_filter('render_block', static function () { throw new RuntimeException('A26_RENDER_PRIVATE_CANARY'); });
    echo 'A26_DISPLAY_PRIVATE_CANARY';
}
'''
    mu.write_text(base_mu, encoding='utf-8')
    audit = OUT / (storage + '-audit')
    b.check(storage + ':audit_success', b.audit(site, audit).returncode == 0)
    before, files = b.fingerprint(db), b.files(site)
    (OUT / (storage + '-db-before.json')).write_text(json.dumps(before), encoding='utf-8')
    dest = OUT / (storage + '-tiers')
    p = inventory(site, dest, audit / 'audit.json')
    b.check(storage + ':confined_success', (p.returncode, p.stdout, p.stderr) == (0, 'A26_OK tiers.json tiers.md\n', ''))
    d = json.loads((dest / 'tiers.json').read_text(encoding='utf-8'))
    b.check(storage + ':one_active_each_family', len(d['families']) == 10 and all(row['active'] == 1 for row in d['families'].values()))
    b.check(storage + ':qualified_identifier_yes_others_unreadable', d['families']['mesure']['identifier'] == 'oui'
            and all(row['identifier'] == 'illisible' for key, row in d['families'].items() if key != 'mesure'))
    b.check(storage + ':exact_content_per_service_once', d['content']['all'] == exact_counts(youtube=3, vimeo=1, spotify=1, autre=1))
    years = {row['year']: row['counts'] for row in d['content']['selection']['years']}
    b.check(storage + ':annual_fallback_utc', d['content']['selection']['mode'] == 'annee'
            and years[2024] == exact_counts(youtube=1) and years[2026] == exact_counts(youtube=1, autre=1)
            and years[2023] == exact_counts(vimeo=1, spotify=1) and years[2022] == exact_counts(youtube=1))
    payload = p.stdout + p.stderr + ''.join(f.read_text(encoding='utf-8') for f in dest.iterdir())
    b.check(storage + ':all_private_values_absent_all_report_files', not re.search(r'CANARY|@|/scratch|\.invalid|a02-admin', payload))
    b.check(storage + ':report_permissions', dest.stat().st_mode & 0o777 == 0o700
            and all(f.stat().st_mode & 0o777 == 0o600 for f in dest.iterdir()))
    repeat = OUT / (storage + '-repeat')
    q = inventory(site, repeat, audit / 'audit.json')
    b.check(storage + ':replay_identical', q.returncode == 0 and report_bytes(dest) == report_bytes(repeat))
    line = next(x for x in Path('/subject/a26/README.md').read_text(encoding='utf-8').splitlines()
                if x.startswith('python3 wp/outils/bascule/a26/confine.py '))
    documented = OUT / (storage + '-documented')
    replacements = {'wp/outils/bascule/a26/confine.py': '/subject/a26/confine.py',
                    '--wp-path=/copie-verifiee': '--wp-path=' + str(site),
                    '--audit=/hors-web/audit-date/audit.json': '--audit=' + str(audit / 'audit.json'),
                    '--output=/hors-web/tiers-date': '--output=' + str(documented)}
    command = [replacements.get(x, x) for x in shlex.split(line)]
    q = cmd(command, check=False)
    b.check(storage + ':documented_command_only_given_arguments', len(command) == 5 and q.returncode == 0
            and q.stdout == 'A26_OK tiers.json tiers.md\n' and q.stderr == '' and report_bytes(documented) == report_bytes(dest))
    mapping = {'version': 1, 'numero_type': 'imagine_numero', 'article_type': 'post',
               'date_cle': 'post_date_gmt', 'pdf_cle': 'imagine_pdf', 'thematique': 'category',
               'liaison': {'source': 'postmeta', 'cle': 'imagine_numero_id'}}
    for mode in ('postmeta', 'post_parent', 'taxonomy'):
        current = dict(mapping)
        current['liaison'] = {'source': mode, 'cle': 'imagine_numero_id'}
        if mode == 'taxonomy':
            current.update(numero_source='taxonomy', numero_type='a26_issue', date_cle='a26_date')
            current['liaison']['cle'] = 'a26_issue'
        path = OUT / (storage + '-mapping-' + mode + '.json')
        path.write_text(json.dumps(current), encoding='utf-8')
        out = OUT / (storage + '-last-ten-' + mode)
        q = inventory(site, out, audit / 'audit.json', '--a16-map=' + str(path))
        b.check(storage + ':a16_mapping_success:' + mode, q.returncode == 0 and q.stderr == '')
        last = json.loads((out / 'tiers.json').read_text(encoding='utf-8'))
        b.check(storage + ':last_ten_exact_no_oldest_no_orphans:' + mode,
                last['content']['selection'] == {'mode': 'dix_derniers', 'years': [],
                                                'last_ten': exact_counts(youtube=1, autre=1)}
                and last['content']['all'] == d['content']['all'])
    for label, path in [('exists', dest), ('site', site / 'forbidden'), ('repo', Path('/subject/forbidden')),
                        ('ancestor', site.parent / 'forbidden'), ('root', Path('/forbidden'))]:
        q = inventory(site, path, audit / 'audit.json')
        b.check(storage + ':guard:' + label, q.returncode == 1 and q.stdout == ''
                and re.fullmatch(r'A(?:26|12)_[A-Z_]+\n', q.stderr) is not None
                and (path == dest or not path.exists()))
    raw = cmd(['php', '/subject/a26/inventorier-tiers', '--wp-path=' + str(site),
               '--audit=' + str(audit / 'audit.json'), '--output=/report/' + storage + '-raw'], check=False)
    b.check(storage + ':unconfined_php_refused', (raw.returncode, raw.stdout, raw.stderr) == (1, '', 'A26_CONFINEMENT_REQUIRED\n'))
    for directory in (False, True):
        link = site / ('A26_SITE_PRIVATE_CANARY_' + str(directory))
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
        dropin.write_text('<?php die("A26_DROPIN_PRIVATE_CANARY");', encoding='utf-8')
        try:
            out = OUT / (storage + '-dropin-' + str(i))
            q = inventory(site, out, audit / 'audit.json')
            want = 'A11_DROPIN_UNSUPPORTED ' + json.dumps({'file': name}, separators=(',', ':')) + '\n'
            b.check(storage + ':closed_dropin:' + str(i), (q.returncode, q.stdout, q.stderr)
                    == (1, '', want) and not out.exists())
        finally:
            dropin.unlink()
    for label, statement in [('define', "define('A26_CONFIG_PRIVATE_CANARY', 'A26_VALUE_PRIVATE_CANARY');"),
                             ('const', "const A26_CONFIG_PRIVATE_CANARY = 'A26_VALUE_PRIVATE_CANARY';")]:
        (site / 'wp-config.php').write_text(cfg + '\n' + statement + '\n', encoding='utf-8')
        try:
            out = OUT / (storage + '-config-' + label)
            q = inventory(site, out, audit / 'audit.json')
            b.check(storage + ':config_closed:' + label, (q.returncode, q.stdout, q.stderr)
                    == (1, '', 'A11_CONFIG_OVERRIDE_UNSUPPORTED\n') and not out.exists())
        finally:
            (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    target = "foreach ($_SERVER['argv'] as $arg) { if (str_starts_with($arg, '--output=')) { $dir=substr($arg,9); } }"
    coherent = "$p=$dir.'/tiers.json'; $d=json_decode(file_get_contents($p),true); $d['families']['mesure']['active']=2; $j=json_encode($d,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES).\"\\n\"; file_put_contents($p,$j); $m=file_get_contents($dir.'/tiers.md'); $pos=strpos($m,'```json'); file_put_contents($dir.'/tiers.md',substr($m,0,$pos).'```json'.\"\\n\".$j.\"```\\n\");"
    cases = [
        ('direct_stdout', "fwrite(STDOUT, 'A26_STDOUT_PRIVATE_CANARY');", 'A26_PROCESS_OUTPUT_INVALID', True),
        ('direct_stderr', "fwrite(STDERR, 'A26_STDERR_PRIVATE_CANARY');", 'A26_PROCESS_OUTPUT_INVALID', True),
        ('display_early_exit', "echo 'A26_EXIT_PRIVATE_CANARY'; exit(0);", 'A26_PROCESS_OUTPUT_INVALID', True),
        ('silent_early_exit', 'exit(0);', 'A26_PROCESS_OUTPUT_INVALID', False),
        ('shutdown_stdout', "register_shutdown_function(function () { fwrite(STDOUT, 'A26_SHUTDOWN_PRIVATE_CANARY'); });", 'A26_PROCESS_OUTPUT_INVALID', True),
        ('shutdown_stderr', "register_shutdown_function(function () { fwrite(STDERR, 'A26_SHUTDOWN_PRIVATE_CANARY'); });", 'A26_PROCESS_OUTPUT_INVALID', True),
        ('shutdown_display', "register_shutdown_function(function () { echo 'A26_SHUTDOWN_PRIVATE_CANARY'; });", 'A26_PROCESS_OUTPUT_INVALID', True),
        ('invalid_utf8', 'fwrite(STDERR, chr(255));', 'A26_PROCESS_OUTPUT_INVALID', False),
        ('oversize_output', "fwrite(STDOUT, str_repeat('A26_PRIVATE_CANARY', 8192));", 'A26_PROCESS_OUTPUT_INVALID', True),
        ('plugin_exception', "throw new RuntimeException('A26_PERSON_PATH_PRIVATE_CANARY');", 'A26_INVENTORY_FAILED', False),
        ('forged_prefix_exception', "throw new RuntimeException('A26_QUERY_FAILED A26_PERSON_PATH_PRIVATE_CANARY');", 'A26_INVENTORY_FAILED', False),
        ('forged_success', 'fwrite(STDOUT, "A26_OK tiers.json tiers.md\\n"); exit(0);', 'A26_PROCESS_OUTPUT_INVALID', False),
        ('shutdown_invalid_json', "register_shutdown_function(function () { " + target + " file_put_contents($dir.'/tiers.json', '{'); });", 'A26_REPORT_INVALID', False),
        ('shutdown_extra_string', "register_shutdown_function(function () { " + target + " $p=$dir.'/tiers.json'; $d=json_decode(file_get_contents($p),true); $d['private']='A26_JSON_PRIVATE_CANARY'; file_put_contents($p,json_encode($d)); });", 'A26_REPORT_INVALID', False),
        ('shutdown_markdown', "register_shutdown_function(function () { " + target + " file_put_contents($dir.'/tiers.md', 'A26_MARKDOWN_PRIVATE_CANARY', FILE_APPEND); });", 'A26_REPORT_INVALID', False),
        ('shutdown_extra_file', "register_shutdown_function(function () { " + target + " file_put_contents($dir.'/extra.txt', 'A26_EXTRA_PRIVATE_CANARY'); });", 'A26_REPORT_INVALID', False),
        ('shutdown_partial', "register_shutdown_function(function () { " + target + " unlink($dir.'/tiers.md'); });", 'A26_REPORT_INVALID', False),
        ('shutdown_valid_counts_and_markdown', "register_shutdown_function(function () { " + target + coherent + " });", 'A26_REPORT_INVALID', False),
    ]
    fence_spec = importlib.util.spec_from_file_location('fence', '/subject/a12/confine.py')
    fence = importlib.util.module_from_spec(fence_spec)
    fence_spec.loader.exec_module(fence)
    try:
        for label, statement, want, witness in cases:
            mu.write_text("<?php if (getenv('A26_CONFINED') === '1') { " + statement + ' }\n' + base_mu[5:], encoding='utf-8')
            out = OUT / (storage + '-' + label)
            q = inventory(site, out, audit / 'audit.json')
            b.check(storage + ':closed_channel:' + label, (q.returncode, q.stdout, q.stderr) == (1, '', want + '\n') and not out.exists())
            b.check(storage + ':no_retained_payload:' + label, not list(OUT.glob('.a26-private-*'))
                    and not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
            if witness:
                with tempfile.TemporaryDirectory(prefix='a26-mutation-', dir='/scratch') as tmp:
                    stage = Path(tmp)
                    (stage / 'audit').mkdir()
                    shutil.copyfile(audit / 'audit.json', stage / 'audit/audit.json')
                    command = ['php', '-d', 'display_errors=0', '-d', 'log_errors=0', '-d', 'error_log=/dev/null', '-d',
                               'disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',
                               '/subject/a26/inventorier-tiers', '--wp-path=' + str(site),
                               '--audit=' + str(stage / 'audit/audit.json'), '--output=' + str(stage / 'out')]
                    mutant = subprocess.run(command, capture_output=True, timeout=120,
                                            env={**os.environ, 'A26_CONFINED': '1'}, preexec_fn=lambda: fence.confine(stage))
                    b.check(storage + ':mutation_without_guard_detected:' + label, b'CANARY' in mutant.stdout + mutant.stderr)
            if label in ('shutdown_markdown', 'shutdown_extra_string', 'shutdown_valid_counts_and_markdown'):
                launcher = Path('/subject/a26/confine.py')
                saved = launcher.read_bytes()
                gate = 'if not report.final_binding(stdout, staged_output) or not report.complete_report(staged_output, audit):'
                assert gate in saved.decode('utf-8')
                try:
                    launcher.write_text(saved.decode('utf-8').replace(gate, 'if False:'), encoding='utf-8')
                    with tempfile.TemporaryDirectory(prefix='a26-file-witness-', dir='/scratch') as tmp:
                        witness_parent = Path(tmp)
                        (witness_parent / 'audit').mkdir()
                        shutil.copyfile(audit / 'audit.json', witness_parent / 'audit/audit.json')
                        leaked = witness_parent / 'out'
                        z = inventory(site, leaked, witness_parent / 'audit/audit.json')
                        contaminated = (any(b'CANARY' in f.read_bytes() for f in leaked.iterdir())
                                        if label != 'shutdown_valid_counts_and_markdown'
                                        else json.loads((leaked / 'tiers.json').read_text())['families']['mesure']['active'] == 2)
                        b.check(storage + ':mutation_without_file_gate_detected:' + label, z.returncode == 0 and contaminated)
                finally:
                    launcher.write_bytes(saved)
    finally:
        mu.write_text(base_mu, encoding='utf-8')
    after = b.fingerprint(db)
    (OUT / (storage + '-db-after.json')).write_text(json.dumps(after), encoding='utf-8')
    (OUT / (storage + '-files.json')).write_text(json.dumps({'before': files, 'after': b.files(site)}), encoding='utf-8')
    b.check(storage + ':all_tables_and_scheduler_identical', before == after)
    b.check(storage + ':site_files_identical', files == b.files(site))
    b.check(storage + ':config_never_executed', not Path('/scratch/a02-bootstrap-trap').exists())
    clone = 'a26_' + storage + '_test'
    b.sql('mysql', 'CREATE DATABASE ' + clone)
    dump = cmd(['mariadb-dump', '--socket=' + b.SOCKET, '-uroot', db]).stdout
    cmd(['mariadb', '--socket=' + b.SOCKET, '-uroot', clone], data=dump)
    phase = cmd(['php', '/opt/a26/neutralise.php'], env={'A26_DB': clone})
    provenance = json.loads(phase.stdout)
    (OUT / (storage + '-neutralisation.json')).write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    b.check(storage + ':actual_unchanged_import_executed', provenance['neutraliser_and_anonymiser_executed']
            and provenance['marker_present'] and provenance['analytics_removed'] and provenance['pixel_removed']
            and provenance['measurement_declaration_retained'] and provenance['sensitive_setting_erased']
            and provenance['published_contents_erased'] >= 1)
    b.sql('mysql', "GRANT SELECT ON " + clone + ".* TO 'a02_" + storage + "'@'localhost'")
    (site / 'wp-config.php').write_text(cfg.replace("define('DB_NAME', '" + db + "')", "define('DB_NAME', '" + clone + "')"), encoding='utf-8')
    try:
        clone_before, clone_files = b.fingerprint(clone), b.files(site)
        neutral_audit = OUT / (storage + '-neutralised-audit')
        b.check(storage + ':neutralised_audit', b.audit(site, neutral_audit).returncode == 0)
        neutral = OUT / (storage + '-neutralised')
        q = inventory(site, neutral, neutral_audit / 'audit.json')
        b.check(storage + ':neutralised_success', q.returncode == 0 and q.stderr == '')
        n = json.loads((neutral / 'tiers.json').read_text(encoding='utf-8'))
        b.check(storage + ':neutral_unknown_never_zero', n['neutralisation'] == UNKNOWN and n['content'] == UNKNOWN
                and all(n['families'][k] == {'active': UNKNOWN, 'identifier': UNKNOWN} for k in ('mesure', 'pixel')))
        b.check(storage + ':unaffected_families_observed_counts_ids_unknown', all(
            row == {'active': 1, 'identifier': UNKNOWN} for key, row in n['families'].items() if key not in ('mesure', 'pixel')))
        clone_after = b.fingerprint(clone)
        for suffix, value in [('before', clone_before), ('after', clone_after)]:
            (OUT / (storage + '-neutralised-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
        (OUT / (storage + '-neutralised-files.json')).write_text(json.dumps({'before': clone_files, 'after': b.files(site)}), encoding='utf-8')
        b.check(storage + ':neutralised_all_tables_files_identical', clone_before == clone_after and clone_files == b.files(site))
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    b.check(storage + ':all_output_artifacts_clean', not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))


b.run_storage = run_storage
if __name__ == '__main__':
    sys.exit(b.main())
