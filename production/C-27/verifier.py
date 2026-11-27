"""C27 : vérification du paquet, Python 3.11 standard, sans site, réseau ni argument."""
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PREFIX='production/C-27/'
CORE=['wp/plugins/imagine-site/'+n for n in ['AcquisitionRegles.php','Acquisition.php','AcquisitionReglages.php','AcquisitionConfidentialite.php','AcquisitionAdmin.php']]
UNIT=['wp/plugins/imagine-site/tests/'+n for n in ['AcquisitionAdapterTest.php','AcquisitionReglesTest.php','AcquisitionWPStubs.php']]
TOOLS=['wp/outils/demo/'+n for n in ['c27.py','c27-native.py','c27-recette.py','c27-gates.py','c27-mutations.py','c27-seed.py','c27-readback.py','c27-finaliser.py','c27-corrections.py']]
TESTS=['wp/tests/demo/'+n for n in ['c27-runtime.php','c27-observer.php','c27-horslive.php','c27-verifier-tests.py','c27-corrections-runtime.php']]
BLOCK="// C27 — déclaration facultative après paiement seulement.\n"+''.join("require_once __DIR__ . '/"+n.rsplit('/',1)[-1]+"';\n" for n in CORE)+'Acquisition::register();\nAcquisitionReglages::register();\nAcquisitionConfidentialite::register();\nAcquisitionAdmin::register();\n\n'
RECIPE=set('observateurs_positifs C10_section_dans_formulaire_sous_bouton_sans_deplacement C10_creation_journal_en_panne_restaure_preimage C10_POST_natif_liste_journal_auteur_date C10_liste_invalide_rejetee_sans_journal C10_modification_panne_restaure_antislash_exact tunnel_avant_paiement_sans_question confirmation_impayee_absence_non_vide POST_signe_avant_paiement_refuse mutation_native_pas_avant_paiement_tue_POST garde_revenue_apres_mutation autre_compte_et_anonyme_sans_question confirmation_payee_question_facultative_fermee question_ne_revient_pas_sans_reponse nonce_invalide_refuse choix_libre_refuse tiers_POST_signe_refuse deux_POST_concurrents_une_reponse double_envoi_refuse_immuable source_compte_vide_initialisee deuxieme_commande_source_non_ecrasee compte_tiers_temoin_reel passer_ne_bloque_rien liste_vide_confirmation_payee_aucune_trace liste_vide_POST_signe_refuse vrai_brouillon_C16_aucun_champ_source C16_meme_payee_jamais_interrogee chiffres_anonymes_periode_exacte periode_sans_reponse_zero_reel periode_invalide_pas_de_nombre chiffres_droits_C19_refus_lecteur export_natif_C21_reponses_date_source_sans_tiers projection_newsletter_et_preferences_inchangees declaration_hors_payload_commande_Odoo effacement_natif_C21_source_reponses_et_propositions effacement_preserve_tiers trace_depersonnalisee_pas_de_nouvelle_reponse chiffres_recalcules_apres_effacement aucun_envoi_C27_email_ou_HTTP mutation_absence_transmission_detectee'.split())
NATIVE=set('adaptateur_present POST_avant_paiement_refuse_sans_trace tiers_refuse hors_liste_refuse reponse_unique_datee_lue double_refuse_immuable source_si_vide_seulement'.split())
RESTORATION=set('users usermeta posts postmeta comments commentmeta navigation wc_orders wc_orders_meta wc_order_addresses wc_order_operational_data woocommerce_order_items woocommerce_order_itemmeta actionscheduler_actions actionscheduler_logs actionscheduler_groups actionscheduler_claims options_metier'.split())
CLEANUP=set('sources_exactes commandes_natives_supprimees adresses_HPOS_et_actions_C16_restaurees brouillon_C16_retire options_et_journaux_C27_restaures profil_admin profil_lecteur profil_tiers observateur_retire'.split())
MUTATIONS=set('avant-paiement tiers operateur source-ecrasee export effacement export-tiers reglage-invalide source-lecture-incertaine effacement-cache vue-effacee'.split())
FUSION=set('I1_corrige I1_mutant I2_corrige I2_mutant deletefail_corrige finalfail_corrige M1_corrige M1_mutant aucune_transmission'.split())
FUSION_CLEANUP=set('sources_exactes commandes_natives_supprimees actions_et_adresses_restaurees options_C27_restaurees profil_lecteur_restaure temporaires_retires'.split())
CHOICES={'lune':'Radio fictive \\ lune','mars':'Journal martien fictif'}
HEADER='## C-27 — Comment nous avez-vous connus ?'


def digest(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def validate(root,packet):
    gates=0
    def need(ok,code):
        nonlocal gates
        gates+=1
        if not ok:raise AssertionError(code)
    def path(name):
        need(isinstance(name,str) and ':' not in name and '\\' not in name and not name.startswith('/') and '..' not in Path(name).parts,'CHEMIN')
        if name.startswith(PREFIX):need(name in packet.get('artifacts',{}),'PREUVE_NON_SCELLEE '+name)
        p=root/name
        need(p.is_file() and not p.is_symlink(),'FICHIER '+name)
        return p
    def receipt(name):
        d=load(path(PREFIX+name));need(d.get('scope')=='imagine-test-demo','CIBLE');return d
    def alltrue(data,expected,code):need(isinstance(data,dict) and set(data)==expected and all(v is True for v in data.values()),code)
    def bound(data,names):
        for name in names:need(data.get('sources',{}).get(name)==digest(path(name).read_bytes()),'SOURCE_TESTEE '+name)
    need(packet.get('version')==2 and packet.get('scope')=='imagine-test-demo','SCHEMA')
    need(set(packet['sources'])==set(CORE+UNIT+TOOLS+TESTS),'SOURCES_ENSEMBLE_EXACT')
    minimum={PREFIX+n for n in ['verifier.py','A-VOIR.md','NOTE.md','sources-officielles.json']}
    need(minimum<=set(packet['artifacts']),'ARTIFACTS_MINIMUM')
    for group in ['sources','artifacts']:
        for name,sha in packet[group].items():
            need(group=='sources' or name.startswith(PREFIX),'PERIMETRE_ARTEFACT')
            need(digest(path(name).read_bytes())==sha,'EMPREINTE '+name)
    boot=path('wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    need(boot.count(BLOCK)==1,'BOOTSTRAP_CONTRAT_C27')
    readme=path('wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    need(readme.count(HEADER)==1,'README_SECTION')
    section=readme.split(HEADER,1)[1].split('\n## ',1)[0].strip()
    need(digest(section.encode())==packet['readme_section_sha256'],'README_CONTRAT')
    need(all(s in section for s in ['imagine_acquisition_choix','imagine_source_acquisition','imagine-acquisition','C16','C21','c27-recette.py','verifier.py']),'README_CONTENU')
    need(all(s in section for s in ['tableau structuré complet','`commande`, `compte`, `date`, `choix`, `libelle`','REPONSE ou VUE','done=false','c27-corrections.py']),'README_CONTRAT_FUSION')
    for label,failures in [('correction-I1-rouge',1),('correction-I2-rouge',3),('correction-M1-rouge',1)]:
        red=receipt(label+'.json');log=path(PREFIX+red['log']);text=log.read_text(encoding='utf-8')
        need(red['exit']==1 and digest(log.read_bytes())==red['log_sha256'] and ('Failures: '+str(failures)+'.') in text and 'ERRORS!' not in text,'TDD_ROUGE '+label)
    names=packet['receipts']
    need(set(names)=={'unit','native','recipe','mutations','prepare','regression','seed','readback','style','fusion'},'REÇUS_ENSEMBLE')
    unit=receipt(names['unit']);bound(unit,CORE+UNIT+['wp/tests/demo/c27-horslive.php'])
    text=path(PREFIX+unit['log']).read_text(encoding='utf-8')
    need(unit['exit']==0 and digest(path(PREFIX+unit['log']).read_bytes())==unit['log_sha256'],'UNIT_LOG')
    m=re.search(r'OK \((\d+) tests, (\d+) assertions\)',text)
    need(m is not None and tuple(map(int,m.groups()))==(12,80),'UNIT_RESULTATS')
    runtime=receipt(names['native']);bound(runtime,CORE+['wp/tests/demo/c27-runtime.php','wp/outils/demo/c27-native.py','wp/outils/demo/c27.py'])
    alltrue(runtime['checks'],NATIVE,'NATIF_CONTROLES');alltrue(runtime['restoration'],RESTORATION,'NATIF_RESTAURATION')
    alltrue(runtime['cleanup'],{'options','profils','runner'},'NATIF_NETTOYAGE');need(runtime['business_preserved'] is True,'NATIF_METIER')
    recipe=receipt(names['recipe']);bound(recipe,CORE+['wp/outils/demo/c27-recette.py','wp/outils/demo/c27-native.py','wp/outils/demo/c27.py','wp/tests/demo/c27-observer.php'])
    alltrue(recipe['checks'],RECIPE,'HTTP_CONTROLES_EXACTS');alltrue(recipe['restoration'],RESTORATION,'HTTP_RESTAURATION');alltrue(recipe['cleanup'],CLEANUP,'HTTP_NETTOYAGE')
    need(recipe['business_preserved'] is True and recipe['error'] is None,'HTTP_METIER')
    need(recipe['positive_observers']=={'ambiance_mail':1,'ambiance_http':1},'OBSERVATEURS_POSITIFS')
    mutation=recipe['mutation_pas_avant_paiement']
    need(mutation['expected_baseline']=={'form_present':False,'post_status':403,'response_written':False},'PAIEMENT_ORACLE')
    need(mutation['mutant_observed']['post_status']==200 and mutation['mutant_observed']['response_written'] is True,'PAIEMENT_MUTATION_REELLE')
    need(sorted(recipe['parallel_statuses'])==[200,403] and recipe['owned_order_count']==7,'CONCURRENCE_FICTIVE')
    need(recipe['counts_observed']==recipe['counts_expected'] and sum(recipe['counts_expected'].values())==3,'COMPTAGE_NATIF')
    need(recipe['erasure']['done'] is True and recipe['erasure']['items_removed'] is True and recipe['erasure']['items_retained'] is False,'EFFACEMENT_NATIF')
    need(all(v==0 for k,v in (recipe['observations_baseline'].items() if isinstance(recipe['observations_baseline'],dict) else []) if k.startswith('c27_')),'AUCUNE_TRANSMISSION')
    need(recipe['observations_mutant'].get('c27_mail')==recipe['observations_mutant'].get('c27_http')==1,'TRANSMISSION_MUTATION')
    mutants=receipt(names['mutations']);bound(mutants,CORE+UNIT+['wp/tests/demo/c27-horslive.php'])
    rows=mutants['mutations'];need(len(rows)==11 and {r['mutation'] for r in rows}==MUTATIONS,'MUTATIONS_EXACTES')
    for row in rows:
        log=path(PREFIX+row['log']);text=log.read_text(encoding='utf-8')
        red=re.search(r'Tests: (\d+), Assertions: (\d+), Failures: (\d+)\.',text)
        need(row['sha256']==digest(log.read_bytes()) and row['exit']==1 and row['detected'] is True and red is not None and int(red[1])==12 and int(red[3])>0 and 'ERRORS!' not in text,'MUTATION_ROUGE '+row['mutation'])
    need(mutants['count']==mutants['detected']==len(rows),'MUTATIONS_TOTAUX')
    fusion=receipt(names['fusion']);bound(fusion,CORE+['wp/outils/demo/c27-corrections.py','wp/tests/demo/c27-corrections-runtime.php'])
    alltrue(fusion['checks'],FUSION,'FUSION_CONTROLES');alltrue(fusion['restoration'],RESTORATION,'FUSION_RESTAURATION');alltrue(fusion['cleanup'],FUSION_CLEANUP,'FUSION_NETTOYAGE')
    need(fusion['error'] is None and fusion['business_preserved'] is True and fusion['owned_orders']==8,'FUSION_METIER')
    ev=fusion['evidence'];need(set(ev)==FUSION-{'aucune_transmission'},'FUSION_PREUVES_EXACTES')
    i1=ev['I1_corrige'];bad1=ev['I1_mutant'];i2=ev['I2_corrige'];bad2=ev['I2_mutant']
    need(i1['pass'] is True and i1['sql_faults']==1 and i1['source_previous_preserved'] is True and i1['answer_present'] is False and i1['refused'] is True,'I1_LECTURE_FIABLE')
    need(bad1['sql_faults']==1 and bad1['source_previous_preserved'] is False and bad1['answer_present'] is True and bad1['result'] is True,'I1_MUTANT_REEL')
    need(i2['sql_faults']==1 and i2['source_present'] is True and i2['result']['done'] is False and i2['result']['items_retained'] is True,'I2_LECTURE_FIABLE')
    need(bad2['sql_faults']==1 and bad2['source_present'] is True and bad2['result']['done'] is True and bad2['result']['items_retained'] is False,'I2_MUTANT_REEL')
    failedDelete=ev['deletefail_corrige'];final=ev['finalfail_corrige']
    need(failedDelete['source_present'] is True and failedDelete['result']['done'] is False and failedDelete['result']['items_retained'] is True,'I2_EFFACEMENT_REFUSE')
    need(final['sql_reads']==3 and final['sql_faults']==1 and final['result']['done'] is False and final['result']['items_retained'] is True,'I2_RELECTURE_FINALE')
    good=ev['M1_corrige'];bad=ev['M1_mutant']
    need(good['pass'] is True and good['old_POST_status']==403 and good['old_POST_wrote_answer'] is False and good['old_POST_wrote_source'] is False and good['seen']['etat']=='effacee','M1_POST_REFUSE')
    need(bad['old_POST_status']==200 and bad['old_POST_wrote_answer'] is True and bad['old_POST_wrote_source'] is True,'M1_MUTANT_REEL')
    prep=receipt(names['prepare']);need(prep['exit']==0 and digest(path(PREFIX+prep['log']).read_bytes())==prep['sha256'] and 'image verifiee sha256:' in path(PREFIX+prep['log']).read_text(encoding='utf-8'),'IMAGE_REBUILD')
    regression=receipt(names['regression']);bound(regression,CORE+UNIT)
    need(regression['exit']==0 and len(regression['results'])==1,'REJEU_EXECUTE')
    result=regression['results'][0]
    need(result['pass'] is True and result['failures']==result['errors']==result['skipped']==0 and result['tools']['failures']==0,'REJEU_VERT')
    text=path(PREFIX+regression['log']).read_text(encoding='utf-8')
    need(digest(path(PREFIX+regression['log']).read_bytes())==regression['sha256'],'REJEU_LOG_EMPREINTE')
    totals={'tests':0,'assertions':0,'failures':0,'errors':0,'skipped':0};c27cases=[]
    for package,xml in re.findall(r'T01 JUNIT BEGIN ([^\n]+)\n(.*?)T01 JUNIT END',text,re.S):
        suite=ET.fromstring(xml.strip()).find('testsuite')
        for key in totals:totals[key]+=int(suite.attrib[key])
        c27cases += [row for row in suite.iter('testcase') if 'Acquisition' in row.attrib.get('class','')]
    need(all(result[k]==v for k,v in totals.items()) and len(c27cases)==12,'REJEU_JUNIT_RECALCULE')
    cases={r.attrib['name'] for r in c27cases}
    need({'testPremiereLectureSourceEnEchecAnnuleLaDeclarationSansEcraser','testEffacementPremiereLectureSourceEnEchecResteIncompletPuisReprend','testEffacementCacheVideEmpoisonneEtSuppressionEnEchecNeDitPasDone','testEffacementRelectureFinaleSourceEnEchecNeDitPasDone','testPropositionVueSeuleEffaceeRefuseUnAncienFormulaire'}<=cases,'FUSION_TESTS_DECOUVERTS')
    need('T01 CLEANUP : absence verifiee' in text,'REJEU_NETTOYAGE')
    need(all(f['lot'] in {'A-31','A-32'} for f in result['packets']['failures']),'PAQUET_HORS_SCOPE_INATTENDU')
    seed=receipt(names['seed']);need(seed['choices']==CHOICES and seed['idempotent'] is True and seed['existing_nonvolatile_options_preserved'] is True and seed['volatile_options_excluded']==['_transient_timeout_wcs_woocommerce_active_version'],'LISTE_DEMO')
    need(all(v is True for k,v in seed['restoration_except_new_setting'].items() if k!='options_metier'),'SEED_AUCUN_PROFIL_OU_COMMANDE_CHANGE')
    final=receipt(names['readback']);bound(final,CORE+['wp/outils/demo/c27-readback.py'])
    need(final['baseline_receipt']==names['recipe'] and final['configuration']==CHOICES and final['answers']==final['seen']==[],'FINAL_CONFIG_SANS_DONNEES_RECETTE')
    need(set(final['remote_hashes'])=={n.removeprefix('wp/') for n in CORE},'FINAL_FICHIERS')
    for name,sha in final['remote_hashes'].items():need(sha==digest(path('wp/'+name).read_bytes()),'FINAL_SOURCE_DISTANTE')
    need(final['temporary_files'] and all(v is False for v in final['temporary_files'].values()),'FINAL_TEMPORAIRES_RETIRES')
    need(set(final['preserved_rows'])==RESTORATION-{'options_metier'} and all(v is True for v in final['preserved_rows'].values()),'FINAL_ETAT_INITIAL_EXACT')
    style=load(path(PREFIX+names['style']));need(style['totals']['errors']==0,'STYLE_PSR12_SANS_ERREUR')
    counts={'unit_tests':12,'unit_assertions':80,'native_checks':len(NATIVE)+len(RECIPE)+len(FUSION),'source_mutations':len(rows),'live_mutations':5,'global_tests':result['tests'],'global_assertions':result['assertions'],'tool_checks':result['tools']['checks'],'foreign_packet_failures':len(result['packets']['failures'])}
    need(packet['counts']==counts,'TOTAUX_RECALCULES')
    return {'gates':gates,**counts}


def main():
    if len(sys.argv)!=1:raise SystemExit('C27 : aucun argument attendu')
    print('C27 PASS '+json.dumps(validate(ROOT,load(ROOT/PREFIX/'correction-final-V2.json')),ensure_ascii=False,sort_keys=True))
if __name__=='__main__':main()
