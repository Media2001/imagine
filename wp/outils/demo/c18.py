"""C18 targeted code-only installation and read-only native probes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
sys.dont_write_bytecode = True
import c17
ROOT = c17.ROOT
PROOF = ROOT / 'production/C-18'
BLOCK = "require_once __DIR__ . '/ExtractionsRegles.php';\nrequire_once __DIR__ . '/ExtractionsNatives.php';\nrequire_once __DIR__ . '/ExtractionsAdmin.php';\nExtractionsAdmin::register();\n\n"
wp = c17.wp

def save(name, data):
    PROOF.mkdir(parents=True, exist_ok=True)
    (PROOF / (name + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def targets():
    paths = [ROOT / 'wp/plugins/imagine-site' / n for n in ('ExtractionsRegles.php', 'ExtractionsNatives.php', 'ExtractionsAdmin.php')]
    paths += sorted((ROOT / 'wp/plugins/imagine-site/extractions').glob('*.php'))
    paths += [ROOT / 'wp/plugins/imagine-site/imagine-site.php']
    return {p.relative_to(ROOT / 'wp').as_posix(): p for p in paths}

def readback():
    names = list(targets())
    actual = wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(names)) + ',true) as $n){$p=WP_CONTENT_DIR."/".$n;token_get_all(file_get_contents($p),TOKEN_PARSE);$out[$n]=hash_file("sha256",$p);}echo wp_json_encode($out);')
    assert actual == {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in targets().items()}, 'Source readback differs'
    return actual

def state():
    out = c17.state()
    out['native_fingerprints'] = wp(r'''global $wpdb;$out=[];
foreach(['users','usermeta','posts','postmeta','actionscheduler_actions','actionscheduler_logs','woocommerce_order_items','woocommerce_order_itemmeta','wc_orders','wc_order_addresses','wc_orders_meta','wc_order_operational_data'] as $suffix){
$t=$wpdb->prefix.$suffix;if($wpdb->get_var($wpdb->prepare('SHOW TABLES LIKE %s',$wpdb->esc_like($t)))!==$t){continue;}
$where=$suffix==='usermeta'?" WHERE meta_key NOT IN ('session_tokens','_woocommerce_persistent_cart_1','_last_update','wc_last_active')":'';
$rows=$wpdb->get_results("SELECT * FROM `$t`".$where,ARRAY_A);$hashes=array_map(static fn($r)=>hash('sha256',serialize($r)),$rows);sort($hashes);$out[$suffix]=['count'=>count($hashes),'sha256'=>hash('sha256',serialize($hashes))];}
$out['roles']=hash('sha256',serialize(wp_roles()->roles));echo wp_json_encode($out);''')
    return out

def deploy():
    c17.profils.guard('imagine-test-demo')
    before = state()
    prior = {}
    for name, source in targets().items():
        current = wp('$p=WP_CONTENT_DIR.' + json.dumps('/' + name) + ';echo wp_json_encode(is_file($p)?hash_file("sha256",$p):null);')
        allowed = {hashlib.sha256(source.read_bytes()).hexdigest()}
        if name.endswith('/imagine-site.php'):
            allowed.add(hashlib.sha256(source.read_text(encoding='utf-8').replace(BLOCK, '').encode()).hexdigest())
        if (PROOF / 'installation.json').is_file():
            old = json.loads((PROOF / 'installation.json').read_text(encoding='utf-8'))
            allowed.add(old['sha256_readback'].get(name))
        if current is not None and current not in allowed:
            raise RuntimeError('Source drift; no overwrite: ' + name)
        prior[name] = current
    for name, source in targets().items():
        c17.profils.b00.upload(name, source.read_bytes())
    hashes = readback()
    after = state()
    assert before == after, 'Native state changed during code-only installation'
    receipt = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo',
               'sha256_before': prior, 'sha256_readback': hashes, 'native_unchanged': before == after,
               'baseline': before, 'fixture_reset': False}
    if (PROOF / 'installation.json').is_file():
        stamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        (PROOF / ('installation-before-' + stamp + '.json')).write_bytes((PROOF / 'installation.json').read_bytes())
    save('installation', receipt)
    print('C18 code installed, exact readback; native state unchanged')

def runtime(label='runtime-final'):
    c17.profils.guard('imagine-test-demo')
    source = ROOT / 'wp/tests/demo/c18-runtime.php'
    name = 'imagine-demo-build/c18-runtime.php'
    c17.profils.b00.upload(name, source.read_bytes())
    actual = wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR.' + json.dumps('/' + name) + '));')
    assert actual == hashlib.sha256(source.read_bytes()).hexdigest()
    before = state()
    result = wp('require WP_CONTENT_DIR . "/imagine-demo-build/c18-runtime.php";')
    result['native_unchanged'] = before == state()
    save(label, result)
    print(json.dumps(result, ensure_ascii=False))
    assert result['checks'] and all(v is True for v in result['checks'].values()) and result['native_unchanged']
    return result

if __name__ == '__main__':
    if '--deploy' in sys.argv:
        deploy()
    elif '--runtime' in sys.argv:
        runtime(sys.argv[-1] if sys.argv[-1] != '--runtime' else 'runtime-final')
    else:
        c17.profils.guard('imagine-test-demo')
        save('readback', {'sha256_readback': readback(), 'state': state()})
        print('C18 exact source readback verified')
