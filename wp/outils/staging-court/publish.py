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
from core_source import prepare_core

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
        (HERE / 'script_capacity_probe.php', 'opt/court/script_capacity_probe.php'),
        (ROOT / 'wp/tests/a01-court/prepare_publication.py', 'opt/court/prepare_publication.py'),
        (ROOT / 'wp/tests/a01-court/qualification_69.py', 'opt/court/qualification_69.py'),
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


def runtime_core_preflight(runner, expected):
    """Read pinned core as data, before site creation, source access or PHP."""
    if not re.fullmatch(r'[0-9]+\.[0-9]+(?:\.[0-9]+)?', expected):
        raise RuntimeError('EXPECTED_CORE_VERSION_REFUSED')
    program = '''import json,re
from pathlib import Path
expected=EXPECTED_VERSION_TOKEN
matches=re.findall(r"^\\s*\\$wp_version\\s*=\\s*'([0-9]+\\.[0-9]+(?:\\.[0-9]+)?)';",Path('/opt/wordpress/wordpress/wp-includes/version.php').read_text(),re.M)
pinned=matches[0] if len(matches)==1 else None
print(json.dumps({'ok':pinned==expected,'stage':'core_preflight','expected':expected,'pinned':pinned,
 'code':'CORE_MATCH' if pinned==expected else ('PINNED_CORE_EXPECTED_VERSION_MISMATCH' if pinned else 'PINNED_CORE_VERSION_REFUSED')}))
'''.replace('EXPECTED_VERSION_TOKEN', repr(expected))
    return json.loads(call(['exec', '-i', runner, 'python3', '-'], program.encode()).stdout)


def archive_core_preflight(runner, archive, expected):
    """Read the validated manifest without restoring files, SQL or bootstrap."""
    program = '''import json,sys
sys.path.insert(0,'/opt/court')
from archive import restore,Refusal,ARCHIVE_REFUSALS
from core_source import select_version
archive_report={}
try:
 with open(ARCHIVE_TOKEN,'rb') as stream:
  sql,package,count=restore(stream,None,metadata_only=True,case_probe_root='/scratch',report=archive_report)
 version=select_version(package,EXPECTED_TOKEN)
 print(json.dumps({'ok':True,'source':version,'expected':EXPECTED_TOKEN,'entries':count,'metadata_only':True,'archive_report':archive_report}))
except Refusal as error:
 code=str(error)
 allowed=ARCHIVE_REFUSALS | {'SOURCE_CORE_METADATA_REFUSED','SOURCE_EXPECTED_CORE_VERSION_MISMATCH','EXPECTED_CORE_VERSION_REFUSED'}
 print(json.dumps({'ok':False,'stage':'archive_core_preflight','code':code if code in allowed else 'ARCHIVE_REFUSED',
 'detail':getattr(error,'detail',None) or {'code':code if code in allowed else 'ARCHIVE_REFUSED','count':1,'locations':[{'zone':'(metadonnees)','extension':'.json','count':1}]},
 'archive_report':archive_report,'core_versions':getattr(error,'core_versions',None),'metadata_only':True}))
'''.replace('ARCHIVE_TOKEN', repr(archive)).replace('EXPECTED_TOKEN', repr(expected))
    return json.loads(call(['exec', '-i', runner, 'python3', '-'], program.encode()).stdout)


def set_empty_runner_core(runner, payload, receipt):
    # No archive file is injected; network remains none throughout.
    program = "import pathlib,shutil\np=pathlib.Path('/opt/wordpress/wordpress')\nshutil.rmtree(p)\np.mkdir()\n"
    call(['exec', '-i', runner, 'python3', '-'], program.encode())
    call(['exec', '-i', runner, 'tar', '-xf', '-', '-C', '/'], payload)
    program = '''from pathlib import Path
import hashlib,json
root=Path('/opt/wordpress/wordpress')
files={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
print(json.dumps(files))
'''
    assert json.loads(call(['exec', '-i', runner, 'python3', '-'], program.encode()).stdout) == receipt['core_files']
    call(['exec', runner, 'mkdir', '-p', '/opt/wordpress/wordpress/wp-content'])
    proof = runtime_core_preflight(runner, receipt['version'])
    assert proof['ok'] is True
    return proof


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


def deleted_readback(slug):
    validate_name(slug)
    missing = api('GET', '/api/sites/' + slug)['code'] == 404
    containers = {}
    for prefix in ('wp-', 'db-', 'nginx-'):
        p = call(['inspect', prefix + slug], check=False)
        containers[prefix + slug] = p.returncode != 0 and b'no such object' in p.stderr.lower()
    volume = call(['volume', 'inspect', 'wp-html-' + slug], check=False)
    network = call(['network', 'inspect', 'site-net-' + slug], check=False)
    volume_absent = volume.returncode != 0 and b'no such volume' in volume.stderr.lower()
    network_absent = network.returncode != 0 and (b'not found' in network.stderr.lower() or b'no such network' in network.stderr.lower())
    program = 'from pathlib import Path\nimport json\nprint(json.dumps({"directory_absent":not Path(' + repr('/app/sites/' + slug) + ').exists()}))\n'
    directory_absent = json.loads(call(['exec', '-i', 'staging-wp-dashboard', 'python', '-'], program.encode()).stdout)['directory_absent']
    assert missing and all(containers.values()) and volume_absent and network_absent and directory_absent
    return {'site': slug, 'api_absent': missing, 'containers_absent': containers,
            'html_volume_absent': volume_absent, 'network_absent': network_absent, 'directory_absent': directory_absent}


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
    # Probe the actual mounted destination, not the runner or assumed OS.
    probe = (HERE / 'archive.py').read_bytes() + b"\nimport json\nprint(json.dumps({'case_sensitive':probe_case_sensitive('/target/wp-content')}))\n"
    target_case_sensitive = json.loads(call(['exec', '-i', file_helper, 'python3', '-'], probe).stdout)['case_sensitive']
    if not target_case_sensitive and 'ARCHIVE_PATH_CASE_ONLY' in offline.get('archive_report', {}).get('warnings', []):
        raise RuntimeError('ARCHIVE_CASE_INSENSITIVE_TARGET')
    # Install/read back the archive-selected core while target content is EMPTY.
    # Only after this receipt do the archived files and database enter this site.
    sender = subprocess.Popen(DOCKER + ['exec', runner, 'tar', '-cf', '-', '--exclude=./wp-content',
                              '--exclude=./wp-config.php', '-C', '/scratch/a01-site', '.'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    receiver = subprocess.run(DOCKER + ['exec', '-i', file_helper, 'tar', '--no-same-owner', '--touch', '-xf', '-', '-C', '/target'],
                              stdin=sender.stdout, capture_output=True, timeout=600)
    sender.stdout.close(); sender.stderr.read(); sender.wait(timeout=60)
    if sender.returncode or receiver.returncode:
        raise RuntimeError('EMPTY_TARGET_CORE_TRANSFER_REFUSED')
    core_check = '''from pathlib import Path
import json,re
root=Path('/target')
text=(root/'wp-includes/version.php').read_text()
versions=re.findall(r"^\\s*\\$wp_version\\s*=\\s*'([0-9]+\\.[0-9]+(?:\\.[0-9]+)?)';",text,re.M)
print(json.dumps({'version':versions[0] if len(versions)==1 else None,
                 'archive_content_absent':not any((root/'wp-content').iterdir())}))
'''
    empty_core = json.loads(call(['exec', '-i', file_helper, 'python3', '-'], core_check.encode()).stdout)
    assert empty_core['archive_content_absent'] is True
    assert empty_core['version'] == offline['core_versions']['source'] == offline['core_versions']['pinned']
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
            'target_case_sensitive': target_case_sensitive,
            'socket_only_target_db_helper': True, 'no_credentials_copied': True,
            'empty_target_core_before_archive_injection': empty_core}


def runtime_probe(slug, port, target):
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
    assigned = wsl_python('''import json,sys,urllib.request,hashlib
v=json.load(sys.stdin)
try:
 r=urllib.request.Request(v['target']+'/',headers={'Cache-Control':'no-cache'})
 with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(r,timeout=15) as p:
  b=p.read(4194304);print(json.dumps({'code':p.status,'body_sha256':hashlib.sha256(b).hexdigest(),'fiction_theme_marker':b'A01_FICTION_PUBLICATION_OK' in b,'redirected':p.url!=r.full_url}))
except Exception as e: print(json.dumps({'code':0,'error_class':type(e).__name__}))
''', json.dumps({'target': target}).encode())
    import urllib.request
    try:
        request = urllib.request.Request(target + '/', headers={'Cache-Control': 'no-cache'})
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=15) as response:
            body = response.read(4194304)
            assigned_operator = {'code': response.status, 'body_sha256': hashlib.sha256(body).hexdigest(),
                'fiction_theme_marker': b'A01_FICTION_PUBLICATION_OK' in body,
                'redirected': response.url != request.full_url, 'transport': 'operator-host'}
    except Exception as exc:
        assigned_operator = {'code': 0, 'error_class': type(exc).__name__, 'transport': 'operator-host'}
    proof['http'] = http
    proof['assigned_url_wsl_http'] = assigned
    proof['assigned_url_http'] = assigned_operator
    proof['ok'] = (proof.get('ok') is True and http['code'] == 200 and not http.get('redirected', True)
                   and assigned_operator['code'] == 200 and not assigned_operator.get('redirected', True))
    return proof


def script_capacity_probe(slug):
    """Synthetic-only post-publication download/deploy/replay/rollback proof."""
    validate_name(slug)
    execution = call(['exec', '-i', '-e', 'A01_CAPACITY_SITE=' + slug, 'wp-' + slug, 'php'],
                     (HERE / 'script_capacity_probe.php').read_bytes(), check=False)
    lines = [line[13:] for line in execution.stdout.decode().splitlines() if line.startswith('A01_CAPACITY=')]
    if len(lines) != 1:
        return {'ok': False, 'failure_code': 'CAPACITY_RECEIPT_REFUSED', 'exit': execution.returncode}
    try:
        result = json.loads(lines[0])
    except ValueError:
        return {'ok': False, 'failure_code': 'CAPACITY_RECEIPT_REFUSED', 'exit': execution.returncode}
    required = ('file_mods_locked', 'admin_updates_denied', 'auto_updates_disabled',
                'script_deploy_readback', 'script_replay_idempotent', 'rollback_readback', 'owned_probe_files_absent')
    result['ok'] = (execution.returncode == 0 and result.get('ok') is True
                    and result.get('policy') == 'deployment_scripts_only'
                    and all(result.get(key) is True for key in required)
                    and result.get('wordpress_download_http') == result.get('woocommerce_egress_http') == 200
                    and bool(re.fullmatch(r'[a-f0-9]{64}', result.get('wordpress_download_sha256', ''))))
    return result


def read_admin_password(from_stdin):
    if not from_stdin:
        return getpass.getpass('Mot de passe neuf du compte test : ')
    if sys.stdin.isatty():
        raise RuntimeError('PASSWORD_STDIN_PIPE_REQUIRED')
    try:
        raw = sys.stdin.buffer.readline(75)
        if raw.endswith(b'\r\n'):
            raw = raw[:-2]
        elif raw.endswith(b'\n'):
            raw = raw[:-1]
        value = raw.decode('utf-8', 'strict')
        if not 20 <= len(raw) <= 72 or any(c in value for c in '\r\n\0'):
            raise ValueError
        return value
    except (UnicodeError, ValueError):
        raise RuntimeError('ADMIN_PASSWORD_REFUSED') from None


def refusal_summary(result):
    """Closed console summary: never use raw exception text or archive names."""
    values = []
    for case in result.get('cases', []):
        gate = case.get('archive_core_preflight', {})
        detail = gate.get('detail') if gate.get('ok') is False else None
        if detail is None:
            detail = case.get('offline_failure', {}).get('detail')
        if detail:
            first = next(iter(detail.get('locations', [])), {})
            values.append({'code': detail['code'], 'count': detail['count'],
                           'first_zone': first.get('zone', '(indeterminee)'),
                           'extension': first.get('extension', '(autre)')})
    return values


def main():
    parser = argparse.ArgumentParser(description='A-01 : archive → vérification hors ligne → publication dans un site imagine-test-…')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test-publication', action='store_true')
    group.add_argument('--archive')
    parser.add_argument('--operator-ced', action='store_true')
    parser.add_argument('--diagnose', action='store_true', help='Lecture seule intégrale : aucun site, extraction ou téléchargement')
    parser.add_argument('--password-stdin', action='store_true',
                        help='Automatisation Ced : mot de passe neuf par pipe stdin seulement, jamais argv')
    parser.add_argument('--name')
    parser.add_argument('--production-url')
    parser.add_argument('--table-decisions')
    parser.add_argument('--php-version', default='8.2', choices=['8.2'])
    parser.add_argument('--expected-core-version', default='6.9.1',
                        help='Version attendue de l’archive ; cœur public préparé à sa version avant injection')
    parser.add_argument('--case', choices=['classic', 'hpos', 'trap', 'personal'], help='Rejeu synthétique ciblé, défaut les quatre')
    args = parser.parse_args()
    if args.diagnose:
        if not args.operator_ced or not args.archive or args.password_stdin or args.case:
            parser.error('--diagnose exige --operator-ced --archive, sans mot de passe ni self-test')
        from diagnosis import diagnose_path
        report = diagnose_path(args.archive, args.expected_core_version, args.table_decisions, args.php_version)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if report['blockers'] else 0
    if not re.fullmatch(r'[0-9]+\.[0-9]+(?:\.[0-9]+)?', args.expected_core_version):
        parser.error('--expected-core-version : version numérique stricte requise')
    if args.archive and not (args.operator_ced and args.name and args.production_url):
        parser.error('--operator-ced, --name imagine-test-… et --production-url requis')
    if args.password_stdin and not args.archive:
        parser.error('--password-stdin réservé au mode opérateur')
    run_id = uuid.uuid4().hex[:12]
    out = ROOT / 'production/A-01/publication-23nov' / run_id
    out.mkdir(parents=True, exist_ok=False)
    cases = [('classic', None), ('hpos', None), ('classic', 'secret'), ('classic', 'personal')] if args.self_test_publication else [('operator', None)]
    if args.case:
        if not args.self_test_publication: parser.error('--case réservé aux tests fictifs')
        cases = [('classic' if args.case in ('trap', 'personal') else args.case,
                  {'trap': 'secret', 'personal': 'personal'}.get(args.case))]
    result = {'status': 'FAIL', 'run_id': run_id, 'cases': [], 'cleanup': [],
              'no_real_archive': args.self_test_publication, 'no_agent_access_used': True,
              'tool_or_templates_modified': False,
              'expected_core_version': args.expected_core_version,
              'update_policy': 'deployment_scripts_only; DISALLOW_FILE_MODS retained; update-host egress retained',
              'post_verified_network_limit': 'WordPress HTTP filtering only; not a system firewall',
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        # WSL.exe consumes inherited stdin even for read-only Docker calls.
        # Capture an explicitly supplied pipe before ANY WSL subprocess.
        # Interactive Ced prompting remains after the ordinary prerequisites.
        piped_password = read_admin_password(True) if args.password_stdin else None
        from publication_preflight import collect
        before = collect()['tool_source_manifest']
        result['tool_source_manifest'] = before
        prepared_core = None
        qualified_69 = args.self_test_publication and args.expected_core_version == '6.9.1'
        if args.self_test_publication:
            # Public preparation is separate from every offline archive restore.
            prepared_core = prepare_core(args.expected_core_version)
            result['public_core'] = prepared_core[1]
            if qualified_69:
                sys.path.insert(0, str(ROOT / 'wp/tests/a01-court'))
                from qualification_69 import public_woo
                prepared_woo = public_woo(args.expected_core_version)
                result['public_fixture_woocommerce'] = prepared_woo[1]
                result['subscriptions_691_limit'] = '9.4.1 requires WP 7.0 / Woo 11.1; only prior 7.0.9 qualification; Ced first real import report must be reviewed before opening'
        for storage, trapped in cases:
            name = validate_name(args.name or ('imagine-test-a01-' + run_id + '-' + ({'secret': 'trap', 'personal': 'personal'}.get(trapped, storage))))
            runner = 'imagine-a01-publication-' + uuid.uuid4().hex[:12]
            helpers = []; created = False; runner_created = False
            receipt = {'name': name, 'storage': storage, 'trapped': bool(trapped), 'trap_kind': trapped, 'status': 'NOT_EXECUTED'}
            result['cases'].append(receipt)
            try:
                manifest = fresh_runner(runner); runner_created = True
                receipt['offline_isolation_before'] = offline_isolation(runner)
                receipt['source_manifest'] = manifest
                if args.archive:
                    # Operator-only path. Selection precedes any site/API lifecycle or PHP.
                    archive = Path(args.archive)
                    if archive.is_symlink() or not archive.is_file() or archive.suffix.lower() != '.wpress':
                        raise RuntimeError('ARCHIVE_REFUSED')
                    p = str(archive.resolve())
                    if os.name == 'nt': p = '/mnt/' + p[0].lower() + p[2:].replace('\\', '/')
                    call(['exec', runner, 'mkdir', '-p', '/input'])
                    call(['cp', p, runner + ':/input/source.wpress'])
                    archive_path = '/input/source.wpress'
                    receipt['archive_core_preflight'] = archive_core_preflight(runner, archive_path, args.expected_core_version)
                    if receipt['archive_core_preflight']['ok'] is not True:
                        raise RuntimeError(receipt['archive_core_preflight']['code'])
                    prepared_core = prepare_core(receipt['archive_core_preflight']['source'])
                    result['public_core'] = prepared_core[1]
                receipt['runtime_core_preflight'] = set_empty_runner_core(runner, *prepared_core)
                if qualified_69:
                    call(['exec', '-i', runner, 'python3', '-'], b"import shutil\nshutil.rmtree('/opt/woocommerce/woocommerce')\n")
                    call(['exec', '-i', runner, 'tar', '-xf', '-', '-C', '/'], prepared_woo[0])
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
                receipt['normal_creation'] = {k: site[k] for k in ('slug', 'status', 'url', 'port', 'php_version', 'mcp_enabled', 'mcp_status')}
                php_runtime = call(['exec', 'wp-' + name, 'php', '-r', 'echo PHP_VERSION;']).stdout.decode().strip()
                if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', php_runtime):
                    raise RuntimeError('TARGET_PHP_VERSION_REFUSED')
                receipt['target_php_runtime'] = php_runtime
                receipt['stopped_before_import'] = stop_site(name)
                lint = call(['exec', runner, 'php', '-l', '/opt/court/publication_probe.php'])
                call(['exec', runner, 'php', '-l', '/opt/court/script_capacity_probe.php'])
                receipt['new_php_lint'] = {'exit': lint.returncode, 'output_sha256': hashlib.sha256(lint.stdout + lint.stderr).hexdigest()}
                receipt['source_manifest'] = manifest
                request = {'target_url': 'http://localhost:' + str(site['port']),
                           'expected_core_version': args.expected_core_version,
                           'php_version': php_runtime,
                           'production_url': args.production_url or 'https://production.synthetic.invalid',
                           'password': (piped_password if args.password_stdin else read_admin_password(False)) if args.archive else secrets.token_urlsafe(40),
                           'decisions': json.loads(Path(args.table_decisions).read_text()) if args.table_decisions else {}}
                if args.self_test_publication:
                    for slug in (('woocommerce-memberships',) if qualified_69 else ('woocommerce-memberships', 'woocommerce-subscriptions')):
                        call(['cp', '/home/ced/staging-wp/plugins/' + slug + '.zip', runner + ':/opt/e2e/' + slug + '.zip'])
                    p = call(['exec', runner, 'python3', '/opt/court/qualification_69.py' if qualified_69 else '/opt/court/prepare_publication.py', storage,
                              (trapped or 'clean') if qualified_69 else {'secret': 'trapped', 'personal': 'personal'}.get(trapped, 'clean')], check=False)
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
                    receipt['archive_core_preflight'] = archive_core_preflight(runner, archive_path, args.expected_core_version)
                    if receipt['archive_core_preflight']['ok'] is not True:
                        raise RuntimeError(receipt['archive_core_preflight']['code'])
                program = '''import json,sys
sys.path.insert(0,'/opt/court')
from inside import execute_offline_request
request=json.load(sys.stdin)
r=execute_offline_request(request.pop('archive'),request,request.pop('start_database'))
from pathlib import Path
Path('/report/offline.json').write_text(json.dumps(r))
print(json.dumps({'data_verified':r['data_verified']}))
raise SystemExit(1 if 'failure' in r else 0)
'''
                request.update(start_database=not args.self_test_publication, archive=archive_path)
                input_program = 'import io,sys\nsys.stdin=io.StringIO(' + repr(json.dumps(request)) + ')\n' + program
                execution = call(['exec', '-i', runner, 'python3', '-'], input_program.encode(), check=False)
                del request['password']
                try:
                    offline = read_json(runner, '/report/offline.json')
                except Exception:
                    receipt['restore_output_sha256'] = hashlib.sha256(execution.stdout + execution.stderr).hexdigest()
                    receipt['offline_failure'] = {'stage': 'offline_restore', 'code': 'OFFLINE_RECEIPT_UNAVAILABLE'}
                    raise RuntimeError('OFFLINE_RECEIPT_UNAVAILABLE') from None
                receipt['offline_isolation_after'] = offline_isolation(runner)
                receipt['offline'] = offline
                if execution.returncode or 'failure' in offline:
                    receipt['offline_failure'] = offline.get('failure', {'stage': 'offline_restore', 'code': 'OFFLINE_RESTORE_REFUSED'})
                    raise RuntimeError('OFFLINE_RESTORE_REFUSED')
                if args.self_test_publication:
                    assert offline['table_engines']['wp_a01_engine_probe'] == 'MYISAM'
                    assert {'code': 'NON_INNODB_TABLE', 'table': 'wp_a01_engine_probe', 'engine': 'MYISAM'} in offline['warnings']
                    receipt['myisam_preserved_and_reported'] = True
                    assert offline['restored_files_before_cleanup'] == fixture['source_files']
                    first = offline['restored_files_before_cleanup']; cleaned = offline['files_after_cleanup']
                    removed = sorted(set(first) - set(cleaned))
                    changed = [p for p in set(first) & set(cleaned) if first[p] != cleaned[p]]
                    assert not changed
                    assert all(p.endswith('.log') or p.startswith(('uploads/wc-logs/', 'cache/', 'ai1wm-backups/')) for p in removed)
                    receipt['archive_fidelity'] = {'all_restored_hashes_equal_source': True,
                        'retained_files_unchanged': True, 'expected_removed': removed,
                        'added_by_safety_or_Woo_bootstrap': sorted(set(cleaned) - set(first)),
                        'file_counts': {folder: {'before': sum(p.startswith(folder + '/') for p in first),
                                                'after': sum(p.startswith(folder + '/') for p in cleaned)}
                                        for folder in ('plugins', 'themes', 'uploads', 'mu-plugins')}}
                if trapped:
                    issues = offline['steps'][-1]['report'].get('issues', [])
                    expected = {'secret': 'SECRET_OU_IDENTIFIANT', 'personal': 'TABLE_PERSONNELLE_A_TRANCHER'}[trapped]
                    assert not offline['data_verified'] and expected in issues
                    receipt['expected_blocking_issue'] = expected
                injection = {}
                def do_inject():
                    injection.update(inject(name, runner, offline, site['url'], helpers))
                def do_start():
                    api('POST', '/api/sites/' + name + '/start')
                    assert api('GET', '/api/sites/' + name)['body']['status'] == 'running'
                    time.sleep(3)
                def checked_runtime():
                    probe = runtime_probe(name, site['port'], site['url'])
                    if probe.get('versions', {}).get('wordpress') != offline['core_versions']['source']:
                        probe.update(ok=False, core_version_mismatch=True)
                    return probe
                published = guarded_publish(offline, do_inject, do_start,
                                            checked_runtime, lambda: stop_site(name))
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
                        assert probe['http']['fiction_theme_marker'] and probe['assigned_url_http']['fiction_theme_marker']
                        assert probe['versions']['hpos'] is (storage == 'hpos')
                        assert probe['fidelity']['rights'] == {k: v['private'] for k, v in fixture['rights']['rights'].items()}
                        for key in ('business', 'membership', 'rules_sha256', 'plugins', 'theme'):
                            assert probe['fidelity'][key] == fixture[key], 'FIDELITY_' + key.upper()
                        if qualified_69:
                            assert probe['fidelity']['orders'] == fixture['orders']
                            assert probe['fidelity']['membership_shortcodes'] == fixture['rights']['shortcodes']
                            assert probe['fidelity']['public_post_unrestricted'] is True
                            assert probe['versions']['subscriptions'] is None
                            assert probe['scheduler']['tested'] is False
                        receipt['script_update_capacity'] = script_capacity_probe(name)
                        if receipt['script_update_capacity']['ok'] is not True:
                            raise RuntimeError('SCRIPT_UPDATE_CAPACITY_REFUSED')
                    marker = {'status': 'verified', 'run_id': run_id, 'site': name,
                              'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                              'report': str(out / 'result.json'), 'offline_verified': True, 'runtime_probe_passed': True,
                              'expected_core_version': args.expected_core_version,
                              'update_policy': result['update_policy'],
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
                # Safety stop must precede every fallible cleanup operation.
                # Retain primary failure and every cleanup error independently.
                def cleanup_attempt(phase, action):
                    try:
                        return action()
                    except Exception as exc:
                        tag = str(exc)
                        result.setdefault('cleanup_errors', []).append({
                            'site': name, 'phase': phase,
                            'code': tag if re.fullmatch(r'[A-Z0-9_]{1,100}', tag) else 'CLEANUP_REFUSED'})
                        return None
                if created and (args.self_test_publication or receipt['status'] != 'PASS'):
                    stopped = cleanup_attempt('failure_stop', lambda: stop_site(name))
                    if stopped is not None:
                        receipt['failure_stop_readback'] = stopped
                for helper in list(helpers):
                    removed = cleanup_attempt('helper_removal', lambda: remove_owned(helper))
                    if removed is not None: result['cleanup'].append(removed)
                def remove_runner():
                    if runner_created:
                        return remove_owned(runner)
                    candidate = call(['inspect', runner], check=False)
                    if candidate.returncode == 0:
                        info = json.loads(candidate.stdout)[0]
                        if info['Config']['Labels'].get(LABEL) != 'true':
                            raise RuntimeError('PARTIAL_RUNNER_OWNERSHIP_REFUSED')
                        return remove_owned(runner)
                    if b'no such object' not in candidate.stderr.lower():
                        raise RuntimeError('PARTIAL_RUNNER_ABSENCE_NOT_PROVEN')
                removed = cleanup_attempt('runner_removal', remove_runner)
                if removed is not None: result['cleanup'].append(removed)
                if created and args.self_test_publication:
                    def delete_test():
                        api('DELETE', '/api/sites/' + name)
                        return deleted_readback(name)
                    deleted = cleanup_attempt('site_deletion', delete_test)
                    if deleted is not None: result['cleanup'].append(deleted)
                (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        after = collect()['tool_source_manifest']
        result['tool_sources_unchanged'] = before == after
        assert before == after
        result['status'] = 'PASS' if all(c['status'] == 'PASS' for c in result['cases']) and not result.get('cleanup_errors') else 'FAIL'
    except Exception as exc:
        result['blocker'] = str(exc) if re.fullmatch(r'[A-Z0-9_]{1,100}', str(exc)) else type(exc).__name__
    finally:
        result['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result['command_sources'] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in sorted(HERE.glob('*.py')) + sorted(HERE.glob('*.php'))}
        (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': result['status'], 'report': str(out / 'result.json'),
                      'refusals': refusal_summary(result)}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
