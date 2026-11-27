"""Scelle uniquement C29 ; historiques intacts et socle inchangé."""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'production/C-29'
sys.path.insert(0, str(ROOT/'wp/tests/demo'))
import lot_reception_contract as contract
spec = importlib.util.spec_from_file_location('c29_verify', OUT/'verifier.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
if __name__ == '__main__':
    names = ['pure-corrections-final-V2.json', 'green-corrections-groupe-V2.json',
        'http-corrections-chaud-V2.json', 'http-corrections-chaud-V2.png', 'http-corrections-chaud-V2-baseline.json',
        'red-corrections-refus-V2.json', 'red-corrections-groupe-V2.json', 'red-corrections-groupe-cache-V2.json',
        'http-corrections-V2.json', 'image-corrections-V2.json', 'image-corrections-V2.log',
        'replay-corrections-V2.json', 'replay-corrections-V2.log', 'code-corrections-demo-V2.json',
        'paquets-etrangers-V2.json', 'A-VOIR.md', 'NOTE-corrections-V2.md', 'sceller-corrections-V2.py']
    historical = ['reception-contrat-V2.json', 'reception-V2.json', 'PRET-avant-corrections-V2', 'verifier-contrat-avant-corrections-V2.py']
    m = {'scope': 'imagine-test-demo', 'ready': True, 'contract_version': 1, 'at': datetime.now(timezone.utc).isoformat(),
        'sources': contract.sources('C29'), 'bootstrap_contract': contract.registration('C29'),
        'readme_section': hashlib.sha256(contract.section('C29').encode()).hexdigest(),
        'evidence': {n:digest(OUT/n) for n in names}, 'historical_files': {n:digest(OUT/n) for n in historical},
        'pure': names[0], 'native': names[1], 'http': names[2], 'image': 'image-corrections-V2.json', 'replay': 'replay-corrections-V2.json'}
    v.verify(False, m, False)
    target = OUT/'reception-corrections-V2.json'
    with target.open('x', encoding='utf-8') as stream: json.dump(m, stream, ensure_ascii=False, indent=2)
    with (OUT/'PRET').open('x', encoding='utf-8') as stream:
        stream.write('C29 PRET technique — corrections C29-01/02/03 et i18n ; reception-corrections-V2.json.\n23 contrôles purs, 57 natifs, 73 HTTP, 27 profils. Historique conservé ; contrat propre, aucun EnvoiRelations changé.\nA31/A32 hors lot selon consigne 19h30 ; ni validation visuelle ni GO sur le réel.\n')
    v.verify(False)
    v.verify(True)
