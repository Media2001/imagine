"""B04 corrections: targeted deploy or real HTTP, exact temporary-state readback."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('b04_http', HERE / 'b04-http.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
w = h.work
FILES = {
    'plugins/imagine-site/Paywall.php': 'wp/plugins/imagine-site/Paywall.php',
    'plugins/imagine-site/Decouverte.php': 'wp/plugins/imagine-site/Decouverte.php',
    'themes/imagine/inc/catalogue.php': 'wp/themes/imagine/inc/catalogue.php',
    'themes/imagine/single-imagine_numero.php': 'wp/themes/imagine/single-imagine_numero.php',
    'mu-plugins/imagine-demo-b04-preview.php': 'wp/outils/demo/b04-preview.php',
}
SNAPSHOT = r'''
$u=(int)get_option('imagine_c09_fixture')['users']['V-DEC'];$m=get_option('imagine_demo_manifest');
$keys=['imagine_decouverte_reglages','imagine_decouverte_relecture',Imagine\Site\Decouverte::key($u)];
$o=[];foreach($keys as $k){$o[$k]=get_option($k,null);}
echo wp_json_encode(['options'=>$o,'verified'=>get_user_meta($u,'imagine_email_confirme',false),
 'release'=>get_post_meta($m['demo-2026-t1'],'imagine_sortie',false)]);
'''
INVENTORY = r'''
$m=get_option('imagine_demo_manifest');$f=get_option('imagine_c12_fixture');$u=get_option('imagine_c09_fixture')['users'];
$a=get_post($f['un']);$issue=get_post($m['demo-2026-t1']);$dissue=get_post($m['demo-2026-t4']);
$terms=get_terms(['taxonomy'=>'imagine_thematique','hide_empty'=>false]);
$t=is_array($terms)&&$terms ? $terms[0] : null;
$owned=[];foreach(Imagine\Site\AchatsNumeros::droits($u['P-NUMERO']) as $r){$owned[]=$r['numero'];}
echo wp_json_encode(['user'=>$u['V-DEC'],'buyer'=>$u['P-NUMERO'],'article'=>$a->ID,
 'article_path'=>wp_parse_url(get_permalink($a),PHP_URL_PATH),
 'issue'=>$issue->ID,'issue_path'=>wp_parse_url(get_permalink($issue),PHP_URL_PATH),
 'discovery_issue'=>$dissue->ID,'discovery_path'=>wp_parse_url(get_permalink($dissue),PHP_URL_PATH),
 'marker'=>trim(wp_strip_all_tags($a->post_content)),
 'term'=>$t ? $t->term_id : null,'term_path'=>$t ? wp_parse_url(get_term_link($t),PHP_URL_PATH) : null,
 'original_terms'=>wp_get_object_terms($a->ID,'imagine_thematique',['fields'=>'ids']),
 'owned'=>$owned,'settings'=>Imagine\Site\Decouverte::reglages()]);
'''

def deploy(phase):
    w.guard()
    paths=list(FILES)
    backup=w.PROOF/('corrections-before-'+phase+'.json')
    assert not backup.exists(), 'Préimage déjà présente'
    old=w.wp('$o=[];foreach(json_decode('+json.dumps(json.dumps(paths))+',true) as $p){$f=WP_CONTENT_DIR."/".$p;$o[$p]=is_file($f)?base64_encode(file_get_contents($f)):null;}echo wp_json_encode($o);')
    backup.write_text(json.dumps(old,indent=2),encoding='utf-8')
    expected={}
    for target,relative in FILES.items():
        p=w.ROOT/relative
        candidate='imagine-demo-build/b04-correction-lint-'+p.name
        w.c08.b00.upload(candidate,p.read_bytes())
        assert w.wp('token_get_all(file_get_contents(WP_CONTENT_DIR."/'+candidate+'"),TOKEN_PARSE);echo "true";') is True
        expected[target]=w.digest(p)
    for target,relative in FILES.items():
        w.c08.b00.upload(target,(w.ROOT/relative).read_bytes())
    actual=w.readback(paths)
    assert actual==expected
    result={'scope':'imagine-test-demo','exact':True,'expected':expected,'actual':actual}
    (w.PROOF/('deploy-corrections-'+phase+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'deploy_exact':True,'files':len(paths)}),flush=True)

def verify(phase):
    w.guard()
    inventory=w.wp(INVENTORY)
    assert inventory['marker'].strip(), 'Marqueur privé vide : preuve refusée'
    assert str(inventory['issue']) in inventory['owned'], 'Achat natif préexistant requis'
    before=w.wp(SNAPSHOT)
    checkpoint={'scope':'imagine-test-demo','before':before,'user':inventory['user'],
        'issue':inventory['issue'],'article':inventory['article'],'original_terms':inventory['original_terms']}
    (w.PROOF/('fixture-corrections-before-'+phase+'.json')).write_text(json.dumps(checkpoint,indent=2),encoding='utf-8')
    checks={}
    key='imagine_decouverte_compte_'+str(inventory['user'])
    settings={'ouverture':'premiere_lecture','forme':'articles','jours':7,'nombre':2,'numeros':[str(inventory['discovery_issue'])]}
    accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    client=h.http.login(accounts['V-DEC'])
    buyer=h.http.login(accounts['P-NUMERO'])
    try:
        w.wp('delete_option('+json.dumps(key)+');update_user_meta('+str(inventory['user'])+',"imagine_email_confirme","1");update_option("imagine_decouverte_reglages",json_decode('+json.dumps(json.dumps(settings))+',true));update_option("imagine_decouverte_relecture","fermee");echo "true";')
        # Existing C12 witness only: restore its exact taxonomy relationship in finally.
        if inventory['term']:
            w.wp('$r=wp_set_object_terms('+str(inventory['article'])+',['+str(inventory['term'])+'],"imagine_thematique");if(is_wp_error($r)){throw new RuntimeException("B04 taxonomy fixture refused");}echo "true";')
        for label,path in [('numero',inventory['discovery_path']),('thematique',inventory['term_path'])]:
            assert path, 'Thématique témoin requise'
            for repeat in range(2):
                status,_,text=h.http.fetch(path,client)
                soup=h.BeautifulSoup(text,'html.parser')
                badge=soup.select_one('[data-imagine-id="'+str(inventory['article'])+'"] [data-imagine-access]')
                prefix=label+':'+str(repeat)+':'
                checks[prefix+'decouverte_visible']=status==200 and bool(badge and badge.get('data-imagine-access')=='decouverte' and badge.get_text(strip=True)=='Découverte')
                checks[prefix+'sans_corps']=inventory['marker'] not in text
                checks[prefix+'sans_ouverture_ni_quota']=w.wp('echo wp_json_encode(get_option('+json.dumps(key)+',null));') is None
        code,_,article=h.http.fetch(inventory['article_path'],client)
        state=w.wp('echo wp_json_encode(get_option('+json.dumps(key)+',null));')
        checks['decouverte_destination_reelle']=code==200 and inventory['marker'] in h.BeautifulSoup(article,'html.parser').get_text(' ',strip=True)
        checks['lecture_seule_consomme']=isinstance(state,dict) and state['articles']==[inventory['article']]
        for label,path in [('numero',inventory['discovery_path']),('thematique',inventory['term_path'])]:
            _,_,text=h.http.fetch(path,client)
            badge=h.BeautifulSoup(text,'html.parser').select_one('[data-imagine-id="'+str(inventory['article'])+'"] [data-imagine-access]')
            checks[label+':apres_lecture_decouverte']=bool(badge and badge.get('data-imagine-access')=='decouverte')
            checks[label+':etat_exact_preserve']=w.wp('echo wp_json_encode(get_option('+json.dumps(key)+',null));')==state
            _,_,anonymous=h.http.fetch(path)
            checks[label+':anonyme_sans_corps']=inventory['marker'] not in anonymous
        # Future date on the already-owned fictive issue, never an order/payment mutation.
        w.wp('update_post_meta('+str(inventory['issue'])+',"imagine_sortie","2099-01-01");echo "true";')
        for label,visitor,expected_buy in [('acheteur',buyer,False),('anonyme',None,True)]:
            code,_,text=h.http.fetch(inventory['issue_path'],visitor)
            soup=h.BeautifulSoup(text,'html.parser')
            checks['futur:'+label+':achat_independant_du_PDF']=code==200 and bool(soup.select_one('[data-imagine-buy]'))==expected_buy
            checks['futur:'+label+':PDF_ferme']=not soup.select_one('[data-imagine-pdf]') and 'imagine_pdf=' not in text
            pcode,pheaders,data=h.http.fetch('/?imagine_pdf='+str(inventory['issue']),visitor)
            checks['futur:'+label+':route_PDF_refusee']=not pheaders.get('content-type','').startswith('application/pdf') and not data.startswith('%PDF-')
        # Real released GET. Exact release instant is separately covered by PHPUnit.
        w.wp('update_post_meta('+str(inventory['issue'])+',"imagine_sortie","2000-01-01");echo "true";')
        code,_,text=h.http.fetch(inventory['issue_path'],buyer)
        soup=h.BeautifulSoup(text,'html.parser')
        checks['sorti:acheteur_sans_achat']=code==200 and not soup.select_one('[data-imagine-buy]')
        checks['sorti:acheteur_PDF_ouvert']=bool(soup.select_one('[data-imagine-pdf]'))
        _,headers,data=h.http.fetch('/?imagine_pdf='+str(inventory['issue']),buyer)
        checks['sorti:PDF_natif_reel']=headers.get('content-type','').startswith('application/pdf') and data.startswith('%PDF-')
        checks['sommaire_sans_redondance']='Dans le numéro :' not in soup.select_one('#imagine-contents-list').get_text()
    finally:
        code='$old=json_decode('+json.dumps(json.dumps(before))+',true);foreach($old["options"] as $k=>$v){if($v===null){delete_option($k);}else{update_option($k,$v);}}'
        code+='delete_user_meta('+str(inventory['user'])+',"imagine_email_confirme");foreach($old["verified"] as $v){add_user_meta('+str(inventory['user'])+',"imagine_email_confirme",$v);}'
        code+='delete_post_meta('+str(inventory['issue'])+',"imagine_sortie");foreach($old["release"] as $v){add_post_meta('+str(inventory['issue'])+',"imagine_sortie",$v);}'
        # Published issue guard forbids removing release: update to original exact single value.
        code=code[:code.index('delete_post_meta(')]+'update_post_meta('+str(inventory['issue'])+',"imagine_sortie",$old["release"][0]);'
        code+='wp_set_object_terms('+str(inventory['article'])+',json_decode('+json.dumps(json.dumps(inventory['original_terms']))+',true),"imagine_thematique");echo "true";'
        w.wp(code)
        checks['restauration_exacte_options_verification_sortie']=w.wp(SNAPSHOT)==before
        checks['restauration_exacte_thematiques']=w.wp('echo wp_json_encode(wp_get_object_terms('+str(inventory['article'])+',"imagine_thematique",["fields"=>"ids"]));')==inventory['original_terms']
    result={'scope':'imagine-test-demo','at':datetime.now(timezone.utc).isoformat(),'total':len(checks),'checks':checks,'failures':[k for k,v in checks.items() if v is not True],
        'owned_native_issue':inventory['issue'],'native_purchase_preexisting':True,'created_order_or_payment':False,'private_marker_nonempty':True}
    (w.PROOF/('native-http-corrections-'+phase+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'phase':phase,'total':len(checks),'failures':result['failures']},ensure_ascii=False),flush=True)
    if result['failures']: raise SystemExit(1)
    return result

if __name__=='__main__':
    {'deploy':deploy,'http':verify}[sys.argv[1]](sys.argv[2] if len(sys.argv)>2 else 'final')
