"""Offline archive -> faithful files -> native cleanup -> report. No web publication."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import time
from urllib.parse import urlsplit

from archive import Refusal, restore
from legacy_importer import sql_plan

BASE = Path('/opt/court')
SITE = Path('/scratch/a01-site')
DB = 'imagine_a01_staging'
SOCKET = '/scratch/mariadb.sock'


def command(args, *, data=None, env=None, check=True):
    p = subprocess.run(args, input=data, capture_output=True, env={**os.environ, **(env or {})}, timeout=300)
    if check and p.returncode:
        raise Refusal('COMMAND_REFUSED')
    return p


def database_start():
    Path('/scratch').mkdir(exist_ok=True)
    data = Path('/scratch/court-db')
    command(['mariadb-install-db', '--datadir=' + str(data), '--auth-root-authentication-method=normal',
             '--skip-test-db', '--user=root'])
    process = subprocess.Popen(['mariadbd', '--user=root', '--datadir=' + str(data), '--socket=' + SOCKET,
                                '--skip-networking', '--skip-log-bin', '--pid-file=/scratch/court.pid',
                                '--log-error=/scratch/court-db.log'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        if process.poll() is not None:
            raise Refusal('DATABASE_START_REFUSED')
        if command(['mariadb-admin', '--socket=' + SOCKET, '--user=root', 'ping'], check=False).returncode == 0:
            return process
        time.sleep(.1)
    raise Refusal('DATABASE_START_TIMEOUT')


def isolation():
    if {p.name for p in Path('/sys/class/net').iterdir()} != {'lo'}:
        raise Refusal('NETWORK_REFUSED')
    for name in ('tcp', 'tcp6'):
        if any(row.split()[3] == '0A' for row in Path('/proc/net/' + name).read_text().splitlines()[1:]):
            raise Refusal('LISTENER_REFUSED')


def manifest(root):
    result = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink() or (not p.is_dir() and not p.is_file()):
            raise Refusal('FILE_TYPE_REFUSED')
        if p.is_file():
            result[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def restore_and_verify(archive, request):
    isolation()
    if SITE.exists():
        raise Refusal('FRESH_SITE_REQUIRED')
    target = request['target_url']
    production = urlsplit(request['production_url'])
    url = urlsplit(target)
    if (url.scheme not in ('http', 'https') or not re.fullmatch(r'localhost|[a-z0-9.-]+\.(?:test|localhost|invalid)', url.hostname or '')
            or url.username or url.password or url.path or url.query or url.fragment
            or not production.hostname or production.hostname == url.hostname):
        raise Refusal('TARGET_REFUSED')
    if not isinstance(request.get('decisions', {}), dict):
        raise Refusal('DECISIONS_REFUSED')
    password = request['password']
    if not isinstance(password, str) or not 20 <= len(password.encode()) <= 72 or any(c in password for c in '\r\n\0'):
        raise Refusal('ADMIN_PASSWORD_REFUSED')
    # Restore the pinned core, but preserve ALL imported wp-content bytes until native cleanup.
    shutil.copytree('/opt/wordpress/wordpress', SITE)
    shutil.rmtree(SITE / 'wp-content')
    with Path(archive).open('rb') as stream:
        sql, package, count = restore(stream, SITE / 'wp-content')
    before = manifest(SITE / 'wp-content')
    plan = sql_plan(sql)
    prefix = plan['prefix']
    command(['mariadb', '--socket=' + SOCKET, '--user=root', '-e', 'CREATE DATABASE ' + DB])
    command(['mariadb', '--socket=' + SOCKET, '--user=root', DB],
            data=(';\n'.join(plan['statements']) + ';\n').encode())
    # Only target home/siteurl are rewritten before the native context guard. No WP bootstrap yet.
    update = "UPDATE `" + prefix + "options` SET option_value='" + target.replace("'", "''") + "' WHERE option_name IN ('home','siteurl');"
    command(['mariadb', '--socket=' + SOCKET, '--user=root', DB], data=update.encode())
    config = """<?php
    define('DB_NAME','imagine_a01_staging'); define('DB_USER','root'); define('DB_PASSWORD','');
    define('DB_HOST','localhost:/scratch/mariadb.sock'); define('DB_CHARSET','utf8mb4'); define('DB_COLLATE','');
    define('WP_ENVIRONMENT_TYPE','staging'); define('WP_HTTP_BLOCK_EXTERNAL',true);
    define('DISABLE_WP_CRON',true); define('AUTOMATIC_UPDATER_DISABLED',true); define('WP_AUTO_UPDATE_CORE',false);
    define('DISALLOW_FILE_MODS',true); define('DISALLOW_FILE_EDIT',true); define('WP_DEBUG',false);
    $table_prefix=PREFIX;
    define('ABSPATH',__DIR__.'/'); require_once ABSPATH.'wp-settings.php';
    """.replace('PREFIX', repr(prefix))
    (SITE / 'wp-config.php').write_text(config)
    os.chmod(SITE / 'wp-config.php', 0o600)
    (SITE / '.imagine-staging-offline').write_text('OFFLINE_COPY\n')
    context = {'environment': 'staging', 'isolated': True, 'restored': True, 'database': DB,
               'wp_path': str(SITE), 'target_url': target, 'production_hosts': [production.hostname],
               'prefix': prefix, 'table_decisions': request.get('decisions', {})}
    Path('/scratch/a01-context.json').write_text(json.dumps(context))
    steps = []
    report = {'ok': False, 'issues': ['NOT_VERIFIED']}
    for phase in ('neutraliser', 'anonymiser', 'verifier'):
        p = command(['php', '/subject/' + phase, '--worker-bridge', str(BASE / 'bridge.php')],
                    data=(password + '\n').encode() if phase == 'anonymiser' else b'',
                    env={'A01_CONTEXT': '/scratch/a01-context.json', 'WP_ENVIRONMENT_TYPE': 'staging'}, check=False)
        try:
            report = json.loads(p.stdout)
        except ValueError:
            report = {'ok': False, 'issues': ['REPORT_INVALID']}
        steps.append({'phase': phase, 'exit': p.returncode, 'report': report})
        if p.returncode or report.get('ok') is not True:
            break
    verified = len(steps) == 3 and all(step['exit'] == 0 for step in steps)
    result = {'status': 'verified-offline' if verified else 'imported', 'data_verified': verified,
              'steps': steps, 'archive_entries': count, 'restored_files_before_cleanup': before,
              'files_after_cleanup': manifest(SITE / 'wp-content'),
              'publication': 'NOT_IMPLEMENTED: no port or egress is opened; site remains stopped',
              'shared_tool_modified': False, 'no_Novamira': True}
    return result


def main():
    process = None
    output = {'status': 'refused', 'data_verified': False}
    try:
        isolation()
        request = json.loads(sys.stdin.buffer.read(16385))
        if len(json.dumps(request)) > 16384:
            raise Refusal('REQUEST_LIMIT')
        process = database_start()
        output = restore_and_verify('/input/source.wpress', request)
    except Exception as exc:
        tag = str(exc)
        output['issues'] = [tag if re.fullmatch(r'[A-Z0-9_]{1,80}', tag) else 'IMPORT_REFUSED']
    finally:
        if process:
            command(['mariadb-admin', '--socket=' + SOCKET, '--user=root', 'shutdown'], check=False)
            process.wait(timeout=30)
        Path('/report').mkdir(exist_ok=True)
        Path('/report/court.json').write_text(json.dumps(output, indent=2))
    print(json.dumps({'status': output['status'], 'data_verified': output['data_verified'], 'runtime': 'stopped'}))
    return 0 if output['data_verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
