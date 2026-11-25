"""Actual WordPress/Woo/Memberships/Subscriptions acceptance; no real inputs."""
import hashlib
import json
import os
import pathlib
import secrets
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = pathlib.Path('/opt/a03')
OUT = pathlib.Path('/report')
SOCKET = '/scratch/mariadb.sock'
CHECKS = []
LICENSED = {'woocommerce-subscriptions.zip': 'ed8c529d1382e2d06fa6e605e799c9db5607d8459806c229e74a20571f871083', 'woocommerce-memberships.zip': 'd3a858a8d6ebc7153248a10d665c6752948ea4fa8a1836d6bdd8a8f267ee3285'}

def cmd(args, data=None, check=True, env=None, timeout=180):
    p = subprocess.run(args, input=data, text=True, capture_output=True, env={**os.environ, **(env or {})}, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError('COMMAND_' + pathlib.Path(args[0]).name + '_' + str(p.returncode) + ':' + p.stderr[:1200])
    return p

def wp(site, args, **kw):
    return cmd(['wp', '--allow-root', '--no-color', '--path=' + str(site)] + args, **kw)

def sql(db, query):
    return cmd(['mariadb', '--socket=' + SOCKET, '-uroot', db, '-e', query])

def check(name, ok, detail=None):
    CHECKS.append({'check': name, 'ok': bool(ok), 'detail': detail})
    print(json.dumps(CHECKS[-1]), flush=True)
    if not ok:
        raise AssertionError(name)

def fingerprint(db, details=False):
    value = json.loads(cmd(['php', str(ROOT / 'fingerprint.php')], env={'A02_DB': db}).stdout)
    return value if details else value['logical_sha256']

def filemap(site):
    return {str(p.relative_to(site)): hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file()}

def install(storage):
    site = pathlib.Path('/scratch') / storage
    db = 'a03_' + storage
    sql('mysql', 'CREATE DATABASE ' + db)
    shutil.copytree('/opt/wordpress/wordpress', site)
    shutil.copytree('/opt/woocommerce/woocommerce', site / 'wp-content/plugins/woocommerce')
    for name, digest in LICENSED.items():
        p = ROOT / name
        assert hashlib.sha256(p.read_bytes()).hexdigest() == digest
        with zipfile.ZipFile(p) as z:
            assert len(z.infolist()) < 30000 and sum(e.file_size for e in z.infolist()) < 512 * 1024**2
            for e in z.infolist():
                parts = pathlib.PurePosixPath(e.filename).parts
                assert parts and parts[0] == name[:-4] and '..' not in parts and '\\' not in e.filename and ':' not in e.filename
                assert (e.external_attr >> 16 & 0o170000) in (0, 0o040000, 0o100000)
            z.extractall(site / 'wp-content/plugins')
    config = """<?php
 define('DB_NAME', '%s'); define('DB_USER', 'root'); define('DB_PASSWORD', ''); define('DB_HOST', 'localhost:/scratch/mariadb.sock'); define('DB_CHARSET', 'utf8mb4'); define('DB_COLLATE', '');
 define('WP_ENVIRONMENT_TYPE', 'staging'); define('WP_HTTP_BLOCK_EXTERNAL', true); define('DISABLE_WP_CRON', true); define('AUTOMATIC_UPDATER_DISABLED', true); define('WP_AUTO_UPDATE_CORE', false); define('WP_DEBUG', false);
 $table_prefix = 'wp_'; if (!defined('ABSPATH')) { define('ABSPATH', __DIR__.'/'); } require '/opt/a03/http-rollback.php'; require_once ABSPATH.'wp-settings.php';
 """ % db
    (site / 'wp-config.php').write_text(config)
    wp(site, ['core', 'install', '--url=http://127.0.0.1:18803', '--title=Fiction A03', '--admin_user=a03-admin', '--admin_email=a03-admin@example.org', '--skip-email', '--prompt=admin_password'], data=secrets.token_urlsafe(40) + '\n')
    for p in ['woocommerce', 'woocommerce-memberships', 'woocommerce-subscriptions']:
        wp(site, ['plugin', 'activate', p])
    wp(site, ['option', 'update', 'woocommerce_custom_orders_table_data_sync_enabled', 'no'])
    wp(site, ['option', 'update', 'woocommerce_custom_orders_table_enabled', 'yes' if storage == 'hpos' else 'no'])
    theme = site / 'wp-content/themes/a03-fiction'
    theme.mkdir()
    (theme / 'style.css').write_text('/* Theme Name: Fiction A03\nVersion: 1.0.0\n*/')
    (theme / 'index.php').write_text('<?php echo "<!doctype html><html><body>A03_PAGE_MARKER"; while (have_posts()) { the_post(); the_content(); } echo "</body></html>";')
    wp(site, ['theme', 'activate', 'a03-fiction'])
    seed_exec = wp(site, ['eval-file', str(ROOT / 'seed.php'), '--use-include'])
    seed = json.loads(next(line[9:] for line in seed_exec.stdout.splitlines() if line.startswith('A03_JSON=')))
    check(storage + ':real_plugins', seed['versions']['subscriptions'] and seed['versions']['memberships'], seed['versions'])
    mu = site / 'wp-content/mu-plugins'
    mu.mkdir(exist_ok=True)
    shutil.copyfile('/subject/000-imagine-staging-safety.php', mu / '000-imagine-staging-safety.php')
    marker = {'status': 'verified', 'offline_verified': True, 'runtime_probe_passed': True, 'site': 'imagine-test-a03-fiction'}
    (site / '.imagine-staging-verified.json').write_text(json.dumps(marker))
    # The marker is synthetic input only; the subject independently checks native runtime safety.
    sql('mysql', "CREATE USER 'a03_" + storage + "'@'localhost' IDENTIFIED BY ''; GRANT SELECT ON " + db + ".* TO 'a03_" + storage + "'@'localhost';")
    log_path = ROOT / (storage + '-php-errors.log')
    log_path.write_text('')
    settings = {'php_error_log': str(log_path), 'as_of_month': '2026-11', 'restricted_ids': [seed['restricted']], 'open_id': seed['open'], 'pages': {k: {'path': path, 'marker': 'A03_PAGE_MARKER'} for k, path in seed['pages'].items()}}
    settings_path = ROOT / (storage + '-settings.json')
    settings_path.write_text(json.dumps(settings))
    return site, db, seed, config, settings_path

def snapshot(site, settings, target, extra=None):
    db = 'a03_' + site.name
    sequence_query = "SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='wp_options'"
    sequence = int(sql(db, sequence_query).stdout.splitlines()[-1])
    result = cmd(['php', '/subject/non-regression', '--wp-path=' + str(site), '--config=' + str(settings), '--output=' + str(target)] + (extra or []), check=False)
    # Fixture web requests execute real transient writes, rollback-only. InnoDB
    # allocates IDs even on rollback: restore only this synthetic option sequence,
    # after the collector releases metadata locks, and verify the exact readback.
    sql(db, 'ALTER TABLE wp_options AUTO_INCREMENT=' + str(sequence))
    assert int(sql(db, sequence_query).stdout.splitlines()[-1]) == sequence
    return result

def run_storage(storage):
    site, db, seed, config, settings = install(storage)
    (site / 'wp-config.php').write_text(config.replace("define('DB_USER', 'root')", "define('DB_USER', 'a03_" + storage + "')"))
    log_path = pathlib.Path(json.loads(settings.read_text())['php_error_log'])
    server = subprocess.Popen(['php', '-d', 'log_errors=1', '-d', 'display_errors=0', '-d', 'date.timezone=UTC', '-d', 'error_log=' + str(log_path), '-S', '127.0.0.1:18803', '-t', str(site)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(.5)
    try:
        before_detail = fingerprint(db, details=True)
        before_db, before_files = before_detail['logical_sha256'], filemap(site)
        settings_path = settings
        dropin = site / 'wp-content/object-cache.php'
        dropin.write_text("<?php throw new RuntimeException('A03_DROPIN_MUST_NOT_BOOT');")
        denied_dropin = snapshot(site, settings_path, OUT / (storage + '-dropin'))
        dropin.unlink()
        check(storage + ':dropin_refused_before_bootstrap', denied_dropin.returncode == 1 and denied_dropin.stderr == 'A03_DB_OR_CACHE_DROPIN\n')
        target = OUT / storage
        p = snapshot(site, settings, target)
        check(storage + ':snapshot_cli', p.returncode == 0 and (target / 'non-regression.json').exists(), {'exit': p.returncode, 'stderr': p.stderr[:160]})
        a = json.loads((target / 'non-regression.json').read_text())
        (OUT / (storage + '-synthetic-php.log')).write_bytes(log_path.read_bytes())
        check(storage + ':php_log_checked_bounded_and_clean', a.get('php_log', {}).get('checked') is True and a['php_log']['errors'] == 0 and a['php_log']['from_utc'] <= a['php_log']['until_utc'])
        check(storage + ':ordinary_not_admin_represents_none', a['samples'].get('none:none') == seed['ordinary'] and a['access'].get(str(seed['ordinary']) + ':' + str(seed['restricted'])) is False and not any(key.startswith('1:') for key in a['access']))
        check(storage + ':storage', a['storage'] == storage)
        check(storage + ':rights_matrix', a['access'][str(seed['users'][0]) + ':' + str(seed['restricted'])] is True and all(a['access'][str(u) + ':' + str(seed['restricted'])] is False for u in [seed['users'][1], seed['users'][2], seed['users'][3], seed['users'][5]]) and a['access'][str(seed['users'][4]) + ':' + str(seed['restricted'])] is True and a['access']['0:' + str(seed['restricted'])] is False and set(a['sample_states']['membership']) >= {'active', 'paused', 'expired', 'cancelled', 'pending', 'none'})
        check(storage + ':subscriptions_dates_counts', len(a['subscriptions']) == 6 and {v['status'] for v in a['subscriptions'].values()} == {'active', 'on-hold', 'expired', 'cancelled', 'pending', 'pending-cancel'} and sum(a['subscription_counts']['status'].values()) == 6 and any(v['next_payment_utc'] == '2027-02-01 10:00:00' for v in a['subscriptions'].values()))
        check(storage + ':orders_twelve_months', len(a['order_months']) == 12 and sum(v['count'] for v in a['orders'].values()) == 3 and sum(v['amount_minor'] for v in a['orders'].values()) == 4244)
        check(storage + ':http_pages', len(a['pages']) == 7 and all(v['final_status'] == 200 and v['marker'] and v['php_error'] is False for v in a['pages'].values()))
        after_detail = fingerprint(db, details=True)
        after_files = filemap(site)
        check(storage + ':readonly_database_and_files', fingerprint(db) == before_db and after_files == before_files, {'row_changes': [k for k in before_detail['tables'] if before_detail['tables'][k]['rows_sha256'] != after_detail['tables'][k]['rows_sha256']], 'schema_changes': [k for k in before_detail['tables'] if before_detail['tables'][k]['schema_sha256'] != after_detail['tables'][k]['schema_sha256']], 'file_changes': [k for k in set(before_files) | set(after_files) if before_files.get(k) != after_files.get(k)]})
        denied_output = snapshot(site, settings, pathlib.Path('/proc') / ('a03-output-' + storage))
        check(storage + ':output_failure_cli_is_nonzero_and_readonly', denied_output.returncode == 1
              and denied_output.stderr == 'A03_OUTPUT_FAILED\n' and denied_output.stdout == ''
              and fingerprint(db) == before_db and filemap(site) == before_files)
        repeat = OUT / (storage + '-repeat')
        p = snapshot(site, settings, repeat)
        check(storage + ':repeat_cli', p.returncode == 0)
        compare = cmd(['php', '/subject/comparer', str(target / 'non-regression.json'), str(repeat / 'non-regression.json')], check=False)
        same = json.loads(compare.stdout)
        check(storage + ':identical_no_diff', compare.returncode == 0 and same['changes'] == [])
        (OUT / (storage + '-identical.json')).write_text(compare.stdout)
        fault_mu = site / 'wp-content/mu-plugins/998-a03-collect-fault.php'
        saved_settings = settings.read_text()
        for label, value, code in [('missing', str(log_path) + '-absent', 'A03_PHP_LOG_READ'), ('not-configured', None, 'A03_PHP_LOG_CONFIG')]:
            bad_settings = json.loads(saved_settings)
            if value is None:
                del bad_settings['php_error_log']
            else:
                bad_settings['php_error_log'] = value
            settings.write_text(json.dumps(bad_settings))
            bad_target = OUT / (storage + '-log-' + label)
            denied_log = snapshot(site, settings, bad_target)
            settings.write_text(saved_settings)
            check(storage + ':log_' + label + '_blocks_report', denied_log.returncode == 1 and denied_log.stdout == '' and denied_log.stderr == code + '\n' and not bad_target.exists())
        for label, content, mode, code in [('format', 'A03_PERSONAL_CANARY\n', 0o600, 'A03_PHP_LOG_FORMAT'), ('unreadable', '', 0, 'A03_PHP_LOG_READ')]:
            log_path.write_text(content)
            log_path.chmod(mode)
            bad_target = OUT / (storage + '-log-' + label)
            denied_log = snapshot(site, settings, bad_target)
            log_path.chmod(0o600)
            log_path.write_text('')
            check(storage + ':log_' + label + '_blocks_report_without_pii', denied_log.returncode == 1 and denied_log.stdout == '' and denied_log.stderr == code + '\n' and not bad_target.exists())
        fault_mu.write_text("<?php if (PHP_SAPI === 'cli-server') { error_reporting(E_ALL); trigger_error('A03_PERSONAL_CANARY@example.org', E_USER_WARNING); }")
        try:
            silent_target = OUT / (storage + '-silent-log')
            silent = snapshot(site, settings, silent_target)
        finally:
            fault_mu.unlink()
        silent_report = json.loads((silent_target / 'non-regression.json').read_text())
        silent_diff = cmd(['php', '/subject/comparer', str(target / 'non-regression.json'), str(silent_target / 'non-regression.json')], check=False)
        check(storage + ':silent_php_warning_detected_with_display_off_and_http_200', silent.returncode == 0 and all(v['final_status'] == 200 and v['marker'] and not v['php_error'] for v in silent_report['pages'].values()) and silent_report['php_log']['errors'] >= 7 and silent_diff.returncode == 2 and json.loads(silent_diff.stdout)['changes'] == [{'path': 'php_log.errors', 'class': 'anormal'}])
        log_path.write_text('')
        fault_mu.write_text("<?php add_filter('home_url', static fn() => 'http://127.0.0.1:18804');")
        try:
            http_target = OUT / (storage + '-http-unavailable')
            unavailable = snapshot(site, settings, http_target)
        finally:
            fault_mu.unlink()
        check(storage + ':http_collection_failure_blocks_report', unavailable.returncode == 1 and unavailable.stdout == '' and unavailable.stderr == 'A03_HTTP_READ\n' and not http_target.exists())
        fault_mu.write_text("<?php namespace Imagine\\NonRegression; function wcs_get_subscriptions($args) { global $wpdb; $wpdb->get_var('SELECT ID FROM wp_a03_missing_table'); $wpdb->get_var('SELECT 1'); return \\wcs_get_subscriptions($args); }")
        try:
            hidden_target = OUT / (storage + '-sql-hidden')
            hidden = snapshot(site, settings, hidden_target)
        finally:
            fault_mu.unlink()
        check(storage + ':nested_failed_read_cannot_be_cleared', hidden.returncode == 1 and hidden.stderr == 'A03_SQL_READ\n' and not hidden_target.exists())
        for label, prefix in [('memberships', 'SELECT ID FROM wp_posts WHERE post_type='), ('users', 'SELECT ID FROM wp_users ORDER BY ID'), ('actions', 'SELECT action_id,hook,scheduled_date_gmt FROM')]:
            fault_mu.write_text("<?php add_filter('query', static function ($query) { return str_starts_with($query, " + json.dumps(prefix) + ") ? 'SELECT ID FROM wp_a03_missing_table' : $query; });")
            try:
                bad_target = OUT / (storage + '-sql-' + label)
                denied_sql = snapshot(site, settings, bad_target)
            finally:
                fault_mu.unlink()
            check(storage + ':sql_' + label + '_failure_is_not_empty', denied_sql.returncode == 1 and denied_sql.stderr == 'A03_SQL_READ\n' and not bad_target.exists(), {'exit': denied_sql.returncode, 'stderr': denied_sql.stderr[:100]})
        fault_mu.write_text("<?php add_filter('query', static function ($query) { return str_starts_with($query, 'SELECT action_id,hook,scheduled_date_gmt FROM') ? 'SELECT action_id,hook,scheduled_date_gmt FROM wp_actionscheduler_actions WHERE 1=0' : $query; });")
        try:
            empty_target = OUT / (storage + '-empty-actions')
            empty = snapshot(site, settings, empty_target)
        finally:
            fault_mu.unlink()
        check(storage + ':legitimate_empty_actions_accepted', empty.returncode == 0 and json.loads((empty_target / 'non-regression.json').read_text())['actions'] == [])
        fault_mu.write_text("<?php namespace Imagine\\NonRegression; function wc_memberships_user_can($uid, $action, $target) { return $uid === " + str(seed['ordinary']) + " ? true : \\wc_memberships_user_can($uid, $action, $target); }")
        try:
            rights_target = OUT / (storage + '-ordinary-rights')
            rights = snapshot(site, settings, rights_target)
        finally:
            fault_mu.unlink()
        rights_report = json.loads((rights_target / 'non-regression.json').read_text())
        rights_diff = cmd(['php', '/subject/comparer', str(target / 'non-regression.json'), str(rights_target / 'non-regression.json')], check=False)
        rights_changes = json.loads(rights_diff.stdout)['changes']
        check(storage + ':only_ordinary_right_changed_and_detected', rights.returncode == 0 and rights_report['samples'] == a['samples'] and rights_diff.returncode == 2 and rights_changes == [{'path': 'access.' + str(seed['ordinary']) + ':' + str(seed['restricted']), 'class': 'anormal'}])
        check(storage + ':fault_probes_readonly', fingerprint(db) == before_db and filemap(site) == before_files)
        # Native synthetic AS rows; only the previous-version oracle is edited.
        hook = 'woocommerce_run_on_woocommerce_admin_updated'
        previous = dict(a)
        previous['versions'] = {**a['versions'], 'woocommerce': '11.0.1'}
        previous_file = OUT / (storage + '-previous-version-oracle.json')
        previous_file.write_text(json.dumps(previous))
        for label, scheduled_hook, expected_code in [('expected', hook, 3), ('not-expected', 'woocommerce_run_update_callback', 2)]:
            sql(db, "INSERT INTO wp_actionscheduler_actions (hook,status,scheduled_date_gmt,scheduled_date_local,args,schedule,group_id) SELECT '" + scheduled_hook + "',status,scheduled_date_gmt,scheduled_date_local,args,schedule,group_id FROM wp_actionscheduler_actions WHERE action_id=" + str(seed['action']))
            action_id = int(sql(db, 'SELECT MAX(action_id) FROM wp_actionscheduler_actions').stdout.splitlines()[-1])
            hook_target = OUT / (storage + '-hook-' + label)
            hook_photo = snapshot(site, settings, hook_target)
            hook_diff = cmd(['php', '/subject/comparer', str(previous_file), str(hook_target / 'non-regression.json')], check=False)
            hook_changes = json.loads(hook_diff.stdout)
            sql(db, 'DELETE FROM wp_actionscheduler_actions WHERE action_id=' + str(action_id))
            check(storage + ':native_hook_' + label + '_classification', hook_photo.returncode == 0 and hook_diff.returncode == expected_code and hook_changes['anormal'] == (0 if label == 'expected' else 2) and len(hook_changes['changes']) == 3)
        # Mutations are oracle-only, created within this disposable fixture.
        sql(db, "UPDATE wp_posts SET post_status='wcm-expired' WHERE ID=" + str(seed['membership_ids']['active']))
        sql(db, 'DELETE FROM wp_actionscheduler_actions WHERE action_id=' + str(seed['action']))
        changed = OUT / (storage + '-altered')
        p = snapshot(site, settings, changed)
        check(storage + ':altered_cli', p.returncode == 0, {'stderr': p.stderr[:160]})
        diff = cmd(['php', '/subject/comparer', str(target / 'non-regression.json'), str(changed / 'non-regression.json')], check=False)
        data = json.loads(diff.stdout)
        (OUT / (storage + '-anomalies.json')).write_text(diff.stdout)
        check(storage + ':two_mutations_detected', diff.returncode == 2 and any(v['class'] == 'anormal' and v['path'].startswith('access.') for v in data['changes']) and any(v['class'] == 'anormal' and v['path'].startswith('actions.') for v in data['changes']))
        # Export privacy only; served-content leak tests belong to the paywall lot.
        check(storage + ':privacy', all(token not in p.read_text() for p in OUT.rglob('*.json') for token in ['A03_PERSONAL_CANARY', 'A03_PRIVATE_ARGS_CANARY', '@example.org']))
        marker_path = site / '.imagine-staging-verified.json'
        marker_bytes = marker_path.read_bytes()
        marker_path.unlink()
        denied = snapshot(site, settings, OUT / (storage + '-unverified'), ['--renewal-test'])
        marker_path.write_bytes(marker_bytes)
        check(storage + ':renewal_unverified_refused', denied.returncode == 1 and denied.stderr == 'A03_JSON_FILE\n' and not (OUT / (storage + '-unverified')).exists())
        # Only the opt-in run gets the synthetic writer config; no real credential exists.
        (site / 'wp-config.php').write_text(config)
        denied_default = snapshot(site, settings, OUT / (storage + '-writer-default'))
        check(storage + ':default_requires_select_account', denied_default.returncode == 1 and denied_default.stderr == 'A03_SELECT_ACCOUNT_REQUIRED\n')
        inverse = site / 'wp-content/mu-plugins/999-a03-inverse.php'
        inverse.write_text("<?php add_filter('woocommerce_subscriptions_is_duplicate_site', '__return_false', PHP_INT_MAX);")
        denied_runtime = snapshot(site, settings, OUT / (storage + '-unsafe-runtime'), ['--renewal-test'])
        inverse.unlink()
        check(storage + ':renewal_runtime_refused', denied_runtime.returncode == 1 and denied_runtime.stderr == 'A03_RUNTIME_UNSAFE\n')
        renewal_before = fingerprint(db, details=True)
        renewed = snapshot(site, settings, OUT / (storage + '-renewal'), ['--renewal-test'])
        check(storage + ':renewal_cli', renewed.returncode == 0, {'exit': renewed.returncode, 'stderr': renewed.stderr[:180]})
        renewal = json.loads((OUT / (storage + '-renewal/non-regression.json')).read_text())['renewal']
        check(storage + ':manual_renewal_created_and_cleaned', renewal['enabled'] and renewal['manual_only'] and renewal['created'] and renewal['linked'] and renewal['pending'] and renewal['cleaned'])
        renewal_after = fingerprint(db, details=True)
        row_changes = [key for key in renewal_before['tables'] if renewal_before['tables'][key]['rows_sha256'] != renewal_after['tables'][key]['rows_sha256']]
        check(storage + ':renewal_business_rows_restored', not row_changes, {'changed_tables': row_changes})
        failure = site / 'wp-content/mu-plugins/999-a03-failure.php'
        failure.write_text("<?php add_filter('wcs_renewal_order_created', static function ($order) { throw new RuntimeException('A03_TEST_FAILURE_AFTER_CREATE'); });")
        failed_before = fingerprint(db, details=True)
        failed = snapshot(site, settings, OUT / (storage + '-renewal-failed'), ['--renewal-test'])
        failure.unlink()
        failed_after = fingerprint(db, details=True)
        check(storage + ':renewal_failure_rolls_back', failed.returncode == 1 and failed.stderr == 'A03_TEST_FAILURE_AFTER_CREATE\n' and all(failed_before['tables'][key]['rows_sha256'] == failed_after['tables'][key]['rows_sha256'] for key in failed_before['tables']) and not (OUT / (storage + '-renewal-failed')).exists())
    finally:
        server.terminate()
        server.wait(timeout=15)


def main():
    pathlib.Path('/scratch').mkdir()
    cmd(['mariadb-install-db', '--datadir=/scratch/mysql', '--auth-root-authentication-method=normal', '--skip-test-db', '--user=root'])
    db = subprocess.Popen(['mariadbd', '--user=root', '--datadir=/scratch/mysql', '--socket=' + SOCKET, '--skip-networking', '--skip-log-bin', '--pid-file=/scratch/mysql.pid', '--log-error=/scratch/mysql.log'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            if cmd(['mariadb-admin', '--socket=' + SOCKET, '-uroot', 'ping'], check=False).returncode == 0:
                break
            time.sleep(.2)
        for storage in ['classic', 'hpos']:
            try:
                run_storage(storage)
            except Exception as error:
                CHECKS.append({'check': storage + ':exception', 'ok': False, 'class': type(error).__name__, 'code': str(error)[:500]})
                print(json.dumps(CHECKS[-1]), flush=True)
        check('network_none', [p.name for p in pathlib.Path('/sys/class/net').iterdir()] == ['lo'])
        for file in ['/proc/net/tcp', '/proc/net/tcp6']:
            check('no_listener:' + pathlib.Path(file).name, not any(line.split()[3] == '0A' for line in pathlib.Path(file).read_text().splitlines()[1:]))
    finally:
        db.terminate()
        db.wait(timeout=30)
        result = {'suite': 'A03-real-classic-hpos', 'checks': CHECKS, 'exit_code': int(any(not c['ok'] for c in CHECKS))}
        (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result['exit_code']

if __name__ == '__main__':
    sys.exit(main())
