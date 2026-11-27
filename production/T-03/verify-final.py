"""Read-only T03 final-state checks; no Docker, writes or PRET mutation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LOTS = ['A-20', 'A-21', 'A-22', 'A-23', 'A-24', 'A-25', 'A-26', 'A-27', 'A-28', 'A-30', 'A-31', 'A-32']
PRET_BYTES = b'T-03 PRET - corrections et gates finales verifiees; aucun GO reel.\n'


def verify_replay(data, failures):
    lines = data.decode('utf-8-sig').splitlines()
    markers = [line[11:] for line in lines if line.startswith('T01_RESULT ')]
    if len(markers) != 1:
        raise ValueError('REPLAY_MARKER')
    marker = json.loads(markers[0])
    packets = marker['packets']
    tools = marker['tools']
    if (marker['pass'] is not True or marker['tests'] < 1 or marker['assertions'] < 1
            or any(marker[key] != 0 for key in ('failures', 'errors', 'skipped'))
            or tools['tools'] < 1 or tools['checks'] < 1 or tools['failures'] != 0 or tools['excluded']
            or packets['verified'] != len(LOTS) or packets['lots'] != LOTS
            or packets['failures'] != failures or packets['excluded']):
        raise ValueError('REPLAY_GATE')
    expected = f"REJEU : {marker['tests']} tests, {marker['assertions']} assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS"
    packet_line = f"PAQUETS : {len(LOTS)} vérifiés, {len(failures)} échecs ; hors rejeu : aucun"
    packet_line += ''.join(' ; ' + row['lot'] + ' ' + row['control'] for row in failures)
    tools_line = f"OUTILS : {tools['tools']} outils, {tools['checks']} contrôles, 0 échecs ; hors rejeu : aucun"
    if (not lines or lines[-1] != expected
            or [line for line in lines if line.startswith('PAQUETS : ')] != [packet_line]
            or [line for line in lines if line.startswith('OUTILS : ')] != [tools_line]
            or sum(bool(re.fullmatch(r'T01 CLEANUP : absence verifiee de imagine-t01-[a-f0-9]{32}', line)) for line in lines) != 1
            or any('NETTOYAGE EN ECHEC' in line for line in lines)):
        raise ValueError('REPLAY_SUMMARY_OR_CLEANUP')
    return {'marker': marker, 'last': expected, 'packets': packet_line, 'tools': tools_line}


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_gates():
    proof = BASE / 'preuves/final'
    native = json.loads((proof / 'native/result.json').read_text(encoding='utf-8-sig'))
    if (native['status'] != 'PASS' or native['native_executed'] is not True
            or native['copy_absent'] is not True or native['original_receipt_unchanged'] is not True
            or len(native['checks']) != 4 or any(row['status'] != 'PASS' for row in native['checks'])
            or [(row['name'], row['exit_code']) for row in native['commands']] != [('green', 0), ('one-byte', 0)]):
        raise ValueError('NATIVE_PROOF')
    green = verify_replay((proof / 'native/green.log').read_bytes(), [])
    red = verify_replay((proof / 'native/one-byte.log').read_bytes(), [{'lot': 'A-28', 'control': 'PACKAGE_DRIFT'}])
    if (green['last'] != red['last'] or native['green']['last'] != green['last']
            or native['mutant']['last'] != red['last'] or native['green']['packets'] != green['marker']['packets']
            or native['mutant']['packets'] != red['marker']['packets']):
        raise ValueError('NATIVE_PROOF_BINDING')
    nominal = verify_replay((proof / 'qualification/nominal-observed.log').read_bytes(), [])
    if nominal['marker'] != green['marker']:
        raise ValueError('NOMINAL_NATIVE_DIVERGENCE')
    for name, directories, extra in [
            ('protected-before.json', ['wp/tests/t01', 'wp/outils/staging', 'wp/outils/staging-court'], ['wp/tests/rejouer.ps1']),
            ('neighbours-before.json', ['production/A-31', 'production/A-32'], [])]:
        expected = json.loads((proof / 'cloture' / name).read_text(encoding='utf-8'))
        files = {p.relative_to(ROOT).as_posix(): digest(p) for directory in directories for p in (ROOT / directory).rglob('*') if p.is_file()}
        files.update({path: digest(ROOT / path) for path in extra})
        if files != expected:
            raise ValueError('PROTECTED_MEMBERSHIP_OR_BYTES')
    closure = json.loads((proof / 'cloture/closure-checks.json').read_text(encoding='utf-8'))
    helper = load('t03_qualification_final', 'qualifier-corrections.py')
    bindings = json.loads((proof / 'native/source-binding.json').read_text(encoding='utf-8'))
    if bindings['source_sha256'] != helper.source_hashes() or bindings['exit_code'] != 0:
        raise ValueError('NATIVE_SOURCE_STALE')
    if closure['status'] != 'PASS' or closure['source_sha256'] != helper.source_hashes():
        raise ValueError('CLOSURE_STALE')
    expected_commands = ['utf8-test-cloture', 'utf8-test-finalisation', 'cp1252-test-cloture', 'cp1252-test-finalisation', 'powershell-parse', 'prepare-image']
    if [row['name'] for row in closure['commands']] != expected_commands:
        raise ValueError('CLOSURE_COMMANDS')
    for row in closure['commands']:
        if row['exit_code'] != 0 or row['tmpdir_present'] is not False:
            raise ValueError('CLOSURE_FAILED')
        for stream, suffix in [('stdout', '.log'), ('stderr', '.stderr.log')]:
            if digest(proof / 'cloture' / (row['name'] + suffix)) != row[stream + '_sha256']:
                raise ValueError('CLOSURE_LOG_DRIFT')
    return nominal


def verify(require_pret=True):
    manifest = json.loads((BASE / 'manifest.json').read_text(encoding='utf-8'))
    if (manifest['lot'] != 'T-03' or manifest['status'] != 'PRET'
            or manifest['readiness_claimed'] is not True or manifest['parent_final_gates_pending'] is not False
            or manifest['pret_sha256'] != hashlib.sha256(PRET_BYTES).hexdigest()):
        raise ValueError('FINAL_STATE_CONTRACT')
    marker = BASE / 'PRET'
    if require_pret and (not marker.is_file() or marker.read_bytes() != PRET_BYTES):
        raise ValueError('PRET_MISSING_OR_DRIFT')
    if not require_pret and marker.exists():
        raise ValueError('BEFORE_PRET_ONLY')
    candidate = load('t03_candidate_final', 'verify-corrections.py')
    evidence = candidate.verify_evidence(manifest)
    gate = verify_gates()
    return {'lot': 'T-03', 'status': 'PASS', 'exit_code': 0, 'readiness_claimed': True,
            'parent_final_gates_pending': False, 'pret_present': marker.is_file(),
            'files': evidence['files'], 'commands': evidence['commands'],
            'packets': gate['marker']['packets'], 'tests': gate['marker']['tests'],
            'assertions': gate['marker']['assertions'], 'tools': gate['marker']['tools']}


if __name__ == '__main__':
    try:
        if len(sys.argv) != 1:
            raise ValueError('NO_ARGUMENTS')
        result = verify()
    except Exception as error:
        result = {'lot': 'T-03', 'status': 'FAIL', 'exit_code': 1,
                  'code': str(error) if isinstance(error, ValueError) else 'FINAL_PACKET_INVALID'}
    print(json.dumps(result, ensure_ascii=True))
    raise SystemExit(result['exit_code'])
