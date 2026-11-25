"""C14 : vrais cookies WP et téléchargement privé ; aucune preuve avec secrets."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c14
from b00_fixtures import fixture_data, dummy_pdf


def verify():
    c14.c10.guard()
    http = c14.module('c14_transport', 'c12-http.py')
    fetch = c14.module('c14_pdf_transport', 'c11-verifier.py').fetch
    wp = c14.wp
    f = wp('echo wp_json_encode(get_option("imagine_c09_fixture"));')
    m = wp('echo wp_json_encode(get_option("imagine_demo_manifest"));')
    uid, oid = f['users']['P-NUMERO'], f['orders']['P-NUMERO']
    issue, other = m['demo-2026-t1'], m['demo-2026-t2']
    articles = wp('''$out=[];foreach(['demo-2026-t1-reserve-1','demo-2026-t2-reserve-1'] as $slug){$p=get_page_by_path($slug,OBJECT,'post');if(!$p){throw new RuntimeException('Article B00 absent');}$out[]=['id'=>$p->ID,'path'=>parse_url(get_permalink($p),PHP_URL_PATH),'witness'=>preg_match('/CONTENU_FICTIF_RESERVE_[A-Z0-9_-]+/',$p->post_content,$match)?$match[0]:throw new RuntimeException('Sentinelle C14 absente')];}echo wp_json_encode($out);''')
    bought, excluded = articles
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    client = http.login(accounts['P-NUMERO'])
    checks = {}
    # Les écritures sont limitées à la commande C09 nommée et vérifiées avant chaque action.
    guard = '$o=wc_get_order(' + str(oid) + ');if(!$o||$o->get_meta("_imagine_c09_fixture")!=="P-NUMERO"||(int)$o->get_customer_id()!==' + str(uid) + '){throw new RuntimeException("Cible commande C14 refusée");}'
    before = wp(guard + 'echo wp_json_encode(["status"=>$o->get_status(),"paid"=>$o->get_date_paid()?->getTimestamp(),"completed"=>$o->get_date_completed()?->getTimestamp(),"modified"=>$o->get_date_modified()?->getTimestamp()]);')
    refund_id = None
    try:
        code, headers, body = http.fetch(bought['path'], client)
        checks['V_NUM_article_achete_HTTP_complet'] = code == 200 and bought['witness'] in body
        checks['HTTP_article_cache_prive'] = 'no-store' in headers.get('cache-control', '') and 'private' in headers.get('cache-control', '')
        code, _, body = http.fetch(excluded['path'], client)
        checks['V_NUM_autre_article_HTTP_ferme'] = code == 200 and excluded['witness'] not in body and 'data-imagine-bloc="abonnement"' in body
        expected = dummy_pdf(next(row['label'] for row in fixture_data()['issues'] if row['slug'] == 'demo-2026-t1'))
        path = '/?imagine_pdf=' + str(issue)
        code, headers, data = fetch(http.BASE, path, client)
        checks['V_NUM_PDF_achete_octets_exacts'] = code == 200 and data == expected and headers.get('content-type', '').startswith('application/pdf')
        checks['HTTP_PDF_cache_prive'] = 'no-store' in headers.get('cache-control', '') and 'private' in headers.get('cache-control', '')
        code, _, data = fetch(http.BASE, '/?imagine_pdf=' + str(other), client)
        checks['V_NUM_autre_PDF_HTTP_ferme'] = code == 200 and b'%PDF-' not in data and b'data-imagine-pdf-bloc="abonnement"' in data
        code, _, data = fetch(http.BASE, path)
        checks['PDF_anonyme_apres_acheteur_ferme'] = code == 200 and b'%PDF-' not in data and b'data-imagine-pdf-bloc="connexion"' in data
        code, _, body = http.fetch(bought['path'])
        checks['article_anonyme_apres_acheteur_ferme'] = code == 200 and bought['witness'] not in body
        # REST vraiment authentifié, avec nonce natif ; pas un faux cookie ignoré.
        nonce_status, _, nonce = http.fetch('/wp-admin/admin-ajax.php?action=rest-nonce', client)
        code, _, body = http.fetch('/wp-json/wp/v2/users/me', client, headers={'X-WP-Nonce': nonce.strip()})
        checks['REST_session_reellement_authentifiee'] = nonce_status == 200 and code == 200 and json.loads(body)['id'] == uid
        code, _, body = http.fetch('/wp-json/wp/v2/posts/' + str(bought['id']), client, headers={'X-WP-Nonce': nonce.strip()})
        checks['REST_achete_complet'] = code == 200 and bought['witness'] in json.loads(body)['content']['rendered']
        for who, visitor, hs in [('anonyme', None, {}), ('acheteur', client, {'X-WP-Nonce': nonce.strip()})]:
            code, _, body = http.fetch('/wp-json/wp/v2/posts/' + str(excluded['id']), visitor, headers=hs)
            checks['REST_autre_' + who + '_ferme'] = code == 200 and excluded['witness'] not in body
        for status in ['pending', 'on-hold', 'failed', 'cancelled', 'refunded']:
            wp(guard + '$o->set_status(' + json.dumps(status) + ');$o->save();echo wp_json_encode(wc_get_order($o->get_id())->get_status()===' + json.dumps(status) + ');')
            code, _, body = http.fetch(bought['path'], client)
            checks[status + '_article_HTTP_ferme_meme_session'] = code == 200 and bought['witness'] not in body
            code, _, data = fetch(http.BASE, path, client)
            checks[status + '_PDF_HTTP_ferme_meme_session'] = code == 200 and b'%PDF-' not in data
        wp(guard + '$o->set_status("processing");$o->save();echo wp_json_encode(wc_get_order($o->get_id())->get_status()==="processing");')
        # Remboursement natif sans transfert financier (commande de fixture à zéro).
        refund_id = wp(guard + '$r=wc_create_refund(["order_id"=>$o->get_id(),"amount"=>0,"refund_payment"=>false,"restock_items"=>false,"reason"=>"FICTIF C14 sans transfert"]);if(is_wp_error($r)){throw new RuntimeException("Refund C14 impossible");}echo wp_json_encode($r->get_id());')
        code, _, body = http.fetch(bought['path'], client)
        checks['remboursement_natif_article_HTTP_revoque'] = code == 200 and bought['witness'] not in body
        code, _, data = fetch(http.BASE, path, client)
        checks['remboursement_natif_PDF_HTTP_revoque'] = code == 200 and b'%PDF-' not in data
        for name, route in [('ancienne_URL', '/wp-content/uploads/imagine-demo/demo-2026-t1.pdf'),
                            ('REST_media', '/wp-json/wp/v2/media/' + str(m['demo-2026-t1-pdf']))]:
            code, _, data = fetch(http.BASE, route, client)
            checks[name + '_aucun_PDF_direct'] = code in (401, 403, 404) and b'%PDF-' not in data
        admin = http.login(accounts['E-ADMIN'])
        pid = wp('echo wp_json_encode(get_page_by_path("c14-numero-fictif",OBJECT,"product")->ID);')
        code, _, body = http.fetch('/wp-admin/post.php?post=' + str(pid) + '&action=edit', admin)
        checks['champ_produit_natif_visible_admin'] = code == 200 and 'name="imagine_achat_numero_id"' in body and str(issue) in body
        code, _, body = http.fetch('/wp-admin/post.php?post=' + str(pid) + '&action=edit', client)
        checks['client_sans_edition_produit'] = (code in (401, 403) or 'woocommerce-MyAccount' in body) and 'name="imagine_achat_numero_id"' not in body
    finally:
        if refund_id is not None:
            wp(guard + '$r=wc_get_order(' + str(refund_id) + ');if($r&&$r->get_type()==="shop_order_refund"&&$r->get_parent_id()===$o->get_id()){$r->delete(true);}echo wp_json_encode(!wc_get_order(' + str(refund_id) + '));')
        wp(guard + '$old=json_decode(' + json.dumps(json.dumps(before)) + ',true);$o->set_status($old["status"]);$o->set_date_paid($old["paid"]);$o->set_date_completed($old["completed"]);$o->set_date_modified($old["modified"]);$o->save();echo "true";')
        after = wp(guard + 'echo wp_json_encode(["status"=>$o->get_status(),"paid"=>$o->get_date_paid()?->getTimestamp(),"completed"=>$o->get_date_completed()?->getTimestamp(),"modified"=>$o->get_date_modified()?->getTimestamp()]);')
        checks['commande_profil_restauree'] = after == before
        code, _, data = fetch(http.BASE, '/?imagine_pdf=' + str(issue), client)
        checks['PDF_achete_final_retabli'] = code == 200 and data == expected
        code, _, body = http.fetch(bought['path'], client)
        checks['article_achete_final_retabli'] = code == 200 and bought['witness'] in body
    failures = [k for k,v in checks.items() if v is not True]
    print('C14 HTTP :', len(checks) - len(failures), '/', len(checks), '; échecs :', failures, flush=True)
    if failures:
        (c14.PROOF / 'http-echec.json').write_text(json.dumps(checks, indent=2, ensure_ascii=False), encoding='utf-8')
        raise RuntimeError('Recette C14 HTTP échouée')
    return checks


if __name__ == '__main__':
    verify()
