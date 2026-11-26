"""C21 fusion : vrais POST C16, AJAX natifs et ZIP relus, comptes jetables uniquement."""
from pathlib import Path
from html import unescape
from urllib.parse import urlencode
import hashlib, importlib.util, io, json, re, secrets, sys, zipfile
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c21

def load(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

native = load('c21_native_http', 'c21-http.py')
c16 = load('c21_C16_http', 'c16-http.py')
h = native.h

def run(label):
    c21.c19.c18.c17.profils.guard('imagine-test-demo')
    checks, evidence, requests, results, drafts = {}, {}, [], [], []
    before = c21.c19.c18.state(); schedule = native.business_schedule()
    password = secrets.token_urlsafe(36)
    uid = c21.wp('$login="imagine-c21-http-operateur";if(get_user_by("login",$login))throw new RuntimeException("Collision C21");$id=wp_insert_user(["user_login"=>$login,"user_pass"=>'+json.dumps(password)+',"user_email"=>"c21-http-operateur@example.org","role"=>"administrator"]);if(is_wp_error($id))throw new RuntimeException("Création refusée");echo wp_json_encode($id);')
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    admin = h.login(accounts['E-ADMIN'])
    operator = h.login({'login': 'imagine-c21-http-operateur', 'password': password})
    product = c21.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["tariffs"]["normal-1"]);')
    address = {'first_name':'C21CLIENTPRENOM', 'last_name':'C21CLIENTNOM', 'address_1':'21 RUE HTTP CLIENT FICTIF',
        'address_2':'', 'postcode':'1000', 'city':'C21VILLECLIENT', 'country':'BE'}
    def post(page, fields):
        return h.fetch(c16.PATH, operator, urlencode(dict(c16.form(page), **fields)).encode())
    def request(kind, user):
        path = '/wp-admin/' + ('export-personal-data.php' if kind == 'export' else 'erase-personal-data.php')
        s, _, text = h.fetch(path, admin); assert s == 200
        nonce = unescape(re.search(r'name="_wpnonce" value="([^"]+)"', text)[1])
        login = c21.wp('echo wp_json_encode(get_userdata('+str(user)+')->user_login);')
        action = 'export_personal_data' if kind == 'export' else 'remove_personal_data'
        s, _, _ = h.fetch(path, admin, urlencode({'action':'add_'+action+'_request','type_of_action':action,
            'username_or_email_for_privacy_request':login,'_wpnonce':nonce}).encode()); assert s == 200
        record = c21.wp('$ids=get_posts(["post_type"=>"user_request","post_status"=>"any","numberposts"=>-1,"fields"=>"ids"]);$out=[];foreach($ids as $id){$q=wp_get_user_request($id);if($q&&$q->email===get_userdata('+str(user)+')->user_email&&$q->action_name==='+json.dumps(action)+'){$out=["id"=>$id,"status"=>$q->status];break;}}echo wp_json_encode($out);')
        requests.append(record['id']); assert record['status'] == 'request-confirmed'
        s, _, text = h.fetch(path, admin); assert s == 200
        span = re.search(r'<(?:span|div) class="(?:export|remove)-personal-data[^>]+data-request-id="'+str(record['id'])+r'"[^>]*>', text)
        nonce = unescape(re.search(r'data-nonce="([^"]+)"', span[0])[1])
        callbacks = c21.wp('echo wp_json_encode(array_keys(apply_filters("wp_privacy_personal_data_'+('exporters' if kind == 'export' else 'erasers')+'",[])));')
        calls, url = [], None
        for i, key in enumerate(callbacks, 1):
            for page in range(1, 10):
                status, result = native.ajax(admin, kind, record['id'], nonce, i, page)
                assert status == 200 and result['success'], (key, status)
                data = result['data']; calls.append({'key':key,'page':page,**data}); url = data.get('url',url)
                if data['done']: break
            else: raise RuntimeError('Pagination incomplète')
        if kind == 'erase':
            assert not any(c.get('items_retained') for c in calls if c['key']=='imagine-site')
            return calls
        assert url and url.startswith(h.BASE+'/')
        archive = admin.open(url, timeout=45).read()
        z = zipfile.ZipFile(io.BytesIO(archive))
        assert set(z.namelist()) == {'index.html','export.json'}
        raw = {n:z.read(n).decode('utf-8') for n in z.namelist()}
        # Archiver les valeurs réellement lues, pas seulement des assertions de présence.
        evidence.setdefault('archives', []).append({'user':user, 'sha256':hashlib.sha256(archive).hexdigest(),
            'export_json':json.loads(raw['export.json']), 'html_sha256':hashlib.sha256(raw['index.html'].encode()).hexdigest(), 'calls':calls})
        return '\n'.join(raw.values()), calls
    try:
        for mode in ('email','sansmail'):
            s, _, first = h.fetch(c16.PATH,operator); assert s == 200
            client = {'mode':'nouveau','nom':'C21CLIENTNOM HTTP '+mode,'email':'c21-http-client@example.org'}
            if mode == 'sansmail': client.update(email='',sans_email='1')
            s, _, second = post(first,dict(client,c16_action='choisir')); assert s==200 and 'data-imagine-etape="2"' in second
            token = c16.form(second)['token']; key='imagine_c16_brouillon_'+str(uid)+'_'+token;drafts.append(key)
            s, _, third = post(second,dict(address,c16_action='preparer',produit=str(product),paiement='imagine_papier')); assert s==200 and 'data-imagine-etape="3"' in third
            s, _, done = post(third,{'c16_action':'creer','confirmer':'oui'}); assert s==200
            oid = int(re.search(r'data-imagine-commande="(\d+)"',done)[1])
            d = c21.wp('echo wp_json_encode(get_transient('+json.dumps(key)+'));')
            result = d['resultat']; results.append(result); user=result['client']
            checks['C16_POST_'+mode+'_vrai_resultat_client'] = result['commande']==oid and d['client']['mode']=='nouveau' and 'id' not in d['client'] and d['commande']['paiement']=='imagine_papier'
            if mode == 'email':
                text,calls = request('export',uid)
                checks['ZIP_operateur_absence_toutes_PII_client'] = all(v not in text for v in [*address.values(),client['email'],client['nom']] if v and v not in ('1000','BE'))
                own = [r for call in calls if call['key']=='imagine-site' for r in call.get('data',[])]
                checks['ZIP_operateur_activite_seule_exacte'] = len(own)==1 and own[0]['data']==[{'name':'Activité','value':'A préparé un brouillon'}]
                request('erase',uid)
                preserved = c21.wp('echo wp_json_encode(get_transient('+json.dumps(key)+'));')
                checks['AJAX_effacement_operateur_ne_detruit_pas_client'] = preserved == dict(d,qui=0)
            text,calls = request('export',user)
            rows = [r for call in calls if call['key']=='imagine-site' for r in call.get('data',[]) if r['group_id']=='imagine-brouillon']
            fields = {f['name']:f['value'] for f in rows[0]['data']} if len(rows)==1 else {}
            checks['ZIP_client_'+mode+'_valeurs_exactes'] = len(rows)==1 and json.loads(fields['client'])==d['client'] and json.loads(fields['commande'])=={'adresse':address,'produit':product} and fields['Mode de règlement']=='Mandat papier'
            checks['ZIP_client_'+mode+'_sans_note_ni_jeton_ni_operateur'] = token not in text and d['empreinte'] not in text and 'C16 — Commande fictive en attente, encodée par' not in text
            if mode == 'sansmail': checks['ZIP_sansmail_entete_ne_divulgue_pas_technique'] = '.invalid' not in text
            request('erase',user)
            checks['AJAX_client_'+mode+'_brouillon_efface_relecture'] = c21.wp('echo wp_json_encode(get_transient('+json.dumps(key)+')===false);')
            native_state = c21.wp('$r=json_decode('+json.dumps(json.dumps(result))+',true);$o=wc_get_order($r["commande"]);$s=wcs_get_subscription($r["souscription"]);echo wp_json_encode([$o->get_status(),$o->get_customer_id(),$s->get_status(),$s->get_customer_id()]);')
            checks['conservation_native_'+mode+'_inchangee'] = native_state==['pending',user,'pending',user]
    finally:
        cleanup = c21.wp('require_once ABSPATH."wp-admin/includes/user.php";$requests=json_decode('+json.dumps(json.dumps(requests))+',true);foreach($requests as $rid){$name=get_post_meta($rid,"_export_file_name",true);if($name&&basename($name)===$name)wp_delete_file(wp_privacy_exports_dir().$name);wp_delete_post($rid,true);} $results=json_decode('+json.dumps(json.dumps(results))+',true);foreach($results as $r){foreach(["souscription","commande"] as $k){$o=wc_get_order($r[$k]);if($o&&$o->get_customer_id()===$r["client"])$o->delete(true);}foreach(Imagine\\Site\\EnvoiNatif::releves((string)$r["souscription"]) as $e){}global $wpdb;$prefix=Imagine\\Site\\EnvoiNatif::RELEVE.$r["souscription"]."_";foreach($wpdb->get_col($wpdb->prepare("SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s",$wpdb->esc_like($prefix)."%")) as $k)delete_option($k);wp_delete_user($r["client"]);}foreach(json_decode('+json.dumps(json.dumps(drafts))+',true) as $k)delete_transient($k);wp_delete_user('+str(uid)+');echo wp_json_encode(!get_userdata('+str(uid)+'));')
        checks['comptes_jetables_supprimes'] = cleanup
        after = c21.c19.c18.state()
        for state in (before,after):
            for key in ('actionscheduler_actions','actionscheduler_logs'): state['native_fingerprints'].pop(key,None)
        checks['profils_C09_et_actions_metier_exacts'] = before==after and schedule==native.business_schedule()
        c21.save(label,{'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True], 'evidence':evidence,'created_then_deleted':results})
    return int(not all(checks.values()))

if __name__ == '__main__': sys.exit(run(sys.argv[1]))
