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


def run_final():
    import io
    import unittest
    tests = Path(__file__).resolve().parent
    def load(name):
        spec = importlib.util.spec_from_file_location(name.replace('-', '_'), tests / (name + '.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    legacy = load('c09-verifier')
    stream = io.StringIO()
    local = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.discover(str(tests), pattern='test_c09_profils.py'))
    legacy.save('complement-local.json', {'total': local.testsRun, 'failures': len(local.failures), 'errors': len(local.errors), 'output': stream.getvalue()})
    if not local.wasSuccessful() or local.skipped:
        raise RuntimeError('Unittest C09 rouge')
    first = profils.run(label='installation')
    again = profils.run(label='relance')
    if first['native']['fixture'] != again['native']['fixture']:
        raise RuntimeError('Identifiants modifiés au rejeu')
    load('c09-reset').run()
    payments = native('final-native')
    if payments['exit']:
        raise RuntimeError('Paiements C09 rouges')
    safety = legacy.native_test('safety')
    corrections = legacy.native_test('corrections')
    readback = profils.run(label='readback', readback_only=True)
    http = load('c09-http').run()
    recipes = load('c09-strict-recipes')
    c13 = recipes.run('C13')
    b02 = recipes.run('B02')
    if c13['exit'] not in (0, 2) or b02['exit'] not in (0, 2):
        raise RuntimeError('Échec technique de recette stricte')
    secret = legacy.secret_scan()
    if secret['matches']:
        raise RuntimeError('Valeur privée détectée ; aucun secret imprimé')
    rows = profils.catalogue()
    result = {'scope': 'imagine-test-demo', 'at': datetime.now(timezone.utc).isoformat(),
        'status': 'TECHNIQUE_VERIFIE_ACCEPTATIONS_PARTIELLES' if c13['exit'] or b02['exit'] else 'VERIFIE',
        'categories': {k: [r['code'] for r in rows if r['etat'] == k] for k in ['créé', 'partiel', 'impossible']},
        'tests': {'local': local.testsRun, 'natif': readback['native']['total'], 'paiements': payments['total'],
            'securite': safety['total'], 'corrections': corrections['total'], 'HTTP': http['total'],
            'C08': readback['c08_regression']['total']},
        'strict_C13_exit': c13['exit'], 'strict_B02_exit': b02['exit'],
        'secret_scan': secret, 'ids_rejoues_identiques': True, 'B00_C08_preserves': readback['preserved_b00_c08']}
    legacy.save('complement-verification.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    if '--full' in sys.argv:
        run_final()
    else:
        if '--seed' in sys.argv:
            seed()
        result = native(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'readback')
        raise SystemExit(result['exit'])
