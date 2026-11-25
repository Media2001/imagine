"""Real C16 admin HTTP, native readback, targeted C09 reset, no payment."""
from pathlib import Path
from html import unescape
import importlib.util
import json
import re
import sys
from urllib.parse import urlencode
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c16
spec=importlib.util.spec_from_file_location('c16_http_transport',Path(__file__).with_name('c12-http.py'))
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
PATH='/wp-admin/admin.php?page=imagine-commandes'

def form(text):
    return {unescape(k):unescape(v) for k,v in re.findall(r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]+value="([^"]*)"',text)}

def run(label='http-final'):
    c16.profils.guard('imagine-test-demo')
    accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    abo=h.login(accounts['E-ABO'])
    checks={};created=[]
    def post(text,fields):
        return h.fetch(PATH,abo,urlencode(dict(form(text),**fields)).encode())
    status,headers,page=h.fetch(PATH,abo)
    checks['etape1_referent']=status==200 and 'data-imagine-etape="1"' in page
    checks['menu_unique']=page.count('id="toplevel_page_imagine"')==1
    checks['hors_perimetre_nomme']=all(x in page for x in ['Don','Pack','Abonnement offert','Abonnement groupé'])
    if not checks['etape1_referent']:
        c16.save(label,{'checks':checks,'failures':[k for k,v in checks.items() if not v]})
        print(json.dumps(checks));return 1
    baseline=c16.wp('echo wp_json_encode(["users"=>count_users()["total_users"],"c09"=>get_option("imagine_c09_fixture"),"c12"=>get_option("imagine_decouverte_compte_".get_option("imagine_c09_fixture")["users"]["V-DEC"])]);')
    native=c16.wp('$f=get_option("imagine_c09_fixture");echo wp_json_encode(["uid"=>$f["users"]["V-INSCRIT"],"produit"=>$f["tariffs"]["normal-1"]]);')
    address={'first_name':'Personnage','last_name':'Fictif C16','address_1':'16 rue Imaginaire','address_2':'','postcode':'1000','city':'Ville Fictive','country':'BE'}
    try:
        for role in ['E-REDAC','A-CARTE']:
            client=h.login(accounts[role]);s,_,body=h.fetch(PATH,client)
            checks['page_refuse_'+role]='data-imagine-etape=' not in body
            s,_,_=h.fetch(PATH,client,urlencode({'c16_action':'choisir','_wpnonce':'invalide'}).encode())
            checks['POST_refuse_'+role]=s==403 or (s==200 and 'woocommerce-MyAccount' in _)
        s,_,_=h.fetch('/wp-admin/admin-post.php?action=imagine_c16_creer')
        checks['anonyme_refuse']=s==403
        for nonce in [{},{'_wpnonce':'invalide'},{'_wpnonce[]':'x'}]:
            s,_,_=h.fetch(PATH,abo,urlencode(dict({'c16_action':'choisir','mode':'direct'},**nonce)).encode())
            checks['nonce_'+('absent' if not nonce else next(iter(nonce)))]=s==403
        for search in ['V-INSCRIT','v-inscrit@example.org','Ville Fictive']:
            s,_,text=h.fetch(PATH+'&recherche='+urlencode({'q':search})[2:],abo)
            checks['recherche_'+search]=s==200 and 'value="'+str(native['uid'])+'"' in text
        scenarios=[('existant',{'mode':'existant','client':str(native['uid'])},'bacs'),
            ('sansmail',{'mode':'nouveau','nom':'Personnage Fictif C16 Sansmail','sans_email':'1','email':''},'bacs'),
            ('doublon',{'mode':'nouveau','nom':'Ne pas remplacer','email':'V-INSCRIT@EXAMPLE.ORG'},'bacs'),
            ('direct',{'mode':'direct'},'imagine_papier')]
        for name,client,payment in scenarios:
            _,_,first=h.fetch(PATH,abo)
            s,_,second=post(first,dict(client,c16_action='choisir'))
            checks[name+'_etape2']=s==200 and 'data-imagine-etape="2"' in second
            s,_,third=post(second,dict(address,c16_action='preparer',produit=str(native['produit']),paiement=payment))
            checks[name+'_etape3']=s==200 and 'data-imagine-etape="3"' in third and 'Créer la commande en attente' in third
            s,_,done=post(third,{'c16_action':'creer','confirmer':'oui'})
            found=re.search(r'data-imagine-commande="(\d+)"',done)
            checks[name+'_cree']=s==200 and found is not None
            if not found: raise RuntimeError('C16 confirmation failed: '+name)
            oid=int(found.group(1));created.append(oid)
            data=c16.wp('$o=wc_get_order('+str(oid)+');$subs=wcs_get_subscriptions_for_order($o->get_id(),["order_type"=>"parent"]);$s=reset($subs);$u=get_userdata($o->get_customer_id());echo wp_json_encode(["id"=>$o->get_id(),"uid"=>$u->ID,"email"=>$u->user_email,"nom"=>$u->display_name,"sans"=>get_user_meta($u->ID,"imagine_sans_email",true),"etat"=>$o->get_status(),"paid"=>$o->is_paid(),"date"=>$o->get_date_paid(),"method"=>$o->get_payment_method(),"sub"=>$s?["id"=>$s->get_id(),"etat"=>$s->get_status(),"manual"=>$s->get_requires_manual_renewal(),"parent"=>$s->get_parent_id(),"uid"=>$s->get_customer_id()]:null,"members"=>count(wc_memberships_get_user_memberships($u->ID,["status"=>"any"]))]);')
            c16.save('native-'+name,data)
            checks[name+'_natif_pending']=data['etat']=='pending' and not data['paid'] and data['date'] is None and data['method']==payment
            checks[name+'_souscription_native']=data['sub'] is not None and data['sub']['etat']=='pending' and data['sub']['manual'] and data['sub']['parent']==oid and data['sub']['uid']==data['uid']
            if name in ('existant','doublon'): checks[name+'_meme_compte']=data['uid']==native['uid'] and data['nom']!='Ne pas remplacer'
            if name=='sansmail':
                checks['sansmail_domaine_reserve_marque']=data['email'].endswith('@sans-email.imagine.invalid') and data['sans']=='1'
                checks['sansmail_pas_adhesion']=data['members']==0
                closed=c16.wp('echo wp_json_encode(Imagine\\Site\\AchatsNumeros::droits('+str(data['uid'])+'));')
                checks['sansmail_pas_acces_numero']=closed==[]
                mail=c16.wp('$email='+json.dumps(data['email'])+';echo wp_json_encode([Imagine\\Site\\SansEmail::filtrer(null,["to"=>$email,"headers"=>[]]),Imagine\\Site\\SansEmail::filtrer(null,["to"=>"normal@example.org","headers"=>"Bcc: ".$email]),Imagine\\Site\\SansEmail::filtrer(null,["to"=>"normal@example.org","headers"=>[]]),Imagine\\Site\\SansEmail::filtrer(null,["to"=>"a-sansmail@example.org","headers"=>[]])]);')
                checks['sansmail_exclusion_individuelle_TO_BCC_C09']=mail==[False,False,None,False]
            if payment=='bacs':
                _,_,text=h.fetch('/wp-admin/admin.php?page=imagine-echeances&vue=virements',abo)
                checks[name+'_C15_visible']='data-imagine-echeance="'+str(oid)+'"' in text
            s,_,again=post(third,{'c16_action':'creer','confirmer':'oui'})
            checks[name+'_rejeu_sans_doublon']=s==200 and 'data-imagine-commande="'+str(oid)+'"' in again
        # Unit-number path uses the same native order, with no subscription.
        number=c16.wp('$ps=wc_get_products(["limit"=>-1]);$out=0;foreach($ps as $p){if(Imagine\\Site\\AchatsNumeros::numero($p)>0){$out=$p->get_id();break;}}echo wp_json_encode($out);')
        _,_,first=h.fetch(PATH,abo)
        _,_,second=post(first,{'c16_action':'choisir','mode':'direct'})
        _,_,third=post(second,{'c16_action':'preparer','produit':str(number),'paiement':'bacs'})
        s,_,done=post(third,{'c16_action':'creer','confirmer':'oui'})
        found=re.search(r'data-imagine-commande="(\d+)"',done)
        checks['numero_direct_cree']=s==200 and bool(found)
        if found:
            oid=int(found.group(1));created.append(oid)
            checks['numero_sans_souscription']=c16.wp('echo wp_json_encode(count(wcs_get_subscriptions_for_order('+str(oid)+',["order_type"=>"parent"]))===0);')
    finally:
        reset=c16.wp('require WP_CONTENT_DIR."/imagine-demo-build/c16-reset.php";echo wp_json_encode(imagine_c16_reset());')
        c16.save('reset',reset)
        after=c16.wp('echo wp_json_encode(["users"=>count_users()["total_users"],"c09"=>get_option("imagine_c09_fixture"),"c12"=>get_option("imagine_decouverte_compte_".get_option("imagine_c09_fixture")["users"]["V-DEC"])]);')
        checks['reset_users_C09_C12_preserves']=after==baseline
        checks['reset_commandes_absentes']=c16.wp('$ids='+json.dumps(created)+';echo wp_json_encode(array_filter($ids,static fn($id)=>wc_get_order($id)!==false)===[]);')
    result={'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],'created_then_deleted':created}
    c16.save(label,result);print(json.dumps(result,ensure_ascii=False))
    return int(bool(result['failures']))
if __name__=='__main__':sys.exit(run(sys.argv[1] if len(sys.argv)>1 else 'http-final'))
