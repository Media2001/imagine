"""Read-only, source-bound A29 packet verification. Never claims readiness."""
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
    def unique(items):
        d = {}
        for key, value in items:
            if key in d:
                raise ValueError('duplicate receipt')
            d[key] = value
        return d
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite receipt')))


def receipt_valid(data):
    if type(data) is not dict or 'tests' in data or type(data.get('exit_code')) is not int or data['exit_code'] != 0:
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


def document_valid(expected, shared):
    lines = expected.splitlines(keepends=True)
    actual = shared.splitlines(keepends=True)
    return len(lines) == 2 and len(set(lines)) == 2 and all(line.endswith(b'\n') and actual.count(line) == 1 for line in lines)


def shared_document_valid():
    return document_valid((ROOT / 'production/A-29/readme-ajout.txt').read_bytes(),
                          (ROOT / 'wp/tests/a02-audit/README.md').read_bytes())


def expected_counts(repeats):
    if repeats == 1:
        return {'pending': {'groups': [{'family': 'renouvellement', 'count': 9}], 'autres': 6},
                'overdue': {'groups': [], 'autres': 2}, 'failed': {'groups': [], 'autres': 1},
                'renewal_weeks': {'groups': [], 'autres': 7}, 'other_tasks': 'moins de cinq',
                'other_active_extensions': 'attribution indéterminée'}
    return {'pending': {'groups': [{'family': family, 'count': n} for family, n in [
                ('autre', 10), ('email', 5), ('entretien_wordpress', 5), ('fin_abonnement', 5),
                ('nouvelle_tentative', 5), ('renouvellement', 45)]], 'autres': 0},
            'overdue': {'groups': [{'family': 'entretien_wordpress', 'count': 5},
                                  {'family': 'renouvellement', 'count': 5}], 'autres': 0},
            'failed': {'groups': [{'family': 'renouvellement', 'count': 5}], 'autres': 0},
            'renewal_weeks': {'groups': [{'week': week, 'count': n} for week, n in [(1, 10), (2, 15), (3, 5), (8, 5)]], 'autres': 0},
            'other_tasks': 10, 'other_active_extensions': 'attribution indéterminée'}


def verify(packet, python_only=False):
    runner = load('a29_runner_verify', ROOT / 'wp/tests/a29/run.py')
    report = load('a29_report_verify', ROOT / 'wp/outils/bascule/a29/report.py')
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
    check('red_python_pointer', matrix.get('red_python') == 'red-python/red-python.json')
    red_python = read(packet / 'red-python/red-python.json')
    check('real_python_red_green_both_consoles', receipt_valid(red_python)
          and red_python.get('scope') == 'python_closed_schema_mutation_only'
          and red_python.get('readiness_claimed') is False
          and [(r['console'], r['phase'], r['exit_code']) for r in red_python['rows']] == [
              (console, phase, 1 if phase == 'mutation-red' else 0)
              for console in ('utf-8', 'cp1252') for phase in ('baseline-green', 'mutation-red', 'restored-green')])
    for row in red_python['rows']:
        log = packet / 'red-python' / row['log']
        text = log.read_text(encoding='utf-8')
        red_ok = ('FAIL: test_k5_and_closed_family' in text and 'FAILED (failures=1)' in text
                  if row['phase'] == 'mutation-red' else text.endswith('\nOK\n'))
        check('python_witness_' + row['console'] + '_' + row['phase'],
              log.resolve().is_relative_to((packet / 'red-python').resolve()) and not log.is_symlink()
              and hashlib.sha256(log.read_bytes()).hexdigest() == row['log_sha256']
              and 'Ran 1 test in ' in text and red_ok)
    check('matrix_scope', matrix['scope'] == ('python_only' if python_only else 'python_and_native'))
    rows = matrix['rows']
    expected = [('python', 'utf-8'), ('python', 'cp1252')] if python_only else [
        ('python', 'utf-8'), ('native', 'utf-8'), ('python', 'cp1252'), ('native', 'cp1252'), ('style', 'utf-8')]
    check('exact_command_matrix', [(row['kind'], row['console']) for row in rows] == expected)
    check('all_commands_pass', matrix['exit_code'] == 0 and matrix['sources_stable'] is True
          and all(type(row['exit_code']) is int and row['exit_code'] == 0 and row.get('all_pass') is not False for row in rows))
    for row in rows:
        log = packet / row['log']
        check('bound_log_' + row['kind'] + '_' + row['console'], log.resolve().is_relative_to(packet.resolve())
              and not log.is_symlink() and hashlib.sha256(log.read_bytes()).hexdigest() == row['log_sha256'])
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
        for name in ('unit', 'result', 'runner', 'classic-standard', 'hpos-standard'):
            receipt = read(native / (name + '.json'))
            counts[console + ':' + name] = len(receipt.get('checks', []))
            check(console + ':' + name + '_pass', receipt_valid(receipt))
        for storage in ('classic', 'hpos'):
            standard = read(native / (storage + '-standard.json'))
            check(console + ':' + storage + ':installed_code_qualified',
                  standard.get('qualification') == 'installed_source_lexical_gate_and_sha256'
                  and len(standard.get('source_sha256', {})) >= 6
                  and all(re.fullmatch('[a-f0-9]{64}', value) for value in standard['source_sha256'].values()))
        red = read(native / 'red-unit.json')
        check(console + ':real_red_mutation', red['exit_code'] == 1 and any(
            c['check'] == 'closed_family_renewal' and c['status'] == 'FAIL' for c in red['checks']))
        check(console + ':executed_sources', read(native / 'sources.json') == source)
        check(console + ':executed_dependencies', read(native / 'dependencies.json') == runner.manifest(runner.DEPS))
        remote = read(native / 'executed-files.json')
        snapshot = {**source, **read(native / 'dependencies.json')}
        check(console + ':remote_executed_bytes_equal_snapshot',
              remote['before'] == remote['after'] == remote['expected']
              and set(source).issubset(remote['expected'])
              and remote['expected'] == {key: snapshot[key] for key in remote['expected']})
        check(console + ':pure_no_extensions_no_writes', (native / 'pure.log').read_text(encoding='utf-8')
              == 'A29_PURE_OK ' + str(counts[console + ':unit']) + '\n')
        actual = {c['check'] for c in read(native / 'result.json')['checks']}
        for storage in ('classic', 'hpos'):
            prefix = console + ':' + storage
            mandatory = ['installed_standard_before_subject', 'native_seed_1', 'confined_success',
                         'exact_wpcron_as_pending_overdue_failed_weeks', 'native_storage_and_audit_clock',
                         'no_action_callback_executed', 'private_hooks_arguments_ids_dates_absent',
                         'private_permissions', 'replay_identical', 'documented_command_literal', 'unconfined_php_refused',
                         'all_tables_scheduler_unchanged', 'site_files_unchanged', 'config_never_executed',
                         'actual_import_erases_cron_cancels_pending_deletes_failed', 'neutral_success',
                         'neutral_all_unknown_no_useful_number', 'neutral_db_files_unchanged',
                         'native_seed_5', 'five_success', 'five_exact_families_utc_boundaries',
                         'five_db_files_unchanged', 'all_retained_files_clean']
            mandatory += ['native_hybrid_store_refused', 'native_hybrid_refusal_database_files_unchanged']
            mandatory += ['guard_' + key for key in ('exists', 'site', 'repo', 'ancestor', 'root')]
            mandatory += ['audit_refusal_' + key for key in ('schema', 'clock', 'storage')]
            mandatory += [kind + '_' + key for key in CHANNELS for kind in ('closed_channel', 'discarded_channel')]
            mandatory += ['shutdown_mutation_still_valid_json_markdown']
            mandatory += ['mutation_witness_' + key for key in WITNESSES]
            check(prefix + ':required_native_cases', all(storage + ':' + key in actual for key in mandatory))
            for variant in ('', '-neutral', '-five'):
                stem = storage + variant
                before = read(native / (stem + '-db-before.json'))
                check(prefix + variant + ':all_db_immutable', before == read(native / (stem + '-db-after.json'))
                      and {'wp_options', 'wp_actionscheduler_actions', 'wp_actionscheduler_logs',
                           'wp_actionscheduler_claims', 'wp_actionscheduler_groups'}.issubset(before['tables']))
                files = read(native / (stem + '-files.json'))
                check(prefix + variant + ':all_site_files_immutable', files['before'] == files['after'])
            for variant, audit_variant in [('tasks', 'audit'), ('repeat', 'audit'), ('documented', 'audit'),
                                           ('neutral', 'neutral-audit'), ('five', 'five-audit')]:
                check(prefix + ':' + variant + '_valid_projection', report.complete_report(
                    native / (storage + '-' + variant), native / (storage + '-' + audit_variant) / 'audit.json'))
            nominal = native / (storage + '-tasks/taches.json')
            check(prefix + ':exact_base_counts', read(nominal)['counts'] == expected_counts(1))
            check(prefix + ':five_exact_counts', read(native / (storage + '-five/taches.json'))['counts'] == expected_counts(5))
            neutral = read(native / (storage + '-neutral/taches.json'))
            check(prefix + ':all_neutral_unknown', neutral['counts'] == dict.fromkeys(report.COUNTS, report.UNKNOWN))
            for variant in ('repeat', 'documented'):
                check(prefix + ':' + variant + '_identical', (native / (storage + '-' + variant + '/taches.json')).read_bytes() == nominal.read_bytes())
            provenance = read(native / (storage + '-neutralisation.json'))
            check(prefix + ':actual_engine_provenance', provenance == {'neutraliser_and_anonymiser_executed': True,
                  'before': {'cron': 3, 'pending': 12, 'failed': 1},
                  'after': {'cron': 0, 'pending': 0, 'failed': 0, 'canceled': 12}, 'marker_count': 1})
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
    ap.add_argument('--evidence', type=Path, default=ROOT / 'production/A-29/preuves/final')
    ap.add_argument('--python-only', action='store_true')
    a = ap.parse_args()
    try:
        sys.exit(verify(a.evidence.resolve(), a.python_only))
    except Exception:
        print(json.dumps({'exit_code': 1, 'code': 'A29_PACKET_INVALID', 'readiness_claimed': False}))
        sys.exit(1)
