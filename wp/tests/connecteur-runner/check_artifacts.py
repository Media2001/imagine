"""Verify final C-04 receipts against delivered bytes, without Docker or network."""
import csv
import datetime
import hashlib
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'production/C-04/tests'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    final = json.loads((OUT / 'final.json').read_text(encoding='utf-8'))
    plugin = ROOT / 'wp/plugins/imagine-connecteur'
    current = {p.relative_to(plugin).as_posix(): digest(p) for p in plugin.rglob('*') if p.is_file()}
    assert current == final['source_sha256'], 'Delivered plugin differs from the executed snapshot'
    for field in ['exit_code', 'psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code']:
        assert final[field] == 0, field
    assert final['container_source_verified'] and final['network_disconnected']
    assert final['no_mounts'] and final['no_ports'] and final['processes_before_suite'] == ['sleep']
    before = json.loads((OUT / 'c01-before.json').read_text(encoding='utf-8'))
    actual = {str(p.relative_to(ROOT)): digest(p)
              for folder in ['wp/plugins/imagine-pilotage', 'wp/tests/numeros-runner']
              for p in (ROOT / folder).rglob('*') if p.is_file()}
    assert before == actual, 'Protected C-01 inventory or bytes changed'
    baseline = json.loads((OUT / 'c01-regression.json').read_text(encoding='utf-8'))
    assert baseline['exit_code'] == baseline['psr12_exit_code'] == 0
    assert baseline['protected_c01_unchanged'] and baseline['container_source_verified']
    assert baseline['driver_sha256'] == digest(ROOT / 'wp/tests/connecteur-runner/verify.py')
    results = {}
    for label, filename in [('C-04', 'final.xml'), ('C-01', 'c01-regression.xml')]:
        xml = ET.parse(OUT / filename).getroot()
        suite = xml.find('testsuite')
        cases = xml.findall('.//testcase')
        assert suite is not None and len(cases) == int(suite.attrib['tests'])
        assert all(int(suite.attrib[field]) == 0 for field in ['errors', 'failures', 'skipped'])
        assertions = sum(int(case.attrib['assertions']) for case in cases)
        assert assertions == int(suite.attrib['assertions'])
        results[label] = {'tests': len(cases), 'assertions': assertions, 'failures': 0, 'errors': 0, 'skipped': 0}
    demo = json.loads((OUT / 'demo-result.json').read_text(encoding='utf-8'))
    assert demo['identical_after_rerun'] and demo['state'] == 'sent'
    assert demo['queue_entries'] == 1 and demo['replay_sent'] is False and demo['alerts'] == []
    assert demo['export_sha256'] == digest(OUT / 'demo-2026-11-19.csv')
    with (OUT / 'demo-2026-11-19.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1 and rows[0]['email'] == 'fiction@example.org'
    assert rows[0]['batch_day'] == '2026-11-19'
    assert json.loads((OUT / 'cleanup.json').read_text(encoding='utf-8'))['owned_runner_removed']
    assert not (OUT / 'runner-state.json').exists()
    assert not (ROOT / 'wp/tests/numeros-runner/__pycache__').exists()
    forbidden = re.compile(r'\b(?:eval|shell_exec|exec|system|fsockopen|stream_socket_client)\s*\(')
    remote = re.compile(r'\b(?:curl_init|wp_remote_get|wp_remote_post)\s*\(')
    issues = []
    for path in plugin.rglob('*.php'):
        text = path.read_text(encoding='utf-8')
        if forbidden.search(text) or remote.search(text):
            issues.append(str(path.relative_to(ROOT)))
        assert 'declare(strict_types=1);' in text
    assert issues == [], issues
    files = [p for folder in ['wp/plugins/imagine-connecteur', 'wp/tests/connecteur-runner']
             for p in (ROOT / folder).rglob('*') if p.is_file()]
    files += [p for p in (ROOT / 'production/C-04').glob('*') if p.is_file()]
    receipt = {
        'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'passed': True, 'results': results,
        'total_tests': sum(result['tests'] for result in results.values()),
        'total_assertions': sum(result['assertions'] for result in results.values()),
        'executed_plugin_equals_delivered_plugin': True, 'protected_c01_unchanged': True,
        'owned_runner_removed': True, 'static_dangerous_primitive_matches': issues,
        'demo_export_sha256': demo['export_sha256'],
        'artifacts_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(files)},
    }
    (OUT / 'artifact-verification.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'artifacts_sha256'}, indent=2))


if __name__ == '__main__':
    main()
