"""A04 offline updater. Linux only; PHP and WP-CLI in target environment."""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import zipfile

ORDER = ['core', 'woocommerce', 'woocommerce-subscriptions', 'woocommerce-memberships']
HOOKS = {'woocommerce_run_update_callback'}
LOCK_FDS = ()

class Refusal(RuntimeError):
    pass

def require(ok, code):
    if not ok:
        raise Refusal(code)

def digest(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def load_json(path):
    path = pathlib.Path(path)
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 16777216, 'A04_JSON')
    return json.loads(path.read_text(encoding='utf8'))

def atomic_json(path, value):
    path = pathlib.Path(path)
    require(not path.is_symlink(), 'A04_SYMLINK')
    fd, name = tempfile.mkstemp(prefix='.a04-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf8') as f:
            json.dump(value, f, indent=2, ensure_ascii=False)
            f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
        if os.name == 'posix':
            directory = os.open(path.parent, os.O_DIRECTORY)
            try: os.fsync(directory)
            finally: os.close(directory)
    finally:
        if os.path.exists(name): os.unlink(name)

def numeric(value):
    require(isinstance(value, str) and re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}', value), 'A04_VERSION')
    parts = value.split('.')
    return tuple(int(v) for v in parts) + (0,) * (4 - len(parts))

def validate_plan(plan):
    require(isinstance(plan, dict) and set(plan) == {'schema', 'site_status', 'steps'} and plan['schema'] == 'imagine-a04-v1', 'A04_PLAN')
    require(plan['site_status'] in ['verified-staging','frozen-production'], 'A04_STATUS')
    steps = plan['steps']
    require(isinstance(steps, list) and 4 <= len(steps) <= 100, 'A04_ORDER')
    names = [s.get('component') for s in steps]
    require(names[:4] == ORDER and len(set(names)) == len(names), 'A04_ORDER')
    for i, step in enumerate(steps):
        require(set(step) == {'component', 'before', 'after', 'archive', 'sha256', 'adapter', 'hooks'}, 'A04_PLAN')
        key = step['component']
        require(isinstance(key, str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,99}', key), 'A04_COMPONENT')
        require(numeric(step['after']) >= numeric(step['before']), 'A04_DOWNGRADE')
        require(step['adapter'] == (key if i < 4 else 'bootstrap-only'), 'A04_ADAPTER')
        require(step['hooks'] == [], 'A04_HOOK')
        require(isinstance(step['archive'], str) and pathlib.Path(step['archive']).is_absolute(), 'A04_PACKAGE')
        require(isinstance(step['sha256'], str) and re.fullmatch('[a-f0-9]{64}', step['sha256']), 'A04_PACKAGE')
    require(steps[0]['after'].startswith('7.0.'), 'A04_CORE_TARGET')
    return plan

def authorize(status, site, identity, gofile):
    if status == 'verified-staging':
        return 'staging'
    require(status == 'frozen-production' and bool(gofile), 'A04_PRODUCTION_GO_REQUIRED')
    go = load_json(gofile)
    require(set(go) == {'author','task','go','site','plan_sha256','expires_at'}
        and go['author'] == 'Ced' and go['task'] == 'A-04-mise-a-jour' and go['go'] is True
        and go['site'] == str(site) and go['plan_sha256'] == identity
        and isinstance(go['expires_at'], int) and 0 < go['expires_at'] - time.time() <= 21600,
        'A04_PRODUCTION_GO_INVALID')
    return 'production'

def check_backup(backup, site):
    require(isinstance(backup, dict) and backup.get('site') == str(site), 'A04_BACKUP_SITE')
    age = time.time() - backup.get('created_at', 0)
    require(0 <= age <= 21600, 'A04_BACKUP_AGE')
    for key in ['database', 'files']:
        entry = backup.get(key, {})
        file = pathlib.Path(entry.get('path', ''))
        require(file.is_absolute() and file.is_file() and not file.is_symlink() and file.stat().st_size > 0, 'A04_BACKUP_FILE')
        require(not file.is_relative_to(pathlib.Path(site)), 'A04_BACKUP_LOCATION')
        require(digest(file) == entry.get('sha256'), 'A04_BACKUP_HASH')

def safe_path(base, relative):
    base = pathlib.Path(base)
    require(not base.is_symlink(), 'A04_SYMLINK')
    path = base
    for part in pathlib.PurePosixPath(relative).parts:
        path = path / part
        require(not path.is_symlink(), 'A04_SYMLINK')
    require(path.resolve().is_relative_to(base.resolve()), 'A04_PATH')
    return path

def archive_entries(archive, component):
    entries = []; seen = set(); total = 0
    with zipfile.ZipFile(archive) as z:
        require(len(z.infolist()) <= 60000, 'A04_ARCHIVE_LIMIT')
        root = 'wordpress' if component == 'core' else component
        for info in z.infolist():
            name = info.filename
            parts = pathlib.PurePosixPath(name).parts
            require(parts and parts[0] == root and '..' not in parts and not name.startswith('/') and not re.search(r'[\\:\x00-\x1f]', name), 'A04_ARCHIVE_PATH')
            require((info.external_attr >> 16 & 0o170000) in (0, stat.S_IFDIR, stat.S_IFREG), 'A04_ARCHIVE_TYPE')
            relative = '/'.join(parts[1:])
            if not relative or info.is_dir(): continue
            require(relative.casefold() not in seen, 'A04_ARCHIVE_COLLISION'); seen.add(relative.casefold())
            total += info.file_size
            require(total <= 1073741824 and info.file_size <= 134217728 and not info.flag_bits & 1, 'A04_ARCHIVE_LIMIT')
            if component == 'core':
                if relative.startswith('wp-content/') or relative in ['wp-config.php', 'wp-config-sample.php', '.htaccess']: continue
                require(relative.startswith(('wp-admin/', 'wp-includes/')) or '/' not in relative and relative.endswith(('.php', '.html', '.txt')), 'A04_CORE_FILE')
            entries.append((info.filename, relative))
    require(bool(entries), 'A04_ARCHIVE_EMPTY')
    return entries

def package_metadata(archive, component):
    member = 'wordpress/wp-includes/version.php' if component == 'core' else component + '/' + component + '.php'
    with zipfile.ZipFile(archive) as z:
        require(member in z.namelist() and z.getinfo(member).file_size < 2097152, 'A04_PACKAGE_METADATA')
        text = z.read(member).decode('utf8')
    if component == 'core':
        match = re.search(r"\$wp_version\s*=\s*'([^']+)'", text)
        require(match is not None, 'A04_PACKAGE_VERSION')
        return {'version':match[1], 'requires_php':None, 'requires_wp':None}
    def header(name):
        match = re.search(r'^\s*\*?\s*' + re.escape(name) + r':\s*([0-9.]+)', text, re.M | re.I)
        return match[1] if match else None
    return {'version':header('Version'), 'requires_php':header('Requires PHP'), 'requires_wp':header('Requires at least')}

def check_package(archive, component, expected, target_wp, php):
    metadata = package_metadata(archive, component)
    require(metadata['version'] == expected, 'A04_PACKAGE_VERSION')
    if metadata['requires_php']:
        require(numeric(php) >= numeric(metadata['requires_php']), 'A04_PACKAGE_PHP')
    if metadata['requires_wp']:
        require(numeric(target_wp) >= numeric(metadata['requires_wp']), 'A04_PACKAGE_WORDPRESS')
    return metadata

def overlay(archive, site, component):
    entries = archive_entries(archive, component)
    base = site if component == 'core' else safe_path(site, 'wp-content/plugins/' + component)
    for _, rel in entries: safe_path(base, rel)
    with zipfile.ZipFile(archive) as z:
        for name, rel in entries:
            target = safe_path(base, rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, temp = tempfile.mkstemp(prefix='.a04-', dir=target.parent)
            try:
                with os.fdopen(fd, 'wb') as out, z.open(name) as source:
                    shutil.copyfileobj(source, out, 1048576); out.flush(); os.fsync(out.fileno())
                os.chmod(temp, 0o644)
                safe_path(base, rel)
                os.replace(temp, target)
            finally:
                if os.path.exists(temp): os.unlink(temp)
    return len(entries)

def version(site, component):
    path = safe_path(site, 'wp-includes/version.php' if component == 'core' else 'wp-content/plugins/' + component + '/' + component + '.php')
    text = path.read_text(encoding='utf8', errors='strict')
    match = re.search(r"\$wp_version\s*=\s*'([^']+)'", text) if component == 'core' else re.search(r'^\s*\*?\s*Version:\s*([0-9.]+)', text, re.M | re.I)
    require(match is not None, 'A04_VERSION_READ')
    numeric(match[1]); return match[1]

def validate_state(state, identity, site, config_hash):
    require(isinstance(state, dict) and state.get('schema') == 'imagine-a04-state-v1' and state.get('plan_sha256') == identity and state.get('site') == str(site) and state.get('config_sha256') == config_hash and isinstance(state.get('steps'), dict) and isinstance(state.get('events'), list), 'A04_STATE')
    return state

def run_wp(site, args, env=None, timeout=300):
    try:
        p = subprocess.run(['wp', '--allow-root', '--no-color', '--path=' + str(site),
                '--require=' + str(pathlib.Path(__file__).resolve().parent / 'bootstrap.php')] + args,
            capture_output=True, text=True, pass_fds=LOCK_FDS, env={**os.environ, 'IMAGINE_A04_SITE': str(site), **(env or {})}, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise Refusal('A04_COMMAND_TIMEOUT') from None
    if p.returncode != 0 or re.search(r'(?:Fatal error|Parse error|Uncaught (?:Error|Exception))', p.stdout + p.stderr, re.I):
        codes = re.findall(r'\bA04_[A-Z_]+\b', p.stderr)
        raise Refusal(codes[-1] if codes else 'A04_COMMAND_FAILED')
    return p

def worker(site, step, mode, journal=None, target_env='staging'):
    script = pathlib.Path(__file__).resolve().parent / 'runtime.php'
    result = run_wp(site, ['eval-file', str(script), '--use-include'],
        {'IMAGINE_A04_COMPONENT': step['component'], 'IMAGINE_A04_MODE': mode,
         'IMAGINE_A04_HOOKS': json.dumps(step['hooks']), 'IMAGINE_A04_EXPECTED_ENV': target_env, 'IMAGINE_A04_JOURNAL': str(journal) if journal else ''})
    lines = [v[len('A04_JSON='):] for v in result.stdout.splitlines() if v.startswith('A04_JSON=')]
    require(len(lines) == 1, 'A04_RUNTIME_RECEIPT')
    receipt = json.loads(lines[0])
    require(receipt.get('safe') is True and receipt.get('complete') is True, 'A04_MIGRATIONS_INCOMPLETE')
    return receipt

def maintenance(site):
    file = safe_path(site, '.maintenance')
    require(file.is_file(), 'A04_MAINTENANCE')
    match = re.fullmatch(r"<\?php\s+\$upgrading\s*=\s*([0-9]+);\s*", file.read_text())
    require(match and 0 <= time.time() - int(match[1]) < 600, 'A04_MAINTENANCE')

def refresh_maintenance(site):
    safe_path(site, '.maintenance').write_text('<?php $upgrading = ' + str(int(time.time())) + ';\n')

def execute(args):
    global LOCK_FDS
    require(sys.platform == 'linux', 'A04_LINUX_REQUIRED')
    import fcntl
    site = pathlib.Path(args.wp_path)
    require(site.is_absolute() and site.is_dir() and site.resolve() == site, 'A04_SITE_PATH')
    plan = validate_plan(load_json(args.plan)); identity = digest(args.plan)
    target_env = authorize(plan['site_status'], site, identity, args.go)
    state_dir = pathlib.Path(args.state)
    require(state_dir.is_absolute() and not state_dir.is_relative_to(site) and state_dir.resolve() == state_dir, 'A04_STATE_PATH')
    state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    with open(safe_path(state_dir, 'execution.lock'), 'a') as lock, open(safe_path(site, '.imagine-a04-bascule.lock'), 'a') as site_lock:
        try:
            fcntl.flock(site_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise Refusal('A04_ALREADY_RUNNING') from None
        # Native children retain the same flock descriptions if this parent is
        # SIGKILLed; a second updater must wait until those children really exit.
        LOCK_FDS = (lock.fileno(), site_lock.fileno())
        maintenance(site)
        if target_env == 'staging':
            marker = load_json(safe_path(site, '.imagine-staging-verified.json'))
            require(marker.get('status') == 'verified' and marker.get('offline_verified') is True and marker.get('runtime_probe_passed') is True, 'A04_NOT_VERIFIED')
            safety = safe_path(site, 'wp-content/mu-plugins/000-imagine-staging-safety.php')
            reference = pathlib.Path(__file__).resolve().parents[2] / 'staging/mu-plugins/000-imagine-staging-safety.php'
            require(safety.is_file() and reference.is_file() and digest(safety) == digest(reference), 'A04_SAFETY_BYTES')
        for name in ['db.php', 'object-cache.php', 'advanced-cache.php']:
            p = site / 'wp-content' / name
            require(not p.exists() and not p.is_symlink(), 'A04_DROPIN')
        check_backup(load_json(args.backup), site)
        config_hash = digest(safe_path(site, 'wp-config.php'))
        state_file = safe_path(state_dir, 'etat.json')
        state = validate_state(load_json(state_file), identity, site, config_hash) if state_file.exists() else {'schema':'imagine-a04-state-v1','plan_sha256':identity,'site':str(site),'config_sha256':config_hash,'steps':{},'events':[]}
        def save():
            atomic_json(state_file, state)
            atomic_json(state_dir / 'journal.json', state['events'])
            (state_dir / 'journal.txt').write_text('A-04 — maintenance conservée\n' + '\n'.join(json.dumps(e, ensure_ascii=False, sort_keys=True) for e in state['events'])+'\n', encoding='utf8')
        def event(key, stage, **extra):
            state['events'].append({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'component':key,'stage':stage,**extra}); save()
        php_probe = subprocess.run(['php','-r','echo PHP_VERSION;'],capture_output=True,text=True,timeout=15)
        require(php_probe.returncode == 0, 'A04_PHP')
        php = php_probe.stdout.strip(); numeric(php)
        planned_bytes = 0
        for step in plan['steps']:
            package = pathlib.Path(step['archive'])
            require(package.is_file() and not package.is_symlink() and digest(package) == step['sha256'], 'A04_PACKAGE_HASH')
            archive_entries(package, step['component'])
            check_package(package,step['component'],step['after'],plan['steps'][0]['after'],php)
            with zipfile.ZipFile(package) as z: planned_bytes += sum(info.file_size for info in z.infolist())
            row = state['steps'].get(step['component']); current = version(site, step['component'])
            if row is None: require(current == step['before'], 'A04_START_VERSION')
            else:
                require(row.get('phase') in ['copying','copied','migrating','verified'], 'A04_STATE')
                require(current in [step['before'],step['after']], 'A04_RESUME_VERSION')
                if row['phase'] == 'verified': require(current == step['after'], 'A04_COMPLETED_DRIFT')
        require(shutil.disk_usage(site).free >= planned_bytes + 134217728, 'A04_DISK_SPACE')
        save()
        persistent = safe_path(site, 'wp-content/mu-plugins/001-imagine-a04-maintenance.php')
        template = pathlib.Path(__file__).resolve().parent / 'maintenance.php'
        if persistent.exists(): require(digest(persistent) == digest(template), 'A04_MAINTENANCE_BYTES')
        else: shutil.copyfile(template, persistent)
        try:
            # Never bootstrap a partly copied component after SIGKILL: finish its overlay first.
            if not any(r['phase'] == 'copying' for r in state['steps'].values()): worker(site, plan['steps'][0], 'guard', safe_path(state_dir, 'migrations.jsonl'), target_env)
            for step in plan['steps']:
                key = step['component']; row = state['steps'].get(key)
                if row and row['phase'] == 'verified': continue
                if row is None:
                    row = {'phase':'copying','before':step['before'],'after':step['after'],'started':time.time(),'attempts':0}
                    state['steps'][key] = row
                row['attempts'] += 1
                event(key,'resume' if row['attempts'] > 1 else 'start',before=row['before'],after=row['after'])
                refresh_maintenance(site)
                if row['phase'] == 'copying':
                    row['files'] = overlay(step['archive'], site, key)
                    require(version(site,key) == step['after'],'A04_TARGET_VERSION')
                    row['phase'] = 'copied'; event(key,'copied',files=row['files'])
                if args.stop_after == key:
                    event(key,'interruption_requested')
                    if args.pause:
                        while True: time.sleep(1)
                    return 75
                row['phase'] = 'migrating'; save()
                if key == 'core': run_wp(site,['core','update-db'])
                row.setdefault('migrations', [])
                for wave in range(10):
                    migrated = worker(site,step,'migrate',safe_path(state_dir,'migrations.jsonl'),target_env)
                    row['migrations'].extend(migrated.get('migrations', [])); save()
                    refresh_maintenance(site)
                    try:
                        worker(site,step,'verify',safe_path(state_dir,'migrations.jsonl'),target_env)
                    except Refusal as error:
                        if key != 'woocommerce' or str(error) != 'A04_KNOWN_MIGRATION_PENDING': raise
                        event(key,'native_follow_up',wave=wave + 1)
                        continue
                    break
                else: raise Refusal('A04_MIGRATION_FIXPOINT_LIMIT')
                require(version(site,key) == step['after'],'A04_TARGET_VERSION')
                row['phase']='verified';row['duration_seconds']=round(time.time()-row['started'],3)
                event(key,'verified',before=row['before'],after=row['after'],duration_seconds=row['duration_seconds'],migrations=row['migrations'])
            for step in plan['steps']:
                worker(site,step,'verify',safe_path(state_dir,'migrations.jsonl'),target_env)
            event('all','complete'); return 0
        except BaseException as error:
            event('all','stopped',code=str(error) if isinstance(error,Refusal) else 'A04_EXECUTION_FAILED')
            raise

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for option in ['wp-path','plan','backup','state']:parser.add_argument('--'+option,required=True)
    parser.add_argument('--go',default=None,help='GO Ced local, borné au site/plan et valable au plus six heures (production seulement).')
    parser.add_argument('--stop-after',default='')
    parser.add_argument('--pause',action='store_true',help='Attend à --stop-after; garde le verrou et la maintenance.')
    args=parser.parse_args()
    try:
        status=execute(args);print('A04_OK' if status == 0 else 'A04_INTERRUPTED');return status
    except Exception as error:
        code=str(error) if isinstance(error,Refusal) and re.fullmatch('A04_[A-Z_]+',str(error)) else 'A04_EXECUTION_FAILED'
        print(code,file=sys.stderr);return 1
