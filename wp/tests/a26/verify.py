"""Read-only verifier. Native acceptance requires a real full packet; never PRET."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16777216:
        raise RuntimeError('A26_EVIDENCE_FILE_INVALID')
    return json.loads(path.read_bytes())


def passed(receipt):
    checks = receipt.get('checks')
    return (receipt.get('exit_code') == 0 and type(checks) is list and len(checks) > 0
            and all(type(row) is dict and row.get('status') == 'PASS' for row in checks))


def named(receipt, required):
    if not passed(receipt):
        return False
    names = [row['check'] for row in receipt['checks']]
    return len(names) == len(set(names)) and set(required) <= set(names)


def shared_document_valid():
    expected = (ROOT / 'production/A-26/readme-ajout.txt').read_bytes().splitlines(keepends=True)
    shared = (ROOT / 'wp/tests/a02-audit/README.md').read_bytes().splitlines(keepends=True)
    return len(expected) == 2 and all(line.endswith(b'\n') and shared.count(line) == 1 for line in expected)


def verify(packet, python_only=False, require_shared=False):
    r = load('a26_verified_runner', HERE / 'run.py')
    m = load('a26_verified_matrix', HERE / 'matrix.py')
    report = load('a26_verified_report', ROOT / 'wp/outils/bascule/a26/report.py')
    if read(packet / 'sources.json') != r.manifest(r.OWN) or read(packet / 'dependencies.json') != r.manifest(r.DEPS):
        raise RuntimeError('A26_SOURCE_DRIFT')
    matrix = read(packet / 'windows-matrix.json')
    rows = matrix['rows']
    if (matrix['exit_code'] != 0 or matrix['native_executed'] is not (not python_only)
            or len(rows) != (2 if python_only else 5)):
        raise RuntimeError('A26_MATRIX_INCOMPLETE')
    summaries = []
    for row in rows:
        relative = Path(row['log'])
        if relative.is_absolute() or '..' in relative.parts:
            raise RuntimeError('A26_LOG_POINTER_INVALID')
        log = packet / relative
        text = log.read_text(encoding='utf-8')
        if row['exit_code'] != 0 or hashlib.sha256(log.read_bytes()).hexdigest() != row['log_sha256']:
            raise RuntimeError('A26_LOG_RECEIPT_INVALID')
        if '-m' in row['command'] and 'unittest' in row['command']:
            summary = m.python_summary(text, row['exit_code'])
            if not summary['all_pass'] or summary['tests_run'] != row['tests_run']:
                raise RuntimeError('A26_PYTHON_DISCOVERY_INVALID')
            summaries.append(summary['tests_run'])
    if len(summaries) != 2 or summaries[0] != summaries[1]:
        raise RuntimeError('A26_PYTHON_MATRIX_INVALID')
    for console, encoding, mode in [('utf8', 'utf-8', 1), ('cp1252', 'cp1252', 0)]:
        folder = packet / console
        environment = read(folder / 'environment.json')
        if (environment['platform'] != 'win32' or environment['stdout'] != encoding
                or environment['stderr'] != encoding or environment['utf8_mode'] != mode):
            raise RuntimeError('A26_CONSOLE_NOT_EXERCISED')
        if python_only:
            continue
        native = folder / 'native'
        for filename in ('sources.json', 'dependencies.json'):
            if read(native / filename) != read(packet / filename):
                raise RuntimeError('A26_EXECUTED_SOURCE_DRIFT')
        runner = read(native / 'runner.json')
        if not named(runner, ['unit_return', 'php_red_green_return', 'pure_inclusion_no_extensions_no_writes',
                              'native_return', 'installed_standard', 'isolation_before', 'isolation_after',
                              'cleanup_exact_owned_container', 'owned_sources_stable', 'dependencies_stable']):
            raise RuntimeError('A26_RUNNER_INCOMPLETE')
        if not passed(read(native / 'standard.json')) or not named(read(native / 'red-green.json'),
            ['neutralisation_mutant_red', 'owned_source_restored_exactly', 'final_source_green']):
            raise RuntimeError('A26_PHP_PROOF_INCOMPLETE')
        if not passed(read(native / 'unit.json')):
            raise RuntimeError('A26_UNIT_FAILED')
        red = read(native / 'red-unit.json')
        if red.get('exit_code') != 1 or not any(row['check'] == 'neutral_content_unknown_possible_whole_value_scrub'
                and row['status'] == 'FAIL' for row in red['checks']):
            raise RuntimeError('A26_RED_NOT_OBSERVED')
        result = read(native / 'result.json')
        required = []
        for storage in ('classic', 'hpos'):
            required.extend(storage + ':' + name for name in (
                'confined_success', 'one_active_each_family', 'exact_content_per_service_once', 'annual_fallback_utc',
                'all_private_values_absent_all_report_files', 'documented_command_only_given_arguments',
                'all_tables_and_scheduler_identical', 'site_files_identical', 'actual_unchanged_import_executed',
                'neutral_unknown_never_zero', 'neutralised_all_tables_files_identical', 'all_output_artifacts_clean'))
            for channel in ('direct_stdout', 'direct_stderr', 'display_early_exit', 'shutdown_stdout', 'shutdown_stderr',
                            'shutdown_display', 'shutdown_markdown', 'shutdown_extra_string', 'shutdown_valid_counts_and_markdown'):
                required.append(storage + ':closed_channel:' + channel)
            for mode in ('postmeta', 'post_parent', 'taxonomy'):
                required.append(storage + ':last_ten_exact_no_oldest_no_orphans:' + mode)
            for phase in ('', '-neutralised'):
                prefix = storage + phase
                if read(native / (prefix + '-db-before.json')) != read(native / (prefix + '-db-after.json')):
                    raise RuntimeError('A26_DATABASE_CHANGED')
                fingerprints = read(native / (prefix + '-files.json'))
                if fingerprints['before'] != fingerprints['after']:
                    raise RuntimeError('A26_SITE_FILES_CHANGED')
            for suffix, photo in [('-tiers', '-audit'), ('-neutralised', '-neutralised-audit'),
                                   ('-repeat', '-audit'), ('-documented', '-audit')]:
                if not report.complete_report(native / (storage + suffix), native / (storage + photo) / 'audit.json'):
                    raise RuntimeError('A26_PUBLISHED_REPORT_INVALID')
        if not named(result, required):
            raise RuntimeError('A26_NATIVE_CASES_INCOMPLETE')
    if not python_only:
        style = read(packet / 'style/style.json')
        if not passed(style) or style.get('sources') != read(packet / 'sources.json'):
            raise RuntimeError('A26_STYLE_NOT_FINAL')
    if require_shared and not shared_document_valid():
        raise RuntimeError('A26_SHARED_DOC_PENDING')
    return {'status': 'PYTHON_ONLY_VERIFIED_NATIVE_PENDING' if python_only else 'NATIVE_PACKET_VERIFIED_PARENT_GATES_PENDING',
            'python_tests_per_console': summaries[0], 'readiness_claimed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', default=ROOT / 'production/A-26/preuves/final', type=Path)
    parser.add_argument('--python-only', action='store_true')
    parser.add_argument('--require-shared-doc', action='store_true')
    args = parser.parse_args()
    try:
        result = verify(args.packet.resolve(strict=True), args.python_only, args.require_shared_doc or not args.python_only)
        print(json.dumps(result))
        return 0
    except Exception as error:
        code = str(error)
        print(code if isinstance(error, RuntimeError) and re.fullmatch('A26_[A-Z_]+', code)
              else 'A26_VERIFICATION_FAILED', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
