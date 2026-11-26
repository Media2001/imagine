"""Préparation C23 HORS commande visiteur : sessions natives éphémères, restaurées.
La commande c23.py reçoit son contexte sur stdin, ne fait que des GET vers la démo.
Ce lanceur n'utilise aucun identifiant/mot de passe et ne fait aucun POST HTTP.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import argparse
import base64
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
import profils
import b05
from b00_fixtures import fixture_data, dummy_pdf
ROOT = profils.b00.ROOT
PROOF = ROOT / 'production/C-23'
wp = b05.wp


def php(value):
    return 'json_decode(base64_decode("'+base64.b64encode(json.dumps(value).encode()).decode()+'"),true)'


def inventory():
    value = wp(Path(__file__).with_name('c23-inventaire.php').read_text(encoding='utf-8').split('<?php',1)[1])
    value['issue_title'] = next(p['title'] for p in value['issues'] if p['id']==value['issue'])
    labels = {i['slug']:i['label'] for i in fixture_data()['issues']}
    for i in value['issues']:
        i['pdf_marker'] = 'Numero '+labels[i['slug']]+' - PDF factice'
    value['pdf_sha256'] = hashlib.sha256(dummy_pdf(labels[value['issue_slug']])).hexdigest()
    value['pdf_hashes'] = {str(i['id']):hashlib.sha256(dummy_pdf(labels[i['slug']])).hexdigest() for i in value['issues']}
    return value


def metadata_snapshot(ids, article):
    return wp('''global $wpdb;$ids='''+php(ids)+''';$out=[];
$out['usermeta']=$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE user_id IN (".implode(',',array_map('intval',$ids)).") AND meta_key IN ('session_tokens','_woocommerce_persistent_cart_1','_last_update','wc_last_active') ORDER BY umeta_id",ARRAY_A);
$out['options']=$wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name IN ('imagine_decouverte_reglages','imagine_decouverte_relecture') ORDER BY option_id",ARRAY_A);
$out['postmeta']=$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->postmeta} WHERE post_id=%d AND meta_key='imagine_reserve' ORDER BY meta_id",'''+str(article)+'''),ARRAY_A);
echo wp_json_encode($out);''')


def restore(snapshot, ids, article):
    # Réécrit les lignes exactes préexistantes, IDs/autoload et valeurs sérialisées compris.
    wp('''global $wpdb;$old='''+php(snapshot)+''';$ids='''+php(ids)+''';
$tables=['usermeta'=>[$wpdb->usermeta,'umeta_id'], 'options'=>[$wpdb->options,'option_id'], 'postmeta'=>[$wpdb->postmeta,'meta_id']];
foreach($tables as $kind=>[$table,$pk]){
if($kind==='usermeta'){$where="user_id IN (".implode(',',array_map('intval',$ids)).") AND meta_key IN ('session_tokens','_woocommerce_persistent_cart_1','_last_update','wc_last_active')";}
elseif($kind==='options'){$where="option_name IN ('imagine_decouverte_reglages','imagine_decouverte_relecture')";}
else{$where="post_id='''+str(article)+''' AND meta_key='imagine_reserve'";}
$beforeIds=array_column($old[$kind],$pk);$extra=$beforeIds?' AND '.$pk.' NOT IN ('.implode(',',array_map('intval',$beforeIds)).')':'';
if($wpdb->query("DELETE FROM $table WHERE $where".$extra)===false){throw new RuntimeException('C23 restauration refusée.');}
foreach($old[$kind] as $row){$existing=$wpdb->get_var($wpdb->prepare("SELECT $pk FROM $table WHERE $pk=%d",$row[$pk]));
$result=$existing?$wpdb->update($table,$row,[$pk=>$row[$pk]]):$wpdb->insert($table,$row);
if($result===false){throw new RuntimeException('C23 restauration refusée.');}}
}
foreach($ids as $id){clean_user_cache($id);wp_cache_delete($id,'user_meta');}
clean_post_cache('''+str(article)+''');wp_cache_delete('alloptions','options');wp_cache_delete('notoptions','options');
foreach(['imagine_decouverte_reglages','imagine_decouverte_relecture'] as $key){wp_cache_delete($key,'options');}
echo 'true';''')


def validate_discovery(f):
    policy, exhausted = f.get('discovery_policy', {}), f.get('discovery')
    if policy.get('ouverture') != 'premiere_lecture' or not policy.get('numeros'):
        raise ValueError('Prérequis découverte incompatible : politique livrée fermée ou sans numéro ; aucun réglage forcé')
    if not exhausted or exhausted.get('reglages') != policy:
        raise ValueError('Prérequis découverte incompatible : personnage à préparer durablement selon les réglages livrés')
    if policy.get('forme') != 'articles' or len(exhausted.get('articles', [])) < policy.get('nombre', 1):
        raise ValueError('Prérequis découverte incompatible : personnage non épuisé en articles')
    if f.get('discovery_relecture') != 'fermee':
        raise ValueError('Prérequis découverte incompatible : relecture livrée non fermée ; aucun réglage forcé')


def prepare(f):
    validate_discovery(f)
    return create_sessions(f)


def create_sessions(f):
    # Authentification seule, également utilisée par la recette B06 séparée.
    mapping = {'connecte-sans-abonnement':'V-INSCRIT','decouverte-epuisee':'V-DEC-FIN',
               'acheteur-autre-numero':'P-NUMERO','abonne-actif':'A-CARTE'}
    mapping.update(f.get('additional_publics',{}))
    return wp('''$mapping='''+php({p:f['users'][k] for p,k in mapping.items()})+''';$out=[];
foreach($mapping as $public=>$id){$expiration=time()+7200;$token=WP_Session_Tokens::get_instance($id)->create($expiration);
$logged=wp_generate_auth_cookie($id,$expiration,'logged_in',$token);$auth=wp_generate_auth_cookie($id,$expiration,'auth',$token);
$_COOKIE[LOGGED_IN_COOKIE]=$logged;wp_set_current_user($id);
$out[$public]=['id'=>$id,'cookie'=>LOGGED_IN_COOKIE.'='.$logged.'; '.AUTH_COOKIE.'='.$auth.'; tk_ai='.bin2hex(random_bytes(16)),'nonce'=>wp_create_nonce('wp_rest')];}
echo wp_json_encode($out);''')


def invoke(context, label):
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
    result = subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('c23.py')),label],
        input=json.dumps(context), text=True, encoding='utf-8', capture_output=True, env=env, cwd=ROOT, timeout=240)
    # Le contexte secret n'est ni fichier ni argv ni reçu. Seule la sortie expurgée est sauvée.
    (PROOF/(label+'.txt')).write_text(result.stdout+result.stderr,encoding='utf-8')
    print(result.stdout, end='',flush=True)
    if result.stderr:
        print('stderr du vérificateur : '+result.stderr,flush=True)
    return result.returncode


def run(label, mutation=False):
    profils.guard('imagine-test-demo')
    PROOF.mkdir(parents=True,exist_ok=True)
    f = inventory()
    ids = list(f['users'].values())
    before = b05.state()
    original = metadata_snapshot(ids,f['article'])
    receipt = dict(scope='imagine-test-demo',at=datetime.now(timezone.utc).isoformat(),label=label,
                   mutation=mutation,primary_command='python -B wp/outils/demo/c23.py '+label,
                   auth='sessions natives temporaires hors commande principale; aucun mot de passe ni POST')
    receipt['sources_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in [ROOT/'wp/outils/demo',ROOT/'wp/tests/demo'] for p in folder.glob('c23*') if p.is_file()}
    code=1
    try:
        sessions = prepare(f)
        f = inventory()
        (PROOF/'inventaire-source.json').write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf-8')
        context={'fixture':f,'sessions':sessions}
        prepared = b05.state()
        if mutation:
            # Mutation éditoriale bornée : ouvrir le seul article témoin T4, pas le paywall.
            assert len(original['postmeta'])==1 and original['postmeta'][0]['meta_value']=='1'
            wp('update_post_meta('+str(f['article'])+',"imagine_reserve","0");echo "true";')
            assert wp('echo wp_json_encode(get_post_meta('+str(f['article'])+',"imagine_reserve",true));')=='0'
        code = invoke(context,label)
        receipt['command_exit']=code
        if not mutation:
            receipt['business_unchanged_during_GETs'] = prepared == b05.state()
        else:
            record=json.loads((PROOF/(label+'.json')).read_text(encoding='utf-8'))
            receipt['mutation_red_detected']=code==1 and any(r['name']=='article' and r['public']=='anonyme' and r['leak'] for r in record['results'])
    finally:
        restore(original,ids,f['article'])
        restored = metadata_snapshot(ids,f['article'])
        receipt['metadata_restored_exactly'] = restored == original
        after = b05.state()
        receipt['profiles_and_scheduled_actions_restored_exactly'] = before == after
        receipt['schedule_before'] = before['schedule_business']
        receipt['schedule_after'] = after['schedule_business']
        receipt['native_before_sha256'] = hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest()
        receipt['native_after_sha256'] = hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest()
        (PROOF/(label+'-restauration.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    assert receipt['metadata_restored_exactly'] and receipt['profiles_and_scheduled_actions_restored_exactly'], 'C23 restauration divergente'
    if mutation:
        assert receipt['mutation_red_detected'], 'C23 mutation non détectée'
        return 0
    assert receipt['business_unchanged_during_GETs'], 'C23 GET a modifié un état métier'
    return code


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label',default='matrice')
    parser.add_argument('--mutation',action='store_true',help='HORS commande GET : ouverture provisoire du témoin, strictement restaurée')
    args=parser.parse_args()
    import re
    assert re.fullmatch('[a-z0-9-]+',args.label)
    raise SystemExit(run(args.label,args.mutation))
