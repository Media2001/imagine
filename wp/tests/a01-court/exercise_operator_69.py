"""Run the EXACT Ced CLI only on provenance-bound invented .wpress files.

The temporary host archive is made by our owned runner, never operator input.
Both source runners and published/refused named sites are removed and read back.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/staging-court'))
import publish
from core_source import prepare_core
from qualification_69 import public_woo


def host_to_wsl(path):
    value = str(path.resolve())
    return '/mnt/' + value[0].lower() + value[2:].replace('\\', '/') if os.name == 'nt' else value


def run():
    run_id = uuid.uuid4().hex[:12]
    out = ROOT / 'production/A-01/qualification-23nov' / ('operator-' + run_id)
    out.mkdir(parents=True, exist_ok=False)
    result = {'status': 'FAIL', 'synthetic_archive_only': True, 'cases': [], 'cleanup': [],
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        core = prepare_core('6.9.1')
        woo = public_woo('6.9.1')
        for kind in ('clean', 'secret'):
            source = 'imagine-a01-publication-' + uuid.uuid4().hex[:12]
            name = publish.validate_name('imagine-test-a01-' + run_id + '-' + kind)
            made = False
            item = {'kind': kind, 'site': name, 'source_runner': source, 'status': 'FAIL'}
            result['cases'].append(item)
            try:
                item['source_manifest'] = publish.fresh_runner(source)
                made = True
                item['source_isolation'] = publish.offline_isolation(source)
                publish.set_empty_runner_core(source, *core)
                publish.call(['exec', '-i', source, 'python3', '-'], b"import shutil\nshutil.rmtree('/opt/woocommerce/woocommerce')\n")
                publish.call(['exec', '-i', source, 'tar', '-xf', '-', '-C', '/'], woo[0])
                publish.call(['cp', '/home/ced/staging-wp/plugins/woocommerce-memberships.zip', source + ':/opt/e2e/woocommerce-memberships.zip'])
                publish.call(['exec', source, 'python3', '/opt/court/qualification_69.py', 'hpos', kind])
                fixture = publish.read_json(source, '/report/fixture.json')
                item['fixture'] = fixture
                scratch = Path.home() / 'AppData/Local/hermes/cache/scratch' if os.name == 'nt' else Path(os.environ['TMPDIR'])
                with tempfile.TemporaryDirectory(prefix='a01-fiction-only-', dir=scratch) as folder:
                    archive = Path(folder) / 'fiction-generated-here.wpress'
                    publish.call(['cp', source + ':/scratch/fiction.wpress', host_to_wsl(archive)])
                    assert hashlib.sha256(archive.read_bytes()).hexdigest() == fixture['archive_sha256']
                    cmd = [sys.executable, str(ROOT / 'wp/outils/staging-court/publish.py'),
                           '--operator-ced', '--archive', str(archive), '--name', name,
                           '--production-url', 'https://production.synthetic.invalid',
                           '--expected-core-version', '6.9.1', '--php-version', '8.2', '--password-stdin']
                    if kind == 'clean':
                        mismatched = cmd.copy()
                        mismatched[mismatched.index('--expected-core-version') + 1] = '7.0.9'
                        refused = subprocess.run(mismatched, input=(secrets.token_urlsafe(40) + '\n').encode(), capture_output=True, timeout=180,
                                                 env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
                        guard = json.loads(refused.stdout.decode().strip().splitlines()[-1])
                        guard_path = Path(guard['report'])
                        guard_value = json.loads(guard_path.read_bytes())
                        guard_case = guard_value['cases'][0]
                        assert refused.returncode == 1 and guard_value['status'] == 'FAIL'
                        assert guard_case['archive_core_preflight']['code'] == 'SOURCE_EXPECTED_CORE_VERSION_MISMATCH'
                        assert not any(key in guard_case for key in ('normal_creation', 'offline', 'publication', 'verified_marker_readback'))
                        assert 'public_core' not in guard_value
                        assert publish.api('GET', '/api/sites/' + name)['code'] == 404
                        item['expected_version_guard'] = {'subject_report': guard_path.relative_to(ROOT).as_posix(),
                                                          'subject_sha256': hashlib.sha256(guard_path.read_bytes()).hexdigest(),
                                                          'exit': refused.returncode, 'no_site_created': True,
                                                          'no_core_download_or_bootstrap': True}
                    execution = subprocess.run(cmd, input=(secrets.token_urlsafe(40) + '\n').encode(),
                                               capture_output=True, timeout=600,
                                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
                    assert hashlib.sha256(archive.read_bytes()).hexdigest() == fixture['archive_sha256']
                    item['command_flags'] = cmd[2:]
                    item['command_flags'][item['command_flags'].index('--archive') + 1] = '<temporary invented archive; deleted>'
                    item['cli_exit'] = execution.returncode
                    item['stdout_sha256'] = hashlib.sha256(execution.stdout).hexdigest()
                    item['stderr_sha256'] = hashlib.sha256(execution.stderr).hexdigest()
                    summary = json.loads(execution.stdout.decode().strip().splitlines()[-1])
                    report = Path(summary['report'])
                    assert report.resolve().is_relative_to(ROOT / 'production/A-01/publication-23nov')
                    item['subject_report'] = report.relative_to(ROOT).as_posix()
                    item['subject_sha256'] = hashlib.sha256(report.read_bytes()).hexdigest()
                    subject = json.loads(report.read_bytes())
                    case = subject['cases'][0]
                    assert case['archive_core_preflight']['source'] == '6.9.1'
                    assert case['offline']['core_versions'] == {'source': '6.9.1', 'pinned': '6.9.1', 'expected': '6.9.1'}
                    assert case['offline']['import_installed_or_updated_plugins'] is False
                    assert case['offline']['restored_files_before_cleanup'] == fixture['source_files']
                    if kind == 'clean':
                        assert execution.returncode == 0 and subject['status'] == 'PASS'
                        probe = case['publication']['probe']
                        assert probe['ok'] and probe['versions']['wordpress'] == '6.9.1'
                        assert probe['fidelity']['orders'] == fixture['orders']
                        assert probe['fidelity']['membership'] == fixture['membership']
                        assert probe['fidelity']['membership_shortcodes'] == fixture['rights']['shortcodes']
                        assert probe['fidelity']['plugins'] == fixture['plugins']
                        assert case['verified_marker_readback']['status'] == 'verified'
                        assert probe['assigned_url_http']['code'] == 200
                    else:
                        assert execution.returncode == 1 and subject['status'] == 'FAIL'
                        assert case['publication']['status'] == 'REFUSED_OFFLINE'
                        assert not case['injection'] and 'verified_marker_readback' not in case
                        assert 'SECRET_OU_IDENTIFIANT' in case['offline']['steps'][-1]['report']['issues']
                        assert case['failure_stop_readback']['all_three_containers_stopped']
                    item['status'] = 'PASS'
                item['temporary_archive_directory_absent'] = not Path(folder).exists()
                assert item['temporary_archive_directory_absent']
            except Exception as error:
                item['error_class'] = type(error).__name__
                item['frames'] = [{'file': Path(f.filename).name, 'line': f.lineno, 'function': f.name}
                                  for f in __import__('traceback').extract_tb(error.__traceback__)]
            finally:
                # Stop a retained operator site before ANY runner cleanup, even on failure.
                if publish.api('GET', '/api/sites/' + name)['code'] != 404:
                    item['final_stop'] = publish.stop_site(name)
                    publish.api('DELETE', '/api/sites/' + name)
                    result['cleanup'].append(publish.deleted_readback(name))
                if made:
                    result['cleanup'].append(publish.remove_owned(source))
                (out / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        result['status'] = 'PASS' if len(result['cases']) == 2 and all(c['status'] == 'PASS' for c in result['cases']) else 'FAIL'
    finally:
        result['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result['sources'] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [Path(__file__), ROOT / 'wp/tests/a01-court/qualification_69.py']}
        (out / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'status': result['status'], 'report': str(out / 'result.json')}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(run())
