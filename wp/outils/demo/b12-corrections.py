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
        b12.save(label, {'identity': identity, 'native': result, 'business_preserved': restored, 'probe_removed': absent, 'sources': b12.sources(), 'bootstrap_contract': b12.contract_block()})
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

def reader():
    import importlib.util
    spec = importlib.util.spec_from_file_location('b12_current', ROOT/'wp/tests/demo/b12-verifier.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def bootstrap(label):
    value = reader().bootstrap()
    b12.save(label, value)
    print(json.dumps(value))

def lint(label):
    import subprocess
    files = ['wp/plugins/imagine-site/IntegrationsCorps.php', 'wp/plugins/imagine-site/imagine-site.php', 'wp/plugins/imagine-site/tests/IntegrationsCorpsB12Test.php', 'wp/plugins/imagine-site/tests/IntegrationsCorpsB12Stubs.php', 'wp/tests/demo/b12-runtime.php', 'wp/tests/demo/b12-routes-runtime.php']
    prefix = ['wsl.exe','-d','Ubuntu','--','docker','run','--rm','--pull','never','--network','none','--read-only','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--entrypoint','php','imagine-tests-t01:1']
    rows = [subprocess.run(prefix+['-l','/repo/'+n], capture_output=True, encoding='utf-8') for n in files]
    b12.save(label, {'files': files, 'exit': max(r.returncode for r in rows), 'stdout': ''.join(r.stdout for r in rows), 'stderr': ''.join(r.stderr for r in rows)})
    assert all(r.returncode==0 and not r.stderr for r in rows)
    print('PHP syntax PASS:', len(files))

def finish(label):
    import os
    import subprocess
    from datetime import datetime, timezone
    assert label=='reception-corrections-V2' and not (OUT/(label+'.json')).exists() and not (OUT/'PRET').exists()
    for script, log in [('b12-proof-tests.py','correction-proof-legacy-V2.log'),('b12-correction-proof-tests.py','correction-proof-current-V2.log')]:
        with (OUT/log).open('xb') as stream:
            r = subprocess.run([sys.executable,'-B',str(ROOT/'wp/tests/demo'/script)], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, env={**os.environ,'PYTHONIOENCODING':'utf-8'})
        assert r.returncode==0, (OUT/log).read_text(encoding='utf-8')
    names = sorted(p.name for p in OUT.glob('correction-*') if p.is_file())
    names += ['NOTE.md','A-VOIR.md','PRET-avant-corrections-V2','reception-V2.json','reception-complement-voisins-V2.json','native-reception-V2.json','mutation-reception-V2.json']
    m = {'scope':'imagine-test-demo','ready':True,'correction_version':1,'at':datetime.now(timezone.utc).isoformat(),'sources':b12.sources(),'evidence':{n:sha((OUT/n).read_bytes()) for n in names},'routes':'correction-routes-final-V2.json','green':'correction-native-final-V2.json','mutation':'correction-mutation-verrou-final-V2.json','bootstrap':'correction-bootstrap-C29-V2.json','image':'correction-image-V2.json','replay':'correction-replay-V2.json','lint':'correction-lint-V2.json','readme_section':sha((ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').split('## B-12 — aucun appel sortant depuis le corps',1)[1].strip().encode()),'limits':['Native WP-CLI routing, not editor UI or authenticated external HTTP capture.','Business rows strictly restored; AUTO_INCREMENT can advance.','Historical B11/C28 and C29 receipts are not resealed. The C29 historical reader tracks old B12 PRET: exact bytes retained in PRET-avant-corrections-V2 and verified by the new companion.','B11 UI_save_verified=false unchanged. A31/A32 failures untouched.']}
    v = reader()
    v.verify_correction(False,m,False)
    v.verify_correction(True,m,False)
    b12.save(label,m)
    with (OUT/'PRET').open('x',encoding='utf-8') as stream:
        stream.write('B12 PRET TECHNIQUE — reception-corrections-V2.json, NOTE.md, A-VOIR.md.\nSix instructions de corrections/B-12.md vérifiées : routes natives MAJ/mixed/cache, mutation source réelle, complément C29 exact, image reconstruite et rejeu frais.\nAncien PRET conservé octet pour octet : PRET-avant-corrections-V2. Historiques non rescellés.\nNi validation visuelle, ni clôture, ni GO sur le réel.\n')
    v.verify(False)
    v.verify(True)

if __name__ == '__main__':
    action, label = sys.argv[1:]
    result = globals()[action](label)
    if action == 'routes':
        raise SystemExit(result['code'])
