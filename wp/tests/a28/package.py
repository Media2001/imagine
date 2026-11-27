"""Assemble only A28; never qualify or reseal another lot."""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/A-28'
PACKET = BASE / 'preuves/final'
SCRATCH = Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a28-correction-20261127-0258')
spec = importlib.util.spec_from_file_location('a28_package_verifier', BASE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
OWN_CHANGED = {'wp/outils/staging/lib.php', 'wp/outils/staging-court/inside.py',
               'wp/outils/staging-court/run.py', 'wp/outils/staging/store.php',
               'wp/outils/staging/form-decision-refused.php', 'wp/outils/staging/engine.php',
               'wp/outils/staging/guard.php'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding='utf-8')


def setup():
    old = SCRATCH / 'old-production'
    assert old.is_dir() and (old / 'preuves/final').is_dir()
    if (BASE / 'preuves').exists():
        shutil.rmtree(BASE / 'preuves')
    (BASE / 'manifest.json').unlink(missing_ok=True)
    PACKET.mkdir(parents=True, exist_ok=False)
    shutil.copytree(old / 'preuves/final/before', PACKET / 'before')
    reds = []
    for name in ('red-i1', 'red-absent'):
        path = SCRATCH / name
        row = v.load(path / 'runner.json')
        assert row['status'] == 'FAIL' and row['commands'][0]['exit'] == 1 and row['cleanup']['absent'] is True
        reds.append({'handle': str(path / 'runner.json'), 'sha256': digest(path / 'runner.json'),
            'unit_handle': str(path / 'unit.json'), 'unit_sha256': digest(path / 'unit.json'),
            'exit': 1, 'cleanup': row['cleanup']})
    write(PACKET / 'red-green.json', {'historical_outside_repository': str(old), 'red_receipts': reds,
        'green_receipts': ['native/utf8/native.json', 'native/cp1252/native.json'],
        'mutation': 'omit_only_postmeta_purge; known parents/revisions gone; refusal/removal/restoration'})
    review()


def review():
    imports = {p.relative_to(ROOT).as_posix(): digest(p)
        for folder in ('wp/outils/staging', 'wp/outils/staging-court')
        for p in (ROOT / folder).rglob('*') if p.is_file() and p.suffix in ('.php', '.py', '.json')
        and '__pycache__' not in p.parts}
    write(PACKET / 'dependency-invalidations.json', {'import_sources': imports,
        'invalidated_lots': ['A-' + str(n) for n in range(21, 28)],
        'A29': 'parent-owned; import dependency changed; no execution or qualification by A28',
        'decision': 'Import frozen after A28. Parent owns all other native replays and reseals.',
        'frozen_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()})


def scope():
    changed = []
    for folder, saved in [('wp/outils/staging', 'old-staging'), ('wp/outils/staging-court', 'old-court')]:
        previous = {p.relative_to(SCRATCH / saved).as_posix(): digest(p)
            for p in (SCRATCH / saved).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'
            and not (folder == 'wp/outils/staging-court' and p.name == 'README.md')}
        current = {p.relative_to(ROOT / folder).as_posix(): digest(p)
            for p in (ROOT / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'
            and not (folder == 'wp/outils/staging-court' and p.name == 'README.md')}
        changed += [folder + '/' + rel for rel in sorted(set(previous) | set(current)) if previous.get(rel) != current.get(rel)]
    contract = v.load(BASE / 'readme-contract.json')
    v.readme_contract((ROOT / 'wp/outils/staging-court/README.md').read_bytes(), contract['lines'], contract['commands'])
    assert set(changed) == OWN_CHANGED
    write(PACKET / 'scope.json', {'correction_scope': True, 'owned_import_changes': sorted(changed),
        'allowed_import_changes': sorted(OWN_CHANGED), 'readme_owned_lines_and_commands': True,
        'other_lots_executed_or_resealed': False,
        'concurrent_roots_not_pinned': ['voie2', 'A26', 'A27', 'T03', 'A30'],
        'historical_packet': str(SCRATCH / 'old-production'),
        'measured_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()})


def seal():
    assert not (BASE / 'manifest.json').exists(), 'A28_ALREADY_SEALED'
    v.runner_contract(PACKET / 'before', ROOT, baseline=True)
    v.native_contract(v.load(PACKET / 'before/native.json'), baseline=True)
    v.matrix_contract(PACKET / 'native', ROOT, v.load(PACKET / 'before/runner.json')['source_manifest'])
    v.gates_contract(PACKET / 'gates', ROOT)
    invalid = v.load(PACKET / 'dependency-invalidations.json')
    assert all(digest(ROOT / rel) == old for rel, old in invalid['import_sources'].items())
    scope()
    write(BASE / 'manifest.json', {'lot': 'A-28', 'packet': v.PACKET.as_posix(), 'files': v.inventory(ROOT)})
    print(json.dumps(v.verify()))


def main():
    parser = argparse.ArgumentParser()
    phase = parser.add_mutually_exclusive_group(required=True)
    phase.add_argument('--setup', action='store_true')
    phase.add_argument('--seal', action='store_true')
    phase.add_argument('--review', action='store_true')
    args = parser.parse_args()
    if args.setup:
        setup()
    elif args.review:
        review()
    else:
        seal()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
