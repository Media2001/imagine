"""A33 package creation/reseal through semantic controls, never hand-edited hashes."""
import argparse
import datetime
import json
from pathlib import Path
import shutil
import sys
sys.dont_write_bytecode = True
from delivery import BASE, EXCLUDE, OWN, ROOT, gates_recorded, gates_valid, inventory, local_valid, verify

VERIFIER = '''"""A33 read-only packet verifier; no arguments, no writes or subprocess."""
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[2]
try:
    if len(sys.argv) != 1:
        raise ValueError('A33_ARGUMENTS_REFUSED')
    spec = importlib.util.spec_from_file_location('a33packet', root / 'wp/tests/a33/delivery.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    code = module.verify(root)
except Exception as error:
    code = str(error) if str(error) == 'A33_ARGUMENTS_REFUSED' else 'A33_PACKET_INVALID'
result = {'lot': 'A-33', 'exit_code': int(code is not None), 'checks': [{'check': code or 'A33_PACKAGE_PASS', 'status': 'FAIL' if code else 'PASS'}]}
print(json.dumps(result, ensure_ascii=True))
sys.exit(result['exit_code'])
'''
CONTROLS = ['A33_ARGUMENTS_REFUSED', 'A33_PACKET_INVALID', 'A33_PACKAGE_DRIFT', 'A33_README_CONTRACT_DRIFT', 'A33_PARTIAL_EVIDENCE', 'A33_GATES_INVALID', 'A33_PACKAGE_PASS']
LOGS = [BASE + '/preuves/final/' + f for f in ['utf8/python-tests.log', 'utf8/runner-console.log', 'utf8/native/native.log', 'cp1252/python-tests.log', 'cp1252/runner-console.log', 'cp1252/native/native.log', 'style-console.log', 'gates/prepare-image.stdout.log', 'gates/global-utf8.stdout.log', 'gates/global-cp1252.stdout.log']]


def outside(path):
    p = path.resolve()
    if p.is_relative_to(ROOT) or ROOT.is_relative_to(p) or not p.is_dir() or any(f.is_symlink() for f in p.rglob('*')):
        raise ValueError('A33_SCRATCH_REQUIRED')
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path)
    ap.add_argument('--gates', type=Path)
    ap.add_argument('--archive-gates', type=Path)
    ap.add_argument('--ready', action='store_true')
    ap.add_argument('--blocked', action='store_true', help='Preserve a real failed gate packet; verifier stays red, never PRET')
    a = ap.parse_args()
    base = ROOT / BASE
    packet = base / 'preuves/final'
    if a.blocked and (a.ready or not a.evidence or not a.gates):
        raise ValueError('A33_BLOCKED_SCOPE_INVALID')
    if (base / 'PRET').exists():
        raise ValueError('A33_PRET_EXISTS')
    if a.evidence:
        evidence = outside(a.evidence)
        if not local_valid(evidence) or packet.exists() or a.gates is None:
            raise ValueError('A33_PARTIAL_EVIDENCE')
        gates = outside(a.gates)
        if not gates_recorded(gates) or (not a.blocked and not gates_valid(gates)):
            raise ValueError('A33_GATES_INVALID')
        shutil.copytree(evidence, packet)
        shutil.copytree(gates, packet / 'gates')
        verifier = base / 'verify.py'
        if verifier.exists():
            raise ValueError('A33_VERIFIER_EXISTS')
        verifier.write_text(VERIFIER, encoding='utf-8', newline='\n')
        (base / 'rejeu.json').write_text(json.dumps({'schema': 1, 'entrypoint': 'verify.py', 'requires': [], 'logs': LOGS, 'controls': CONTROLS}, indent=2) + '\n', encoding='utf-8')
    elif a.gates:
        gates = outside(a.gates)
        if not gates_valid(gates, True) or not local_valid(packet) or a.archive_gates is None:
            raise ValueError('A33_GATES_INVALID')
        archive = a.archive_gates.resolve()
        if archive.exists() or archive.is_relative_to(ROOT) or ROOT.is_relative_to(archive):
            raise ValueError('A33_ARCHIVE_UNSAFE')
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(packet / 'gates'), str(archive))
        shutil.copytree(gates, packet / 'gates')
    if a.ready and not gates_valid(packet / 'gates', True):
        raise ValueError('A33_GATES_INVALID')
    if not local_valid(packet) or not gates_recorded(packet / 'gates') or (not a.blocked and not gates_valid(packet / 'gates')):
        raise ValueError('A33_PARTIAL_EVIDENCE')
    (base / 'manifest.json').write_text(json.dumps({'lot': 'A-33', 'files': inventory(OWN, ROOT, EXCLUDE)}, indent=2) + '\n', encoding='utf-8')
    code = verify()
    if a.blocked:
        if code != 'A33_GATES_INVALID' or gates_valid(packet / 'gates'):
            raise ValueError('A33_BLOCKED_VERDICT_INVALID')
        print(json.dumps({'exit_code': 1, 'sealed': True, 'ready': False, 'local_matrix_verified': True, 'code': code}))
        return 1
    if code is not None:
        raise ValueError(code)
    if a.ready:
        (base / 'PRET').write_text('A-33 ' + datetime.datetime.now(datetime.timezone.utc).isoformat() + '\n', encoding='utf-8')
        if verify() is not None:
            (base / 'PRET').unlink()
            raise ValueError('A33_READINESS_FAILED')
    print(json.dumps({'exit_code': 0, 'sealed': True, 'ready': a.ready, 'files': len(inventory(OWN, ROOT, EXCLUDE))}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
