"""Pannes réelles C08 : écritures locales bornées, restauration et readback dans finally."""
from pathlib import Path
import importlib.util
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c08
spec = importlib.util.spec_from_file_location('http_c08', Path(__file__).with_name('c08-verifier.py'))
http = importlib.util.module_from_spec(spec)
spec.loader.exec_module(http)


def run():
    site, _ = c08.guard()
    base = site['url'].rstrip('/')
    fixture = json.loads(c08.b00.wp('eval', 'echo wp_json_encode(get_option("imagine_c08_fixture"));')['stdout'])
    aid = fixture['article']
    original = json.loads(c08.b00.wp('eval', 'echo wp_json_encode(["plans"=>get_option("imagine_acces_plans"),"numero"=>get_post_meta(' + str(aid) + ',"imagine_numero_id",true)]);')['stdout'])
    creds = json.loads((Path.home() / '.imagine-demo/c08-identifiants.json').read_text(encoding='utf-8'))
    client = http.login(base, creds['accounts']['actif'])
    nonce_meta, nonce = http.fetch(base, '/wp-admin/admin-ajax.php?action=rest-nonce', client)
    if nonce_meta['status'] != 200 or len(nonce.strip()) != 10:
        raise RuntimeError('Nonce natif de la session de test indisponible.')
    checks, responses = {}, {}
    def probe(label):
        for name, path in {'page': '/c08-article-reserve-article/', 'rest': '/wp-json/wp/v2/posts/' + str(aid),
                           'flux': '/?feed=rss2', 'oembed': '/wp-json/oembed/1.0/embed?url=' + base + '/c08-article-reserve-article/'}.items():
            meta, body = http.fetch(base, path, client, headers={'X-WP-Nonce': nonce.strip()})
            responses[label + ':' + name] = meta
            checks[label + ':' + name + ':200'] = meta['status'] == 200
            checks[label + ':' + name + ':ferme'] = http.WITNESS not in body
            checks[label + ':' + name + ':prive'] = 'private' in meta['headers'].get('cache-control', '') and 'no-store' in meta['headers'].get('cache-control', '')
    try:
        changed = json.loads(c08.b00.wp('eval', 'update_option("imagine_acces_plans","invalide-c08");echo wp_json_encode(get_option("imagine_acces_plans"));')['stdout'])
        checks['configuration:readback_invalide'] = changed == 'invalide-c08'
        probe('configuration-invalide')
        code = 'update_option("imagine_acces_plans",json_decode(' + json.dumps(json.dumps(original['plans'])) + ',true));echo wp_json_encode(get_option("imagine_acces_plans"));'
        checks['configuration:readback_restaure'] = json.loads(c08.b00.wp('eval', code)['stdout']) == original['plans']
        changed = c08.b00.wp('eval', 'update_post_meta(' + str(aid) + ',"imagine_numero_id",0);echo get_post_meta(' + str(aid) + ',"imagine_numero_id",true);')['stdout'].strip()
        checks['contenu:readback_numero_invalide'] = changed == '0'
        probe('numero-invalide')
    finally:
        code = 'update_option("imagine_acces_plans",json_decode(' + json.dumps(json.dumps(original['plans'])) + ',true));update_post_meta(' + str(aid) + ',"imagine_numero_id",' + json.dumps(original['numero']) + ');echo wp_json_encode(["plans"=>get_option("imagine_acces_plans"),"numero"=>get_post_meta(' + str(aid) + ',"imagine_numero_id",true)]);'
        restored = json.loads(c08.b00.wp('eval', code)['stdout'])
        checks['restauration_finale_exacte'] = restored == original
        meta, body = http.fetch(base, '/c08-article-reserve-article/', client)
        checks['restauration_abonne_complet'] = meta['status'] == 200 and http.WITNESS in body
        failures = [k for k, v in checks.items() if not v]
        record = {'scope': c08.b00.SLUG, 'total': len(checks), 'passed': len(checks)-len(failures), 'failures': failures,
                  'checks': checks, 'responses': responses, 'restoration_exact': restored == original}
        (c08.PROOF / 'faults.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: record[k] for k in ['scope', 'total', 'passed', 'failures', 'restoration_exact']}, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    run()
