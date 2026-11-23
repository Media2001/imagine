"""Read-only independent A-01 6.9.1 delivery verification. No lifecycle or archive I/O."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
if not __debug__:
    raise SystemExit('PYTHON_OPTIMIZATION_REFUSED')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_publication
sys.path.insert(0, str(ROOT / 'wp/outils/staging-court'))
import publish


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_relative(relative):
    path = (ROOT / relative).resolve()
    assert path.is_relative_to(ROOT / 'production/A-01') and path.suffix == '.json'
    return path, json.loads(path.read_bytes())


def sources_match(mapping):
    for rel, expected in mapping.items():
        path = (ROOT / rel).resolve()
        assert path.is_relative_to(ROOT / 'wp')
        assert sha(path) == expected, 'SOURCE_DRIFT:' + rel


def verify_operator(report, live):
    value = json.loads(report.read_bytes())
    assert value['status'] == 'PASS' and value['synthetic_archive_only'] is True
    assert [c['kind'] for c in value['cases']] == ['clean', 'secret']
    sources_match(value['sources'])
    summaries = []
    for item in value['cases']:
        assert item['status'] == 'PASS' and item['temporary_archive_directory_absent'] is True
        assert item['decisions_are_synthetic_not_Ced_approval'] is True
        sources_match(item['source_manifest'])
        path, subject = read_relative(item['subject_report'])
        assert sha(path) == item['subject_sha256']
        sources_match(subject['command_sources'])
        assert subject['tool_sources_unchanged'] is True and not subject.get('cleanup_errors')
        case = subject['cases'][0]
        fixture = item['fixture']
        assert case['offline']['restored_files_before_cleanup'] == fixture['source_files']
        assert case['offline']['import_installed_or_updated_plugins'] is False
        assert case['offline']['core_versions'] == {'source': '6.9.1', 'pinned': '6.9.1', 'expected': '6.9.1'}
        if item['kind'] == 'clean':
            assert item['cli_exit'] == 0 and subject['status'] == 'PASS'
            probe = case['publication']['probe']
            assert probe['ok'] and probe['versions']['wordpress'] == '6.9.1'
            assert probe['fidelity']['orders'] == fixture['orders'] and len(fixture['orders']) == 30
            assert probe['fidelity']['membership'] == fixture['membership']
            assert probe['fidelity']['plugins'] == fixture['plugins']
            assert probe['fidelity']['membership_shortcodes'] == fixture['rights']['shortcodes']
            assert case['verified_marker_readback']['status'] == 'verified'
            assert probe['assigned_url_http']['code'] == 200
            guard = item['expected_version_guard']
            guard_path, refused = read_relative(guard['subject_report'])
            assert sha(guard_path) == guard['subject_sha256'] and guard['exit'] == 1
            assert refused['status'] == 'FAIL' and 'public_core' not in refused
            guarded = refused['cases'][0]
            assert guarded['archive_core_preflight']['code'] == 'SOURCE_EXPECTED_CORE_VERSION_MISMATCH'
            assert not any(k in guarded for k in ('normal_creation', 'offline', 'publication', 'runtime_core_preflight', 'new_php_lint'))
        else:
            assert item['cli_exit'] == 1 and subject['status'] == 'FAIL'
            assert case['publication']['status'] == 'REFUSED_OFFLINE' and not case['injection']
            assert 'verified_marker_readback' not in case
            assert 'SECRET_OU_IDENTIFIANT' in case['offline']['steps'][-1]['report']['issues']
            assert case['failure_stop_readback']['all_three_containers_stopped'] is True
        assert item['final_stop']['all_three_containers_stopped'] is True
        if live:
            publish.deleted_readback(item['site'])
            absent = publish.call(['inspect', item['source_runner']], check=False)
            assert absent.returncode and b'no such object' in absent.stderr.lower()
        summaries.append({'kind': item['kind'], 'site': item['site'], 'subject_exit': item['cli_exit'], 'status': 'PASS'})
    assert len([c for c in value['cleanup'] if 'site' in c]) == 2
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publication', required=True)
    parser.add_argument('--operator', required=True)
    parser.add_argument('--offline', required=True)
    parser.add_argument('--live-cleanup', action='store_true')
    parser.add_argument('--output')
    args = parser.parse_args()
    publication = Path(args.publication).resolve()
    operator = Path(args.operator).resolve()
    offline = Path(args.offline).resolve()
    for path in (publication, operator, offline):
        assert path.is_relative_to(ROOT / 'production/A-01')
    proof = verify_publication.verify(publication, args.live_cleanup)
    operator_cases = verify_operator(operator, args.live_cleanup)
    data = json.loads(offline.read_bytes())
    assert data['status'] == 'PASS' and data['passed'] == 18 and data['failed'] == 0
    assert len(data['checks']) == 18 and all(c['pass'] is True for c in data['checks'])
    assert data['full_staging_ready'] is False and data['no_real_archive'] is True
    assert data['owned_container_removed'] is data['no_ports_no_mounts_network_none'] is True
    assert all(unit['exit'] == 0 for unit in data['unit_results'].values())
    sources_match(json.loads((offline.parent / 'sources.json').read_bytes()))
    previous = json.loads((ROOT / 'production/A-01/tests-21nov/899049f5bdbf/sources.json').read_bytes())
    native = {rel: digest for rel, digest in previous.items() if rel.startswith('wp/outils/staging/')}
    assert len(native) == 11
    sources_match(native)
    assert data['runner_sha256'] == sha(ROOT / 'wp/outils/staging-court/run.py')
    if args.live_cleanup:
        name = 'imagine-a01-court-' + offline.parent.name
        absent = publish.call(['inspect', name], check=False)
        assert absent.returncode and b'no such object' in absent.stderr.lower()
        recovery = ROOT / 'production/A-01/publication-23nov/040686b78372/interrupted-cleanup.json'
        recovered = json.loads(recovery.read_bytes())
        publish.deleted_readback(recovered['deleted']['site'])
        absent = publish.call(['inspect', recovered['runner']['name']], check=False)
        assert absent.returncode and b'no such object' in absent.stderr.lower()
        recovery = ROOT / 'production/A-01/qualification-23nov/operator-303efe89cded/aborted-recovery.json'
        recovered = json.loads(recovery.read_bytes())
        assert recovered['status'] == 'RECOVERED_NOT_QUALIFIED'
        assert recovered['temporary_synthetic_archive_directory_absent'] is True
        for site in recovered['sites_absent']:
            publish.deleted_readback(site['site'])
        for runner in recovered['runners_removed']:
            absent = publish.call(['inspect', runner['name']], check=False)
            assert absent.returncode and b'no such object' in absent.stderr.lower()
        for label in (publish.LABEL, publish.offline_runner.LABEL):
            residue = publish.call(['ps', '-aq', '--filter', 'label=' + label + '=true']).stdout.strip()
            assert not residue, 'OWNED_RUNNER_LABEL_RESIDUE'
    units = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'wp/tests/a01-court', '-p', 'test_*.py', '-v'],
                           cwd=ROOT, capture_output=True, timeout=90,
                           env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
                                'TMPDIR': str(Path.home() / 'AppData/Local/hermes/cache/scratch') if os.name == 'nt' else os.environ.get('TMPDIR', '/opt/court/test-scratch'),
                                'PYTHONPATH': str(ROOT / 'wp/outils/staging-court'),
                                'A01_691_REPORT': publication.relative_to(ROOT).as_posix()})
    transcript = units.stdout + units.stderr
    assert units.returncode == 0, transcript.decode('utf-8', 'replace')[-3000:]
    count = re.search(rb'Ran ([0-9]+) tests? in ', transcript)
    assert count and b'\nOK' in transcript and b'skipped=' not in transcript
    paths = sorted((ROOT / 'wp/outils/staging-court').glob('*')) + sorted((ROOT / 'wp/tests/a01-court').glob('*.py'))
    paths += [ROOT / 'production/A-01/notes.md', ROOT / 'production/A-01/PRET']
    delivery = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths
                if p.is_file() and (p.suffix in ('.py', '.php', '.md') or p.name == 'PRET')}
    result = {'status': 'PASS', 'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'publication': {'path': publication.relative_to(ROOT).as_posix(), 'sha256': sha(publication), 'cases': proof['cases_verified']},
              'operator': {'path': operator.relative_to(ROOT).as_posix(), 'sha256': sha(operator), 'cases': operator_cases},
              'offline': {'path': offline.relative_to(ROOT).as_posix(), 'sha256': sha(offline), 'checks': 18},
              'unit_tests': int(count[1]), 'unit_exit': units.returncode, 'unit_transcript_sha256': hashlib.sha256(transcript).hexdigest(),
              'live_cleanup_checked': args.live_cleanup, 'payloads_match_current': True,
              'owned_runner_labels_empty': args.live_cleanup,
              'delivery_sources': delivery, 'no_real_archive_or_agent_io': True,
              'subscriptions_691': 'NOT_TESTED; prior 7.0.9 qualification retained; first Ced real-import report reviewed before opening',
              'memberships_691': '1.30.3 actually activated and rights/shortcodes preserved'}
    if args.output:
        output = Path(args.output).resolve()
        assert output.is_relative_to(ROOT / 'production/A-01') and not output.exists()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        output.with_suffix('.units.log').write_bytes(transcript)
    print(json.dumps({k: v for k, v in result.items() if k != 'delivery_sources'}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
