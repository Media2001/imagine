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
import tempfile
from datetime import datetime, timezone
import profils
import b05
import c23
from b00_fixtures import fixture_data, dummy_pdf
ROOT = profils.b00.ROOT
PROOF = ROOT / 'production/C-23'
wp = b05.wp
PRIVATE_ROOT = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData/Local'))) / 'hermes/cache/scratch'


def private_snapshot(label, payload):
    PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix='c23-private-', dir=PRIVATE_ROOT))
    path = folder / 'snapshot.json'
    raw = json.dumps({'scope':'imagine-test-demo','label':label,'payload':payload},ensure_ascii=False).encode('utf-8')
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    os.chmod(path, 0o600)
    assert path.read_bytes() == raw
    return {'file':folder.name+'/snapshot.json','sha256':hashlib.sha256(raw).hexdigest(),'private':True}


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
    if policy.get('ouverture') == 'fermee':
        return
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
    mapping = {'connecte-sans-abonnement':'V-INSCRIT',c23.discovery_audience(f):'V-DEC-FIN',
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


def cooperator_snapshot(f):
    ids = [p['id'] for p in f['cooperator_pages']]
    return wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE ID IN (".implode(\',\','+php(ids)+').") ORDER BY ID",ARRAY_A));')


def seed_cooperator_witness(rows):
    if len(rows) != 5 or any(r['post_content'] != '' or r['post_excerpt'] != '' for r in rows):
        raise ValueError('B06 cinq pages vides requises ; aucun contenu existant écrasé')
    wp('''global $wpdb;$rows='''+php(rows)+''';foreach($rows as $r){
$sql=$wpdb->prepare("UPDATE {$wpdb->posts} SET post_content=%s WHERE ID=%d AND BINARY post_content=%s AND BINARY post_excerpt=%s",'<p>C23_COOP_TEMOIN_'.$r['ID'].'</p>',$r['ID'],'','');
if($wpdb->query($sql)!==1){throw new RuntimeException('C23 B06 témoin non écrit.');}clean_post_cache((int)$r['ID']);}echo 'true';''')


def restore_cooperator(rows):
    wp('''global $wpdb;$rows='''+php(rows)+''';foreach($rows as $r){
$current=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->posts} WHERE ID=%d",$r['ID']),ARRAY_A);
if($current===$r){continue;}$expected=$r;$expected['post_content']='<p>C23_COOP_TEMOIN_'.$r['ID'].'</p>';
if($current!==$expected){throw new RuntimeException('C23 B06 dérive concurrente, restauration refusée.');}
if($wpdb->update($wpdb->posts,['post_content'=>$r['post_content']],['ID'=>$r['ID']])===false){throw new RuntimeException('C23 B06 restauration impossible.');}clean_post_cache((int)$r['ID']);}echo 'true';''')


def run(label, mutation=False, b06_only=False, discovery_recipe=False):
    import re
    if not re.fullmatch('[a-zA-Z0-9-]+', label):
        raise ValueError('Nom de reçu refusé')
    if any((PROOF/(label+suffix)).exists() for suffix in ['.json','.txt','.md','-restauration.json']):
        raise ValueError('Reçu existe déjà ; nouveau nom requis')
    import b06
    b06.guard()
    PROOF.mkdir(parents=True,exist_ok=True)
    f = inventory()
    ids = list(f['users'].values())
    before = b05.state()
    original = metadata_snapshot(ids,f['article'])
    pages = cooperator_snapshot(f)
    private = private_snapshot(label, {'metadata':original,'pages':pages,'business':before})
    receipt = dict(scope='imagine-test-demo',at=datetime.now(timezone.utc).isoformat(),label=label,
                   coverage='recette-decouverte-ouverte-epuisee' if discovery_recipe else 'mutation-temoin' if mutation else 'B06-only' if b06_only else 'livraison',
                   private_snapshot=private, discovery_recipe=discovery_recipe,
                   mutation=mutation,primary_command='python -B wp/outils/demo/c23.py '+label,
                   auth='sessions natives temporaires hors commande principale; aucun mot de passe ni POST')
    receipt['sources_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in [ROOT/'wp/outils/demo',ROOT/'wp/tests/demo'] for p in folder.glob('c23*') if p.is_file()}
    (PROOF/(label+'-etat.json')).write_text(json.dumps({'scope':'imagine-test-demo','state':before},ensure_ascii=False,indent=2),encoding='utf-8')
    code, changed = 1, False
    try:
        if mutation or discovery_recipe:
            # Politique TEMPORAIRE : recettes nommées seulement, jamais le rejeu normal.
            changed = True
            wp('update_option("imagine_decouverte_reglages",'+php(f['discovery']['reglages'])+');update_option("imagine_decouverte_relecture","fermee");echo "true";')
            f = inventory()
        if not b06_only:
            validate_discovery(f)  # Avant la moindre écriture normale, même avant les sessions.
        changed = True
        seed_cooperator_witness(pages)
        sessions = create_sessions(f)
        f = inventory()
        (PROOF/(label+'-inventaire.json')).write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf-8')
        context={'fixture':f,'sessions':sessions,'coverage':receipt['coverage']}
        if mutation:
            assert len(original['postmeta'])==1 and original['postmeta'][0]['meta_value']=='1'
            wp('update_post_meta('+str(f['article'])+',"imagine_reserve","0");echo "true";')
            assert wp('echo wp_json_encode(get_post_meta('+str(f['article'])+',"imagine_reserve",true));')=='0'
        prepared = b05.state()
        code = invoke(context,label)
        receipt['command_exit']=code
        if discovery_recipe:
            record=json.loads((PROOF/(label+'.json')).read_text(encoding='utf-8'))
            case=next(r for r in record['results'] if r['name']=='c12-epuisee' and r['public']=='decouverte-epuisee')
            receipt['discovery_open_exhausted_proved']=case['ok'] and not case['leak'] and record['discovery']['exhausted_played'] is True
        receipt['business_unchanged_during_GETs'] = prepared == b05.state()
        if mutation:
            record=json.loads((PROOF/(label+'.json')).read_text(encoding='utf-8'))
            receipt['mutation_red_detected']=code==1 and any(r['name']=='article' and r['public']=='anonyme' and r['leak'] for r in record['results'])
    except ValueError as error:
        if changed:
            raise
        message = str(error)
        receipt.update(command_exit=1, prerequisite=message, no_sessions_created=True,
                       business_unchanged_during_GETs=True)
        summary='ETANCHEITE : 0 contrôles, 0 fuites — FAIL ; '+message
        (PROOF/(label+'.json')).write_text(json.dumps({'scope':'imagine-test-demo','coverage':'livraison',
            'total':0,'leaks':0,'failures':1,'results':[],'prerequisite':message,'summary':summary,
            'command_sha256':receipt['sources_sha256']['wp/outils/demo/c23.py']},ensure_ascii=False,indent=2),encoding='utf-8')
        (PROOF/(label+'.txt')).write_text(summary+'\n',encoding='utf-8')
        (PROOF/(label+'-inventaire.json')).write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf-8')
        print(summary)
    finally:
        if changed:
            # Indépendants : une restauration défaillante ne saute jamais l'autre.
            try:
                restore_cooperator(pages)
            finally:
                restore(original,ids,f['article'])
        restored = metadata_snapshot(ids,f['article'])
        receipt['metadata_restored_exactly'] = restored == original
        receipt['cooperator_pages_restored_exactly'] = cooperator_snapshot(f) == pages
        receipt['cooperator_pages_sha256'] = hashlib.sha256(json.dumps(pages,sort_keys=True).encode()).hexdigest()
        after = b05.state()
        receipt['profiles_and_scheduled_actions_restored_exactly'] = before == after
        receipt['schedule_before'] = before['schedule_business']
        receipt['schedule_after'] = after['schedule_business']
        receipt['native_before_sha256'] = hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest()
        receipt['native_after_sha256'] = hashlib.sha256(json.dumps(after,sort_keys=True).encode()).hexdigest()
        (PROOF/(label+'-restauration.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    assert receipt['metadata_restored_exactly'] and receipt['profiles_and_scheduled_actions_restored_exactly'] and receipt['cooperator_pages_restored_exactly'], 'C23 restauration divergente'
    if mutation:
        assert receipt['mutation_red_detected'], 'C23 mutation non détectée'
        return 0
    assert receipt['business_unchanged_during_GETs'], 'C23 GET a modifié un état métier'
    if discovery_recipe:
        assert receipt['discovery_open_exhausted_proved'], 'C23 découverte ouverte épuisée non prouvée'
    return code


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label',default='livraison-arbitrage1930')
    parser.add_argument('--mutation',action='store_true',help='HORS commande GET : ouverture provisoire du témoin, strictement restaurée')
    parser.add_argument('--b06-seul',action='store_true',help='Recette B06 seule, ne vaut jamais livraison C23 complète')
    parser.add_argument('--decouverte-ouverte-epuisee',action='store_true',help='Recette séparée : ouvre temporairement la découverte, vérifie V-DEC-FIN épuisé, restaure exactement')
    args=parser.parse_args()
    import re
    assert re.fullmatch('[a-zA-Z0-9-]+',args.label)
    assert sum([args.mutation,args.b06_seul,args.decouverte_ouverte_epuisee]) <= 1
    raise SystemExit(run(args.label,args.mutation,args.b06_seul,args.decouverte_ouverte_epuisee))
