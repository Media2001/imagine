"""Qualification 6.9.1 only: public Woo preparation and invented fixture."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import secrets
import shutil
import sys
import zipfile


def public_woo(core, php='8.2'):
    from core_source import download, numeric, zip_payload
    api_url = 'https://api.wordpress.org/plugins/info/1.2/?action=plugin_information&request[slug]=woocommerce&request[fields][versions]=true'
    raw = download(api_url, 2 * 1024 * 1024)
    versions = json.loads(raw)['versions']
    stable = sorted((v for v in versions if re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', v)), key=numeric, reverse=True)
    checked = []
    for version in stable:
        url = 'https://plugins.svn.wordpress.org/woocommerce/tags/' + version + '/woocommerce.php'
        header = download(url, 4 * 1024 * 1024)
        text = header[:8192].decode()
        minima = {}
        for field in ('Requires at least', 'Requires PHP'):
            minima[field] = re.search(re.escape(field) + r':\s*([0-9.]+)', text)[1]
        compatible = numeric(minima['Requires at least']) <= numeric(core) and numeric(minima['Requires PHP']) <= numeric(php)
        checked.append({'version': version, 'url': url, 'header_sha256': hashlib.sha256(header).hexdigest(),
                        'requires_wordpress': minima['Requires at least'], 'requires_php': minima['Requires PHP'], 'compatible': compatible})
        if not compatible:
            continue
        url = 'https://downloads.wordpress.org/plugin/woocommerce.' + version + '.zip'
        raw = download(url)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            actual = archive.read('woocommerce/woocommerce.php')[:8192].decode()
        if not re.search(r'Version:\s*' + re.escape(version) + r'\s*$', actual, re.M):
            raise RuntimeError('WOO_VERSION_REFUSED')
        for field, minimum in minima.items():
            if not re.search(re.escape(field) + r':\s*' + re.escape(minimum) + r'\s*$', actual, re.M):
                raise RuntimeError('WOO_HEADER_MISMATCH')
        payload, files = zip_payload(raw, 'woocommerce', 'opt/woocommerce/woocommerce')
        return payload, {'url': url, 'version': version, 'sha256': hashlib.sha256(raw).hexdigest(),
                         'files': files, 'selection_api': api_url, 'checked_newest_first': checked,
                         'only_for_synthetic_fixture_not_import': True}
    raise RuntimeError('NO_PUBLIC_COMPATIBLE_WOO')


def fixture(storage, kind):
    # Only called inside the owned network-none runner.
    sys.path.insert(0, '/opt/court')
    sys.path.insert(0, '/opt/e2e')
    import inside as base
    import inside_commercial as commercial
    from prepare_publication import write_archive
    base.isolation()
    base.database_start()
    database = 'imagine_e2e_' + storage + '_test'
    base.command(['mariadb', '--socket=' + base.SOCKET, '--user=root', '-e', 'CREATE DATABASE ' + database])
    site = Path('/scratch/site-' + storage)
    shutil.copytree('/opt/wordpress/wordpress', site)
    (site / 'wp-content/plugins').mkdir(parents=True)
    shutil.copytree('/opt/woocommerce/woocommerce', site / 'wp-content/plugins/woocommerce')
    config = """<?php
    define('DB_NAME', '%s'); define('DB_USER','root'); define('DB_PASSWORD','');
    define('DB_HOST','localhost:/scratch/mariadb.sock'); define('DB_CHARSET','utf8mb4');define('DB_COLLATE','');
    define('WP_ENVIRONMENT_TYPE','staging');define('WP_HTTP_BLOCK_EXTERNAL',true);define('DISABLE_WP_CRON',true);
    define('AUTOMATIC_UPDATER_DISABLED',true);define('WP_AUTO_UPDATE_CORE',false);define('WP_DEBUG',false);
    $table_prefix='wp_';define('ABSPATH',__DIR__.'/');require_once ABSPATH.'wp-settings.php';
    """ % database
    (site / 'wp-config.php').write_text(config)
    base.wp(site, ['core', 'install', '--url=https://fixture.synthetic.test', '--title=Fiction 6.9.1',
                   '--admin_user=fiction-admin', '--admin_email=fiction-admin@example.org', '--skip-email', '--prompt=admin_password'],
            input_text=secrets.token_urlsafe(40) + '\n')
    base.wp(site, ['plugin', 'activate', 'woocommerce'])
    base.wp(site, ['option', 'update', 'woocommerce_custom_orders_table_data_sync_enabled', 'no'])
    base.wp(site, ['option', 'update', 'woocommerce_custom_orders_table_enabled', 'yes' if storage == 'hpos' else 'no'])
    base.wp(site, ['eval-file', '/opt/e2e/fixture.php'])
    # Memberships package is independently compatible; never install incompatible Subscriptions.
    package = Path('/opt/e2e/woocommerce-memberships.zip')
    assert hashlib.sha256(package.read_bytes()).hexdigest() == base.LICENSED[package.name]
    with zipfile.ZipFile(package) as archive:
        for entry in archive.infolist():
            parts = entry.filename.rstrip('/').split('/')
            assert parts[0] == 'woocommerce-memberships' and not any(p in ('', '.', '..') for p in parts)
            assert not any(c in entry.filename for c in '\\:')
            assert entry.external_attr >> 16 & 0o170000 in (0, 0o040000, 0o100000)
        archive.extractall(site / 'wp-content/plugins')
    base.wp(site, ['plugin', 'activate', 'woocommerce-memberships'])
    cases = Path('/opt/e2e/cases.php')
    cases.write_text(cases.read_text().replace('@invented.invalid', '@example.org'))
    with contextlib.redirect_stdout(io.StringIO()):
        commercial.case(site, 'seed')
        before = commercial.case(site, 'snapshot')
        rights = commercial.case(site, 'rights')
    orders = base.wp_json(site, 'snapshot.php')['orders']
    assert len(orders) == 30
    assert rights['restricted'] and all(v['private'] is (k == 'active') and v['public'] for k, v in rights['rights'].items())
    assert all(v is (k == 'active') for k, v in rights['shortcodes'].items())
    theme = site / 'wp-content/themes/a01-fiction'
    theme.mkdir(parents=True)
    (theme / 'style.css').write_text('/*\nTheme Name: A01 Fiction Only\n*/\n')
    (theme / 'index.php').write_text('<?php echo "A01_FICTION_PUBLICATION_OK";')
    base.wp(site, ['theme', 'activate', 'a01-fiction'])
    base.wp(site, ['option', 'update', 'imagine_publication_setting', '{"layout":"fiction","quantity":7}', '--format=json'])
    base.wp(site, ['option', 'update', 'imagine_a01_69_fixture', 'yes'])
    uploads = site / 'wp-content/uploads'
    uploads.mkdir(exist_ok=True)
    (uploads / 'a01-fictitious-media.txt').write_text('Invented media must survive exactly.\n')
    warning = site / 'wp-content/plugins/a01-warning'
    warning.mkdir()
    # Inert fixture only; inactive to avoid claiming activation guard bypass.
    (warning / 'a01-warning.php').write_text('<?php\n/*\nPlugin Name: A01 fictitious incompatible header\nVersion: 1.0\nRequires at least: 99.0\nRequires PHP: 99.0\n*/\n')
    mu = site / 'wp-content/mu-plugins'
    mu.mkdir(exist_ok=True)
    if kind == 'secret':
        (mu / 'a01-fiction-persistent-key.php').write_text("<?php add_action('init', static function (): void { update_option('a01_fiction_residual', '" + 'sk_' + "live_A01_FICTION_NOT_A_CREDENTIAL'); });")
    base.command(['mariadb', '--socket=' + base.SOCKET, '--user=root', database, '-e',
                  'CREATE TABLE wp_a01_engine_probe (id bigint NOT NULL PRIMARY KEY, flag int) ENGINE=MyISAM; INSERT INTO wp_a01_engine_probe VALUES (1,7);'])
    if kind == 'personal':
        base.command(['mariadb', '--socket=' + base.SOCKET, '--user=root', database, '-e',
                      "CREATE TABLE wp_a01_unresolved_people (id bigint NOT NULL PRIMARY KEY, email varchar(191)) ENGINE=InnoDB; INSERT INTO wp_a01_unresolved_people VALUES (1,'fiction@example.org');"])
    plugins = json.loads(base.wp(site, ['option', 'get', 'active_plugins', '--format=json']).stdout)
    sql = base.command(['php', '/opt/court/export.php'], env={'E2E_DATABASE': database}).stdout.encode()
    archive = Path('/scratch/fiction.wpress')
    write_archive(archive, site, sql)
    receipt = {'fixture_only': True, 'storage': storage, 'trapped': kind == 'secret',
               'unresolved_personal_table_canary': kind == 'personal', 'myisam_table': 'wp_a01_engine_probe',
               'persistent_service_key_canary_in_archived_php': kind == 'secret',
               'versions': before['versions'], 'business': before['business'], 'orders': orders,
               'membership': before['membership'], 'rules_sha256': before['rules_sha256'],
               'rights': rights, 'plugins': plugins, 'theme': 'a01-fiction',
               'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'archive_bytes': archive.stat().st_size,
               'source_files': {p.relative_to(site / 'wp-content').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (site / 'wp-content').rglob('*') if p.is_file()},
               'subscriptions_691': 'NOT_TESTED: only available 9.4.1 requires WP 7.0 / Woo 11.1; prior 7.0.9 qualification retained',
               'memberships_691': 'actual API and restrict-shortcode before/after; no license/account connection'}
    Path('/report/fixture.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps({'fixture_only': True, 'storage': storage, 'trap': kind}))


if __name__ == '__main__':
    fixture(sys.argv[1], sys.argv[2])
