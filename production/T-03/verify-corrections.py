"""Read-only T03 correction verifier: BEFORE PRET ONLY, never a global/final gate.

A successful read validates correction evidence, not readiness. Run before the
PRET marker; after PRET its deliberate refusal is not a final-package verdict.
Use the independent canonical replay to verify the final state after PRET.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'production/T-03'


def inventory(source_names):
    names = set(source_names)
    names.update(p.relative_to(ROOT).as_posix() for p in (BASE / 'preuves/final').rglob('*') if p.is_file())
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(names)}


def verify_console(console, context):
    if console.get('tmpdir_present') is not False:
        raise ValueError('CLEAN_WINDOWS_SESSION_NOT_MEASURED')
    if console['stdout'] != ('utf-8' if context == 'utf8' else 'cp1252') or console['utf8_mode'] != int(context == 'utf8'):
        raise ValueError('CONSOLE_CONTEXT_NOT_MEASURED')


def verify():
    if len(sys.argv) != 1:
        raise ValueError('NO_ARGUMENTS')
    manifest = json.loads((BASE / 'manifest.json').read_text(encoding='utf-8'))
    if (manifest.get('status') != 'CORRECTIONS_TESTEES_GATES_PARENT_EN_ATTENTE'
            or manifest.get('readiness_claimed') is not False
            or manifest.get('parent_final_gates_pending') is not True or (BASE / 'PRET').exists()):
        raise ValueError('CANDIDATE_NOT_PRET_CONTRACT')
    return verify_evidence(manifest)


def verify_evidence(manifest):
    """Shared read-only evidence assertions, with no readiness/status decision."""
    spec = importlib.util.spec_from_file_location('t03_candidate_qualification', BASE / 'qualifier-corrections.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    sources = helper.source_hashes()
    if inventory(sources) != manifest['files'] or len(manifest['files']) != manifest['file_count']:
        raise ValueError('PACKAGE_DRIFT')
    proof = BASE / 'preuves/final/qualification'
    result = json.loads((proof / 'result.json').read_text(encoding='utf-8'))
    if (result['status'] != 'PASS' or not result['source_unchanged'] or result['source_sha256'] != sources
            or result['expected_command_count'] != 14 or result['completed_command_count'] != 14
            or len(result['commands']) != 14 or len({row['name'] for row in result['commands']}) != 14):
        raise ValueError('QUALIFICATION_INCOMPLETE_OR_STALE')
    for command in result['commands']:
        if command['exit_code'] != 0 or not re.fullmatch(r'[a-z0-9_-]+', command['name']):
            raise ValueError('COMMAND_FAILED')
        for stream in ('stdout', 'stderr'):
            suffix = '.log' if stream == 'stdout' else '.stderr.log'
            if hashlib.sha256((proof / (command['name'] + suffix)).read_bytes()).hexdigest() != command[stream + '_sha256']:
                raise ValueError('COMMAND_LOG_DRIFT')
    for context in ('utf8', 'cp1252'):
        real = json.loads((proof / (context + '-real-fixtures/result.json')).read_text(encoding='utf-8'))
        if (real['status'] != 'PASS' or len(real['cases']) != 3
                or any(case['status'] != 'PASS' or not case['fixture_absent'] or not all(case['checks'].values()) for case in real['cases'])):
            raise ValueError('REAL_FIXTURE_FAILED')
        console = json.loads((proof / (context + '-python-context.log')).read_bytes())
        verify_console(console, context)
    native = (proof / 'streams-native.log').read_text(encoding='utf-8-sig')
    if not re.search(r'Ran 7 tests in ', native) or '\nOK' not in native or 'FAILED' in native:
        raise ValueError('NATIVE_STREAM_REGRESSIONS_MISSING')
    nominal = next(row for row in result['commands'] if row['name'] == 'nominal-observed')
    return {'lot':'T-03', 'status':'CORRECTION_TESTS_PASS_PARENT_PENDING', 'exit_code':0,
            'readiness_claimed':False, 'parent_final_gates_pending':True,
            'commands':len(result['commands']), 'files':len(manifest['files']),
            'observed_nominal_summaries':nominal['summaries']}


if __name__ == '__main__':
    try:
        result = verify()
    except Exception as error:
        result = {'lot':'T-03', 'status':'FAIL', 'exit_code':1,
                  'readiness_claimed':False, 'code':str(error) if isinstance(error, ValueError) else 'PACKET_INVALID'}
    print(json.dumps(result, ensure_ascii=True))
    raise SystemExit(result['exit_code'])
