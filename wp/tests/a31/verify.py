"""Read-only A31 packet verifier; Python-only is explicitly not a native seal."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
CHANNELS = ('direct_stdout', 'direct_stderr', 'display_exit', 'silent_exit', 'shutdown_stdout', 'shutdown_stderr',
            'shutdown_display', 'invalid_utf8', 'oversize', 'exception', 'forged_success', 'shutdown_invalid_json',
            'shutdown_json_canary', 'shutdown_markdown', 'shutdown_extra_file', 'shutdown_partial',
            'shutdown_valid_counts_and_markdown')
WITNESSES = ('direct_stdout', 'direct_stderr', 'display_exit', 'shutdown_stdout', 'shutdown_stderr',
             'shutdown_display', 'oversize', 'shutdown_json_canary', 'shutdown_markdown', 'shutdown_extra_file',
             'shutdown_valid_counts_and_markdown')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('packet')
    return json.loads(path.read_text(encoding='utf-8'))


def receipt_valid(data):
    if type(data) is not dict or type(data.get('exit_code')) is not int or data['exit_code'] != 0:
        return False
    rows = data.get('checks')
    return (type(rows) is list and bool(rows)
            and all(type(c) is dict and type(c.get('check')) is str and c['check'] and c.get('status') == 'PASS' for c in rows)
            and len({c['check'] for c in rows}) == len(rows))


def log_summary(text):
    found = re.findall(r'^Ran (\d+) tests? in .+$', text, re.M)
    total = int(found[0]) if len(found) == 1 else 0
    return total, total > 0 and text.endswith('\nOK\n')


def shared_document_valid():
    expected = (ROOT / 'production/A-31/readme-ajout.txt').read_bytes().splitlines(keepends=True)
    shared = (ROOT / 'wp/tests/a02-audit/README.md').read_bytes().splitlines(keepends=True)
    return len(expected) == 2 and all(line.endswith(b'\n') and shared.count(line) == 1 for line in expected)


def verify(packet, python_only=False):
    if packet.is_symlink() or any(p.is_symlink() for p in packet.rglob('*')):
        raise ValueError('packet')
    runner = load('a31_runner_verify', ROOT / 'wp/tests/a31/run.py')
    report = load('a31_report_verify', ROOT / 'wp/outils/bascule/a31/report.py')
    oracle = load('a31_expected_verify', ROOT / 'wp/tests/a31/expected.py')
    matrix = read(packet / 'windows-matrix.json')
    checks, counts = [], {}

    def check(key, ok):
        checks.append({'check': key, 'status': 'PASS' if ok else 'FAIL'})

    source = read(packet / 'sources.json')
    check('exact_current_sources', source == runner.manifest(runner.OWN))
    check('exact_current_dependencies', read(packet / 'dependencies.json') == runner.manifest(runner.DEPS))
    check('no_readiness_claim', matrix.get('readiness_claimed') is False)
    check('matrix_scope', matrix['scope'] == ('python_only' if python_only else 'python_and_native'))
    rows = matrix['rows']
    expected = [('python', 'utf-8'), ('python', 'cp1252')] if python_only else [
        ('python', 'utf-8'), ('native', 'utf-8'), ('python', 'cp1252'), ('native', 'cp1252'), ('style', 'utf-8')]
    check('exact_command_matrix', [(row['kind'], row['console']) for row in rows] == expected)
    check('all_commands_pass', matrix['exit_code'] == 0 and matrix['sources_stable'] is True
          and all(row['exit_code'] == 0 and row.get('all_pass') is not False for row in rows))
    for row in rows:
        log = packet / row['log']
        check('bound_log_' + row['kind'] + '_' + row['console'], log.resolve().is_relative_to(packet.resolve())
              and not log.is_symlink() and hashlib.sha256(log.read_bytes()).hexdigest() == row['log_sha256'])
    if not python_only:
        check('shared_document_exact_owned_lines', shared_document_valid())
    for console, encoding in [('utf8', 'utf-8'), ('cp1252', 'cp1252')]:
        base = packet / console
        env = read(base / 'environment.json')
        check(console + ':real_windows_console', env['platform'] == 'win32' and env['stdout'] == env['stderr'] == encoding
              and env['utf8_mode'] == int(console == 'utf8') and env.get('tmpdir', 'missing') is None)
        total, good = log_summary((base / 'python-tests.log').read_text(encoding='utf-8'))
        counts[console + ':python'] = total
        pyrows = [row for row in rows if row['kind'] == 'python' and row['console'] == encoding]
        check(console + ':real_python_tests', good and len(pyrows) == 1 and pyrows[0]['tests_run'] == total)
        if python_only:
            continue
        native = base / 'native'
        receipts = {}
        for name in ('unit', 'adapter-unit', 'result', 'runner', 'classic-standard', 'hpos-standard'):
            receipts[name] = read(native / (name + '.json'))
            counts[console + ':' + name] = len(receipts[name].get('checks', []))
            check(console + ':' + name + '_pass', receipt_valid(receipts[name]))
        red = read(native / 'red-unit.json')
        check(console + ':targeted_k5_red', red['exit_code'] == 1 and any(
            c['check'] == 'year_five_k5' and c['status'] == 'FAIL' for c in red['checks']))
        scalar_red = read(native / 'red-scalar-unit.json')
        check(console + ':targeted_rare_scalar_red', scalar_red['exit_code'] == 1 and any(
            c['check'] == 'scalar_orphan_renewals_1_alone_orphan_renewals' and c['status'] == 'FAIL'
            for c in scalar_red['checks']))
        check(console + ':executed_sources', read(native / 'sources.json') == source)
        check(console + ':executed_dependencies', read(native / 'dependencies.json') == runner.manifest(runner.DEPS))
        check(console + ':pure_no_extensions_no_writes', (native / 'pure.log').read_text(encoding='utf-8')
              == 'A31_PURE_OK ' + str(counts[console + ':unit']) + '\n')
        outer = {c['check']: c for c in receipts['runner']['checks']}
        for phase in ('before', 'after'):
            isolation = outer['isolation_' + phase]['detail']
            check(console + ':isolated_' + phase, isolation['network'] == 'none' and isolation['mounts'] == []
                  and isolation['ports'] == [] and isolation['privileged'] is False and isolation['cap_drop'] == ['ALL']
                  and isolation['no_new_privileges'] is True)
        check(console + ':runner_required', {'red_mutation_k5_caught', 'red_scalar_rare_pool_caught', 'unit_green', 'adapter_native_relation_boundary_green',
              'pure_no_extensions_no_writes', 'native_green', 'cleanup_exact_owned_container',
              'owned_sources_stable', 'dependencies_stable'}.issubset(outer))
        actual = {c['check'] for c in receipts['result']['checks']}
        check(console + ':network_no_listener', {'network_interfaces', 'no_listener:tcp', 'no_listener:tcp6'}.issubset(actual))
        units = {c['check'] for c in receipts['unit']['checks']}
        unit_required = {'renewal_five', 'year_five_k5', 'rare_nature_one_pooled', 'rare_nature_four_pooled', 'oldest_rare_suppressed', 'oldest_five_exact', 'oldest_not_next_visible_year',
                         'closed_unknown_status', 'unknown_nature_not_none', 'neutral_natures_unknown',
                         'neutral_orphan_readable', 'neutral_years_preserved', 'refund_objects_separate',
                         'invalid_date_oldest_illisible', 'missing_account_separate_from_guest',
                         'renewal_orphans_count_orders_not_links'}
        unit_required |= {'nature_' + n for n in report.NATURES}
        unit_required |= {'scalar_' + metric + '_' + str(n) + '_' + mixed + '_' + key
                          for metric in report.LINKS for n in range(6)
                          for mixed in ('alone', 'mixed') for key in report.LINKS}
        unit_required |= {'refund_exact_total_' + str(n) for n in range(6)}
        unit_required |= {'refund_pooled_year_' + str(n) for n in range(6)}
        unit_required |= {'nature_k5_' + nature + '_' + str(n) for nature in report.NATURES for n in range(6)}
        unit_required |= {'nature_k5_mixed', 'refund_k5_mixed_total_exact'}
        check(console + ':required_pure_cases', unit_required.issubset(units))
        adapter = {c['check'] for c in receipts['adapter-unit']['checks']}
        check(console + ':required_adapter_cases', {'parent_native_relation', 'renewal_missing_native_subscription',
              'existing_subscription_not_orphan', 'mixed_natures_illisible', 'parent_and_renewal_illisible',
              'extension_relation_illisible', 'native_filter_contradiction_illisible',
              'missing_reference_never_resolved_by_logging_getter'}.issubset(adapter))
        for storage in ('classic', 'hpos'):
            prefix = console + ':' + storage
            standard = receipts[storage + '-standard']
            check(prefix + ':installed_hashes', type(standard.get('source_sha256')) is dict
                  and len(standard['source_sha256']) >= 10
                  and all(re.fullmatch('[a-f0-9]{64}', h) for h in standard['source_sha256'].values()))
            mandatory = ['installed_standard_before_subject', 'native_seed_1', 'confined_success', 'ten_exact_native_cases',
                         'native_storage_no_fine_date', 'private_references_accounts_dates_absent', 'private_permissions',
                         'replay_identical', 'documented_command_literal', 'unconfined_php_refused',
                         'all_tables_scheduler_unchanged', 'site_files_unchanged', 'config_never_executed',
                         'actual_import_changes_extension_not_structure', 'neutral_success', 'neutral_exact_partial_unknown',
                         'neutral_db_files_unchanged', 'native_seed_5', 'five_success',
                         'five_exact_year_status_nature_relations', 'five_db_files_unchanged', 'all_retained_files_clean',
                         'trash_subscription_exists_not_living_not_orphan', 'utc_boundary_both_directions_oldest']
            mandatory += ['guard_' + key for key in ('exists', 'site', 'repo', 'ancestor', 'root')]
            mandatory += ['audit_refusal_' + key for key in ('schema', 'storage')]
            mandatory += [kind + '_' + key for key in CHANNELS for kind in ('closed_channel', 'discarded_channel')]
            mandatory += ['mutation_witness_' + key for key in WITNESSES]
            check(prefix + ':required_native_cases', all(storage + ':' + key in actual for key in mandatory))
            scalar_rows = read(native / (storage + '-scalar-matrix.json'))
            scalar_cases = [metric + ':' + str(n) + ':' + mixed for metric in report.LINKS
                            for n in range(6) for mixed in ('alone', 'mixed')]
            check(prefix + ':exact_scalar_matrix_complete', [row['case'] for row in scalar_rows] == scalar_cases)
            for row in scalar_rows:
                metric, raw_n, mixed = row['case'].split(':')
                expected_links = {key: int(raw_n) if key == metric else (4 if mixed == 'mixed' else 0) for key in report.LINKS}
                slug = row['case'].replace(':', '_')
                directory = native / (storage + '-scalar-' + slug)
                check(prefix + ':scalar_' + slug,
                      row['expected'] == expected_links and row['db_before'] == row['db_after']
                      and row['files_before'] == row['files_after']
                      and report.complete_report(directory, native / (storage + '-audit/audit.json'))
                      and {key: read(directory / 'commandes.json')['counts'][key] for key in report.LINKS} == expected_links
                      and all(storage + ':scalar_' + stage + '_' + slug in actual for stage in ('seed', 'success', 'exact', 'immutable')))
            for variant in ('', '-neutral', '-five'):
                stem = storage + variant
                before = read(native / (stem + '-db-before.json'))
                required_tables = {'wp_options', 'wp_users', 'wp_usermeta', 'wp_actionscheduler_actions', 'wp_actionscheduler_logs'}
                required_tables |= {'wp_wc_orders', 'wp_wc_orders_meta'} if storage == 'hpos' else {'wp_posts', 'wp_postmeta'}
                check(prefix + variant + ':all_db_immutable', before == read(native / (stem + '-db-after.json'))
                      and required_tables.issubset(before['tables']))
                files = read(native / (stem + '-files.json'))
                check(prefix + variant + ':site_files_immutable', files['before'] == files['after'])
            for variant, av in [('history', 'audit'), ('repeat', 'audit'), ('documented', 'audit'),
                                ('neutral', 'neutral-audit'), ('five', 'five-audit')]:
                directory = native / (storage + '-' + variant)
                check(prefix + ':' + variant + '_valid_projection', report.complete_report(
                    directory, native / (storage + '-' + av) / 'audit.json'))
            nominal = native / (storage + '-history/commandes.json')
            check(prefix + ':exact_base_counts', read(nominal)['counts'] == oracle.expected(1))
            check(prefix + ':exact_five_counts', read(native / (storage + '-five/commandes.json'))['counts'] == oracle.expected(5))
            neutral = oracle.expected(1)
            neutral.update(dict.fromkeys(report.UNREADABLE_AFTER_IMPORT, report.UNKNOWN))
            check(prefix + ':exact_neutral_readable_unknown', read(native / (storage + '-neutral/commandes.json'))['counts'] == neutral)
            for variant in ('repeat', 'documented'):
                check(prefix + ':' + variant + '_identical', (native / (storage + '-' + variant + '/commandes.json')).read_bytes() == nominal.read_bytes())
            provenance = read(native / (storage + '-neutralisation.json'))
            check(prefix + ':actual_import_provenance', provenance['neutraliser_and_anonymiser_executed'] is True
                  and provenance['extension_relation_before'] == 1 and provenance['extension_relation_after'] == 0
                  and provenance['renewal_relation_before'] == provenance['renewal_relation_after'] == 3
                  and provenance['renewal_rows_before'] == provenance['renewal_rows_after'] == 4
                  and provenance['opaque_renewal_before'] == provenance['opaque_renewal_after'] == 1
                  and provenance['structure_before_sha256'] == provenance['structure_after_sha256']
                  and provenance['marker_count'] == 1)
    if not python_only:
        style = read(packet / 'style/style.json')
        check('strict_psr12', receipt_valid(style) and style['phpcs_exit'] == 0
              and style['totals']['errors'] == style['totals']['warnings'] == 0 and style['sources'] == source)
    check('no_retained_private_canary', not any(b'CANARY' in p.read_bytes() for p in packet.rglob('*') if p.is_file()))
    return {'scope': 'python_only' if python_only else 'python_and_native', 'readiness_claimed': False,
            'counts': counts, 'checks': checks, 'exit_code': int(any(c['status'] != 'PASS' for c in checks))}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path, default=ROOT / 'production/A-31/preuves/final')
    ap.add_argument('--python-only', action='store_true')
    a = ap.parse_args()
    try:
        result = verify(a.evidence.resolve(), a.python_only)
    except Exception:
        result = {'exit_code': 1, 'code': 'A31_PACKET_INVALID', 'readiness_claimed': False}
    print(json.dumps(result, indent=2))
    sys.exit(result['exit_code'])
