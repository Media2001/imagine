"""Vérification C28 sans argument ; --live relit seulement le site fictif gardé."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'wp/outils/demo'))
import c28


def verify(live=False):
    load = lambda name: json.loads((c28.OUT/(name+'.json')).read_text(encoding='utf-8'))
    r = load('recette-finale')
    n = load('natif-final')
    p = load('preservation-finale')
    c14 = load('c14-regressions-finales')
    checks = {}
    def check(key, value):
        checks[key] = bool(value)
        if not value:
            raise AssertionError(key)
    check('recette_complete_non_vide', r['error'] is None and r['total'] == len(r['checks']) == 200 and r['failures'] == 0 and all(r['checks'].values()))
    check('profils_commandes_actions_retablis', bool(r['cleanup']) and all(r['cleanup'].values()) and r['cleanup']['business_preserved'])
    check('instantane_pas_liste_courante', r['checks']['instantane3_relu_immuable'] and r['mutations']['live_list']['observed'] != r['mutations']['live_list']['expected'])
    for stage in ['avant','paye','ajout4','retrait1','refund_commande','refund_ligne_non_ventile','refund_ligne_pack']:
        check('parcours_'+stage, r['checks'][stage+'_compte_HTTP_memes_numeros'] and r['checks'][stage+'_compte_memes_numeros'])
    check('32_temoins_C26_inchanges', r['C26']['witnesses'] == 32 and r['mutations']['response_only'] == {'count':32,'detected':32} and hashlib.sha256((ROOT/r['C26']['file']).read_bytes()).hexdigest() == r['C26']['sha256'])
    check('sept_sorties_pack_non_vides', len(r['surfaces']) == 7 and all(x['surface_present'] and x['bytes'] > 0 and x['ok'] and not x['leak'] for x in r['surfaces']))
    check('reseau_mail_bloques', r['checks']['HTTP_mail_tous_bloques'] and r['checks']['aucun_tiers_public_seuls_gravatars_admin_bloques'])
    data = json.loads(n['native']['stdout'])
    check('natif_25', n['native']['code'] == 0 and not n['native']['stderr'] and data['total'] == len(data['checks']) == 25 and data['failures'] == 0 and all(data['checks'].values()) and n['business_preserved'])
    check('C14_45_regressions', c14['business_preserved'] and len(c14['results']) == 1 and all(v['code'] == 0 and not v['stderr'] and len(json.loads(v['stdout'])) == 45 and all(json.loads(v['stdout']).values()) for v in c14['results'].values()))
    check('etat_avant_fixture_sauf_produit_declare', bool(p['checks']) and all(p['checks'].values()) and p['initial_before_fixture'] == p['projected_without_only_owned_product'])
    check('sources_apres_derniere_ecriture', all(x['sources'] == c28.sources() for x in [r,n,p,c14]))
    unit = (c28.OUT/'unitaire-final.log').read_text(encoding='utf-8')
    lint = load('lint-final')
    check('syntaxe_sources_PHP', lint['exit'] == 0 and lint['files'] and len(lint['files']) == len(lint['stdout'].splitlines()) and not lint['stderr'])
    check('PHPUnit_2_18', bool(re.search(r'OK \(2 tests, 18 assertions\)', unit)))
    image = load('preparation-image')
    check('image_reconstruite', image['exit'] == 0 and 'image verifiee sha256:' in (c28.OUT/image['log']).read_text(encoding='utf-8'))
    replay = load('regression-finale')
    log = (c28.OUT/replay['log']).read_text(encoding='utf-8')
    raw = re.search(r'^T01_RESULT (.+)$', log, re.M)
    totals = json.loads(raw[1]) if raw else {}
    check('rejeu_general_au_vert', replay['exit'] == 0 and totals.get('tests',0) > 1100 and totals.get('failures') == totals.get('errors') == totals.get('skipped') == 0 and totals.get('pass') is True and bool(re.search(r'REJEU : .* PASS',log)))
    check('outils_584_verts_A32_limite_inchangee', totals['tools']['checks'] == 584 and totals['tools']['failures'] == 0 and totals['packets']['failures'] == [{'lot':'A-32','control':'A32_PARTIAL_EVIDENCE'}])
    for name in ['NOTE.md','A-VOIR.md']:
        check(name, (c28.OUT/name).is_file() and len((c28.OUT/name).read_text(encoding='utf-8')) > 400)
    readme = (ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    check('README_section_unique', readme.count('## C-28 — packs thématiques') == 1)
    if (c28.OUT/'reception.json').exists():
        receipt = load('reception')
        check('sceau_sources', receipt['sources'] == c28.sources())
        check('sceau_preuves', bool(receipt['evidence']) and all(hashlib.sha256((c28.OUT/name).read_bytes()).hexdigest() == expected for name,expected in receipt['evidence'].items()))
    if live:
        identity = c28.guard()
        expected = {name:hashlib.sha256((ROOT/'wp'/name).read_bytes()).hexdigest() for name in c28.FILES}
        check('live_sources_relues', c28.hashes(c28.FILES) == expected)
        demo = 'mu-plugins/imagine-c28-demo.php'
        check('live_exception_fictive_relue', c28.hashes([demo])[demo] == hashlib.sha256((ROOT/'wp/outils/demo/c28-demo.php').read_bytes()).hexdigest())
        value = c28.wp('''$f=get_option('imagine_c28_fixture');$p=wc_get_product($f['product']);echo wp_json_encode(['fixture'=>$f,'ids'=>Imagine\\Site\\PacksThematiques::numeros($p),'price'=>$p->get_price(),'fictif'=>$p->get_meta('_imagine_c28_fictif'),'observer'=>file_exists(WP_CONTENT_DIR.'/mu-plugins/c28-observer.php'),'buyer_rights'=>Imagine\\Site\\AchatsNumeros::droits((int)get_option('imagine_c09_fixture')['users']['V-INSCRIT']),'active_plugins'=>get_option('active_plugins')]);''')
        check('live_fixture3_prix_fictif', value['fixture']['fictif'] is True and value['ids'] == [11,18,25] and value['price'] == '3.28' and value['fictif'] == '1')
        check('live_acheteur_retabli_sans_achat', value['buyer_rights'] == [] and value['observer'] is False)
        check('live_pas_extension_bundle_commerciale', not any('product-bundles' in v or 'composite-products' in v for v in value['active_plugins']))
        # Contrat des objets préexistants : l'unique delta produit C28 est déjà qualifié.
        check('live_etat_restaure_relu', c28.state() == p['current'])
    print(json.dumps({'C28':'PASS','mode':'live-readonly' if live else 'offline','checks':len(checks),'success':all(checks.values())}, ensure_ascii=False))
    return checks


if __name__ == '__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
