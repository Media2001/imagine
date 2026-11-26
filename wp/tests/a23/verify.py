"""Read-only A23 candidate verification. PRET and global gates belong to parent."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OWN = ['wp/outils/bascule/a23', 'wp/tests/a23']
PACKAGE = OWN + ['production/A-23']
RESERVED = {'production/A-23/PRET', 'production/A-23/manifest.json', 'production/A-23/candidate-verification.json'}
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
    if type(d) is not dict or 'tests' in d or d.get('exit_code') != 0 or type(d.get('checks')) is not list or not d['checks']:
        return False
    rows = d['checks']
    if not all(type(c) is dict and type(c.get('check')) is str and c['check'] and c.get('status') == 'PASS' for c in rows):
        return False
    return len({c['check'] for c in rows}) == len(rows)


def shared_contract(shared, expected):
    lines = expected.splitlines(keepends=True)
    return len(lines) == 2 and all(line.endswith(b'\n') and shared.splitlines(keepends=True).count(line) == 1 for line in lines)


def verify(packet, sealed=True, require_shared=False):
    checks, counts = [], {}

    def check(key, ok):
        checks.append({'check': key, 'status': 'PASS' if ok else 'FAIL'})

    source = read(packet / 'sources.json')
    check('current_owned_sources', source == inventory(OWN))
    runner_module = load_module('a23_runner', ROOT / 'wp/tests/a23/run.py')
    report_module = load_module('a23_report', ROOT / 'wp/outils/bascule/a23/report.py')
    required = ['commercial_fixture', 'native_seed', 'audit_success', 'confined_success',
                'exact:readers', 'exact:live_readers', 'exact:without_commerce', 'all_private_values_absent',
                'private_report_permissions', 'replay_identical', 'documented_only_given_arguments',
                'unconfined_php_refused', 'transaction_readonly_even_root', 'audit_guard:schema', 'audit_guard:storage',
                'all_tables_and_scheduler_identical', 'site_files_identical', 'config_never_executed',
                'actual_import_replaces_three_fields', 'neutralised_audit', 'neutralised_success',
                'six_unknown_blocks_never_zero', 'useful_counts_preserved_after_import',
                'neutralised_all_tables_files_identical', 'all_output_artifacts_clean']
    required += ['guard:' + name for name in ('exists', 'site', 'repo', 'ancestor', 'root')]
    required += ['symlink_closed:' + name for name in ('False', 'True')]
    required += ['closed_dropin:' + str(i) for i in range(6)]
    required += ['config_closed:' + name for name in ('define', 'const')]
    required += [kind + ':' + name for name in CHANNELS for kind in ('closed_channel', 'no_retained_payload')]
    required += ['mutation_without_guard_detected:' + name for name in ('direct_stdout', 'direct_stderr', 'display_early_exit', 'shutdown_stdout')]
    for console in ('utf8', 'cp1252'):
        base, folder = packet / console, packet / console / 'native'
        environment = read(base / 'environment.json')
        check(console + ':measured_windows_console', environment['platform'] == 'win32'
              and environment['stdout'] == ('utf-8' if console == 'utf8' else 'cp1252')
              and environment['stderr'] == environment['stdout'] and environment['utf8_mode'] == int(console == 'utf8'))
        text = (base / 'python-tests.log').read_text(encoding='utf-8')
        match = re.search(r'Ran (\d+) tests in ', text)
        counts[console + ':python'] = int(match[1]) if match else 0
        check(console + ':python_tests_pass', counts[console + ':python'] >= 22 and '\nOK\n' in text)
        for kind in ('unit', 'standard', 'result', 'runner'):
            d = read(folder / (kind + '.json'))
            counts[console + ':' + kind] = len(d.get('checks', []))
            check(console + ':' + kind + '_all_pass', receipt_valid(d))
        native = {c['check']: c for c in read(folder / 'result.json')['checks']}
        check(console + ':executed_current_sources', read(folder / 'sources.json') == source)
        check(console + ':current_dependencies', read(folder / 'dependencies.json') == runner_module.manifest(runner_module.DEPS))
        check(console + ':pure_no_writes', (folder / 'pure.log').read_text(encoding='utf-8')
              == 'A23_PURE_OK ' + str(counts[console + ':unit']) + '\n')
        for storage in ('classic', 'hpos'):
            prefix = console + ':' + storage
            check(prefix + ':all_mandatory_cases', all(storage + ':' + name in native for name in required))
            before, after = read(folder / (storage + '-db-before.json')), read(folder / (storage + '-db-after.json'))
            check(prefix + ':all_table_hashes_identical', before == after
                  and {'wp_users', 'wp_options', 'wp_actionscheduler_actions', 'wp_actionscheduler_logs'}.issubset(before['tables']))
            check(prefix + ':neutralised_all_table_hashes_identical',
                  read(folder / (storage + '-neutralised-db-before.json')) == read(folder / (storage + '-neutralised-db-after.json')))
            audit = folder / (storage + '-audit/audit.json')
            report = folder / (storage + '-accounts')
            check(prefix + ':strict_report_projection', report_module.complete_report(report, audit))
            d = read(report / 'comptes.json')
            check(prefix + ':authoritative_storage', d['storage'] == storage)
            check(prefix + ':exact_population_counts', d['counts']['readers']['accounts'] == 32
                  and d['counts']['live_readers']['accounts'] == 20
                  and d['counts']['without_commerce'] == {'groups': [], 'autres': 3})
            for suffix in ('repeat', 'documented', 'root-readonly'):
                check(prefix + ':' + suffix + '_identical', (folder / (storage + '-' + suffix) / 'comptes.json').read_bytes()
                      == (report / 'comptes.json').read_bytes())
            check(prefix + ':neutralised_strict_projection', report_module.complete_report(
                folder / (storage + '-neutralised'), folder / (storage + '-neutralised-audit/audit.json')))
    style = read(packet / 'style/style.json')
    check('strict_psr12_current_sources', receipt_valid(style) and style['phpcs_exit'] == 0
          and style['totals']['errors'] == style['totals']['warnings'] == 0 and style['sources'] == source)
    matrix = read(packet / 'windows-matrix.json')
    check('five_commands_all_pass', matrix['exit_code'] == 0 and len(matrix['rows']) == 5
          and all(row['exit_code'] == 0 and row.get('all_pass') is not False for row in matrix['rows']))
    check('command_log_hashes', all(hashlib.sha256((packet / row['log']).read_bytes()).hexdigest() == row['log_sha256'] for row in matrix['rows']))
    check('retained_artifacts_clean', not any(b'CANARY' in p.read_bytes() for p in packet.rglob('*') if p.is_file()))
    check('parent_gates_not_claimed', read(packet / 'candidate.json') == {'status': 'CANDIDAT_GATE_PARENT', 'readiness_claimed': False,
                                                                      'parent_preparation': 'pending', 'parent_global_T01': 'pending'})
    delta = (ROOT / 'production/A-23/readme-ajout.txt').read_bytes()
    check('two_line_delta', len(delta.splitlines()) == 2 and delta.endswith(b'\n'))
    if require_shared:
        check('only_own_shared_lines', shared_contract((ROOT / 'wp/tests/a02-audit/README.md').read_bytes(), delta))
    if sealed:
        check('exact_final_inventory_and_hashes', read(ROOT / 'production/A-23/manifest.json') == inventory(PACKAGE))
    result = {'status': 'CANDIDAT_GATE_PARENT', 'readiness_claimed': False,
              'counts': counts, 'checks': checks, 'exit_code': int(any(c['status'] != 'PASS' for c in checks))}
    print(json.dumps(result, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path, default=ROOT / 'production/A-23/preuves/final')
    ap.add_argument('--unsealed', action='store_true')
    ap.add_argument('--require-shared-doc', action='store_true')
    a = ap.parse_args()
    try:
        sys.exit(verify(a.evidence.resolve(), not a.unsealed, a.require_shared_doc))
    except Exception:
        print(json.dumps({'exit_code': 1, 'code': 'A23_PACKET_INVALID'}))
        sys.exit(1)
