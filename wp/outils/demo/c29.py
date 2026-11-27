"""C29: bounded local pure/native acceptance, unique fictitious demo."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'production/C-29'
OUT.mkdir(exist_ok=True)
BLOCK = "// C29 — projection en lecture seule, aucun connecteur.\nrequire_once __DIR__ . '/ContactBrevoRegles.php';\nrequire_once __DIR__ . '/ContactBrevo.php';\nContactBrevo::register();\n\n"
FILES = ['plugins/imagine-site/'+n for n in ['ContactBrevoRegles.php','ContactBrevo.php','imagine-site.php']]

def save(label, data):
    with (OUT/(label+'.json')).open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def docker(*args):
    return subprocess.run(['wsl.exe','-d','Ubuntu','--','docker',*args],capture_output=True,encoding='utf-8')

def pure(label):
    r = docker('run','--rm','--pull','never','--network','none','--read-only',
        '--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly',
        '--entrypoint','php','imagine-tests-t01:1','/repo/wp/tests/demo/c29-pure.php')
    save(label, {'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    print(r.stdout,r.stderr)
    return r.returncode

def native(label):
    import b11
    identity = b11.guard()
    before = b11.state()
    source = (ROOT/'wp/tests/demo/c29-runtime.php').read_text(encoding='utf-8').split('<?php',1)[1]
    expected = (ROOT/'wp/tests/demo/c29-attendus.php').read_text(encoding='utf-8').split('<?php',1)[1]
    source = source.replace("require __DIR__ . '/c29-attendus.php'", 'eval('+b11.php(expected)+')')
    code = 'global $wpdb;$wpdb->query("START TRANSACTION");try{eval('+b11.php(source)+');}finally{$wpdb->query("ROLLBACK");wp_cache_flush();}'
    r = b11.b10.b09.b08.c25.b06.profils.b00.wp('eval',code,check=False)
    restored = b11.state() == before
    save(label, {'identity':identity,'native':r,'business_preserved':restored})
    print(json.dumps(r,ensure_ascii=False)); assert restored
    return r['code']

def deploy(label):
    import b11
    identity=b11.guard(); before=b11.state()
    old=b11.wp('$o=[];foreach('+b11.php(FILES)+' as $n){$p=WP_CONTENT_DIR."/".$n;$o[$n]=is_file($p)?hash_file("sha256",$p):null;}echo wp_json_encode($o);')
    raw=(ROOT/'wp'/FILES[-1]).read_bytes()
    assert raw.count(BLOCK.encode())==1
    allowed={hashlib.sha256(raw).hexdigest(),hashlib.sha256(raw.replace(BLOCK.encode(),b'',1)).hexdigest()}
    assert old[FILES[-1]] in allowed, 'Bootstrap divergent'
    for n in FILES:
        b11.upload(n,(ROOT/'wp'/n).read_bytes())
    import b06
    actual=b06.hashes(FILES)
    assert actual=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in FILES}
    assert before==b11.state()
    save(label,{'identity':identity,'before':old,'readback':actual,'business_preserved':True})
    print('C29 readback exact',len(actual))

if __name__ == '__main__':
    if sys.argv[1]=='deploy': deploy(sys.argv[2]); raise SystemExit(0)
    if sys.argv[1]=='native': raise SystemExit(native(sys.argv[2]))
    if sys.argv[1]=='pure': raise SystemExit(pure(sys.argv[2]))
    if sys.argv[1]=='inspect':
        r=docker('run','--rm','--pull','never','--network','none','--read-only','--entrypoint','php','imagine-tests-t01:1','-r','echo getcwd(),PHP_EOL; foreach(["/opt","/opt/t01"] as $p){if(is_dir($p)){echo $p,":",implode(",",array_diff(scandir($p),[".",".."])),PHP_EOL;}}')
        print(r.stdout,r.stderr)
