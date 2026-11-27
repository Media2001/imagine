"""Vérificateur B11 sans argument ; --live ajoute uniquement des lectures du site fictif."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'wp/outils/demo'))
import b11


def verify(live=False):
    out=b11.OUT
    load=lambda n:json.loads((out/(n+'.json')).read_text(encoding='utf-8'))
    manifest=load('reception-corrections-V2')
    assert manifest['scope']=='imagine-test-demo'
    assert manifest['sources']==b11.sources(),'Sources modifiées après réception complémentaire'
    assert all(hashlib.sha256((out/n).read_bytes()).hexdigest()==h for n,h in manifest['evidence'].items()),'Preuve complémentaire modifiée'
    assert all(hashlib.sha256((out/n).read_bytes()).hexdigest()==h for n,h in manifest['historical_receipts'].items()),'Historique modifié'
    r=load('corrections-final-V2');native=load('corrections-natif-V2');image=load('corrections-image-V2');replay=load('corrections-rejeu-V2')
    details=load('corrections-final-V2-details')
    if not manifest['ready']:
        assert not (out/'PRET').exists(),'PRET interdit pendant blocage'
        assert r['error'] is not None or r['failures'] or not all(r['checks'].values()),'Blocage sans preuve rouge'
        assert all(r['cleanup'].values()),'Restauration non prouvée'
        if live:
            b11.guard()
            assert b11.b10.b09.b08.c25.b06.hashes(b11.FILES)=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in b11.FILES}
            assert b11.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/mu-plugins/b11-observer.php")&&!file_exists(WP_CONTENT_DIR."/mu-plugins/b11-no-persist.php")&&get_option("imagine_b11_observations",null)===null);')
        print(json.dumps({'B11':'BLOCKED','receipt':'reception-corrections-V2.json','mode':'live-readonly' if live else 'offline','ready':False,'recipe_error':r['error'],'failed':[k for k,v in r['checks'].items() if not v],'blockers':manifest['blockers'],'restoration_verified':True},ensure_ascii=False))
        return False
    checks={}
    def check(k,v):
        checks[k]=bool(v)
        if not v:raise AssertionError(k)
    check('recette_complete',r['error'] is None and r['total']==len(r['checks']) and r['failures']==0 and all(r['checks'].values()))
    check('persistance_changement_effacement_OFF_ON',all(r['checks'].get(k) for k in ['save_0_readback','save_1_readback','effacement_0_readback','effacement_1_readback']))
    check('editeurs_livres_et_reload',set(details['editors'])=={'11','3454'} and all(e.get('forced') is False and not e.get('error') and 'reload_values' in e for e in details['editors'].values()))
    check('autres_reglages_conserves',bool(details['settings_evidence']) and {x['mode'] for x in details['settings_evidence']}=={'0','1'} and all(x['others_unchanged'] and len(x['names'])>3 for x in details['settings_evidence']))
    check('mutations_non_persistance_UI',all(r['mutations'].get('no_persist_'+i,{}).get('persistence_control_failed') for i in ['11','3454']))
    check('mutation_gravatar_public_avant_transport',r['mutations']['gravatar_public']['zero_tiers_failed'] and r['mutations']['gravatar_public']['event']['blocked_before_transport'])
    check('restauration_relue',all(r['cleanup'].values()) and r['cleanup']['business_preserved'])
    check('sources_apres_derniere_ecriture',r['sources']==b11.sources() and native['sources']==b11.sources())
    check('deux_reglages_sans_reseau_public',set(r['network'])=={'0','1'} and all(x['browser_requests'] and not x['external'] for x in r['network'].values()))
    check('32_sorties_etanches_non_vides',len(r['surfaces'])==32 and all(x['ok'] and x['surface_present'] and not x['leak'] and x['bytes']>0 for x in r['surfaces']))
    check('garde_article_mutation_native',r['mutations']['garde_article']['leak'] and not r['mutations']['garde_article']['ok'])
    check('garde_audio_mutation_native',r['mutations']['garde_audio']['status']==200 and r['mutations']['garde_audio']['bytes']==48044)
    check('temoins_C26_complets',r['C26_witness_inventory']['count']==32 and r['mutations']['detecteur_reponse_seulement']=={'count':36,'detected':36,'not_source_mutations':True})
    witness=ROOT/r['C26_witness_inventory']['file']
    check('inventaire_C26_inchange',hashlib.sha256(witness.read_bytes()).hexdigest()==r['C26_witness_inventory']['sha256'])
    check('pas_appel_B11',r['checks']['save_render_B11_zero_HTTP_oembed_mail'] and r['checks']['tentatives_ambiance_qualifiees_bloquees_B00'])
    n=native['native'];data=json.loads(n['stdout'])
    check('natif_23',n['code']==0 and not n['stderr'] and data['total']==len(data['checks'])==23 and all(data['checks'].values()) and native['business_preserved'])
    text=(out/'corrections-unitaire-V2.log').read_text(encoding='utf-8')
    check('PHPUnit_4_34',bool(re.search(r'OK \(4 tests, 34 assertions\)',text)))
    check('image_reconstruite',image['exit']==0 and 'image verifiee sha256:' in (out/image['log']).read_text(encoding='utf-8'))
    replay_text=(out/replay['log']).read_text(encoding='utf-8')
    check('rejeu_parent_reel',replay['exit']==0 and bool(re.search(r'REJEU : [1-9][0-9]* tests, .* PASS',replay_text)))
    for path in ['NOTE.md','A-VOIR.md']:
        check(path,(out/path).is_file() and len((out/path).read_text(encoding='utf-8'))>200)
    readme=(ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    check('section_README_unique',readme.count('## B-11 — vidéos, podcasts et sommaire audio')==1)
    if live:
        b11.guard()
        actual=b11.b10.b09.b08.c25.b06.hashes(b11.FILES)
        check('live_sources_relues',actual=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in b11.FILES})
        value=b11.wp('''$f=get_option('imagine_b11_fixture');$o=['fixture'=>$f,'settings'=>Imagine\\Site\\Medias::configuration(),'audio'=>[],'observer'=>file_exists(WP_CONTENT_DIR.'/mu-plugins/b11-observer.php')];foreach([$f['issue'],$f['issue_active']] as $id){$p=Imagine\\Site\\AudioNumero::path($id);$o['audio'][]=['sha256'=>hash_file('sha256',$p),'mode'=>fileperms($p)&0777,'same_private_C11'=>dirname($p)===Imagine\\Site\\PdfNumero::directory()];}echo wp_json_encode($o);''')
        check('live_fixture_fictive',value['fixture']['fictif'] is True and value['fixture']['article']==3454 and value['fixture']['issue']==11 and value['fixture']['issue_active']==39)
        check('live_reglage_OFF_hote_fictif',value['settings']=={'hosts':['video-fictive.example.invalid'],'integration':'0'})
        check('live_deux_silences_prives',len(value['audio'])==2 and all(a=={'sha256':value['fixture']['silence_sha256'],'mode':384,'same_private_C11':True} for a in value['audio']))
        check('live_observateur_absent',value['observer'] is False)
    print(json.dumps({'B11':'PASS','mode':'live-readonly' if live else 'offline','checks':len(checks),'success':all(checks.values())},ensure_ascii=False))
    return checks

if __name__=='__main__':
    assert sys.argv[1:] in [[],['--live']]
    raise SystemExit(1 if verify(bool(sys.argv[1:])) is False else 0)
