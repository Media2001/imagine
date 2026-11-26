"""Vérification B08 hors réseau, aucun accès à un site ni mutation."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PROOF = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    final = json.loads((PROOF / 'final.json').read_text(encoding='utf-8'))
    for name, expected in final['manifest'].items():
        assert name.startswith(('wp/plugins/imagine-site/', 'wp/outils/demo/b08', 'wp/tests/demo/b08', 'wp/themes/imagine/header.php', 'production/B-08/'))
        assert digest(ROOT / name) == expected, 'Source périmée : ' + name
    for name, expected in final['proofs'].items():
        assert digest(PROOF / name) == expected, 'Preuve altérée : ' + name
    assert final['bootstrap_additif_preserve'] and all(final['checks'].values())
    assert final['pages'] == 10 and final['menu_items'] == 15
    assert final['cleanup'] == {'sujets': [], 'configuration': {'don': False, 'parts_url': ''}, 'observateur': False, 'seed': False}
    canon = json.loads((PROOF / 'canonique.json').read_text(encoding='utf-8'))
    assert canon['exit'] == 0
    assert digest(PROOF / canon['log']) == canon['sha256']
    assert canon['results'][0] == {'tests': 1149, 'assertions': 36036, 'failures': 0, 'errors': 0, 'skipped': 0, 'tools': {'tools': 18, 'checks': 417, 'failures': 0, 'excluded': []}, 'pass': True}
    prep = json.loads((PROOF / 'preparation-image.json').read_text(encoding='utf-8'))
    assert prep['exit'] == 0 and digest(PROOF / prep['log']) == prep['sha256']
    local = (PROOF / 'horslive-final.log').read_text(encoding='utf-8')
    xml = re.search(r'B08 JUNIT BEGIN\s*(.*?)B08 JUNIT END', local, re.S).group(1)
    unit = ET.fromstring(xml).find('testsuite').attrib
    assert {k: int(unit[k]) for k in ['tests','assertions','errors','failures','skipped']} == {'tests': 6, 'assertions': 181, 'errors': 0, 'failures': 0, 'skipped': 0}
    mutants = json.loads((PROOF / 'mutations.json').read_text(encoding='utf-8'))
    assert len(mutants['results']) == len({r['mutation'] for r in mutants['results']}) == 12
    for r in mutants['results']:
        assert r['failures'] > 0 and r['errors'] == 0 and r['exit'] == 1
        assert digest(PROOF / r['log']) == r['sha256']
    native = json.loads((PROOF / 'recette-livraison.json').read_text(encoding='utf-8'))
    assert len(native['checks']) == 31 and all(native['checks'].values())
    assert all(native['exact_restoration'].values()) and native['business_preserved'] and native['observer_removed']
    for receipt in [canon, mutants, native]:
        assert all(final['manifest'].get(k) == v for k, v in receipt['sources'].items()), 'Lien aux sources exécutées périmé'
    assert (PROOF / 'A-VOIR.md').stat().st_size > 1000
    print('B08 PASS : 6 tests / 181 assertions ; 12 mutations détectées ; 31 contrôles HTTP/native ; 1149 tests / 36036 assertions canoniques ; 18 outils / 417 contrôles ; restauration exacte ; 10 pages et 15 items natifs ; don OFF / URL vide / essais retirés.')


if __name__ == '__main__':
    main()
