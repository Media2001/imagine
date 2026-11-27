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
    check(f'{role}_{index}_texte_vide',main.locator('article').inner_text().split()==['Bienvenue','S’abonner'])
    check(f'{role}_{index}_etanche',common.c26.c23.assess(200,body,markers)['ok'])
    check(f'{role}_{index}_mutation',not common.c26.c23.assess(200,body+'<!--'+markers[0]+'-->',markers)['ok'])
    check(f'{role}_{index}_abonnement',main.locator('a[href$="/abonnement-en-attente/"]').count()==1)
    cookies=[c for c in page.context.cookies() if c['name'].startswith('wp_woocommerce_session_')]
    if index<2:
        check(f'{role}_{index}_pas_cookie_code_inconnu',cookies==[])
        value=None
    else:
        check(f'{role}_{index}_cookie_natif',len(cookies)==1 and cookies[0]['httpOnly'])
        key=cookies[0]['value'].split('%7C')[0].split('|')[0]
        keys.add(key)
        value=b13.wp('$s=new WC_Session_Handler();$d=$s->get_session('+b13.php(key)+');echo wp_json_encode(isset($d[Imagine\\Site\\CodesSuivis::SESSION])?maybe_unserialize($d[Imagine\\Site\\CodesSuivis::SESSION]):null);')
        expected='fictif-affiche' if index==2 else 'fictif-magazine'
        check(f'{role}_{index}_session_relue',value is not None and value['code']==expected)
    return {'session_code':value['code'] if value else None}
try:
    common.run(owner,sys.argv[1],checker,paths=['/bienvenue/','/bienvenue/?code=NON_LISTE_INTERDIT','/bienvenue/?code=fictif-affiche','/bienvenue/?code=fictif-magazine','/bienvenue/'])
finally:
    by_key={r['session_key']:r for r in rows_before}
    current=b13.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));')
    now={r['session_key']:r for r in current}
    changed={k for k in by_key.keys()|now.keys() if by_key.get(k)!=now.get(k)}
    assert all(k in keys or (k not in by_key and not k.isdigit()) or 'imagine_code_suivi' in now.get(k,{}).get('session_value','') for k in changed), 'Session préexistante étrangère non restaurée'
    for key in changed:
        code='global $wpdb;$wpdb->delete($wpdb->prefix."woocommerce_sessions",["session_key"=>'+b13.php(key)+']);'
        if key in by_key:code+='$wpdb->insert($wpdb->prefix."woocommerce_sessions",'+b13.php(by_key[key])+');'
        assert b13.wp(code+'echo wp_json_encode(true);')
    readback=b13.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));')
    restore=readback==rows_before
    b13.save(owner,sys.argv[1]+'-sessions',{'restored':restore,'private':private,'sources':owner.sources(owner)})
    print('Sessions restaurées',restore)
    assert restore
