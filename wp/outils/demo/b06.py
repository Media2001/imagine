"""B06 : cible fictive gardée, installation additive et reçus immuables V2."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys, os, tempfile
sys.dont_write_bytecode = True
import b05
ROOT, wp, profils, hashes, state = b05.ROOT, b05.wp, b05.profils, b05.hashes, b05.state
PROOF = ROOT / 'production/B-06'
NAMES = ['plugins/imagine-site/' + n for n in ('CooperateursRegles.php', 'Cooperateurs.php', 'imagine-site.php')]
BLOCK = "require_once __DIR__ . '/CooperateursRegles.php';\nrequire_once __DIR__ . '/Cooperateurs.php';\nCooperateurs::register();\n\n"

def save(label, data):
    assert label.endswith('-V2') and label.replace('-', '').isalnum()
    PROOF.mkdir(parents=True, exist_ok=True)
    p = PROOF / (label + '.json')
    assert not p.exists(), p
    p.write_text(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(), scope='imagine-test-demo', **data), ensure_ascii=False, indent=2), encoding='utf-8')

def guard():
    site = profils.guard('imagine-test-demo')
    expected = hashlib.sha256((ROOT/'wp/outils/demo/imagine-demo-offline.php').read_bytes()).hexdigest()
    assert hashes(['mu-plugins/imagine-demo-offline.php'])['mu-plugins/imagine-demo-offline.php'] == expected
    guards = wp('''$m=apply_filters('pre_wp_mail',null,[]);$h=apply_filters('pre_http_request',false,[],'https://example.org');$p=apply_filters('woocommerce_available_payment_gateways',['fictif'=>true]);echo wp_json_encode(['mail'=>$m===false,'http'=>is_wp_error($h)&&$h->get_error_code()==='imagine_demo_offline','paiements'=>$p===[]]);''')
    assert guards == {'mail':True,'http':True,'paiements':True}
    return {'site':site['slug'], 'url':site['url'], 'guards':guards, 'offline_sha256':expected}

def baseline(label):
    save(label, {'identity':guard(), 'state':state(), 'sources':hashes(NAMES)})

def private_snapshot(label, payload=None):
    """Préimage durable PRIVÉE avant mutation ; jamais de session dans le dépôt."""
    if payload is None:
        payload = wp('''global $wpdb;echo wp_json_encode(['users'=>$wpdb->get_results("SELECT * FROM {$wpdb->users} ORDER BY ID",ARRAY_A),'meta'=>$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} ORDER BY umeta_id",ARRAY_A),'options'=>$wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name LIKE 'imagine_%' OR option_name='cron' ORDER BY option_id",ARRAY_A),'pages'=>$wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE post_type='page' ORDER BY ID",ARRAY_A)]);''')
    folder = Path(tempfile.mkdtemp(prefix='b06-private-', dir=os.environ['TMPDIR']))
    path = folder/'snapshot.json'
    raw = json.dumps({'label':label,'scope':'imagine-test-demo','payload':payload},ensure_ascii=False).encode('utf-8')
    with path.open('xb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    os.chmod(path, 0o600)
    assert path.read_bytes() == raw
    return {'file':folder.name+'/snapshot.json','sha256':hashlib.sha256(raw).hexdigest(),'private':True}

def deploy(label):
    identity = guard()
    prior = hashes(NAMES)
    base = json.loads((PROOF/'baseline-V2.json').read_text(encoding='utf-8'))['sources']
    for n in NAMES[:-1]:
        allowed = {base[n], hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest()}
        for p in PROOF.glob('deploy*-V2.json'):
            allowed.add(json.loads(p.read_text(encoding='utf-8'))['sources'][n])
        assert prior[n] in allowed, 'Dérive: '+n
    # Bootstrap partagé : relire les octets frais distants avant remplacement minimal.
    bootstrap = NAMES[-1]
    remote = wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/'+bootstrap+'"));')
    local = (ROOT/'wp'/bootstrap).read_text(encoding='utf-8')
    assert remote.count(BLOCK) == 1, 'Bloc B06 absent : aucune réécriture du bootstrap partagé'
    before = state()
    private_snapshot(label)
    for n in NAMES[:-1]:
        profils.b00.upload(n, (ROOT/'wp'/n).read_bytes())
    actual = hashes(NAMES)
    assert actual == {**{n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in NAMES[:-1]}, NAMES[-1]:prior[NAMES[-1]]}
    assert before == state()
    save(label, {'identity':identity, 'sources':actual, 'state_preserved':True})

def runtime(label, case='attribute', mutation=''):
    guard()
    filename = 'b06-space.php' if case == 'space' else ('b06-settings.php' if case == 'settings' else 'b06-runtime.php')
    target = 'imagine-demo-build/' + filename
    source = ROOT/'wp/tests/demo'/filename
    profils.b00.upload(target, source.read_bytes())
    assert hashes([target])[target] == hashlib.sha256(source.read_bytes()).hexdigest()
    before = state()
    snapshot = private_snapshot(label)
    p = profils.b00.wp('eval', '$GLOBALS["imagine_b06_case"]='+json.dumps(case)+';$GLOBALS["imagine_b06_mutation"]='+json.dumps(mutation)+';require WP_CONTENT_DIR."/'+target+'";',check=False)
    data = json.loads(p['stdout'])
    data.update(exit=p['code'], stderr=p['stderr'], state_preserved=state()==before, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), private_snapshot=snapshot)
    save(label, data)
    print(json.dumps(data, ensure_ascii=False))
    assert not data['failures'] and not data['exit'] and not data['stderr'] and data['state_preserved']

def seed(label):
    guard()
    target = 'imagine-demo-build/b06-seed.php'
    source = ROOT/'wp/outils/demo/b06-seed.php'
    profils.b00.upload(target, source.read_bytes())
    assert hashes([target])[target] == hashlib.sha256(source.read_bytes()).hexdigest()
    data = wp('require WP_CONTENT_DIR."/'+target+'";')
    reread = wp('$out=[];foreach(Imagine\\Site\\Cooperateurs::ids() as $id){$p=get_post($id);$out[]=["id"=>$id,"path"=>wp_parse_url(get_permalink($id),PHP_URL_PATH),"title"=>$p->post_title,"content"=>$p->post_content,"parent"=>$p->post_parent];}echo wp_json_encode($out);')
    assert len(reread) == len(data['pages']) == 5 and all(p['content'] == '' for p in reread)
    assert sorted((p['id'],p['path'],p['title']) for p in reread) == sorted((p['id'],p['path'],p['title']) for p in data['pages'])
    save(label, {'fixture':data,'readback':reread})

if __name__=='__main__':
    assert sys.argv[1] in ('baseline','deploy','runtime','seed')
    globals()[sys.argv[1]](*sys.argv[2:])
