"""Vérifie B09 sans site, réseau, Docker ni argument ; Python 3.11 standard."""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PREFIX='production/B-09/'
RECIPE=set('observateurs_positifs footer_natif_present footer_cinq_pages_natives principal_sans_entree_B09 page_publique_faq FAQ_quatre_rubriques_sans_question page_publique_cgv page_legale_vide_cgv page_publique_confidentialite page_legale_vide_confidentialite page_publique_cookies page_legale_vide_cookies page_publique_contact privacy_declaree_native consentement_initial_non_coche POST_reel_pas_enumeration_compte stockage_prive_local nonce_refuse_sans_insertion admin_liste_detail_positifs antislash_detail_exact detail_admin_seul declaration_outils_C21_natifs export_adresse_antislash_exact_sans_tiers REST_temoin_public_positif recherche_temoin_public_positif absence_REST_recherche mutation_reelle_REST_recherche_detectee isolation_revenue_apres_mutation effacement_natif_cible_tiers_preserve effacement_postmeta_relu aucun_email_HTTP_du_contact'.split())
STRUCTURE=set('seed_disponible pages_et_menu_idempotents intitules_publics_exacts contenu_vide_cgv contenu_vide_confidentialite contenu_vide_cookies contenu_vide_contact privacy_native FAQ_quatre_rubriques_vides_natives FAQ_editable_blocs_sans_code_seed_non_destructif menu_principal_non_modifie footer_natif_attribue seed_stable_ne_reecrit_pas_les_items item_etranger_refuse menu_etranger_refuse page_etrangere_refusee'.split())
SEED=set('interruption_processus_reelle item_orphelin_marque reprise_autre_processus ids_partiels_reutilises rejeu_idempotent items_principaux_preserves'.split())
RESTORATION=set('users usermeta posts postmeta comments commentmeta navigation wc_orders wc_orders_meta wc_order_addresses wc_order_operational_data woocommerce_order_items woocommerce_order_itemmeta options_metier'.split())
CLEANUP=set('contacts_et_observations_retires usermeta_admin_restaure usermeta_lecteur_restaure observateur_et_mutation_retires'.split())
ISOLATION={'route_rest_fermee':True,'REST_aucun_message':True,'recherche_aucun_message':True}
MUTATIONS=set('slash consentement mail http prive rest export effacement lecture nonce admin raccord'.split())
TITLES={'faq':'FAQ du service client','cgv':'Conditions générales de vente','confidentialite':'Politique de confidentialité','cookies':'Gestion des cookies','contact':'Contact'}
BLOCK="// B09 — pages natives et contact privé local.\nrequire_once __DIR__ . '/Contact.php';\nrequire_once __DIR__ . '/ContactConfidentialite.php';\nrequire_once __DIR__ . '/AutresPages.php';\nContact::register();\nContactConfidentialite::register();\nAutresPages::register();\n\n"
CORE=['wp/plugins/imagine-site/'+n for n in ['Contact.php','ContactConfidentialite.php','AutresPages.php']]
TESTS=['wp/plugins/imagine-site/tests/ContactAdapterTest.php','wp/plugins/imagine-site/tests/ContactWPStubs.php','wp/tests/demo/b09-horslive.php']


def digest(raw): return hashlib.sha256(raw).hexdigest()
def load(path): return json.loads(path.read_text(encoding='utf-8'))
def junit(text):
    m=re.search(r'B09 JUNIT BEGIN\s*(.*?)B09 JUNIT END',text,re.S)
    if not m: raise AssertionError('JUNIT absent')
    return {k:int(ET.fromstring(m.group(1)).find('testsuite').attrib[k]) for k in ['tests','assertions','errors','failures','skipped']}


def validate(root,packet):
    n=0
    def need(ok,code):
        nonlocal n
        n+=1
        if not ok: raise AssertionError(code)
    def path(name):
        need(isinstance(name,str) and '\\' not in name and not name.startswith('/') and ':' not in name and '..' not in Path(name).parts,'CHEMIN')
        p=root/name
        need(p.is_file() and not p.is_symlink(),'FICHIER '+name)
        return p
    def alltrue(data,expected,code):
        need(set(data)==expected and all(v is True for v in data.values()),code)
    def receipt(name):
        d=load(path(PREFIX+name))
        need(d.get('scope')=='imagine-test-demo','CIBLE '+name)
        return d
    def bound(d,names):
        for name in names:
            need(d.get('sources',{}).get(name)==digest(path(name).read_bytes()),'SOURCE_TESTEE '+name)
    need(packet.get('scope')=='imagine-test-demo' and packet.get('version')==1,'SCHEMA')
    need(bool(packet.get('sources')) and bool(packet.get('artifacts')),'MANIFESTE_VIDE')
    minimum_sources=set(CORE+TESTS+['wp/outils/demo/'+name for name in ['b09.py','b09-seed.php','b09-recette.py','b09-readback.py','b09-local.py','b09-mutations.py','b09-gates.py']]+['wp/tests/demo/b09-structure.php','wp/tests/demo/b09-observer.php','wp/tests/demo/b09-mutation-prive.php'])
    need(minimum_sources <= set(packet['sources']),'MANIFESTE_SOURCES_COMPLET')
    minimum_artifacts={PREFIX+name for name in ['verifier.py','A-VOIR.md','NOTE.md','sources-officielles.json','tests-finaux.log','mutations-finales.json','recette-finale.json','structure-finale-verifiee.json','pages-reprise-finale.json','reprise-stable-finale.json','readback-final.json','preparation-finale.json','preparation-finale.log','regression-finale.json','regression-finale.log']}
    minimum_artifacts|={PREFIX+'mutations-finales-'+name+'.log' for name in MUTATIONS}
    need(minimum_artifacts <= set(packet['artifacts']),'MANIFESTE_PREUVES_COMPLET')
    for name,sha in packet['sources'].items():
        need(name.startswith(('wp/outils/demo/b09','wp/tests/demo/b09','wp/plugins/imagine-site/Contact','wp/plugins/imagine-site/AutresPages','wp/plugins/imagine-site/tests/Contact')),'PERIMETRE_SOURCE')
        need(digest(path(name).read_bytes())==sha,'EMPREINTE_SOURCE '+name)
    for name,sha in packet['artifacts'].items():
        need(name.startswith(PREFIX),'PERIMETRE_PREUVE')
        need(digest(path(name).read_bytes())==sha,'EMPREINTE_PREUVE '+name)
    boot=path('wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    need(boot.count(BLOCK)==1,'CONTRAT_BOOTSTRAP')
    footer=path('wp/themes/imagine/footer.php').read_text(encoding='utf-8')
    need("has_nav_menu('imagine-footer')" in footer and "'theme_location' => 'imagine-footer'" in footer and "'fallback_cb' => false" in footer and 'imagine_navigation()' not in footer,'CONTRAT_FOOTER')
    readme=path('wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    header='## B-09 — FAQ, pages légales et contact'
    need(readme.count(header)==1,'README_SECTION')
    section=readme.split(header,1)[1].split('\n## ',1)[0].strip()
    need(digest(section.encode())==packet['readme_section_sha256'],'README_CONTRAT')
    need(all(t in section for t in ['wp_slash($meta)','imagine-contacts','imagine_contact_nom/email/texte/consentement/date','production/B-09/verifier.py','Détails']),'README_CONTENU')
    unit=junit(path(PREFIX+'tests-finaux.log').read_text(encoding='utf-8'))
    need(unit=={'tests':6,'assertions':188,'errors':0,'failures':0,'skipped':0},'UNITAIRES')
    mutations=receipt('mutations-finales.json')
    bound(mutations,CORE+TESTS)
    rows=mutations['mutations']
    need(len(rows)==12 and {r['mutation'] for r in rows}==MUTATIONS,'MUTATIONS_ENSEMBLE')
    for row in rows:
        text=path(PREFIX+row['log']).read_text(encoding='utf-8');j=junit(text)
        need(row['sha256']==digest(text.encode()),'MUTATION_LOG')
        need(row['exit']==1 and j['failures']>0 and j['errors']==j['skipped']==0 and j['tests']==6,'MUTATION_REELLEMENT_ROUGE')
        need(row['detected'] is True and all(int(row['junit'][k])==j[k] for k in j),'MUTATION_RESULTAT')
    need(mutations['count']==mutations['detected']==len(rows),'MUTATIONS_TOTAL')
    recipe=receipt('recette-finale.json')
    bound(recipe,CORE+['wp/outils/demo/b09-recette.py','wp/tests/demo/b09-observer.php','wp/tests/demo/b09-mutation-prive.php'])
    alltrue(recipe['checks'],RECIPE,'RECETTE_CONTROLES')
    alltrue(recipe['cleanup'],CLEANUP,'RECETTE_NETTOYAGE')
    alltrue(recipe['restoration'],RESTORATION,'RECETTE_RESTAURATION')
    need(recipe['business_preserved'] is True and recipe['error'] is None,'RECETTE_METIER')
    need(recipe['baseline_isolation']==recipe['after_mutation_isolation']==ISOLATION,'ISOLATION_VERTE')
    need(recipe['mutation_isolation']=={k:False for k in ISOLATION},'ISOLATION_MUTATION_ROUGE')
    need(recipe['positive_observers']=={'ambiance_mail':1,'ambiance_http':1},'OBSERVATEURS_POSITIFS')
    need(not any(v for k,v in (recipe['observations'].items() if isinstance(recipe['observations'],dict) else []) if k.startswith('b09_')),'TRANSPORTS')
    structure=receipt('structure-finale-verifiee.json')
    bound(structure,['wp/outils/demo/b09-seed.php','wp/tests/demo/b09-structure.php'])
    alltrue(structure['checks'],STRUCTURE,'STRUCTURE_CONTROLES')
    alltrue(structure['restoration'],RESTORATION,'STRUCTURE_RESTAURATION')
    need(structure['business_preserved'] is True and structure['runners_removed'] is True,'STRUCTURE_NETTOYAGE')
    seed=receipt('pages-reprise-finale.json')
    bound(seed,['wp/outils/demo/b09-seed.php'])
    alltrue(seed['checks'],SEED,'SEED_CONTROLES')
    need(seed['interrupted_exit']==73 and seed['partial']['attached']==2 and len(seed['partial']['ownership']['items'])==3,'INTERRUPTION_REELLE')
    need(seed['seed_runner_removed'] is True,'SEED_RUNNER')
    f=seed['fixture'];partial=seed['partial']
    need(set(f['pages'])==set(f['items'])==set(TITLES) and len(set(f['pages'].values())|set(f['items'].values()))==10,'FIXTURE_ENSEMBLE')
    need(partial['pages']==f['pages'] and all(f['items'][k]==v for k,v in partial['ownership']['items'].items()),'REPRISE_IDS')
    expected_faq=''.join('<!-- wp:heading --><h2 class="wp-block-heading">'+h+'</h2><!-- /wp:heading -->\n' for h in ['Accès numérique','Abonnement','Facturation','Livraison'])
    need(set(seed['readback'])==set(TITLES),'PAGES_ENSEMBLE')
    for key,title in TITLES.items():
        r=seed['readback'][key]
        need(r['id']==f['pages'][key] and r['title']==title and r['content']==(expected_faq if key=='faq' else '') and r['url'].startswith('http://192.168.129.32:8085/'),'PAGE '+key)
    stable=receipt('reprise-stable-finale.json')
    bound(stable,['wp/outils/demo/b09-seed.php','wp/outils/demo/b09.py'])
    alltrue(stable['unchanged_existing_fixture'],set('users usermeta posts postmeta navigation'.split()),'SEED_STABLE')
    need(stable['idempotent'] is True and stable['business_preserved'] is True and stable['runner_removed'] is True and stable['fixture']==f,'SEED_STABLE_RESULTAT')
    final=receipt('readback-final.json')
    bound(final,CORE+['wp/outils/demo/b09-readback.py'])
    need(final['checks'] and len(final['checks'])==9 and all(v is True for v in final['checks'].values()),'READBACK_CONTROLES')
    need(final['foreign_preserved'] and len(final['foreign_preserved'])==12 and all(v is True for v in final['foreign_preserved'].values()),'TIERS_PRESERVES')
    native=final['native']
    need(native['contact_posts']==native['contact_meta']==0 and len(native['temporary_files'])==4 and all(v is False for v in native['temporary_files'].values()),'RESIDUS')
    need(native['privacy']==f['pages']['confidentialite'] and native['locations']['imagine-principal']==22 and native['locations']['imagine-footer']==f['menu'],'NATIF')
    need(native['menu']=={'menu':f['menu'],'items':f['items']},'MENU_FINAL')
    for key,row in native['pages'].items():
        need({k:row[k] for k in ['id','title','content','url']}==seed['readback'][key] and row['marker']==key and row['status']=='publish' and row['type']=='page' and row['parent']==0,'PAGE_READBACK')
    need(set(native['pages'])==set(TITLES),'PAGES_READBACK_ENSEMBLE')
    need(set(final['remote_hashes'])=={'plugins/imagine-site/Contact.php','plugins/imagine-site/ContactConfidentialite.php','plugins/imagine-site/AutresPages.php','plugins/imagine-site/imagine-site.php','themes/imagine/footer.php'},'READBACK_FICHIERS_ENSEMBLE')
    for file,sha in final['remote_hashes'].items():
        need(re.fullmatch('[a-f0-9]{64}',sha) is not None,'READBACK_SHA')
        if 'wp/'+file in CORE:
            need(sha==digest(path('wp/'+file).read_bytes()),'READBACK_SOURCE_DISTANTE')
    prep=receipt('preparation-finale.json')
    need(prep['exit']==0 and 'image verifiee sha256:' in path(PREFIX+prep['log']).read_text(encoding='utf-8'),'IMAGE_RECONSTRUITE')
    reg=receipt('regression-finale.json')
    bound(reg,CORE+TESTS[:2])
    need(reg['exit']==0 and len(reg['results'])==1,'REGRESSION_EXECUTION')
    result=reg['results'][0]
    need(result['pass'] is True and result['tests']>=unit['tests'] and result['failures']==result['errors']==result['skipped']==0,'REGRESSION_VERTE')
    need(result['tools']['failures']==0 and result['packets']['failures']==[],'REGRESSION_PORTES')
    need('T01 CLEANUP : absence verifiee' in path(PREFIX+reg['log']).read_text(encoding='utf-8'),'REGRESSION_NETTOYAGE')
    counts={'unit_tests':unit['tests'],'unit_assertions':unit['assertions'],'native_checks':len(RECIPE)+len(STRUCTURE)+len(SEED),'source_mutations':len(rows),'live_mutations':1,'global_tests':result['tests'],'global_assertions':result['assertions'],'global_tool_checks':result['tools']['checks']}
    need(packet['counts']==counts,'TOTAUX_RECALCULES')
    return {'gates':n,**counts}


def main():
    if len(sys.argv)!=1: raise SystemExit('B09 : aucun argument attendu')
    counts=validate(ROOT,load(ROOT/PREFIX/'final-V2.json'))
    print('B09 PASS '+json.dumps(counts,ensure_ascii=False,sort_keys=True))


if __name__=='__main__':
    main()
