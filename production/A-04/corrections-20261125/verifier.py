"""Verify A04 correction evidence; --seal publishes PRET only after real gates."""
import argparse
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'production/A-04/corrections-20261125'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf8'))


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf8')


def rel(path):
    return path.relative_to(ROOT).as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--style', required=True)
    parser.add_argument('--report', required=True)
    parser.add_argument('--seal', action='store_true')
    args = parser.parse_args()
    run = load(OUT / 'final-run.json')
    packet = pathlib.Path(run['packet'])
    assert packet.is_relative_to(ROOT / 'production/A-04/preuves')
    runner = load(packet / 'runner.json')
    result = load(packet / 'result.json')
    assert run['exit_code'] == runner['exit_code'] == result['exit_code'] == 0
    assert all(check['ok'] for check in runner['checks'] + result['checks'])
    assert len(runner['checks']) == 8
    for filename in ['sources.json', 'dependencies.json']:
        for path, expected in load(packet / filename).items():
            assert sha(ROOT / path.replace('\\', '/')) == expected, path
    log = (packet / 'unit.log').read_text(encoding='utf8')
    count = re.search(r'Ran (\d+) tests in ', log)
    assert count and re.search(r'\nOK\s*$', log) and 'skipped=' not in log
    unit_count = int(count[1])
    assert unit_count >= 48
    for name in ['test_dotdot_resolving_inside_site_refused',
                 'test_parent_symlink_resolving_inside_site_refused',
                 'test_parent_symlink_to_external_backup_also_refused',
                 'test_different_folder_and_main_file_metadata_and_installed_version',
                 'test_bootstrap_only_without_audit_refused',
                 'test_audit_file_readback_detects_changed_or_missing_evidence']:
        assert re.search(r'^' + name + r' .* \.\.\. ok$', log, re.M), name
    checks = {item['check']: item for item in result['checks']}
    for storage in ['classic', 'hpos']:
        for suffix in ['audit_bytes_checked_before_bootstrap',
                       'expired_resume_accepted_with_exact_mu',
                       'expired_resume_missing_mu_refused',
                       'expired_resume_changed_mu_refused',
                       'expired_resume_invalid_checkpoint_refused',
                       'expired_resume_refreshes_under_locks',
                       'expired_resume_preserves_verified_core',
                       'resume_bootstrap_canary_exercised',
                       'concurrent_refused', 'same_site_other_state_refused',
                       'orphan_child_keeps_site_lock', 'idempotent_repeat',
                       'remaining_file_only_plugin_updated_last',
                       'native_callbacks_not_double_executed']:
            assert checks[storage + ':' + suffix]['ok'], (storage, suffix)
        comparison = load(packet / (storage + '-comparison-receipt.json'))
        assert comparison['native_a03_exit'] == 3 and comparison['native_a03_anormal'] == 0
        assert comparison['changes'] and all(c['class'] == 'attendu' for c in comparison['changes'])
        roundtrip = load(packet / (storage + '-production-roundtrip-comparison.json'))
        assert roundtrip['native_a03_exit'] == 0 and roundtrip['changes'] == []
        for stage in ['before', 'after', 'production-roundtrip']:
            php_log = load(packet / (storage + '-' + stage) / 'non-regression.json')['php_log']
            assert php_log['checked'] is True and php_log['errors'] == 0
        plan_path = packet / (storage + '-plan.json')
        plan = load(plan_path)
        state = load(packet / (storage + '-etat.json'))
        assert state['plan_sha256'] == sha(plan_path)
        last = plan['steps'][-1]
        assert last['component'] == 'a04-rest' and last['main_file'] == 'fiction-entry.php'
        assert last['audit']['component'] == last['component']
        assert last['audit']['sha256'] == sha(packet / (storage + '-rest-audit.md'))
        assert all(row['phase'] == 'verified' for row in state['steps'].values())
    style = load(ROOT / args.style / 'receipt.json')
    assert style['exit_code'] == 0 and style['cleanup'] is True
    assert style['totals']['errors'] == 0
    for path, expected in style['sources'].items():
        assert sha(ROOT / path.replace('\\', '/')) == expected
    baseline = load(OUT / 'baseline.json')['sha256']
    for path in ['wp/outils/bascule/a04/bootstrap.php', 'wp/outils/bascule/a04/maintenance.php', 'wp/outils/bascule/a04/runtime.php']:
        assert sha(ROOT / path) == baseline[path]
    assert "default => '(?!)'" in (ROOT / 'wp/outils/bascule/a04/runtime.php').read_text()
    historical = load(OUT / 'avant/production/A-04/manifest-final.json')
    historical_checked = 0
    for path, expected in historical.items():
        if any(path.startswith('production/A-04/' + part + '/') for part in ['preuves', 'style', 'global-final', 'global-actualisation', 'historique-avant-complements-a03']):
            assert sha(ROOT / path) == expected, 'Historical drift: ' + path
            historical_checked += 1
    image = load(OUT / 'image-final/preparation.json')
    assert image['exit_code'] == 0
    image_log = (OUT / 'image-final/preparation.log').read_text(encoding='utf8')
    image_id = re.search(r'PREPARATION T01 : image verifiee (sha256:[a-f0-9]{64})', image_log)[1]
    probe = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'image', 'inspect', image_id], capture_output=True, text=True)
    assert probe.returncode == 0
    inspected = json.loads(probe.stdout)[0]
    assert inspected['Config']['Labels']['org.imagine.t01-image'] == '1'
    assert not inspected['Config'].get('Volumes') and not inspected['Config'].get('ExposedPorts')
    global_dir = OUT / 'global-final'
    global_run = load(global_dir / 'native-result.json')
    assert global_run['exit_code'] == 0 and global_run['source_unchanged'] is True
    assert load(global_dir / 'source-stability.json')['unchanged'] is True
    global_log = (global_dir / 'rejeu.log').read_text(encoding='utf8')
    assert 'T01 IMAGE : ' + image_id in global_log
    totals = json.loads(re.findall(r'^T01_RESULT (.*)$', global_log, re.M)[0])
    assert totals['pass'] is True and totals['tests'] > 0
    assert totals['failures'] == totals['errors'] == totals['skipped'] == 0
    junit = list(global_dir.glob('imagine-*.xml'))
    assert len(junit) == 4
    assert sum(int(ET.parse(p).getroot()[0].attrib['tests']) for p in junit) == totals['tests']
    for label in ['org.imagine.a04-update', 'org.imagine.t01']:
        probe = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'ps', '-aq', '--filter', 'label=' + label], capture_output=True, text=True)
        assert probe.returncode == 0 and not probe.stdout.strip(), 'Owned runner still present: ' + label
    report = ROOT / args.report
    assert report.is_file() and report.is_relative_to(ROOT / 'files/rapports')
    summary = {'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'packet': rel(packet), 'python_tests': unit_count, 'integration_checks': len(result['checks']),
               'runner_checks': len(runner['checks']), 'global': totals, 'image_id': image_id,
               'style': {'errors': style['totals']['errors'], 'warnings': style['totals']['warnings']},
               'historical_files_unchanged': historical_checked, 'report': rel(report),
               'all_passed': True, 'real_access_authorized': False}
    if args.seal:
        production = ROOT / 'production/A-04'
        assert not (production / 'PRET').exists(), 'Do not overwrite an existing readiness pointer'
        write(production / 'finalisation-receipt.json', summary)
        owned = [ROOT / 'wp/outils/bascule/mettre-a-jour', ROOT / 'wp/outils/bascule/mettre-a-jour.md', report]
        owned += [p for folder in ['wp/outils/bascule/a04', 'wp/tests/a04'] for p in (ROOT / folder).iterdir() if p.is_file()]
        excluded = {production / name for name in ['PRET', 'manifest-final.json', 'verification-finale.json']}
        owned += [p for p in production.rglob('*') if p.is_file() and p not in excluded and p.suffix.lower() != '.zip']
        manifest = {rel(p): sha(p) for p in sorted(set(owned))}
        write(production / 'manifest-final.json', manifest)
        assert all(sha(ROOT / path) == expected for path, expected in manifest.items())
        verification = {**summary, 'manifest_path': 'production/A-04/manifest-final.json',
                        'manifest_sha256': sha(production / 'manifest-final.json'), 'verified_files': len(manifest)}
        write(production / 'verification-finale.json', verification)
        ready = {'lot': 'A-04', 'ready_for_review': True, 'real_access_authorized': False,
                 'packet': rel(packet), 'manifest_path': verification['manifest_path'],
                 'manifest_sha256': verification['manifest_sha256'],
                 'verification_path': 'production/A-04/verification-finale.json',
                 'verification_sha256': sha(production / 'verification-finale.json'),
                 'scope': 'Corrections A04 sur fixtures fictives classique/HPOS ; ni clôture ni GO réel.'}
        write(production / 'PRET', ready)
        readback = load(production / 'PRET')
        assert sha(ROOT / readback['manifest_path']) == readback['manifest_sha256']
        assert sha(ROOT / readback['verification_path']) == readback['verification_sha256']
        assert all(sha(ROOT / path) == expected for path, expected in load(ROOT / readback['manifest_path']).items())
        summary['pret_deposited_and_read_back'] = True
        summary['verified_files'] = len(manifest)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
