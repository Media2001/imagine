"""Request validation and trusted adapters (no imports of archive PHP)."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

from worker import PROTOCOL, ROOT, SOCKET, WORKFLOW, TRUSTED, Refusal, read_archive, sql_plan

STATE = ROOT / '.staging-worker.json'
CHECKS = ('emails', 'service_keys', 'payment_ids', 'mail_blocked', 'subscriptions_staging',
          'unknown_tables_resolved', 'production_refused', 'imported_code_not_loaded')


def validate(r, stage):
    if not isinstance(r, dict) or r.get('protocol') != PROTOCOL or r.get('stage') != stage:
        raise Refusal('REQUEST_PROTOCOL')
    if r.get('environment') != 'staging' or r.get('wordpress_path') != '/var/www/html':
        raise Refusal('REQUEST_CONTEXT')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,62}', r.get('slug', '')):
        raise Refusal('REQUEST_SLUG')
    db = r.get('database', {})
    if (db.get('socket') != SOCKET or db.get('host') != 'localhost' or db.get('user') != 'wp'
            or not re.fullmatch(r'[a-zA-Z0-9_]+_(?:staging|test)', db.get('name', ''))
            or not isinstance(db.get('password'), str) or not db['password'] or len(db['password']) > 128):
        raise Refusal('REQUEST_DATABASE')
    target, prod = urlsplit(r.get('staging_url', '')), urlsplit(r.get('production_url', ''))
    hosts = r.get('production_hosts')
    if (target.scheme not in ('http', 'https') or prod.scheme not in ('http', 'https')
            or not target.hostname or not prod.hostname or target.username or target.password
            or prod.username or prod.password or target.path or target.query or target.fragment
            or not re.fullmatch(r'localhost|[a-z0-9.-]+\.(?:test|localhost|invalid)', target.hostname)
            or not isinstance(hosts, list) or not hosts or len(hosts) > 64
            or any(not isinstance(h, str) or not re.fullmatch(r'[a-z0-9.-]+', h) for h in hosts)
            or prod.hostname not in hosts or target.hostname in hosts):
        raise Refusal('REQUEST_TARGET')
    if stage == 'importer' and r.get('archive') != '/input/source.wpress':
        raise Refusal('REQUEST_ARCHIVE')
    if stage == 'anonymiser':
        admin = r.get('admin', {})
        password = admin.get('password', '')
        if (admin.get('login') != 'imagine-test-admin' or not isinstance(password, str)
                or not 20 <= len(password.encode()) <= 72 or any(c in password for c in '\n\r\0')):
            raise Refusal('REQUEST_ADMIN')
    elif 'admin' in r:
        raise Refusal('REQUEST_ADMIN')


def confined():
    if os.geteuid() != 33 or set(p.name for p in Path('/sys/class/net').iterdir()) != {'lo'}:
        raise Refusal('WORKER_ISOLATION')
    for name in ('tcp', 'tcp6', 'udp', 'udp6'):
        if len(Path('/proc/net/' + name).read_text().splitlines()) > 1:
            raise Refusal('WORKER_NETWORK_SOCKET')


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def signature(r):
    return hashlib.sha256(json.dumps({k: r[k] for k in ('slug', 'staging_url', 'production_hosts')}, sort_keys=True).encode()).hexdigest()


def inventory():
    out = {}
    for p in ROOT.rglob('*'):
        if p.is_symlink() or (not p.is_dir() and not p.is_file()):
            raise Refusal('COPY_INVENTORY')
        if p.is_file() and p != STATE:
            out[p.relative_to(ROOT).as_posix()] = digest(p)
    return out


def save(s):
    STATE.write_text(json.dumps(s, sort_keys=True))
    os.chmod(STATE, 0o600)


def load(r):
    if STATE.is_symlink():
        raise Refusal('COPY_STATE')
    s = json.loads(STATE.read_text())
    if s['signature'] != signature(r) or s['files'] != inventory():
        raise Refusal('COPY_DRIFT')
    return s


def run_php(script, r, *, stdin=None, args=(), negative_report=False):
    payload = json.dumps(r).encode()
    if len(payload) > 8192:
        raise Refusal('REQUEST_LIMIT')
    rd, wr = os.pipe()
    try:
        # The request stays in an anonymous kernel pipe; no password in argv/env/disk.
        os.write(wr, payload)
        os.close(wr); wr = -1
        env = {'PATH': '/usr/bin:/bin', 'WP_ENVIRONMENT_TYPE': 'staging',
               'STAGING_REQUEST_FD': str(rd)}
        p = subprocess.run(['php', '-d', 'display_errors=0', '-d', 'log_errors=0', str(script), *args],
                           input=stdin, capture_output=True, pass_fds=(rd,), env=env, timeout=300)
        if len(p.stdout) > 16384:
            raise Refusal('DATA_REPORT_LIMIT')
        try:
            report = json.loads(p.stdout)
        except (ValueError, UnicodeError):
            raise Refusal('DATA_REPORT_INVALID') from None
        if negative_report and isinstance(report, dict) and type(report.get('ok')) is bool:
            if p.returncode == 0 or report['ok'] is False:
                return report
        if p.returncode or report.get('ok') is not True:
            raise Refusal('DATA_REFUSED')
        return report
    finally:
        os.close(rd)
        if wr >= 0:
            os.close(wr)


def assets():
    manifest = json.loads((TRUSTED / 'assets/manifest.json').read_text())
    for key, value in manifest.items():
        if (not re.fullmatch(r'[a-z][a-z0-9_-]*', key) or not isinstance(value, dict)
                or not re.fullmatch(r'[a-zA-Z0-9_.-]+\.zip', value.get('file', ''))
                or not re.fullmatch(r'[a-f0-9]{64}', value.get('sha256', ''))):
            raise Refusal('ASSET_MANIFEST')
        p = TRUSTED / 'assets' / value['file']
        if p.is_symlink() or digest(p) != value['sha256']:
            raise Refusal('ASSET_HASH')
    return manifest


def unpack_asset(key, destination):
    import zipfile
    manifest = assets()
    if key not in manifest:
        raise Refusal('LICENSE_SUBSCRIPTIONS_MISSING' if key == 'subscriptions' else 'ASSET_' + key.upper() + '_MISSING')
    with zipfile.ZipFile(TRUSTED / 'assets' / manifest[key]['file']) as z:
        entries = z.infolist()
        if len(entries) > 50000 or sum(e.file_size for e in entries) > 512 * 1024 * 1024:
            raise Refusal('ASSET_LIMIT')
        seen = set()
        for e in entries:
            parts = e.filename.rstrip('/').split('/')
            mode = e.external_attr >> 16
            if (any(p in ('', '.', '..') for p in parts) or e.filename.startswith('/')
                    or '\\' in e.filename or ':' in e.filename or mode & 0o170000 not in (0, 0o040000, 0o100000)
                    or e.filename.casefold() in seen):
                raise Refusal('ASSET_PATH')
            seen.add(e.filename.casefold())
        z.extractall(destination)


def config(r, prefix):
    settings = dict(database=r['database'], prefix=prefix, salts=base64.b64encode(os.urandom(64)).decode())
    encoded = base64.b64encode(json.dumps(settings).encode()).decode()
    return "<?php\n$c=json_decode(base64_decode('" + encoded + "'),true);\n" + """
define('DB_NAME',$c['database']['name']); define('DB_USER',$c['database']['user']);
define('DB_PASSWORD',$c['database']['password']); define('DB_HOST','localhost:/run/mysqld/mysqld.sock');
define('DB_CHARSET','utf8mb4'); define('DB_COLLATE','');
foreach(['AUTH_KEY','SECURE_AUTH_KEY','LOGGED_IN_KEY','NONCE_KEY','AUTH_SALT','SECURE_AUTH_SALT','LOGGED_IN_SALT','NONCE_SALT'] as $k) define($k,hash('sha256',$k.$c['salts']));
$table_prefix=$c['prefix']; unset($c);
define('WP_ENVIRONMENT_TYPE','staging'); define('DISABLE_WP_CRON',true);
define('AUTOMATIC_UPDATER_DISABLED',true); define('DISALLOW_FILE_MODS',true); define('DISALLOW_FILE_EDIT',true);
define('WP_DEBUG',false); define('WP_HTTP_BLOCK_EXTERNAL',true); define('WP_AUTO_UPDATE_CORE',false);
define('ABSPATH',__DIR__.'/'); require_once ABSPATH.'wp-settings.php';
"""


def importer(r):
    if list(ROOT.iterdir()):
        raise Refusal('FRESH_COPY_REQUIRED')
    archive = Path('/input/source.wpress')
    if archive.is_symlink() or not archive.is_file():
        raise Refusal('ARCHIVE_TYPE')
    with archive.open('rb') as f:
        sql, count = read_archive(f)
    try:
        plan = sql_plan(sql)
    except (IndexError, ValueError, UnicodeError):
        raise Refusal('SQL_REFUSED') from None
    # Only image-approved code is copied. No archive file, media, config or plugin survives.
    unpack_asset('wordpress', ROOT)
    core = ROOT / 'wordpress'
    for p in core.iterdir():
        shutil.move(str(p), ROOT / p.name)
    core.rmdir()
    shutil.rmtree(ROOT / 'wp-content/plugins')
    (ROOT / 'wp-content/plugins').mkdir()
    for key in ('woocommerce', 'subscriptions', 'memberships'):
        if key in assets():
            unpack_asset(key, ROOT / 'wp-content/plugins')
    # wp-config-sample is not a runtime configuration.
    (ROOT / 'wp-config-sample.php').unlink(missing_ok=True)
    (ROOT / 'wp-config.php').write_text(config(r, plan['prefix']))
    os.chmod(ROOT / 'wp-config.php', 0o600)
    (ROOT / '.imagine-staging-offline').write_bytes(b'OFFLINE_COPY\n')
    request = dict(r, sql_plan=plan)
    run_php(TRUSTED / 'database.php', request)
    s = dict(signature=signature(r), prefix=plan['prefix'], phases=['importer'], files=inventory())
    save(s)
    return {'entries_discarded': count - 1}


def adapt(r):
    stage = r['stage']
    s = load(r)
    required = {'neutraliser': 'importer', 'anonymiser': 'neutraliser', 'verifier': 'anonymiser',
                'bascule': 'verifier', 'novamira': 'bascule'}[stage]
    if required not in s['phases']:
        raise Refusal('STAGE_ORDER')
    request = dict(r, prefix=s['prefix'])
    if stage in ('neutraliser', 'anonymiser', 'verifier'):
        # The native probe determines whether Subscriptions is PRESENT. Absence is
        # not a failed staging mode, nor a claim of licensed-plugin acceptance.
        native_report = run_php(WORKFLOW / 'staging' / stage, request,
                stdin=(r['admin']['password'] + '\n').encode() if stage == 'anonymiser' else b'',
                args=('--worker-bridge', str(TRUSTED / 'worker-bridge.php')),
                negative_report=stage == 'verifier')
        # Native data scripts only add/replace the single reviewed safety MU plugin.
        expected = dict(s['files'])
        expected['wp-content/mu-plugins/000-imagine-staging-safety.php'] = digest(WORKFLOW / 'staging/mu-plugins/000-imagine-staging-safety.php')
        if inventory() != expected:
            raise Refusal('DATA_FILES_DRIFT')
        s['files'] = expected
    elif stage == 'bascule':
        # Empty numbered manifest is valid. All output remains private and is discarded.
        p = subprocess.run(['bash', str(WORKFLOW / 'bascule/lancer')], input=b'', capture_output=True,
                           timeout=300, env={'PATH':'/usr/bin:/bin','WP_ENVIRONMENT_TYPE':'staging'}, cwd=ROOT)
        if p.returncode:
            raise Refusal('BASCULE_REFUSED')
        # Changed code cannot become trusted merely because a bascule returned zero.
        if inventory() != s['files']:
            raise Refusal('BASCULE_CODE_REVIEW_REQUIRED')
    elif stage == 'novamira':
        for key in ('novamira', 'novamira-pro'):
            if key not in assets():
                raise Refusal('NOVAMIRA_APPROVED_ASSETS_MISSING')
        # The current native verifier rejects non-Woo active_plugins and unknown options.
        # Do not weaken its catalogue or issue a fake activation receipt.
        raise Refusal('NOVAMIRA_NATIVE_VERIFIER_CONTRACT_BLOCKED')
    if stage != 'verifier' or native_report.get('ok') is True:
        s['phases'].append(stage)
        save(s)
    if stage == 'verifier':
        version_text = (ROOT / 'wp-includes/version.php').read_text()
        match = re.search(r"\$wp_version\s*=\s*'([0-9]+\.[0-9]+(?:\.[0-9]+)?)';", version_text)
        if not match or tuple(map(int, match[1].split('.')[:2])) < (6, 9):
            raise Refusal('WORDPRESS_VERSION')
        ok = native_report.get('ok') is True
        # An all-true map is issued only after the real native verifier succeeded,
        # including its deferred runtime callback and post-bootstrap rescan.
        return dict(ok=ok, wordpress_version=match[1], checks={k: ok for k in CHECKS},
                    **{k: native_report[k] for k in ('issues', 'warnings', 'unknown_tables',
                        'unknown_post_types', 'disabled_plugins') if k in native_report})
    return {}


def main(stage):
    try:
        if sys.argv[1:] != ['--request-stdin']:
            raise Refusal('REQUEST_ARGUMENTS')
        raw = sys.stdin.buffer.read(16385)
        if len(raw) > 16384:
            raise Refusal('REQUEST_LIMIT')
        r = json.loads(raw)
        validate(r, stage)
        confined()
        detail = importer(r) if stage == 'importer' else adapt(r)
        response = dict(protocol=PROTOCOL, stage=stage, **detail)
        response.setdefault('ok', True)
        print(json.dumps(response))
        return 0
    except Refusal as e:
        reason = str(e)
        if not re.fullmatch(r'[A-Z0-9_]{1,80}', reason):
            reason = 'WORKER_REFUSED'
    except Exception:
        reason = 'WORKER_REFUSED'
    print(json.dumps(dict(protocol=PROTOCOL, stage=stage, ok=False, reason=reason)))
    return 78
