"""C-01 only: disposable PHP/Composer, no mounts, DB, WP or ports.

Preparation alone has network access for public Composer dependencies.
Tests and lint run after Docker's bridge is disconnected. No host installs.
"""
import argparse
import datetime
import hashlib
import io
import json
import pathlib
import subprocess
import tarfile
import urllib.request
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[3]
PLUGIN = ROOT / 'wp/plugins/imagine-pilotage'
OUT = ROOT / 'production/C-01/tests'
STATE = OUT / 'runner-state.json'
DOCKER = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker']
LABEL = 'org.imagine.c01-runner'


def call(args, data=None, check=True):
    p = subprocess.run(DOCKER + args, input=data, capture_output=True, timeout=600)
    if check and p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace') + p.stdout.decode(errors='replace'))
    return p


def info(name):
    i = json.loads(call(['inspect', name]).stdout)[0]
    assert i['Config']['Labels'].get(LABEL) == 'true'
    assert not i['Mounts'] and not i['HostConfig'].get('Binds')
    assert not i['HostConfig'].get('PortBindings') and not i['Config'].get('ExposedPorts')
    assert not i['HostConfig']['Privileged']
    assert 'ALL' in i['HostConfig']['CapDrop']
    assert 'no-new-privileges' in i['HostConfig']['SecurityOpt']
    return i


def payload():
    b = io.BytesIO()
    files = {}
    with tarfile.open(fileobj=b, mode='w') as tar:
        for p in sorted(PLUGIN.rglob('*')):
            if not p.is_file() or 'vendor' in p.parts or p.name == '.gitkeep':
                continue
            rel = p.relative_to(PLUGIN).as_posix()
            content = p.read_bytes()
            files[rel] = hashlib.sha256(content).hexdigest()
            ti = tarfile.TarInfo(rel)
            ti.size = len(content)
            ti.mode = 0o644
            tar.addfile(ti, io.BytesIO(content))
    return b.getvalue(), files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run', 'close'])
    parser.add_argument('--name', default='green')
    parser.add_argument('--filter')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.action == 'prepare':
        assert not STATE.exists(), 'Close the preceding owned runner first'
        name = 'imagine-c01-' + uuid.uuid4().hex[:12]
        # Reuse the existing PHP 8.2 image, never pull or alter a service.
        image = json.loads(call(['image', 'inspect', 'php:8.2-cli']).stdout)[0]['Id']
        call(['create', '--name', name, '--label', LABEL + '=true', '--network', 'bridge',
              '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--pids-limit', '128',
              '--memory', '512m', '--cpus', '1', '--entrypoint', 'sleep', image, 'infinity'])
        STATE.write_text(json.dumps({'container': name, 'image': image}), encoding='utf-8')
        call(['start', name])
        info(name)
        packages = call(['exec', name, 'sh', '-c', 'apt-get update -qq && apt-get install -y --no-install-recommends unzip'])
        (OUT / 'runner-packages.log').write_bytes(packages.stdout + packages.stderr)
        phar = urllib.request.urlopen('https://getcomposer.org/composer-stable.phar', timeout=90).read()
        sha = urllib.request.urlopen('https://getcomposer.org/composer-stable.phar.sha256sum', timeout=90).read().decode().split()[0]
        assert hashlib.sha256(phar).hexdigest() == sha
        call(['exec', '-i', name, 'sh', '-c', 'cat > /tmp/composer.phar'], phar)
        call(['exec', name, 'mkdir', '-p', '/work'])
        tar, files = payload()
        call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/work'], tar)
        p = call(['exec', '-w', '/work', '-e', 'COMPOSER_ALLOW_SUPERUSER=1', name, 'php', '/tmp/composer.phar',
                  'install', '--no-interaction', '--no-progress', '--prefer-dist', '--no-scripts', '--no-plugins'], check=False)
        (OUT / 'composer-install.log').write_bytes(p.stdout + p.stderr)
        if p.returncode:
            raise RuntimeError('Composer failed; see composer-install.log; close runner')
        lock = call(['exec', name, 'cat', '/work/composer.lock']).stdout
        (PLUGIN / 'composer.lock').write_bytes(lock)
        call(['network', 'disconnect', 'bridge', name])
        i = info(name)
        assert not i['NetworkSettings']['Networks']
        (OUT / 'preparation.json').write_text(json.dumps({
            'image': image, 'composer_sha256': sha, 'php': call(['exec', name, 'php', '-v']).stdout.decode(),
            'composer': call(['exec', name, 'php', '/tmp/composer.phar', '--version']).stdout.decode(),
            'no_mounts': True, 'no_ports': True, 'networks_after_preparation': i['NetworkSettings']['Networks'],
            'database': 'none', 'wordpress': 'none', 'composer_install_exit': p.returncode
        }, indent=2), encoding='utf-8')
        print('PREPARED', name)
        return
    state = json.loads(STATE.read_text(encoding='utf-8'))
    name = state['container']
    if args.action == 'close':
        info(name)
        call(['rm', '-f', name])
        p = call(['inspect', name], check=False)
        assert p.returncode != 0
        (OUT / 'cleanup.json').write_text(json.dumps({'owned_runner_removed': True, 'container': name}), encoding='utf-8')
        STATE.unlink()
        print('CLOSED', name)
        return
    i = info(name)
    assert not i['NetworkSettings']['Networks'], 'Tests require network disconnected'
    tar, files = payload()
    call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/work'], tar)
    command = ['exec', '-w', '/work', name, 'php', '/tmp/composer.phar', 'test', '--',
               '--log-junit', '/tmp/result.xml']
    if args.filter:
        command += ['--filter', args.filter]
    p = call(command, check=False)
    lint = call(['exec', '-w', '/work', name, 'php', '/tmp/composer.phar', 'lint'], check=False)
    syntax = call(['exec', '-w', '/work', name, 'sh', '-c',
                   'find src tests -name "*.php" -exec php -l {} \\;'], check=False)
    version = call(['exec', name, 'php', '-r', 'echo PHP_VERSION;']).stdout.decode()
    xml = call(['exec', name, 'cat', '/tmp/result.xml'], check=False)
    (OUT / (args.name + '.log')).write_bytes(p.stdout + p.stderr)
    (OUT / (args.name + '-lint.log')).write_bytes(lint.stdout + lint.stderr + syntax.stdout + syntax.stderr)
    if xml.returncode == 0:
        (OUT / (args.name + '.xml')).write_bytes(xml.stdout)
    receipt = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'php': version,
               'command': 'composer test' + (' -- --filter ' + args.filter if args.filter else ''),
               'exit_code': p.returncode, 'psr12_exit_code': lint.returncode, 'syntax_exit_code': syntax.returncode,
               'source_sha256': files, 'network_disconnected': True, 'no_mounts': True, 'no_ports': True}
    (OUT / (args.name + '.json')).write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(p.stdout.decode(errors='replace') + p.stderr.decode(errors='replace'))
    print(lint.stdout.decode(errors='replace') + lint.stderr.decode(errors='replace'))
    print(json.dumps({k: v for k, v in receipt.items() if k != 'source_sha256'}))
    raise SystemExit(p.returncode or lint.returncode or syntax.returncode)


if __name__ == '__main__':
    main()
