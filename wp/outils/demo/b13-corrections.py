"""B13 corrections : banc partagé inchangé, nouvelles preuves immuables."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
import b13
ROOT, OUT = b13.ROOT, b13.OUT
spec = importlib.util.spec_from_file_location('b13_shared_browser', ROOT/'wp/outils/demo/b13-browser.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
EXPECTED = None

def checker(page, body, role, index, fixture, markers, check):
    result = b.b13_checker(page, body, role, index, fixture, markers, check)
    nav = page.locator('nav[aria-label="Navigation principale"]')
    for term, ids in EXPECTED['selection'].items():
        section = nav.locator('[data-b13-theme="'+term+'"]')
        actual = section.locator('[data-b13-article]').evaluate_all('(els)=>els.map(e=>Number(e.dataset.b13Article))')
        check(role+'_'+str(index)+'_recents_theme_'+term, actual == ids)
        for article in ids:
            li = section.locator('[data-b13-article="'+str(article)+'"]')
            check(role+'_'+str(index)+'_image_article_'+str(article), li.count() == 1 and li.locator('img').count() == 1)
    check(role+'_'+str(index)+'_abonnement_destination', nav.locator('.imagine-nav-abonnement > a').get_attribute('href') == EXPECTED['abonnement'])
    result['selection'] = EXPECTED['selection']
    return result

def browser(name):
    global EXPECTED
    b13.guard()
    EXPECTED = b13.wp('$o=["selection"=>[],"abonnement"=>Imagine\\Site\\Navigation::abonnementUrl()];foreach(get_terms(["taxonomy"=>"imagine_thematique","hide_empty"=>false]) as $t){$q=new WP_Query(["post_type"=>"post","post_status"=>"publish","post_password"=>"","posts_per_page"=>3,"orderby"=>["date"=>"DESC","ID"=>"DESC"],"tax_query"=>[["taxonomy"=>"imagine_thematique","terms"=>$t->term_id]],"fields"=>"ids"]);$o["selection"][(string)$t->term_id]=$q->posts;}echo wp_json_encode($o);')
    b.run(b13, name, checker, warm=lambda:b13.wp('Imagine\\Site\\Navigation::invalider();Imagine\\Site\\Navigation::thematiques();echo wp_json_encode(true);'))

def native(name):
    b13.guard()
    names = ['imagine-demo-build/b13-seed-correction.php','imagine-demo-build/b13-b08-sequence.php']
    assert not any(b13.wp('$o=[];foreach('+b13.php(names)+' as $n){$o[]=file_exists(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($o);'))
    try:
        b13.b11.upload(names[0], (ROOT/'wp/outils/demo/b13-seed.php').read_bytes())
        b13.b11.upload(names[1], (ROOT/'wp/outils/demo/b08-seed.php').read_bytes())
        b13.runtime(b13, name)
    finally:
        b13.b11.b10.b09.remove_remote(names)
        assert b13.wp('$ok=true;foreach('+b13.php(names)+' as $n){$ok=$ok&&!file_exists(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($ok);') is True

def seed(name):
    b13.guard()
    src = (ROOT/'wp/outils/demo/b13-seed.php').read_text(encoding='utf-8').split('<?php',1)[1]
    a = b13.wp(src)
    c = b13.wp(src)
    assert a == c
    actual = b13.wp('$f=get_option("imagine_b13_fixture");$o=[];foreach($f["illustrations"] as $id){$o[(string)$id]=get_post_thumbnail_id($id);}echo wp_json_encode($o);')
    assert len(actual) == 9 and all(actual.values())
    b13.save(b13, name, {'fixture':a,'idempotent':a==c,'images_readback':actual})
    print(json.dumps({'idempotent':True,'illustrated_articles':len(actual)},ensure_ascii=False))

if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2])
