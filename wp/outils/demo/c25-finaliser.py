"""Scellement C25 et vérification hors site des preuves, sans toucher aux lots voisins."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import xml.etree.ElementTree as ET
import c25

NAMES = {
    'canonical': 'canonique-corrections002-V2',
    'mutations': 'mutations-corrections002-V2',
    'image': 'image-corrections002-V2',
    'regression': 'regression-corrections002-V2',
    'native': 'recette-corrections002-V2',
}


def read(name):
    return json.loads((c25.PROOF / (name + '.json')).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def readme_contract():
    text = (c25.ROOT / 'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    marker = '## C-25 — rétractation, demande seule'
    assert text.count(marker) == 1
    section = marker + text.split(marker, 1)[1].split('\n## ', 1)[0]
    for required in ['wp_slash($record)', 'added_option', 'updated_option', 'avant/après', 'UTC', '1–365', 'delete_user', 'panne SQL persistante', 'wp_die', 'c25-recette.py', 'c25.py local', 'preparer-image.ps1', 'rejouer.ps1', 'hors réseau', 'imagine-test-demo']:
        assert required in section, required
    return hashlib.sha256(section.encode()).hexdigest()


def gates():
    sources = c25.sources()
    receipts = {key: read(name) for key, name in NAMES.items()}
    for key in ['canonical', 'image', 'regression', 'native']:
        assert receipts[key]['sources'] == sources, 'Preuve périmée : ' + key
    for key in ['canonical', 'image', 'regression']:
        row = receipts[key]
        assert row['exit'] == 0 and digest(c25.PROOF / row['log']) == row['log_sha256'], key
    canonical = receipts['canonical']['junit']
    assert int(canonical['tests']) == 10 and int(canonical['assertions']) == 172
    assert all(int(canonical[k]) == 0 for k in ['errors', 'failures', 'skipped'])
    image = (c25.PROOF / receipts['image']['log']).read_text(encoding='utf-8')
    assert 'PREPARATION T01 : image verifiee sha256:' in image
    regression = receipts['regression']['results']
    assert len(regression) == 1
    regression = regression[0]
    assert regression['pass'] and regression['tests'] >= int(canonical['tests'])
    assert all(regression[k] == 0 for k in ['errors', 'failures', 'skipped'])
    assert regression['tools']['failures'] == 0
    log = (c25.PROOF / receipts['regression']['log']).read_text(encoding='utf-8')
    for name in ['testAntislashWordPressReluEtExporteSansPerte', 'testReglagesJournalAjoutModificationEtRollbackPreimage', 'testDemandeSeulePersistanteEtRejeuSansAucunEffet', 'testDelaiEtOriginesAvecBornesEtFermeturePrudente', 'testRaccordsEntreeAdministrationEtDateManuelle']:
        assert '<testcase name="' + name + '"' in log
    mutations = receipts['mutations']
    assert mutations['all_detected'] and mutations['total'] == len(mutations['mutations']) == 15
    for row in mutations['mutations']:
        proof = read(row['log'][:-4])
        assert proof['sources'] == sources and proof['exit'] == 1
        assert digest(c25.PROOF / row['log']) == proof['log_sha256']
        text = (c25.PROOF / row['log']).read_text(encoding='utf-8')
        xml = text.split('C25 JUNIT BEGIN', 1)[1].split('C25 JUNIT END', 1)[0].strip()
        failed = [t.attrib['name'] for t in ET.fromstring(xml).iter('testcase') if t.find('failure') is not None]
        assert row['required_failure'] in failed
    native = receipts['native']
    assert all(native['checks'].values()) and not native['native']['failures']
    assert not native.get('error')
    for name in ['options_creation_panne_preimage_absente_relue', 'options_creation_journal_avant_apres_auteur_UTC', 'options_modification_journal_2_reglages', 'options_modification_panne_preimage_exacte_relue', 'options_deux_pannes_SQL_reelles']:
        assert native['checks'][name] is True
    for name in ['motif_HTTP_relu', 'motif_HTTP_meta_WP_exacte', 'motif_HTTP_export_C21_registre_natif_exact', 'journal_panne_note_annulee']:
        assert native['native']['checks'][name] is True
    assert native['settings_HTTP']['fixture_group_restricted_to_C25'] is True
    readme_contract()
    assert native['native']['total'] == len(native['native']['checks']) and all(native['native']['checks'].values())
    assert native['native_exit'] == 0 and native['native_stderr'] == ''
    assert all(native['restoration'].values()) and native['business_preserved']
    assert all(native['exact_rows_preserved'].values()) and all(native['tests_removed'].values())
    assert not any(k.startswith('c25_') and v for k, v in native['observer_counts'].items())
    assert read('recovery-metier-V2')['business_equal_original'] is True
    for name in ['A-VOIR.md', 'NOTE.md']:
        assert (c25.PROOF / name).is_file()
    bootstrap = (c25.ROOT / 'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    assert bootstrap.count(c25.BLOCK) == 1
    return sources, receipts, regression


def sceller():
    sources, receipts, regression = gates()
    identity = c25.b06.guard()
    readback = c25.b06.hashes(c25.NAMES)
    assert readback == {name: digest(c25.ROOT / 'wp' / name) for name in c25.NAMES}
    state = c25.wp('''echo wp_json_encode(['default'=>Imagine\\Site\\Retractation::configuration(),'requests_empty'=>Imagine\\Site\\RetractationConfidentialite::lignes()===[],'observer_absent'=>!file_exists(WP_CONTENT_DIR.'/mu-plugins/c25-observer.php'),'runtime_absent'=>!file_exists(WP_CONTENT_DIR.'/imagine-demo-build/c25-runtime.php'),'bootstrap_contract'=>substr_count(file_get_contents(WP_PLUGIN_DIR.'/imagine-site/imagine-site.php'),''' + c25.php(c25.BLOCK) + ''')===1]);''')
    assert state == {'default': {'jours': 14, 'origine': 'paiement'}, 'requests_empty': True, 'observer_absent': True, 'runtime_absent': True, 'bootstrap_contract': True}
    native = receipts['native']
    data = {'result': 'PASS', 'identity': identity, 'sources': sources, 'remote_sources': readback,
            'bootstrap_contract': True, 'receipts': {name + '.json': digest(c25.PROOF / (name + '.json')) for name in NAMES.values()},
            'docs': {name: digest(c25.PROOF / name) for name in ['A-VOIR.md', 'NOTE.md']},
            'canonical': receipts['canonical']['junit'], 'regression': regression,
            'mutations_detected': len(receipts['mutations']['mutations']),
            'http_checks': len(native['checks']), 'native_checks': native['native']['total'],
            'integration_checks': len(native['checks']) + native['native']['total'],
            'readback': state, 'business_restored': True, 'blockers': [], 'visual_validation_pending': True,
            'readme_C25_sha256': readme_contract()}
    c25.save('livraison-corrections002-V2', data)
    print(json.dumps({k: data[k] for k in ['result', 'canonical', 'regression', 'mutations_detected', 'integration_checks', 'business_restored', 'blockers']}, ensure_ascii=False))


def verifier():
    sources, receipts, regression = gates()
    final = read('livraison-corrections002-V2')
    assert final['result'] == 'PASS' and final['sources'] == sources and final['blockers'] == []
    assert final['readme_C25_sha256'] == readme_contract()
    for key in ['receipts', 'docs']:
        for name, expected in final[key].items():
            assert digest(c25.PROOF / name) == expected, name
    pret = (c25.PROOF / 'PRET').read_text(encoding='utf-8')
    assert 'C-25' in pret and digest(c25.PROOF / 'livraison-corrections002-V2.json') in pret
    print(json.dumps({'result': 'PASS', 'sources': len(sources), 'canonical_tests': int(final['canonical']['tests']), 'canonical_assertions': int(final['canonical']['assertions']), 'integration_checks': final['integration_checks'], 'mutations': final['mutations_detected'], 'regression_tests': regression['tests'], 'regression_assertions': regression['assertions'], 'tools': regression['tools'], 'pret_verified': True}, ensure_ascii=False))


if __name__ == '__main__':
    assert sys.argv[1] in ['sceller', 'verifier']
    globals()[sys.argv[1]]()
