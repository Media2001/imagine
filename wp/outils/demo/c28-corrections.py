"""C28 corrections only: two-file guarded deploy and transactional native proof."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import c28

FILES = ['plugins/imagine-site/PacksThematiques.php', 'plugins/imagine-site/AchatsNumeros.php']

def deploy(label):
    identity = c28.guard()
    before = c28.state()
    old = c28.wp('$out=[];foreach('+c28.php(FILES)+' as $n){$out[$n]=file_get_contents(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($out);')
    known = [json.loads(p.read_text(encoding='utf-8')).get('readback', {}) for pattern in ['installation-*.json', 'correction-installation*.json'] for p in c28.OUT.glob(pattern) if not p.name.endswith('-avant.json')]
    expected = {n: hashlib.sha256((c28.ROOT/'wp'/n).read_bytes()).hexdigest() for n in FILES}
    for n in FILES:
        assert hashlib.sha256(old[n].encode()).hexdigest() in [expected[n], *[k.get(n) for k in known]], n
    snap = c28.private(label, {'files': old, 'business': before})
    for n in FILES:
        c28.upload(n, (c28.ROOT/'wp'/n).read_bytes())
    actual = c28.hashes(FILES)
    assert actual == expected and c28.state() == before
    c28.save(label, {'identity': identity, 'private_snapshot': snap, 'readback': actual, 'business_preserved': True})
    print('C28 correction: two files deployed and read back; no B11 write.')

def native(label):
    c28.guard()
    before = c28.state()
    source = (c28.ROOT/'wp/tests/demo/c28-corrections-runtime.php').read_text(encoding='utf-8').split('<?php', 1)[1]
    code = "global $wpdb;if(wp_using_ext_object_cache()){throw new RuntimeException('Cache externe');}$wpdb->query('START TRANSACTION');try{eval("+c28.php(source)+");}finally{$wpdb->query('ROLLBACK');wp_cache_flush();}"
    r = c28.b11.b10.b09.b08.c25.b06.profils.b00.wp('eval', code, check=False)
    after = c28.state()
    c28.save(label, {'native': r, 'business_preserved': before == after, 'before': before, 'after': after, 'sources': c28.sources()})
    print(json.dumps({'native': r, 'business_preserved': before == after}, ensure_ascii=False))
    assert r['code'] == 0 and not r['stderr'] and before == after
    data = json.loads(r['stdout'])
    assert data['total'] == len(data['checks']) and not data['failures'] and all(data['checks'].values())

if __name__ == '__main__':
    assert sys.argv[1] in ['deploy', 'native']
    globals()[sys.argv[1]](sys.argv[2])
