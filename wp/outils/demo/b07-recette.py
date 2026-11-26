"""Recette réelle HTTP B07 : POST visiteurs, données privées et inverses propres."""
import sys
sys.dont_write_bytecode=True
import json,re,html,hashlib,os
from urllib.parse import urlencode,urlsplit,urljoin
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.error import HTTPError
from html.parser import HTMLParser
from pathlib import Path
import b07
wp,php=b07.wp,b07.php
BASE='http://192.168.129.32:8085'
class Inputs(HTMLParser):
 def __init__(self):super().__init__();self.values={};self.checkboxes=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='input' and 'name' in a:self.values[a['name']]=a.get('value','')
  if tag=='input' and a.get('type')=='checkbox':self.checkboxes.append(a)
  if tag=='a':self.links.append(a)
class Redirect(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  assert urlsplit(urljoin(req.full_url,newurl)).netloc=='192.168.129.32:8085','Refus hors démo'
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def request(path,session=None,data=None):
 assert path.startswith('/') and not path.startswith('//')
 h={'User-Agent':'Imagine-B07/1.0'}
 if session:
  h['Cookie']=session['cookie']
  if session.get('nonce'):h['X-WP-Nonce']=session['nonce']
 try:r=build_opener(Redirect()).open(Request(BASE+path,data=None if data is None else urlencode(data).encode(),headers=h),timeout=45)
 except HTTPError as e:r=e
 with r:return r.code,dict(r.headers),r.read().decode('utf-8','replace'),r.url

def mutations(evidence):
 """Mutations en mémoire des réponses réellement reçues : jamais du HTML fabriqué comme témoin initial."""
 checks={}
 for key in ['passe','partenaire']:
  raw=evidence[key];anchor='id="evenement-'
  assert anchor in raw and '</article>' in raw
  detector=lambda s: anchor in s and 'id="imagine-agenda-inscription"' not in s
  assert detector(raw)
  checks[key+'_formulaire_absent']=not detector(raw.replace('</article>','<form id="imagine-agenda-inscription"></form></article>',1))
 raw=evidence['partenaire'];assert 'rel="sponsored noopener noreferrer"' in raw
 checks['lien_sponsored']= 'rel="sponsored noopener noreferrer"' not in raw.replace('rel="sponsored noopener noreferrer"','rel="noopener noreferrer"')
 raw=evidence['rencontre'];p=Inputs();p.feed(raw);assert p.checkboxes
 def unchecked(s):
  p=Inputs();p.feed(s);return len(p.checkboxes)==1 and 'checked' not in p.checkboxes[0] and 'required' not in p.checkboxes[0]
 assert unchecked(raw)
 checks['consentement_non_coche']=not unchecked(raw.replace('type="checkbox"','type="checkbox" checked',1))
 checks['consentement_facultatif']=not unchecked(raw.replace('type="checkbox"','type="checkbox" required',1))
 return checks

def run(label):
 identity=b07.b06.guard();fixture=json.loads((b07.PROOF/'fixtures-V2.json').read_text(encoding='utf-8'))['readback']
 sources=b07.b06.hashes(b07.FILES);baseline=b07.b06.state()
 accounts=wp('$f=get_option("imagine_c09_fixture");echo wp_json_encode(["admin"=>get_user_by("login","admin")->ID,"plain"=>$f["users"]["V-INSCRIT"]]);')
 email=wp('echo wp_json_encode(get_userdata('+str(accounts['plain'])+')->user_email);')
 assert email.endswith('@example.org')
 before=b07.snapshot()
 for address in ['b07-visiteur@example.org',email]:
  assert wp(r'echo wp_json_encode(Imagine\Site\Agenda::inscriptions('+php(address)+'));')==[], 'Inscription préexistante : refus sans mutation'
 oldobs=wp('echo wp_json_encode(["exists"=>file_exists(WP_CONTENT_DIR."/mu-plugins/b07-observer.php"),"option"=>get_option("imagine_b07_observer",null)]);')
 assert not oldobs['exists'] and oldobs['option'] is None
 durable=b07.private(label,{'database':before,'business':baseline,'sources':sources,'accounts':accounts})
 sessions={};checks={};evidence={};error=None;created=[]
 src=b07.ROOT/'wp/tests/demo/b07-observer.php';observer='mu-plugins/b07-observer.php';observer_hash=hashlib.sha256(src.read_bytes()).hexdigest()
 try:
  b07.b06.profils.b00.upload(observer,src.read_bytes());assert b07.b06.hashes([observer])[observer]==observer_hash
  empty={'mail':0,'http':0,'agenda_mail':0,'agenda_http':0,'transport_mail':0,'transport_http':0}
  control=wp('update_option("imagine_b07_observer",'+php(empty)+',false);wp_mail("b07-transport-fictif@example.org","Sonde fictive","Aucun envoi");wp_remote_get("https://example.org/b07-sonde");echo wp_json_encode(get_option("imagine_b07_observer"));')
  checks['observateur_controle_positif']=control=={**empty,'mail':1,'http':1}
  wp('update_option("imagine_b07_observer",'+php(empty)+',false);echo "true";')
  sessions=wp('$out=[];foreach('+php(accounts)+' as $key=>$id){$exp=time()+3600;$token=WP_Session_Tokens::get_instance($id)->create($exp);$out[$key]=["token"=>$token,"cookie"=>LOGGED_IN_COOKIE."=".wp_generate_auth_cookie($id,$exp,"logged_in",$token)."; ".AUTH_COOKIE."=".wp_generate_auth_cookie($id,$exp,"auth",$token)];}echo wp_json_encode($out);')
  b07.private(label+'-sessions',sessions)
  code,headers,body,url=request('/evenements/')
  checks['agenda_deux_sections']=code==200 and 'id="agenda-futurs"' in body and 'id="agenda-passes"' in body
  future=body.split('id="agenda-futurs"',1)[-1].split('</section>',1)[0]
  past=body.split('id="agenda-passes"',1)[-1].split('</section>',1)[0]
  ids=re.findall(r'data-evenement="(\d+)"',future)
  checks['tri_futur']=ids==[str(fixture[k]['id']) for k in ['rencontre','sortie','partenaire']]
  checks['passe_separe']=str(fixture['passe']['id']) in re.findall(r'data-evenement="(\d+)"',past) and str(fixture['passe']['id']) not in ids
  for key,e in fixture.items():
   code,h,body,url=request(e['path']);evidence[key]=body
   checks[key+'_fiche']=code==200 and 'id="evenement-'+str(e['id'])+'"' in body and html.escape(e['nom']) in body and e['lieu'] in body
   p=Inputs();p.feed(body)
   checks[key+'_formulaire']=('id="imagine-agenda-inscription"' in body)==(key in ['rencontre','sortie'])
   schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',body,re.S).group(1))
   checks[key+'_schema_champs_visibles']=schema['@type']=='Event' and schema['name']==e['nom'] and schema['startDate']==e['iso'] and schema['location']['name']==e['lieu'] and schema['description']==e['description'] and schema['description'] in html.unescape(re.sub('<[^>]+>','',body))
   no_ticket=lambda s:all(k not in s for k in ['offers','maximumAttendeeCapacity','remainingAttendeeCapacity'])
   checks[key+'_schema_sans_billet']=no_ticket(schema)
   for field in ['offers','maximumAttendeeCapacity','remainingAttendeeCapacity']:
    checks['mutation_'+key+'_schema_'+field]=not no_ticket({**schema,field:1})
   if key in ['rencontre','sortie']:
    checks[key+'_consentement_facultatif_non_coche']=len(p.checkboxes)==1 and 'checked' not in p.checkboxes[0] and 'required' not in p.checkboxes[0]
   if key=='partenaire':checks['partenaire_sponsored']=any(a.get('href')==e['url'] and 'sponsored' in a.get('rel','').split() for a in p.links)
  e=fixture['rencontre'];p=Inputs();p.feed(evidence['rencontre'])
  data={k:p.values[k] for k in ['action','evenement','imagine_agenda_nonce']};data.update(nom='Visiteur fictif B07',email='b07-visiteur@example.org')
  first=request('/wp-admin/admin-post.php',data=data);second=request('/wp-admin/admin-post.php',data={**data,'email':'B07-VISITEUR@EXAMPLE.ORG'})
  checks['inscription_http']=first[0]==200 and 'Votre demande a été enregistrée.' in html.unescape(first[2])
  stable=lambda response:(response[0],response[2],response[3])
  checks['doublon_meme_reponse']=stable(first)==stable(second)
  checks['mutation_doublon_reponse']=stable(first)!=stable((second[0],second[1],second[2]+'Adresse déjà inscrite',second[3]))
  stored=wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions("b07-visiteur@example.org",'+str(e['id'])+'));')
  created+=stored;checks['doublon_une_ligne']=len(stored)==1
  checks['mutation_doublon_deux_lignes']=len(stored+[stored[0]+1])!=1
  checks['consentement_non_exige']=wp('echo wp_json_encode(get_post_meta('+str(stored[0])+',"imagine_agenda_consentement",true));')=='0'
  result=request('/wp-admin/admin-post.php',data={**data,'email':email,'consentement':'1'})
  checks['adresse_compte_meme_reponse']=stable(result)==stable(first)
  checks['mutation_fuite_compte']=stable(result)!=stable((first[0],first[1],first[2]+email,first[3]))
  userids=wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions('+php(email)+','+str(e['id'])+'));');created+=userids
  checks['consentement_coche_persistant']=len(userids)==1 and wp('echo wp_json_encode(get_post_meta('+str(userids[0])+',"imagine_agenda_consentement",true));')=='1'
  code,h,body,url=request('/wp-admin/edit.php?post_type=imagine_inscription',sessions['admin'])
  checks['admin_liste_reelle']=code==200 and 'post-'+str(stored[0]) in body and 'post-'+str(userids[0]) in body
  code,h,body,url=request('/wp-admin/post.php?post='+str(userids[0])+'&action=edit',sessions['admin'])
  checks['admin_details_reels']=code==200 and 'id="imagine-agenda-admin"' in body and email in body and 'Visiteur fictif B07' in body
  code,h,body,url=request('/wp-admin/edit.php?post_type=imagine_inscription',sessions['plain'])
  checks['admin_non_gestionnaire_refuse']=code==403 and email not in body
  nonces=wp('wp_set_current_user(0);$out=[];foreach('+php({k:v['id'] for k,v in fixture.items()})+' as $k=>$id){$out[$k]=wp_create_nonce("imagine_agenda_".$id);}echo wp_json_encode($out);')
  for key in ['passe','partenaire']:
   response=request('/wp-admin/admin-post.php',data={**data,'evenement':fixture[key]['id'],'imagine_agenda_nonce':nonces[key]})
   refused=lambda r:r[0]==400
   checks[key+'_POST_direct_refuse']=refused(response)
   checks['mutation_'+key+'_POST_accepte']=not refused((200,*response[1:]))
   absent=lambda rows:rows==[]
   posted_rows=wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions("b07-visiteur@example.org",'+str(fixture[key]['id'])+'));')
   checks[key+'_POST_sans_ligne']=absent(posted_rows)
   checks['mutation_'+key+'_POST_avec_ligne']=not absent(posted_rows+[fixture[key]['id']])
  checks['nonce_invalide_refuse']=request('/wp-admin/admin-post.php',data={**data,'imagine_agenda_nonce':'invalide'})[0]==403
  # Les callbacks réellement enregistrés sont appelés comme le fait le pipeline natif.
  exported=wp('$ex=apply_filters("wp_privacy_personal_data_exporters",[]);echo wp_json_encode(call_user_func($ex["imagine-agenda"]["callback"],'+php(email)+',1));')
  checks['export_compte_donnees']=exported['done'] and len(exported['data'])==1 and email in json.dumps(exported) and 'Visiteur fictif B07' in json.dumps(exported)
  sans_tiers=lambda x:bool(x['data']) and 'b07-visiteur@example.org' not in json.dumps(x)
  checks['export_preserve_tiers']=sans_tiers(exported)
  checks['mutation_export_tiers']=not sans_tiers({**exported,'fuite':'b07-visiteur@example.org'})
  erased=wp('$er=apply_filters("wp_privacy_personal_data_erasers",[]);echo wp_json_encode(call_user_func($er["imagine-agenda"]["callback"],'+php(email)+',1));')
  checks['effacement_compte']=erased['done'] and erased['items_removed'] and not erased['items_retained'] and wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions('+php(email)+'));')==[]
  tiers_intacts=lambda rows:bool(stored) and rows==stored
  checks['effacement_preserve_tiers']=tiers_intacts(wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions("b07-visiteur@example.org"));'))
  checks['mutation_effacement_detruit_tiers']=not tiers_intacts([])
  erase_complete=lambda x:x['done'] and x['items_removed'] and not x['items_retained']
  checks['mutation_effacement_incomplet']=not erase_complete({**erased,'items_retained':True})
  for path in ['/?p='+str(stored[0]),'/wp-json/wp/v2/imagine_inscription','/?rest_route=/wp/v2/imagine_inscription']:
   code,h,body,url=request(path);checks['prive_'+str(len(checks))]=code in [403,404] and 'b07-visiteur@example.org' not in body
   detector=lambda c,s:c in [403,404] and 'b07-visiteur@example.org' not in s
   checks['mutation_prive_'+str(len(checks))]=not detector(code,body+'b07-visiteur@example.org')
  mut=mutations(evidence);checks.update({'mutation_'+k:v for k,v in mut.items()})
  # Contrôle d'absence qualifié sur les vrais compteurs et leur mutation témoin.
  counts=wp('echo wp_json_encode(get_option("imagine_b07_observer"));')
  expected_keys=set(empty)
  closed=lambda c:set(c)==expected_keys and all(c[k]==0 for k in ['agenda_mail','agenda_http','transport_mail','transport_http'])
  checks['aucun_transport_pendant_parcours']=closed(counts)
  for key in ['agenda_mail','agenda_http','transport_mail','transport_http']:
   checks['mutation_observateur_'+key]=not closed({**counts,key:1})
 except Exception as exc:error=type(exc).__name__+': '+str(exc)
 finally:
  # Inverses indépendants : les sessions ne se trouvent jamais dans les preuves publiques.
  try:
   wp('$f=get_option("imagine_b07_fixture");foreach(get_posts(["post_type"=>"imagine_inscription","post_status"=>"any","numberposts"=>-1]) as $p){$email=get_post_meta($p->ID,"imagine_agenda_email",true);if(in_array($p->post_parent,array_values($f))&&in_array($email,["b07-visiteur@example.org",'+php(email)+'])){wp_delete_post($p->ID,true);}}echo "true";')
   if sessions:wp('$sessions='+php(sessions)+';$ids='+php(accounts)+';foreach($sessions as $key=>$s){WP_Session_Tokens::get_instance($ids[$key])->destroy($s["token"]);}echo "true";')
   # La première visite de l'écran Woo natif ajoute cette préférence UI seulement.
   if not any(int(r['user_id'])==accounts['admin'] and r['meta_key']=='meta-box-order_product' for r in before['usermeta']):
    wp('delete_user_meta('+str(accounts['admin'])+',"meta-box-order_product");echo wp_json_encode(!metadata_exists("user",'+str(accounts['admin'])+',"meta-box-order_product"));')
   checks['inscriptions_essai_retirees']=wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions("b07-visiteur@example.org"));')==[] and wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions('+php(email)+'));')==[]
  finally:
   removed=b07.remove_observer(observer_hash)
   wp('delete_option("imagine_b07_observer");echo "true";')
   checks['observateur_retire']=removed and wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/mu-plugins/b07-observer.php")&&get_option("imagine_b07_observer",null)===null);')
  checks['etat_metier_exact']=baseline==b07.b06.state()
  checks['sources_inchangees']=sources==b07.b06.hashes(b07.FILES)
 d={'identity':identity,'total':len(checks),'checks':checks,'failures':[k for k,v in checks.items() if not v],'error':error,'sources':sources,'private_snapshot':durable,'transport_counts':locals().get('counts'),'mutations':{k:v for k,v in checks.items() if k.startswith('mutation_')}}
 b07.save(label,d);print(json.dumps(d,ensure_ascii=False));assert not error and not d['failures']
if __name__=='__main__':run(sys.argv[1])
