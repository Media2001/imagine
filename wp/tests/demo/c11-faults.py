"""Défauts HTTP sur un seul canari C11 éphémère, restauré dans finally."""
from pathlib import Path
import importlib.util
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c10


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


def verify():
    site, _ = c10.guard()
    php = '''$m=get_option('imagine_demo_manifest');$name=bin2hex(random_bytes(16)).'.pdf';
    $path=\\Imagine\\Site\\PdfNumero::directory().'/'.$name;file_put_contents($path,'FICHIER INVALIDE C11');chmod($path,0600);
    $id=wp_insert_post(['post_type'=>'imagine_numero','post_status'=>'publish','post_name'=>'c11-canari-erreur-temporaire',
        'post_title'=>'Canari entièrement fictif C11 temporaire','post_date'=>'2000-01-01 12:00:00','post_date_gmt'=>'2000-01-01 11:00:00',
        'meta_input'=>['_imagine_c11_fixture'=>'http-fault','imagine_sortie'=>'2026-10-15','_imagine_pdf_blob'=>$name]]);
    echo wp_json_encode(['id'=>$id,'blob'=>$name,'valid'=>get_post_meta($m['demo-2026-t4'],'_imagine_pdf_blob',true)]);'''
    fixture = json.loads(c10.b00.wp('eval', php)['stdout'])
    cid = fixture['id']
    http = module('c08_http_fault', 'c08-verifier.py')
    verifier = module('c11_http_fault', 'c11-verifier.py')
    credentials = json.loads((Path.home() / '.imagine-demo/c08-identifiants.json').read_text(encoding='utf-8'))
    active = http.login(site['url'], credentials['accounts']['actif'])
    checks = {}
    guard = f'if(get_post_meta({cid},"_imagine_c11_fixture",true)!=="http-fault"){{throw new RuntimeException("Canari non détenu.");}}'
    try:
        for name, blob in [('corrompu', fixture['blob']), ('absent', '0' * 32 + '.pdf'), ('traversee', '../source/demo-2026-t4.pdf')]:
            c10.b00.wp('eval', guard + f'update_post_meta({cid},"_imagine_pdf_blob",' + json.dumps(blob) + ');')
            status, hs, body = verifier.fetch(site['url'], '/?imagine_pdf=' + str(cid), active)
            checks[name + ':ferme-avec-bloc'] = status == 200 and hs.get('content-type', '').startswith('text/html') and b'data-imagine-pdf-bloc="abonnement"' in body
            checks[name + ':sans-octets'] = b'IMAGINE - DEMONSTRATION FICTIVE' not in body and b'FICHIER INVALIDE C11' not in body
        c10.b00.wp('eval', guard + f'update_post_meta({cid},"_imagine_pdf_blob",' + json.dumps(fixture['valid']) + ');')
        status, hs, body = verifier.fetch(site['url'], '/?imagine_pdf=' + str(cid), active)
        checks['positif-retabli'] = status == 200 and hs.get('content-type') == 'application/pdf' and b'IMAGINE - DEMONSTRATION FICTIVE' in body
    finally:
        code = guard + '$p=\\Imagine\\Site\\PdfNumero::directory()."/".' + json.dumps(fixture['blob']) + ';if(is_file($p)){unlink($p);}' + f'wp_delete_post({cid},true);echo wp_json_encode(!get_post({cid})&&!file_exists($p));'
        checks['nettoyage-relu'] = json.loads(c10.b00.wp('eval', code)['stdout']) is True
    out = c10.ROOT / 'production/C-11/faults.json'
    out.write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Défauts HTTP C11 :', sum(checks.values()), '/', len(checks), '; échecs :', [k for k,v in checks.items() if not v])
    if not all(checks.values()):
        raise SystemExit(1)
    return checks


if __name__ == '__main__':
    verify()
