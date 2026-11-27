"""Corrections B09 : interruption durable exacte, reprise et restauration ciblée."""
import sys
sys.dont_write_bytecode = True
import json
import hashlib
import b09


def seed(label):
    b09.b08.c25.b06.guard()
    before = b09.b08.snapshot()
    business = b09.b08.c25.b06.state()
    durable = b09.b08.c25.private('b09-' + label, {'database': before, 'business': business})
    original = b09.wp("echo wp_json_encode(get_option('imagine_b09_menu'));")
    old_id = original['items']['contact']
    baseline = b09.wp("global $wpdb;echo wp_json_encode(array_map('intval',$wpdb->get_col(\"SELECT DISTINCT post_id FROM {$wpdb->postmeta} WHERE meta_key='imagine_b09_menu_item'\")));")
    name = 'imagine-demo-build/b09-correction-seed.php'
    assert b09.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR.' + b09.php('/' + name) + '));') is False
    checks = {}
    evidence = {}
    try:
        b09.b08.c25.b06.profils.b00.upload(name, (b09.ROOT / 'wp/outils/demo/b09-seed.php').read_bytes())
        b09.wp('$id=' + str(old_id) + ';if(get_post_meta($id,"imagine_b09_menu_item",true)!=="contact"){throw new RuntimeException("Propriété");}wp_delete_post($id,true);$v=get_option("imagine_b09_menu");unset($v["items"]["contact"]);update_option("imagine_b09_menu",$v,false);echo wp_json_encode(get_post($id)===null);')
        code = "add_action('added_post_meta',static function($mid,$id,$key,$value){if($key==='imagine_b09_menu_item'&&$value==='contact'){exit(73);}},10,4);require WP_CONTENT_DIR.'/" + name + "';"
        interrupted = b09.b08.c25.b06.profils.b00.wp('eval', code, check=False)
        partial = b09.wp("global $wpdb;$ids=array_map('intval',$wpdb->get_col(\"SELECT DISTINCT post_id FROM {$wpdb->postmeta} WHERE meta_key='imagine_b09_menu_item' AND meta_value='contact'\"));echo wp_json_encode(['ids'=>$ids,'option'=>get_option('imagine_b09_menu'),'menus'=>array_map(static fn($id)=>wp_get_object_terms($id,'nav_menu',['fields'=>'ids']),$ids)]);")
        checks['interruption_entre_marqueur_et_option'] = interrupted['code'] == 73 and len(partial['ids']) == 1 and 'contact' not in partial['option']['items'] and partial['menus'] == [[]]
        assert checks['interruption_entre_marqueur_et_option'], partial
        first = b09.wp('require WP_CONTENT_DIR.' + b09.php('/' + name) + ';')
        second = b09.wp('require WP_CONTENT_DIR.' + b09.php('/' + name) + ';')
        native = b09.wp("global $wpdb;$ids=array_map('intval',$wpdb->get_col(\"SELECT DISTINCT post_id FROM {$wpdb->postmeta} WHERE meta_key='imagine_b09_menu_item'\"));$out=[];foreach($ids as $id){$out[]=['id'=>$id,'key'=>get_post_meta($id,'imagine_b09_menu_item',true),'menus'=>wp_get_object_terms($id,'nav_menu',['fields'=>'ids'])];}echo wp_json_encode($out);")
        checks['id_marque_hors_option_reutilise'] = first['items']['contact'] == partial['ids'][0]
        checks['aucun_orphelin_ni_doublon'] = len(native) == 5 and len({r['key'] for r in native}) == 5 and all(r['menus'] == [original['menu']] for r in native) and {r['id'] for r in native} == set(first['items'].values())
        checks['rejeu_idempotent'] = first == second
        evidence = {'interrupted_exit': interrupted['code'], 'partial': partial, 'first': first, 'second': second, 'native': native}
    finally:
        # Retirer nos seuls nouveaux items ; restituer le seul item B09 retiré, ses métas et relations.
        cleanup = b09.wp('global $wpdb;$base=' + b09.php(baseline) + ';$ids=array_map("intval",$wpdb->get_col("SELECT DISTINCT post_id FROM {$wpdb->postmeta} WHERE meta_key=\'imagine_b09_menu_item\'"));foreach(array_diff($ids,$base) as $id){wp_delete_post($id,true);}$rows=' + b09.php([r for r in before['posts'] if int(r['ID']) == old_id]) + ';foreach($rows as $row){$wpdb->insert($wpdb->posts,$row);}$rows=' + b09.php([r for r in before['postmeta'] if int(r['post_id']) == old_id]) + ';foreach($rows as $row){$wpdb->insert($wpdb->postmeta,$row);}$rows=' + b09.php([r for r in before['navigation']['term_relationships'] if int(r['object_id']) == old_id]) + ';foreach($rows as $row){$wpdb->insert($wpdb->term_relationships,$row);}update_option("imagine_b09_menu",' + b09.php(original) + ',false);wp_update_term_count_now([' + str(original['menu']) + '],"nav_menu");wp_cache_flush();echo wp_json_encode(true);')
        b09.remove_remote([name])
        after = b09.b08.snapshot()
        restoration = {k: before[k] == after[k] for k in ['users', 'usermeta', 'posts', 'postmeta', 'navigation']}
        opts = lambda db: [r for r in db['options'] if r['option_name'].startswith('imagine_') or r['option_name'] in ['cron', 'wp_page_for_privacy_policy', 'theme_mods_imagine']]
        restoration['options_metier'] = opts(before) == opts(after)
        preserved = business == b09.b08.c25.b06.state()
        b09.save(label, {'checks': checks, 'restoration': restoration, 'business_preserved': preserved, 'runner_removed': True, 'private_snapshot': durable, **evidence})
        print(json.dumps({'checks': checks, 'restoration': restoration, 'business_preserved': preserved}, ensure_ascii=False))
        assert cleanup and all(restoration.values()) and preserved, 'Restauration non prouvée'
    assert len(checks) == 4 and all(checks.values()), checks


if __name__ == '__main__':
    seed(sys.argv[1])
