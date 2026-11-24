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

def fingerprint(db):
    return json.loads(cmd(['php', str(ROOT / 'fingerprint.php')], env={'A02_DB': db}).stdout)['logical_sha256']

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
 $table_prefix = 'wp_'; if (!defined('ABSPATH')) { define('ABSPATH', __DIR__.'/'); } require_once ABSPATH.'wp-settings.php';
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
    settings = {'as_of_month': '2026-11', 'restricted_ids': [seed['restricted']], 'open_id': seed['open'], 'pages': {k: {'path': path, 'marker': 'A03_PAGE_MARKER'} for k, path in seed['pages'].items()}}
    settings_path = ROOT / (storage + '-settings.json')
    settings_path.write_text(json.dumps(settings))
    return site, db, seed, config, settings_path

def snapshot(site, settings, target, extra=None):
    return cmd(['php', '/subject/non-regression', '--wp-path=' + str(site), '--config=' + str(settings), '--output=' + str(target)] + (extra or []), check=False)

def run_storage(storage):
    site, db, seed, config, settings = install(storage)
    (site / 'wp-config.php').write_text(config.replace("define('DB_USER', 'root')", "define('DB_USER', 'a03_" + storage + "')"))
    server = subprocess.Popen(['php', '-d', 'log_errors=0', '-d', 'display_errors=0', '-S', '127.0.0.1:18803', '-t', str(site)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(.5)
    try:
        before_db, before_files = fingerprint(db), filemap(site)
        target = OUT / storage
        p = snapshot(site, settings, target)
        check(storage + ':snapshot_cli', p.returncode == 0 and (target / 'non-regression.json').exists(), {'exit': p.returncode, 'stderr': p.stderr[:160]})
        a = json.loads((target / 'non-regression.json').read_text())
        check(storage + ':storage', a['storage'] == storage)
        check(storage + ':rights_matrix', a['access'][str(seed['users'][0]) + ':' + str(seed['restricted'])] is True and all(a['access'][str(u) + ':' + str(seed['restricted'])] is False for u in [seed['users'][1], seed['users'][2], seed['users'][3], seed['users'][5]]) and a['access'][str(seed['users'][4]) + ':' + str(seed['restricted'])] is True and a['access']['0:' + str(seed['restricted'])] is False and set(a['sample_states']['membership']) >= {'active', 'paused', 'expired', 'cancelled', 'pending', 'none'})
        check(storage + ':subscriptions_dates_counts', len(a['subscriptions']) == 6 and {v['status'] for v in a['subscriptions'].values()} == {'active', 'on-hold', 'expired', 'cancelled', 'pending', 'pending-cancel'} and sum(a['subscription_counts']['status'].values()) == 6 and any(v['next_payment_utc'] == '2027-02-01 10:00:00' for v in a['subscriptions'].values()))
        check(storage + ':orders_twelve_months', len(a['order_months']) == 12 and sum(v['count'] for v in a['orders'].values()) == 3 and sum(v['amount_minor'] for v in a['orders'].values()) == 4244)
        check(storage + ':http_pages', len(a['pages']) == 7 and all(v['final_status'] == 200 and v['marker'] and v['php_error'] is False for v in a['pages'].values()))
        check(storage + ':readonly_database_and_files', fingerprint(db) == before_db and filemap(site) == before_files)
        repeat = OUT / (storage + '-repeat')
        p = snapshot(site, settings, repeat)
        check(storage + ':repeat_cli', p.returncode == 0)
        compare = cmd(['php', '/subject/comparer', str(target / 'non-regression.json'), str(repeat / 'non-regression.json')], check=False)
        same = json.loads(compare.stdout)
        check(storage + ':identical_no_diff', compare.returncode == 0 and same['changes'] == [])
        (OUT / (storage + '-identical.json')).write_text(compare.stdout)
        # Mutations are oracle-only, created within this disposable fixture.
        sql(db, "UPDATE wp_posts SET post_status='wcm-expired' WHERE ID=" + str(seed['membership_ids']['active']))
        sql(db, 'DELETE FROM wp_actionscheduler_actions WHERE action_id=' + str(seed['action']))
        changed = OUT / (storage + '-altered')
        p = snapshot(site, settings, changed)
        check(storage + ':altered_cli', p.returncode == 0)
        diff = cmd(['php', '/subject/comparer', str(target / 'non-regression.json'), str(changed / 'non-regression.json')], check=False)
        data = json.loads(diff.stdout)
        (OUT / (storage + '-anomalies.json')).write_text(diff.stdout)
        check(storage + ':two_mutations_detected', diff.returncode == 2 and any(v['class'] == 'anormal' and v['path'].startswith('access.') for v in data['changes']) and any(v['class'] == 'anormal' and v['path'].startswith('actions.') for v in data['changes']))
        check(storage + ':privacy', all(token not in p.read_text() for p in OUT.rglob('*.json') for token in ['A03_PERSONAL_CANARY', 'A03_PRIVATE_CONTENT_CANARY', 'A03_PRIVATE_ARGS_CANARY', '@example.org']))
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
