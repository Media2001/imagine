"""Stage a fully verified A32 matrix, or attach real green gates and seal. No PRET."""
import argparse
import datetime
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
from delivery import ROOT, OWN, EXCLUDED, gates_valid, inventory, local_valid, read

BASE = ROOT / 'production/A-32'
TARGET = BASE / 'preuves/final'


def outside(path):
    path = path.resolve()
    if path.is_relative_to(ROOT) or ROOT.is_relative_to(path) or path.is_symlink() or not path.is_dir():
        raise ValueError('scratch')
    if any(p.is_symlink() for p in path.rglob('*')):
        raise ValueError('link')
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', type=Path)
    ap.add_argument('--gates', type=Path)
    ap.add_argument('--archive-existing', type=Path)
    a = ap.parse_args()
    if not a.evidence and not a.gates:
        ap.error('--evidence or --gates required')
    evidence = outside(a.evidence) if a.evidence else TARGET
    if not local_valid(evidence):
        raise ValueError('A32_PARTIAL_EVIDENCE')
    gates = outside(a.gates) if a.gates else None
    if gates and not gates_valid(gates):
        raise ValueError('A32_GATES_MISSING')
    if (BASE / 'PRET').exists():
        raise ValueError('A32_PRET_EXISTS')
    if a.evidence:
        if TARGET.exists() or (BASE / 'manifest.json').exists():
            if not a.archive_existing:
                raise ValueError('A32_EXISTING_PACKET_REFUSED')
            archive = a.archive_existing.resolve()
            if archive.exists() or archive.is_relative_to(ROOT) or ROOT.is_relative_to(archive):
                raise ValueError('A32_ARCHIVE_UNSAFE')
            archive.mkdir(parents=True)
            if TARGET.exists():
                shutil.move(str(TARGET), str(archive / 'final'))
            if (BASE / 'manifest.json').exists():
                shutil.move(str(BASE / 'manifest.json'), str(archive / 'manifest.json'))
        shutil.copytree(evidence, TARGET)
    if gates:
        if (TARGET / 'gates').exists():
            raise ValueError('A32_EXISTING_GATES_REFUSED')
        shutil.copytree(gates, TARGET / 'gates')
    complete = (TARGET / 'gates').is_dir() and gates_valid(TARGET / 'gates')
    seal = {'lot': 'A-32', 'packet': 'production/A-32/preuves/final', 'complete': complete,
            'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'files': inventory(OWN, EXCLUDED)}
    (BASE / 'manifest.json').write_text(json.dumps(seal, indent=2) + '\n', encoding='utf-8')
    result = {'exit_code': 0, 'local_matrix_verified': True, 'canonical_gates_verified': complete,
              'readiness_claimed': False, 'code': 'A32_SEALED' if complete else 'A32_LOCAL_STAGED_GATES_PENDING'}
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        known = {'A32_PARTIAL_EVIDENCE', 'A32_GATES_MISSING', 'A32_PRET_EXISTS', 'A32_EXISTING_PACKET_REFUSED', 'A32_ARCHIVE_UNSAFE', 'A32_EXISTING_GATES_REFUSED'}
        code = str(error) if str(error) in known else 'A32_PACKET_INVALID'
        print(json.dumps({'exit_code': 1, 'code': code, 'readiness_claimed': False}))
        sys.exit(1)
