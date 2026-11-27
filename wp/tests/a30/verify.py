"""No-argument A30 packet verifier. Python-only is intentionally NOT acceptance."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET = ROOT / 'production/A-30/preuves/final'
from cases import CHANNELS, EXPECTED_LINES


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def receipt_valid(data):
    if (not isinstance(data, dict) or data.get('exit_code') != 0
            or not isinstance(data.get('checks'), list) or not data['checks']):
        return False
    rows = data['checks']
    return (all(isinstance(row, dict) and isinstance(row.get('check'), str) and row['check']
                and row.get('status') == 'PASS' for row in rows)
            and len({row['check'] for row in rows}) == len(rows))


def shared_contract(shared, expected):
    lines = expected.splitlines(keepends=True)
    return len(lines) == 2 and all(line.endswith(b'\n') and shared.splitlines(keepends=True).count(line) == 1 for line in lines)


def verify(packet=PACKET):
    checks = []

    def check(name, value):
        checks.append({'check': name, 'status': 'PASS' if value else 'FAIL'})

    native = False
    try:
        spec = importlib.util.spec_from_file_location('a30_verify_runner', HERE / 'run.py')
        runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
        check('current_owned_sources', read(packet / 'sources.json') == runner.manifest(runner.OWN))
        check('parent_shared_two_lines', shared_contract(
            (ROOT / 'wp/outils/bascule/README.md').read_bytes(),
            (ROOT / 'production/A-30/README-AJOUT-2-LIGNES.txt').read_bytes()))
        matrix = read(packet / 'windows-matrix.json')
        check('python_matrix_exit', matrix['exit_code'] == 0)
        for label, encoding, mode in [('utf8', 'utf-8', 1), ('cp1252', 'cp1252', 0)]:
            folder = packet / label
            env = read(folder / 'environment.json')
            check(label + ':real_windows_console', env['platform'] == 'win32' and env['utf8_mode'] == mode
                  and env['stdout'].lower() == encoding and env['stderr'].lower() == encoding
                  and bool(env['executable']) and '3.14.6' in env['version'])
            rows = [row for row in matrix['rows'] if row['console'] == encoding and 'tests_run' in row]
            check(label + ':python_tests', len(rows) == 1 and rows[0]['exit_code'] == 0
                  and rows[0]['all_pass'] is True and rows[0]['tests_run'] >= 17
                  and rows[0]['log_sha256'] == hashlib.sha256((folder / 'python-tests.log').read_bytes()).hexdigest())
            # Missing files fail closed, never convert a test plan into a native receipt.
            n = folder / 'native'
            receipt = read(n / 'runner.json')
            required_runner = {'isolation_before', 'isolation_after', 'unit_return', 'pure_no_extensions_no_writes',
                               'native_return', 'cleanup_exact_owned_container', 'owned_sources_stable', 'dependencies_stable'}
            check(label + ':native_runner', receipt_valid(receipt) and receipt['mode'] == 'full'
                  and required_runner <= {r['check'] for r in receipt['checks']})
            check(label + ':native_current_sources', read(n / 'sources.json') == runner.manifest(runner.OWN)
                  and read(n / 'dependencies.json') == runner.manifest(runner.DEPS))
            unit = read(n / 'unit.json')
            check(label + ':pure_seven_checks', len(unit['checks']) == 7 and all(r['status'] == 'PASS' for r in unit['checks']))
            result = read(n / 'result.json')
            check(label + ':native_checks', receipt_valid(result) and result['no_real_site'] is True)
            names = {r['check'] for r in result['checks']}
            for storage in ('classic', 'hpos'):
                required = ['commercial_fixture', 'native_seed', 'audit_success', 'confined_success',
                            'five_issues_exact_lines', 'counts_k5', 'no_private_values', 'input_immutable',
                            'replay_identical', 'existing_output_refused', 'documented_command',
                            'a13_exact_refusal:iban', 'a13_exact_refusal:encoding',
                            'a13_fixture:clean', 'a13_fixture:dirty', 'a13_exact_lines:clean', 'a13_exact_lines:dirty',
                            'all_sql_tables_identical', 'site_files_identical', 'config_never_executed',
                            'actual_neutralisation', 'neutral_audit', 'neutral_success', 'neutral_unknown_never_zero',
                            'neutral_sql_files_identical']
                required += [prefix + channel for channel in CHANNELS for prefix in ('closed_channel:', 'no_retained_payload:')]
                check(label + ':' + storage + ':required_native_checks', {storage + ':' + x for x in required} <= names)
                lines = read(n / (storage + '-five/lines.json'))
                summary = read(n / (storage + '-five/summary.json'))
                check(label + ':' + storage + ':actual_five_issues', lines['issues'] == EXPECTED_LINES
                      and lines['rapprochement_inconnu'] == [] and summary['total'] == 25
                      and summary['storage'] == storage
                      and summary['issues'] == {'groups': [{'key': key, 'count': 5} for key in sorted(EXPECTED_LINES)], 'autres': 0})
                check(label + ':' + storage + ':db_observations_equal', read(n / (storage + '-db-before.json'))
                      == read(n / (storage + '-db-after.json')))
                files = read(n / (storage + '-files.json'))
                check(label + ':' + storage + ':file_observations_equal', files['before'] == files['after'])
                neutral = read(n / (storage + '-neutral/summary.json'))
                neutral_lines = read(n / (storage + '-neutral/lines.json'))
                check(label + ':' + storage + ':actual_neutral_unknown', neutral['accounts'] == 'inconnu après neutralisation'
                      and neutral_lines['issues']['compte_a_creer'] == neutral_lines['issues']['compte_existant'] == 'inconnu après neutralisation'
                      and neutral_lines['rapprochement_inconnu'] == list(range(2, 12)))
                check(label + ':' + storage + ':neutral_db_equal', read(n / (storage + '-neutral-db-before.json'))
                      == read(n / (storage + '-neutral-db-after.json')))
        native = all(c['status'] == 'PASS' for c in checks)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        check('complete_current_packet_required', False)
    return {'exit_code': int(not native), 'native_proven': native, 'readiness_claimed': False, 'checks': checks}


if __name__ == '__main__':
    if len(sys.argv) != 1:
        print('A30_VERIFY_NO_ARGUMENTS', file=sys.stderr)
        sys.exit(1)
    result = verify()
    print(json.dumps(result, indent=2))
    sys.exit(result['exit_code'])
