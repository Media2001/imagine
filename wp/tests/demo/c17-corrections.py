"""C17 fusion: targeted real WordPress/HTTP gates; synthetic demo only."""
from pathlib import Path
import importlib.util
import json
import hashlib
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import c17_http as t
ROOT = t.c17.ROOT
PROOF = ROOT / 'production/C-17/corrections-20261126'
PROOF.mkdir(parents=True, exist_ok=True)
t.c17.PROOF = PROOF

def save(name, result):
    t.c17.save(name, result)
    print(json.dumps(result, ensure_ascii=False))
    return int(bool(result.get('failures')))

def action():
    return t.c17.wp('global $wpdb;echo wp_json_encode($wpdb->get_row("SELECT * FROM {$wpdb->prefix}actionscheduler_actions WHERE action_id=8793",ARRAY_A));')

def b02(label):
    source = ROOT / 'wp/tests/demo/b02-runtime.php'
    target = '/imagine-demo-build/b02-runtime.php'
    t.c17.profils.b00.upload(target.lstrip('/'), source.read_bytes())
    actual = t.c17.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR.' + json.dumps(target) + '));')
    assert actual == hashlib.sha256(source.read_bytes()).hexdigest()
    checks = t.c17.wp('require WP_CONTENT_DIR.' + json.dumps(target) + ';')
    checks['C17_charge_et_hook_compte'] = t.c17.wp('echo wp_json_encode(class_exists(Imagine\\Site\\Justificatifs::class)&&has_action("imagine_compte_justificatif",[Imagine\\Site\\Justificatifs::class,"compte"])!==false);')
    return save(label, {'checks': checks, 'total': len(checks), 'failures': [k for k,v in checks.items() if v is not True], 'runtime_sha256_readback': actual})

def deploy(label):
    name = 'plugins/imagine-site/Justificatifs.php'
    source = ROOT / 'wp/plugins/imagine-site/Justificatifs.php'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    old = t.c17.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR.' + json.dumps('/'+name) + '));')
    prior = ROOT / 'production/C-17/installation.json'
    allowed = {digest, json.loads(prior.read_text())['sha256_readback'][name]}
    for p in PROOF.glob('deploy-*.json'):
        allowed.add(json.loads(p.read_text())['sha256_readback'])
    assert old in allowed, 'Refusing source drift'
    native = t.c17.state(); planned = action()
    t.c17.profils.b00.upload(name, source.read_bytes())
    actual = t.c17.wp('$p=WP_CONTENT_DIR.' + json.dumps('/'+name) + ';token_get_all(file_get_contents($p),TOKEN_PARSE);echo wp_json_encode(hash_file("sha256",$p));')
    assert actual == digest and native == t.c17.state() and action() == planned
    return save('deploy-'+label, {'sha256_before':old,'sha256_readback':actual,'native_preserved':True,'action8793_before':planned,'action8793_after':action(),'failures':[]})

def replacement(label):
    accounts = json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text())['c09_accounts']
    owner = t.h.login(accounts['P-SOL-ATT'])
    abo = t.h.login(accounts['E-ABO'])
    uid = t.c17.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]["P-SOL-ATT"]);')
    before = t.c17.state(); planned = action(); checks = {}; evidence = {}
    try:
        old = t.stored(uid)
        opened = t.form(abo, uid)
        old_url = t.file_url(t.form(owner))
        # Fault injection is process-local: production has no test filter or endpoint.
        # The real receiver deletes the real old file before its fopen() fails.
        fault = t.c17.wp('eval(\'namespace Imagine\\\\Site; function fopen($path,$mode) { return false; }\');'
            '$id=' + str(uid) + ';$s=Imagine\\Site\\Justificatifs::etat($id);$failed=false;'
            'try {Imagine\\Site\\Justificatifs::recevoir($id,"à préciser",base64_decode(' + json.dumps(__import__('base64').b64encode(t.dummy_pdf('C17 fictif remplacement')).decode()) + '),Imagine\\Site\\Justificatifs::version($s));}'
            'catch(Throwable $e){$failed=true;}echo wp_json_encode($failed);')
        current = t.stored(uid)
        checks['echec_fopen_injecte_apres_suppression_reelle'] = fault and t.absent(old['path'])
        checks['revision_invalidee'] = current['state'] != old['state']
        checks['etat_indisponible_sans_blob'] = current['state'].get('indisponible') is True and 'blob' not in current['state']
        account_html = t.form(owner); queue_html = t.form(abo, uid)
        checks['compte_indisponibilite_sans_lien_mort'] = 'Document indisponible' in account_html and 'imagine_justificatif=' not in account_html
        checks['file_indisponibilite_sans_lien_ni_decision'] = 'Document indisponible' in queue_html and 'imagine_justificatif=' not in queue_html and 'imagine_justificatif_decider' not in queue_html
        checks['ancienne_URL_404'] = t.h.fetch(old_url, owner)[0] == 404
        stale_status,_,_ = t.decision(abo, opened)
        checks['ancien_formulaire_referent_refuse_409'] = stale_status == 409 and t.stored(uid) == current
        status,_,_ = t.upload(owner, t.form(owner), t.dummy_pdf('C17 nouveau fictif'))
        checks['nouveau_depot_repare'] = status == 200 and t.stored(uid)['exists'] and 'indisponible' not in t.stored(uid)['state']
        evidence = {'before':old,'after_failed_write':current,'old_form_status':stale_status, 'new_upload_status':status}
    finally:
        t.c17.reset()
        checks['etat_natif_preserve'] = before == t.c17.state()
        checks['action8793_exacte_pending101_preservee'] = action() == planned and planned['status'] == 'pending' and '101' in planned['args']
    return save(label, {'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True], 'evidence':evidence,'fault_injection':'process-local namespaced fopen returns false; real old file deletion and persistent WP option + HTTP stale form'})

def deletion(label):
    import uuid, base64
    before = t.c17.state(); planned = action(); checks = {}; evidence = []
    for state in ['en_attente', 'valide', 'refuse', 'obstacle']:
        login = 'c17-fictif-delete-' + uuid.uuid4().hex
        uid = t.c17.wp('$id=wp_insert_user(["user_login"=>' + json.dumps(login) + ',"user_pass"=>wp_generate_password(40,true),"user_email"=>' + json.dumps(login+'@example.org') + ',"display_name"=>"C17 FICTIF suppression","role"=>"subscriber"]);if(is_wp_error($id))throw new RuntimeException("Fixture failed");echo wp_json_encode($id);')
        prefix = '$id=' + str(uid) + ';$key=Imagine\\Site\\Justificatifs::PREFIX.$id;'
        source = None
        try:
            t.c17.wp(prefix + 'Imagine\\Site\\Justificatifs::recevoir($id,"à préciser",base64_decode(' + json.dumps(base64.b64encode(t.dummy_pdf('C17 FICTIF suppression')).decode()) + '),Imagine\\Site\\Justificatifs::version([]));echo "true";')
            source = t.stored(uid)
            if state in ['valide', 'refuse']:
                t.c17.wp(prefix + '$s=Imagine\\Site\\Justificatifs::etat($id);$new=Imagine\\Site\\JustificatifRegles::decider($s,' + json.dumps(state) + ',gmdate("Y-m-d"),"e-abo",gmdate("Y-m-d\\TH:i:s\\Z"));Imagine\\Site\\Justificatifs::supprimerFichier($s);update_option($key,$new,false);echo "true";')
            if state == 'obstacle':
                t.c17.wp('$p=' + json.dumps(source['path']) + ';if(!rename($p,$p.".c17-backup")||!mkdir($p,0700))throw new RuntimeException("Obstacle failed");echo "true";')
            result = t.c17.wp(prefix + 'require_once ABSPATH."wp-admin/includes/user.php";'
                'add_filter("wp_die_handler",static fn()=>static function($message,$title,$args){throw new RuntimeException((string)$message,(int)($args["response"]??0));});'
                '$result=null;$error=null;try{$result=wp_delete_user($id);}catch(Throwable $e){$error=["message"=>$e->getMessage(),"code"=>$e->getCode()];}echo wp_json_encode(["deleted"=>$result,"error"=>$error]);')
            # A separate process reads the actual deletion, option and private disk.
            readback = t.c17.wp(prefix + '$p=' + json.dumps(source['path']) + ';echo wp_json_encode(["account_exists"=>(bool)get_userdata($id),"option"=>get_option($key,null),"file_or_directory"=>file_exists($p),"backup"=>file_exists($p.".c17-backup")]);')
            if state == 'obstacle':
                checks['suppression_physique_impossible_erreur_explicite'] = result['deleted'] is None and result['error'] is not None and result['error']['code'] == 409 and 'Suppression du compte refusée' in result['error']['message']
                checks['echec_physique_compte_option_reference_conserves'] = readback['account_exists'] and readback['option'] == source['state'] and readback['file_or_directory'] and readback['backup']
            else:
                checks[state+'_compte_supprime_nativement'] = result['deleted'] is True and not readback['account_exists']
                checks[state+'_option_supprimee'] = readback['option'] is None
                checks[state+'_fichier_absent'] = not readback['file_or_directory']
            evidence.append({'state':state,'user':uid,'result':result,'readback':readback})
        finally:
            # Delete only this uniquely named synthetic user and its exact file.
            cleanup = prefix + '$u=get_userdata($id);if($u&&$u->user_login!==' + json.dumps(login) + ')throw new RuntimeException("Foreign user");'
            if source:
                cleanup += '$p=' + json.dumps(source['path']) + ';if(is_dir($p)&&!is_link($p))rmdir($p);if(is_file($p))unlink($p);if(is_file($p.".c17-backup"))unlink($p.".c17-backup");'
            cleanup += 'delete_option($key);require_once ABSPATH."wp-admin/includes/user.php";if($u)wp_delete_user($id);echo wp_json_encode(!get_userdata($id)&&get_option($key,null)===null);'
            checks[state+'_fixture_nettoyee'] = t.c17.wp(cleanup)
    checks['etat_natif_preserve'] = before == t.c17.state()
    checks['action8793_exacte_preservee'] = planned == action()
    return save(label, {'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],'evidence':evidence})

def boundaries(label):
    from PIL import Image
    import io
    accounts = json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text())['c09_accounts']
    owner = t.h.login(accounts['P-SOL-ATT']); abo = t.h.login(accounts['E-ABO'])
    uid = t.c17.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]["P-SOL-ATT"]);')
    before = t.c17.state(); planned = action(); checks = {}; evidence = {}
    try:
        for extension, mime in [('png','image/png'),('jpg','image/jpeg')]:
            data = (ROOT / ('wp/plugins/imagine-site/tests/fixtures/c17-fictif.' + extension)).read_bytes()
            Image.open(io.BytesIO(data)).verify()
            status,_,_ = t.upload(owner,t.form(owner),data,name='fictif.pdf')
            stored = t.stored(uid)
            served,headers,body = t.raw(t.file_url(t.form(owner)),owner)
            checks[extension+'_complet_upload_persistant'] = status == 200 and stored['exists'] and stored['sha256'] == hashlib.sha256(data).hexdigest()
            checks[extension+'_lecture_type_octets_exacts'] = served == 200 and headers['content-type'] == mime and body == data
        pdf = (ROOT/'wp/plugins/imagine-site/tests/fixtures/c17-fictif.pdf').read_bytes()
        pdf = pdf.replace(b'%%EOF', b'%' + b' '*(5242880-len(pdf)-2) + b'\n%%EOF')
        assert len(pdf) == 5242880
        status,_,_ = t.upload(owner,t.form(owner),pdf)
        stored = t.stored(uid)
        served,headers,body = t.raw(t.file_url(t.form(owner)),owner)
        checks['plafond_exact_5Mio_depot_accepte'] = status == 200 and stored['exists'] and stored['sha256'] == hashlib.sha256(pdf).hexdigest()
        checks['plafond_exact_5Mio_servi_integralement'] = served == 200 and body == pdf and headers['content-type'] == 'application/pdf'
        today = t.c17.wp('echo wp_json_encode(gmdate("Y-m-d"));')
        status,_,_ = t.decision(abo,t.form(abo,uid),{'fin':today})
        decided = t.stored(uid)
        checks['date_fin_aujourdhui_acceptee_HTTP'] = status == 200 and decided['state']['decision'] == 'valide' and decided['state']['fin'] == today and t.absent(stored['path'])
        checks['trois_champs_selon_arbitrage_4h30'] = set(decided['state']) == {'categorie','decision','fin'}
        evidence = {'today_UTC':today, 'exact_max_size':len(pdf), 'decision_readback':decided}
    finally:
        t.c17.reset()
        checks['etat_natif_preserve'] = before == t.c17.state()
        checks['action8793_exacte_preservee'] = planned == action()
    return save(label, {'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],'evidence':evidence})

def all_gates(label):
    from datetime import datetime, timezone
    import re, subprocess
    def module(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        out = importlib.util.module_from_spec(spec); spec.loader.exec_module(out)
        return out
    def sources():
        names = ['plugins/imagine-site/imagine-site.php','imagine-demo-build/c09-seed.php','themes/imagine/parts/mon-compte.php']
        return t.c17.wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(names)) + ',true) as $n){$out[$n]=hash_file("sha256",WP_CONTENT_DIR."/".$n);}echo wp_json_encode($out);')
    before = t.c17.state(); planned = action(); shared = sources()
    t.c17.save('before-final', {'native':before,'action8793':planned,'shared_sources':shared})
    outcomes = {}
    for name, fn in [('b02-final',b02),('replacement-final',replacement),('deletion-final',deletion),('boundaries-final',boundaries)]:
        outcomes[name] = fn(name)
    outcomes['http-final'] = t.run('http-final')
    legacy = module('c17_legacy_faults', ROOT/'wp/tests/demo/c17-faults.py')
    outcomes['faults-final'] = legacy.run()
    settings = module('c17_legacy_settings', ROOT/'wp/tests/demo/c17-reglages.py')
    outcomes['reglages-final'] = settings.run('reglages-final')
    # Reuse B02 real HTTP without overwriting its historical production receipts.
    b02_http = module('c17_b02_http', ROOT/'wp/tests/demo/b02-http.py')
    b02_http.b02.PROOF = PROOF
    http_checks = b02_http.verify()
    t.c17.save('b02-http-final',{'checks':http_checks,'total':len(http_checks),'failures':[k for k,v in http_checks.items() if v is not True]})
    native = t.c17.profils.b00.wp('eval','require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";',check=False)
    assert not native['stderr']
    native = dict(json.loads(native['stdout']), exit=native['code'])
    t.c17.save('c09-native-final',native)
    after = t.c17.state(); after_action = action(); shared_after = sources()
    t.c17.save('after-final',{'native':after,'action8793':after_action,'shared_sources':shared_after})
    checks = {'native_exactement_preserve': before == after, 'action8793_pending101_exactement_preservee':planned == after_action and planned['status']=='pending' and json.loads(planned['args'])=={'subscription_id':101},
        'bootstrap_seed_theme_partages_preserves':shared==shared_after,
        'C09_382_sur_382':native['exit']==0 and native['total']==382 and len(native['checks'])==382 and not native['failures'] and all(x is True for x in native['checks'].values()),
        'gates_sans_echec':all(x==0 for x in outcomes.values()) and all(v is True for v in http_checks.values())}
    names = ['b02-final','replacement-final','deletion-final','boundaries-final','http-final','faults-final','reglages-final','b02-http-final']
    receipts = {}
    for name in names:
        r = json.loads((PROOF/(name+'.json')).read_text())
        assert r['total']==len(r['checks'])
        receipts[name] = {'total':r['total'],'failures':r['failures']}
        checks[name+'_tous_vrais'] = not r['failures'] and all(v is True for v in r['checks'].values())
    current_source = ROOT/'wp/plugins/imagine-site/Justificatifs.php'
    actual = t.c17.wp('echo wp_json_encode(hash_file("sha256",WP_PLUGIN_DIR."/imagine-site/Justificatifs.php"));')
    checks['Justificatifs_source_readback_exact'] = actual == hashlib.sha256(current_source.read_bytes()).hexdigest()
    cleanup = t.c17.wp('global $wpdb;echo wp_json_encode(["fixtures"=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->users} WHERE user_login LIKE \'c17-fictif-delete-%\'"),"files"=>array_map("basename",glob(Imagine\\Site\\PdfNumero::directory()."/c17-*.bin"))]);')
    state = t.c17.wp('$f=get_option("imagine_c09_fixture");echo wp_json_encode(["att"=>Imagine\\Site\\Justificatifs::etat($f["users"]["P-SOL-ATT"]),"ok"=>Imagine\\Site\\Justificatifs::etat($f["users"]["P-SOL-OK"])]);')
    checks['fixtures_nettoyees_un_fichier_C09_seul'] = cleanup['fixtures']==0 and cleanup['files']==['c17-'+state['att']['blob']+'.bin'] and state['ok']['decision']=='valide'
    source_paths = [current_source,ROOT/'wp/tests/demo/b02-runtime.php',Path(__file__),ROOT/'wp/tests/demo/c17-faults.py',ROOT/'wp/plugins/imagine-site/tests/JustificatifReglesTest.php'] + sorted((ROOT/'wp/plugins/imagine-site/tests/fixtures').glob('c17-fictif.*'))
    source_hashes = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    return save(label, {'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','status':'PRET_TECHNIQUE_ARBITRAGE_4H30_APPLIQUE' if all(checks.values()) else 'ECHEC',
        'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True], 'receipts':receipts,'sha256_Justificatifs_readback':actual,'source_sha256':source_hashes,'shared_sha256_before':shared,'shared_sha256_after':shared_after,
        'action8793_before':planned,'action8793_after':after_action,'final_documentary_state':state,'cleanup':cleanup,
        'RGPD':'arbitre A-FAIRE-2 4h30; dossier trois champs; date et operateur journal C10', 'C18_treated':False,'C21_treated':False})

def seal(label):
    from datetime import datetime, timezone
    import re
    result = json.loads((PROOF/'final-V2.json').read_text())
    assert not result['failures'] and all(result['checks'].values())
    for name,digest in result['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, 'Source drift: '+name
    receipts = {}
    for name,expected in result['receipts'].items():
        receipt = json.loads((PROOF/(name+'.json')).read_text())
        assert receipt['total'] == len(receipt['checks']) == expected['total'] and not receipt['failures'] and all(x is True for x in receipt['checks'].values())
        receipts[name] = expected
    for name in ['unit-rules','unit-root']:
        unit = json.loads((PROOF/(name+'.json')).read_text())
        assert unit['exit']==0 and unit['removed']
        counts = re.search(r'OK \((\d+) tests?, (\d+) assertions?\)',unit['stdout'])
        assert counts
        receipts[name] = {'tests':int(counts[1]),'assertions':int(counts[2]),'container_removed':True}
    text = (PROOF/'rejouer.log').read_text(encoding='utf-8-sig')
    markers = re.findall(r'^T01_RESULT (\{[^\r\n]+\})',text,re.M)
    assert len(markers)==1
    canonical = json.loads(markers[0]); assert canonical['pass']
    assert 'T01 IMAGE READY' in (PROOF/'preparer-image.log').read_text(encoding='utf-8-sig')
    readback = t.c17.wp('echo wp_json_encode(hash_file("sha256",WP_PLUGIN_DIR."/imagine-site/Justificatifs.php"));')
    assert readback == result['sha256_Justificatifs_readback']
    native = json.loads((PROOF/'c09-native-final.json').read_text())
    assert native['exit']==0 and native['total']==len(native['checks'])==382 and not native['failures']
    assert action() == result['action8793_after']
    remote = t.c17.wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(list(result['shared_sha256_after']))) + ',true) as $n){$out[$n]=hash_file("sha256",WP_CONTENT_DIR."/".$n);}echo wp_json_encode($out);')
    assert remote == result['shared_sha256_after']
    assert t.c17.state() == json.loads((PROOF/'after-final.json').read_text())['native']
    return save(label,{'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','status':'PRET_TECHNIQUE_ARBITRAGE_4H30_APPLIQUE','receipts':receipts,'canonical_T01':canonical,'native_C09':{'total':382,'failures':[]},
        'source_sha256':result['source_sha256'],'sha256_readback_Justificatifs':readback,'shared_sha256_successor_preserved':remote,'action8793_exactly_preserved':True,
        'RGPD_question5':'RESOLUE_CONSIGNE_4H30; trois champs et journal C10','failures':[]})

if __name__ == '__main__':
    t.c17.profils.guard('imagine-test-demo')
    mode = sys.argv[1]
    fn = {'b02': b02, 'replacement': replacement, 'deploy': deploy, 'deletion': deletion, 'boundaries': boundaries, 'all': all_gates, 'seal': seal}[mode]
    sys.exit(fn(sys.argv[2] if len(sys.argv)>2 else mode))
