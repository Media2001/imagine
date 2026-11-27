"""C27 fusion : vraies pannes SQL et mutants sur la seule démo fictive, avec inverse."""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
import c27
spec = importlib.util.spec_from_file_location('c27_native', c27.ROOT/'wp/outils/demo/c27-native.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def run(label):
    assert not (c27.PROOF/(label+'.json')).exists()
    identity = c27.guard()
    saved, business = c27.snapshot(), c27.state()
    durable = c27.private('c27-'+label, {'database': saved, 'business': business})
    paths = ['plugins/imagine-site/Acquisition.php', 'plugins/imagine-site/AcquisitionConfidentialite.php']
    original = {p: (c27.ROOT/'wp'/p).read_bytes() for p in paths}
    runtime, observer = 'imagine-demo-build/c27-corrections-runtime.php', 'mu-plugins/c27-observer.php'
    assert c27.wp('echo wp_json_encode([file_exists(WP_CONTENT_DIR."/'+runtime+'"),file_exists(WP_CONTENT_DIR."/'+observer+'")]);') == [False, False]
    assert c27.b09.b08.c25.b06.hashes(paths) == {p: hashlib.sha256(v).hexdigest() for p, v in original.items()}
    assert c27.wp('echo wp_json_encode(Imagine\\Site\\AcquisitionConfidentialite::lignes());') == []
    checks, evidence, cleanup, owned = {}, {}, {}, []
    error = None

    def install(p, raw):
        c27.upload(p, raw)
        assert c27.b09.b08.c25.b06.hashes([p]) == {p: hashlib.sha256(raw).hexdigest()}

    try:
        c27.upload(runtime, (c27.ROOT/'wp/tests/demo/c27-corrections-runtime.php').read_bytes())
        c27.upload(observer, (c27.ROOT/'wp/tests/demo/c27-observer.php').read_bytes())
        session = c27.wp('$u=get_userdata(28);if(!$u||!str_ends_with($u->user_email,"@example.org")){throw new RuntimeException("Profil fictif requis");}$t=WP_Session_Tokens::get_instance(28)->create(time()+3600);echo wp_json_encode(LOGGED_IN_COOKIE."=".wp_generate_auth_cookie(28,time()+3600,"logged_in",$t));')
        c27.private('c27-'+label+'-session', {'cookie': session})
        def http(url, data=None):
            assert urllib.parse.urlsplit(url).netloc == urllib.parse.urlsplit(identity['url']).netloc
            req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None,
                headers={'Cookie': session, 'X-Imagine-C27-Recette': 'recette-fictive'})
            # Aucun suivi hors site : même une redirection inattendue doit rester locale.
            class SameSite(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    assert urllib.parse.urlsplit(newurl).netloc == urllib.parse.urlsplit(identity['url']).netloc
                    return super().redirect_request(req, fp, code, msg, headers, newurl)
            try:
                response = urllib.request.build_opener(SameSite()).open(req, timeout=45)
            except urllib.error.HTTPError as ex:
                response = ex
            with response:
                return response.status, response.read().decode('utf-8')
        for mode, mutant in [('I1', False), ('I1', True), ('I2', False), ('I2', True),
                             ('deletefail', False), ('finalfail', False), ('M1', False), ('M1', True)]:
            key = mode+('_mutant' if mutant else '_corrige')
            row = c27.wp('$o=wc_create_order(["customer_id"=>28,"status"=>"pending","created_via"=>"checkout"]);$o->update_meta_data("_imagine_c27_recette",'+c27.php(label)+');$o->set_total(1);$o->set_status("processing");$o->set_date_paid(time());$o->save();echo wp_json_encode(["id"=>$o->get_id(),"url"=>$o->get_checkout_order_received_url()]);')
            owned.append(row['id'])
            c27.private('c27-'+label+'-objets', {'ids': owned})
            if mode == 'M1':
                status, form = http(row['url'])
                assert status == 200 and '<section id="imagine-acquisition">' in form
                section = form.split('<section id="imagine-acquisition">', 1)[1].split('</section>', 1)[0]
                signed = unescape(re.search(r'name="_c27" value="([^"]+)"', section)[1])
            mutated_path = paths[1] if mode == 'I2' else paths[0]
            if mutant:
                raw = original[mutated_path]
                if mode == 'I1':
                    old = b'$source = self::sourceFiable($actor);'
                    new = b"$source = get_user_meta($actor, self::SOURCE, true) === '' ? [] : [get_user_meta($actor, self::SOURCE, true)];"
                    assert raw.count(old) == 1
                elif mode == 'I2':
                    old = b'Acquisition::sourceFiable($owner)'
                    new = b"(get_user_meta($owner, Acquisition::SOURCE, true) === '' ? [] : [get_user_meta($owner, Acquisition::SOURCE, true)])"
                    assert raw.count(old) == 3
                else:
                    old = b"(is_array($seen) && ($seen['etat'] ?? '') === 'effacee')"
                    new = b'false'
                    assert raw.count(old) == 1
                install(mutated_path, raw.replace(old, new))
            try:
                data = c27.wp('$c27_order='+str(row['id'])+';$c27_mode='+c27.php(mode)+';require WP_CONTENT_DIR."/'+runtime+'";')
                if mode == 'M1':
                    status, body = http(identity['url']+'/wp-admin/admin-post.php',
                        {'action': 'imagine_acquisition', 'commande': str(row['id']), 'choix': 'lune', '_c27': signed})
                    after = c27.wp('echo wp_json_encode(["answer"=>get_option(Imagine\\Site\\Acquisition::REPONSE . '+str(row['id'])+',null),"source"=>get_user_meta(28,Imagine\\Site\\Acquisition::SOURCE,true)]);')
                    data['old_POST_status'] = status
                    data['old_POST_wrote_answer'] = isinstance(after['answer'], dict)
                    data['old_POST_wrote_source'] = isinstance(after['source'], dict)
                    passed = data['pass'] and status == 403 and after['answer'] is None and after['source'] == ''
                else:
                    passed = data['pass']
                checks[key] = passed is (not mutant)
                if mutant and mode == 'I1':
                    checks[key] = checks[key] and data['sql_faults'] == 1 and data['answer_present'] is True and data['source_previous_preserved'] is False
                if mutant and mode == 'I2':
                    checks[key] = checks[key] and data['sql_faults'] == 1 and data['source_present'] is True and data['result']['done'] is True and data['result']['items_retained'] is False
                evidence[key] = data
                print(key, checks[key], json.dumps(data, ensure_ascii=False))
            finally:
                if mutant:
                    install(mutated_path, original[mutated_path])
        observations = c27.wp('echo wp_json_encode(get_option("imagine_c27_observations",[]));')
        checks['aucune_transmission'] = all(v == 0 for k, v in (observations.items() if isinstance(observations, dict) else []) if k.startswith('c27_'))
        assert all(v is True for v in checks.values()), checks
    except Exception as ex:
        error = type(ex).__name__+': '+str(ex)
        raise
    finally:
        def attempt(key, fn):
            try:
                fn()
                cleanup[key] = True
            except Exception as ex:
                cleanup[key] = False
                cleanup[key+'_error'] = type(ex).__name__+': '+str(ex)
        attempt('sources_exactes', lambda: [install(p, v) for p, v in original.items()])
        attempt('commandes_natives_supprimees', lambda: c27.wp('foreach('+c27.php(owned)+' as $id){$o=wc_get_order($id);if($o){if($o->get_meta("_imagine_c27_recette")!=='+c27.php(label)+'){throw new RuntimeException("Commande étrangère");}$o->delete(true);}}echo wp_json_encode(true);'))
        attempt('actions_et_adresses_restaurees', lambda: native.restore_order_edges(saved, set(owned)))
        attempt('options_C27_restaurees', lambda: native.restore_options(saved))
        attempt('profil_lecteur_restaure', lambda: native.restore_users(saved, {28}))
        attempt('temporaires_retires', lambda: c27.b09.remove_remote([runtime, observer]))
        exact = native.compare(saved, c27.snapshot())
        preserved = business == c27.state()
        c27.save(label, {'identity': identity, 'private_snapshot': durable, 'checks': checks, 'evidence': evidence,
            'restoration': exact, 'cleanup': cleanup, 'business_preserved': preserved, 'error': error, 'owned_orders': len(owned)})
        print(json.dumps({'checks': checks, 'restoration': exact, 'cleanup': cleanup, 'business_preserved': preserved, 'error': error}, ensure_ascii=False))
        assert all(v is True for v in cleanup.values()) and all(exact.values()) and preserved


if __name__ == '__main__':
    run(sys.argv[1])
