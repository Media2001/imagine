"""Prepare real AI1WM exports in an owned offline container; no site API."""
import hashlib
import io
import json
from pathlib import Path
import secrets
import sys
import tarfile
import uuid
import zipfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/staging-court'))
import publish


def main():
    run = uuid.uuid4().hex[:12]
    name = 'imagine-test-a01-ai1wm-' + run
    out = ROOT / 'production/A-01/archive-reelle-2' / run
    out.mkdir(parents=True, exist_ok=False)
    result = {'status': 'PREPARING', 'name': name, 'synthetic_only': True, 'created': False, 'output': str(out)}
    package = Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a01-ai1wm-7.109.zip')
    if not package.exists():
        # Public dependency preparation is completed before the offline runner.
        from core_source import download
        raw = download('https://downloads.wordpress.org/plugin/all-in-one-wp-migration.7.109.zip')
        assert hashlib.sha256(raw).hexdigest() == 'cc592ad8e929d6ddb14b46a70dc840a0571f8bd6addda36a9bbf007d0bb3b72f'
        package.write_bytes(raw)
    assert hashlib.sha256(package.read_bytes()).hexdigest() == 'cc592ad8e929d6ddb14b46a70dc840a0571f8bd6addda36a9bbf007d0bb3b72f'
    def save():
        (out / 'prepare.json').write_text(json.dumps(result, indent=2))
    save()
    try:
        image = json.loads(publish.call(['image', 'inspect', publish.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        publish.call(['create', '--pull', 'never', '--name', name, '--label', publish.LABEL + '=true', '--network', 'none',
                      '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--memory', '1g', '--cpus', '2',
                      '--pids-limit', '256', '--log-driver', 'none', '--entrypoint', 'sleep', publish.IMAGE, 'infinity'])
        result['created'] = True; save()
        publish.call(['start', name])
        result['isolation'] = publish.offline_isolation(name); save()
        # Send only public dependency + explicitly named fixture and subject files.
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode='w') as tar:
            for path, dest in [(ROOT / 'wp/outils/staging-court/inside.py', 'opt/court/inside.py'),
                               (ROOT / 'wp/tests/a01-court/ai1wm_export_fixture.php', 'opt/fixture.php')]:
                data = path.read_bytes(); item = tarfile.TarInfo(dest); item.size = len(data); tar.addfile(item, io.BytesIO(data))
            with zipfile.ZipFile(package) as z:
                for info in z.infolist():
                    if info.is_dir(): continue
                    assert info.filename.startswith('all-in-one-wp-migration/') and '..' not in info.filename.split('/')
                    data = z.read(info); item = tarfile.TarInfo('opt/public/' + info.filename); item.size = len(data); tar.addfile(item, io.BytesIO(data))
        publish.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/'], stream.getvalue())
        program = (ROOT / 'wp/tests/a01-court/ai1wm_prepare_inside.py').read_bytes()
        execution = publish.call(['exec', '-i', name, 'python3', '-'], program, check=False, timeout=1800)
        (out / 'prepare.log').write_bytes(execution.stdout + execution.stderr)
        result['exit'] = execution.returncode
        if execution.returncode: raise RuntimeError('REAL_EXPORT_PREPARE_FAILED')
        for case in ('small', 'large'):
            result[case] = publish.read_json(name, '/report/export-' + case + '.json')
        result['status'] = 'PREPARED'; save()
    except Exception as exc:
        result.update(status='FAIL', error=type(exc).__name__ + ':' + str(exc)); save()
        if result['created']:
            result['cleanup'] = publish.remove_owned(name); save()
        raise
    print(json.dumps(result))


if __name__ == '__main__':
    main()
