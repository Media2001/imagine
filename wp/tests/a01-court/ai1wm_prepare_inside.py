"""Only synthetic site creation and real public extension export."""
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time


def call(args, data=None):
    p = subprocess.run(args, input=data, capture_output=True, timeout=1200)
    if p.returncode:
        sys.stderr.buffer.write(p.stderr[-4000:] + p.stdout[-2000:])
        raise RuntimeError('FIXTURE_COMMAND_FAILED:' + args[0])
    return p


Path('/scratch').mkdir(exist_ok=True)
Path('/report').mkdir(exist_ok=True)
assert shutil.disk_usage('/scratch').free > 8 * 1024**3
call(['mariadb-install-db', '--datadir=/scratch/db', '--auth-root-authentication-method=normal', '--skip-test-db', '--user=root'])
subprocess.Popen(['mariadbd', '--user=root', '--datadir=/scratch/db', '--socket=/scratch/mariadb.sock', '--skip-networking',
                  '--skip-log-bin', '--pid-file=/scratch/db.pid', '--log-error=/scratch/db.log'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(100):
    if subprocess.run(['mariadb-admin', '--socket=/scratch/mariadb.sock', '--user=root', 'ping'], capture_output=True).returncode == 0: break
    time.sleep(.2)
else: raise RuntimeError('FIXTURE_DB_FAILED')
site = Path('/scratch/imagine-test-a01-ai1wm-synthetic')
shutil.copytree('/opt/wordpress/wordpress', site)
shutil.copytree('/opt/public/all-in-one-wp-migration', site / 'wp-content/plugins/all-in-one-wp-migration')
(site / 'wp-config.php').write_text("""<?php
define('DB_NAME','imagine_ai1wm_fixture'); define('DB_USER','root'); define('DB_PASSWORD','');
define('DB_HOST','localhost:/scratch/mariadb.sock'); define('DB_CHARSET','utf8mb4'); define('DB_COLLATE','');
define('WP_ENVIRONMENT_TYPE','staging'); define('DISABLE_WP_CRON',true); define('WP_HTTP_BLOCK_EXTERNAL',true);
define('AUTOMATIC_UPDATER_DISABLED',true); define('WP_AUTO_UPDATE_CORE',false);
$table_prefix='wp_'; define('ABSPATH',__DIR__.'/'); require_once ABSPATH.'wp-settings.php';
""")
call(['mariadb', '--socket=/scratch/mariadb.sock', '--user=root', '-e', 'CREATE DATABASE imagine_ai1wm_fixture'])
def wp(args, data=None): return call(['wp', '--allow-root', '--path=' + str(site)] + args, data)
wp(['core', 'install', '--url=https://imagine-test-a01-ai1wm.invalid', '--title=FICTION ONLY', '--admin_user=fiction', '--admin_email=fiction@example.org', '--skip-email', '--prompt=admin_password'], (secrets.token_urlsafe(32) + '\n').encode())
wp(['plugin', 'activate', 'all-in-one-wp-migration'])
content = site / 'wp-content'
for path, data in {'uploads/2026/11/fixture.jpg': b'FICTION MEDIA', 'uploads/wpallexport/fiction.csv': b'FICTION EXPORT NOT TO READ',
                   'uploads/woocommerce_uploads/issue.pdf': b'%PDF FICTION', 'uploads/woocommerce_uploads/private.csv': b'FICTION CSV',
                   'uploads/simple-file-list/issue.jpg': b'FICTION IMAGE', 'uploads/simple-file-list/private.html': b'FICTION HTML',
                   'uploads/wc-logs/order.log': b'FICTION LOG', 'themes/fiction-backup.zip': b'FICTION ARCHIVE',
                   'mu-plugins/fiction.json': b'{"api_key":"FICTION_SITE_VALUE"}'}.items():
    p = content / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
wp(['eval-file', '/opt/fixture.php', 'small', '--use-include'])
wp(['eval-file', '/opt/fixture.php', 'grow', '--use-include'])
media = content / 'uploads/2026/11'
block = b'FICTION GENERATED MEDIA NO REAL DATA\n' * 1000
for i in range(32000):
    (media / ('generated-%05d.pdf' % i)).write_bytes(block)
print(json.dumps({'generated_media_files': 32000, 'generated_media_bytes': len(block) * 32000}), flush=True)
wp(['eval-file', '/opt/fixture.php', 'large', '--use-include'])
print('REAL_AI1WM_EXPORTS_READY', flush=True)
