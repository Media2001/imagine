"""Read-only A25 evidence verifier; PRET and global gates remain parent-owned."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OWN = ['wp/outils/bascule/a25', 'wp/tests/a25']
PACKAGE = OWN + ['production/A-25']
RESERVED = {'production/A-25/PRET', 'production/A-25/manifest.json', 'production/A-25/candidate-verification.json'}
CHANNELS = ['direct_stdout', 'direct_stderr', 'display_early_exit', 'silent_early_exit', 'shutdown_stdout',
            'shutdown_stderr', 'shutdown_display', 'invalid_utf8', 'oversize_output', 'plugin_exception',
            'forged_success', 'shutdown_invalid_json', 'shutdown_extra_string', 'shutdown_markdown',
            'shutdown_extra_file', 'shutdown_partial']


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def inventory(roots):
    files = []
    for key in roots:
        p = ROOT / key
        files.extend([p] if p.is_file() else [f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts])
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files)) if p.relative_to(ROOT).as_posix() not in RESERVED}


def receipt_valid(d):
    if (type(d) is not dict or 'tests' in d or d.get('exit_code') != 0
            or type(d.get('checks')) is not list or not d['checks']):
        return False
    rows = d['checks']
    return (all(type(c) is dict and type(c.get('check')) is str and c['check'] and c.get('status') == 'PASS' for c in rows)
            and len({c['check'] for c in rows}) == len(rows))


def shared_contract(shared, expected):
    lines = expected.splitlines(keepends=True)
    return len(lines) == 2 and all(line.endswith(b'\n') and shared.splitlines(keepends=True).count(line) == 1 for line in lines)


def form_observation_valid(data, variant):
    """Require actual new observations; historic PASS labels alone are insufficient."""
    pk = {'year': 2022, 'state': 'autre', 'count': 5}
    profiles = {
        'visitors': (['Fluent Forms'], 2, [pk], 4),
        'neutralised': (['Fluent Forms'], 2, [], None),
        'five': (['Fluent Forms'], 2, [{'year': 1999, 'state': 'Fluent Forms', 'count': 5}, pk], 4),
        'absent': ([], 2, [pk], 2),
        'nodate': ([], 3, [{'year': 0, 'state': 'autre', 'count': 5}, pk], 2),
        'pk-only': ([], 1, [pk], 0),
        'ambiguous': ([], 1, [], None),
    }
    listed, other, groups, pooled = profiles[variant]
    coverage = 'couverture indéterminée' if variant == 'ambiguous' else 'heuristique bornée'
    counts = ('inconnu après neutralisation' if variant == 'neutralised' else coverage) if pooled is None else {
        'groups': groups, 'autres': pooled}
    return data['forms'] == {'listed_extensions': listed, 'other_tables': other, 'coverage': coverage,
        'clear_messages_after_import': True,
        'clear_messages_after_import_label': 'avertissement éditorial permanent, non mesuré sur la copie inspectée'} and data['counts']['forms'] == counts


def verify(packet, sealed=True, require_shared=False):
    checks, counts = [], {}

    def check(key, ok):
        checks.append({'check': key, 'status': 'PASS' if ok else 'FAIL'})

    source = read(packet / 'sources.json')
    check('current_owned_sources', source == inventory(OWN))
    runner = load_module('a25_runner', ROOT / 'wp/tests/a25/run.py')
    report = load_module('a25_report', ROOT / 'wp/outils/bascule/a25/report.py')
    required = ['commercial_fixture', 'native_seed', 'audit_success', 'confined_success', 'exact_native_counts',
                'closed_form_adapter_and_other', 'all_private_values_absent', 'private_report_permissions',
                'replay_identical', 'documented_only_given_arguments', 'unconfined_php_refused',
                'transaction_readonly_even_root', 'audit_guard:schema', 'audit_guard:storage',
                'all_tables_and_scheduler_identical', 'site_files_identical', 'config_never_executed',
                'actual_import_comments_changed_forms_clear', 'neutralised_audit', 'neutralised_success',
                'neutral_unknown_never_zero', 'unchanged_native_counts_after_import',
                'neutralised_all_tables_files_identical', 'five_native_seed', 'five_audit', 'five_confined_success',
                'five_native_year_state_utc', 'five_native_form_year', 'five_native_guests_year',
                'five_tables_files_identical', 'absent_audit', 'absent_confined_success',
                'absent_known_extension_explicit', 'absent_tables_files_identical',
                'nodate_audit', 'nodate_confined_success', 'nodate_closed_zero_not_invented_year',
                'nodate_tables_files_identical', 'all_output_artifacts_clean',
                'submission_pk_five_child_excluded', 'pk_only_audit', 'pk_only_confined_success',
                'pk_only_no_silent_zero_or_child_double_count', 'pk_only_tables_files_identical',
                'ambiguous_audit', 'ambiguous_confined_success', 'ambiguous_coverage_never_zero',
                'ambiguous_tables_files_identical']
    required += ['guard:' + key for key in ('exists', 'site', 'repo', 'ancestor', 'root')]
    required += ['symlink_closed:' + key for key in ('False', 'True')]
    required += ['closed_dropin:' + str(i) for i in range(6)]
    required += ['config_closed:' + key for key in ('define', 'const')]
    required += [kind + ':' + key for key in CHANNELS for kind in ('closed_channel', 'no_retained_payload')]
    required += ['mutation_without_guard_detected:' + key for key in (
        'direct_stdout', 'direct_stderr', 'display_early_exit', 'shutdown_stdout',
        'shutdown_stderr', 'shutdown_display', 'oversize_output')]
    for console in ('utf8', 'cp1252'):
        base, folder = packet / console, packet / console / 'native'
        environment = read(base / 'environment.json')
        check(console + ':real_windows_encoding', environment['platform'] == 'win32'
              and environment['stdout'] == ('utf-8' if console == 'utf8' else 'cp1252')
              and environment['stderr'] == environment['stdout'] and environment['utf8_mode'] == int(console == 'utf8'))
        text = (base / 'python-tests.log').read_text(encoding='utf-8')
        match = re.search(r'Ran (\d+) tests in ', text)
        counts[console + ':python'] = int(match[1]) if match else 0
        check(console + ':python_pass', counts[console + ':python'] >= 17 and '\nOK\n' in text)
        for kind in ('unit', 'standard', 'result', 'runner'):
            d = read(folder / (kind + '.json'))
            counts[console + ':' + kind] = len(d.get('checks', []))
            check(console + ':' + kind + '_pass', receipt_valid(d))
        pure_names = {c['check'] for c in read(folder / 'unit.json')['checks']}
        check(console + ':corrected_pure_cases', {'submission_pk_is_entry',
              'own_id_submission_reference_is_child', 'unindexed_submission_reference_is_child',
              'composite_submission_pk_is_ambiguous', 'unkeyed_submission_is_ambiguous',
              'unique_submission_not_assumed_primary', 'unkeyed_entry_is_ambiguous',
              'own_id_is_entry', 'meta_child_excluded', 'not_form_structure_ignored'}.issubset(pure_names))
        native = {c['check']: c for c in read(folder / 'result.json')['checks']}
        check(console + ':executed_sources_equal', read(folder / 'sources.json') == source)
        check(console + ':dependencies_equal', read(folder / 'dependencies.json') == runner.manifest(runner.DEPS))
        check(console + ':pure_no_extensions_writes', (folder / 'pure.log').read_text(encoding='utf-8')
              == 'A25_PURE_OK ' + str(counts[console + ':unit']) + '\n')
        for storage in ('classic', 'hpos'):
            prefix = console + ':' + storage
            check(prefix + ':mandatory_cases', all(storage + ':' + key in native for key in required))
            before = read(folder / (storage + '-db-before.json'))
            check(prefix + ':all_tables_identical', before == read(folder / (storage + '-db-after.json'))
                  and {'wp_comments', 'wp_fluentform_submissions', 'wp_a25_unknown_entries',
                       'wp_a25_submission_entries', 'wp_a25_submission_details',
                       'wp_options', 'wp_actionscheduler_actions', 'wp_actionscheduler_logs'}.issubset(before['tables']))
            files = read(folder / (storage + '-files.json'))
            check(prefix + ':files_identical', files['before'] == files['after'])
            for variant in ('neutralised', 'five', 'absent', 'nodate', 'pk-only', 'ambiguous'):
                check(prefix + ':' + variant + '_tables_identical',
                      read(folder / (storage + '-' + variant + '-db-before.json'))
                      == read(folder / (storage + '-' + variant + '-db-after.json')))
            for suffix, audit_suffix in [('visitors', 'audit'), ('neutralised', 'neutralised-audit'),
                                         ('five', 'five-audit'), ('absent', 'absent-audit'), ('nodate', 'nodate-audit'),
                                         ('pk-only', 'pk-only-audit'), ('ambiguous', 'ambiguous-audit')]:
                check(prefix + ':' + suffix + '_projection', report.complete_report(
                    folder / (storage + '-' + suffix), folder / (storage + '-' + audit_suffix + '/audit.json')))
                check(prefix + ':' + suffix + '_exact_form_observation', form_observation_valid(
                    read(folder / (storage + '-' + suffix) / 'visiteurs.json'), suffix))
            nominal = folder / (storage + '-visitors/visiteurs.json')
            d = read(nominal)
            check(prefix + ':storage_and_exact_counts', d['storage'] == storage and d['counts'] == {
                'comments': {key: {'groups': [], 'autres': n} for key, n in [('all', 3), ('email', 2), ('ip', 2), ('account', 1)]},
                'forms': {'groups': [{'year': 2022, 'state': 'autre', 'count': 5}], 'autres': 4},
                'guests': {'groups': [], 'autres': 2}})
            for suffix in ('repeat', 'documented', 'root-readonly'):
                check(prefix + ':' + suffix + '_identical', (folder / (storage + '-' + suffix) / 'visiteurs.json').read_bytes()
                      == nominal.read_bytes())
    style = read(packet / 'style/style.json')
    check('strict_psr12', receipt_valid(style) and style['phpcs_exit'] == 0
          and style['totals']['errors'] == style['totals']['warnings'] == 0 and style['sources'] == source)
    matrix = read(packet / 'windows-matrix.json')
    check('five_real_commands_pass', matrix['exit_code'] == 0 and len(matrix['rows']) == 5
          and all(row['exit_code'] == 0 and row.get('all_pass') is not False for row in matrix['rows']))
    check('command_logs_bound', all(hashlib.sha256((packet / row['log']).read_bytes()).hexdigest() == row['log_sha256']
                                    for row in matrix['rows']))
    check('artifacts_clean', not any(b'CANARY' in p.read_bytes() for p in packet.rglob('*') if p.is_file()))
    check('parent_gates_not_claimed', read(packet / 'candidate.json') == {'status': 'CANDIDAT_GATE_PARENT',
          'readiness_claimed': False, 'parent_preparation': 'pending', 'parent_global_T01': 'pending'})
    delta = (ROOT / 'production/A-25/readme-ajout.txt').read_bytes()
    check('two_delta_lines', len(delta.splitlines()) == 2 and delta.endswith(b'\n'))
    if require_shared:
        check('own_shared_contract_only', shared_contract((ROOT / 'wp/tests/a02-audit/README.md').read_bytes(), delta))
    if sealed:
        check('current_exact_package', read(ROOT / 'production/A-25/manifest.json') == inventory(PACKAGE))
    result = {'status': 'CANDIDAT_GATE_PARENT', 'readiness_claimed': False, 'counts': counts,
              'checks': checks, 'exit_code': int(any(c['status'] != 'PASS' for c in checks))}
    print(json.dumps(result, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path, default=ROOT / 'production/A-25/preuves/final')
    ap.add_argument('--unsealed', action='store_true')
    ap.add_argument('--require-shared-doc', action='store_true')
    a = ap.parse_args()
    try:
        sys.exit(verify(a.evidence.resolve(), not a.unsealed, a.require_shared_doc))
    except Exception:
        print(json.dumps({'exit_code': 1, 'code': 'A25_PACKET_INVALID'}))
        sys.exit(1)
