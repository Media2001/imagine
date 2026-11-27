"""C27 : HTTP réel, mutant pas-avant-paiement, callbacks natifs et inverses indépendantes."""
import sys
sys.dont_write_bytecode = True
import concurrent.futures
import hashlib
import importlib.util
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
import c27
spec=importlib.util.spec_from_file_location('c27_native',c27.ROOT/'wp/outils/demo/c27-native.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)


class SameSite(urllib.request.HTTPRedirectHandler):
    def __init__(self,base): self.base=base
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        assert urllib.parse.urlsplit(newurl).netloc==urllib.parse.urlsplit(self.base).netloc
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def fields(node):
    return {unescape(k):unescape(v) for k,v in re.findall(r'name=["\']([^"\']+)["\']\s+(?:[^>]*?)value=["\']([^"\']*)["\']',node)}


def run(label):
    assert not (c27.PROOF/(label+'.json')).exists()
    identity=c27.guard();saved=c27.snapshot();business=c27.state()
    durable=c27.private('c27-'+label,{'database':saved,'business':business})
    auth={};owned=[];checks={};evidence={};cleanup={};error=None;draft_token=None
    observer='mu-plugins/c27-observer.php'
    remote_regles='plugins/imagine-site/AcquisitionRegles.php'
    remote_adapter='plugins/imagine-site/Acquisition.php'
    regles=(c27.ROOT/'wp'/remote_regles).read_bytes();adapter=(c27.ROOT/'wp'/remote_adapter).read_bytes()
    assert c27.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+observer+'"));') is False
    assert c27.wp('echo wp_json_encode(Imagine\\Site\\AcquisitionConfidentialite::lignes());')==[]
    try:
        c27.upload(observer,(c27.ROOT/'wp/tests/demo/c27-observer.php').read_bytes())
        positive=c27.wp("wp_mail('fictif@example.org','Fictif','Fictif');wp_remote_get('https://example.org/');$r=get_option('imagine_c27_observations');delete_option('imagine_c27_observations');echo wp_json_encode($r);")
        checks['observateurs_positifs']=positive=={'ambiance_mail':1,'ambiance_http':1}
        auth=c27.wp("$out=[];foreach(['admin'=>get_users(['role'=>'administrator','number'=>1])[0]->ID,'lecteur'=>28,'tiers'=>29] as $role=>$id){$u=get_userdata($id);if(!$u||!str_ends_with($u->user_email,'@example.org')){throw new RuntimeException('Personnage fictif requis');}$token=WP_Session_Tokens::get_instance($id)->create(time()+3600);$out[$role]=['id'=>$id,'cookie'=>LOGGED_IN_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'logged_in',$token).'; '.AUTH_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'auth',$token).'; '.SECURE_AUTH_COOKIE.'='.wp_generate_auth_cookie($id,time()+3600,'secure_auth',$token)];}echo wp_json_encode($out);")
        c27.private('c27-'+label+'-sessions',auth)
        opener=urllib.request.build_opener(SameSite(identity['url']))
        def http(path,data=None,role='',headers=None):
            if path.startswith(identity['url']+'/'): path=path[len(identity['url']):]
            assert path.startswith('/') and not path.startswith('//')
            hs={'User-Agent':'Imagine-C27-fictif',**(headers or {})}
            if role:hs['Cookie']=auth[role]['cookie']
            req=urllib.request.Request(identity['url']+path,data=urllib.parse.urlencode(data).encode() if data is not None else None,headers=hs)
            try:r=opener.open(req,timeout=45)
            except urllib.error.HTTPError as e:r=e
            with r:
                assert r.geturl().startswith(identity['url']+'/')
                return r.status,r.read().decode('utf-8'),r.geturl()
        def nonce(oid,role='lecteur'):
            return c27.wp('wp_set_current_user('+str(auth[role]['id'])+');foreach(explode("; ",'+c27.php(auth[role]['cookie'])+') as $part){[$k,$v]=explode("=",$part,2);$_COOKIE[$k]=$v;}echo wp_json_encode(wp_create_nonce("imagine_acquisition:'+str(oid)+'"));')
        def settings(value,fault=False):
            status,body,_=http('/wp-admin/admin.php?page=imagine-reglages',role='admin')
            forms=re.findall(r'<form\b[^>]*action=["\']options.php["\'][^>]*>(.*?)</form>',body,re.S)
            assert status==200 and len(forms)==1 and 'imagine-acquisition-reglages' in forms[0]
            f=fields(forms[0]);payload={k:f[k] for k in ['option_page','action','_wpnonce','_wp_http_referer']}
            payload['imagine_acquisition_choix']=value
            return http('/wp-admin/options.php',payload,'admin',{'X-Imagine-C27-Settings':'recette-fictive','Referer':identity['url']+'/wp-admin/admin.php?page=imagine-reglages',**({'X-Imagine-C27-Failure':'journal'} if fault else {})})
        def configuration():
            return c27.wp('global $wpdb;$events=[];foreach($wpdb->get_col("SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE \'imagine_reglages_journal_%\' ORDER BY option_id") as $raw){$e=maybe_unserialize($raw);if(is_array($e)&&($e["option"]??"")==="imagine_acquisition_choix"){$events[]=$e;}}echo wp_json_encode(["value"=>get_option("imagine_acquisition_choix",null),"events"=>$events]);')
        settings_path='/wp-admin/admin.php?page=imagine-reglages'
        _,settings_body,_=http(settings_path,role='admin')
        checks['C10_section_dans_formulaire_sous_bouton_sans_deplacement']=settings_body.index('id="submit"')<settings_body.index('id="imagine-acquisition-reglages"')<settings_body.index('</form>',settings_body.index('id="imagine-acquisition-reglages"')) and all(n in settings_body for n in ['imagine-retractation-reglages','imagine-personnalisation','imagine-newsletter'])
        initial=configuration()
        _,failed_create,_=settings('lune|Radio fictive',True)
        checks['C10_creation_journal_en_panne_restaure_preimage']=configuration()==initial and 'setting-error-imagine_acquisition_journal' in failed_create
        settings('lune|Radio fictive \\ lune\nmars|Journal martien fictif')
        configured=configuration()
        event=configured['events'][-1]
        choices={'lune':'Radio fictive \\ lune','mars':'Journal martien fictif'}
        checks['C10_POST_natif_liste_journal_auteur_date']=configured['value']==choices and len(configured['events'])==len(initial['events'])+1 and event['avant']==initial['value'] and event['apres']==choices and event['qui_id']==auth['admin']['id'] and bool(event['qui_login']) and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',event['quand_utc']) is not None
        settings('id invalide|<script>Fictif</script>')
        checks['C10_liste_invalide_rejetee_sans_journal']=configuration()==configured
        _,failed_update,_=settings('autre|Fictif',True)
        checks['C10_modification_panne_restaure_antislash_exact']=configuration()==configured and 'setting-error-imagine_acquisition_journal' in failed_update
        def create(status='processing',uid=28):
            row=c27.wp('$o=wc_create_order(["customer_id"=>'+str(uid)+',"status"=>"pending","created_via"=>"checkout"]);$o->update_meta_data("_imagine_c27_recette",'+c27.php(label)+');$o->set_total(1);'+('$o->set_status("processing");$o->set_date_paid(time());' if status=='processing' else '')+'$o->save();echo wp_json_encode(["id"=>$o->get_id(),"url"=>$o->get_checkout_order_received_url()]);')
            owned.append(row['id']);c27.private('c27-'+label+'-objets',{'ids':owned})
            return row
        pending=create('pending');paid=create();second=create();third=create(uid=29);skip=create();empty=create()
        def record(row):return c27.wp('echo wp_json_encode(get_option(Imagine\\Site\\Acquisition::REPONSE . '+str(row['id'])+',null));')
        def seen(row):return c27.wp('echo wp_json_encode(get_option(Imagine\\Site\\Acquisition::VUE . '+str(row['id'])+',null));')
        def post(row,choice,role='lecteur',signed=None):return http('/wp-admin/admin-post.php',{'action':'imagine_acquisition','commande':str(row['id']),'choix':choice,'_c27':signed if signed is not None else nonce(row['id'],role)},role)
        _,checkout,_=http('/checkout/',role='lecteur')
        checks['tunnel_avant_paiement_sans_question']='id="imagine-acquisition"' not in checkout and 'woocommerce' in checkout
        status,body,_=http(pending['url'],role='lecteur')
        checks['confirmation_impayee_absence_non_vide']=status==200 and 'woocommerce-order' in body and 'id="imagine-acquisition"' not in body and seen(pending) is None
        pre=post(pending,'lune')
        checks['POST_signe_avant_paiement_refuse']=pre[0]==403 and record(pending) is None
        original_source=c27.wp('echo wp_json_encode(get_user_meta(28,Imagine\\Site\\Acquisition::SOURCE,true));')
        assert regles.count(b'$paid && $dated')==1
        try:
            c27.upload(remote_regles,regles.replace(b'$paid && $dated',b'true'))
            status,mutbody,_=http(pending['url'],role='lecteur')
            mutated=post(pending,'lune')
            mutation={'form_present':'id="imagine-acquisition"' in mutbody,'post_status':mutated[0],'response_written':isinstance(record(pending),dict)}
            checks['mutation_native_pas_avant_paiement_tue_deux_controles']=mutation=={'form_present':True,'post_status':200,'response_written':True}
            evidence['mutation_pas_avant_paiement']={'expected_baseline':{'form_present':False,'post_status':403,'response_written':False},'mutant_observed':mutation}
        finally:
            c27.upload(remote_regles,regles)
            c27.wp('foreach([Imagine\\Site\\Acquisition::VUE,Imagine\\Site\\Acquisition::REPONSE] as $p){delete_option($p . '+str(pending['id'])+');}delete_user_meta(28,Imagine\\Site\\Acquisition::SOURCE);'+('update_user_meta(28,Imagine\\Site\\Acquisition::SOURCE,wp_slash('+c27.php(original_source)+'));' if original_source!='' else '')+'echo wp_json_encode(true);')
        _,body,_=http(pending['url'],role='lecteur')
        checks['garde_revenue_apres_mutation']='id="imagine-acquisition"' not in body and post(pending,'lune')[0]==403 and seen(pending) is None and record(pending) is None
        _,anon,_=http(paid['url']);_,foreign,_=http(paid['url'],role='tiers')
        checks['autre_compte_et_anonyme_sans_question']='id="imagine-acquisition"' not in anon+foreign and seen(paid) is None
        _,form,_=http(paid['url'],role='lecteur')
        node=form.split('<section id="imagine-acquisition">',1)[1].split('</section>',1)[0]
        signed=fields(node)['_c27']
        checks['confirmation_payee_question_facultative_fermee']='name="choix"' in node and 'required' not in node and 'textarea' not in node and 'Je préfère ne pas répondre' in node and 'Continuer sans répondre' in node and unescape(node).count('Radio fictive \\ lune')==1
        _,refresh,_=http(paid['url'],role='lecteur')
        checks['question_ne_revient_pas_sans_reponse']='id="imagine-acquisition"' not in refresh and record(paid) is None and isinstance(seen(paid),dict)
        checks['nonce_invalide_refuse']=post(paid,'lune',signed='faux')[0]==403 and record(paid) is None
        checks['choix_libre_refuse']=post(paid,'texte libre',signed=signed)[0]==403 and record(paid) is None
        checks['tiers_POST_signe_refuse']=post(paid,'lune',role='tiers')[0]==403 and record(paid) is None
        before_projection=c27.wp('echo wp_json_encode([Imagine\\Site\\Personnalisation::attributsConnecteur(28),Imagine\\Site\\Newsletters::preferences(28)]);')
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda value:post(paid,value,signed=signed)[0],['lune','mars']))
        first=record(paid)
        checks['deux_POST_concurrents_une_reponse']=sorted(results)==[200,403] and first['choix'] in choices and first['libelle']==choices[first['choix']] and first['compte']==28 and first['commande']==paid['id'] and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',first['date']) is not None
        checks['double_envoi_refuse_immuable']=post(paid,'lune',signed=signed)[0]==403 and record(paid)==first
        checks['source_compte_vide_initialisee']=c27.wp('echo wp_json_encode(get_user_meta(28,Imagine\\Site\\Acquisition::SOURCE,true));')==first
        post(second,'mars')
        checks['deuxieme_commande_source_non_ecrasee']=record(second)['choix']=='mars' and c27.wp('echo wp_json_encode(get_user_meta(28,Imagine\\Site\\Acquisition::SOURCE,true));')==first
        post(third,'mars',role='tiers');foreign_record=record(third)
        checks['compte_tiers_temoin_reel']=foreign_record['compte']==29
        _,skipform,_=http(skip['url'],role='lecteur')
        skipnonce=fields(skipform.split('<section id="imagine-acquisition">',1)[1])['_c27']
        checks['passer_ne_bloque_rien']=post(skip,'',signed=skipnonce)[0]==200 and record(skip) is None and 'id="imagine-acquisition"' not in http(skip['url'],role='lecteur')[1]
        settings('')
        status,emptybody,_=http(empty['url'],role='lecteur')
        checks['liste_vide_confirmation_payee_aucune_trace']=status==200 and 'woocommerce-order' in emptybody and 'id="imagine-acquisition"' not in emptybody and seen(empty) is None and record(empty) is None
        checks['liste_vide_POST_signe_refuse']=post(empty,'lune')[0]==403 and record(empty) is None
        settings('lune|Radio fictive \\ lune\nmars|Journal martien fictif')
        # Vrai brouillon C16, trois écrans et création native d'un achat au numéro (pas de souscription).
        c16path='/wp-admin/admin.php?page=imagine-commandes'
        def c16form(body,action):
            forms=re.findall(r'<form\b[^>]*>(.*?)</form>',body,re.S)
            return next(fields(f) for f in forms if fields(f).get('c16_action')==action)
        _,firstpage,_=http(c16path,role='admin')
        f=c16form(firstpage,'choisir');f.update({'mode':'existant','client':'28'})
        s,secondpage,_=http(c16path,f,'admin')
        f=c16form(secondpage,'preparer');draft_token=f['token']
        product=c27.wp('$p=array_values(array_filter(Imagine\\Site\\CommandeNative::produits(),static fn($p)=>!$p->is_type("subscription")));if(!$p){throw new RuntimeException("Produit C14 requis");}echo wp_json_encode($p[0]->get_id());')
        f.update({'produit':str(product),'paiement':'bacs','first_name':'Personnage','last_name':'Fictif','address_1':'27 rue Imaginaire','address_2':'','postcode':'1000','city':'Ville fictive','country':'BE'})
        _,thirdpage,_=http(c16path,f,'admin')
        f=c16form(thirdpage,'creer');f['confirmer']='oui'
        _,resultpage,_=http(c16path,f,'admin')
        oid=int(re.search(r'data-imagine-commande="(\d+)"',resultpage).group(1));owned.append(oid)
        c16=c27.wp('$o=wc_get_order('+str(oid)+');$o->update_meta_data("_imagine_c27_recette",'+c27.php(label)+');$o->set_status("processing");$o->set_date_paid(time());$o->save();echo wp_json_encode(["id"=>$o->get_id(),"url"=>$o->get_checkout_order_received_url(),"via"=>$o->get_created_via()]);')
        c27.private('c27-'+label+'-objets',{'ids':owned})
        checks['vrai_brouillon_C16_aucun_champ_source']=all('id="imagine-acquisition"' not in page and 'name="choix"' not in page for page in [firstpage,secondpage,thirdpage,resultpage]) and 'data-imagine-etape="2"' in secondpage and 'data-imagine-etape="3"' in thirdpage and c16['via']=='imagine-c16'
        _,c16body,_=http(c16['url'],role='lecteur')
        checks['C16_meme_payee_jamais_interrogee']=('id="imagine-acquisition"' not in c16body and post(c16,'lune')[0]==403 and record(c16) is None and seen(c16) is None)
        _,adminbody,_=http('/wp-admin/admin.php?page=imagine-acquisition&du=2026-01-01&au=2026-12-31',role='admin')
        table=adminbody.split('id="imagine-acquisition-nombres"',1)[1].split('</table>',1)[0]
        actual={k:int(v) for k,v in re.findall(r'data-acquisition="([^"]+)">(\d+)</td>',table)}
        expected={}
        for row in [first,record(second),foreign_record]:expected[row['choix']]=expected.get(row['choix'],0)+1
        checks['chiffres_anonymes_periode_exacte']=actual==expected and all(str(r['id']) not in table for r in [paid,second,third]) and '@example.org' not in table and 'Personnage' not in table
        _,outside,_=http('/wp-admin/admin.php?page=imagine-acquisition&du=2000-01-01&au=2000-01-31',role='admin')
        checks['periode_sans_reponse_zero_reel']='Aucune déclaration sur cette période' in outside and 'data-acquisition=' not in outside
        _,badperiod,_=http('/wp-admin/admin.php?page=imagine-acquisition&du=2026-02-30&au=2026-12-31',role='admin')
        checks['periode_invalide_pas_de_nombre']='aucun nombre affiché' in badperiod and 'data-acquisition=' not in badperiod
        denied= http('/wp-admin/admin.php?page=imagine-acquisition',role='lecteur')
        checks['chiffres_droits_C19_refus_lecteur']='imagine-acquisition-nombres' not in denied[1]
        privacy=c27.wp('$e=apply_filters("wp_privacy_personal_data_exporters",[]);$r=apply_filters("wp_privacy_personal_data_erasers",[]);$u=get_userdata(28);echo wp_json_encode(["exporteur"=>isset($e["imagine-acquisition"]),"effaceur"=>isset($r["imagine-acquisition"]),"export"=>call_user_func($e["imagine-acquisition"]["callback"],$u->user_email,1)]);')
        exported=privacy['export'];export_text=json.dumps(exported,ensure_ascii=False)
        checks['export_natif_C21_reponses_date_source_sans_tiers']=privacy['exporteur'] and privacy['effaceur'] and exported['done'] and any(r['item_id']=='imagine-acquisition-reponse-'+str(paid['id']) for r in exported['data']) and any(r['item_id']=='imagine-acquisition-reponse-'+str(second['id']) for r in exported['data']) and all(r['item_id']!='imagine-acquisition-reponse-'+str(third['id']) for r in exported['data']) and first['date'] in export_text and any(r['item_id']=='imagine-acquisition-compte' for r in exported['data'])
        checks['projection_newsletter_et_preferences_inchangees']=before_projection==c27.wp('echo wp_json_encode([Imagine\\Site\\Personnalisation::attributsConnecteur(28),Imagine\\Site\\Newsletters::preferences(28)]);')
        commerce=c27.wp('$o=wc_get_order('+str(paid['id'])+');echo wp_json_encode($o->get_data());')
        checks['declaration_hors_payload_commande_Odoo']='imagine_acquisition' not in json.dumps(commerce) and first['libelle'] not in json.dumps(commerce,ensure_ascii=False)
        erased=c27.wp('$r=apply_filters("wp_privacy_personal_data_erasers",[]);echo wp_json_encode(call_user_func($r["imagine-acquisition"]["callback"],get_userdata(28)->user_email,1));')
        after_export=c27.wp('echo wp_json_encode(Imagine\\Site\\AcquisitionConfidentialite::exporter(get_userdata(28)->user_email));')
        checks['effacement_natif_C21_source_reponses_et_propositions']=erased['done'] and erased['items_removed'] and not erased['items_retained'] and after_export=={'data':[],'done':True} and c27.wp('echo wp_json_encode(get_user_meta(28,Imagine\\Site\\Acquisition::SOURCE,true));')==''
        checks['effacement_preserve_tiers']=record(third)==foreign_record
        checks['trace_depersonnalisee_pas_de_nouvelle_reponse']=record(paid)=={'commande':paid['id'],'date':first['date'],'etat':'effacee'} and post(paid,'mars',signed=signed)[0]==403
        _,erasedbody,_=http('/wp-admin/admin.php?page=imagine-acquisition&du=2026-01-01&au=2026-12-31',role='admin')
        erased_table=erasedbody.split('id="imagine-acquisition-nombres"',1)[1].split('</table>',1)[0]
        checks['chiffres_recalcules_apres_effacement']=dict(re.findall(r'data-acquisition="([^"]+)">(\d+)</td>',erased_table))=={'mars':'1'}
        observations=c27.wp('echo wp_json_encode(get_option("imagine_c27_observations",[]));')
        checks['aucun_envoi_C27_email_ou_HTTP']=all(v==0 for k,v in (observations.items() if isinstance(observations,dict) else []) if k.startswith('c27_'))
        # Mutation témoin d'absence de transmission, sur une commande fictive possédée seulement.
        target=b"$record = ['commande' => $id, 'compte' => $actor, 'date' => gmdate('Y-m-d\\TH:i:s\\Z'),"
        assert adapter.count(target)==1
        try:
            c27.upload(remote_adapter,adapter.replace(target,b"wp_mail('fictif@example.org', 'Mutation fictive', 'Fictif');wp_remote_get('https://example.org/');\n            "+target))
            mutated_send=c27.wp('echo wp_json_encode(Imagine\\Site\\Acquisition::repondre('+str(empty['id'])+',28,"lune"));')
            witnessed=c27.wp('echo wp_json_encode(get_option("imagine_c27_observations",[]));')
            checks['mutation_absence_transmission_detectee']=mutated_send is True and witnessed.get('c27_mail')==1 and witnessed.get('c27_http')==1
        finally:c27.upload(remote_adapter,adapter)
        evidence.update({'settings':{'initial':initial,'configured':configured},'parallel_statuses':results,'counts_expected':expected,'counts_observed':actual,'export_items':len(exported['data']),'erasure':erased,'observations_baseline':observations,'observations_mutant':witnessed,'positive_observers':positive,'owned_order_count':len(owned)})
        assert checks and all(v is True for v in checks.values()),{k:v for k,v in checks.items() if v is not True}
    except Exception as e:
        error=type(e).__name__+': '+str(e)
        raise
    finally:
        def attempt(key,fn):
            try:fn();cleanup[key]=True
            except Exception as e:cleanup[key]=False;cleanup[key+'_error']=type(e).__name__+': '+str(e)
        attempt('sources_exactes',lambda:[c27.upload(remote_regles,regles),c27.upload(remote_adapter,adapter)])
        def orders():
            # Seulement les identifiants obtenus de cette recette, avec contrôle de propriété.
            c27.wp('foreach('+c27.php(owned)+' as $id){$o=wc_get_order($id);if($o){if($o->get_meta("_imagine_c27_recette")!=='+c27.php(label)+'){throw new RuntimeException("Commande étrangère");}$o->delete(true);}}echo wp_json_encode(true);')
        attempt('commandes_natives_supprimees',orders)
        if draft_token:
            attempt('brouillon_C16_retire',lambda:c27.wp('delete_transient("imagine_c16_brouillon_'+str(auth['admin']['id'])+'_'+draft_token+'");echo wp_json_encode(true);'))
        attempt('options_et_journaux_C27_restaures',lambda:native.restore_options(saved))
        for role,session in auth.items():attempt('profil_'+role,lambda uid=session['id']:native.restore_users(saved,{uid}))
        attempt('observateur_retire',lambda:c27.b09.remove_remote([observer]))
        exact=native.compare(saved,c27.snapshot());preserved=business==c27.state()
        c27.save(label,{'checks':checks,'cleanup':cleanup,'restoration':exact,'business_preserved':preserved,'private_snapshot':durable,'identity':identity,'error':error,**evidence})
        print(json.dumps({'checks':checks,'cleanup':cleanup,'restoration':exact,'business_preserved':preserved,'error':error},ensure_ascii=False))
        assert all(v is True for v in cleanup.values()) and all(exact.values()) and preserved,'Inverse non prouvée'


if __name__=='__main__':run(sys.argv[1])
