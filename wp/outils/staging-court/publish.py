"""Standalone A-01 publication: normal named-test API, offline data, no agent access."""
import argparse
import datetime
import getpass
import hashlib
import io
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tarfile
import time
import uuid

sys.dont_write_bytecode = True
if not __debug__:
    raise SystemExit('PYTHON_OPTIMIZATION_REFUSED')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as offline_runner
from publication import guarded_publish, validate_name

ROOT = HERE.parents[2]
IMAGE = 'sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2'
LABEL = 'org.imagine.a01-publication'
DOCKER = offline_runner.DOCKER
WSL = ['wsl.exe', '-d', 'Ubuntu', '--'] if os.name == 'nt' else []


def call(args, data=None, check=True, timeout=600):
    p = subprocess.run(DOCKER + args, input=data, capture_output=True, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError('DOCKER_' + args[0].upper() + '_REFUSED')
    return p


def wsl_python(code, data=None):
    # Stdin transport avoids Windows/WSL quote and newline rewriting entirely.
    program = 'import io,sys\nsys.stdin=io.StringIO(' + repr((data or b'{}').decode()) + ')\n' + code
    p = subprocess.run(WSL + ['python3', '-'], input=program.encode(), capture_output=True, timeout=60)
    if p.returncode:
        raise RuntimeError('WSL_TRANSPORT_REFUSED')
    return json.loads(p.stdout)


def api(method, path, payload=None):
    if path not in ('/api/sites', '/api/health'):
        match = re.fullmatch(r'/api/sites/(imagine-test-[a-z0-9-]+)(?:/(start|stop))?', path)
        if not match:
            raise RuntimeError('API_SCOPE_REFUSED')
        validate_name(match[1])
    if path == '/api/sites' and method != 'POST':
        raise RuntimeError('SITE_LIST_REFUSED')
    code = '''import json,sys,urllib.request,urllib.error
v=json.load(sys.stdin)
r=urllib.request.Request('http://127.0.0.1:7000'+v['path'], data=json.dumps(v['payload']).encode() if v['payload'] is not None else None, method=v['method'], headers={'Content-Type':'application/json'})
try:
 with urllib.request.urlopen(r,timeout=45) as p:
  raw=p.read(); print(json.dumps({'code':p.status,'body':json.loads(raw) if raw else None}))
except urllib.error.HTTPError as e:
 print(json.dumps({'code':e.code,'body':None}))
'''
    response = wsl_python(code, json.dumps({'method': method, 'path': path, 'payload': payload}).encode())
    if response['code'] not in (200, 201, 204, 404):
        raise RuntimeError('STAGING_API_REFUSED')
    return response


def inspect(name):
    return json.loads(call(['inspect', name]).stdout)[0]


def fresh_runner(name):
    info = json.loads(call(['image', 'inspect', IMAGE]).stdout)[0]
    if info['Config'].get('Volumes') or info['Config'].get('ExposedPorts'):
        raise RuntimeError('RUNNER_IMAGE_REFUSED')
    call(['create', '--pull', 'never', '--name', name, '--label', LABEL + '=true', '--network', 'none',
          '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--no-healthcheck',
          '--memory', '2g', '--cpus', '2', '--pids-limit', '256', '--log-driver', 'none',
          '--entrypoint', 'sleep', IMAGE, 'infinity'])
    info = inspect(name)
    assert info['Config']['Labels'].get(LABEL) == 'true'
    assert info['HostConfig']['NetworkMode'] == 'none' and not info['Mounts']
    assert not info['HostConfig'].get('PortBindings') and not info['HostConfig']['Privileged']
    call(['start', name])
    data, manifest = offline_runner.payload(True)
    call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/'], data)
    extras = [
        (HERE / 'publication_probe.php', 'opt/court/publication_probe.php'),
        (ROOT / 'wp/tests/a01-court/prepare_publication.py', 'opt/court/prepare_publication.py'),
        (ROOT / 'wp/tests/licensed-a01/inside-commercial.py', 'opt/e2e/inside_commercial.py'),
        (ROOT / 'wp/tests/licensed-a01/cases.php', 'opt/e2e/cases.php'),
    ]
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as tar:
        for source, target in extras:
            content = source.read_bytes()
            manifest[source.relative_to(ROOT).as_posix()] = hashlib.sha256(content).hexdigest()
            entry = tarfile.TarInfo(target); entry.size = len(content)
            tar.addfile(entry, io.BytesIO(content))
    call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/'], stream.getvalue())
    return manifest


def offline_isolation(name):
    info = inspect(name)
    assert info['Config']['Labels'].get(LABEL) == 'true'
    assert info['HostConfig']['NetworkMode'] == 'none' and not info['Mounts']
    assert not info['HostConfig'].get('PortBindings') and not info['HostConfig']['Privileged']
    assert not info['Config'].get('ExposedPorts') and not info['Config'].get('Volumes')
    assert 'ALL' in info['HostConfig']['CapDrop']
    assert any(v.startswith('no-new-privileges') for v in info['HostConfig']['SecurityOpt'])
    return {'network': 'none', 'mounts': [], 'ports': [], 'privileged': False,
            'cap_drop': info['HostConfig']['CapDrop'], 'no_new_privileges': True,
            'image_id': info['Image'], 'name': name}


def read_json(runner, path):
    return json.loads(call(['exec', runner, 'cat', path]).stdout)


def remove_owned(name):
    info = inspect(name)
    if info['Config']['Labels'].get(LABEL) != 'true':
        raise RuntimeError('OWNERSHIP_REFUSED')
    call(['rm', '-f', name])
    p = call(['inspect', name], check=False)
    if p.returncode == 0 or b'no such object' not in p.stderr.lower():
        raise RuntimeError('REMOVAL_NOT_PROVEN')
    return {'name': name, 'absent': True}


def stop_site(slug):
    validate_name(slug)
    api('POST', '/api/sites/' + slug + '/stop')
    value = api('GET', '/api/sites/' + slug)['body']
    assert value['status'] == 'stopped'
    for prefix in ('wp-', 'db-', 'nginx-'):
        assert not target_info(slug, prefix)['State']['Running']
    return {'slug': slug, 'status': 'stopped', 'all_three_containers_stopped': True}


def target_info(slug, prefix):
    validate_name(slug)
    info = inspect(prefix + slug)
    assert info['Config']['Labels'].get('staging-wp.site-slug') == slug
    return info


def inject(slug, runner, offline, target, helpers):
    """No WordPress executes here: stopped volumes, socket-only DB helper."""
    stop_site(slug)
    wp_info = target_info(slug, 'wp-')
    db_info = target_info(slug, 'db-')
    html = next(m for m in wp_info['Mounts'] if m['Destination'] == '/var/www/html')
    content = next(m for m in wp_info['Mounts'] if m['Destination'] == '/var/www/html/wp-content')
    db = next(m for m in db_info['Mounts'] if m['Destination'] == '/var/lib/mysql')
    assert html['Type'] == 'volume' and html['Name'] == 'wp-html-' + slug
    assert content['Type'] == db['Type'] == 'bind'
    assert content['Source'].endswith('/' + slug + '/wp-content')
    assert db['Source'].endswith('/' + slug + '/db')
    file_helper = slug + '-files'
    call(['create', '--pull', 'never', '--name', file_helper, '--label', LABEL + '=true',
          '--network', 'none', '--cap-drop', 'ALL', '--cap-add', 'CHOWN', '--cap-add', 'DAC_OVERRIDE', '--cap-add', 'FOWNER',
          '--security-opt', 'no-new-privileges', '--log-driver', 'none', '--entrypoint', 'sleep',
          '--mount', 'type=volume,source=' + html['Name'] + ',target=/target',
          '--mount', 'type=bind,source=' + content['Source'] + ',target=/target/wp-content', IMAGE, 'infinity'])
    helpers.append(file_helper)
    call(['start', file_helper])
    cleanup = '''import pathlib,shutil
root=pathlib.Path('/target')
for p in root.iterdir():
 if p.name=='wp-content':
  for child in p.iterdir():
   if child.is_dir() and not child.is_symlink(): shutil.rmtree(child)
   else: child.unlink()
 elif p.is_dir() and not p.is_symlink(): shutil.rmtree(p)
 else: p.unlink()
'''
    call(['exec', '-i', file_helper, 'python3', '-'], cleanup.encode())
    # Pipe the exact offline tree; neither SQL nor archives are written to the host.
    sender = subprocess.Popen(DOCKER + ['cp', runner + ':/scratch/a01-site/.', '-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    receiver = subprocess.run(DOCKER + ['exec', '-i', file_helper, 'tar', '--no-same-owner', '--no-overwrite-dir', '--touch', '-xf', '-', '-C', '/target'],
                              stdin=sender.stdout, capture_output=True, timeout=600)
    sender.stdout.close(); sender_error = sender.stderr.read(); sender.wait(timeout=60)
    if sender.returncode or receiver.returncode:
        diagnostic = {'sender_exit': sender.returncode, 'receiver_exit': receiver.returncode,
                      'sender_stderr_sha256': hashlib.sha256(sender_error).hexdigest(),
                      'receiver_stderr_sha256': hashlib.sha256(receiver.stderr).hexdigest()}
        print(json.dumps({'file_transfer_diagnostic': diagnostic}))
        raise RuntimeError('FILE_TRANSFER_REFUSED')
    config = '''<?php
declare(strict_types=1);
define('DB_NAME', getenv('WORDPRESS_DB_NAME'));
define('DB_USER', getenv('WORDPRESS_DB_USER'));
define('DB_PASSWORD', getenv('WORDPRESS_DB_PASSWORD'));
define('DB_HOST', getenv('WORDPRESS_DB_HOST'));
define('DB_CHARSET','utf8mb4'); define('DB_COLLATE','');
define('WP_ENVIRONMENT_TYPE','staging'); define('DISABLE_WP_CRON',true);
define('IMAGINE_STAGING_VERIFIED',true); define('WP_HTTP_BLOCK_EXTERNAL',true);
define('WP_ACCESSIBLE_HOSTS','*.wordpress.org,*.woocommerce.com');
define('AUTOMATIC_UPDATER_DISABLED',true); define('WP_AUTO_UPDATE_CORE',false);
define('DISALLOW_FILE_MODS',true); define('DISALLOW_FILE_EDIT',true);
define('WP_DEBUG',false); define('WP_MEMORY_LIMIT','256M');
$table_prefix=PREFIX;
define('ABSPATH',__DIR__.'/'); require_once ABSPATH.'wp-settings.php';
'''
    prefix = read_json(runner, '/scratch/a01-context.json')['prefix']
    assert re.fullmatch(r'[a-zA-Z0-9_]+_', prefix)
    config = config.replace('PREFIX', repr(prefix))
    salts = ''.join("define('" + key + "','" + secrets.token_hex(48) + "');\n"
                    for key in ('AUTH_KEY', 'SECURE_AUTH_KEY', 'LOGGED_IN_KEY', 'NONCE_KEY',
                                'AUTH_SALT', 'SECURE_AUTH_SALT', 'LOGGED_IN_SALT', 'NONCE_SALT'))
    config = config.replace("define('ABSPATH'", salts + "define('ABSPATH'")
    call(['exec', '-i', file_helper, 'tee', '/target/wp-config.php'], config.encode())
    verify = '''import pathlib,hashlib,json,os
root=pathlib.Path('/target')
content=root/'wp-content'
files={p.relative_to(content).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in content.rglob('*') if p.is_file()}
print(json.dumps(files))
for p in root.rglob('*'):
 if p.is_symlink(): raise RuntimeError('SYMLINK_REFUSED')
 os.chown(p,33,33); os.chmod(p,0o755 if p.is_dir() else 0o644)
os.chown(root,33,33); os.chmod(root,0o755)
'''
    copied = json.loads(call(['exec', '-i', file_helper, 'python3', '-'], verify.encode()).stdout)
    assert copied == offline['files_after_cleanup']
    # Existing MariaDB image/data format, no network/ports, no credentials copied or displayed.
    db_helper = slug + '-database'
    call(['create', '--pull', 'never', '--name', db_helper, '--label', LABEL + '=true', '--network', 'none',
          '--user', 'mysql', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--no-healthcheck',
          '--log-driver', 'none', '--mount', 'type=bind,source=' + db['Source'] + ',target=/var/lib/mysql',
          '--entrypoint', 'sleep', db_info['Image'], 'infinity'])
    helpers.append(db_helper)
    call(['start', db_helper])
    call(['exec', '-d', db_helper, 'mariadbd', '--datadir=/var/lib/mysql', '--skip-networking', '--skip-grant-tables',
          '--socket=/tmp/a01.sock', '--pid-file=/tmp/a01.pid', '--log-error=/tmp/a01-db.log'])
    for _ in range(100):
        if call(['exec', db_helper, 'mariadb-admin', '--socket=/tmp/a01.sock', '--user=root', 'ping'], check=False).returncode == 0:
            break
        time.sleep(.2)
    else:
        raise RuntimeError('TARGET_SOCKET_DATABASE_REFUSED')
    call(['exec', db_helper, 'mariadb', '--socket=/tmp/a01.sock', '--user=root', '-e',
          'DROP DATABASE wordpress; CREATE DATABASE wordpress CHARACTER SET utf8mb4;'])
    dump = call(['exec', runner, 'mariadb-dump', '--socket=/scratch/mariadb.sock', '--user=root',
                 '--skip-comments', '--skip-dump-date', '--single-transaction', 'imagine_a01_staging']).stdout
    call(['exec', '-i', db_helper, 'mariadb', '--socket=/tmp/a01.sock', '--user=root', 'wordpress'], dump)
    assert re.fullmatch(r'http://[a-zA-Z0-9.-]+:[0-9]+', target)
    sql = "UPDATE `" + prefix + "options` SET option_value='" + target + "' WHERE option_name IN ('home','siteurl');"
    call(['exec', '-i', db_helper, 'mariadb', '--socket=/tmp/a01.sock', '--user=root', 'wordpress'], sql.encode())
    homes = call(['exec', '-i', db_helper, 'mariadb', '--socket=/tmp/a01.sock', '--user=root', '--skip-column-names', 'wordpress'],
                 ("SELECT option_value FROM `" + prefix + "options` WHERE option_name IN ('home','siteurl') ORDER BY option_name;").encode()).stdout.decode().splitlines()
    assert homes == [target, target]
    call(['exec', db_helper, 'mariadb-admin', '--socket=/tmp/a01.sock', '--user=root', 'shutdown'])
    remove_owned(db_helper); helpers.remove(db_helper)
    remove_owned(file_helper); helpers.remove(file_helper)
    return {'all_wp_content_hashes_equal': True, 'files': len(copied), 'home_siteurl_rewritten_offline': True,
            'socket_only_target_db_helper': True, 'no_credentials_copied': True}


def runtime_probe(slug, port):
    code = (ROOT / 'wp/outils/staging/runtime-probe.php').read_bytes() + b'\n' + (HERE / 'publication_probe.php').read_bytes().split(b'<?php', 1)[1].replace(b'declare(strict_types=1);', b'', 1).replace(b'namespace Imagine\\Staging;', b'', 1)
    result = call(['exec', '-i', 'wp-' + slug, 'php'], code, check=False)
    if result.returncode:
        return {'ok': False, 'issues': ['RUNTIME_PROBE_FAILED'], 'exit': result.returncode}
    lines = [l[9:] for l in result.stdout.decode().splitlines() if l.startswith('A01_JSON=')]
    if len(lines) != 1:
        return {'ok': False, 'issues': ['RUNTIME_REPORT_INVALID']}
    proof = json.loads(lines[0])
    http = wsl_python('''import json,sys,urllib.request,urllib.error,hashlib
v=json.load(sys.stdin)
try:
 r=urllib.request.Request('http://127.0.0.1:'+str(v['port'])+'/',headers={'Cache-Control':'no-cache'})
 with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(r,timeout=30) as p:
  b=p.read(4194304);print(json.dumps({'code':p.status,'body_sha256':hashlib.sha256(b).hexdigest(),'fiction_theme_marker':b'A01_FICTION_PUBLICATION_OK' in b,'redirected':p.url!=r.full_url}))
except Exception as e: print(json.dumps({'code':0,'error_class':type(e).__name__}))
''', json.dumps({'port': port}).encode())
    proof['http'] = http
    proof['ok'] = proof.get('ok') is True and http['code'] == 200 and not http.get('redirected', True)
    return proof


def main():
    parser = argparse.ArgumentParser(description='A-01 : archive → vérification hors ligne → publication dans un site imagine-test-…')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test-publication', action='store_true')
    group.add_argument('--archive')
    parser.add_argument('--operator-ced', action='store_true')
    parser.add_argument('--name')
    parser.add_argument('--production-url')
    parser.add_argument('--table-decisions')
    parser.add_argument('--php-version', default='8.2', choices=['8.2'])
    parser.add_argument('--case', choices=['classic', 'hpos', 'trap'], help='Rejeu synthétique ciblé, défaut les trois')
    args = parser.parse_args()
    if args.archive and not (args.operator_ced and args.name and args.production_url):
        parser.error('--operator-ced, --name imagine-test-… et --production-url requis')
    run_id = uuid.uuid4().hex[:12]
    out = ROOT / 'production/A-01/publication-22nov' / run_id
    out.mkdir(parents=True, exist_ok=False)
    cases = [('classic', False), ('hpos', False), ('classic', True)] if args.self_test_publication else [('operator', False)]
    if args.case:
        if not args.self_test_publication: parser.error('--case réservé aux tests fictifs')
        cases = [('classic' if args.case == 'trap' else args.case, args.case == 'trap')]
    result = {'status': 'FAIL', 'run_id': run_id, 'cases': [], 'cleanup': [],
              'no_real_archive': args.self_test_publication, 'no_agent_access_used': True,
              'tool_or_templates_modified': False,
              'post_verified_network_limit': 'WordPress HTTP filtering only; not a system firewall',
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        from publication_preflight import collect
        before = collect()['tool_source_manifest']
        result['tool_source_manifest'] = before
        for storage, trapped in cases:
            name = validate_name(args.name or ('imagine-test-a01-' + run_id + '-' + ('trap' if trapped else storage)))
            runner = 'imagine-a01-publication-' + uuid.uuid4().hex[:12]
            helpers = []; created = False; runner_created = False
            receipt = {'name': name, 'storage': storage, 'trapped': trapped, 'status': 'NOT_EXECUTED'}
            result['cases'].append(receipt)
            try:
                if api('GET', '/api/sites/' + name)['code'] != 404:
                    raise RuntimeError('FRESH_SITE_REQUIRED')
                # Normal API creation is explicitly authorized, automatic platform activation included.
                site = api('POST', '/api/sites', {'name': name, 'template_slug': 'sandbox-wp-minimal',
                            'php_version': args.php_version, 'client_name': None, 'target_domain': None})['body']
                created = True
                assert site['slug'] == name
                for _ in range(150):
                    site = api('GET', '/api/sites/' + name)['body']
                    if site['status'] not in ('creating', 'provisioning'):
                        break
                    time.sleep(2)
                if site['status'] != 'running':
                    raise RuntimeError('NORMAL_SITE_CREATION_REFUSED')
                receipt['normal_creation'] = {k: site[k] for k in ('slug', 'status', 'port', 'php_version', 'mcp_enabled', 'mcp_status')}
                receipt['stopped_before_import'] = stop_site(name)
                manifest = fresh_runner(runner); runner_created = True
                receipt['offline_isolation_before'] = offline_isolation(runner)
                lint = call(['exec', runner, 'php', '-l', '/opt/court/publication_probe.php'])
                receipt['new_php_lint'] = {'exit': lint.returncode, 'output_sha256': hashlib.sha256(lint.stdout + lint.stderr).hexdigest()}
                receipt['source_manifest'] = manifest
                request = {'target_url': 'http://localhost:' + str(site['port']),
                           'production_url': args.production_url or 'https://production.synthetic.invalid',
                           'password': getpass.getpass('Mot de passe neuf du compte test : ') if args.archive else secrets.token_urlsafe(40),
                           'decisions': json.loads(Path(args.table_decisions).read_text()) if args.table_decisions else {}}
                if args.self_test_publication:
                    for slug in ('woocommerce-memberships', 'woocommerce-subscriptions'):
                        call(['cp', '/home/ced/staging-wp/plugins/' + slug + '.zip', runner + ':/opt/e2e/' + slug + '.zip'])
                    p = call(['exec', runner, 'python3', '/opt/court/prepare_publication.py', storage,
                              'trapped' if trapped else 'clean'], check=False)
                    receipt['fixture_prepare_exit'] = p.returncode
                    if p.returncode:
                        receipt['fixture_output_sha256'] = hashlib.sha256(p.stdout + p.stderr).hexdigest()
                        # Only Python frame/class names, never raw output or row values.
                        raise RuntimeError('SYNTHETIC_FIXTURE_REFUSED')
                    fixture = read_json(runner, '/report/fixture.json')
                    receipt['fixture'] = fixture
                    request['decisions'] = {'wp_wc_email_unsubscribes': {'action': 'garder'}}
                    receipt['decisions_are_synthetic_not_Ced_approval'] = True
                    archive_path = '/scratch/fiction.wpress'
                else:
                    archive = Path(args.archive).resolve()
                    if not archive.is_file() or archive.is_symlink() or archive.suffix.lower() != '.wpress':
                        raise RuntimeError('ARCHIVE_REFUSED')
                    p = str(archive)
                    if os.name == 'nt': p = '/mnt/' + p[0].lower() + p[2:].replace('\\', '/')
                    call(['exec', runner, 'mkdir', '-p', '/input'])
                    call(['cp', p, runner + ':/input/source.wpress'])
                    archive_path = '/input/source.wpress'
                program = '''import json,sys
sys.path.insert(0,'/opt/court')
from inside import restore_and_verify, database_start
request=json.load(sys.stdin)
if request.pop('start_database'): database_start()
r=restore_and_verify(request.pop('archive'),request)
from pathlib import Path
Path('/report/offline.json').write_text(json.dumps(r))
print(json.dumps({'data_verified':r['data_verified']}))
'''
                request.update(start_database=not args.self_test_publication, archive=archive_path)
                input_program = 'import io,sys\nsys.stdin=io.StringIO(' + repr(json.dumps(request)) + ')\n' + program
                execution = call(['exec', '-i', runner, 'python3', '-'], input_program.encode(), check=False)
                del request['password']
                if execution.returncode:
                    receipt['restore_output_sha256'] = hashlib.sha256(execution.stdout + execution.stderr).hexdigest()
                    raise RuntimeError('OFFLINE_RESTORE_REFUSED')
                offline = read_json(runner, '/report/offline.json')
                receipt['offline_isolation_after'] = offline_isolation(runner)
                receipt['offline'] = offline
                if args.self_test_publication:
                    assert offline['restored_files_before_cleanup'] == fixture['source_files']
                    first = offline['restored_files_before_cleanup']; cleaned = offline['files_after_cleanup']
                    removed = sorted(set(first) - set(cleaned))
                    changed = [p for p in set(first) & set(cleaned) if first[p] != cleaned[p]]
                    assert not changed
                    assert all(p.endswith('.log') or p.startswith(('uploads/wc-logs/', 'cache/', 'ai1wm-backups/')) for p in removed)
                    receipt['archive_fidelity'] = {'all_restored_hashes_equal_source': True,
                        'retained_files_unchanged': True, 'expected_removed': removed,
                        'file_counts': {folder: {'before': sum(p.startswith(folder + '/') for p in first),
                                                'after': sum(p.startswith(folder + '/') for p in cleaned)}
                                        for folder in ('plugins', 'themes', 'uploads', 'mu-plugins')}}
                if trapped:
                    issues = offline['steps'][-1]['report'].get('issues', [])
                    assert not offline['data_verified'] and 'SECRET_OU_IDENTIFIANT' in issues
                injection = {}
                def do_inject():
                    injection.update(inject(name, runner, offline, site['url'], helpers))
                def do_start():
                    api('POST', '/api/sites/' + name + '/start')
                    assert api('GET', '/api/sites/' + name)['body']['status'] == 'running'
                    time.sleep(3)
                published = guarded_publish(offline, do_inject, do_start,
                                            lambda: runtime_probe(name, site['port']), lambda: stop_site(name))
                receipt['publication'] = published
                receipt['injection'] = injection
                if trapped:
                    assert published['status'] == 'REFUSED_OFFLINE' and not injection
                    receipt['refusal_stop_readback'] = stop_site(name)
                    stopped_http = wsl_python('''import json,sys,urllib.request
v=json.load(sys.stdin)
try:
 with urllib.request.build_opener(urllib.request.ProxyHandler({})).open('http://127.0.0.1:'+str(v['port'])+'/',timeout=5) as p: print(json.dumps({'reachable':True,'code':p.status}))
except Exception as e: print(json.dumps({'reachable':False,'error_class':type(e).__name__}))
''', json.dumps({'port': site['port']}).encode())
                    assert stopped_http['reachable'] is False
                    receipt['refused_http_readback'] = stopped_http
                    receipt['status'] = 'PASS'
                else:
                    assert published['full_staging_ready'] is True
                    if args.self_test_publication:
                        probe = published['probe']
                        assert probe['http']['fiction_theme_marker']
                        for key in ('business', 'membership', 'rules_sha256', 'plugins', 'theme'):
                            assert probe['fidelity'][key] == fixture[key], 'FIDELITY_' + key.upper()
                    marker = {'status': 'verified', 'run_id': run_id, 'site': name,
                              'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                              'report': str(out / 'result.json'), 'offline_verified': True, 'runtime_probe_passed': True,
                              'post_verified_network_limit': result['post_verified_network_limit']}
                    call(['exec', '-i', 'wp-' + name, 'tee', '/var/www/html/.imagine-staging-verified.json'], json.dumps(marker).encode())
                    assert read_json('wp-' + name, '/var/www/html/.imagine-staging-verified.json') == marker
                    receipt['verified_marker_readback'] = marker
                    receipt['api_status_readback'] = {k: api('GET', '/api/sites/' + name)['body'][k] for k in ('status', 'container_state')}
                    receipt['status'] = 'PASS'
                for rel, digest in manifest.items():
                    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest
            except Exception as exc:
                receipt['status'] = 'FAIL'
                receipt['error'] = str(exc) if re.fullmatch(r'[A-Z0-9_]{1,100}', str(exc)) else type(exc).__name__
                receipt['frames'] = [{'file': Path(f.filename).name, 'line': f.lineno, 'function': f.name}
                                     for f in __import__('traceback').extract_tb(exc.__traceback__)]
            finally:
                for helper in list(helpers): result['cleanup'].append(remove_owned(helper))
                if runner_created: result['cleanup'].append(remove_owned(runner))
                if created:
                    if args.self_test_publication:
                        stop_site(name)
                        api('DELETE', '/api/sites/' + name)
                        missing = api('GET', '/api/sites/' + name)['code'] == 404
                        absence = {}
                        for prefix in ('wp-', 'db-', 'nginx-'):
                            p = call(['inspect', prefix + name], check=False)
                            absence[prefix + name] = p.returncode != 0 and b'no such object' in p.stderr.lower()
                        assert missing and all(absence.values())
                        result['cleanup'].append({'site': name, 'api_absent': missing, 'containers_absent': absence})
                    elif receipt['status'] != 'PASS':
                        receipt['failure_stop_readback'] = stop_site(name)
                (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        after = collect()['tool_source_manifest']
        result['tool_sources_unchanged'] = before == after
        assert before == after
        result['status'] = 'PASS' if all(c['status'] == 'PASS' for c in result['cases']) else 'FAIL'
    except Exception as exc:
        result['blocker'] = str(exc) if re.fullmatch(r'[A-Z0-9_]{1,100}', str(exc)) else type(exc).__name__
    finally:
        result['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result['command_sources'] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in sorted(HERE.glob('*.py')) + sorted(HERE.glob('*.php'))}
        (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': result['status'], 'report': str(out / 'result.json')}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
