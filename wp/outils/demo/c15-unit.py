"""C15 pure PHP: isolated T01 image, no network, repository read-only."""
from pathlib import Path
import json
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[3]


def run(label='unit'):
    def docker(*args):
        return subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', *args], capture_output=True, text=True, encoding='utf-8', check=True).stdout
    image = json.loads(docker('image', 'inspect', 'imagine-tests-t01:1'))[0]
    assert image['Config']['Labels']['org.imagine.t01-image'] == '1'
    source = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', str(ROOT / 'wp').replace('\\', '/')], capture_output=True, text=True, check=True).stdout.strip()
    name = 'imagine-c15-unit-' + uuid.uuid4().hex
    try:
        docker('create', '--name', name, '--pull', 'never', '--network', 'none', '--read-only', '--user', '65534:65534', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--mount', 'type=bind,source=' + source + ',target=/repo/wp,readonly', '--entrypoint', 'php', image['Id'], '/repo/wp/tests/demo/c15-unit.php')
        info = json.loads(docker('inspect', name))[0]
        assert info['HostConfig']['NetworkMode'] == 'none' and info['HostConfig']['ReadonlyRootfs'] and not info['Mounts'][0]['RW']
        result = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'start', '-a', name], capture_output=True, text=True, encoding='utf-8')
        record = {'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'network': 'none'}
        proof = ROOT / 'production/C-15'; proof.mkdir(parents=True, exist_ok=True)
        (proof / (label + '.json')).write_text(json.dumps(record, indent=2), encoding='utf-8')
        print(result.stdout + result.stderr)
        if result.returncode:
            raise SystemExit(result.returncode)
        return json.loads(result.stdout)
    finally:
        docker('rm', '-f', name)


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'unit')
