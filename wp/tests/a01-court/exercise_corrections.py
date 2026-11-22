"""Real named-test orchestration, deliberate failures on synthetic fixtures only.

No real archive arguments. Infrastructure remains real; only the named fault is
injected. Each invocation of publish.main writes its unmodified FAIL receipt.
"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/staging-court'))
import publish


def mutate_archive(runner, kind, execute):
    # This replaces only the fictional archive just generated in this owned,
    # network-none runner. No archive is read from or exported to the host.
    program = '''import json,re,struct
from pathlib import Path
kind=KIND
version=re.search(r"^\\$wp_version\\s*=\\s*'([^']+)';",Path('/opt/wordpress/wordpress/wp-includes/version.php').read_text(),re.M)[1]
if kind=='core-mismatch': version='6.9.1'
def entry(name,body):
 return struct.pack('255s14s12s4096s',name.encode(),str(len(body)).encode(),b'0',b'')+body
sql=b'CREATE VIEW `wp_forbidden` AS SELECT 1;' if kind=='sql-unsupported' else b'CREATE TABLE `wp_options` (`option_id` bigint) ENGINE=InnoDB;'
blob=entry('database.sql',sql)+entry('package.json',json.dumps({'SyntheticFixtureOnly':True,'WordPress':{'Version':version}}).encode())+bytes(4377)
if kind=='archive-truncated': blob=blob[:-1]
Path('/scratch/fiction.wpress').write_bytes(blob)
'''.replace('KIND', repr(kind))
    execute(['exec', '-i', runner, 'python3', '-'], program.encode())


def run_case(kind, output):
    original_call = publish.call
    original_remove = publish.remove_owned
    observed = {'kind': kind, 'fault_injected': False}
    recovery = []

    def call(args, data=None, **kwargs):
        if kind == 'marker-and-removal' and '/var/www/html/.imagine-staging-verified.json' in args:
            observed['marker_write_attempted'] = True
            raise RuntimeError('MARKER_WRITE_REFUSED')
        if kind != 'marker-and-removal' and args[:2] == ['exec', '-i'] and b'from inside import execute_offline_request' in (data or b''):
            assert not observed['fault_injected']
            mutate_archive(args[2], kind, original_call)
            observed['runner'] = args[2]
            observed['fault_injected'] = True
        return original_call(args, data, **kwargs)

    def remove(name):
        if name.startswith('imagine-a01-publication-'):
            observed['runner'] = name
            if kind == 'marker-and-removal':
                # Read actual state after the safety stop, before cleanup fails.
                slug = observed['site']
                state = publish.api('GET', '/api/sites/' + slug)['body']['status']
                running = {prefix: publish.target_info(slug, prefix)['State']['Running']
                           for prefix in ('wp-', 'db-', 'nginx-')}
                observed['stop_readback_before_removal_failure'] = {'status': state, 'containers_running': running}
                observed['fault_injected'] = True
                recovery.append(name)
                raise RuntimeError('REMOVAL_NOT_PROVEN')
            databases = original_call(['exec', name, 'mariadb', '--socket=/scratch/mariadb.sock', '--user=root',
                                       '--skip-column-names', '-e', "SHOW DATABASES LIKE 'imagine_a01_staging';"]).stdout
            observed['import_database_absent_before_cleanup'] = databases.strip() == b''
        return original_remove(name)

    original_api = publish.api
    def api(method, path, payload=None):
        response = original_api(method, path, payload)
        if method == 'POST' and path == '/api/sites':
            observed['site'] = response['body']['slug']
        return response

    capture = io.StringIO()
    publish.call, publish.remove_owned, publish.api = call, remove, api
    argv = sys.argv
    sys.argv = ['publish.py', '--self-test-publication', '--case', 'classic']
    try:
        with contextlib.redirect_stdout(capture):
            code = publish.main()
    finally:
        sys.argv = argv
        publish.call, publish.remove_owned, publish.api = original_call, original_remove, original_api
        observed['runner_recovery'] = [original_remove(name) for name in recovery]
    response = json.loads(capture.getvalue().splitlines()[-1])
    report = Path(response['report'])
    value = json.loads(report.read_text(encoding='utf-8'))
    case = value['cases'][0]
    observed.update(command_exit=code, report=str(report), report_sha256=hashlib.sha256(report.read_bytes()).hexdigest())
    # Persist the real observation before evaluating assertions; no fake PASS receipt.
    (output / (kind + '.json')).write_text(json.dumps(observed, indent=2), encoding='utf-8')
    assert code == 1 and value['status'] == 'FAIL' and case['status'] == 'FAIL'
    assert observed['fault_injected'] and case['failure_stop_readback']['all_three_containers_stopped']
    assert not case.get('verified_marker_readback')
    if kind == 'marker-and-removal':
        assert case['error'] == 'MARKER_WRITE_REFUSED'
        assert value['cleanup_errors'] == [{'site': case['name'], 'phase': 'runner_removal', 'code': 'REMOVAL_NOT_PROVEN'}]
        state = observed['stop_readback_before_removal_failure']
        assert state['status'] == 'stopped' and not any(state['containers_running'].values())
        assert observed['runner_recovery'][0]['absent']
    else:
        expected = {
            'archive-truncated': {'stage': 'archive_restore', 'code': 'ARCHIVE_TRUNCATED'},
            'sql-unsupported': {'stage': 'sql_preflight', 'code': 'SQL_DDL_UNSUPPORTED'},
            'core-mismatch': {'stage': 'core_preflight', 'code': 'SOURCE_CORE_VERSION_MISMATCH'},
        }[kind]
        assert case['offline_failure'] == expected
        assert observed['import_database_absent_before_cleanup']
        assert 'injection' not in case and 'publication' not in case
        if kind == 'core-mismatch':
            assert case['offline']['core_versions'] == {'source': '6.9.1', 'pinned': '7.0.9'}
        assert not value.get('cleanup_errors')
    observed['live_cleanup'] = publish.deleted_readback(case['name'])
    missing = publish.call(['inspect', observed['runner']], check=False)
    assert missing.returncode and b'no such object' in missing.stderr.lower()
    observed['runner_absent_readback'] = True
    observed['status'] = 'PASS'
    (output / (kind + '.json')).write_text(json.dumps(observed, indent=2), encoding='utf-8')
    return observed


def main():
    output = ROOT / 'production/A-01/corrections-22nov' / ('faults-' + uuid.uuid4().hex[:12])
    output.mkdir(parents=True, exist_ok=False)
    result = {'status': 'FAIL', 'cases': [], 'no_real_archive': True, 'fault_injection_only_on_owned_synthetic_fixtures': True}
    try:
        for kind in ('marker-and-removal', 'archive-truncated', 'sql-unsupported', 'core-mismatch'):
            result['cases'].append(run_case(kind, output))
        result['status'] = 'PASS'
    finally:
        result['driver_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        (output / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'status': result['status'], 'cases': len(result['cases']), 'report': str(output / 'result.json')}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
