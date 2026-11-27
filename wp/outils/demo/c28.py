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


def deploy(label):
    identity = guard()
    before = state()
    old = wp('$o=[];foreach('+php(FILES)+' as $n){$p=WP_CONTENT_DIR."/".$n;$o[$n]=is_file($p)?file_get_contents($p):null;}echo wp_json_encode($o);')
    local = {n:(ROOT/'wp'/n).read_text(encoding='utf-8') for n in FILES}
    assert old[FILES[3]] in [local[FILES[3]], local[FILES[3]].replace(BLOCK, '')], 'Bootstrap divergent'
    # C14 : seul un point d'expansion, même décision/remboursement, aucune bibliothèque changée.
    c14 = local[FILES[2]]
    start = c14.index('                    // C28 :')
    end = c14.index('\n                }\n            }\n        } while', start)
    wrapped = c14[start:end].splitlines()
    legacy = '\n'.join(line[4:] for line in wrapped[3:-1])
    c14old = c14[:start] + legacy + c14[end:]
    assert old[FILES[2]] in [c14, c14old], 'Adaptateur C14 divergent'
    for name in [FILES[0], FILES[1], FILES[4]]:
        known = [json.loads(p.read_text(encoding='utf-8')).get('readback', {}).get(name) for p in OUT.glob('installation-*.json') if not p.name.endswith('-avant.json')]
        assert old[name] in [None, local[name]] or hashlib.sha256(old[name].encode()).hexdigest() in known, name
    snap = private('C28-'+label, {'files':old, 'business':before})
    save(label+'-avant', {'identity':identity, 'private_snapshot':snap, 'business':before})
    for name in FILES:
        upload(name, (ROOT/'wp'/name).read_bytes())
    expected = {n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in FILES}
    assert hashes(FILES) == expected and before == state()
    save(label, {'readback':expected, 'business_preserved':True})
    print('C28 sources relues :', len(expected))


def seed(label):
    identity = guard()
    prior = state()
    snap = private('C28-'+label, {'business':prior})
    src = (ROOT/'wp/outils/demo/c28-seed.php').read_text(encoding='utf-8').split('<?php', 1)[1]
    first = wp(src)
    second = wp(src)
    assert first == second
    save(label, {'identity':identity, 'fixture':first, 'idempotent':True, 'before':prior, 'after':state(), 'private_snapshot':snap})
    print(json.dumps(first, ensure_ascii=False))


def preservation(label):
    import copy
    guard()
    baseline = json.loads((OUT/'fixture-01.json').read_text(encoding='utf-8'))['before']
    current = state()
    projected = copy.deepcopy(current)
    fixture = wp('echo wp_json_encode(get_option("imagine_c28_fixture"));')
    ident = fixture['product']
    projected['native']['produits'].pop(str(ident))
    fingerprints = wp('''global $wpdb;$id='''+str(ident)+''';$out=[];foreach(['posts'=>"SELECT * FROM {$wpdb->posts} WHERE ID<>$id",'postmeta'=>"SELECT * FROM {$wpdb->postmeta} WHERE post_id<>$id"] as $key=>$sql){$rows=$wpdb->get_results($sql,ARRAY_A);$hashes=array_map(static fn($r)=>hash('sha256',serialize($r)),$rows);sort($hashes);$out[$key]=['count'=>count($hashes),'sha256'=>hash('sha256',serialize($hashes))];}echo wp_json_encode($out);''')
    projected['native']['native_fingerprints'].update(fingerprints)
    checks = {key:baseline[key] == projected[key] for key in baseline}
    assert all(checks.values()), checks
    save(label, {'checks':checks, 'initial_before_fixture':baseline, 'current':current, 'projected_without_only_owned_product':projected, 'declared_delta':{'product':ident, 'fixture_option':'imagine_c28_fixture', 'demo_mu':'mu-plugins/imagine-c28-demo.php'}, 'sources':sources()})
    print('C28 : état initial préservé, seul produit fictif ajouté.')


def regressions(label):
    guard()
    before = state()
    results = {}
    for filename in ['c14-corrections-runtime.php']:
        source = (ROOT/'wp/tests/demo'/filename).read_text(encoding='utf-8').split('<?php',1)[1]
        code = "global $wpdb;$wpdb->query('START TRANSACTION');try{eval("+php(source)+");}finally{$wpdb->query('ROLLBACK');wp_cache_flush();}"
        r = b11.b10.b09.b08.c25.b06.profils.b00.wp('eval', code, check=False)
        results[filename] = r
        assert r['code'] == 0 and not r['stderr'] and all(json.loads(r['stdout']).values()), r
    assert before == state()
    save(label, {'results':results, 'business_preserved':True, 'sources':sources()})
    print(json.dumps({n:len(json.loads(r['stdout'])) for n,r in results.items()}))


if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2])
