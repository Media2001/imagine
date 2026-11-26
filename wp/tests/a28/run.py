"""Owned disposable A28 runner; no API/site, no real archive, no Docker sweep."""
import argparse
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
sys.path.insert(0, str(ROOT / 'wp/outils/staging-court'))
import publish

LABEL = 'org.imagine.a28-synthetic'
publish.LABEL = LABEL


def transfer(name, pairs):
    stream = io.BytesIO()
    manifest = {}
    with tarfile.open(fileobj=stream, mode='w') as tar:
        for source, dest in pairs:
            raw = source.read_bytes()
            manifest[source.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
            info = tarfile.TarInfo(dest)
            info.size = len(raw)
            tar.addfile(info, io.BytesIO(raw))
    publish.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/'], stream.getvalue())
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--unit-only', action='store_true')
    parser.add_argument('--regression-only', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-test-a28-' + uuid.uuid4().hex[:12]
    receipt = {'status': 'FAIL', 'runner': name, 'owner_label': LABEL, 'synthetic_only': True,
               'commands': [], 'baseline': args.baseline}
    created = False
    manifest = {}
    try:
        image = json.loads(publish.call(['image', 'inspect', publish.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        publish.call(['create', '--pull', 'never', '--name', name, '--label', LABEL + '=true', '--network', 'none',
            '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--memory', '2g', '--cpus', '2',
            '--pids-limit', '256', '--no-healthcheck', '--log-driver', 'none', '--entrypoint', 'sleep', image['Id'], 'infinity'])
        created = True
        receipt['isolation_before'] = publish.offline_isolation(name)
        (out / 'handle.json').write_text(json.dumps({'name': name, 'label': LABEL, 'value': 'true',
            'image': image['Id'], 'isolation': receipt['isolation_before']}, indent=2), encoding='utf-8')
        print('A28_RUNNER ' + name, flush=True)
        publish.call(['start', name])
        payload, manifest = publish.offline_runner.payload(True)
        publish.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/'], payload)
        pairs = [(p, 'opt/a28/' + p.name) for p in Path(__file__).parent.iterdir() if p.suffix in ('.py', '.php')]
        pairs += [(p, 'checkout/' + p.relative_to(ROOT).as_posix()) for p in (ROOT / 'wp/tests/a01-court').iterdir() if p.suffix in ('.py', '.php')]
        pairs += [(p, 'checkout/' + p.relative_to(ROOT).as_posix()) for p in (ROOT / 'wp/outils/staging-court').iterdir() if p.suffix in ('.py', '.php', '.json')]
        pairs += [(ROOT/'wp/outils/staging-wp-integration/worker/worker.py', 'checkout/wp/outils/staging-court/legacy_importer.py')]
        for path in ('publication-23nov/52170a14f7a7/result.json', 'publication-22nov/a6ca179f2442/result.json', 'publication-22nov/79cef0705045/result.json'):
            p = ROOT / 'production/A-01' / path
            pairs.append((p, 'checkout/' + p.relative_to(ROOT).as_posix()))
        # The fixed staging payload list is the deployed contract; new dependencies must be there, not hidden here.
        manifest.update(transfer(name, pairs))

        def run(key, argv, copy=None):
            p = publish.call(['exec', '-e', 'PYTHONDONTWRITEBYTECODE=1', '-e', 'PYTHONIOENCODING=utf-8', name] + argv, check=False, timeout=1800)
            (out / (key + '.stdout.log')).write_bytes(p.stdout)
            (out / (key + '.stderr.log')).write_bytes(p.stderr)
            receipt['commands'].append({'key': key, 'argv': argv, 'exit': p.returncode,
                                       'stdout_sha256': hashlib.sha256(p.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(p.stderr).hexdigest()})
            if copy:
                raw = publish.call(['exec', name, 'cat', copy], check=False)
                if raw.returncode == 0:
                    (out / (key + '.json')).write_bytes(raw.stdout)
            if p.returncode:
                raise RuntimeError('A28_COMMAND_FAILED:' + key)

        if args.unit_only:
            publish.call(['exec', name, 'mkdir', '-p', '/report'])
            run('unit', ['php', '/opt/a28/unit.php'], '/report/unit.json')
        else:
            if not args.regression_only:
                run('native', ['python3', '/opt/a28/inside.py'] + (['baseline'] if args.baseline else []), '/report/a28-native.json')
            if not args.baseline:
                publish.call(['exec', name, 'mkdir', '-p', '/scratch/a01-unit', '/root/AppData/Local/hermes/cache/scratch', '/report'])
                run('a01-python', ['env', 'TMPDIR=/scratch/a01-unit', 'python3', '-m', 'unittest', 'discover', '-s', '/checkout/wp/tests/a01-court', '-p', 'test_*.py', '-v'])
                run('a01-data', ['env', 'PHP_BIN=/usr/bin/php', 'IMAGINE_TEST_SCRATCH=/scratch/a01-unit', 'python3',
                                 '/checkout/wp/tests/staging-data/verify.py', '--output', '/report/a01-data.json'], '/report/a01-data.json')
                for f in ('test_database_policy.php', 'test_diagnostics.php', 'test_native_file_policy.php'):
                    run('a01-' + f[:-4], ['php', '/checkout/wp/tests/a01-court/' + f])
                if (Path(__file__).parent / 'unit.php').is_file():
                    run('unit', ['php', '/opt/a28/unit.php'], '/report/unit.json')
        receipt['isolation_after'] = publish.offline_isolation(name)
        receipt['sources_unchanged'] = all(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest for rel, digest in manifest.items())
        assert receipt['sources_unchanged']
        receipt['status'] = 'PASS'
    except Exception as error:
        receipt['error'] = {'class': type(error).__name__, 'code': str(error)}
    finally:
        if created:
            receipt['cleanup'] = publish.remove_owned(name)
        receipt['source_manifest'] = manifest
        (out / 'runner.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({'status': receipt['status'], 'report': str(out / 'runner.json')}))
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
