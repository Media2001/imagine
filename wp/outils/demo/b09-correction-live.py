"""B09 : déploiement borné des deux fichiers corrigés, suppression partielle native."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import b09


def deploy(label):
    identity = b09.b08.c25.b06.guard()
    names = ['plugins/imagine-site/Contact.php', 'plugins/imagine-site/ContactConfidentialite.php']
    old = json.loads((b09.PROOF / 'final-V2.json').read_text(encoding='utf-8'))['sources']
    current = b09.b08.c25.b06.hashes(names)
    for name in names:
        assert current[name] in [old['wp/' + name], hashlib.sha256((b09.ROOT / 'wp' / name).read_bytes()).hexdigest()], name
    before = b09.b08.c25.b06.state()
    for name in names:
        b09.b08.c25.b06.profils.b00.upload(name, (b09.ROOT / 'wp' / name).read_bytes())
    actual = b09.b08.c25.b06.hashes(names)
    assert actual == {n: hashlib.sha256((b09.ROOT / 'wp' / n).read_bytes()).hexdigest() for n in names}
    assert before == b09.b08.c25.b06.state()
    b09.save(label, {'identity': identity, 'readback': actual, 'business_preserved': True})
    print('Deux fichiers corrigés relus, état métier inchangé')


def partial(label):
    b09.b08.c25.b06.guard()
    before = b09.b08.snapshot()
    business = b09.b08.c25.b06.state()
    email = 'b09-partiel-correction@example.org'
    assert b09.wp('echo wp_json_encode(Imagine\\Site\\Contact::ids(' + b09.php(email) + '));') == []
    assert not any(r['option_name'].startswith('imagine_contact_effacement_') for r in before['options'])
    durable = b09.b08.c25.private('b09-' + label, {'database': before, 'business': business})
    owned = []
    checks = {}
    evidence = {}
    try:
        owned = b09.wp('if(!Imagine\\Site\\Contact::enregistrer("Fictif B09",' + b09.php(email) + ',"B09_TEXTE_PERSONNEL_PARTIEL",false)){throw new RuntimeException("Insertion");}echo wp_json_encode(Imagine\\Site\\Contact::ids(' + b09.php(email) + '));')
        assert len(owned) == 1
        id = owned[0]
        # wp_delete_post appelle réellement delete_metadata_by_mid ; seule la méta texte survit.
        first = b09.wp('add_filter("delete_post_metadata_by_mid",static function($v,$mid){$m=get_metadata_by_mid("post",$mid);return $m&&(int)$m->post_id===' + str(id) + '&&$m->meta_key==="imagine_contact_texte"?true:$v;},10,2);$r=Imagine\\Site\\ContactConfidentialite::effacer(' + b09.php(email) + ');global $wpdb;echo wp_json_encode(["result"=>$r,"post"=>get_post(' + str(id) + '),"meta"=>$wpdb->get_results("SELECT meta_key,meta_value FROM {$wpdb->postmeta} WHERE post_id=' + str(id) + '",ARRAY_A),"pending"=>get_option("imagine_contact_effacement_".hash("sha256",' + b09.php(email) + '))]);')
        checks['post_disparu_texte_personnel_survit'] = first['post'] is None and first['meta'] == [{'meta_key': 'imagine_contact_texte', 'meta_value': 'B09_TEXTE_PERSONNEL_PARTIEL'}]
        checks['jamais_done_si_meta_survit'] = first['result']['done'] is False and first['result']['items_retained'] is True and first['result']['items_removed'] is False
        checks['temoin_durable_sans_email_stocke'] = first['pending'] == [id]
        second = b09.wp('add_filter("delete_post_metadata",static fn()=>true);echo wp_json_encode(Imagine\\Site\\ContactConfidentialite::effacer(' + b09.php(email) + '));')
        checks['nettoyage_refuse_reste_incomplet'] = second['done'] is False and second['items_retained'] is True
        last = b09.wp('echo wp_json_encode(Imagine\\Site\\ContactConfidentialite::effacer(' + b09.php(email) + '));')
        final = b09.wp('global $wpdb;echo wp_json_encode(["metas"=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->postmeta} WHERE post_id=' + str(id) + '"),"pending"=>get_option("imagine_contact_effacement_".hash("sha256",' + b09.php(email) + '),null)]);')
        checks['reprise_autre_processus_supprime_orphelin_et_temoin'] = last['done'] is True and last['items_removed'] is True and final == {'metas': 0, 'pending': None}
        evidence = {'first': first, 'blocked_retry': second, 'last': last, 'readback': final}
    finally:
        b09.wp('foreach(' + b09.php(owned) + ' as $id){wp_delete_post($id,true);foreach(array_keys(get_post_meta($id)) as $key){if(str_starts_with($key,"imagine_contact_")){delete_post_meta($id,$key);}}}delete_option("imagine_contact_effacement_".hash("sha256",' + b09.php(email) + '));echo wp_json_encode(true);')
        after = b09.b08.snapshot()
        restoration = {k: before[k] == after[k] for k in ['users', 'usermeta', 'posts', 'postmeta', 'navigation']}
        opts = lambda db: [r for r in db['options'] if r['option_name'].startswith('imagine_') or r['option_name'] in ['cron', 'wp_page_for_privacy_policy', 'theme_mods_imagine']]
        restoration['options_metier'] = opts(before) == opts(after)
        preserved = business == b09.b08.c25.b06.state()
        b09.save(label, {'checks': checks, 'restoration': restoration, 'business_preserved': preserved, 'private_snapshot': durable, **evidence})
        print(json.dumps({'checks': checks, 'restoration': restoration, 'business_preserved': preserved}, ensure_ascii=False))
        assert all(restoration.values()) and preserved
    assert len(checks) == 5 and all(checks.values()), checks


if __name__ == '__main__':
    assert sys.argv[1] in ['deploy', 'partial']
    globals()[sys.argv[1]](sys.argv[2])
