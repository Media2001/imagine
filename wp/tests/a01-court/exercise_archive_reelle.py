"""Banc A-01 sans site : runner possédé, archives synthétiques, réseau coupé."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'wp/outils/staging-court'
sys.path.insert(0, str(TOOLS))
import publish


def main():
    out = ROOT / 'production/A-01/archive-reelle' / uuid.uuid4().hex[:12]
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a01-diag-test-' + uuid.uuid4().hex[:12]
    created = False
    result = {'status': 'FAIL', 'synthetic_only': True, 'created_sites': [], 'commands': []}
    files = list(TOOLS.glob('*.py')) + [TOOLS / 'politique-tables.json'] + list((ROOT / 'wp/tests/a01-court').glob('test_*.py'))
    files += [Path(__file__), ROOT / 'wp/outils/staging/schema.php', ROOT / 'wp/outils/staging/lib.php',
              ROOT / 'wp/outils/staging/policy.php', ROOT / 'wp/outils/staging-wp-integration/worker/worker.py']
    files += [ROOT / 'wp/tests/a01-court' / f for f in ('verify_publication.py', 'verify_correction_artifacts.py')]
    files += [TOOLS / 'script_capacity_probe.php', ROOT / 'production/A-01/publication-23nov/52170a14f7a7/result.json']
    files += [ROOT / 'production/A-01/publication-22nov' / case / 'result.json' for case in ('a6ca179f2442', '79cef0705045')]
    stream = io.BytesIO()
    manifest = {}
    with tarfile.open(fileobj=stream, mode='w') as tar:
        for path in files:
            raw = path.read_bytes()
            rel = path.relative_to(ROOT).as_posix()
            manifest[rel] = hashlib.sha256(raw).hexdigest()
            item = tarfile.TarInfo('checkout/' + rel)
            item.size = len(raw)
            tar.addfile(item, io.BytesIO(raw))
    try:
        image = json.loads(publish.call(['image', 'inspect', publish.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        publish.call(['create', '--pull', 'never', '--name', name, '--label', publish.LABEL + '=true',
                      '--network', 'none', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                      '--no-healthcheck', '--log-driver', 'none', '--entrypoint', 'sleep', publish.IMAGE, 'infinity'])
        created = True
        result['isolation_before'] = publish.offline_isolation(name)
        publish.call(['start', name])
        publish.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/'], stream.getvalue())
        publish.call(['exec', name, 'mkdir', '-p', '/scratch/tests', '/root/AppData/Local/hermes/cache/scratch'])
        command = ['exec', '-e', 'PYTHONDONTWRITEBYTECODE=1', '-e', 'TMPDIR=/scratch/tests',
                   '-e', 'PYTHONPATH=/checkout/wp/outils/staging-court', name, 'python3', '-m', 'unittest', 'discover',
                   '-s', '/checkout/wp/tests/a01-court', '-p', sys.argv[1] if len(sys.argv) > 1 else 'test_archive_reelle.py', '-v']
        p = publish.call(command, check=False)
        (out / 'tests.log').write_bytes(p.stdout + p.stderr)
        result['commands'].append({'argv': command, 'exit': p.returncode})
        result['isolation_after'] = publish.offline_isolation(name)
        result['source_manifest'] = manifest
        assert all(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == sha for rel, sha in manifest.items())
        result['sources_unchanged'] = True
        result['status'] = 'PASS' if p.returncode == 0 else 'FAIL'
    finally:
        if created:
            result['cleanup'] = publish.remove_owned(name)
        (out / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'status': result['status'], 'report': str(out / 'result.json')}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
