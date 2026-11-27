"""Run strict, unmodified PSR12 only in an owned disconnected PHP container."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
ROOT = Path(__file__).resolve().parents[3]
FILES = ['wp/outils/staging/' + n for n in ('lib.php', 'engine.php', 'store.php', 'guard.php', 'form-decision-refused.php')]
FILES += ['wp/tests/a28/unit.php', 'wp/tests/a28/seed.php']
DOCKER = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker'] if os.name == 'nt' else ['docker']
LABEL = 'org.imagine.a28-style'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-test-a28-style-' + uuid.uuid4().hex[:12]
    frozen = {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in FILES}
    result = {'status': 'FAIL', 'standard': 'PSR12', 'exclusions': [], 'runner': name,
              'sources': frozen, 'commands': [], 'cleanup': None}
    created = False

    def docker(argv):
        p = subprocess.run(DOCKER + argv, capture_output=True, timeout=180)
        result['commands'].append({'argv': argv, 'exit': p.returncode,
            'stdout_sha256': hashlib.sha256(p.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(p.stderr).hexdigest()})
        return p

    try:
        path = str(ROOT / 'wp').replace('\\', '/')
        if os.name == 'nt':
            p = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', path], capture_output=True, timeout=30)
            assert p.returncode == 0 and not p.stderr
            path = p.stdout.decode().strip()
        image = docker(['image', 'inspect', 'imagine-tests-t01:1'])
        assert image.returncode == 0
        image = json.loads(image.stdout)[0]
        result['image'] = image['Id']
        assert image['Config']['Labels']['org.imagine.t01-image'] == '1'
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        argv = ['create', '--pull', 'never', '--name', name, '--label', LABEL + '=true', '--network', 'none',
            '--read-only', '--tmpfs', '/tmp:rw,nosuid,nodev,size=32m,mode=1777', '--cap-drop', 'ALL',
            '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--pids-limit', '128',
            '--memory', '256m', '--no-healthcheck', '--log-driver', 'none',
            '--mount', 'type=bind,source=' + path + ',target=/repo/wp,readonly', '--entrypoint', 'php', image['Id'],
            '/opt/t01/imagine-non-regression/vendor/bin/phpcs', '--standard=PSR12', '--report=json']
        argv += ['/repo/' + rel for rel in FILES]
        p = docker(argv)
        assert p.returncode == 0
        created = True
        before = json.loads(docker(['inspect', name]).stdout)[0]
        h = before['HostConfig']
        assert before['Config']['Labels'][LABEL] == 'true' and h['NetworkMode'] == 'none'
        assert h['ReadonlyRootfs'] is True and not h['Privileged'] and not h.get('PortBindings')
        assert 'ALL' in h['CapDrop'] and 'no-new-privileges' in h['SecurityOpt']
        assert len(before['Mounts']) == 1 and before['Mounts'][0]['Destination'] == '/repo/wp'
        assert before['Mounts'][0]['RW'] is False
        result['isolation'] = {'network': 'none', 'readonly_root': True, 'readonly_wp_mount': True,
                               'privileged': False, 'cap_drop': h['CapDrop'], 'security_opt': h['SecurityOpt']}
        p = docker(['start', '-a', name])
        (out / 'phpcs.stdout.json').write_bytes(p.stdout)
        (out / 'phpcs.stderr.log').write_bytes(p.stderr)
        report = json.loads(p.stdout)
        result['exit'] = p.returncode
        result['totals'] = report['totals']
        after = json.loads(docker(['inspect', name]).stdout)[0]
        assert p.returncode == after['State']['ExitCode'] == 0 and not p.stderr
        assert report['totals']['errors'] == report['totals']['warnings'] == 0
        assert {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in FILES} == frozen
        result['status'] = 'PASS'
    finally:
        if created:
            owned = json.loads(docker(['inspect', name]).stdout)[0]
            assert owned['Config']['Labels'][LABEL] == 'true'
            assert docker(['rm', '-f', name]).returncode == 0
            absent = docker(['inspect', name])
            missing = b'no such object' in (absent.stdout + absent.stderr).lower()
            assert absent.returncode != 0 and missing
            result['cleanup'] = {'name': name, 'absent': True}
        (out / 'psr12.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'status': result['status'], 'totals': result.get('totals'), 'cleanup': result['cleanup']}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
