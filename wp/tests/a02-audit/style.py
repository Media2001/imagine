"""Optional PSR-12 check in an owned container, no host PHP or downloads."""
import hashlib
import json
import pathlib
import sys
import uuid
sys.dont_write_bytecode = True
import run


def main():
    tool = pathlib.Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a02-phpcs.phar')
    expected = '204214c1ea5ba814fb0b2608c19cca2c10bf5ffcc9f0e3d4c34aadc0179517b7'
    assert hashlib.sha256(tool.read_bytes()).hexdigest() == expected
    name = 'imagine-a02-audit-style-' + uuid.uuid4().hex[:12]
    created = False
    result = {'phpcs_sha256': expected, 'exit_code': 1}
    out = run.REPO / 'production/A-02/style'
    out.mkdir(exist_ok=True)
    try:
        run.call(['create', '--name', name, '--label', run.LABEL + '=' + name, '--network', 'none', '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--pull', 'never', '--entrypoint', '/bin/sleep', run.IMAGE, 'infinity'])
        created = True
        run.validate(json.loads(run.call(['inspect', name]).stdout)[0], name)
        run.call(['start', name]); run.call(['exec', name, 'mkdir', '/subject'])
        run.call(['cp', run.local(tool), name + ':/phpcs.phar'])
        files = [run.SUBJECT] + list(run.ROOT.glob('*.php'))
        targets = []
        for file in files:
            target = '/subject/' + ('audit.php' if file == run.SUBJECT else file.name)
            targets.append(target)
            run.call(['cp', run.local(file), name + ':' + target])
        p = run.call(['exec', name, 'php', '/phpcs.phar', '--standard=PSR12', '--report=json'] + targets, check=False)
        (out / 'phpcs.json').write_text(p.stdout, encoding='utf8')
        (out / 'stderr.log').write_text(p.stderr, encoding='utf8')
        result['exit_code'] = p.returncode
        print(p.stdout)
    finally:
        if created:
            info = json.loads(run.call(['inspect', name]).stdout)[0]
            run.validate(info, name)
            run.call(['rm', '-f', name])
            missing = run.call(['inspect', name], check=False)
            result['container_absent'] = missing.returncode != 0 and 'no such object' in missing.stderr.lower()
        (out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    return result['exit_code']

if __name__ == '__main__':
    sys.exit(main())
