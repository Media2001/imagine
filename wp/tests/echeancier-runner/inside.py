"""Boot a fresh invented site; no HTTP services, external calls or host data."""
import hashlib
import json
import pathlib
import secrets
import shutil
import subprocess
import time
import traceback
import zipfile

BASE = pathlib.Path('/work/wp/tests/echeancier-runner')
REPORT = pathlib.Path('/report/c05-result.json')
CHECKS = []


def command(args, input_text=None, check=True, timeout=240):
    p = subprocess.run(args, input=input_text, capture_output=True, text=True, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError(pathlib.Path(args[0]).name + ': ' + p.stderr[-3500:] + p.stdout[-1500:])
    return p


def wp(site, args, **kwargs):
    return command(['wp', '--allow-root', '--no-color', '--path=' + str(site)] + args, **kwargs)


def check(name, condition, detail):
    CHECKS.append({'check': name, 'pass': bool(condition), 'detail': detail})
    if not condition:
        raise AssertionError(name)


def isolation():
    check('loopback_only', [p.name for p in pathlib.Path('/sys/class/net').iterdir()] == ['lo'], 'network none')
    for filename in ('tcp', 'tcp6'):
        rows = pathlib.Path('/proc/net/' + filename).read_text().splitlines()[1:]
        check('no_listener_' + filename, not any(row.split()[3] == '0A' for row in rows), 'MariaDB Unix socket only')


def install(storage):
    database = 'c05_' + storage
    command(['mariadb', '--socket=/scratch/mariadb.sock', '--user=root', '-e', 'CREATE DATABASE ' + database])
    site = pathlib.Path('/scratch/site-' + storage)
    shutil.copytree('/opt/wordpress/wordpress', site)
    shutil.copytree('/opt/woocommerce/woocommerce', site / 'wp-content/plugins/woocommerce')
    package = pathlib.Path('/opt/e2e/woocommerce-subscriptions.zip')
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    check(storage + ':authorized_package', digest == 'ed8c529d1382e2d06fa6e605e799c9db5607d8459806c229e74a20571f871083', digest)
    with zipfile.ZipFile(package) as z:
        for e in z.infolist():
            parts = pathlib.PurePosixPath(e.filename).parts
            assert parts and parts[0] == 'woocommerce-subscriptions' and '..' not in parts
            assert '\\' not in e.filename and ':' not in e.filename
            assert e.external_attr >> 16 & 0o170000 in (0, 0o040000, 0o100000)
        z.extractall(site / 'wp-content/plugins')
    (site / 'wp-config.php').write_text("""<?php
    define('DB_NAME','%s');define('DB_USER','root');define('DB_PASSWORD','');
    define('DB_HOST','localhost:/scratch/mariadb.sock');define('DB_CHARSET','utf8mb4');define('DB_COLLATE','');
    define('WP_ENVIRONMENT_TYPE','staging');define('WP_HTTP_BLOCK_EXTERNAL',true);define('DISABLE_WP_CRON',true);
    define('AUTOMATIC_UPDATER_DISABLED',true);define('WP_AUTO_UPDATE_CORE',false);define('WP_DEBUG',false);
    $table_prefix='wp_';define('ABSPATH',__DIR__.'/');require_once ABSPATH.'wp-settings.php';
    """ % database)
    mu = site / 'wp-content/mu-plugins'
    mu.mkdir(exist_ok=True)
    (mu / 'imagine-c05-fixture.php').write_text("""<?php
    add_filter('pre_wp_mail','__return_false',PHP_INT_MAX);
    add_filter('pre_http_request',static function(){return new WP_Error('c05_offline');},PHP_INT_MAX);
    add_filter('action_scheduler_allow_async_request_runner','__return_false',PHP_INT_MAX);
    add_action('plugins_loaded',static function(){remove_all_actions('action_scheduler_run_queue');},PHP_INT_MAX);
    """)
    wp(site, ['core', 'install', '--url=https://c05.synthetic.test', '--title=Fiction C05',
              '--admin_user=c05-fiction', '--admin_email=c05-fiction@example.org', '--skip-email', '--prompt=admin_password'],
       input_text=secrets.token_urlsafe(40) + '\n')
    wp(site, ['plugin', 'activate', 'woocommerce', 'woocommerce-subscriptions'])
    wp(site, ['option', 'update', 'timezone_string', 'Europe/Brussels'])
    wp(site, ['option', 'update', 'woocommerce_currency', 'EUR'])
    wp(site, ['option', 'update', 'woocommerce_custom_orders_table_data_sync_enabled', 'no'])
    wp(site, ['option', 'update', 'woocommerce_custom_orders_table_enabled', 'yes' if storage == 'hpos' else 'no'])
    result = wp(site, ['eval-file', str(BASE / 'scenario.php'), '--use-include'], timeout=600)
    lines = [row[9:] for row in result.stdout.splitlines() if row.startswith('C05_JSON=')]
    assert len(lines) == 1, result.stdout[-2000:]
    value = json.loads(lines[0])
    check(storage + ':scenario', value['failed'] == 0, value)
    check(storage + ':storage', value['versions']['hpos'] == (storage == 'hpos'), value['versions'])
    return value


def main():
    database = None
    result = {'scope': 'C05 synthetic manual renewals, not bank payments or production integration', 'runs': []}
    try:
        pathlib.Path('/scratch').mkdir(exist_ok=False)
        pathlib.Path('/report').mkdir(exist_ok=True)
        isolation()
        command(['mariadb-install-db', '--datadir=/scratch/mysql', '--auth-root-authentication-method=normal', '--skip-test-db', '--user=root'])
        database = subprocess.Popen(['mariadbd', '--user=root', '--datadir=/scratch/mysql', '--socket=/scratch/mariadb.sock',
                                     '--skip-networking', '--skip-log-bin', '--pid-file=/scratch/mariadb.pid', '--log-error=/scratch/mariadb.log'],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(150):
            if command(['mariadb-admin', '--socket=/scratch/mariadb.sock', '--user=root', 'ping'], check=False, timeout=5).returncode == 0:
                break
            if database.poll() is not None:
                raise RuntimeError('Synthetic DB failed to start')
            time.sleep(.2)
        else:
            raise RuntimeError('Synthetic DB readiness timeout')
        for storage in ('classic', 'hpos'):
            result['runs'].append(install(storage))
        isolation()
    except Exception as error:
        result['error'] = {'class': type(error).__name__, 'message': str(error),
                           'frames': [{'file': pathlib.Path(f.filename).name, 'line': f.lineno} for f in traceback.extract_tb(error.__traceback__)]}
    finally:
        if database:
            database.terminate()
            database.wait(timeout=30)
        result['checks'] = CHECKS
        result['exit_code'] = int('error' in result or any(not c['pass'] for c in CHECKS))
        REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'exit_code': result['exit_code'], 'runs': len(result['runs']), 'error': result.get('error')}, ensure_ascii=False))
    return result['exit_code']


if __name__ == '__main__':
    raise SystemExit(main())
