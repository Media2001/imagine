"""B12: only the existing fictitious demo; native probes roll back."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path
import b11
ROOT = b11.ROOT
OUT = ROOT/'production/B-12'
OUT.mkdir(exist_ok=True)
wp, php, guard = b11.wp, b11.php, b11.guard
FILES = ['plugins/imagine-site/IntegrationsCorps.php', 'plugins/imagine-site/imagine-site.php']
BLOCK = "// B12 — aucune résolution externe du corps sans consentement.\nrequire_once __DIR__ . '/IntegrationsCorps.php';\nIntegrationsCorps::register();\n\n"

def save(label, value):
    with (OUT/(label+'.json')).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

def sources():
    files = [ROOT/'wp'/n for n in FILES]
    for pat in ['wp/outils/demo/b12*', 'wp/tests/demo/b12*', 'wp/plugins/imagine-site/tests/IntegrationsCorpsB12*']:
        files.extend(p for p in ROOT.glob(pat) if p.is_file())
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files)) if p.is_file()}

def runtime(label, mutant=False):
    identity = guard()
    before = b11.state()
    name = 'imagine-demo-build/b12-runtime.php'
    assert not wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR . '+php('/'+name)+'));')
    result = None
    try:
        b11.upload(name, (ROOT/'wp/tests/demo/b12-runtime.php').read_bytes())
        assert b11.b10.b09.b08.c25.b06.hashes([name])[name] == hashlib.sha256((ROOT/'wp/tests/demo/b12-runtime.php').read_bytes()).hexdigest()
        code = '''global $wpdb;if(wp_using_ext_object_cache()){throw new RuntimeException('External cache refused');}foreach([$wpdb->posts,$wpdb->postmeta,$wpdb->options] as $table){$r=$wpdb->get_row($wpdb->prepare('SHOW TABLE STATUS WHERE Name=%s',$table),ARRAY_A);if($r['Engine']!=='InnoDB'){throw new RuntimeException('Transaction unavailable');}}$wpdb->query('START TRANSACTION');try{$GLOBALS['b12_mutant']='''+('true' if mutant else 'false')+''';require WP_CONTENT_DIR . '''+php('/'+name)+''';}finally{$wpdb->query('ROLLBACK');wp_cache_flush();}'''
        result = b11.b10.b09.b08.c25.b06.profils.b00.wp('eval', code, check=False)
    finally:
        b11.b10.b09.remove_remote([name])
        absent = wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR . '+php('/'+name)+'));')
        restored = before == b11.state()
        save(label, {'identity': identity, 'native': result, 'business_preserved': restored, 'probe_removed': absent, 'sources': sources()})
    print(json.dumps(result, ensure_ascii=False))
    assert result['code'] == 0 and not result['stderr'] and restored and absent

def deploy(label):
    identity = guard(); before = b11.state()
    old = wp('$o=[];foreach('+php(FILES)+' as $n){$p=WP_CONTENT_DIR."/".$n;$o[$n]=is_file($p)?file_get_contents($p):null;}echo wp_json_encode($o);')
    local = {n: (ROOT/'wp'/n).read_text(encoding='utf-8') for n in FILES}
    assert old[FILES[0]] in [None, local[FILES[0]]]
    assert old[FILES[1]] in [local[FILES[1]], local[FILES[1]].replace(BLOCK, '')], 'Divergent bootstrap'
    save(label+'-before', {'identity': identity, 'hashes': {n: hashlib.sha256(s.encode()).hexdigest() if s else None for n,s in old.items()}})
    for n in FILES:
        b11.upload(n, (ROOT/'wp'/n).read_bytes())
    actual = b11.b10.b09.b08.c25.b06.hashes(FILES)
    assert actual == {n: hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in FILES}
    assert before == b11.state()
    save(label, {'identity': identity, 'readback': actual, 'business_preserved': True})
    print('B12 deployed and read back:',len(actual))

def gate(action, label):
    scripts = {'image': 'preparer-image.ps1', 'replay': 'rejouer.ps1'}
    command = ['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'wp/tests'/scripts[action])]
    log = OUT/(label+'.log')
    with log.open('xb') as stream:
        r = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    save(label, {'command': command, 'exit': r.returncode, 'log': log.name})
    print('\n'.join(log.read_text(encoding='utf-8',errors='replace').splitlines()[-15:]))
    return r.returncode

if __name__ == '__main__':
    action,label = sys.argv[1:3]
    if action == 'mutant': runtime(label, True)
    elif action in ['image','replay']: raise SystemExit(gate(action,label))
    else: globals()[action](label)
