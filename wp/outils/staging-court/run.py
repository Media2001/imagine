"""Standalone A-01 offline operator command; never modifies the shared staging tool."""
import argparse
import datetime
import getpass
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import uuid
from diagnostics import execute, CommandFailure

ROOT = Path(__file__).resolve().parents[3]
LABEL = 'org.imagine.a01-court'
DOCKER = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker'] if os.name == 'nt' else ['docker']
DEFAULT_IMAGE = 'sha256:b2ffa6ad01ffacc6d31b176232c8d0779c0320daba381e05cbbd80f56d5327a0'
SUBJECT = ['neutraliser', 'anonymiser', 'verifier', 'command.php', 'lib.php', 'schema.php',
           'store.php', 'form-decision-refused.php', 'engine.php', 'guard.php',
           'files.php', 'pdo-store.php', 'runtime-probe.php', 'policy.php', 'form-policy.json', 'mu-plugins/000-imagine-staging-safety.php']
FIXTURE = ['inside.py', 'fixture.php', 'snapshot.php', 'oracle.php', 'mutate.php', 'db-probe.php',
           'mail-probe.php', 'worker-bridge.php', 'subject-preflight.php', 'fidelity.php', 'fidelity-mu.php',
           'licensed-fixture.php', 'subject-adapter.json']


def docker(args, data=None, check=True, timeout=600):
    return execute(DOCKER + args, input=data, capture_output=True, timeout=timeout,
                   stage='docker_' + args[0], check=check)


def inspect(name):
    info = json.loads(docker(['inspect', name]).stdout)[0]
    assert info['Config']['Labels'].get(LABEL) == 'true'
    assert info['HostConfig']['NetworkMode'] == 'none'
    assert not info['Mounts'] and not info['HostConfig'].get('PortBindings')
    assert not info['Config'].get('ExposedPorts') and not info['Config'].get('Volumes')
    assert not info['HostConfig']['Privileged'] and 'ALL' in info['HostConfig']['CapDrop']
    assert any(s.startswith('no-new-privileges') for s in info['HostConfig']['SecurityOpt'])
    return info


def payload(test):
    pairs = [(ROOT / 'wp/outils/staging' / f, 'subject/' + f) for f in SUBJECT]
    pairs += [(ROOT / 'wp/outils/staging-court' / f, 'opt/court/' + f)
              for f in ['archive.py', 'archive_policy.py', 'sql_stream.py', 'sql_compat.py', 'sql_diagnostic.py', 'diagnosis.py', 'table_policy.py', 'politique-tables.json', 'inside.py', 'bridge.php', 'core_source.py', 'diagnostics.py', 'database_only.py']]
    pairs.append((ROOT / 'wp/outils/staging-wp-integration/worker/worker.py', 'opt/court/legacy_importer.py'))
    pairs.append((ROOT / 'wp/outils/staging/schema.php', 'opt/staging/schema.php'))
    pairs.append((ROOT / 'wp/outils/staging/form-policy.json', 'opt/staging/form-policy.json'))
    if test:
        pairs += [(ROOT / 'wp/tests/staging-e2e' / f, 'opt/e2e/' + f) for f in FIXTURE + ['harness.py', 'test_harness.py']]
        pairs += [(ROOT / 'wp/tests/a01-court' / f, 'opt/court/' + f)
                  for f in ['roundtrip.py', 'export.php', 'test_archive.py']]
        pairs += [(ROOT / 'wp/outils/staging' / f, 'checkout/wp/outils/staging/' + f) for f in SUBJECT]
        pairs += [(p, 'checkout/wp/tests/staging-data/' + p.name)
                  for p in (ROOT / 'wp/tests/staging-data').iterdir()
                  if p.is_file() and p.suffix in {'.php', '.py'}]
    stream = io.BytesIO()
    manifest = {}
    with tarfile.open(fileobj=stream, mode='w') as tar:
        for source, dest in pairs:
            assert source.is_file() and not source.is_symlink()
            data = source.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
            manifest[source.relative_to(ROOT).as_posix()] = digest
            entry = tarfile.TarInfo(dest)
            entry.size = len(data)
            tar.addfile(entry, io.BytesIO(data))
    return stream.getvalue(), manifest


def main():
    parser = argparse.ArgumentParser(description='Restauration et vérification hors ligne, aucune publication web.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test', action='store_true')
    group.add_argument('--archive')
    parser.add_argument('--operator-ced', action='store_true', help='Import réservé à Ced, jamais un agent')
    parser.add_argument('--target-url')
    parser.add_argument('--production-url')
    parser.add_argument('--table-decisions')
    args = parser.parse_args()
    request = None
    if args.archive:
        if not args.operator_ced or not args.target_url or not args.production_url:
            parser.error('Ced uniquement : --operator-ced, --target-url et --production-url obligatoires')
        archive = Path(args.archive).resolve()
        if archive.is_symlink() or not archive.is_file() or archive.suffix.lower() != '.wpress':
            parser.error('Une archive .wpress régulière est requise, aucun repli.')
        decisions = json.loads(Path(args.table_decisions).read_text()) if args.table_decisions else {}
        request = {'target_url': args.target_url, 'production_url': args.production_url, 'decisions': decisions,
                   'password': getpass.getpass('Mot de passe neuf du compte test (20 à 72 octets) : ')}
    run_id = uuid.uuid4().hex[:12]
    out = ROOT / 'production/A-01/tests-21nov' / run_id
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a01-court-' + run_id
    created = False
    result = {'status': 'BLOCKED', 'issues': ['NOT_EXECUTED']}
    code = 1
    try:
        image = json.loads(docker(['image', 'inspect', DEFAULT_IMAGE]).stdout)[0]
        if image['Config'].get('Volumes') or image['Config'].get('ExposedPorts'):
            raise RuntimeError('IMAGE_ISOLATION_REFUSED')
        tar, manifest = payload(args.self_test)
        docker(['create', '--pull', 'never', '--name', name, '--label', LABEL + '=true', '--network', 'none',
                '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                '--memory', '2g', '--cpus', '2', '--pids-limit', '256', '--log-driver', 'none',
                '--entrypoint', 'sleep', image['Id'], 'infinity'])
        created = True
        inspect(name)
        docker(['start', name])
        docker(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/'], tar)
        (out / 'sources.json').write_text(json.dumps(manifest, indent=2))
        unit_results = {}
        if args.self_test:
            docker(['exec', name, 'mkdir', '-p', '/opt/data-scratch'])
            checks = {
                'archive': ['python3', '/opt/court/test_archive.py'],
                'harness': ['python3', '/opt/e2e/test_harness.py'],
                'data': ['env', 'PHP_BIN=/usr/bin/php', 'IMAGINE_TEST_SCRATCH=/opt/data-scratch',
                         'python3', '/checkout/wp/tests/staging-data/verify.py', '--output', '/report/data.json'],
                'new_php_syntax': ['sh', '-c', 'php -l /opt/court/bridge.php && php -l /opt/court/export.php'],
            }
            for key, cmd in checks.items():
                unit = docker(['exec', name] + cmd, check=False)
                (out / (key + '-tests.log')).write_bytes(unit.stdout + unit.stderr)
                unit_results[key] = {'exit': unit.returncode}
                if key == 'harness' and unit.returncode == 0:
                    unit_results[key]['receipt'] = json.loads(unit.stdout)
                if unit.returncode:
                    raise RuntimeError('UNIT_' + key.upper() + '_FAILED')
            for key, file in [('archive', 'archive-safety.json'), ('data', 'data.json')]:
                unit_results[key]['receipt'] = json.loads(docker(['exec', name, 'cat', '/report/' + file]).stdout)
        if args.archive:
            docker(['exec', name, 'mkdir', '-p', '/input'])
            # Operator-only execution. No agent uses this path in the synthetic test.
            archive_path = str(archive)
            if os.name == 'nt':
                archive_path = '/mnt/' + archive_path[0].lower() + archive_path[2:].replace('\\', '/')
            docker(['cp', archive_path, name + ':/input/source.wpress'])
        path = '/opt/court/roundtrip.py' if args.self_test else '/opt/court/inside.py'
        p = docker(['exec', '-i', name, 'python3', path], json.dumps(request).encode() if request else b'', check=False)
        (out / 'execution.json').write_text(json.dumps({'exit':p.returncode,'stage':'offline_execution',
            'raw_output_omitted':True}))
        code = p.returncode
        data = docker(['exec', name, 'cat', '/report/court.json'], check=False)
        if data.returncode == 0:
            result = json.loads(data.stdout)
        # Verify the delivered source batch again, not just the transport exit code.
        for rel, digest in manifest.items():
            assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest
        inspect(name)
        result['image_id'] = image['Id']
        result['unit_results'] = unit_results
        result['runner_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        result['source_manifest_verified'] = True
        result['no_ports_no_mounts_network_none'] = True
    except Exception as exc:
        result = {'status': 'BLOCKED', 'issues': [str(exc) if re.fullmatch(r'[A-Z0-9_]{1,80}', str(exc)) else 'EXECUTION_REFUSED']}
        result['failure'] = exc.failure if isinstance(exc,CommandFailure) else {'stage':'offline_runner','code':result['issues'][0]}
        code = 1
    finally:
        if created:
            if args.self_test:
                docker(['rm', '-f', name])
                assert docker(['inspect', name], check=False).returncode != 0
                result['owned_container_removed'] = True
            else:
                docker(['stop', name])
                result['owned_container'] = name
                result['runtime_stopped_verified'] = not inspect(name)['State']['Running']
        result['recorded_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': result['status'], 'report': str(out / 'result.json'),
                      'full_staging_ready': False, 'runtime': 'removed' if args.self_test else 'stopped'}, ensure_ascii=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
