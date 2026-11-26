"""C22: cible fictive unique, installation ciblée et reçus non écrasés."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
sys.dont_write_bytecode = True
import b05
ROOT = b05.ROOT
PROOF = ROOT / 'production/C-22'
wp, profils, php_json, state, hashes = b05.wp, b05.profils, b05.php_json, b05.state, b05.hashes
NAMES = ['plugins/imagine-site/' + n for n in ('NewslettersRegles.php','Newsletters.php','NewslettersReglages.php')]
# Shared C21/bootstrap are contract-only: never rewritten by C22 corrections.

def save(label, data):
    assert label.replace('-', '').isalnum()
    PROOF.mkdir(parents=True, exist_ok=True)
    p = PROOF / (label + '.json')
    assert not p.exists(), p
    p.write_text(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(), scope='imagine-test-demo', **data), ensure_ascii=False, indent=2), encoding='utf-8')

def remove_observer():
    import subprocess
    # Only the exact owned, hash-checked temporary observer; no chmod or sibling deletion.
    name = 'mu-plugins/imagine-c22-observer.php'
    expected = hashlib.sha256((ROOT/'wp/tests/demo/c22-observer.php').read_bytes()).hexdigest()
    assert hashes([name])[name] == expected
    code = '<?php $p="/var/www/html/wp-content/' + name + '";if(hash_file("sha256",$p)!=="' + expected + '"){exit(3);}if(!unlink($p)){exit(4);}echo "removed";'
    p = subprocess.run(['wsl.exe','-d','Ubuntu','--','docker','exec','-i','--user','root','wp-imagine-test-demo','php'],input=code,capture_output=True,text=True,encoding='utf-8')
    assert p.returncode == 0 and p.stdout == 'removed', p.stderr
    assert hashes([name])[name] is None

def baseline(label):
    save(label, {'state':state(), 'source_before':hashes(NAMES)})

def deploy(label):
    before = state()
    prior = hashes(NAMES)
    first = json.loads((PROOF/'baseline.json').read_text(encoding='utf-8'))['source_before']
    for name in NAMES:
        allowed = {first[name], hashlib.sha256((ROOT/'wp'/name).read_bytes()).hexdigest()}
        for receipt in PROOF.glob('installation-*.json'):
            allowed.add(json.loads(receipt.read_text(encoding='utf-8'))['source_readback'].get(name))
        assert prior[name] in allowed, 'Source drift: '+name
    for name in NAMES:
        profils.b00.upload(name, (ROOT / 'wp' / name).read_bytes())
    actual = hashes(NAMES)
    assert actual == {n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in NAMES}
    assert before == state()
    save(label, {'source_readback':actual, 'native_preserved':True})

def runtime(label):
    source = ROOT / 'wp/tests/demo/c22-runtime.php'
    name = 'imagine-demo-build/c22-runtime.php'
    profils.b00.upload(name, source.read_bytes())
    assert hashes([name])[name] == hashlib.sha256(source.read_bytes()).hexdigest()
    before = state()
    result = profils.b00.wp('eval', 'require WP_CONTENT_DIR."/' + name + '";', check=False)
    data = json.loads(result['stdout'])
    data.update(exit=result['code'], stderr=result['stderr'], native_preserved=state()==before)
    save(label, data)
    print(json.dumps(data,ensure_ascii=False))
    assert not data['failures'] and data['native_preserved'] and not data['exit'] and not data['stderr']

def seed(label):
    rows = [{'id':'lettre-fictive','titre':'La lettre fictive Imagine','presentation':'Les nouvelles de la rédaction de démonstration.','principale':True},
            {'id':'rencontres-fictives','titre':'Les rencontres fictives','presentation':'Des rencontres entièrement inventées pour la démonstration.','principale':False},
            {'id':'cooperateurs-fictifs','titre':'La lettre des coopérateurs fictifs','presentation':'Une lettre de démonstration pour les coopérateurs.','principale':False}]
    data = wp('$old=get_option("imagine_newsletters_catalogue",null);if($old!==null && $old!=='+php_json(rows)+')throw new Exception("Catalogue étranger");update_option("imagine_newsletters_catalogue",'+php_json(rows)+',false);$p=get_page_by_path("nos-newsletters");if(!$p){$id=wp_insert_post(["post_type"=>"page","post_status"=>"publish","post_title"=>"Nos newsletters","post_name"=>"nos-newsletters","post_content"=>"[imagine_newsletters]"],true);if(is_wp_error($id))throw new Exception("Page non créée");}else{$id=$p->ID;if($p->post_content!=="[imagine_newsletters]")throw new Exception("Page étrangère");}echo wp_json_encode(["catalogue"=>get_option("imagine_newsletters_catalogue"),"page"=>get_post($id),"auto"=>get_option("imagine_newsletters_creation","non")]);')
    assert data['catalogue']==rows and data['auto']=='non' and data['page']['post_content']=='[imagine_newsletters]'
    save(label, data)

if __name__=='__main__':
    profils.guard('imagine-test-demo')
    globals()[sys.argv[1]](sys.argv[2])
