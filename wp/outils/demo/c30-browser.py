import sys
sys.dont_write_bytecode=True
import importlib.util
import json
import c30 as owner
import b13
spec=importlib.util.spec_from_file_location('c30_browser_common',b13.ROOT/'wp/outils/demo/b13-browser.py')
common=importlib.util.module_from_spec(spec);spec.loader.exec_module(common)
rows_before=b13.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));')
private=b13.b11.private(sys.argv[1]+'-sessions',rows_before)
keys=set()
def checker(page,body,role,index,f,markers,check):
    main=page.locator('#imagine-main')
    check(f'{role}_{index}_page',main.locator('h1').all_text_contents()==['Bienvenue'])
    check(f'{role}_{index}_aucun_code_affiche','NON_LISTE_INTERDIT' not in main.inner_html() and 'fictif-affiche' not in main.inner_html())
    check(f'{role}_{index}_texte_vide',main.locator('article').inner_text().strip()=="Bienvenue\nS’abonner")
    check(f'{role}_{index}_etanche',common.c26.c23.assess(200,body,markers)['ok'])
    check(f'{role}_{index}_mutation',not common.c26.c23.assess(200,body+'<!--'+markers[0]+'-->',markers)['ok'])
    check(f'{role}_{index}_abonnement',main.locator('a[href$="/abonnement-en-attente/"]').count()==1)
    cookies=[c for c in page.context.cookies() if c['name'].startswith('wp_woocommerce_session_')]
    if index<2:
        check(f'{role}_{index}_pas_cookie_code_inconnu',cookies==[])
        value=None
    else:
        check(f'{role}_{index}_cookie_natif',len(cookies)==1 and cookies[0]['httpOnly'])
        key=cookies[0]['value'].split('%7C')[0].split('||')[0]
        keys.add(key)
        value=b13.wp('$s=new WC_Session_Handler();$d=$s->get_session('+b13.php(key)+');echo wp_json_encode(isset($d[Imagine\\Site\\CodesSuivis::SESSION])?maybe_unserialize($d[Imagine\\Site\\CodesSuivis::SESSION]):null);')
        expected='fictif-affiche' if index==2 else 'fictif-magazine'
        check(f'{role}_{index}_session_relue',value is not None and value['code']==expected)
    return {'session_code':value['code'] if value else None}
try:
    common.run(owner,sys.argv[1],checker,paths=['/bienvenue/','/bienvenue/?code=NON_LISTE_INTERDIT','/bienvenue/?code=fictif-affiche','/bienvenue/?code=fictif-magazine','/bienvenue/'])
finally:
    restore=b13.wp('global $wpdb;$before='+b13.php(rows_before)+';$keys='+b13.php(list(keys))+';foreach($keys as $key){$wpdb->delete($wpdb->prefix."woocommerce_sessions",["session_key"=>$key]);}foreach($before as $row){if(in_array($row["session_key"],$keys,true)){$wpdb->insert($wpdb->prefix."woocommerce_sessions",$row);}}echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A)===$before);')
    b13.save(owner,sys.argv[1]+'-sessions',{'restored':restore,'private':private,'sources':owner.sources(owner)})
    print('Sessions restaurées',restore)
    assert restore
