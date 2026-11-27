"""Transport borné B13, réutilisable par les lots suivants sans mutation du socle."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path
import b11
import c29
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'production/B-13'
FILES = ['plugins/imagine-site/Navigation.php']
BLOCK = "// B13 — menu natif enrichi sans corps d’article.\nrequire_once __DIR__ . '/Navigation.php';\nNavigation::register();\n\n"
HEADING = '## B-13 — menu principal et menu étendu'
wp, php, guard = b11.wp, b11.php, b11.guard

def sources(owner):
    paths = [ROOT/'wp'/n for n in owner.FILES]
    prefix = owner.OUT.name.replace('-', '').lower()
    for pat in [f'wp/outils/demo/{prefix}*', f'wp/tests/demo/{prefix}*', f'wp/plugins/imagine-site/tests/*{prefix.upper()}*']:
        paths.extend(p for p in ROOT.glob(pat) if p.is_file())
    paths.extend([ROOT/'wp/outils/demo/b13.py', ROOT/'wp/tests/demo/b13-contract.py', owner.OUT/'verifier.py'])
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if p.is_file()}

def save(owner, name, data):
    owner.OUT.mkdir(exist_ok=True)
    with (owner.OUT/(name+'.json')).open('x', encoding='utf-8') as f:
        json.dump({'scope': 'imagine-test-demo', **data}, f, ensure_ascii=False, indent=2)

def runtime(owner, name):
    identity = guard()
    before = c29.state()
    src = (ROOT/'wp/tests/demo'/f"{owner.OUT.name.replace('-', '').lower()}-runtime.php").read_text(encoding='utf-8').split('<?php', 1)[1]
    code = 'global $wpdb;$wpdb->query("START TRANSACTION");try{eval('+php(src)+');}finally{$wpdb->query("ROLLBACK");wp_cache_flush();}'
    r = b11.b10.b09.b08.c25.b06.profils.b00.wp('eval', code, check=False)
    after = c29.state()
    save(owner, name, {'identity': identity, 'native': r, 'before': before, 'after': after, 'restored': before == after, 'sources': sources(owner)})
    print(json.dumps({'native': r, 'restored': before == after}, ensure_ascii=False))
    assert r['code'] == 0 and not r['stderr'] and before == after

def install(owner, name):
    identity = guard()
    names = owner.FILES + ['plugins/imagine-site/imagine-site.php']
    old = wp('$o=[];foreach('+php(names)+' as $n){$p=WP_CONTENT_DIR."/".$n;$o[$n]=is_file($p)?hash_file("sha256",$p):null;}echo wp_json_encode($o);')
    for n in owner.FILES:
        current = hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest()
        pre = getattr(owner, 'PREIMAGES', {}).get(n)
        assert old[n] in [None, current, pre], 'Fichier distant divergent : '+n
    boot = (ROOT/'wp/plugins/imagine-site/imagine-site.php').read_bytes()
    assert old[names[-1]] in [hashlib.sha256(boot).hexdigest(), hashlib.sha256(boot.replace(owner.BLOCK.encode(), b'', 1)).hexdigest()], 'Bootstrap distant divergent'
    private = b11.private(name, {'hashes': old})
    for n in names:
        b11.upload(n, (ROOT/'wp'/n).read_bytes())
    import b06
    actual = b06.hashes(names)
    assert actual == {n: hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in names}
    save(owner, name, {'identity': identity, 'before': old, 'readback': actual, 'private_snapshot': private})
    print('Copie démo et readback exact', len(names))

def gate(owner, action, name):
    command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT/'wp/tests'/({'image':'preparer-image.ps1', 'replay':'rejouer.ps1'}[action]))]
    with (owner.OUT/(name+'.log')).open('xb') as f:
        r = subprocess.run(command, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
    save(owner, name, {'command': command, 'exit': r.returncode, 'log': name+'.log'})
    print('\n'.join((owner.OUT/(name+'.log')).read_text(encoding='utf-8', errors='replace').splitlines()[-10:]))
    assert r.returncode == 0

if __name__ == '__main__':
    owner = sys.modules[__name__]
    OUT.mkdir(exist_ok=True)
    {'native': runtime, 'install': install, 'image': lambda o,n:gate(o,'image',n), 'replay': lambda o,n:gate(o,'replay',n)}[sys.argv[1]](owner, sys.argv[2])
