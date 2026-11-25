"""C13 pur, aucun site ni réseau, dépôt en lecture seule. Aussi découvert par T01."""
from pathlib import Path
import json
import re
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[3]


def run():
    name = 'imagine-c13-unit-' + uuid.uuid4().hex
    owner = uuid.uuid4().hex

    def docker(*args, check=True):
        p = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', *args],
                           capture_output=True, text=True, encoding='utf-8')
        if check and p.returncode:
            raise RuntimeError(p.stdout + p.stderr)
        return p

    source = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', str(ROOT / 'wp').replace('\\', '/')],
                            capture_output=True, text=True, check=True).stdout.strip()
    image = json.loads(docker('image', 'inspect', 'imagine-tests-t01:1').stdout)[0]
    if image['Config'].get('Labels', {}).get('org.imagine.t01-image') != '1':
        raise RuntimeError('Image inconnue')
    try:
        docker('create', '--name', name, '--label', 'org.imagine.c13-unit=' + owner,
               '--pull', 'never', '--network', 'none', '--read-only', '--user', '65534:65534',
               '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
               '--mount', 'type=bind,source=' + source + ',target=/repo/wp,readonly',
               '--entrypoint', 'php', image['Id'], '/opt/t01/imagine-site/vendor/bin/phpunit',
               '--configuration', '/repo/wp/plugins/imagine-site/phpunit.c13.xml',
               '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--fail-on-skipped',
               '--fail-on-incomplete', '--do-not-cache-result', '--colors=never')
        info = json.loads(docker('inspect', name).stdout)[0]
        if (info['HostConfig']['NetworkMode'] != 'none' or not info['HostConfig']['ReadonlyRootfs']
                or len(info['Mounts']) != 1 or info['Mounts'][0]['RW'] or info['Image'] != image['Id']):
            raise RuntimeError('Isolation refusée')
        p = docker('start', '-a', name, check=False)
        print(p.stdout + p.stderr)
        state = json.loads(docker('inspect', name).stdout)[0]['State']
        match = re.search(r'OK \((\d+) tests?, (\d+) assertions?\)', p.stdout)
        if p.returncode or state['ExitCode'] or not match:
            raise RuntimeError('Suite pure C13 rouge')
        return {'tests': int(match[1]), 'assertions': int(match[2]), 'succes': True, 'network': 'none'}
    finally:
        probe = docker('inspect', name, check=False)
        if probe.returncode == 0:
            info = json.loads(probe.stdout)[0]
            if info['Config'].get('Labels', {}).get('org.imagine.c13-unit') != owner:
                raise RuntimeError('Propriété du conteneur refusée')
            docker('rm', '-f', name)
            absent = docker('inspect', name, check=False)
            if absent.returncode == 0 or 'no such' not in (absent.stdout + absent.stderr).lower():
                raise RuntimeError('Absence non relue')


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False))
