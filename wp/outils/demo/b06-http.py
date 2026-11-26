"""B06 : vrais GET/POST natifs, sessions éphémères, restauration exacte hors attribut P-COOP."""
import sys
sys.dont_write_bytecode = True
import json, re, html
from urllib.parse import urlencode
from urllib.request import Request, build_opener
from urllib.error import HTTPError
from html.parser import HTMLParser
import b06, c23
BASE = c23.BASE
wp, php = b06.wp, b06.b05.php_json
MARKER = 'B06TemoinConfidentielReserve2026'

class Inputs(HTMLParser):
    def __init__(self):
        super().__init__(); self.values = {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'input' and a.get('name'):
            self.values[a['name']] = a.get('value', '')

def request(path, session=None, data=None):
    c23.validate_path(path)
    headers = {'User-Agent':'Imagine-B06/1.0'}
    if session:
        headers['Cookie'] = session['cookie']
        if 'wp-json' in path or 'rest_route' in path: headers['X-WP-Nonce'] = session['nonce']
    req = Request(BASE+path, data=urlencode(data).encode() if data is not None else None, headers=headers, method='POST' if data is not None else 'GET')
    try: r = build_opener(c23.DemoRedirect()).open(req, timeout=45)
    except HTTPError as e: r=e
    with r:
        return r.code, dict(r.headers), r.read().decode('utf-8','replace'), r.url

def profile(session, uid, oui, badnonce=False):
    path = '/wp-admin/user-edit.php?user_id='+str(uid)
    code,headers,body,url = request(path, session)
    assert code == 200 and 'id="your-profile"' in body and 'name="imagine_cooperateur_nonce"' in body
    fields = Inputs(); fields.feed(body)
    native = wp('$u=get_userdata('+str(uid)+');echo wp_json_encode(["nickname"=>get_user_meta($u->ID,"nickname",true),"email"=>$u->user_email]);')
    data = {**native, 'action':'update','user_id':str(uid),'from':'profile','_wpnonce':fields.values['_wpnonce'],
            'imagine_cooperateur_present':'1','imagine_cooperateur_nonce':'faux' if badnonce else fields.values['imagine_cooperateur_nonce']}
    if oui: data['imagine_cooperateur_oui']='1'
    code,headers,body,url = request(path, session, data)
    if badnonce:
        return code == 403 and 'Statut coopérateur non modifié' in html.unescape(body)
    return code == 200 and 'updated=true' in url and 'id="your-profile"' in body

def snapshot(ids):
    return wp('''global $wpdb;$ids='''+php(ids)+''';$list=implode(',',array_map('intval',$ids));echo wp_json_encode([
'users'=>$wpdb->get_results("SELECT * FROM {$wpdb->users} WHERE ID IN ($list) ORDER BY ID",ARRAY_A),
'meta'=>$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE user_id IN ($list) ORDER BY umeta_id",ARRAY_A)]);''')

def restore(old, ids, coop):
    wp('''global $wpdb;$old='''+php(old)+''';$ids='''+php(ids)+''';$coop='''+str(coop)+''';$list=implode(',',array_map('intval',$ids));
foreach($old['users'] as $r){if($wpdb->update($wpdb->users,$r,['ID'=>$r['ID']])===false)throw new RuntimeException('Restauration compte refusée.');}
$where="user_id IN ($list) AND NOT (user_id=$coop AND meta_key='imagine_cooperateur')";
$oldmeta=array_values(array_filter($old['meta'],static fn($r)=>!((int)$r['user_id']===$coop&&$r['meta_key']==='imagine_cooperateur')));
$keep=array_column($oldmeta,'umeta_id');$extra=$keep?' AND umeta_id NOT IN ('.implode(',',array_map('intval',$keep)).')':'';
if($wpdb->query("DELETE FROM {$wpdb->usermeta} WHERE $where".$extra)===false)throw new RuntimeException('Restauration méta refusée.');
foreach($oldmeta as $r){$exists=$wpdb->get_var($wpdb->prepare("SELECT umeta_id FROM {$wpdb->usermeta} WHERE umeta_id=%d",$r['umeta_id']));
if(($exists?$wpdb->update($wpdb->usermeta,$r,['umeta_id'=>$r['umeta_id']]):$wpdb->insert($wpdb->usermeta,$r))===false)throw new RuntimeException('Restauration ligne refusée.');}
foreach($ids as $id){clean_user_cache($id);wp_cache_delete($id,'user_meta');}echo 'true';''')
    new = snapshot(ids)
    without = lambda x: {'users':x['users'],'meta':[r for r in x['meta'] if not (int(r['user_id'])==coop and r['meta_key']=='imagine_cooperateur')]}
    assert without(old) == without(new), 'Restauration exacte comptes/métas divergente'

def invariant(coop):
    value = b06.state()
    value['native']['native_fingerprints']['usermeta'] = wp('''global $wpdb;$rows=$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE NOT (user_id='''+str(coop)+''' AND meta_key='imagine_cooperateur') AND meta_key NOT IN ('session_tokens','_woocommerce_persistent_cart_1','_last_update','wc_last_active') ORDER BY umeta_id",ARRAY_A);echo wp_json_encode(hash('sha256',serialize($rows)));''')
    value['options_imagine'] = wp('''global $wpdb;$o=[];foreach($wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name LIKE 'imagine_%' ORDER BY option_id",ARRAY_A) as $r){$v=maybe_unserialize($r['option_value']);if(str_starts_with($r['option_name'],'imagine_reglages_journal_')&&is_array($v)&&str_starts_with($v['option']??'','imagine_cooperateur_'))continue;$o[]=$r;}echo wp_json_encode(hash('sha256',serialize($o)));''')
    return value

def run(label):
    assert not (b06.PROOF/(label+'.json')).exists()
    identity = b06.guard()
    fixture = json.loads((b06.PROOF/'seed-V2.json').read_text(encoding='utf-8'))['fixture']
    accounts = wp('''$f=get_option('imagine_c09_fixture');$a=get_option('imagine_c08_fixture');echo wp_json_encode(['admin'=>get_user_by('login','admin')->ID,'coop'=>$f['users']['P-COOP'],'active'=>$f['users']['A-CARTE'],'plain'=>$f['users']['V-INSCRIT'],'article'=>$a['article'],'article_path'=>wp_parse_url(get_permalink($a['article']),PHP_URL_PATH)]);''')
    ids = [accounts[k] for k in ['admin','coop','active','plain']]
    prior = snapshot(ids)
    baseline = invariant(accounts['coop'])
    child = fixture['pages'][2]
    original_page = wp('global $wpdb;echo wp_json_encode($wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->posts} WHERE ID=%d",'+str(child['id'])+'),ARRAY_A));')
    checks = {}
    sources = b06.hashes(b06.NAMES)
    error = None
    try:
        sessions = wp('''$ids='''+php({k:accounts[k] for k in ['admin','coop','active','plain']})+''';$out=[];foreach($ids as $key=>$id){$expiration=time()+3600;$token=WP_Session_Tokens::get_instance($id)->create($expiration);$logged=wp_generate_auth_cookie($id,$expiration,'logged_in',$token);$auth=wp_generate_auth_cookie($id,$expiration,'auth',$token);$_COOKIE[LOGGED_IN_COOKIE]=$logged;wp_set_current_user($id);$out[$key]=['cookie'=>LOGGED_IN_COOKIE.'='.$logged.'; '.AUTH_COOKIE.'='.$auth.'; tk_ai='.bin2hex(random_bytes(16)),'nonce'=>wp_create_nonce('wp_rest')];}echo wp_json_encode($out);''')
        checks['ecran_admin_pose_native'] = profile(sessions['admin'], accounts['coop'], True)
        attr = wp('echo wp_json_encode(get_user_meta('+str(accounts['coop'])+',"imagine_cooperateur",true));')
        checks['attribut_persistant_relu'] = attr['cooperateur'] is True and attr['source']=='administration'
        checks['nonce_invalide_refuse'] = profile(sessions['admin'], accounts['coop'],False,True)
        checks['nonce_refuse_sans_mutation'] = wp('echo wp_json_encode(get_user_meta('+str(accounts['coop'])+',"imagine_cooperateur",true));') == attr
        wp('global $wpdb;$id='+str(child['id'])+';$wpdb->update($wpdb->posts,["post_content"=>'+php(MARKER)+',"post_excerpt"=>'+php(MARKER)+'],["ID"=>$id]);clean_post_cache($id);echo wp_json_encode(get_post($id)->post_content);')
        checks['temoin_sous_page_persistant'] = wp('echo wp_json_encode(get_post('+str(child['id'])+')->post_content);') == MARKER
        for audience in ['coop','admin']:
            for p in fixture['pages']:
                code,headers,body,url = request(p['path'], sessions[audience])
                checks[audience+'_page_'+str(p['id'])] = code==200 and p['title'] in html.unescape(body) and 'data-imagine-cooperateurs-refus' not in body and (p['id']!=child['id'] or MARKER in body)
            code,headers,body,url = request('/wp-json/wp/v2/pages/'+str(child['id']),sessions[audience])
            checks[audience+'_REST_inverse'] = code==200 and MARKER in body
        for audience in ['anon','active','plain']:
            session = sessions.get(audience)
            for p in fixture['pages']:
                code,headers,body,url = request(p['path'],session)
                checks[audience+'_page_'+str(p['id'])] = code==200 and 'data-imagine-cooperateurs-refus' in body and MARKER not in body
                checks[audience+'_cache_'+str(p['id'])] = 'no-store' in next((v for k,v in headers.items() if k.lower()=='cache-control'),'')
            for route in ['/wp-json/wp/v2/pages/'+str(child['id']), '/?rest_route=/wp/v2/pages/'+str(child['id']), '/wp-json/wp/v2/pages/'+str(child['id'])+'?context=edit']:
                code,headers,body,url = request(route,session)
                checks[audience+'_rest_'+str(len(checks))] = code==403 and json.loads(body).get('code')=='imagine_cooperateurs_reserve' and MARKER not in body
            code,headers,body,url = request('/wp-json/wp/v2/pages?include='+str(child['id']),session)
            checks[audience+'_rest_liste_exclut'] = code==200 and json.loads(body)==[]
            code,headers,body,url = request('/?feed=rss2&post_type=page&posts_per_rss=100',session)
            checks[audience+'_flux_existant_sans_temoin'] = code==200 and '<item>' in body and MARKER not in body and child['path'] not in body
            code,headers,body,url = request('/?s='+MARKER,session)
            main = c23.search_results_body(body.encode()).decode()
            checks[audience+'_recherche_existe_sans_temoin'] = code==200 and '<main' in body and MARKER not in main and child['path'] not in main
            code,headers,body,url = request('/wp-json/wp/v2/search?search='+MARKER,session)
            checks[audience+'_rest_recherche_exclut'] = code==200 and json.loads(body)==[]
        code,headers,body,url = request('/?s='+MARKER,sessions['coop'])
        checks['recherche_inverse_non_vide'] = code==200 and child['path'] in c23.search_results_body(body.encode()).decode()
        for audience in ['coop','active','plain']:
            code,headers,body,url = request('/mon-compte/', sessions[audience])
            checks[audience+'_compte_natif'] = code==200 and 'id="mon-statut-cooperateur"' in body and ('Coopérateur : oui' if audience=='coop' else 'Coopérateur : non') in html.unescape(body)
        # Le même article reste fermé pour le coopérateur ; l'abonné valide prouve le témoin.
        witness = 'Les lucioles violettes de C08 gardent le secret du village fictif.'
        code,headers,body,url = request(accounts['article_path'], sessions['active'])
        checks['article_temoin_abonne_ouvert'] = code==200 and witness in html.unescape(body)
        code,headers,body,url = request(accounts['article_path'], sessions['coop'])
        checks['statut_nouvre_jamais_article'] = code==200 and witness not in html.unescape(body) and 'Extrait public C08' in body
        code,headers,body,url = request('/wp-sitemap-posts-page-1.xml')
        checks['sitemap_http_noindex_natif'] = code==404 and MARKER not in body
        checks['ecran_admin_retrait_natif'] = profile(sessions['admin'],accounts['coop'],False)
        code,headers,body,url = request(child['path'],sessions['coop'])
        checks['retrait_referme_http'] = code==200 and 'data-imagine-cooperateurs-refus' in body and MARKER not in body
        checks['ecran_admin_repose_native'] = profile(sessions['admin'],accounts['coop'],True)
    except Exception as exc:
        error = type(exc).__name__ + ': ' + str(exc)
    finally:
        # La seule page temporairement remplie revient à ses octets exacts.
        wp('global $wpdb;$p='+php(original_page)+';if($wpdb->update($wpdb->posts,$p,["ID"=>$p["ID"]])===false)throw new RuntimeException("Restauration page refusée");clean_post_cache((int)$p["ID"]);echo "true";')
        restored = wp('global $wpdb;echo wp_json_encode($wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->posts} WHERE ID=%d",'+str(child['id'])+'),ARRAY_A));')
        checks['page_restauree_exacte'] = restored == original_page
        restore(prior, ids, accounts['coop'])
        checks['comptes_restauration_exacte_sauf_attribut_coop'] = True
        checks['options_actions_roles_abonnements_consentements_preserves'] = baseline == invariant(accounts['coop'])
        retained = wp('echo wp_json_encode(get_user_meta('+str(accounts['coop'])+',"imagine_cooperateur",true));')
        checks['P_COOP_seule_exception_conservee'] = isinstance(retained,dict) and retained['cooperateur'] is True and retained['source']=='administration'
        failures = [k for k,v in checks.items() if v is not True]
        b06.save(label, {'identity':identity,'checks':checks,'total':len(checks),'failures':failures,'error':error,'sources':sources,'pages':fixture['pages'],'retained':retained})
        print(json.dumps({'total':len(checks),'failures':failures,'error':error},ensure_ascii=False))
    assert not failures and error is None

if __name__=='__main__': run(sys.argv[1])
