"""C21 real native admin POST/AJAX/ZIP; disposable account only, no confirmation email."""
from pathlib import Path
from html import unescape
from urllib.parse import urlencode, urlsplit
import hashlib, importlib.util, io, json, re, sys, zipfile
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c21
spec = importlib.util.spec_from_file_location('c21_http', Path(__file__).with_name('c12-http.py'))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)


def request(client, kind, user):
    path = '/wp-admin/' + ('export-personal-data.php' if kind == 'export' else 'erase-personal-data.php')
    s, _, text = h.fetch(path, client)
    assert s == 200 and 'name="send_confirmation_email"' in text
    nonce = re.search(r'name="_wpnonce" value="([^"]+)"', text)
    action = 'export_personal_data' if kind == 'export' else 'remove_personal_data'
    values = {'action': 'add_' + action + '_request', 'type_of_action': action,
        'username_or_email_for_privacy_request': 'imagine-c21-fictif', '_wpnonce': unescape(nonce[1])}
    # Deliberately omit send_confirmation_email : existing native admin route.
    s, _, text = h.fetch(path, client, urlencode(values).encode())
    assert s == 200
    record = c21.wp('$f=get_option("imagine_c21_fixture");$ids=get_posts(["post_type"=>"user_request","post_status"=>"any","numberposts"=>-1,"fields"=>"ids"]);$r=[];foreach($ids as $id){$q=wp_get_user_request($id);if($q&&$q->email===get_userdata($f["user"])->user_email&&$q->action_name===' + json.dumps(action) + '){$f["requests"][]= $id;update_option("imagine_c21_fixture",$f,false);$r=["id"=>$id,"status"=>$q->status];break;}}echo wp_json_encode($r);')
    assert record['status'] == 'request-confirmed'
    s, _, text = h.fetch(path, client)
    span = re.search(r'<(?:span|div) class="(?:export|remove)-personal-data[^>]+data-request-id="' + str(record['id']) + r'"[^>]*>', text)
    assert span, 'Native request row missing'
    nonce = re.search(r'data-nonce="([^"]+)"', span[0])[1]
    return record, unescape(nonce), text


def ajax(client, kind, rid, nonce, index, page=1):
    fields = {'action': 'wp-privacy-' + ('export' if kind == 'export' else 'erase') + '-personal-data',
        'id': str(rid), 'security': nonce, 'exporter' if kind == 'export' else 'eraser': str(index),
        'page': str(page), 'sendAsEmail': 'false'}
    s, _, text = h.fetch('/wp-admin/admin-ajax.php', client, urlencode(fields).encode())
    try: result = json.loads(text)
    except ValueError: raise RuntimeError('Native AJAX returned non-JSON status ' + str(s)) from None
    return s, result


def business_schedule():
    # Only WCS report-cache jobs are volatile; every payment/renewal/action/log remains exact.
    return c21.wp(r'''global $wpdb;$a=$wpdb->prefix.'actionscheduler_actions';$l=$wpdb->prefix.'actionscheduler_logs';
$out=['actions'=>$wpdb->get_results("SELECT * FROM $a WHERE hook<>'wcs_report_update_cache' ORDER BY action_id",ARRAY_A),
'logs'=>$wpdb->get_results("SELECT l.* FROM $l l INNER JOIN $a a ON a.action_id=l.action_id WHERE a.hook<>'wcs_report_update_cache' ORDER BY l.log_id",ARRAY_A)];
$out['action8793']=$wpdb->get_row("SELECT * FROM $a WHERE action_id=8793",ARRAY_A);echo wp_json_encode($out);''')


def run(label):
    c21.c19.c18.c17.profils.guard('imagine-test-demo')
    checks = {}; observation = {}
    schedule_before = business_schedule()
    baseline = json.loads((c21.PROOF / 'baseline.json').read_text(encoding='utf-8'))['native']
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    admin = h.login(accounts['E-ADMIN']); reader = h.login(accounts['A-CARTE'])
    fixture = c21.wp('echo wp_json_encode(get_option("imagine_c21_fixture",null));')
    if fixture is None:
        c21.fixture('setup')
        fixture = c21.wp('echo wp_json_encode(get_option("imagine_c21_fixture"));')
    # Include exact C17 audit rows in disposable cleanup, even after a prior interrupted setup.
    c21.wp('global $wpdb;$f=get_option("imagine_c21_fixture");foreach($wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE \'imagine_reglages_journal_%\'",ARRAY_A) as $r){$v=maybe_unserialize($r["option_value"]);if(($v["option"]??"")===Imagine\\Site\\Justificatifs::PREFIX.$f["user"])$f["options"][]=$r["option_name"];} $f["options"]=array_values(array_unique($f["options"]));update_option("imagine_c21_fixture",$f,false);echo "true";')
    retention_before = c21.wp('global $wpdb;$o=[];foreach($wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE \'%retention%\' OR option_name LIKE \'%erasure%\'",ARRAY_A) as $r)$o[$r["option_name"]]=maybe_unserialize($r["option_value"]);echo wp_json_encode($o);')
    try:
        reg = c21.fixture('registration'); checks['callbacks_natifs_declares'] = reg == {'exporter': True, 'eraser': True}
        er, nonce, page = request(admin, 'export', fixture['user'])
        checks['creation_demande_admin_sans_email'] = er['status'] == 'request-confirmed'
        s, refused = ajax(reader, 'export', er['id'], nonce, 1)
        checks['lecteur_export_refuse'] = not refused.get('success')
        s, refused = ajax(admin, 'export', er['id'], 'invalide', 1)
        checks['nonce_export_invalide_refuse'] = s == 403 or refused.get('success') is False
        exporters = c21.wp('echo wp_json_encode(array_keys(apply_filters("wp_privacy_personal_data_exporters",[])));')
        all_rows = []; url = None; calls = []
        for index, key in enumerate(exporters, 1):
            for page_num in range(1, 30):
                s, result = ajax(admin, 'export', er['id'], nonce, index, page_num)
                if not result.get('success'): raise RuntimeError('Native exporter failure: ' + key + ' ' + json.dumps(result))
                data = result['data']; all_rows.extend(data.get('data', [])); calls.append([key, page_num, data['done']])
                url = data.get('url', url)
                if data['done']: break
            else: raise RuntimeError('Exporter pagination did not finish')
        checks['export_natif_tous_callbacks'] = len(set(c[0] for c in calls)) == len(exporters)
        checks['export_Imagine_deux_pages_reelles'] = [c[1:] for c in calls if c[0] == 'imagine-site'] == [[1, False], [2, True]]
        assert url and url.startswith(h.BASE + '/')
        from urllib.request import Request
        response = admin.open(Request(url), timeout=45)
        archive = response.read()
        z = zipfile.ZipFile(io.BytesIO(archive))
        text = '\n'.join(z.read(n).decode('utf-8') for n in z.namelist())
        grouped = json.loads(z.read('export.json'))
        checks['archive_native_html_json'] = set(z.namelist()) == {'index.html', 'export.json'}
        expected = {'imagine-meta', 'imagine-decouverte', 'imagine-justificatif', 'imagine-postal', 'imagine-gel', 'imagine-audit', 'imagine-brouillon'}
        checks['toutes_donnees_inventaire_dans_archive'] = expected <= set(r['group_id'] for r in all_rows)
        checks['achat_et_bloc_exportes_nativement'] = 'numéros achetés' in text and 'Début de bloc postal' in text and 'Début de grâce' in text and 'Fin de grâce' in text
        docs = [f['value'] for r in all_rows if r['group_id'] == 'imagine-justificatif' for f in r['data'] if f['name'] == 'Document déposé (base64)']
        import base64
        checks['document_exporte_octets_exacts'] = len(docs) == 1 and hashlib.sha256(base64.b64decode(docs[0])).hexdigest() == fixture['document_sha256']
        checks['aucun_secret_note_ou_reference_paiement'] = not any(x in text for x in ['C21-SECRET-TOKEN', 'C21-NOTE-INTERNE-INTERDITE', 'C21-TOKEN-PRIVE', fixture['doc'], 'c17-' + Path(fixture['doc']).stem[4:]])
        checks['email_technique_absent_archive_entete_comprise'] = '.invalid' not in text and '[sans adresse électronique]' in text
        own_text = json.dumps([r for r in all_rows if r['group_id'].startswith('imagine-')], ensure_ascii=False)
        checks['autres_personnes_non_divulguees'] = 'C21-AUTRE-PERSONNE' not in own_text and 'C21-AUTRE-BENEFICIAIRE' not in own_text
        observation.update(exporters=exporters, export_calls=calls, zip_sha256=hashlib.sha256(archive).hexdigest(), zip_members=z.namelist(), groups=sorted(set(r['group_id'] for r in all_rows)))
        rem, nonce, _ = request(admin, 'erase', fixture['user'])
        checks['effacement_demande_admin_sans_email'] = rem['status'] == 'request-confirmed'
        s, refused = ajax(reader, 'erase', rem['id'], nonce, 1)
        checks['lecteur_effacement_refuse'] = not refused.get('success')
        s, refused = ajax(admin, 'erase', rem['id'], 'invalide', 1)
        checks['nonce_effacement_invalide_refuse'] = s == 403 or refused.get('success') is False
        erasers = c21.wp('echo wp_json_encode(array_keys(apply_filters("wp_privacy_personal_data_erasers",[])));')
        erasure = []
        for index, key in enumerate(erasers, 1):
            for page_num in range(1, 30):
                s, result = ajax(admin, 'erase', rem['id'], nonce, index, page_num)
                if not result.get('success'): raise RuntimeError('Native eraser failure: ' + key + ' ' + json.dumps(result))
                data = result['data']; erasure.append({'key': key, 'page': page_num, **data})
                if data['done']: break
            else: raise RuntimeError('Eraser pagination did not finish')
        readback = c21.fixture('inspect')
        checks['options_et_marqueurs_effaces'] = readback['imagine_sans_email'] == readback['imagine_email_confirme'] == '' and readback['decouverte'] is None and readback['justificatif'] is None
        checks['document_et_brouillon_effaces'] = not readback['document_exists'] and not readback['draft_exists']
        remaining = c21.wp('$f=get_option("imagine_c21_fixture");$e=apply_filters("wp_privacy_personal_data_exporters",[]);echo wp_json_encode(call_user_func($e["imagine-site"]["callback"],get_userdata($f["user"])->user_email,1));')
        checks['relecture_export_Imagine_vide'] = remaining == {'data': [], 'done': True}
        checks['commandes_abonnement_actif_comportement_natif_seul'] = readback['native'][str(fixture['orders'][0])] == ['pending', fixture['user']] and readback['native'][str(fixture['orders'][1])] == ['active', fixture['user']]
        checks['autre_beneficiaire_partage_preserve'] = 'C21-AUTRE-BENEFICIAIRE' in json.dumps(readback['residual_options']) and 'C21 BENEFICIAIRE' not in json.dumps(readback['residual_options'])
        checks['gel_vide_conserve_numero_et_cloture'] = readback['residual_options']['imagine_envoi_gel_C21-FICTIF']['observations'] == [] and readback['residual_options']['imagine_envoi_gel_C21-FICTIF']['blocs'] == []
        checks['effaceur_Imagine_sans_retenue_silencieuse'] = all(not r['items_retained'] for r in erasure if r['key'] == 'imagine-site')
        repeat = c21.wp('$e=apply_filters("wp_privacy_personal_data_erasers",[]);echo wp_json_encode(call_user_func($e["imagine-site"]["callback"],"c21-sans-email@compte.invalid",2));')
        checks['effacement_idempotent'] = repeat == {'items_removed': False, 'items_retained': False, 'messages': [], 'done': True}
        observation.update(erasers=erasers, erasure=erasure, after_erasure=readback)
    finally:
        cleanup = c21.fixture('cleanup')
        checks['compte_fixture_supprime_fin'] = all(cleanup.values())
        retention_after = c21.wp('global $wpdb;$o=[];foreach($wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE \'%retention%\' OR option_name LIKE \'%erasure%\'",ARRAY_A) as $r)$o[$r["option_name"]]=maybe_unserialize($r["option_value"]);echo wp_json_encode($o);')
        checks['reglages_conservation_inchanges'] = retention_before == retention_after
        after = c21.c19.c18.state()
        comparison_before = json.loads(json.dumps(baseline))
        comparison_after = json.loads(json.dumps(after))
        for v in (comparison_before, comparison_after):
            for key in ('actionscheduler_actions', 'actionscheduler_logs'):
                v['native_fingerprints'].pop(key, None)
        checks['etat_natif_profils_C09_inchange'] = comparison_before == comparison_after
        checks['actions_metier_C09_exactes'] = schedule_before == business_schedule()
        observation['remaining_export'] = remaining if 'remaining' in locals() else None
        observation['erasure_repeat'] = repeat if 'repeat' in locals() else None
        c21.save(label, {'checks': checks, 'total': len(checks), 'failures': [k for k, v in checks.items() if v is not True],
            'observation': observation, 'retention_before': retention_before, 'retention_after': retention_after,
            'native_before': baseline, 'native_after': after, 'cleanup': cleanup})
    return int(not all(checks.values()))

if __name__ == '__main__':
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else 'http-final'))
