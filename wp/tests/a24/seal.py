"""Seal a verified scratch matrix into the single parent-readable A24 packet."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('a24_seal_verifier', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def reception_controls(candidate, mirror):
    seal = v.load(candidate / 'packet.json')
    for key in set(seal['owned_sources']) | set(seal['dependency_sources']) | set(seal['delivery_sources']):
        target = mirror / key
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / key, target)
    checks = []

    def record(name, ok):
        checks.append({'check': name, 'status': 'PASS' if ok else 'FAIL'})

    record('full_verifier_before_future_pret', v.verify(mirror, candidate, require_controls=False)['exit_code'] == 0)
    marker = mirror / 'production/A-24/PRET'
    marker.write_bytes(b'FUTURE_PARENT_READINESS\n')
    record('full_verifier_after_future_pret', v.verify(mirror, candidate, require_controls=False)['exit_code'] == 0)
    for name, file in [('owned_source_mutation_refused', mirror / 'wp/outils/bascule/a24/Analysis.php'),
                       ('dependency_mutation_refused', mirror / 'wp/outils/bascule/stream_guard.py'),
                       ('report_payload_mutation_refused', candidate / 'utf8/classic-addresses/expedition.json')]:
        original = file.read_bytes()
        try:
            file.write_bytes(original + b'RECEPTION_MUTATION\n')
            record(name, v.verify(mirror, candidate, require_controls=False)['exit_code'] == 1)
        finally:
            file.write_bytes(original)
    record('all_mutations_restored_green', v.verify(mirror, candidate, require_controls=False)['exit_code'] == 0)
    receipt = {'suite': 'A24-real-reception-controls', 'checks': checks,
               'exit_code': int(any(c['status'] != 'PASS' for c in checks))}
    if receipt['exit_code']:
        raise RuntimeError('A24_SEAL_REFUSED')
    (candidate / 'utf8/reception-controls.json').write_bytes((json.dumps(receipt, indent=2) + '\n').encode('utf-8'))
    seal['evidence_sha256'] = {p.relative_to(candidate).as_posix(): v.sha(p)
                               for p in sorted(candidate.rglob('*')) if p.is_file() and p != candidate / 'packet.json'}
    (candidate / 'packet.json').write_bytes((json.dumps(seal, indent=2) + '\n').encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    target = ROOT / 'production/A-24/preuves/final'
    if (source.is_relative_to(ROOT) or not source.is_dir() or source.is_symlink()
            or target.exists() or target.is_symlink()
            or any(p.is_symlink() for p in source.rglob('*'))):
        raise RuntimeError('A24_SEAL_REFUSED')
    if {p.name for p in source.iterdir()} != {'utf8', 'cp1252', 'matrix.json'}:
        raise RuntimeError('A24_SEAL_REFUSED')
    with tempfile.TemporaryDirectory(prefix='a24-sealing-', dir=os.environ.get('TMPDIR')) as temporary:
        candidate = Path(temporary) / 'packet'
        shutil.copytree(source, candidate)
        seal = {'schema': 'imagine-a24-proof-v1', 'owned_sources': v.inventory(ROOT, v.OWN),
                'dependency_sources': v.inventory(ROOT, v.DEPS), 'delivery_sources': v.inventory(ROOT, v.DELIVERY),
                'evidence_sha256': {p.relative_to(candidate).as_posix(): v.sha(p)
                                    for p in sorted(candidate.rglob('*')) if p.is_file()}}
        (candidate / 'packet.json').write_bytes((json.dumps(seal, indent=2) + '\n').encode('utf-8'))
        result = v.verify(ROOT, candidate, require_controls=False)
        if result['exit_code']:
            # The detailed offline verifier can be run against the source after
            # creating its own seal; never publish a partially qualified packet.
            print(json.dumps(result, ensure_ascii=True), file=sys.stderr)
            raise RuntimeError('A24_SEAL_REFUSED')
        reception_controls(candidate, Path(temporary) / 'mirror')
        if v.verify(ROOT, candidate)['exit_code']:
            raise RuntimeError('A24_SEAL_REFUSED')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(candidate, target)
    if v.verify(ROOT, target)['exit_code']:
        raise RuntimeError('A24_SEAL_REFUSED')
    print('A24_PACKET_OK production/A-24/preuves/final')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        print('A24_SEAL_REFUSED', file=sys.stderr)
        sys.exit(1)
