"""C28 : site fictif unique, transport existant gardé et reçus neufs."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import b11
ROOT = b11.ROOT
OUT = ROOT/'production/C-28'
wp, php, guard, upload, state, private = b11.wp, b11.php, b11.guard, b11.upload, b11.state, b11.private
hashes = b11.b10.b09.b08.c25.b06.hashes
FILES = ['plugins/imagine-site/'+n for n in ['PacksRegles.php', 'PacksThematiques.php', 'AchatsNumeros.php', 'imagine-site.php']] + ['themes/imagine/single-product.php']
BLOCK = "// C28 — instantané du pack au paiement, décision et remboursements C14 inchangés.\nrequire_once __DIR__ . '/PacksRegles.php';\nrequire_once __DIR__ . '/PacksThematiques.php';\nPacksThematiques::register();\n\n"


def save(label, data):
    assert label.replace('-', '').isalnum()
    OUT.mkdir(exist_ok=True)
    path = OUT/(label+'.json')
    assert not path.exists(), path
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def sources():
    paths = [ROOT/'wp'/n for n in FILES]
    for pattern in ['wp/outils/demo/c28*', 'wp/tests/demo/c28*', 'wp/plugins/imagine-site/tests/PacksC28*']:
        paths.extend(p for p in ROOT.glob(pattern) if p.is_file())
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if p.is_file()}


def runtime(label):
    guard()
    before = state()
    source = (ROOT/'wp/tests/demo/c28-runtime.php').read_text(encoding='utf-8').split('<?php',1)[1]
    code = "global $wpdb;if(wp_using_ext_object_cache()){throw new RuntimeException('Cache externe');}$wpdb->query('START TRANSACTION');try{eval("+php(source)+");}finally{$wpdb->query('ROLLBACK');wp_cache_flush();}"
    result = b11.b10.b09.b08.c25.b06.profils.b00.wp('eval', code, check=False)
    preserved = before == state()
    save(label, {'native': result, 'business_preserved': preserved, 'sources': sources()})
    print(json.dumps({'native':result, 'business_preserved':preserved}, ensure_ascii=False))
    assert result['code'] == 0 and not result['stderr'] and preserved


if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2])
