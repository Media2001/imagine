"""C10 : Composer existant, image T01 hors réseau, aucun montage ni installation."""
from pathlib import Path
import io
import json
import subprocess
import sys
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
NAME = 'imagine-c10-correction'
D = ['wsl.exe', 'docker']


def call(args, data=None):
    return subprocess.run(D + args, input=data, capture_output=True, timeout=600)


def run(label, filtered=False):
    info = json.loads(call(['inspect', NAME]).stdout)[0]
    assert info['Config']['Labels']['org.imagine.c10-correction'] == 'true'
    assert not info['Mounts'] and not info['HostConfig']['PortBindings']
    assert info['HostConfig']['NetworkMode'] == 'none'
    assert not info['HostConfig']['Privileged']
    plugin = ROOT / 'wp/plugins/imagine-pilotage'
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode='w') as archive:
        for path in plugin.rglob('*'):
            if path.is_file() and 'vendor' not in path.parts:
                archive.add(path, arcname='c10/' + path.relative_to(plugin).as_posix())
        for path in (ROOT / 'wp/plugins/imagine-connecteur/src').rglob('*.php'):
            archive.add(path, arcname='imagine-connecteur/src/' + path.relative_to(ROOT / 'wp/plugins/imagine-connecteur/src').as_posix())
    prep = call(['exec', NAME, 'sh', '-c', 'mkdir -p /tmp/c10; cp -a /opt/t01/imagine-pilotage/vendor /tmp/c10/; rm -rf /tmp/c10/src /tmp/c10/tests; rm -f /tmp/c10/result.xml'])
    assert prep.returncode == 0, prep.stderr
    p = call(['exec', '-i', NAME, 'tar', '-xf', '-', '-C', '/tmp'], payload.getvalue())
    assert p.returncode == 0, p.stderr
    command = ['exec', '-w', '/tmp/c10', '-e', 'COMPOSER_ROOT_VERSION=dev-main',
               NAME, 'composer', 'test', '--', '--log-junit', '/tmp/c10/result.xml']
    if filtered:
        command += ['--testsuite', 'Administration']
    result = call(command)
    lint = call(['exec', '-w', '/tmp/c10', '-e', 'COMPOSER_ROOT_VERSION=dev-main', NAME, 'composer', 'lint'])
    out = ROOT / 'production/C-10'
    (out / (label + '-phpunit.log')).write_bytes(result.stdout + result.stderr)
    (out / (label + '-lint.log')).write_bytes(lint.stdout + lint.stderr)
    xml = call(['exec', NAME, 'cat', '/tmp/c10/result.xml'])
    if xml.returncode == 0:
        (out / (label + '-phpunit.xml')).write_bytes(xml.stdout)
        tree = ET.fromstring(xml.stdout)
        facade = [t for t in tree.iter('testcase') if '\\Administration\\ReglagesTest' in t.attrib.get('class', '')]
        assert len(facade) == 10, 'La suite façade doit être découverte par Composer'
    receipt = {'command': 'composer test -- --log-junit /tmp/c10/result.xml' + (' --testsuite Administration' if filtered else ''), 'test_exit': result.returncode,
               'lint_command': 'composer lint', 'lint_exit': lint.returncode,
               'image': info['Config']['Image'], 'network': 'none', 'mounts': [], 'ports': {}}
    (out / (label + '-unit.json')).write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(result.stdout.decode(errors='replace') + result.stderr.decode(errors='replace'))
    print(lint.stdout.decode(errors='replace') + lint.stderr.decode(errors='replace'))
    print(json.dumps(receipt))
    return result.returncode or lint.returncode


if __name__ == '__main__':
    raise SystemExit(run(sys.argv[1], '--facade' in sys.argv))
