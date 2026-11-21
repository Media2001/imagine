"""C05-owned offline runner. No host install, pull, site import or mounts."""
import argparse
import datetime
import hashlib
import io
import json
import pathlib
import re
import subprocess
import tarfile
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
OUT = ROOT / 'production/C-05/preuves'
STATE = OUT / 'runner-state.json'
DOCKER = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker']
LABEL = 'org.imagine.c05-runner'
IMAGE = 'sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2'
PACKAGE = '/home/ced/staging-wp/plugins/woocommerce-subscriptions.zip'


def call(args, data=None, check=True, timeout=600):
    p = subprocess.run(DOCKER + args, input=data, capture_output=True, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace') + p.stdout.decode(errors='replace'))
    return p


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def inspect(name):
    v = json.loads(call(['inspect', name]).stdout)[0]
    assert v['Config']['Labels'].get(LABEL) == 'true'
    assert v['Image'] == IMAGE
    assert not v['Mounts'] and not v['HostConfig'].get('Binds')
    assert not v['HostConfig'].get('PortBindings') and not v['Config'].get('ExposedPorts')
    assert v['HostConfig']['NetworkMode'] == 'none'
    assert set(v['NetworkSettings']['Networks']) == {'none'}
    assert not v['HostConfig']['Privileged'] and 'ALL' in v['HostConfig']['CapDrop']
    assert 'no-new-privileges' in v['HostConfig']['SecurityOpt']
    return {'container': name, 'image': v['Image'], 'network': 'none', 'mounts': [], 'ports': [],
            'privileged': False, 'cap_drop': v['HostConfig']['CapDrop'], 'no_new_privileges': True}


def payload():
    manifest = {}
    b = io.BytesIO()
    paths = []
    for relative in ('src/Numeros', 'src/Echeancier', 'tests/Echeancier'):
        paths += sorted((ROOT / 'wp/plugins/imagine-pilotage' / relative).rglob('*.php'))
    paths += sorted(HERE.glob('*.php')) + sorted(HERE.glob('inside.py'))
    with tarfile.open(fileobj=b, mode='w') as t:
        for p in paths:
            rel = p.relative_to(ROOT).as_posix()
            data = p.read_bytes()
            manifest[rel] = hashlib.sha256(data).hexdigest()
            info = tarfile.TarInfo(rel)
            info.size = len(data)
            info.mode = 0o644
            t.addfile(info, io.BytesIO(data))
    return b.getvalue(), manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['prepare', 'unit', 'e2e', 'close'])
    p.add_argument('--name', default='final')
    a = p.parse_args()
    assert re.fullmatch('[a-z0-9-]{1,64}', a.name)
    OUT.mkdir(parents=True, exist_ok=True)
    if a.action == 'prepare':
        assert not STATE.exists()
        image = json.loads(call(['image', 'inspect', IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        name = 'imagine-c05-' + uuid.uuid4().hex[:12]
        call(['create', '--name', name, '--label', LABEL + '=true', '--network', 'none',
              '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
              '--pids-limit', '256', '--memory', '1536m', '--cpus', '2', '--log-driver', 'none',
              '--pull', 'never', '--entrypoint', 'sleep', IMAGE, 'infinity'])
        save(STATE, {'container': name})
        call(['start', name])
        save(OUT / 'preparation.json', inspect(name))
        call(['exec', name, 'mkdir', '-p', '/work'])
        print(name)
        return
    name = json.loads(STATE.read_text(encoding='utf-8'))['container']
    safety = inspect(name)
    if a.action == 'close':
        call(['rm', '-f', name])
        missing = call(['inspect', name], check=False)
        assert missing.returncode and 'no such object' in missing.stderr.decode().lower()
        save(OUT / 'cleanup.json', {'container': name, 'owned_removed': True, 'missing_diagnostic': missing.stderr.decode().strip()})
        STATE.unlink()
        print('Owned runner removed and exact absence verified:', name)
        return
    tar, manifest = payload()
    call(['exec', name, 'rm', '-rf', '/work/wp'])
    call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/work'], tar)
    probe = b'<?php $r=[]; foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator("/work", FilesystemIterator::SKIP_DOTS)) as $f) {if($f->isFile()){$r[substr($f->getPathname(),6)]=hash_file("sha256",$f->getPathname());}} echo json_encode($r);'
    assert json.loads(call(['exec', '-i', name, 'php'], probe).stdout) == manifest
    lint = call(['exec', name, 'sh', '-c', 'find /work -name "*.php" -print0 | xargs -0 -n 1 php -l'], check=False)
    (OUT / (a.name + '-syntax.log')).write_bytes(lint.stdout + lint.stderr)
    if a.action == 'unit':
        command = ['exec', name, 'php', '/work/wp/plugins/imagine-pilotage/tests/Echeancier/run.php']
    else:
        call(['cp', PACKAGE, name + ':/opt/e2e/woocommerce-subscriptions.zip'])
        call(['exec', name, 'rm', '-rf', '/scratch', '/report'])
        command = ['exec', name, 'python3', '/work/wp/tests/echeancier-runner/inside.py']
    result = call(command, check=False, timeout=1200)
    (OUT / (a.name + '.log')).write_bytes(result.stdout + result.stderr)
    if a.action == 'unit':
        text = result.stdout.decode(errors='replace')
        lines = [line[9:] for line in text.splitlines() if line.startswith('C05_JSON=')]
        if lines:
            save(OUT / (a.name + '-result.json'), json.loads(lines[-1]))
    else:
        report = call(['exec', name, 'cat', '/report/c05-result.json'], check=False)
        if report.returncode == 0:
            save(OUT / (a.name + '-result.json'), json.loads(report.stdout))
    assert payload()[1] == manifest, 'Sources changed during execution'
    save(OUT / (a.name + '.json'), {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'command': command[2:], 'exit_code': result.returncode, 'syntax_exit': lint.returncode,
         'source_sha256': manifest, 'container_sources_verified': True, 'safety_before': safety,
         'safety_after': inspect(name), 'runner_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()})
    if a.action == 'unit' and lines:
        value = json.loads(lines[-1])
        print(json.dumps({k: v for k, v in value.items() if k != 'results'}))
        print(json.dumps([r for r in value['results'] if not r['pass']]))
    else:
        print(result.stdout.decode(errors='replace') + result.stderr.decode(errors='replace'))
    raise SystemExit(result.returncode or lint.returncode)


if __name__ == '__main__':
    main()
