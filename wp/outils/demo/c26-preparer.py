"""C26 préparation séparée, fixtures natives temporaires et restauration relue."""
import sys
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import c26
import b08
import b06
ROOT = b06.ROOT
PROOF = ROOT / 'production/C-26'
spec = importlib.util.spec_from_file_location('c23_preparation_c26', Path(__file__).with_name('c23-preparer.py'))
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)
wp, php = b06.wp, prep.php


def scratch():
    p = Path(os.environ.get('TMPDIR') or str(Path(os.environ.get('LOCALAPPDATA', str(Path.home()/'AppData/Local'))) / 'hermes/cache/scratch'))
    p.mkdir(parents=True, exist_ok=True)
    return p


def save(name, data):
    PROOF.mkdir(exist_ok=True)
    p = PROOF / (name+'.json')
    if p.exists():
        raise ValueError('C26 reçu déjà présent')
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def fixture(operation, data):
    source = (ROOT/'wp/tests/demo/c26-fixture.php').read_text(encoding='utf-8').split('<?php', 1)[1]
    return wp('$GLOBALS["c26_operation"]='+php(operation)+';$GLOBALS["c26_input"]='+php(data)+';eval('+php(source)+');')


def own_sources():
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ['wp/outils/demo', 'wp/tests/demo'] for p in (ROOT/folder).glob('c26*') if p.is_file()}


def restoration(saved, ids, pages):
    # Supprimer exclusivement les nouvelles données de fixture via les APIs natives.
    owner = next(int(r['ID']) for r in saved['users'] if r['user_login'] == 'v-dec')
    fixture('cleanup', {'owner':owner, 'old_private_ids':[int(p['ID']) for p in saved['posts'] if p['post_type'] in ['imagine_inscription','imagine_sujet']]})
    prep.restore_cooperator(pages)
    rows = [r for r in saved['usermeta'] if int(r['user_id']) in ids]
    wp('''global $wpdb;$ids='''+php(ids)+''';$old='''+php(rows)+''';
$all=$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE user_id IN (".implode(',',array_map('intval',$ids)).")",ARRAY_A);
$prior=array_column($old,'umeta_id');foreach($all as $r){if(!in_array($r['umeta_id'],$prior,true)){$wpdb->delete($wpdb->usermeta,['umeta_id'=>$r['umeta_id']]);}}
foreach($old as $r){$ok=$wpdb->replace($wpdb->usermeta,$r);if($ok===false){throw new RuntimeException('C26 restauration meta impossible');}}
foreach($ids as $id){clean_user_cache($id);wp_cache_delete($id,'user_meta');}echo 'true';''')


def privacy(extension, f, mutation=''):
    audiences = wp('$ids='+php(f['users'])+';$out=[];foreach($ids as $k=>$id){$out[$k]=get_userdata($id)->user_email;}echo wp_json_encode($out);')
    publics = c26.c23.audience_order(f)+['abonne-actif']
    mapping = {'connecte-sans-abonnement':'V-INSCRIT',c26.c23.discovery_audience(f):'V-DEC-FIN','acheteur-autre-numero':'P-NUMERO','abonne-actif':'A-CARTE', **f['additional_publics']}
    by_public = {p:audiences[mapping[p]] if p in mapping else 'c26-'+p+'@example.org' for p in publics}
    owner_email = wp('echo wp_json_encode(get_userdata('+str(extension['owner'])+')->user_email);')
    by_public['inverse-proprietaire'] = owner_email
    raw = fixture('privacy', {'owner':extension['owner'], 'audiences':by_public, 'mutation':mutation})
    rows = []
    for row in raw:
        positive = row['public'] == 'inverse-proprietaire'
        verdict = c26.privacy_assess(row['payload'], [extension['markers'][row['family']]] if positive else list(extension['markers'].values()), positive)
        rows.append(dict(public=row['public'], family=row['family'], name='privacy-'+row['family'],
                         positive=positive, payload_sha256=hashlib.sha256(json.dumps(row['payload'],sort_keys=True).encode()).hexdigest(), **verdict))
    return dict(scope='imagine-test-demo', route='registered-native-exporter-callbacks', mutation=mutation,
                total=len(rows), failures=sum(not r['ok'] for r in rows), leaks=sum(r['leak'] for r in rows), results=rows)


def run(label, mutations=False):
    if not re.fullmatch('[a-zA-Z0-9-]+', label) or any(PROOF.glob(label+'*')):
        raise ValueError('C26 nom de reçu neuf requis')
    identity = b06.guard()
    # Lire le bootstrap actuel et les dépendances livrées ; ne rien installer ni réécrire.
    names = ['plugins/imagine-site/'+n for n in ['imagine-site.php','Agenda.php','AgendaConfidentialite.php','Personnalisation.php','PersonnalisationConfidentialite.php','Retractation.php','RetractationConfidentialite.php','Cooperative.php','Soutenir.php','Sujet.php','SujetConfidentialite.php','Cooperateurs.php']]
    remote = b06.hashes(names)
    assert remote == {n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in names}, 'C26 sources live différentes'
    before = b06.state()
    saved = b08.snapshot()
    f = prep.inventory()
    owner = wp('echo wp_json_encode((int)get_option("imagine_c09_fixture")["users"]["V-DEC"]);')
    assert owner and owner not in f['users'].values()
    ids = sorted(set(list(f['users'].values())+[owner]))
    pages = prep.cooperator_snapshot(f)
    assert not wp('echo wp_json_encode(wc_get_orders(["created_via"=>"c26-fixture","limit"=>-1,"return"=>"ids"]));'), 'C26 fixture précédente non nettoyée'
    prep.PRIVATE_ROOT = scratch()
    private = prep.private_snapshot('c26-'+label, {'database':saved, 'business':before, 'pages':pages})
    save(label+'-avant', {'scope':'imagine-test-demo','business':before,'sources':own_sources(), 'live_source_hashes':remote, 'private_snapshot':private})
    result = {'scope':'imagine-test-demo','identity':identity,'private_snapshot':private}
    try:
        extension = fixture('seed', {'owner':owner})
        extension['account_path'] = f['account_path']
        save(label+'-extension', extension)
        prep.seed_cooperator_witness(pages)
        f = prep.inventory()
        prep.validate_discovery(f)
        f['extension'] = extension
        sessions = prep.create_sessions(f)
        save(label+'-inventaire', f)
        privacy_normal = privacy(extension, f)
        save(label+'-privacy', privacy_normal)
        if mutations:
            mutated = []
            for family in c26.FAMILIES:
                receipt = privacy(extension, f, family)
                save(label+'-mutation-'+family, receipt)
                assert receipt['failures'] and receipt['leaks'] and any(r['family']==family and r['leak'] and not r['ok'] for r in receipt['results'])
                mutated.append(family)
            # Mutation B06 effective de fixture d'autorisation persistée ; réponse HTTP réelle.
            user = f['users']['V-INSCRIT']
            wp('update_user_meta('+str(user)+',"imagine_cooperateur",["cooperateur"=>true,"source"=>"administration","date_utc"=>"2026-11-26T00:00:00Z"]);echo "true";')
            try:
                route = c26.c23.cooperator_routes(f)[0]
                session = sessions['connecte-sans-abonnement']
                response = c26.c23.fetch(route['path'], {'Cookie':session['cookie'],'X-WP-Nonce':session['nonce']})
                verdict = c26.c23.assess_response(response,[route['cooperator_marker']],present=route['present'])
                assert verdict['leak'] and not verdict['ok']
                save(label+'-mutation-cooperateurs', {'scope':'imagine-test-demo','total':1,'results':[dict(name=route['name'], public='connecte-sans-abonnement',status=response[0],bytes=len(response[2]),**verdict)],'persisted_fixture':True})
                mutated.append('cooperateurs')
            finally:
                prior = [r for r in saved['usermeta'] if int(r['user_id'])==user and r['meta_key']=='imagine_cooperateur']
                wp('''global $wpdb;$wpdb->delete($wpdb->usermeta,['user_id'=>'''+str(user)+''','meta_key'=>'imagine_cooperateur']);foreach('''+php(prior)+''' as $r){$wpdb->insert($wpdb->usermeta,$r);}wp_cache_delete('''+str(user)+''','user_meta');echo 'true';''')
            public_page = next(p for p in extension['pages'] if p['path']=='/soutenir/')
            original_page = next(p for p in saved['posts'] if int(p['ID'])==public_page['id'])
            assert original_page['post_content'] == ''
            primary = 'CONTENU_FICTIF_RESERVE_DEMO-2026-T4_1'
            wp('''global $wpdb;if($wpdb->query($wpdb->prepare("UPDATE {$wpdb->posts} SET post_content=%s WHERE ID=%d AND BINARY post_content=%s",'<p>'''+primary+'''</p>','''+str(public_page['id'])+''',''))!==1){throw new RuntimeException('C26 mutation publique refusée');}clean_post_cache('''+str(public_page['id'])+''');echo 'true';''')
            try:
                route = next(r for r in c26.routes(extension) if r['path']==public_page['path'])
                response = c26.c23.fetch(route['path'])
                verdict = c26.assess(route,response,[primary])
                assert verdict['leak'] and not verdict['ok']
                save(label+'-mutation-cooperative', {'scope':'imagine-test-demo','total':1,'results':[dict(name=route['name'],public='anonyme',status=response[0],bytes=len(response[2]),**verdict)],'persisted_fixture':True})
                mutated.append('cooperative')
            finally:
                restored_page = wp('''global $wpdb;$wpdb->update($wpdb->posts,['post_content'=>''],['ID'=>'''+str(public_page['id'])+''']);clean_post_cache('''+str(public_page['id'])+''');echo wp_json_encode($wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->posts} WHERE ID=%d",'''+str(public_page['id'])+'''),ARRAY_A));''')
                assert restored_page == original_page, 'C26 page publique non restaurée'
            result['mutations_detected'] = mutated
        prepared = b06.state()
        env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
        p = subprocess.run([sys.executable,'-B',str(ROOT/'wp/outils/demo/c26.py'),label],input=json.dumps({'fixture':f,'sessions':sessions}),capture_output=True,text=True,encoding='utf-8',env=env,cwd=ROOT,timeout=900)
        (PROOF/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
        print(p.stdout[-2000:]+p.stderr,flush=True)
        result.update(command_exit=p.returncode,privacy_green=privacy_normal['failures']==0,
                      business_unchanged_during_GETs=prepared==b06.state())
    finally:
        restoration(saved, ids, pages)
        current = b08.snapshot()
        exact = {k:current[k]==saved[k] for k in ['users','usermeta','posts','postmeta','comments','commentmeta','wc_orders','wc_orders_meta','wc_order_addresses','wc_order_operational_data','woocommerce_order_items','woocommerce_order_itemmeta','navigation']}
        options = lambda db:[r for r in db['options'] if r['option_name'].startswith('imagine_') or r['option_name']=='cron']
        exact['business_options'] = options(current)==options(saved)
        after = b06.state()
        result.update(exact_restoration=exact,business_preserved=before==after,
                      before_sha256=hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),
                      after_sha256=hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest(),
                      live_sources_preserved=b06.hashes(names)==remote)
        if not all(exact.values()):
            result['private_after'] = prep.private_snapshot('c26-'+label+'-after',current)
        save(label+'-restauration', result)
        print(json.dumps({'restoration':exact,'business':result['business_preserved']},ensure_ascii=False),flush=True)
    assert all(exact.values()) and result['business_preserved'] and result['live_sources_preserved'], 'C26 restauration non prouvée'
    assert result['command_exit']==0 and result['privacy_green'] and result['business_unchanged_during_GETs'], 'C26 matrice rouge'
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', required=True)
    parser.add_argument('--mutations', action='store_true')
    a = parser.parse_args()
    raise SystemExit(run(a.label, a.mutations))
