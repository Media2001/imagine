"""Bounded parent integration: preserve historical packets before resealing."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil

REPO = Path(__file__).resolve().parents[2]
SCRATCH = Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a10-a13-reception')

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def inventory(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob('*')) if p.is_file()}

def main():
    SCRATCH.mkdir(parents=True, exist_ok=False)
    for lot in ['A-10', 'A-11', 'A-12', 'A-13']:
        source = REPO/'production'/lot
        target = SCRATCH/'historical'/lot
        shutil.copytree(source, target)
        assert inventory(source) == inventory(target)
    roots = ['wp/tests/a02-audit', 'wp/outils/bascule/audit', 'wp/outils/bascule/a09', 'wp/outils/bascule/a10', 'wp/outils/bascule/a11', 'wp/outils/bascule/a12', 'wp/outils/bascule/a13', 'wp/tests/a13', 'wp/outils/bascule/controler-export', 'wp/outils/bascule/controler-export.md', 'wp/tests/preparer-image.ps1', '.hermes.lock', '.hermes-2.lock']
    protected = {}
    for key in roots:
        root = REPO/key
        for p in ([root] if root.is_file() else root.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                protected[p.relative_to(REPO).as_posix()] = digest(p)
    (SCRATCH/'protected-before.json').write_text(json.dumps(protected, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'scratch': str(SCRATCH), 'historical_packages': 4, 'protected_files': len(protected), 'at': datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2))

if __name__ == '__main__':
    main()
