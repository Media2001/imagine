"""Scoped B12 corrections: real native routes; receipt history is append-only."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import b12
ROOT, OUT = b12.ROOT, b12.OUT
CODE = 'plugins/imagine-site/IntegrationsCorps.php'
BOOT = 'plugins/imagine-site/imagine-site.php'
OLD = "rtrim($request->get_route(), '/') !== '/oembed/1.0/proxy'"
NEW = "strcasecmp(rtrim($request->get_route(), '/'), '/oembed/1.0/proxy') !== 0"
sha = lambda raw: hashlib.sha256(raw).hexdigest()

def routes(label):
    identity = b12.guard()
    before = b12.b11.state()
    name = 'imagine-demo-build/b12-routes-runtime.php'
    assert not b12.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR.' + b12.php('/' + name) + '));')
    result = None
    try:
        b12.b11.upload(name, (ROOT/'wp/tests/demo/b12-routes-runtime.php').read_bytes())
        assert b12.b11.b10.b09.b08.c25.b06.hashes([name])[name] == sha((ROOT/'wp/tests/demo/b12-routes-runtime.php').read_bytes())
        code = '''global $wpdb;if(wp_using_ext_object_cache()){throw new RuntimeException('External cache refused');}foreach([$wpdb->posts,$wpdb->postmeta,$wpdb->options] as $table){$r=$wpdb->get_row($wpdb->prepare('SHOW TABLE STATUS WHERE Name=%s',$table),ARRAY_A);if($r['Engine']!=='InnoDB'){throw new RuntimeException('Transaction unavailable');}}$wpdb->query('START TRANSACTION');try{require WP_CONTENT_DIR.''' + b12.php('/' + name) + ''';}finally{$wpdb->query('ROLLBACK');wp_cache_flush();}'''
        result = b12.b11.b10.b09.b08.c25.b06.profils.b00.wp('eval', code, check=False)
    finally:
        b12.b11.b10.b09.remove_remote([name])
        absent = b12.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR.' + b12.php('/' + name) + '));')
        restored = before == b12.b11.state()
        b12.save(label, {'identity': identity, 'native': result, 'business_preserved': restored, 'probe_removed': absent, 'sources': b12.sources()})
    print(json.dumps(result, ensure_ascii=False))
    assert restored and absent
    return result

def deploy(label):
    identity = b12.guard()
    before = b12.b11.state()
    local = (ROOT/'wp'/CODE).read_bytes()
    old = b12.wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR.'+b12.php('/'+CODE)+'));').encode()
    assert old in [local, local.replace(NEW.encode(), OLD.encode(), 1)]
    boot = sha((ROOT/'wp'/BOOT).read_bytes())
    assert b12.b11.b10.b09.b08.c25.b06.hashes([BOOT])[BOOT] == boot
    b12.b11.upload(CODE, local)
    actual = b12.b11.b10.b09.b08.c25.b06.hashes([CODE, BOOT])
    assert actual == {CODE: sha(local), BOOT: boot}
    assert before == b12.b11.state()
    b12.save(label, {'identity': identity, 'old': sha(old), 'readback': actual, 'business_preserved': True, 'bootstrap_not_written': True})
    print('B12 class exact readback; C29 bootstrap untouched')

def mutant(label):
    b12.guard()
    before = b12.b11.state()
    local = (ROOT/'wp'/CODE).read_bytes()
    assert local.count(NEW.encode()) == 1
    assert b12.b11.b10.b09.b08.c25.b06.hashes([CODE])[CODE] == sha(local)
    try:
        raw = local.replace(NEW.encode(), OLD.encode(), 1)
        b12.b11.upload(CODE, raw)
        assert b12.b11.b10.b09.b08.c25.b06.hashes([CODE])[CODE] == sha(raw)
        result = routes(label + '-rejet')
        assert result['code'] != 0 and 'B12_ROUTE_CASE' in result['stderr']
        data = json.loads(result['stdout'])
        assert any(c['cache'] == 'ancien' and '<iframe' in c['data'].get('html', '') for c in data['cases'])
        assert any(c['cache'] == 'absent' and c['attempts'] > 0 for c in data['cases'])
    finally:
        b12.b11.upload(CODE, local)
        actual = b12.b11.b10.b09.b08.c25.b06.hashes([CODE])[CODE]
        assert actual == sha(local)
        restored = before == b12.b11.state()
        b12.save(label, {'source_mutation': 'exact pre-fix case-sensitive comparison on actual demo', 'source_restored': actual == sha(local), 'business_preserved': restored})
        assert restored
    assert routes(label + '-retabli')['code'] == 0

if __name__ == '__main__':
    action, label = sys.argv[1:]
    result = globals()[action](label)
    if action == 'routes':
        raise SystemExit(result['code'])
