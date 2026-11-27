"""Réception B11 selon A-FAIRE-2 du 27/11/2026 13h30, sans inventer de validation UI."""
import sys
sys.dont_write_bytecode=True
import hashlib
import importlib.util
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'wp/outils/demo'))
import b11
sys.path.insert(0,str(ROOT/'wp/tests/demo'))
import lot_reception_contract as contract
spec=importlib.util.spec_from_file_location('b11_recipe',ROOT/'wp/outils/demo/b11-recette.py')
recipe=importlib.util.module_from_spec(spec);spec.loader.exec_module(recipe)
RECEIPT='reception-contrat-V2.json'


def verify(live=False, manifest=None, require_pret=True):
    out=b11.OUT
    load=lambda n:json.loads((out/n).read_text(encoding='utf-8'))
    manifest=manifest or load(RECEIPT)
    checks={}
    def check(name, value):
        checks[name]=bool(value)
        assert value,name
    check('reception',manifest['ready'] is True and manifest['scope']=='imagine-test-demo' and manifest['policy']=='A-FAIRE-2 2026-11-27 13h30')
    contract.integrity('B11',manifest,out)
    check('sources_finales',manifest['sources']==contract.sources('B11'))
    for key in ['evidence','historical_receipts']:
        check(key,bool(manifest[key]) and all(hashlib.sha256((out/n).read_bytes()).hexdigest()==h for n,h in manifest[key].items()))
    r=load('politique1330-final-V2.json');details=load('politique1330-final-V2-details.json')
    native=load('politique1330-natif-V2.json');write=load('politique1330-ecritures-V2.json');audit=load('politique1330-editeurs-final-V2.json')
    check('recette_complete_selon_politique',r['policy']==manifest['policy'] and r['error'] is None and r['failures']==0 and r['total']==len(r['checks']) and all(r['checks'].values()))
    check('pas_UI_inventee',r['persistence_boundary']=='native-save_post-hook-not-UI' and set(details['editors'])=={'11','3454'} and all(e['kind']=='native-save_post-hook-not-UI' and e['forced'] is False for e in details['editors'].values()))
    check('champs_proposes_editeur_livre',audit['declaration_patch_required'] is False and len(audit['editors'])==2 and all(e['proposed_by_native_bridge'] for e in audit['editors']) and all(audit['checks'].values()) and audit['business_preserved'])
    check('changements_effacements_OFF_ON',all(r['checks'].get(k) for k in ['save_0_readback','save_1_readback','effacement_0_readback','effacement_1_readback']))
    w=write['native']
    check('backend_8_sur_8',len(w['checks'])==8 and all(w['checks'].values()) and write['business_exactly_restored'])
    check('deux_mutations_ecriture',len(w['mutations'])==2 and {row['id'] for row in w['mutations']}=={11,3454} and all(row['returned'] is False and row['actual']==['',''] and all(row['attempted']) for row in w['mutations']))
    settings=details['settings_evidence']
    check('formulaire_OFF_ON_16_options',len(settings)==3 and [x['mode'] for x in settings]==['0','1','0'] and all(len(x['names'])==16 and set(x['names'])==set(x['before'])==set(x['after']) for x in settings))
    check('valeurs_effectives_strictes',all(recipe.compare_options(x['before'],x['after'])=={k:x[k] for k in ['ok','absent_to_exact_default','different']} and x['ok'] for x in settings))
    expected={'imagine_decouverte_reglages','imagine_decouverte_relecture','imagine_solidaire_categories','imagine_newsletters_creation','imagine_retractation_reglages'}
    check('cinq_defauts_explicites_listes',set().union(*(set(x['absent_to_exact_default']) for x in settings))==set(manifest['absent_to_exact_default'])==expected)
    check('B11_modification_intentionnelle_exacte',all(x['after']['imagine_medias']['effective_value']=={'hosts':['video-fictive.example.invalid'],'integration':x['mode']} for x in settings))
    check('refus_hote_antislash',r['checks']['mauvais_host_POST_natif_refuse'] and r['checks']['antislash_POST_refuse_sans_perte'])
    event=r['mutations']['gravatar_public']['event']
    check('Gravatar_public_temoin',r['mutations']['gravatar_public']['zero_tiers_failed'] and event['blocked_before_transport'] and recipe.forbidden_external(event) and '/wp-admin/' not in event['origin'])
    check('OFF_ON_zero_tiers_public',set(r['network'])=={'0','1'} and all(x['browser_requests'] and not x['external'] for x in r['network'].values()))
    check('32_sorties_etanches',len(r['surfaces'])==32 and all(x['ok'] and x['surface_present'] and not x['leak'] and x['bytes']>0 for x in r['surfaces']))
    check('garde_article_mutation',r['mutations']['garde_article']['leak'] and not r['mutations']['garde_article']['ok'])
    check('garde_audio_mutation',r['mutations']['garde_audio']['status']==200 and r['mutations']['garde_audio']['bytes']==48044)
    check('C26_complet',r['C26_witness_inventory']['count']==32 and r['mutations']['detecteur_reponse_seulement']=={'count':36,'detected':36,'not_source_mutations':True})
    check('inventaire_C26_inchange',hashlib.sha256((ROOT/r['C26_witness_inventory']['file']).read_bytes()).hexdigest()==r['C26_witness_inventory']['sha256'])
    check('zero_B11_et_coupe_circuit',all(r['checks'][k] for k in ['save_render_B11_zero_HTTP_oembed_mail','tentatives_ambiance_qualifiees_bloquees_B00','toutes_tentatives_HTTP_coupees_avant_transport','seuls_gravatars_admin_bloques']))
    n=native['native'];data=json.loads(n['stdout'])
    check('natif_23_sur_23',n['code']==0 and not n['stderr'] and data['total']==len(data['checks'])==23 and all(data['checks'].values()) and native['business_preserved'])
    check('sources_apres_derniere_ecriture',all(contract.tested_sources('B11',x['sources']) for x in [r,native,write,audit]))
    check('restaurations_relues',len(r['cleanup'])==16 and all(r['cleanup'].values()) and r['cleanup']['business_preserved'])
    check('PHPUnit_4_34',bool(re.search(r'OK \(4 tests, 34 assertions\)',(out/'politique1330-unitaire-V2.log').read_text(encoding='utf-8'))))
    text=(out/'politique1330-preuves-V2.log').read_text(encoding='utf-8')
    check('unites_preuve_9','Ran 9 tests' in text and text.rstrip().endswith('OK'))
    image=load('politique1330-image-V2.json');replay=load('politique1330-rejeu-V2.json')
    check('image_reconstruite',image['exit']==0 and 'image verifiee sha256:' in (out/image['log']).read_text(encoding='utf-8'))
    check('rejeu_reel_vert',replay['exit']==0 and bool(re.search(r'REJEU : [1-9][0-9]* tests, .* PASS',(out/replay['log']).read_text(encoding='utf-8'))))
    check('limite_tete_NOTE','13h30' in (out/'NOTE.md').read_text(encoding='utf-8')[:1500] and 'UI' in (out/'NOTE.md').read_text(encoding='utf-8')[:1500])
    if require_pret:
        check('PRET',(out/'PRET').is_file() and RECEIPT in (out/'PRET').read_text(encoding='utf-8'))
    if live:
        b11.guard()
        names=[p.removeprefix('wp/') for p in manifest['sources'] if p.startswith(('wp/plugins/','wp/themes/')) and '/tests/' not in p]
        check('live_sources',b11.b10.b09.b08.c25.b06.hashes(names)=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in names})
        contract.live_registration('B11',b11.wp,b11.php)
        value=b11.wp('''$f=get_option('imagine_b11_fixture');$o=['fictif'=>$f['fictif'],'settings'=>Imagine\\Site\\Medias::configuration(),'audio'=>[],'probes_absent'=>!file_exists(WP_CONTENT_DIR.'/mu-plugins/b11-observer.php')&&!file_exists(WP_CONTENT_DIR.'/mu-plugins/b11-no-persist.php')&&get_option('imagine_b11_observations',null)===null];foreach([$f['issue'],$f['issue_active']] as $id){$p=Imagine\\Site\\AudioNumero::path($id);$o['audio'][]=hash_file('sha256',$p)===$f['silence_sha256']&&(fileperms($p)&0777)===0600&&dirname($p)===Imagine\\Site\\PdfNumero::directory();}echo wp_json_encode($o);''')
        check('live_fictif_OFF_audio_prive',value['fictif'] is True and value['settings']=={'hosts':['video-fictive.example.invalid'],'integration':'0'} and value['audio']==[True,True])
        check('live_sondes_absentes',value['probes_absent'])
    print(json.dumps({'B11':'PASS','receipt':RECEIPT,'mode':'live-readonly' if live else 'offline','checks':len(checks),'success':all(checks.values()),'UI_save_verified':False,'effective_options':16,'backend_witness_checks':len(w['checks']),'contract':'owned-files + unique exact own block + bounded own README'},ensure_ascii=False))
    return checks


if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    verify(bool(sys.argv[1:]))
