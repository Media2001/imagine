"""C-03: reuse the owned disposable bench; never rewrite C-01 lock/evidence."""
import importlib.util
import sys
import pathlib
import json
import hashlib
import urllib.request
import uuid

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('c01_bench', ROOT / 'wp/tests/numeros-runner/run.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
bench.OUT = ROOT / 'production/C-03/tests'
bench.STATE = bench.OUT / 'runner-state.json'
bench.LABEL = 'org.imagine.c03-runner'


def prepare():
    bench.OUT.mkdir(parents=True, exist_ok=True)
    assert not bench.STATE.exists(), 'Close preceding owned runner first'
    name = 'imagine-c03-' + uuid.uuid4().hex[:12]
    image = json.loads(bench.call(['image', 'inspect', 'imagine-staging-e2e-public:644662e9cc4f']).stdout)[0]['Id']
    bench.call(['create', '--name', name, '--label', bench.LABEL + '=true', '--network', 'bridge',
                '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--pids-limit', '128',
                '--memory', '512m', '--cpus', '1', '--entrypoint', 'sleep', image, 'infinity'])
    bench.STATE.write_text(json.dumps({'container': name, 'image': image}), encoding='utf-8')
    bench.call(['start', name])
    bench.info(name)
    phar = urllib.request.urlopen('https://getcomposer.org/composer-stable.phar', timeout=90).read()
    sha = urllib.request.urlopen('https://getcomposer.org/composer-stable.phar.sha256sum', timeout=90).read().decode().split()[0]
    assert hashlib.sha256(phar).hexdigest() == sha
    bench.call(['exec', '-i', name, 'sh', '-c', 'cat > /tmp/composer.phar'], phar)
    bench.call(['exec', name, 'mkdir', '-p', '/work'])
    tar, files = bench.payload()
    bench.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/work'], tar)
    p = bench.call(['exec', '-w', '/work', '-e', 'COMPOSER_ALLOW_SUPERUSER=1',
                    '-e', 'COMPOSER_ROOT_VERSION=dev-main', name, 'php', '/tmp/composer.phar',
                    'install', '--no-interaction', '--no-progress', '--prefer-dist', '--no-scripts', '--no-plugins'], check=False)
    (bench.OUT / 'composer-install.log').write_bytes(p.stdout + p.stderr)
    assert p.returncode == 0, 'Composer install failed; close runner'
    lock = bench.call(['exec', name, 'cat', '/work/composer.lock']).stdout
    assert lock == (bench.PLUGIN / 'composer.lock').read_bytes(), 'Locked dependencies drifted'
    bench.call(['network', 'disconnect', 'bridge', name])
    i = bench.info(name)
    assert not i['NetworkSettings']['Networks']
    (bench.OUT / 'preparation.json').write_text(json.dumps({
        'image': image, 'composer_sha256': sha,
        'php': bench.call(['exec', name, 'php', '-v']).stdout.decode(),
        'composer': bench.call(['exec', name, 'php', '/tmp/composer.phar', '--version']).stdout.decode(),
        'no_mounts': True, 'no_ports': True, 'networks_after_preparation': i['NetworkSettings']['Networks'],
        'database': 'none', 'wordpress': 'none', 'composer_install_exit': p.returncode,
        'host_lock_unchanged': True, 'label': bench.LABEL
    }, indent=2), encoding='utf-8')
    print('PREPARED', name)


if __name__ == '__main__':
    if sys.argv[1:] == ['prepare']:
        prepare()
    else:
        if '--filter' in sys.argv:
            import re
            value = sys.argv[sys.argv.index('--filter') + 1]
            if re.fullmatch(r'[A-Za-z0-9_]+', value) is None:
                raise SystemExit('Use only a simple class/method name as --filter (WSL transport).')
        if sys.argv[1:2] == ['run']:
            state = json.loads(bench.STATE.read_text(encoding='utf-8'))
            name = state['container']
            info = bench.info(name)
            assert not info['NetworkSettings']['Networks']
            bench.call(['exec', name, 'rm', '-f', '/tmp/result.xml'])
        bench.main()
