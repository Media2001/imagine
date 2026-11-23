"""Écritures REST HTTP authentifiées : booléens natifs et retrait de clé, article jetable."""
from pathlib import Path
import importlib.util
import json
from urllib.parse import urlencode

spec = importlib.util.spec_from_file_location('c08_http', Path(__file__).with_name('c08-verifier.py'))
http = importlib.util.module_from_spec(spec)
spec.loader.exec_module(http)
c08 = http.c08


def run():
    site, _ = c08.guard()
    base = site['url'].rstrip('/')
    credentials = json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))
    client = http.login(base, {'login': credentials['admin_user'], 'password': credentials['admin_password']})
    meta, nonce = http.fetch(base, '/wp-admin/admin-ajax.php?action=rest-nonce', client)
    if meta['status'] != 200 or len(nonce.strip()) != 10:
        raise RuntimeError('Nonce natif absent')
    headers = {'X-WP-Nonce': nonce.strip(), 'Content-Type': 'application/json'}
    issue = json.loads(c08.b00.wp('eval', 'echo wp_json_encode(get_option("imagine_demo_manifest")["demo-2026-t1"]);')['stdout'])
    checks, responses = {}, {}
    aid = None
    witness = 'C08_BOOL_HTTP_WITNESS'
    try:
        meta, body = http.fetch(base, '/wp-json/wp/v2/posts', client, headers, data=json.dumps({
            'title': 'Canari HTTP éphémère C08', 'status': 'publish', 'date': '2026-01-01T12:00:00',
            'content': witness, 'excerpt': 'Extrait public canari HTTP',
            'meta': {'imagine_numero_id': issue, 'imagine_reserve': False}}).encode())
        checks['creation_rest_http_201'] = meta['status'] == 201
        if not checks['creation_rest_http_201']:
            raise RuntimeError('Création REST HTTP refusée')
        aid = json.loads(body)['id']
        for name, value in [('false', False), ('true', True), ('absent', None), ('false_retabli', False)]:
            meta, body = http.fetch(base, '/wp-json/wp/v2/posts/' + str(aid), client, headers,
                data=json.dumps({'meta': {'imagine_reserve': value}}).encode())
            responses[name + ':write'] = meta
            checks[name + ':ecriture_http_200'] = meta['status'] == 200
            native = json.loads(c08.b00.wp('eval', 'echo wp_json_encode(["exists"=>metadata_exists("post",' + str(aid) + ',"imagine_reserve"),"value"=>get_post_meta(' + str(aid) + ',"imagine_reserve",true),"password"=>get_post(' + str(aid) + ')->post_password]);')['stdout'])
            checks[name + ':stockage_natif_exact'] = native == {'exists': value is not None, 'value': '1' if value is True else '', 'password': ''}
            meta, body = http.fetch(base, '/wp-json/wp/v2/posts/' + str(aid))
            responses[name + ':anonymous'] = meta
            full = value is False
            checks[name + ':lecture_anonyme_http'] = meta['status'] == 200 and (witness in body) == full
            checks[name + ':cache_prive'] = all(s in meta['headers'].get('cache-control', '') for s in ['private', 'no-store'])
            meta, body = http.fetch(base, '/wp-json/wp/v2/search?' + urlencode({'search': witness}))
            checks[name + ':recherche_droit_identique'] = (aid in [x['id'] for x in json.loads(body)]) == full
        meta, _ = http.fetch(base, '/wp-json/wp/v2/posts/' + str(aid), data=json.dumps({'meta': {'imagine_reserve': True}}).encode(), headers={'Content-Type': 'application/json'})
        checks['ecriture_anonyme_http_interdite'] = meta['status'] in (401, 403)
    finally:
        if aid:
            restored = c08.b00.wp('eval', 'wp_delete_post(' + str(aid) + ',true);echo wp_json_encode(get_post(' + str(aid) + ') === null);')['stdout']
            checks['article_temporaire_supprime_readback'] = json.loads(restored) is True
        failures = [k for k, ok in checks.items() if not ok]
        result = {'scope': c08.b00.SLUG, 'checks': checks, 'total': len(checks), 'passed': len(checks)-len(failures), 'failures': failures, 'responses': responses}
        (c08.PROOF/'rest-write.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['total', 'passed', 'failures']}))
    if failures:
        raise SystemExit(1)
    return result


if __name__ == '__main__':
    run()
