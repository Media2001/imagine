"""B08 corrigé : vérification locale sans réseau, site, argument ou écriture."""
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
PROOF = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((PROOF / (name + '.json')).read_text(encoding='utf-8'))


def main():
    assert len(sys.argv) == 1, 'Aucun argument'
    final = load('corrections-final')
    assert final['scope'] == 'imagine-test-demo'
    for name, expected in final['manifest'].items():
        assert name.startswith(('wp/plugins/imagine-site/', 'wp/outils/demo/b08', 'wp/tests/demo/b08', 'wp/themes/imagine/header.php', 'production/B-08/'))
        assert digest(ROOT / name) == expected, 'Source périmée : ' + name
    for name, expected in final['proofs'].items():
        assert Path(name).name == name
        assert digest(PROOF / name) == expected, 'Preuve altérée : ' + name
    assert final['checks'] and all(v is True for v in final['checks'].values())
    assert final['pages'] == 10 and final['menu_items'] == 15
    assert final['cleanup'] == {'sujets': [], 'configuration': {'don': False, 'parts_url': ''}, 'observateur': False, 'seed': False}
    canon = load('corrections-final-canonique')
    prep = load('corrections-final-preparation')
    for receipt in [canon, prep]:
        assert receipt['exit'] == 0 and digest(PROOF / receipt['log']) == receipt['sha256']
    result = canon['results'][0]
    assert len(canon['results']) == 1 and result['tests'] >= 1151 and result['assertions'] > 36036
    assert result['pass'] and all(result[k] == 0 for k in ['failures', 'errors', 'skipped'])
    assert result['tools']['failures'] == 0 and result['tools']['excluded'] == []
    xml = re.search(r'B08 JUNIT BEGIN\s*(.*?)B08 JUNIT END', (PROOF / 'corrections-final-local.log').read_text(encoding='utf-8'), re.S).group(1)
    unit = ET.fromstring(xml).find('testsuite').attrib
    assert {k: int(unit[k]) for k in ['tests', 'assertions', 'errors', 'failures', 'skipped']} == {'tests': 8, 'assertions': 194, 'errors': 0, 'failures': 0, 'skipped': 0}
    mutants = load('corrections-final-mutations')
    assert {r['mutation'] for r in mutants['results']} == {'slash', 'https', 'don', 'parts', 'consentement', 'mail', 'http', 'prive', 'rest', 'public', 'export', 'effacement', 'lecture', 'nonce'}
    assert len(mutants['results']) == 14
    for row in mutants['results']:
        assert row['exit'] == 1 and row['errors'] == 0 and row['failures'] > 0
        assert digest(PROOF / row['log']) == row['sha256']
    receipts = [canon, prep, mutants]
    for kind, count in [('reprise', 5), ('cibles', 7), ('collisions', 10), ('http', 35)]:
        receipt = load('corrections-final-' + kind)
        assert len(receipt['checks']) == count and all(v is True for v in receipt['checks'].values())
        assert receipt['exact_restoration'] and all(receipt['exact_restoration'].values()) and receipt['business_preserved']
        receipts.append(receipt)
    for label, failure in [('item', 'item_refuse'), ('cible', 'compte_sans_url_si_cible_absente')]:
        receipt = load('corrections-final-mutant-' + label)
        assert receipt['checks'][failure] is False
        assert all(v is True for k, v in receipt['checks'].items() if k != failure)
        assert all(receipt['exact_restoration'].values()) and receipt['business_preserved']
        receipts.append(receipt)
    for receipt in receipts:
        assert receipt['scope'] == 'imagine-test-demo'
        assert all(final['manifest'].get(k) == v for k, v in receipt['sources'].items()), 'Sources exécutées périmées'
    for label in ['slash', 'https']:
        xml = re.search(r'B08 JUNIT BEGIN\s*(.*?)B08 JUNIT END', (PROOF / ('corrections-red-' + label + '.log')).read_text(encoding='utf-8'), re.S).group(1)
        red = ET.fromstring(xml).find('testsuite').attrib
        assert int(red['failures']) == 1 and int(red['errors']) == 0
    assert load('corrections-red-reprise')['checks']['reprise_sans_doublon'] is False
    assert load('corrections-red-cibles-oracle')['checks']['compte_sans_url_si_cible_absente'] is False
    readme = (ROOT / 'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    for lot, expected in final['readme_sections'].items():
        section = re.search(r'^## ' + lot + r' — .*?(?=^## |\Z)', readme, re.M | re.S).group(0)
        assert hashlib.sha256(section.encode()).hexdigest() == expected
    print('B08 PASS : 8 tests / 194 assertions ; 14 mutations PHP + 2 mutations seed détectées ; 35 contrôles HTTP + 22 contrôles seed ; restauration exacte ; suite globale ' + str(result['tests']) + ' tests / ' + str(result['assertions']) + ' assertions ; ' + str(result['tools']['checks']) + ' contrôles outils ; 10 pages / 15 items ; nettoyage vérifié.')


if __name__ == '__main__':
    main()
