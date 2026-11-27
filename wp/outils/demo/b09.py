"""B09 : cible fictive unique, preuves immuables et readback après écriture."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path
import b08
ROOT = b08.ROOT
PROOF = ROOT/'production/B-09'
wp, php = b08.wp, b08.php
NAMES = ['plugins/imagine-site/'+n for n in ['Contact.php', 'ContactConfidentialite.php', 'AutresPages.php']] + ['themes/imagine/footer.php']
BLOCK = "// B09 — pages natives et contact privé local.\nrequire_once __DIR__ . '/Contact.php';\nrequire_once __DIR__ . '/ContactConfidentialite.php';\nrequire_once __DIR__ . '/AutresPages.php';\nContact::register();\nContactConfidentialite::register();\nAutresPages::register();\n\n"


def sources():
    files = [ROOT/'wp'/n for n in NAMES if (ROOT/'wp'/n).is_file()]
    for pattern in ['wp/plugins/imagine-site/tests/Contact*', 'wp/outils/demo/b09*', 'wp/tests/demo/b09*']:
        files += [p for p in ROOT.glob(pattern) if p.is_file()]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}


def save(label, data):
    PROOF.mkdir(exist_ok=True)
    p=PROOF/(label+'.json')
    assert not p.exists(), p
    p.write_text(json.dumps({'scope':'imagine-test-demo','sources':sources(),**data},ensure_ascii=False,indent=2),encoding='utf-8')


def inspect(label):
    identity=b08.c25.b06.guard()
    data=wp('''echo wp_json_encode(['privacy'=>get_option('wp_page_for_privacy_policy'),'pages'=>array_map(static fn($p)=>['id'=>$p->ID,'slug'=>$p->post_name,'title'=>$p->post_title,'status'=>$p->post_status,'empty'=>$p->post_content===''],get_posts(['post_type'=>'page','post_status'=>'any','numberposts'=>-1])),'locations'=>get_nav_menu_locations()]);''')
    save(label,{'identity':identity,'structure':data})
    print(json.dumps(data,ensure_ascii=False))


def deploy(label):
    identity=b08.c25.b06.guard()
    boot='plugins/imagine-site/imagine-site.php'
    local=(ROOT/'wp'/boot).read_text(encoding='utf-8')
    names=NAMES+[boot]
    old=wp('$v=[];foreach('+php(names)+' as $n){$p=WP_CONTENT_DIR."/".$n;$v[$n]=is_file($p)?file_get_contents($p):null;}echo wp_json_encode($v);')
    assert old[boot] in [local,local.replace(BLOCK,'')], 'Bootstrap divergent'
    for n in NAMES[:-1]:
        assert old[n] in [None,(ROOT/'wp'/n).read_text(encoding='utf-8')], n
    footer=(ROOT/'wp/themes/imagine/footer.php').read_text(encoding='utf-8')
    assert old[NAMES[-1]] in [footer,footer.replace("if (has_nav_menu('imagine-footer')) {\n                wp_nav_menu(['theme_location' => 'imagine-footer', 'container' => false, 'fallback_cb' => false]);\n            }", 'imagine_navigation();')], 'Footer divergent'
    before=b08.c25.b06.state()
    durable=b08.c25.private('b09-'+label,{'database':b08.snapshot(),'files':old,'business':before})
    for n in names:
        b08.c25.b06.profils.b00.upload(n,(ROOT/'wp'/n).read_bytes())
    actual=b08.c25.b06.hashes(names)
    assert actual=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in names}
    assert before==b08.c25.b06.state()
    save(label,{'identity':identity,'private_snapshot':durable,'readback':actual,'business_preserved':True})
    print('Déploiement relu :',len(actual),'fichiers')


def remove_remote(names):
    code='import pathlib,json;root=pathlib.Path("/app/sites/imagine-test-demo/wp-content");names='+repr(names)+';[(root/n).unlink() for n in names];print(json.dumps(all(not (root/n).exists() for n in names)))'
    p=subprocess.run(['wsl.exe','docker','exec','staging-wp-dashboard','python','-c',code],capture_output=True,encoding='utf-8')
    assert p.returncode==0 and json.loads(p.stdout) is True


def runtime(label):
    b08.c25.b06.guard()
    before=b08.snapshot();business=b08.c25.b06.state()
    durable=b08.c25.private('b09-'+label,{'database':before,'business':business})
    names=['imagine-demo-build/b09-structure.php','imagine-demo-build/b09-seed.php']
    assert not any(wp('$v=[];foreach('+php(names)+' as $n){$v[]=file_exists(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($v);'))
    result={};cleanup={}
    try:
        b08.c25.b06.profils.b00.upload(names[0],(ROOT/'wp/tests/demo/b09-structure.php').read_bytes())
        seed=ROOT/'wp/outils/demo/b09-seed.php'
        if seed.exists(): b08.c25.b06.profils.b00.upload(names[1],seed.read_bytes())
        result=wp('require WP_CONTENT_DIR."/'+names[0]+'";')
    finally:
        present=wp('$v=[];foreach('+php(names)+' as $n){if(file_exists(WP_CONTENT_DIR."/".$n)){$v[]=$n;}}echo wp_json_encode($v);')
        remove_remote(present)
        after=b08.snapshot()
        exact={k:before[k]==after[k] for k in ['users','usermeta','posts','postmeta','comments','commentmeta','navigation','wc_orders','wc_orders_meta','wc_order_addresses','wc_order_operational_data','woocommerce_order_items','woocommerce_order_itemmeta']}
        opts=lambda db:[r for r in db['options'] if r['option_name'].startswith('imagine_') or r['option_name'] in ['cron','wp_page_for_privacy_policy','theme_mods_imagine']]
        exact['options_metier']=opts(before)==opts(after)
        preserved=business==b08.c25.b06.state()
        save(label,{**result,'private_snapshot':durable,'restoration':exact,'business_preserved':preserved,'runners_removed':True})
        print(json.dumps({**result,'restoration':exact,'business_preserved':preserved},ensure_ascii=False))
        assert all(exact.values()) and preserved
    assert result.get('checks') and all(v is True for v in result['checks'].values())


if __name__=='__main__':
    assert sys.argv[1] in ['inspect','deploy','runtime','seed']
    globals()[sys.argv[1]](*sys.argv[2:])
