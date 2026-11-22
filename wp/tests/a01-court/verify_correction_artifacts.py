"""Read-only source/receipt/cleanup validation for the scoped A-01 correction handoff."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
if not __debug__:
    raise SystemExit('PYTHON_OPTIMIZATION_REFUSED')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/staging-court'))
import publish

PUBLICATION = ROOT / 'production/A-01/publication-22nov/6d5fac463e61/result.json'
FAULTS = ROOT / 'production/A-01/corrections-22nov/faults-a4d2ca414cea/result.json'
BASELINE = ROOT / 'production/A-01/tests-21nov/3c4e0cfbc8c4/result.json'
MODIFIED = [
    'wp/outils/staging-court/publish.py', 'wp/outils/staging-court/inside.py',
    'wp/outils/staging-court/README.md', 'wp/outils/staging-wp-integration/worker/worker.py',
    'wp/tests/a01-court/prepare_publication.py', 'wp/tests/a01-court/roundtrip.py',
    'wp/tests/a01-court/verify_publication.py', 'wp/tests/a01-court/test_corrections.py',
    'wp/tests/a01-court/exercise_corrections.py', 'wp/tests/a01-court/verify_correction_artifacts.py',
    'production/A-01/notes.md', 'production/A-01/NON-PRET-22nov.md',
    'production/A-01/PRET-invalide-22nov-historique.txt',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sources(manifest):
    for relative, expected in manifest.items():
        source = (ROOT / relative).resolve()
        assert source.is_relative_to(ROOT / 'wp') and digest(source) == expected, relative


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    assert output.is_relative_to(ROOT / 'production/A-01') and not output.exists()
    publication, faults, baseline = load(PUBLICATION), load(FAULTS), load(BASELINE)
    assert publication['status'] == faults['status'] == baseline['status'] == 'PASS'
    assert len(publication['cases']) == len(faults['cases']) == 4
    assert baseline['passed'] == 18 and baseline['failed'] == 0
    assert baseline['owned_container_removed'] and baseline['source_manifest_verified']
    sources(publication['command_sources'])
    sources(load(BASELINE.with_name('sources.json')))
    assert faults['driver_sha256'] == digest(ROOT / 'wp/tests/a01-court/exercise_corrections.py')
    sites, runners = set(), set()
    for case in publication['cases']:
        sources(case['source_manifest'])
        assert case['status'] == 'PASS'
        sites.add(case['name']); runners.add(case['offline_isolation_before']['name'])
    for fault in faults['cases']:
        assert fault['status'] == 'PASS' and fault['command_exit'] == 1
        report = Path(fault['report'])
        assert digest(report) == fault['report_sha256']
        subject = load(report)
        assert subject['status'] == 'FAIL' and len(subject['cases']) == 1
        sources(subject['command_sources']); sources(subject['cases'][0]['source_manifest'])
        sites.add(fault['site']); runners.add(fault['runner'])
    assert len(sites) == len(runners) == 8
    cleanup = [publish.deleted_readback(site) for site in sorted(sites)]
    runners.add('imagine-a01-court-' + BASELINE.parent.name)
    for runner in sorted(runners):
        result = publish.call(['inspect', runner], check=False)
        assert result.returncode and b'no such object' in result.stderr.lower(), runner
    assert not (ROOT / 'production/A-01/PRET').exists()
    assert 'NON PRÊT' in (ROOT / 'production/A-01/notes.md').read_text(encoding='utf-8')
    assert "define('DISALLOW_FILE_MODS',true)" in (ROOT / 'wp/outils/staging-court/publish.py').read_text()
    tests = []
    folder = ROOT / 'production/A-01/corrections-22nov'
    for log in sorted(folder.glob('unit-*-final.log')):
        text = log.read_text()
        count = re.search(r'Ran ([0-9]+) tests?', text)
        if not count and log.name == 'unit-harness-final.log':
            count = re.search(r'"tests_run": ([0-9]+)', text)
        assert count and ('\nOK' in text or '"successful": true' in text), log.name
        tests.append({'log': log.relative_to(ROOT).as_posix(), 'tests': int(count[1]), 'sha256': digest(log)})
    assert len(tests) == 5
    evidence = [PUBLICATION, FAULTS, BASELINE, folder / 'verification-live-final.json', folder / 'package-format-source.json']
    final_verification = load(folder / 'verification-live-final.json')
    assert final_verification['status'] == 'PASS' and final_verification['cases_verified'] == 4
    result = {
        'status': 'SCOPED_CORRECTIONS_VERIFIED_GLOBAL_HANDOFF_BLOCKED',
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'ready_for_review_global': False, 'pret_present': False,
        'corrected': ['R4', 'R3', 'R1', 'R2', 'R6', 'R7'],
        'blockers': ['R5_CED_ADMIN_OR_SCRIPTS_REQUIRED', 'PRODUCTION_CORE_6_9_1_NOT_QUALIFIED_BY_COMMERCIAL_7_0_9_BASELINE'],
        'modified_file_sha256': {relative: digest(ROOT / relative) for relative in MODIFIED},
        'evidence_sha256': {path.relative_to(ROOT).as_posix(): digest(path) for path in evidence},
        'unit_suites': tests, 'unit_tests_passed': sum(test['tests'] for test in tests),
        'publication_cases_passed': len(publication['cases']), 'real_fault_scenarios_passed': len(faults['cases']),
        'expected_subject_failures': [case['command_exit'] for case in faults['cases']],
        'offline_checks_passed': baseline['passed'], 'offline_data_cases': baseline['unit_results']['data']['receipt']['cases'],
        'offline_data_assertions': baseline['unit_results']['data']['receipt']['assertions'],
        'source_receipts_match_current_files': True,
        'new_sites_absent_count': len(cleanup), 'site_cleanup': cleanup,
        'owned_runner_absence_names': sorted(runners),
        'correction_source_sha256': digest(ROOT / 'corrections/A-01.md'),
        'no_real_archive_no_agent_access_no_shared_tool_changes': True,
        'not_a_production_import_authorization': True,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'unit_tests_passed': result['unit_tests_passed'],
                      'new_sites_absent': len(cleanup), 'owned_runners_absent': len(runners), 'report': str(output)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
