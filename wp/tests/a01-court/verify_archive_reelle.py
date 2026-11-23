"""Vérification indépendante des preuves archive-reelle, sans site ni archive."""
import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/staging-court'))
import publish


def counts(text):
    run = int(re.search(r'Ran (\d+) tests', text)[1])
    skipped = int(re.search(r'OK \(skipped=(\d+)\)', text)[1])
    assert 'FAILED (' not in text
    return {'run': run, 'skipped_platform_branches': skipped, 'executed_passed': run - skipped,
            'failures': 0, 'errors': 0}


def new_tests(text):
    return {line.split()[0]: ('ok' if line.endswith('... ok') else 'skipped')
            for line in text.splitlines() if '.ArchiveReelle.' in line and line.startswith('test_')}


def verify():
    lp = ROOT / 'production/A-01/archive-reelle/946da1e537e3'
    linux = json.loads((lp / 'result.json').read_bytes())
    ordinary = json.loads((ROOT / 'production/A-01/archive-reelle/refusal-c4473bce2038/result.json').read_bytes())
    offline_path = ROOT / 'production/A-01/tests-21nov/c6a70d1458cb/result.json'
    offline = json.loads(offline_path.read_bytes())
    assert linux['status'] == ordinary['status'] == offline['status'] == 'PASS'
    assert linux['synthetic_only'] and ordinary['synthetic_only'] and not linux['created_sites']
    assert linux['sources_unchanged'] and linux['cleanup']['absent']
    for rel, digest in linux['source_manifest'].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, rel
    for rel, digest in json.loads((offline_path.parent / 'sources.json').read_bytes()).items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, rel
    assert offline['source_manifest_verified'] and offline['owned_container_removed']
    assert len(offline['checks']) == 18 and all(c['pass'] for c in offline['checks'])
    assert all(unit['exit'] == 0 for unit in offline['unit_results'].values())
    assert ordinary['subject_exit'] == 1 and ordinary['no_site_created'] and ordinary['no_core_download']
    assert ordinary['synthetic_archive_removed'] and ordinary['scratch_directory_removed']
    subject_path = ROOT / ordinary['subject_report']
    subject = json.loads(subject_path.read_bytes())
    for rel, digest in subject['command_sources'].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, rel
    assert subject['tool_sources_unchanged'] and not subject.get('cleanup_errors')
    assert ordinary['console_refusals'] == [
        {'code': 'ARCHIVE_PATH_BACKSLASH', 'count': 2, 'first_zone': 'uploads/2026', 'extension': '.jpg'}]
    host_log = (ROOT / 'production/A-01/archive-reelle-unitaires-remise.log').read_text()
    linux_log = (lp / 'tests.log').read_text()
    host_tests, linux_tests = new_tests(host_log), new_tests(linux_log)
    parsed = ast.parse((ROOT / 'wp/tests/a01-court/test_archive_reelle.py').read_text())
    methods = {node.name for node in ast.walk(parsed)
               if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}
    assert len(methods) == 29
    assert all(host_tests.get(name) == 'ok' or linux_tests.get(name) == 'ok' for name in methods)
    required_linux = [
        'test_real_cli_no_writes_and_no_network_even_on_valid_source',
        'test_valid_archive_cli_exits_zero_with_warnings_only', 'test_case_only_needs_actual_target_probe',
        'test_colon_preserved_but_drive_refused', 'test_symlink_case_neighbor_is_refused_before_writes',
        'test_inserted_parent_symlink_cannot_escape_restoration',
        'test_sql_resynchronisation_never_exports_identifiers_inside_values',
        'test_duplicate_metadata_does_not_hide_first_payload_findings',
        'test_ordinary_preflight_keeps_precise_rule_count']
    assert all(linux_tests[name] == 'ok' for name in required_linux)
    assert host_tests['test_real_case_insensitive_host_refuses_case_only'] == 'ok'
    assert host_tests['test_case_probe_uses_destination_directory_itself'] == 'ok'
    # Only inspect exact resources with a recorded owned creation/cleanup.
    owned, receipts = set(), []
    for path in sorted((ROOT / 'production/A-01/archive-reelle').glob('*/result.json')):
        value = json.loads(path.read_bytes())
        if value.get('synthetic_only'):
            cleanup = value.get('cleanup', [])
            if isinstance(cleanup, dict):
                cleanup = [cleanup]
            for item in cleanup:
                assert item.get('absent') is True
                owned.add(item['name'])
            receipts.append({'path': path.relative_to(ROOT).as_posix(), 'status': value['status'],
                             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    owned.update(['imagine-a01-court-c6a70d1458cb', 'imagine-a01-court-c35323231a8f'])
    process = publish.call(['inspect', *sorted(owned)], check=False)
    assert process.returncode != 0 and json.loads(process.stdout) == []
    assert all(('No such object: ' + name).lower() in process.stderr.decode().lower() for name in owned)
    # Immutable old evidence must not qualify changed code.
    sys.path.insert(0, str(ROOT / 'wp/tests/a01-court'))
    import verify_publication
    try:
        verify_publication.verify(ROOT / 'production/A-01/publication-23nov/52170a14f7a7/result.json')
    except AssertionError as error:
        assert str(error).startswith('COMMAND_SOURCE_DRIFT:')
        historical_status = 'STALE_SOURCE_REFUSED'
    else:
        raise AssertionError('OLD_QUALIFICATION_MUST_NOT_QUALIFY_NEW_SOURCE')
    historical = ROOT / 'production/A-01/PRET-qualification-23nov-historique-avant-archive-reelle.txt'
    assert historical.is_file()
    marker = ROOT / 'production/A-01/PRET'
    if marker.exists():
        assert marker.read_text(encoding='utf-8').startswith('A-01 archive-reelle — PRET DE CODE')
    notes = (ROOT / 'production/A-01/notes.md').read_text(encoding='utf-8')
    assert '--diagnose --operator-ced --archive $ARCHIVE_WPRESS' in notes[:800]
    assert '# Historique antérieur intégral' in notes
    paths = [
        'wp/outils/staging-court/archive.py', 'wp/outils/staging-court/diagnosis.py',
        'wp/outils/staging-court/inside.py', 'wp/outils/staging-court/publish.py',
        'wp/tests/a01-court/test_archive.py', 'wp/tests/a01-court/test_archive_reelle.py',
        'wp/tests/a01-court/exercise_archive_reelle.py', 'wp/tests/a01-court/exercise_archive_refusal.py',
        'wp/tests/a01-court/test_qualification_receipts.py', 'wp/tests/a01-court/verify_publication.py',
        'wp/tests/a01-court/verify_archive_reelle.py', 'production/A-01/notes.md']
    if marker.exists():
        paths.append('production/A-01/PRET')
    for rel in paths:
        if rel.endswith('.py'):
            ast.parse((ROOT / rel).read_text())
    return {
        'status': 'PASS',
        'scope': 'A-01 archive-reelle : correction/diagnostic, archives inventées uniquement, aucun GO réel',
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'host': counts(host_log), 'linux': counts(linux_log),
        'new_test_methods': len(methods), 'new_methods_covered_across_both_real_filesystems': len(methods),
        'linux_receipt': (lp / 'result.json').relative_to(ROOT).as_posix(),
        'ordinary_refusal_receipt': 'production/A-01/archive-reelle/refusal-c4473bce2038/result.json',
        'ordinary_subject_exit': 1, 'ordinary_console': ordinary['console_refusals'],
        'offline_receipt': offline_path.relative_to(ROOT).as_posix(),
        'offline_checks': len(offline['checks']), 'offline_passed': sum(c['pass'] for c in offline['checks']),
        'offline_full_staging_ready': False,
        'native_unit_tests': {
            'archive': offline['unit_results']['archive']['receipt']['tests'],
            'harness': offline['unit_results']['harness']['receipt']['tests_run'],
            'data_cases': offline['unit_results']['data']['receipt']['cases'],
            'data_assertions': offline['unit_results']['data']['receipt']['assertions']},
        'all_named_owned_containers_rechecked_absent': sorted(owned), 'owned_containers_count': len(owned),
        'historical_current_source_status': historical_status,
        'historical_pret_preserved': {'path': historical.relative_to(ROOT).as_posix(),
                                     'sha256': hashlib.sha256(historical.read_bytes()).hexdigest()},
        'command_sources': {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in paths},
        'receipts_preserved': receipts, 'no_real_archive': True, 'no_real_import': True,
        'no_site_created': True, 'no_commercial_account_used': True, 'no_downloads': True,
        'no_host_php': True, 'new_full_publication_executed': False,
        'scope_boundaries': 'Aucun fichier partagé/voie2/verrou/file/rapport parent modifié; aucun Git.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.output:
        target = Path(args.output).resolve()
        assert target.is_relative_to((ROOT / 'production/A-01').resolve()) and not target.exists()
    result = verify()
    if args.output:
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('status', 'host', 'linux', 'new_test_methods',
                      'offline_checks', 'offline_passed', 'owned_containers_count',
                      'historical_current_source_status')}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
