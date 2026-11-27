"""B10 corrigé : reçu successeur, vérifications autonomes/offline et live avant PRET."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
import b10

ROOT, OUT = b10.ROOT, b10.OUT
refs = {
    'unit': 'corrections-unitaires-normal.log',
    'fallback': 'corrections-unitaires-fallback.log',
    'native': 'corrections-natif-V2.json',
    'recipe': 'corrections-recette-finale-V2.json',
    'cleanup': 'corrections-recette-finale-V2-nettoyage.json',
    'image': 'corrections-preparation-V2.log',
    'regression': 'corrections-regression-V2.log',
}
assert not (OUT/'PRET').exists()
assert not (OUT/'corrections-reception-V2.json').exists()
unit = (OUT/refs['unit']).read_text(encoding='utf-8')
u = re.search(r'OK \((\d+) tests, (\d+) assertions\)', unit)
assert u
native = json.loads(json.loads((OUT/refs['native']).read_text(encoding='utf-8'))['stdout'])
recipe = json.loads((OUT/refs['recipe']).read_text(encoding='utf-8'))
text = (OUT/refs['regression']).read_text(encoding='utf-8-sig')
global_result = json.loads(re.search(r'^T01_RESULT (.+)$', text, re.M)[1])
paths = []
for pattern in ['wp/plugins/imagine-site/PointsVente*.php', 'wp/plugins/imagine-site/tests/PointsVente*.php', 'wp/outils/demo/b10*.py', 'wp/outils/demo/b10*.php', 'wp/tests/demo/b10*.py', 'wp/tests/demo/b10*.php']:
    paths.extend(p for p in ROOT.glob(pattern) if p.is_file())
for name in ['NOTE.md', 'A-VOIR.md', 'mapping-exemple.json', 'commerces-fictifs.csv', 'page-navigation.json', 'page-mobile.png', 'corrections-installation-V2.json', *refs.values()]:
    paths.append(OUT/name)
paths.extend(OUT.glob('corrections-rouge-*.log'))
paths.extend(OUT.glob('corrections-vert-*.log'))
readme = (ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
section = '## B-10 — points de vente' + readme.split('## B-10 — points de vente', 1)[1].split('\n## ', 1)[0]
payload = {
    'scope': 'imagine-test-demo', 'at': datetime.now(timezone.utc).isoformat(),
    'supersedes': 'reception.json', 'python': sys.version,
    'bootstrap_block': b10.BLOCK, 'readme_section': section,
    'proofs': refs,
    'counts': {'unit_tests': int(u[1]), 'unit_assertions': int(u[2]), 'native': len(native['checks']), 'browser': len(recipe['checks'])},
    'global_result': global_result,
    'sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))},
}
with (OUT/'corrections-reception-V2.json').open('x', encoding='utf-8') as stream:
    json.dump(payload, stream, ensure_ascii=False, indent=2)
logs = []
for flags in [[], ['--live']]:
    result = subprocess.run([sys.executable, '-B', str(ROOT/'wp/tests/demo/b10-verifier.py'), *flags], cwd=ROOT, capture_output=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    logs.append(result.stdout+result.stderr)
    print(logs[-1])
    assert result.returncode == 0, 'Contrôle refusé ; aucun PRET déposé'
with (OUT/'corrections-verification-finale-V2.log').open('x', encoding='utf-8') as stream:
    stream.write('\n'.join(logs))
with (OUT/'PRET').open('x', encoding='utf-8') as stream:
    stream.write('B-10 corrigé, prêt à relire. 14 tests / 80 assertions ; 13 contrôles natifs ; 31 contrôles navigateur. Image reconstruite ; régression fraîche 1187 tests / 36494 assertions, 584 contrôles outils. Reçu corrections-reception-V2.json ; vérifications offline et live PASS, 30 commerces fictifs, carte OFF, reprise vide. B11 inchangé. A32 rouge hors périmètre. Validation visuelle de Ced attendue ; aucun GO réel.\n')
print('B10 CORRECTIONS PRET :', len(payload['sha256']), 'empreintes ; offline et live PASS')
