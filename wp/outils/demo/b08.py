"""B08 cible unique gardée, état privé durable et reçus bornés."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import c25
ROOT = c25.ROOT
PROOF = ROOT / 'production/B-08'
wp = c25.wp
php = c25.php
NAMES = ['plugins/imagine-site/' + n for n in ['CooperativeRegles.php', 'Cooperative.php', 'Soutenir.php', 'SujetRegles.php', 'Sujet.php', 'SujetConfidentialite.php']]
BLOCK = "// B08 — pages publiques et propositions locales privées.\n" + ''.join("require_once __DIR__ . '/" + n.split('/')[-1] + "';\n" for n in NAMES) + "Cooperative::register();\nSoutenir::register();\nSujet::register();\nSujetConfidentialite::register();\n\n"
NAMES.append('themes/imagine/header.php')


def snapshot():
    data = c25.snapshot()
    data['navigation'] = wp('''global $wpdb;$v=[];foreach(['terms','term_taxonomy','term_relationships','termmeta'] as $k){$v[$k]=$wpdb->get_results("SELECT * FROM {$wpdb->$k}",ARRAY_A);if($wpdb->last_error){throw new RuntimeException('Navigation illisible');}}echo wp_json_encode($v);''')
    return data


def sources():
    files = [ROOT / 'wp' / n for n in NAMES]
    for pattern in ['wp/plugins/imagine-site/tests/Cooperative*', 'wp/plugins/imagine-site/tests/Soutenir*', 'wp/plugins/imagine-site/tests/Sujet*', 'wp/outils/demo/b08*', 'wp/tests/demo/b08*']:
        files += [p for p in ROOT.glob(pattern) if p.is_file()]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def save(label, data):
    PROOF.mkdir(exist_ok=True)
    p = PROOF / (label + '.json')
    assert not p.exists(), p
    p.write_text(json.dumps({'scope': 'imagine-test-demo', 'sources': sources(), **data}, ensure_ascii=False, indent=2), encoding='utf-8')


def inspect(label):
    identity = c25.b06.guard()
    data = wp('''$out=['pages'=>[],'menus'=>[],'locations'=>get_nav_menu_locations(),'manifest'=>get_option('imagine_demo_manifest')];foreach(get_posts(['post_type'=>'page','post_status'=>'publish','numberposts'=>-1]) as $p){$out['pages'][]=['id'=>$p->ID,'slug'=>$p->post_name,'title'=>$p->post_title,'parent'=>$p->post_parent,'empty'=>$p->post_content===''];}foreach(wp_get_nav_menus() as $m){foreach(wp_get_nav_menu_items($m->term_id) as $i){$out['menus'][]=['menu'=>$m->term_id,'id'=>$i->ID,'title'=>$i->title,'object'=>$i->object,'object_id'=>$i->object_id,'type'=>$i->type,'url'=>$i->url,'order'=>$i->menu_order];}}echo wp_json_encode($out);''')
    save(label, {'identity': identity, 'structure': data})
    print(json.dumps(data, ensure_ascii=False))


def deploy(label):
    identity = c25.b06.guard()
    boot = 'plugins/imagine-site/imagine-site.php'
    p = ROOT / 'wp' / boot
    local = p.read_text(encoding='utf-8')
    old = wp('$out=[];foreach(' + php(NAMES + [boot]) + ' as $n){$p=WP_CONTENT_DIR."/".$n;$out[$n]=is_file($p)?file_get_contents($p):null;}echo wp_json_encode($out);')
    assert old[boot] in [local, local.replace(BLOCK, '')], 'Bootstrap divergent'
    before = c25.b06.state()
    snapshot = c25.private('b08-' + label, {'files': old, 'database': c25.snapshot(), 'business': before})
    for name in NAMES:
        source = (ROOT / 'wp' / name).read_text(encoding='utf-8')
        if name == 'themes/imagine/header.php':
            native = """            <?php
            if (has_nav_menu('imagine-principal')) {
                wp_nav_menu(['theme_location' => 'imagine-principal', 'container' => false, 'fallback_cb' => false]);
            } else {
                imagine_navigation();
            }
            ?>"""
            assert old[name] in [source, source.replace(native, '            <?php imagine_navigation(); ?>')]
        else:
            assert old[name] is None or old[name] == source
        c25.b06.profils.b00.upload(name, (ROOT / 'wp' / name).read_bytes())
    assert wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/' + boot + '"));') == old[boot]
    c25.b06.profils.b00.upload(boot, p.read_bytes())
    actual = c25.b06.hashes(NAMES + [boot])
    assert actual == {n: hashlib.sha256((ROOT / 'wp' / n).read_bytes()).hexdigest() for n in NAMES + [boot]}
    assert before == c25.b06.state()
    save(label, {'identity': identity, 'private_snapshot': snapshot, 'readback': actual, 'business_preserved': True})


def seed(label):
    c25.b06.guard()
    snapshot = c25.private('b08-' + label, {'database': globals()['snapshot'](), 'business': c25.b06.state()})
    target = 'imagine-demo-build/b08-seed.php'
    source = ROOT / 'wp/outils/demo/b08-seed.php'
    c25.b06.profils.b00.upload(target, source.read_bytes())
    a = wp('require WP_CONTENT_DIR."/' + target + '";')
    b = wp('require WP_CONTENT_DIR."/' + target + '";')
    assert a == b
    rows = wp('''$out=[];$v=get_option('imagine_b08_pages');foreach([$v['cooperative'],$v['soutenir'],$v['sujet'],...array_values($v['enfants'])] as $id){$p=get_post($id);$out[]=['id'=>$id,'title'=>$p->post_title,'content'=>$p->post_content,'parent'=>$p->post_parent,'url'=>get_permalink($id)];}echo wp_json_encode($out);''')
    assert len(rows) == 10 and all(r['content'] == '' for r in rows)
    save(label, {'private_snapshot': snapshot, 'fixture': a, 'readback': rows, 'idempotent': True})
    print(json.dumps(rows, ensure_ascii=False))


if __name__ == '__main__':
    assert sys.argv[1] in ['inspect', 'deploy', 'seed']
    globals()[sys.argv[1]](*sys.argv[2:])
