"""A02 integration: real Woo/WCS/Memberships, both authoritative stores."""
import hashlib
import json
import os
import pathlib
import re
import secrets
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = pathlib.Path('/opt/a02')
OUT = pathlib.Path('/report')
SCRATCH = pathlib.Path('/scratch')
SOCKET = '/scratch/mariadb.sock'
CHECKS = []
LICENSED = {
    'woocommerce-subscriptions.zip': 'ed8c529d1382e2d06fa6e605e799c9db5607d8459806c229e74a20571f871083',
    'woocommerce-memberships.zip': 'd3a858a8d6ebc7153248a10d665c6752948ea4fa8a1836d6bdd8a8f267ee3285',
}

def cmd(args, check=True, env=None, data=None, timeout=240):
    p = subprocess.run(args, input=data, text=True, capture_output=True, env={**os.environ, **(env or {})}, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError('COMMAND_FAILED:' + pathlib.Path(args[0]).name + ':' + str(p.returncode) + ':stderr_sha256=' + hashlib.sha256(p.stderr.encode()).hexdigest())
    return p

def wp(site, args, **kw):
    return cmd(['wp', '--allow-root', '--no-color', '--path=' + str(site)] + args, **kw)

def sql(db, query):
    return cmd(['mariadb', '--socket=' + SOCKET, '-uroot', db, '-e', query])

def check(name, ok, detail=None):
    CHECKS.append({'check': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
    print(json.dumps(CHECKS[-1]), flush=True)
    if not ok:
        raise AssertionError(name)

def fingerprint(db):
    return json.loads(cmd(['php', str(ROOT / 'fingerprint.php')], env={'A02_DB': db}).stdout)

def files(site):
    entries = {str(p.relative_to(site)): hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file()}
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()

def install(storage):
    db = 'a02_' + storage
    sql('mysql', 'CREATE DATABASE ' + db)
    site = SCRATCH / storage
    shutil.copytree('/opt/wordpress/wordpress', site)
    shutil.copytree('/opt/woocommerce/woocommerce', site / 'wp-content/plugins/woocommerce')
    for name, expected in LICENSED.items():
        package = ROOT / name
        assert hashlib.sha256(package.read_bytes()).hexdigest() == expected
        with zipfile.ZipFile(package) as archive:
            assert len(archive.infolist()) < 30000 and sum(e.file_size for e in archive.infolist()) < 512 * 1024 ** 2
            for e in archive.infolist():
                parts = pathlib.PurePosixPath(e.filename).parts
                assert parts and parts[0] == name[:-4] and '..' not in parts and '\\' not in e.filename and ':' not in e.filename and (e.external_attr >> 16 & 0o170000) in (0, 0o040000, 0o100000)
            archive.extractall(site / 'wp-content/plugins')
    config = """<?php
define('DB_NAME', '%s'); define('DB_USER', 'root'); define('DB_PASSWORD', ''); define('DB_HOST', 'localhost:/scratch/mariadb.sock'); define('DB_CHARSET', 'utf8mb4'); define('DB_COLLATE', '');
define('WP_ENVIRONMENT_TYPE', 'staging'); define('WP_HTTP_BLOCK_EXTERNAL', true); define('DISABLE_WP_CRON', true); define('AUTOMATIC_UPDATER_DISABLED', true); define('WP_AUTO_UPDATE_CORE', false); define('WP_DEBUG', false);
$table_prefix = 'wp_'; define('ABSPATH', __DIR__.'/'); require_once ABSPATH.'wp-settings.php';
""" % db
    (site / 'wp-config.php').write_text(config)
    wp(site, ['core', 'install', '--url=https://a02.synthetic.test', '--title=A02 invented fixture', '--admin_user=a02-admin', '--admin_email=a02-admin@example.org', '--skip-email', '--prompt=admin_password'], data=secrets.token_urlsafe(40) + '\n')
    for plugin in ['woocommerce', 'woocommerce-memberships', 'woocommerce-subscriptions']:
        wp(site, ['plugin', 'activate', plugin])
    wp(site, ['option', 'update', 'woocommerce_custom_orders_table_data_sync_enabled', 'no'])
    wp(site, ['option', 'update', 'woocommerce_custom_orders_table_enabled', 'yes' if storage == 'hpos' else 'no'])
    builder = site / 'wp-content/plugins/fixture-builder'
    builder.mkdir()
    (builder / 'fixture-builder.php').write_text('<?php\n/* Plugin Name: Fixture builder\nVersion: 1.0.0\nRequires at least: 6.0\nRequires PHP: 8.2\n*/\n')
    inactive = site / 'wp-content/plugins/inactive-fixture'
    inactive.mkdir()
    (inactive / 'inactive-fixture.php').write_text('<?php\n/* Plugin Name: Inactive fixture\nVersion: 0.5.0\n*/\n')
    mu = site / 'wp-content/mu-plugins'
    mu.mkdir(exist_ok=True)
    (mu / 'a02-fixture.php').write_text('<?php\n/* Plugin Name: A02 MU\nVersion: 1.0.0\n*/\n')
    theme = site / 'wp-content/themes/a02-theme'
    (theme / 'woocommerce/myaccount').mkdir(parents=True)
    (theme / 'style.css').write_text('/*\nTheme Name: A02 fixture\nVersion: 1.0.0\nRequires at least: 6.0\nRequires PHP: 8.2\n*/\n')
    (theme / 'index.php').write_text('<?php // fixture\n')
    (theme / 'woocommerce/myaccount/form-login.php').write_text('<?php /** @version 1.0.0 */\n')
    p = wp(site, ['eval-file', str(ROOT / 'seed.php'), '--use-include'])
    lines = [line[9:] for line in p.stdout.splitlines() if line.startswith('A02_JSON=')]
    seed = json.loads(lines[0])
    (OUT / (storage + '-seed.json')).write_text(json.dumps(seed, indent=2) + '\n')
    check(storage + ':commercial_fixture', seed['subscriptions'] == 3 and seed['rules'] == 2 and seed['restriction_real'] and seed['hpos'] == (storage == 'hpos'), seed)
    (site / 'wp-content/debug.log').write_text('[23-Nov-2026] PHP Deprecated: Function a02_legacy_function is deprecated since version 6.0! A02_LOG_PRIVATE_CANARY in /private/person@example.org/file.php\n')
    # Any execution of wp-config or WP bootstrap is now independently visible.
    (site / 'wp-config.php').write_text(config + "\nfile_put_contents('/scratch/a02-bootstrap-trap', 'EXECUTED');\n")
    # Subject credential has ONLY SELECT, no UPDATE/DDL; root remains oracle-only.
    sql('mysql', "CREATE USER 'a02_" + storage + "'@'localhost' IDENTIFIED BY ''; GRANT SELECT ON " + db + ".* TO 'a02_" + storage + "'@'localhost';")
    (site / 'wp-config.php').write_text((site / 'wp-config.php').read_text().replace("define('DB_USER', 'root')", "define('DB_USER', 'a02_" + storage + "')"))
    return site, db, seed

def audit(site, out):
    return cmd(['php', '/subject/audit', '--wp-path=' + str(site), '--output=' + str(out)], check=False)

def run_storage(storage):
    site, db, seed = install(storage)
    before = fingerprint(db)
    (OUT / (storage + '-db-before.json')).write_text(json.dumps(before, indent=2) + '\n')
    file_before = files(site)
    target = OUT / storage
    p = audit(site, target)
    check(storage + ':cli_success', p.returncode == 0 and (target / 'audit.json').is_file() and (target / 'audit.md').is_file(), {'exit': p.returncode, 'stdout_sha256': hashlib.sha256(p.stdout.encode()).hexdigest(), 'stderr_sha256': hashlib.sha256(p.stderr.encode()).hexdigest()})
    data = json.loads((target / 'audit.json').read_text())
    check(storage + ':seven_sections', set(data['sections']) == {'versions', 'commerce', 'memberships', 'content', 'database', 'scheduling', 'risks'})
    versions = data['sections']['versions']
    check(storage + ':runtime_versions', versions['wordpress'] == seed['versions']['wordpress'] and versions['php'] and versions['database'])
    plugins = {v['name']: v for v in versions['plugins']}
    check(storage + ':plugins_inactive_mu', plugins['inactive-fixture/inactive-fixture.php']['active'] is False and plugins['mu/a02-fixture.php']['active'] is True)
    check(storage + ':cached_update_and_requirements', plugins['fixture-builder/fixture-builder.php']['latest'] == '3.0.0' and plugins['fixture-builder/fixture-builder.php']['requires_php'] == '8.2')
    check(storage + ':commercial_requirements_constants', plugins['woocommerce-memberships/woocommerce-memberships.php']['requires_php'] == '7.4' and plugins['woocommerce-memberships/woocommerce-memberships.php']['requires_wp'] == '5.6')
    check(storage + ':unknown_latest_not_invented', plugins['inactive-fixture/inactive-fixture.php']['latest'] is None)
    themes = {v['name']: v for v in versions['themes']}
    check(storage + ':theme_inventory', themes['a02-theme']['active'] and themes['a02-theme']['latest'] == '2.0.0')
    commerce = data['sections']['commerce']
    check(storage + ':authoritative_storage', commerce['order_storage'] == storage)
    check(storage + ':subscription_aggregates', sum(v['count'] for v in commerce['subscriptions']) == 3 and {v['status'] for v in commerce['subscriptions']} == {'wc-active', 'wc-on-hold', 'wc-pending-cancel'} and {v['period'] for v in commerce['subscriptions']} == {'month', 'year'})
    check(storage + ':membership_aggregates', sum(v['count'] for v in commerce['memberships']) == 3 and {v['status'] for v in commerce['memberships']} == {'wcm-active', 'wcm-expired', 'wcm-cancelled'})
    check(storage + ':order_years', {str(v['year']): v['count'] for v in commerce['orders_by_year']} == {'2023': 1, '2025': 2})
    check(storage + ':gateways_present', {'bacs', 'cheque', 'cod'}.issubset(set(commerce['gateways'])))
    product = next(v for v in commerce['subscription_products'] if v['id'] == seed['product_id'])
    check(storage + ':product_safe_settings', product['period'] == 'month' and product['interval'] == 2 and product['trial_length'] == 7 and product['sign_up_fee'] == '4.50' and product['sync'] == 15)
    memberships = data['sections']['memberships']
    check(storage + ':membership_plan_and_rules', seed['plan_id'] in [v['id'] for v in memberships['plans']] and len(memberships['rules']) == 2)
    check(storage + ':restriction_taxonomy_drip', any(v['content_type_name'] == 'category' and v['drip'] and v['amount'] == 7 and v['period'] == 'day' for v in memberships['rules']))
    content = data['sections']['content']
    check(storage + ':content_counts', next(v['count'] for v in content['post_types'] if v['name'] == 'post') >= 3 and any(v['name'] == 'category' for v in content['taxonomies']))
    check(storage + ':empty_core_types_and_taxonomies', any(v['name'] == 'revision' and v['count'] == 0 for v in content['post_types']) and any(v['name'] == 'post_tag' and v['count'] == 0 for v in content['taxonomies']))
    check(storage + ':no_fixture_specific_builder_detection', content['page_builders'] == [])
    check(storage + ':yearly_articles_fields', any(v['year'] == 2025 and v['count'] == 2 for v in content['posts_by_year']) and any(v['name'] == 'a02_editorial_field' and v['count'] == 3 for v in content['custom_fields']))
    dbs = data['sections']['database']
    check(storage + ':all_tables_counts_sizes', len(dbs['tables']) == len(before['tables']) and all(v['rows'] == before['tables'][v['name']]['rows'] and v['bytes'] >= 0 for v in dbs['tables']))
    check(storage + ':orphan_candidate', any(v['name'] == 'wp_orphan_fixture' and v['ownership'] == 'unattributed_candidate' for v in dbs['tables']))
    check(storage + ':commercial_tables_not_orphaned', all(v['ownership'] == 'active_subscriptions' for v in dbs['tables'] if v['name'] in {'wp_wcs_health_check_candidates', 'wp_wcs_health_check_runs', 'wp_woocommerce_subscription_downloads'}))
    check(storage + ':heavy_autoload_names_sizes', any(v['name'] == 'a02_heavy_secret_setting' and v['bytes'] > 100000 for v in dbs['largest_autoload']))
    schedule = data['sections']['scheduling']
    check(storage + ':action_counts', any(v['hook'] == 'a02_fixture_action' and v['status'] == 'pending' and v['count'] == 1 for v in schedule['actions']) and any(v['hook'] == 'a02_fixture_failed' and v['status'] == 'failed' for v in schedule['actions']))
    check(storage + ':cron_no_arguments', any(v['hook'] == 'a02_fixture_cron' and v['schedule'] == 'daily' for v in schedule['cron']))
    risks = data['sections']['risks']
    check(storage + ':update_gap_stale_plugin', any(v['name'] == 'fixture-builder/fixture-builder.php' and v['update_available'] and v['older_than_two_years'] for v in risks['plugin_updates']))
    check(storage + ':outdated_override', any(v['file'] == 'myaccount/form-login.php' and v['outdated'] for v in risks['woocommerce_templates']))
    check(storage + ':deprecated_only_function', risks['deprecated_functions'] == [{'function': 'a02_legacy_function', 'count': 1}])
    check(storage + ':five_priorities', len(data['priorities']) == 5 and '## Synthese' in (target / 'audit.md').read_text())
    payload = (target / 'audit.json').read_text() + (target / 'audit.md').read_text() + p.stdout + p.stderr
    check(storage + ':no_private_values', not re.search(r'A02_(?:PERSONAL|CONTENT|FIELD|TERM|PLAN|PRODUCT|SECRET_VALUE|BANK|CRON_ARGUMENT|ACTION_ARGUMENT|PACKAGE_TOKEN|TABLE|LOG)_PRIVATE?_?CANARY|@example|private.invalid|/scratch|DB_PASSWORD', payload) and not any(x in payload for x in ['A02_PERSONAL_CANARY', 'A02_CONTENT_PRIVATE_CANARY', 'A02_SECRET_VALUE_CANARY', 'A02_PACKAGE_TOKEN_CANARY']))
    # A second run cannot reuse or overwrite an existing report directory.
    report_hash = hashlib.sha256((target / 'audit.json').read_bytes()).hexdigest()
    repeat = audit(site, target)
    check(storage + ':existing_output_refused', repeat.returncode != 0 and hashlib.sha256((target / 'audit.json').read_bytes()).hexdigest() == report_hash)
    unsafe = audit(site, site / 'audit-output')
    check(storage + ':output_inside_site_refused', unsafe.returncode != 0 and not (site / 'audit-output').exists())
    second = OUT / (storage + '-repeat')
    rerun = audit(site, second)
    check(storage + ':replay_success', rerun.returncode == 0 and json.loads((second / 'audit.json').read_text())['sections'] == data['sections'])
    after = fingerprint(db)
    (OUT / (storage + '-db-after.json')).write_text(json.dumps(after, indent=2) + '\n')
    check(storage + ':db_identical', before == after, {'before': before['logical_sha256'], 'after': after['logical_sha256'], 'tables': len(before['tables'])})
    check(storage + ':site_files_identical', file_before == files(site), {'before': file_before, 'after': files(site)})
    check(storage + ':never_bootstrap', not (SCRATCH / 'a02-bootstrap-trap').exists())
    original = (site / 'wp-config.php').read_text()
    try:
        (site / 'wp-config.php').write_text(original.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')"))
        guard = cmd(['php', str(ROOT / 'readonly-probe.php')], env={'A02_SITE': str(site)}, check=False)
        check(storage + ':transaction_blocks_even_root', guard.returncode == 0 and all(json.loads(guard.stdout).values()), json.loads(guard.stdout))
    finally:
        (site / 'wp-config.php').write_text(original)
    # Invalid dynamic configuration must never be executed or printed.
    try:
        (site / 'wp-config.php').write_text(original.replace("define('DB_PASSWORD', '')", "define('DB_PASSWORD', getenv('A02_NEVER_EXECUTE_PRIVATE_CANARY'))"))
        bad = audit(site, OUT / (storage + '-invalid-config'))
        check(storage + ':dynamic_config_safe_refusal', bad.returncode == 1 and bad.stderr == 'A02_CONFIG_NON_LITERAL\n' and not (OUT / (storage + '-invalid-config')).exists())
    finally:
        (site / 'wp-config.php').write_text(original)
    # Parent-directory symlinks must not escape the selected synthetic site.
    link = site / 'wp-content/themes/a02-symlink'
    external = SCRATCH / ('external-' + storage)
    external.mkdir()
    (external / 'style.css').write_text('/* Theme Name: private canary\nVersion: 1.0.0\n*/')
    link.symlink_to(external, target_is_directory=True)
    bad = audit(site, OUT / (storage + '-symlink'))
    check(storage + ':symlink_parent_refused', bad.returncode == 1 and not (OUT / (storage + '-symlink')).exists())
    link.unlink()
    check(storage + ':negative_probes_no_database_change', before == fingerprint(db))
    check(storage + ':negative_probes_files_restored', file_before == files(site))
    # A separate, explicit synthetic variant removes local knowledge, not site data.
    sql(db, "DELETE FROM wp_options WHERE option_name IN ('_site_transient_update_plugins','_site_transient_update_themes')")
    (site / 'wp-content/debug.log').unlink()
    variant_before = fingerprint(db)
    (OUT / (storage + '-no-cache-db-before.json')).write_text(json.dumps(variant_before, indent=2) + '\n')
    no_cache = OUT / (storage + '-no-cache')
    unknown = audit(site, no_cache)
    check(storage + ':no_cache_audit_success', unknown.returncode == 0)
    unknown_report = json.loads((no_cache / 'audit.json').read_text())
    check(storage + ':missing_knowledge_explicit', all(p['latest'] is None for p in unknown_report['sections']['versions']['plugins']) and all(p['older_than_two_years'] is None for p in unknown_report['sections']['risks']['plugin_updates']) and unknown_report['sections']['risks']['debug_log_coverage'] == 'absent')
    variant_after = fingerprint(db)
    (OUT / (storage + '-no-cache-db-after.json')).write_text(json.dumps(variant_after, indent=2) + '\n')
    check(storage + ':no_cache_database_unchanged', variant_before == variant_after)

def main():
    SCRATCH.mkdir()
    cmd(['mariadb-install-db', '--datadir=/scratch/mysql', '--auth-root-authentication-method=normal', '--skip-test-db', '--user=root'])
    process = subprocess.Popen(['mariadbd', '--user=root', '--datadir=/scratch/mysql', '--socket=' + SOCKET, '--skip-networking', '--skip-log-bin', '--pid-file=/scratch/mysql.pid', '--log-error=/scratch/mysql.log'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            if cmd(['mariadb-admin', '--socket=' + SOCKET, '-uroot', 'ping'], check=False, timeout=5).returncode == 0:
                break
            time.sleep(.2)
        for file in ['/subject/audit', '/opt/a02/seed.php', '/opt/a02/fingerprint.php', '/opt/a02/unit.php', '/opt/a02/readonly-probe.php']:
            p = cmd(['php', '-l', file], check=False)
            check('lint:' + pathlib.Path(file).name, p.returncode == 0)
        for storage in ['classic', 'hpos']:
            try:
                run_storage(storage)
            except Exception as exc:
                CHECKS.append({'check': storage + ':exception', 'status': 'FAIL', 'detail': {'class': type(exc).__name__, 'code': str(exc)}})
        check('network_interfaces', [p.name for p in pathlib.Path('/sys/class/net').iterdir()] == ['lo'])
        for file in ['/proc/net/tcp', '/proc/net/tcp6']:
            check('no_listener:' + pathlib.Path(file).name, not any(line.split()[3] == '0A' for line in pathlib.Path(file).read_text().splitlines()[1:]))
    finally:
        process.terminate(); process.wait(timeout=30)
        result = {'suite': 'A02-real-commercial-fixture', 'checks': CHECKS, 'exit_code': int(any(c['status'] != 'PASS' for c in CHECKS)), 'licensed_sha256': LICENSED, 'no_real_site': True}
        (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result['exit_code']

if __name__ == '__main__':
    sys.exit(main())
