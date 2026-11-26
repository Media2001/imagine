"""Verify the one A24 packet offline. PRET is parent-owned and never a precondition."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OWN = ['wp/outils/bascule/a24', 'wp/tests/a24']
DEPS = ['wp/outils/bascule/' + f for f in ['audit', 'a11', 'a12', 'stream_guard.py', 'stream_refusals.json']] + [
    'wp/tests/a02-audit/' + f for f in ['run.py', 'inside.py', 'seed.php', 'fingerprint.php', 'unit.php', 'readonly-probe.php']
] + ['wp/outils/staging']
CHANNELS = ['direct_stdout', 'direct_stderr', 'display_early_exit', 'silent_early_exit', 'shutdown_stdout',
            'shutdown_stderr', 'shutdown_display', 'invalid_utf8', 'oversize_output', 'plugin_exception',
            'forged_refusal', 'forged_success', 'shutdown_invalid_json', 'shutdown_extra_string',
            'shutdown_markdown', 'shutdown_extra_file', 'shutdown_partial', 'native_free_field', 'native_free_country']
MUTATIONS = ['direct_stdout', 'direct_stderr', 'display_early_exit', 'shutdown_stdout', 'shutdown_stderr', 'shutdown_display']
DELIVERY = ['production/A-24/' + f for f in ('notes.md', 'readme-ajout.txt', 'COMMANDES.md', 'RAPPORT.md')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root, paths):
    files = []
    for relative in paths:
        path = root / relative
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(set(files))}


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def shared_contract(root):
    try:
        lines = (root / 'production/A-24/readme-ajout.txt').read_bytes().splitlines(keepends=True)
        body = (root / 'wp/tests/a02-audit/README.md').read_bytes().splitlines(keepends=True)
        return len(lines) == 2 and all(line.endswith(b'\n') and body.count(line) == 1 for line in lines)
    except OSError:
        return False


def all_green(receipt, minimum=1):
    checks = receipt.get('checks')
    return (receipt.get('exit_code') == 0 and type(checks) is list and len(checks) >= minimum
            and all(c.get('status') == 'PASS' for c in checks)
            and len({c['check'] for c in checks}) == len(checks))


def verify(root=ROOT, packet=None, require_shared=False, require_controls=True):
    packet = packet or root / 'production/A-24/preuves/final'
    checks = []

    def check(name, ok):
        checks.append({'check': name, 'status': 'PASS' if ok else 'FAIL'})

    try:
        seal = load(packet / 'packet.json')
        check('schema', seal['schema'] == 'imagine-a24-proof-v1')
        check('owned_sources_exact', seal['owned_sources'] == inventory(root, OWN))
        check('dependencies_exact', seal['dependency_sources'] == inventory(root, DEPS))
        check('delivery_exact', seal['delivery_sources'] == inventory(root, DELIVERY) and len(seal['delivery_sources']) == 4)
        files = {p.relative_to(packet).as_posix(): sha(p) for p in packet.rglob('*') if p.is_file() and p != packet / 'packet.json'}
        check('packet_inventory_and_bytes_exact', files == seal['evidence_sha256'] and len(files) >= 50)
        delta = (root / 'production/A-24/readme-ajout.txt').read_bytes().splitlines(keepends=True)
        check('shared_delta_two_complete_lines', len(delta) == 2 and all(x.endswith(b'\n') for x in delta))
        if require_shared:
            check('shared_readme_owned_lines_only', shared_contract(root))
        matrix = load(packet / 'matrix.json')
        check('matrix_real_windows_two_encodings', matrix['exit_code'] == 0 and matrix['platform'] == 'win32'
              and matrix['python']['version'].startswith('3.14.')
              and set(matrix['contexts']) == {'utf8', 'cp1252'})
        for context, encoding in [('utf8', 'utf-8'), ('cp1252', 'cp1252')]:
            folder = packet / context
            run = load(folder / 'runner.json')
            check(context + ':runner', all_green(run, 8))
            check(context + ':sources_executed_current', load(folder / 'sources.json') == seal['owned_sources'])
            check(context + ':dependencies_executed_current', load(folder / 'dependencies.json') == seal['dependency_sources'])
            check(context + ':isolated_owned_cleanup', any(c['check'] == 'cleanup_exact_owned_container' for c in run['checks']))
            unit = load(folder / 'unit.json')
            check(context + ':pure_nonempty', all_green(unit, 12))
            lint = load(folder / 'lint.json')
            check(context + ':lint_all_owned_php', all_green(lint, 5))
            py = load(folder / 'python.json')
            check(context + ':python_real_console', py['exit_code'] == 0 and py['encoding'] == encoding
                  and py['python']['platform'] == 'win32' and py['python']['stdout_encoding'] == encoding
                  and py['python']['version'].startswith('3.14.') and py['tests'] >= 13
                  and py['log_sha256'] == sha(folder / 'python.log'))
            native = load(folder / 'result.json')
            check(context + ':native_all_green', all_green(native, 200) and native['no_real_site'] is True)
            names = {c['check'] for c in native['checks']}
            for storage in ('classic', 'hpos'):
                mandatory = ['commercial_fixture', 'native_seed', 'native_standard', 'confined_success',
                             'select_only_account', 'exact_all_metrics_and_country_groups', 'all_private_values_absent',
                             'private_report_permissions', 'documented_only_given_arguments', 'replay_identical',
                             'unconfined_php_refused', 'transaction_readonly_even_root', 'native_filter_requirements_not_hardcoded',
                             'actual_import_preserves_three_country_columns', 'actual_import_erases_non_country_fields',
                             'unknown_for_every_erased_count_country_counts_preserved', 'neutralised_all_tables_files_identical',
                             'all_tables_and_scheduler_identical', 'site_files_identical', 'config_never_executed', 'all_output_artifacts_clean']
                mandatory += ['closed_channel:' + c for c in CHANNELS]
                mandatory += ['mutation_without_guard_detected:' + c for c in MUTATIONS]
                check(context + ':' + storage + ':named_native_cases', all(storage + ':' + n in names for n in mandatory))
                standard = load(folder / (storage + '-standard.json'))
                check(context + ':' + storage + ':standard', all_green(standard, 7)
                      and standard['woocommerce'] == '11.1.1' and standard['subscriptions'] == '9.4.1'
                      and len(standard['source_sha256']) >= 12)
                check(context + ':' + storage + ':complete_db_fingerprints', load(folder / (storage + '-db-before.json'))
                      == load(folder / (storage + '-db-after.json')))
                check(context + ':' + storage + ':neutralised_db_fingerprints', load(folder / (storage + '-neutralised-db-before.json'))
                      == load(folder / (storage + '-neutralised-db-after.json')))
                for label in ('files', 'neutralised-files'):
                    f = load(folder / (storage + '-' + label + '.json'))
                    check(context + ':' + storage + ':' + label, len(f['before']) == 64 and f['before'] == f['after'])
                for label, photo in [('addresses', storage + '-audit'), ('documented', storage + '-audit'),
                                     ('repeat', storage + '-audit'), ('root-readonly', storage + '-audit'),
                                     ('native-required-override', storage + '-audit'), ('neutralised', storage + '-neutralised-audit')]:
                    spec = __import__('importlib.util', fromlist=['spec_from_file_location'])
                    module_spec = spec.spec_from_file_location('a24_verify_report', root / 'wp/outils/bascule/a24/report.py')
                    report = spec.module_from_spec(module_spec)
                    module_spec.loader.exec_module(report)
                    check(context + ':' + storage + ':closed_report:' + label,
                          report.complete_report(folder / (storage + '-' + label), folder / photo / 'audit.json'))
            check(context + ':payload_canaries_absent', all(b'CANARY' not in p.read_bytes() for p in folder.rglob('*') if p.is_file()))
        if require_controls:
            controls = load(packet / 'utf8/reception-controls.json')
            expected_controls = {'full_verifier_before_future_pret', 'full_verifier_after_future_pret',
                                 'owned_source_mutation_refused', 'dependency_mutation_refused',
                                 'report_payload_mutation_refused', 'all_mutations_restored_green'}
            check('real_reception_controls', all_green(controls, 6)
                  and {c['check'] for c in controls['checks']} == expected_controls)
        # No PRET read, hash or absence check: future owner readiness is orthogonal.
    except (OSError, ValueError, KeyError, TypeError, AssertionError, ImportError):
        check('packet_complete_and_parseable', False)
    return {'suite': 'A24-offline-reception', 'checks': checks,
            'shared_readme': 'verified' if require_shared else 'delta_pending_parent',
            'exit_code': int(any(c['status'] != 'PASS' for c in checks))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path)
    parser.add_argument('--require-shared', action='store_true')
    args = parser.parse_args()
    result = verify(ROOT, args.packet, args.require_shared)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
