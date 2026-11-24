"""PHPUnit C11 hors ligne : réutilise les dépendances T01 sans modifier son image."""
from pathlib import Path
import json
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[3]


def docker(*args, check=True):
    result = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', *args],
                            capture_output=True, text=True, encoding='utf-8')
    if check and result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result


def run():
    name = 'imagine-c11-unit-' + uuid.uuid4().hex
    owner = uuid.uuid4().hex
    image = json.loads(docker('image', 'inspect', 'imagine-tests-t01:1').stdout)[0]
    if image['Config'].get('Labels', {}).get('org.imagine.t01-image') != '1':
        raise RuntimeError('Image T01 non reconnue')
    source = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', str(ROOT / 'wp').replace('\\', '/')],
                            capture_output=True, text=True, check=True).stdout.strip()
    created = False
    try:
        created = True
        docker('create', '--name', name, '--label', 'org.imagine.c11-unit=' + owner,
               '--pull', 'never', '--network', 'none', '--read-only',
               '--mount', 'type=bind,source=' + source + ',target=/repo/wp,readonly',
               '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m,mode=1777', '--user', '65534:65534',
               '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--pids-limit', '128',
               '--memory', '256m', '--cpus', '2', '--no-healthcheck', '--log-driver', 'none',
               '--entrypoint', 'timeout', image['Id'], '120', 'php',
               '/opt/t01/imagine-pilotage/vendor/bin/phpunit',
               '--configuration', '/repo/wp/plugins/imagine-site/phpunit.c11.xml',
               '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--fail-on-skipped',
               '--fail-on-incomplete', '--do-not-cache-result', '--colors=never')
        info = json.loads(docker('inspect', name).stdout)[0]
        host = info['HostConfig']
        if (host['NetworkMode'] != 'none' or not host['ReadonlyRootfs'] or host['Privileged']
                or info['Image'] != image['Id'] or len(info['Mounts']) != 1
                or info['Mounts'][0]['RW'] or info['Mounts'][0]['Destination'] != '/repo/wp'
                or host.get('PortBindings') or info['Config'].get('ExposedPorts')):
            raise RuntimeError('Isolation C11 refusée')
        result = docker('start', '-a', name, check=False)
        print(result.stdout + result.stderr)
        state = json.loads(docker('inspect', name).stdout)[0]['State']
        if result.returncode or state['ExitCode'] or state['Running']:
            raise SystemExit(1)
    finally:
        if created:
            probe = docker('inspect', name, check=False)
            if probe.returncode == 0:
                info = json.loads(probe.stdout)[0]
                if info['Config'].get('Labels', {}).get('org.imagine.c11-unit') != owner:
                    raise RuntimeError('Propriété du conteneur C11 refusée')
                docker('container', 'rm', '-f', name)
                absent = docker('inspect', name, check=False)
                if absent.returncode == 0 or 'No such' not in absent.stderr:
                    raise RuntimeError('Absence du conteneur C11 non vérifiée')
                print('C11 PHPUnit : conteneur propre supprimé, absence relue.')
            elif 'No such' not in probe.stderr:
                raise RuntimeError('État du conteneur C11 indéterminé')


if __name__ == '__main__':
    run()
