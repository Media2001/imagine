"""C09 complément : ciblage strict, relecture distante et résultats sous C09 seulement."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import profils

ROOT = profils.b00.ROOT
PROOF = ROOT / 'production/C-09'


def upload(source):
    target = 'imagine-demo-build/' + source.name
    data = source.read_bytes()
    profils.b00.upload(target, data)
    actual = profils.b00.wp('eval', '$p=WP_CONTENT_DIR . ' + json.dumps('/' + target) + ';token_get_all(file_get_contents($p),TOKEN_PARSE);echo hash_file("sha256",$p);')['stdout'].strip()
    if actual != hashlib.sha256(data).hexdigest():
        raise RuntimeError('Relecture divergente : ' + target)
    return target


def native(label):
    profils.guard('imagine-test-demo')
    target = upload(ROOT / 'wp/tests/demo/c09-payments.php')
    raw = profils.b00.wp('eval', 'require WP_CONTENT_DIR . ' + json.dumps('/' + target) + ';', check=False)
    if raw['stderr']:
        raise RuntimeError(raw['stderr'])
    result = json.loads(raw['stdout'])
    result['exit'] = raw['code']
    result['at'] = datetime.now(timezone.utc).isoformat()
    (PROOF / ('complement-' + label + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['exit', 'total', 'failures']}, ensure_ascii=False), flush=True)
    return result


def preserve():
    code = r'''global $wpdb;$out=[];foreach(['imagine_demo_manifest','imagine_demo_calendrier','imagine_c08_fixture'] as $key){$out[$key]=get_option($key);}$f=get_option('imagine_c08_fixture');foreach($f['users'] as $k=>$id){$u=get_userdata($id);$out['users'][$k]=[$id,$u->user_login,$u->user_email,$u->roles];}foreach($f['subscriptions'] as $k=>$id){$out['subs'][$k]=wcs_get_subscription($id)->get_data();}foreach($f['memberships'] as $k=>$id){$m=wc_memberships_get_user_membership($id);$out['members'][$k]=[$m->get_plan_id(),$m->get_status(),$m->get_end_date(),get_post_meta($id)];}$ids=array_map('intval',array_values(get_option('imagine_demo_manifest')));$out['editorial']=$wpdb->get_results('SELECT * FROM '.$wpdb->posts.' WHERE ID IN ('.implode(',',$ids).') ORDER BY ID',ARRAY_A);echo wp_json_encode($out);'''
    return json.loads(profils.b00.wp('eval', code)['stdout'])


def seed():
    profils.guard('imagine-test-demo')
    before = preserve()
    for source in [ROOT / 'wp/outils/demo/c09-profils.json', ROOT / 'wp/outils/demo/c09-seed.php']:
        if source.suffix == '.php':
            upload(source)
        else:
            data = source.read_bytes(); profils.b00.upload('imagine-demo-build/' + source.name, data)
            actual = profils.b00.wp('eval', 'echo hash_file("sha256",WP_CONTENT_DIR . "/imagine-demo-build/c09-profils.json");')['stdout'].strip()
            assert actual == hashlib.sha256(data).hexdigest()
    raw = profils.b00.wp('eval', '(static function(){require WP_CONTENT_DIR . "/imagine-demo-build/c09-seed.php";})();')
    if raw['stderr']:
        raise RuntimeError(raw['stderr'])
    after = preserve()
    if before != after:
        raise RuntimeError('B00/C08 modifiés')
    print('Seed relu ; B00/C08 préservés', flush=True)
    return json.loads(raw['stdout'])


if __name__ == '__main__':
    if '--seed' in sys.argv:
        seed()
    result = native(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'readback')
    raise SystemExit(result['exit'])
