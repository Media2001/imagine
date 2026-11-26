"""B07 non-régression GET seule des portes articles existantes ; aucun réglage forcé."""
import sys
sys.dont_write_bytecode=True
import json,importlib.util
from urllib.parse import urlencode,quote
import b07
spec=importlib.util.spec_from_file_location('b07_http',b07.ROOT/'wp/outils/demo/b07-recette.py');http=importlib.util.module_from_spec(spec);spec.loader.exec_module(http)
wp,php=b07.wp,b07.php

def run(label):
 b07.b06.guard();baseline=b07.b06.state()
 f=wp('$a=get_option("imagine_c08_fixture");$u=get_option("imagine_c09_fixture")["users"];echo wp_json_encode(["article"=>$a["article"],"title"=>get_the_title($a["article"]),"path"=>wp_parse_url(get_permalink($a["article"]),PHP_URL_PATH),"users"=>["sans-droit"=>$u["V-INSCRIT"],"abonne"=>$u["A-CARTE"],"cooperateur"=>$u["P-COOP"]]]);')
 snap=b07.private(label,{'business':baseline,'database':b07.snapshot()})
 sessions={};checks={};error=None
 marker='Les lucioles violettes de C08 gardent le secret du village fictif.'
 try:
  sessions=wp('$out=[];foreach('+php(f['users'])+' as $key=>$id){$exp=time()+3600;$token=WP_Session_Tokens::get_instance($id)->create($exp);$logged=wp_generate_auth_cookie($id,$exp,"logged_in",$token);$_COOKIE[LOGGED_IN_COOKIE]=$logged;wp_set_current_user($id);$out[$key]=["token"=>$token,"cookie"=>LOGGED_IN_COOKIE."=".$logged,"nonce"=>wp_create_nonce("wp_rest")];}echo wp_json_encode($out);')
  b07.private(label+'-sessions',sessions)
  for audience in ['abonne','anonyme','sans-droit','cooperateur']:
   session=sessions.get(audience)
   for path in [f['path'],'/wp-json/wp/v2/posts/'+str(f['article']),'/?rest_route=/wp/v2/posts/'+str(f['article'])]:
    code,h,body,url=http.request(path,session)
    present=marker in body or marker in json.dumps(json.loads(body),ensure_ascii=False) if body.lstrip().startswith('{') else marker in body
    exists=(f['title'] in body or json.dumps(f['title'],ensure_ascii=True)[1:-1] in body)
    checks[audience+'_'+str(len(checks))]=code==200 and exists and (present if audience=='abonne' else not present)
    if audience!='abonne':
     detector=lambda raw:marker not in raw
     checks['mutation_article_'+str(len(checks))]=not detector(body+marker)
  for path in ['/?feed=rss2&posts_per_rss=100','/?s='+quote(f['title']),'/wp-json/oembed/1.0/embed?'+urlencode({'url':http.BASE+f['path']})]:
   code,h,body,url=http.request(path)
   checks['anonyme_surface_'+str(len(checks))]=code==200 and (('<channel>' in body) if 'feed=' in path else ('<main' in body if '?s=' in path else '"html"' in body)) and marker not in body
   detector=lambda raw:marker not in raw
   checks['mutation_surface_'+str(len(checks))]=not detector(body+marker)
  code,h,body,url=http.request('/wp-json/wp/v2/posts/'+str(f['article'])+'?context=edit')
  checks['REST_edit_ferme']=code in [401,403] and marker not in body
 except Exception as exc:error=type(exc).__name__+': '+str(exc)
 finally:
  if sessions:wp('$sessions='+php(sessions)+';$ids='+php(f['users'])+';foreach($sessions as $key=>$s){WP_Session_Tokens::get_instance($ids[$key])->destroy($s["token"]);}echo "true";')
  checks['etat_metier_exact']=baseline==b07.b06.state()
 d={'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if not v],'error':error,'private_snapshot':snap}
 b07.save(label,d);print(json.dumps(d,ensure_ascii=False));assert not error and not d['failures']
if __name__=='__main__':run(sys.argv[1])
