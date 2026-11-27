"""Read-only source-bound A27 packet verifier. No Docker/PHP or readiness claim."""
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
    return json.loads(path.read_text(encoding='utf-8'))


def receipt_valid(data):
    if type(data) is not dict or type(data.get('exit_code')) is not int or data['exit_code'] != 0:
        return False
    rows = data.get('checks')
    if type(rows) is not list or not rows:
        return False
    return (all(type(c) is dict and type(c.get('check')) is str and c['check'] and c.get('status') == 'PASS' for c in rows)
            and len({c['check'] for c in rows}) == len(rows))


def log_summary(text):
    found = re.findall(r'^Ran (\d+) tests? in .+$', text, re.M)
    total = int(found[0]) if len(found) == 1 else 0
    return total, total > 0 and text.endswith('\nOK\n')


def shared_document_valid():
    expected = (ROOT / 'production/A-27/readme-ajout.txt').read_bytes().splitlines(keepends=True)
    shared = (ROOT / 'wp/tests/a02-audit/README.md').read_bytes().splitlines(keepends=True)
    return len(expected) == 2 and all(line.endswith(b'\n') and shared.count(line) == 1 for line in expected)


def verify(packet, python_only=False):
    runner = load('a27_runner_verify', ROOT / 'wp/tests/a27/run.py')
    report = load('a27_report_verify', ROOT / 'wp/outils/bascule/a27/report.py')
    matrix = read(packet / 'windows-matrix.json')
    checks = []
    counts = {}

    def check(key, ok):
        checks.append({'check': key, 'status': 'PASS' if ok else 'FAIL'})

    source = read(packet / 'sources.json')
    check('exact_current_sources', source == runner.manifest(runner.OWN))
    if not python_only:
        check('shared_document_exact_owned_lines', shared_document_valid())
    check('exact_current_dependencies', read(packet / 'dependencies.json') == runner.manifest(runner.DEPS))
    check('no_pret_claim', matrix.get('readiness_claimed') is False)
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
              and hashlib.sha256(log.read_bytes()).hexdigest() == row['log_sha256'])
    for console, encoding in [('utf8', 'utf-8'), ('cp1252', 'cp1252')]:
        base = packet / console
        env = read(base / 'environment.json')
        check(console + ':real_windows_console', env['platform'] == 'win32' and env['stdout'] == env['stderr'] == encoding
              and env['utf8_mode'] == int(console == 'utf8'))
        total, good = log_summary((base / 'python-tests.log').read_text(encoding='utf-8'))
        counts[console + ':python'] = total
        pyrows = [row for row in rows if row['kind'] == 'python' and row['console'] == encoding]
        check(console + ':real_python_tests', good and len(pyrows) == 1 and pyrows[0]['tests_run'] == total)
        if python_only:
            continue
        native = base / 'native'
        for name in ('unit', 'adapter-unit', 'result', 'runner', 'classic-standard', 'hpos-standard'):
            receipt = read(native / (name + '.json'))
            counts[console + ':' + name] = len(receipt.get('checks', []))
            check(console + ':' + name + '_pass', receipt_valid(receipt))
        red = read(native / 'red-unit.json')
        check(console + ':real_red_mutation', red['exit_code'] == 1 and any(
            c['check'] == 'cc_native_type' and c['status'] == 'FAIL' for c in red['checks']))
        for filename, required in [('red-r2.json', {'opaque_adapted_presence',
                                                      'opaque_five_automatic_illisible', 'opaque_five_relation_unknown'}),
                                   ('red-r3.json', {'explicit_contradiction_stripe_sepa'})]:
            red = read(native / filename)
            failed = {c['check'] for c in red['checks'] if c['status'] == 'FAIL'}
            check(console + ':' + filename + '_targeted_red', red['exit_code'] == 1 and required.issubset(failed))
        adapter = {c['check'] for c in read(native / 'adapter-unit.json')['checks']}
        check(console + ':adapter_boundary_required', {'opaque_actual_a19_boundary', 'opaque_adapted_presence',
              'opaque_five_automatic_illisible', 'opaque_five_relation_unknown', 'opaque_one_schema_evaluation',
              'empty_adapted_presence', 'observer_removed_after_exception'}.issubset(adapter))
        unit_checks = {c['check'] for c in read(native / 'unit.json')['checks']}
        check(console + ':r3_required_distinct_cases', all(kind + gateway in unit_checks
              for gateway in ('stripe_sepa', 'paypal') for kind in ('explicit_contradiction_',
              'explicit_unresolved_', 'reference_only_fallback_', 'explicit_unique_match_')))
        check(console + ':executed_sources', read(native / 'sources.json') == source)
        check(console + ':executed_dependencies', read(native / 'dependencies.json') == runner.manifest(runner.DEPS))
        check(console + ':pure_no_extensions_no_writes', (native / 'pure.log').read_text(encoding='utf-8')
              == 'A27_PURE_OK ' + str(counts[console + ':unit']) + '\n')
        actual = {c['check'] for c in read(native / 'result.json')['checks']}
        for storage in ('classic', 'hpos'):
            prefix = console + ':' + storage
            mandatory = ['installed_standard_before_subject', 'native_seed_1', 'confined_success',
                         'six_exact_native_cases', 'native_storage_and_audit_clock', 'private_references_accounts_dates_absent',
                         'private_permissions', 'replay_identical', 'documented_command_literal', 'unconfined_php_refused',
                         'all_tables_scheduler_unchanged', 'site_files_unchanged', 'config_never_executed',
                         'actual_import_purges_tokens', 'neutral_success', 'neutral_all_unknown_no_useful_number',
                         'neutral_db_files_unchanged', 'native_seed_5', 'five_success',
                         'five_exact_gateway_type_expiry_relations', 'five_db_files_unchanged', 'all_retained_files_clean']
            mandatory += ['guard_' + key for key in ('exists', 'site', 'repo', 'ancestor', 'root')]
            mandatory += ['audit_refusal_' + key for key in ('schema', 'clock', 'storage')]
            mandatory += [kind + '_' + key for key in CHANNELS for kind in ('closed_channel', 'discarded_channel')]
            mandatory += ['mutation_witness_' + key for key in WITNESSES]
            mandatory += [kind + case for case in ('opaque', 'conflict', 'reference-only', 'unique')
                          for kind in ('correction_seed_', 'correction_success_', 'correction_exact_five_',
                                       'correction_db_files_unchanged_', 'correction_private_values_absent_')]
            check(prefix + ':required_native_cases', all(storage + ':' + key in actual for key in mandatory))
            for case in ('opaque', 'conflict', 'reference-only', 'unique'):
                stem = storage + '-correction-' + case
                gateway = 'ppcp-gateway' if case == 'opaque' else 'stripe_sepa'
                kind = 'illisible' if case in ('opaque', 'conflict') else 'mandat_sepa'
                relations = []
                if case in ('conflict', 'unique'):
                    relations.append({'gateway': 'autre', 'metric': 'accounts_multiple_tokens', 'count': 5})
                if case != 'unique':
                    relations.append({'gateway': gateway, 'metric': 'subscriptions_unlinked' if case == 'reference-only'
                                      else 'subscriptions_link_unknown', 'count': 5})
                expected_case = {'automatic': {'groups': [{'gateway': gateway, 'type': kind, 'count': 5}], 'autres': 0},
                                 'cards': {'groups': [], 'autres': 0}, 'relations': {'groups': relations, 'autres': 0}}
                correction = read(native / stem / 'paiements.json')
                check(prefix + ':correction_exact_counts_' + case,
                      correction['storage'] == storage and correction['counts'] == expected_case)
                check(prefix + ':correction_projection_' + case, report.complete_report(
                    native / stem, native / (stem + '-audit') / 'audit.json'))
                check(prefix + ':correction_db_immutable_' + case,
                      read(native / (stem + '-db-before.json')) == read(native / (stem + '-db-after.json')))
                files = read(native / (stem + '-files.json'))
                check(prefix + ':correction_files_immutable_' + case, files['before'] == files['after'])
            for variant in ('', '-neutral', '-five'):
                stem = storage + variant
                before = read(native / (stem + '-db-before.json'))
                check(prefix + variant + ':all_db_immutable', before == read(native / (stem + '-db-after.json'))
                      and {'wp_options', 'wp_woocommerce_payment_tokens', 'wp_woocommerce_payment_tokenmeta',
                           'wp_actionscheduler_actions', 'wp_actionscheduler_logs'}.issubset(before['tables']))
                files = read(native / (stem + '-files.json'))
                check(prefix + variant + ':all_site_files_immutable', files['before'] == files['after'])
            for variant, audit_variant in [('payments', 'audit'), ('repeat', 'audit'), ('documented', 'audit'),
                                           ('neutral', 'neutral-audit'), ('five', 'five-audit')]:
                check(prefix + ':' + variant + '_valid_projection', report.complete_report(
                    native / (storage + '-' + variant), native / (storage + '-' + audit_variant) / 'audit.json'))
            nominal = native / (storage + '-payments/paiements.json')
            data = read(nominal)
            check(prefix + ':exact_base_counts', data['storage'] == storage and data['counts'] == {
                key: {'groups': [], 'autres': n} for key, n in [('automatic', 6), ('cards', 3), ('relations', 4)]})
            neutral = read(native / (storage + '-neutral/paiements.json'))
            check(prefix + ':all_neutral_unknown', neutral['counts'] == dict.fromkeys(report.COUNTS, report.UNKNOWN))
            for variant in ('repeat', 'documented'):
                check(prefix + ':' + variant + '_identical', (native / (storage + '-' + variant + '/paiements.json')).read_bytes() == nominal.read_bytes())
            five = read(native / (storage + '-five/paiements.json'))
            expected_auto = [{'gateway': 'paypal', 'type': 'accord_paypal', 'count': 5},
                             {'gateway': 'stripe', 'type': 'carte', 'count': 15},
                             {'gateway': 'stripe', 'type': 'illisible', 'count': 5},
                             {'gateway': 'stripe_sepa', 'type': 'mandat_sepa', 'count': 5}]
            check(prefix + ':five_reference_types_exact', five['counts']['automatic'] == {'groups': expected_auto, 'autres': 0})
            provenance = read(native / (storage + '-neutralisation.json'))
            check(prefix + ':actual_engine_provenance', provenance == {'neutraliser_and_anonymiser_executed': True,
                  'tokens_before': 6, 'tokens_after': 0, 'tokenmeta_after': 0, 'marker_count': 1})
    if not python_only:
        style = read(packet / 'style/style.json')
        check('strict_psr12', receipt_valid(style) and style['phpcs_exit'] == 0
              and style['totals']['errors'] == style['totals']['warnings'] == 0 and style['sources'] == source)
    check('no_retained_private_canary', not any(b'CANARY' in p.read_bytes() for p in packet.rglob('*') if p.is_file()))
    result = {'scope': 'python_only' if python_only else 'python_and_native', 'readiness_claimed': False,
              'counts': counts, 'checks': checks, 'exit_code': int(any(c['status'] != 'PASS' for c in checks))}
    print(json.dumps(result, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path, default=ROOT / 'production/A-27/preuves/final')
    ap.add_argument('--python-only', action='store_true')
    a = ap.parse_args()
    try:
        sys.exit(verify(a.evidence.resolve(), a.python_only))
    except Exception:
        print(json.dumps({'exit_code': 1, 'code': 'A27_PACKET_INVALID', 'readiness_claimed': False}))
        sys.exit(1)
