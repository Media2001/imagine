"""C18 PHPUnit on the prepared offline image; shared C16 launcher is unchanged."""
from pathlib import Path
import json, re, subprocess, sys, uuid
ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/C-18'


def run(label='unit-final', selection='ExtractionsReglesTest'):
    if not re.fullmatch(r'[a-z0-9-]+', label):
        raise ValueError('Receipt label refused')
    def docker(*args, check=True):
        p = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', *args], capture_output=True, text=True, encoding='utf-8')
        if check and p.returncode:
            raise RuntimeError(p.stdout + p.stderr)
        return p
    source = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', str(ROOT / 'wp').replace('\\','/')], capture_output=True, text=True, check=True).stdout.strip()
    image = json.loads(docker('image', 'inspect', 'imagine-tests-t01:1').stdout)[0]
    assert image['Config']['Labels']['org.imagine.t01-image'] == '1'
    owner = uuid.uuid4().hex
    name = 'imagine-c18-unit-' + owner
    created = False
    result = {'exit': 1, 'removed': False, 'selection': selection, 'image': image['Id']}
    try:
        docker('create', '--name', name, '--label', 'org.imagine.c18-unit=' + owner,
               '--pull', 'never', '--network', 'none', '--read-only', '--user', '65534:65534',
               '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m,mode=1777',
               '--mount', 'type=bind,source=' + source + ',target=/repo/wp,readonly', '--entrypoint', 'php', image['Id'],
               '/repo/wp/tests/demo/c16-unit-runtime.php', selection)
        created = True
        info = json.loads(docker('inspect', name).stdout)[0]
        assert info['HostConfig']['NetworkMode'] == 'none' and info['HostConfig']['ReadonlyRootfs']
        assert len(info['Mounts']) == 1 and not info['Mounts'][0]['RW'] and info['Image'] == image['Id']
        assert not info['HostConfig']['PortBindings'] and info['HostConfig']['CapDrop'] == ['ALL']
        p = docker('start', '-a', name, check=False)
        state = json.loads(docker('inspect', name).stdout)[0]['State']
        result.update(exit=p.returncode or state['ExitCode'], stdout=p.stdout, stderr=p.stderr, network='none')
        counts = re.search(r'OK \((\d+) tests?, (\d+) assertions?\)', p.stdout)
        if counts:
            result.update(tests=int(counts[1]), assertions=int(counts[2]))
            print(counts[0])
        else:
            print(p.stdout + p.stderr)
    finally:
        if created:
            info = json.loads(docker('inspect', name).stdout)[0]
            assert info['Config']['Labels']['org.imagine.c18-unit'] == owner
            docker('rm', '-f', name)
            absent = docker('inspect', name, check=False)
            result['removed'] = bool(absent.returncode and 'no such' in (absent.stdout + absent.stderr).lower())
        PROOF.mkdir(parents=True, exist_ok=True)
        (PROOF / (label + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    assert result['removed']
    return result['exit']


if __name__ == '__main__':
    selection = sys.argv[2] if len(sys.argv) > 2 else 'ExtractionsReglesTest'
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else 'unit-final', '' if selection == '--root' else selection))
