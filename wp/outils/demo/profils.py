"""C09 — profils natifs fictifs, cible unique, aucun paiement externe."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import construire as b00
import json


def catalogue():
    rows = json.loads(Path(__file__).with_name('c09-profils.json').read_text(encoding='utf-8'))
    for row in rows:
        row['login'] = row['code'].lower() if row['compte'] else None
    return rows


def validate_target(slug):
    if not isinstance(slug, str) or slug != 'imagine-test-demo':
        raise ValueError('Voie 2 : seul imagine-test-demo est autorisé')


def merge_credentials(original):
    import copy
    import secrets
    merged = copy.deepcopy(original)
    accounts = merged.setdefault('c09_accounts', {})
    for row in catalogue():
        if row['compte']:
            account = accounts.setdefault(row['code'], {'login': row['login'], 'password': secrets.token_urlsafe(24)})
            if account.get('login') != row['login'] or len(account.get('password', '')) < 24:
                raise ValueError('Identifiants C09 existants invalides ; aucun remplacement silencieux')
    return merged


def guard(slug):
    validate_target(slug)
    site = b00.request_api('GET', '/api/sites/' + slug)
    validate_target(site['slug'])
    if site['status'] != 'running' or site['url'].rstrip('/') != 'http://192.168.129.32:8085':
        raise RuntimeError('Cible voie 2 non démarrée ou adresse différente')
    state = json.loads(b00.wp('eval', 'echo wp_json_encode(["env"=>wp_get_environment_type(),"demo"=>get_option("imagine_demo_site"),"home"=>home_url()]);')['stdout'])
    if state != {'env': 'local', 'demo': slug, 'home': site['url'].rstrip('/')}:
        raise RuntimeError('La garde locale fictive refuse cette exécution')
    return site


def preserve():
    code = '''$out=["b00"=>get_option("imagine_demo_manifest"),"c08"=>get_option("imagine_c08_fixture"),"users"=>[],"subs"=>[],"members"=>[]];
$f=$out["c08"];foreach($f["users"] as $k=>$id){$u=get_userdata($id);$out["users"][$k]=[$u->ID,$u->user_login,$u->user_email,$u->roles];}
foreach($f["subscriptions"] as $k=>$id){$s=wcs_get_subscription($id);$out["subs"][$k]=[$id,$s->get_status(),$s->get_customer_id(),$s->get_date("start"),$s->get_date("end"),$s->get_date("next_payment"),$s->get_meta("_imagine_acces_grace_debut"),$s->get_meta("_imagine_acces_grace_fin")];}
foreach($f["memberships"] as $k=>$id){$m=wc_memberships_get_user_membership($id);$out["members"][$k]=[$id,$m->get_status(),$m->get_user_id(),$m->get_plan_id(),$m->get_start_date(),$m->get_end_date("mysql",false),get_post_meta($id,"_subscription_id",true)];}
ob_start();require WP_CONTENT_DIR . "/imagine-demo-build/b00-snapshot.php";$out["snapshot_b00"]=json_decode(ob_get_clean(),true);echo wp_json_encode($out);'''
    return json.loads(b00.wp('eval', code)['stdout'])


def run(slug='imagine-test-demo', label='installation', readback_only=False):
    import hashlib
    import os
    from datetime import datetime, timezone
    site = guard(slug)
    proof_dir = b00.ROOT / 'production/C-09'
    proof_dir.mkdir(parents=True, exist_ok=True)
    before = preserve()
    files = {'imagine-demo-build/c09-runtime.php': b00.ROOT / 'wp/tests/demo/c09-runtime.php',
             'imagine-demo-build/c09-calendar.php': Path(__file__).with_name('c09-calendar.php'),
             'imagine-demo-build/c12-profils.php': Path(__file__).with_name('c12-profils.php'),
             'imagine-demo-build/c12-seed.php': Path(__file__).with_name('c12-seed.php'),
             'imagine-demo-build/c09-profils.json': Path(__file__).with_name('c09-profils.json')}
    if not readback_only:
        path = b00.validate_credentials_path(Path.home() / '.imagine-demo/identifiants.json')
        if not path.is_file():
            raise RuntimeError('Fichier privé B00 absent ; aucune création hors de B00')
        base = json.loads(path.read_text(encoding='utf-8'))
        credentials = merge_credentials(base)
        path.write_text(json.dumps(credentials, ensure_ascii=False, indent=2), encoding='utf-8')
        os.chmod(path, 0o600)
        # Le pipe privé est le même que B00 ; rien de secret dans argv ou preuves.
        c08_path = Path.home() / '.imagine-demo/c08-identifiants.json'
        if c08_path.is_file():
            credentials['c08_accounts'] = json.loads(c08_path.read_text(encoding='utf-8'))['accounts']
        if b00.remote('seed-secret', secret=credentials)['code']:
            raise RuntimeError('Transmission privée C09 impossible')
        files['imagine-demo-build/c09-seed.php'] = Path(__file__).with_name('c09-seed.php')
    hashes = {}
    for target, source in files.items():
        data = source.read_bytes()
        b00.upload(target, data)
        hashes[target] = hashlib.sha256(data).hexdigest()
    verify = '$names=json_decode(' + json.dumps(json.dumps(list(files))) + ',true);$out=[];foreach($names as $name){$p=WP_CONTENT_DIR . "/" . $name;if(str_ends_with($p,".php")){token_get_all(file_get_contents($p),TOKEN_PARSE);}$out[$name]=hash_file("sha256",$p);}echo wp_json_encode($out);'
    actual = json.loads(b00.wp('eval', verify)['stdout'])
    if actual != hashes:
        raise RuntimeError('Readback fichiers C09 divergent')
    if not readback_only:
        b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c09-seed.php";')
    # Processus distincts : lecture des objets réellement persistés, non des retours save().
    native = b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c09-runtime.php";', check=False)
    native_data = json.loads(native['stdout'])
    after = preserve()
    c08_result = b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c08-runtime.php";', check=False)
    c08_data = json.loads(c08_result['stdout'])
    record = {'scope': slug, 'at': datetime.now(timezone.utc).isoformat(), 'url': site['url'], 'files_sha256': actual,
              'before': before, 'after': after, 'preserved_b00_c08': before == after,
              'native': native_data, 'c08_regression': c08_data, 'native_exit': native['code'],
              'status': 'VERIFIED' if not native['code'] and not c08_result['code'] and before == after else 'FAILED'}
    (proof_dir / (label + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'scope': slug, 'label': label, 'status': record['status'], 'total': native_data['total'],
                      'failures': native_data['failures'], 'c08_total': c08_data['total'],
                      'c08_failures': c08_data['failures'], 'preserved_b00_c08': before == after}, ensure_ascii=False))
    if record['status'] != 'VERIFIED':
        raise RuntimeError('Recette C09 échouée ; voir la preuve ciblée')
    return record


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', default='imagine-test-demo')
    parser.add_argument('--preuve', choices=['installation', 'relance', 'reset', 'readback'], default='installation')
    parser.add_argument('--readback-only', action='store_true')
    args = parser.parse_args()
    run(args.site, args.preuve, args.readback_only)
