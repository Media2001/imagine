"""A32 read-only evidence contracts, shared by sealing and replay."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OWN = ['wp/outils/bascule/tournee', 'wp/tests/a32', 'production/A-32']
EXCLUDED = {'production/A-32/manifest.json', 'production/A-32/PRET'}
GATES = ('prepare-image', 'global-utf8', 'global-cp1252', 'a20-readonly', 'a21-readonly', 'a22-readonly', 'a28-readonly')
TOOLS = ['A10', 'A11', 'A12', 'A15', 'A16', 'A17', 'A18', 'A19', 'A20', 'A21', 'A23', 'A24', 'A25', 'A26', 'A27']
CHANNELS = ('stdout', 'stderr', 'early_exit', 'silent_exit', 'shutdown_stdout', 'shutdown_stderr', 'report')
GUARD_CASES = ('absent', 'invalid', 'fields', 'production', 'environment_absent', 'define_in_string', 'define_in_comment')
CLOCK_CASES = ('current', 'later', 'year_before', 'equality', 'year_after')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('file')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate')
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(roots, excluded=()):
    result = {}
    for key in roots:
        path = ROOT / key
        if not path.exists() or path.is_symlink():
            raise ValueError('source')
        for file in [path] if path.is_file() else sorted(path.rglob('*')):
            if file.is_symlink():
                raise ValueError('link')
            if file.is_file() and '__pycache__' not in file.parts:
                name = file.relative_to(ROOT).as_posix()
                if name not in excluded:
                    result[name] = digest(file)
    return result


def sources():
    return load('a32_evidence_runner', ROOT / 'wp/tests/a32/run.py').sources()


def local_valid(folder):
    matrix = read(folder / 'windows-matrix.json')
    if (matrix.get('scope') != 'python_and_native' or matrix.get('exit_code') != 0
            or matrix.get('sources_stable') is not True or read(folder / 'sources.json') != sources()):
        return False
    rows = matrix['rows']
    if [(r['encoding'], r['kind']) for r in rows] != [('utf-8', 'python'), ('utf-8', 'native'), ('cp1252', 'python'), ('cp1252', 'native')]:
        return False
    for row in rows:
        path = folder / row['log']
        if (row['exit_code'] != 0 or row['tmpdir_present'] is not False or row['temp_is_scratch'] is not True
                or not path.resolve().is_relative_to(folder.resolve()) or path.is_symlink() or digest(path) != row['sha256']
                or row['probe']['platform'] != 'win32' or row['probe']['encoding'] != row['encoding']
                or row['probe']['tmpdir_present'] is not False):
            return False
        if row['kind'] == 'python':
            text = path.read_text(encoding='utf-8')
            matches = re.findall(r'^Ran (\d+) tests? in ', text, re.M)
            if row.get('all_pass') is not True or len(matches) != 1 or int(matches[0]) != row['tests_run'] or row['tests_run'] < 1 or 'OK' not in text.splitlines():
                return False
    for console in ('utf8', 'cp1252'):
        native = folder / console / 'native'
        result, runner = read(native / 'result.json'), read(native / 'runner.json')
        if (read(native / 'sources.json') != sources() or any(d.get('exit_code') != 0 or not d['checks']
                or any(c['status'] != 'PASS' for c in d['checks']) for d in (result, runner))):
            return False
        checks = [c['check'] for c in result['checks']]
        if len(checks) != len(set(checks)):
            return False
        for storage in ('classic', 'hpos'):
            wanted = {storage + ':' + k for k in ('documented_command_exact_complete', 'named_doubles_continue_every_remaining_real_tool',
                      'whole_nominal_db_files_immutable', 'whole_tour_all_tables_scheduler_files_immutable', 'config_never_executed')}
            wanted |= {storage + ':whole_tour_channel:' + c for c in CHANNELS}
            wanted |= {storage + ':tour_guard_zero_tools:' + c for c in GUARD_CASES}
            wanted |= {storage + ':a19_clock:' + c for c in CLOCK_CASES}
            wanted |= {storage + ':' + c for c in ('supervision_codes_preserved', 'a16_omitted_limit_still_default_ten', 'a19_later_replay_advances_utc', 'a19_equality_and_year_change')}
            if not wanted.issubset(checks):
                return False
            doc = read(native / (storage + '-complete/bilan.json'))
            if doc['tournee'] != 'complète' or [r['outil'] for r in doc['outils']] != TOOLS or any(r['statut'] != 'réussi' for r in doc['outils']):
                return False
            doubles = read(native / (storage + '-doubles.json'))
            mixed = read(native / (storage + '-named-doubles/bilan.json'))
            if (doubles['declared_doubles'] != {'A10': 'refusal', 'A11': 'exit255'} or len(doubles['commands']) != len(TOOLS)
                    or mixed['tournee'] != 'partielle' or [r['statut'] for r in mixed['outils']] != ['refusé', 'en échec'] + ['réussi'] * 13):
                return False
            for label in GUARD_CASES:
                proof = read(native / (storage + '-unverified-' + label + '-proof.json'))
                if (proof.get('measurement') != 'real_default_executor_python_audit_subprocess.Popen'
                        or proof['exit_code'] != 1 or proof['stdout_empty'] is not True or proof['stderr'] != 'A32_NOT_VERIFIED\n'
                        or proof['commands'] != [] or proof['tools_launched'] != 0 or proof['output_absent'] is not True
                        or proof['database_before'] != proof['database_after'] or proof['files_before'] != proof['files_after']):
                    return False
            supervision = read(native / (storage + '-supervision.json'))
            expected = {'A15': 'A15_PROCESS_TIMEOUT', 'A19': 'A19_SUCCESS_INCOMPLETE'}
            supervised = read(native / (storage + '-supervision-doubles/bilan.json'))
            if (supervision['emitted_codes'] != expected or supervision['exit_code'] != 1
                    or set(supervision['declared_doubles']) != set(expected) or len(supervision['commands']) != len(TOOLS)
                    or supervised['tournee'] != 'partielle' or [r['outil'] for r in supervised['outils']] != TOOLS
                    or any((r['statut'] != 'refusé' or r.get('code') != expected[r['outil']]) if r['outil'] in expected
                           else r['statut'] != 'réussi' for r in supervised['outils'])):
                return False
            timing = read(native / (storage + '-clock.json'))
            clock_rows = timing['rows']
            if tuple(r['case'] for r in clock_rows) != CLOCK_CASES:
                return False
            import datetime
            for clock in clock_rows:
                stamp = int(datetime.datetime.fromisoformat(clock['as_of_utc'].replace('Z', '+00:00')).timestamp())
                expected_count = sum(0 < value < stamp for value in timing['oracle']['active_next_native'])
                if clock['exit_code'] != 0 or clock['expected_count'] != expected_count or clock['actual_count'] != expected_count:
                    return False
                if clock['case'] in ('current', 'later') and (not clock['start_utc'] <= stamp <= clock['end_utc']
                        or any(arg.startswith('--as-of=') for arg in clock['command'])):
                    return False
            if (clock_rows[1]['as_of_utc'] <= clock_rows[0]['as_of_utc']
                    or clock_rows[3]['actual_count'] != clock_rows[2]['actual_count'] + 1
                    or clock_rows[4]['actual_count'] != clock_rows[3]['actual_count'] + 1):
                return False
            if read(native / (storage + '-complete-a16/numeros.json')).get('limit') != 10:
                return False
            channels = read(native / (storage + '-channels.json'))
            if {r['channel'] for r in channels} != set(CHANNELS) or any(not r['clean'] or not r['immutable'] or r['exit_code'] != 1 for r in channels):
                return False
    return True


def gates_valid(folder):
    result, rows = read(folder / 'result.json'), read(folder / 'commands.json')
    if (result.get('exit_code') != 0 or result.get('sources_stable') is not True
            or tuple(r['name'] for r in rows) != GATES
            or read(folder / 'source-roots.json') != read(ROOT / 'production/A-32/source-roots.json')['gates']
            or read(folder / 'sources.json') != inventory(read(folder / 'source-roots.json'))):
        return False
    for row in rows:
        if row.get('exit_code') != 0 or row.get('sources_stable') is not True or row.get('tmpdir_present') is not False:
            return False
        for field in ('stdout', 'stderr'):
            path = folder / row[field]
            if not path.resolve().is_relative_to(folder.resolve()) or path.is_symlink() or digest(path) != row[field + '_sha256']:
                return False
        if (folder / row['stderr']).read_bytes():
            return False
        text = (folder / row['stdout']).read_text(encoding='utf-8')
        if row['name'].startswith('global-'):
            matches = re.findall(r'^T01_RESULT (.+)$', text, re.M)
            if len(matches) != 1:
                return False
            data = json.loads(matches[0])
            if (data.get('pass') is not True or data['failures'] != 0 or data['errors'] != 0 or data['skipped'] != 0
                    or data['tools']['failures'] != 0 or data['packets']['failures'] != []
                    or not {'A-22', 'A-28'}.issubset(data['packets']['lots'])):
                return False
        elif row['name'].endswith('-readonly'):
            data = json.loads(text)
            if data.get('exit_code', data.get('exit')) != 0:
                return False
        elif 'T03 IMAGE PYTHON : offline standard-library probe PASS' not in text:
            return False
    return True
