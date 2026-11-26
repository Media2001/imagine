"""Bounded C16 correction proofs: real synchronized POSTs and native rereads."""
from pathlib import Path
from datetime import datetime, timezone
import concurrent.futures
import importlib.util
import json
import re
import sys
import threading
import subprocess
from urllib.parse import urlencode
from html.parser import HTMLParser

class SettingsForm(HTMLParser):
    """Successful controls of the existing C10 form; preserve other lots' fields."""
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.fields={};self.current=None;self.select=None;self.option=None;self.textarea=None
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='form': self.current={}
        if self.current is None: return
        if tag=='input' and a.get('name') and a.get('type') not in ('submit','button') and (a.get('type') not in ('checkbox','radio') or 'checked' in a):
            self.current[a['name']]=a.get('value','')
        if tag=='select': self.select={'name':a.get('name'),'values':[]}
        if tag=='option' and self.select is not None: self.option={'value':a.get('value'),'selected':'selected' in a,'text':''}
        if tag=='textarea': self.textarea={'name':a.get('name'),'value':''}
    def handle_data(self,data):
        if self.option is not None: self.option['text']+=data
        if self.textarea is not None: self.textarea['value']+=data
    def handle_endtag(self,tag):
        if tag=='option' and self.option is not None:
            self.select['values'].append(self.option);self.option=None
        if tag=='select' and self.select is not None:
            values=self.select['values']
            if values and self.select['name']:
                selected=next((v for v in values if v['selected']),values[0])
                self.current[self.select['name']]=selected['value'] if selected['value'] is not None else selected['text']
            self.select=None
        if tag=='textarea' and self.textarea is not None:
            self.current[self.textarea['name']]=self.textarea['value'];self.textarea=None
        if tag=='form' and self.current is not None:
            if self.current.get('option_page')=='imagine_reglages': self.fields=self.current
            self.current=None
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c16
spec = importlib.util.spec_from_file_location('c16_http_original', Path(__file__).with_name('c16-http.py'))
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
h, form, PATH = base.h, base.form, base.PATH

STATE = r'''$f=get_option('imagine_c09_fixture');$s=wcs_get_subscription($f['subscriptions']['A-PAPIER']);$a=ActionScheduler::store()->fetch_action(8793);echo wp_json_encode(['fixture'=>$f,'status'=>$s->get_status(),'id'=>$s->get_id(),'next'=>$s->get_date('next_payment'),'action'=>['id'=>8793,'status'=>ActionScheduler::store()->get_status(8793),'args'=>$a->get_args(),'date'=>$a->get_schedule()->get_date()->format('Y-m-d H:i:s')]]);'''
OBJECTS = r'''$out=[];foreach(['shop_order','shop_subscription'] as $type){$out[$type]=[];foreach(wc_get_orders(['type'=>$type,'limit'=>-1,'status'=>'any','meta_key'=>'_imagine_c16_fixture','meta_value'=>'1']) as $o){$out[$type][]=['id'=>$o->get_id(),'uid'=>$o->get_customer_id(),'status'=>$o->get_status(),'parent'=>$o->get_parent_id(),'paid'=>$o->is_paid()];}}echo wp_json_encode($out);'''

def run(label='http-corrections-V2', selection='all'):
    c16.profils.guard('imagine-test-demo')
    accounts = json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    operator = h.login(accounts['E-ABO'])
    checks, evidence, created = {}, {}, []
    before = c16.wp(STATE)
    policy_before = c16.wp('echo wp_json_encode(get_option("imagine_commande_adresse_nouveau",null));')
    native = c16.wp('echo wp_json_encode(["uid"=>get_option("imagine_c09_fixture")["users"]["E-ABO"],"product"=>get_option("imagine_c09_fixture")["tariffs"]["normal-1"],"customer"=>get_option("imagine_c09_fixture")["users"]["V-INSCRIT"]]);')
    address = {'first_name':'Personnage', 'last_name':'Fictif', 'address_1':'16 rue Imaginaire', 'address_2':'', 'postcode':'1000', 'city':"Localite O'Fictif V2", 'country':'BE'}
    def post(page, fields, client=operator):
        return h.fetch(PATH, client, urlencode(dict(form(page), **fields)).encode())
    def draft(client):
        _,_,first = h.fetch(PATH, operator)
        s,_,second = post(first, dict(client, c16_action='choisir'))
        assert s == 200 and 'data-imagine-etape="2"' in second
        s,_,third = post(second, dict(address,c16_action='preparer',produit=str(native['product']),paiement='bacs'))
        assert s == 200 and 'data-imagine-etape="3"' in third
        return third
    def owned_fs(command):
        subprocess.run(['wsl.exe','-d','Ubuntu','--','docker','exec','--user','root','wp-imagine-test-demo','sh','-c',command],check=True,capture_output=True)
    def configure(third, mode):
        owned_fs('mkdir -p /var/www/html/wp-content/imagine-demo-build/c16-recette-v2 && chown www-data:www-data /var/www/html/wp-content/imagine-demo-build/c16-recette-v2 && chmod 700 /var/www/html/wp-content/imagine-demo-build/c16-recette-v2')
        config = {'token':form(third)['token'], 'uid':native['uid'], 'mode':mode}
        c16.wp('$p=WP_CONTENT_DIR."/imagine-demo-build/c16-recette-v2";if(!is_dir($p))mkdir($p,0700);foreach(glob($p."/*") as $f)unlink($f);update_option("imagine_c16_recette_v2",json_decode('+json.dumps(json.dumps(config))+',true),false);echo "true";')
        assert c16.wp('echo wp_json_encode(get_option("imagine_c16_recette_v2"));') == config
    def search(query, uid):
        status,_,text = h.fetch(PATH+'&'+urlencode({'recherche':query}),operator)
        return status==200 and f'name="client" value="{uid}"' in text, text
    c16.upload('mu-plugins/imagine-c16-recette-v2.php',Path(__file__).with_name('c16-concurrence-probe.php'))
    try:
        if selection in ('all','concurrence'):
            third = draft({'mode':'existant','client':str(native['customer'])})
            configure(third,'concurrence')
            # Separate authenticated clients; both wait server-side immediately before GET_LOCK.
            jar = next(handler.cookiejar for handler in operator.handlers if isinstance(handler,h.HTTPCookieProcessor))
            clients = [h.build_opener(h.DemoRedirect(),h.HTTPCookieProcessor(jar)) for _ in range(2)]
            barrier = threading.Barrier(2)
            def confirm(client):
                barrier.wait(timeout=10)
                status,_,body = post(third,{'c16_action':'creer','confirmer':'oui'},client)
                match = re.search(r'data-imagine-commande="(\d+)"',body)
                return {'status':status,'id':int(match.group(1)) if match else None}
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                replies = list(pool.map(confirm,clients))
            objects = c16.wp(OBJECTS)
            arrivals = c16.wp('$p=WP_CONTENT_DIR."/imagine-demo-build/c16-recette-v2";$o=[];foreach(glob($p."/arrive-*") as $f){$o[]=["connection"=>(int)substr(basename($f),7),"before_GET_LOCK"=>(float)file_get_contents($f)];}echo wp_json_encode($o);')
            checks['deux_POST_synchronises_avant_verrou_connexions_distinctes'] = len(arrivals)==2 and arrivals[0]['connection']!=arrivals[1]['connection']
            checks['deux_POST_meme_ID'] = all(r['status']==200 and r['id'] for r in replies) and replies[0]['id']==replies[1]['id']
            checks['exactement_une_commande_et_une_souscription'] = len(objects['shop_order'])==len(objects['shop_subscription'])==1 and objects['shop_subscription'][0]['parent']==objects['shop_order'][0]['id']
            evidence['concurrence'] = {'responses':replies,'before_lock':arrivals,'native_reread':objects}
            created += [o['id'] for o in objects['shop_order']]
            c16.wp('delete_option("imagine_c16_recette_v2");echo "true";')
        if selection in ('all','interruption'):
            third = draft({'mode':'existant','client':str(native['customer'])})
            configure(third,'interruption')
            snapshot = c16.wp(OBJECTS)
            status,_,_ = post(third,{'c16_action':'creer','confirmer':'oui'})
            key = f"imagine_c16_brouillon_{native['uid']}_{form(third)['token']}"
            persisted = c16.wp('echo wp_json_encode(get_transient('+json.dumps(key)+'));')
            c16.wp('delete_option("imagine_c16_recette_v2");echo "true";')
            retries = [post(third,{'c16_action':'creer','confirmer':'oui'})[0] for _ in range(2)]
            checks['interruption_apres_commence_persistant'] = status==409 and persisted.get('commence') is True and 'resultat' not in persisted
            checks['reprises_interruption_fermees_sans_nouvelle_creation'] = retries==[409,409] and c16.wp(OBJECTS)==snapshot
            evidence['interruption'] = {'first_status':status,'retries':retries,'commence_reread':persisted.get('commence'),'resultat_present':'resultat' in persisted,'objects_before':snapshot,'objects_after':c16.wp(OBJECTS)}
        if selection in ('all','adresse'):
            settings_client=h.login(accounts['E-ADMIN'])
            s,_,settings=h.fetch('/wp-admin/admin.php?page=imagine-reglages',settings_client)
            checks['reglage_C10_visible_defaut_prudent_question_Imagine']=s==200 and 'name="imagine_commande_adresse_nouveau"' in settings and 'Oui — nouveau compte seulement (défaut prudent)' in settings and 'à confirmer par Imagine' in settings
            fields=SettingsForm(settings).fields
            keys=sorted({k.split('[')[0] for k in fields if k.startswith('imagine_') and k!='imagine_commande_adresse_nouveau'})
            options_code='$o=[];foreach(json_decode('+json.dumps(json.dumps(keys))+',true) as $k){$o[$k]=get_option($k,null);}echo wp_json_encode($o);'
            other_settings_before=c16.wp(options_code)
            for value in ['non','oui']:
                _,_,settings=h.fetch('/wp-admin/admin.php?page=imagine-reglages',settings_client)
                fields=SettingsForm(settings).fields
                assert fields.get('option_page')=='imagine_reglages' and '_wpnonce' in fields
                fields['imagine_commande_adresse_nouveau']=value
                status,_,_=h.fetch('/wp-admin/options.php',settings_client,urlencode(fields).encode())
                checks['reglage_C10_POST_natif_'+value+'_reread']=status==200 and c16.wp('echo wp_json_encode(get_option("imagine_commande_adresse_nouveau"));')==value
            checks['reglages_autres_lots_preserves']=c16.wp(options_code)==other_settings_before
            existing_code = '$u=get_userdata('+str(native['customer'])+');$c=new WC_Customer($u->ID);echo wp_json_encode(["name"=>$u->display_name,"email"=>$u->user_email,"first_name"=>$c->get_first_name(),"last_name"=>$c->get_last_name(),"billing"=>$c->get_billing(),"shipping"=>$c->get_shipping()]);'
            existing_before = c16.wp(existing_code)
            for name,client,policy in [
                ('avec_email',{'mode':'nouveau','nom':"Personnage O'Fictif Avec",'email':'c16-localite-v2@example.org'},'oui'),
                ('sans_email',{'mode':'nouveau','nom':"Personnage O'Fictif Sans",'sans_email':'1'},'oui'),
                ('reglage_non',{'mode':'nouveau','nom':'Personnage Fictif Non','email':'c16-non-v2@example.org'},'non'),
                ('preexistant',{'mode':'existant','client':str(native['customer'])},'oui')]:
                c16.wp('update_option("imagine_commande_adresse_nouveau",'+json.dumps(policy)+',false);echo "true";')
                assert c16.wp('echo wp_json_encode(get_option("imagine_commande_adresse_nouveau"));')==policy
                third=draft(client)
                status,_,done=post(third,{'c16_action':'creer','confirmer':'oui'})
                match=re.search(r'data-imagine-commande="(\d+)"',done)
                assert status==200 and match, name
                oid=int(match.group(1));created.append(oid)
                data=c16.wp('$o=wc_get_order('+str(oid)+');$u=new WC_Customer($o->get_customer_id());echo wp_json_encode(["uid"=>$u->get_id(),"first_name"=>$u->get_first_name(),"last_name"=>$u->get_last_name(),"shipping"=>$u->get_shipping(),"billing"=>$u->get_billing(),"email"=>$u->get_email(),"sans"=>get_user_meta($u->get_id(),"imagine_sans_email",true)]);')
                evidence[name]=data
                if name in ('avec_email','sans_email'):
                    found,text=search(address['city'],data['uid'])
                    checks[name+'_adresse_native_reread']=data['first_name']==address['first_name'] and data['last_name']==address['last_name'] and all(data[k].get(f)==v for k in ('shipping','billing') for f,v in address.items())
                    checks[name+'_localite_distincte_retrouve']=found and address['city'] not in client['nom'] and address['city'] not in data['email']
                    found,text=search("O'Fictif",data['uid'])
                    checks[name+'_GET_nom_apostrophe_reel_sans_slash']=found and ('value="O&#039;Fictif"' in text or 'value="O\'Fictif"' in text) and "O\\&#039;Fictif" not in text
                    found,text=search(address['city'],data['uid'])
                    checks[name+'_GET_localite_apostrophe_reel_sans_slash']=found and '\\&#039;' not in text
                elif name=='reglage_non':
                    checks['reglage_non_pas_adresse_compte']=data['shipping']['city']==data['billing']['city']==''
                else:
                    checks['compte_preexistant_adresse_nom_email_inchanges']=c16.wp(existing_code)==existing_before
                    evidence['compte_preexistant_avant']=existing_before
                    evidence['compte_preexistant_apres']=c16.wp(existing_code)
    finally:
        c16.wp(('delete_option("imagine_commande_adresse_nouveau");' if policy_before is None else 'update_option("imagine_commande_adresse_nouveau",'+json.dumps(policy_before)+',false);')+'echo "true";')
        checks['reglage_restaure_exactement']=c16.wp('echo wp_json_encode(get_option("imagine_commande_adresse_nouveau",null));')==policy_before
        c16.wp('delete_option("imagine_c16_recette_v2");echo "true";')
        owned_fs('rm -f /var/www/html/wp-content/mu-plugins/imagine-c16-recette-v2.php; if [ -d /var/www/html/wp-content/imagine-demo-build/c16-recette-v2 ]; then rm -f /var/www/html/wp-content/imagine-demo-build/c16-recette-v2/arrive-* /var/www/html/wp-content/imagine-demo-build/c16-recette-v2/interruption; rmdir /var/www/html/wp-content/imagine-demo-build/c16-recette-v2; fi')
        checks['sonde_temporaire_supprimee_reread']=c16.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/mu-plugins/imagine-c16-recette-v2.php")&&!file_exists(WP_CONTENT_DIR."/imagine-demo-build/c16-recette-v2")&&get_option("imagine_c16_recette_v2",null)===null);')
        reset=c16.wp('require WP_CONTENT_DIR."/imagine-demo-build/c16-reset.php";echo wp_json_encode(imagine_c16_reset());')
        c16.save('reset-corrections-V2',reset)
        checks['objets_C16_supprimes_reread']=c16.wp(OBJECTS)=={'shop_order':[],'shop_subscription':[]}
        after=c16.wp(STATE)
        checks['C09_action_8793_pending_abo101_preserves']=before==after and after['id']==101 and after['action']['id']==8793 and after['action']['status']=='pending'
        evidence['C09_before']=before; evidence['C09_after']=after
    result={'at':datetime.now(timezone.utc).isoformat(),'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],'created_then_deleted':created,'evidence':evidence}
    c16.save(label,result)
    print(json.dumps({'total':result['total'],'failures':result['failures'],'concurrence':evidence.get('concurrence')},ensure_ascii=False))
    return int(bool(result['failures']))

if __name__=='__main__':
    sys.exit(run(sys.argv[1] if len(sys.argv)>1 else 'http-corrections-V2',sys.argv[2] if len(sys.argv)>2 else 'all'))
