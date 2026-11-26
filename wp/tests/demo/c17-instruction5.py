"""C17 instruction 5 only: dated successor, native hooks and HTTP readback."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import c17_http as t
spec = importlib.util.spec_from_file_location('c17_corrections_reuse', Path(__file__).with_name('c17-corrections.py'))
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
ROOT = t.c17.ROOT
PROOF = ROOT / 'production/C-17/instruction5-20261126'
PROOF.mkdir(parents=True, exist_ok=True)
c.PROOF = t.c17.PROOF = PROOF
OWNED = ['plugins/imagine-site/JustificatifRegles.php', 'plugins/imagine-site/Justificatifs.php']
SHARED = ['plugins/imagine-site/imagine-site.php', 'imagine-demo-build/c09-seed.php',
          'imagine-demo-build/c17-profils.php', 'themes/imagine/parts/mon-compte.php',
          'plugins/imagine-site/ExtractionsAdmin.php', 'plugins/imagine-site/ExtractionsRegles.php',
          'plugins/imagine-pilotage/src/Administration/Reglages.php']

def save(label, data):
    target = PROOF / (label + '.json')
    if target.exists():
        raise RuntimeError('Immutable evidence already exists: ' + str(target))
    data = dict(at=datetime.now(timezone.utc).isoformat(), scope='imagine-test-demo', **data)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'receipt': target.name, 'status': data.get('status'), 'failures': data.get('failures', [])}))
    return data

def hashes(names):
    return t.c17.wp('$out=[];foreach(json_decode('+json.dumps(json.dumps(names))+',true) as $n){$p=WP_CONTENT_DIR."/".$n;if(!is_file($p))throw new RuntimeException("Missing source: ".$n);$out[$n]=hash_file("sha256",$p);}echo wp_json_encode($out);')

def local_owned():
    return {n: hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in OWNED}

def baseline(label):
    return save(label, {'owned_before': hashes(OWNED), 'shared': hashes(SHARED),
        'native': t.c17.state(), 'action8793': c.action(), 'failures': []})

def deploy(label):
    before = json.loads((PROOF/'baseline.json').read_text(encoding='utf-8'))
    actual = hashes(OWNED); wanted = local_owned()
    assert all(actual[n] in {before['owned_before'][n], wanted[n]} for n in OWNED), 'Owned source drift'
    assert hashes(SHARED) == before['shared'], 'Shared source drift'
    native = t.c17.state(); action = c.action()
    for name in OWNED:
        t.c17.profils.b00.upload(name, (ROOT/'wp'/name).read_bytes())
    assert hashes(OWNED) == wanted
    # Migrate only C17's two synthetic profiles; preserve original decision actor/time in C10.
    migration = t.c17.wp(r'''$f=get_option('imagine_c09_fixture');$out=[];
foreach(['P-SOL-ATT','P-SOL-OK'] as $code){$id=(int)$f['users'][$code];
if(get_user_meta($id,'_imagine_c09_fixture',true)!==$code)throw new RuntimeException('Foreign profile');
Imagine\Site\Justificatifs::verrou($id,static function()use($id,&$out,$code){
$s=Imagine\Site\Justificatifs::etat($id);if(in_array($s['decision']??'', ['valide','refuse'],true)){
$new=['categorie'=>$s['categorie'],'decision'=>$s['decision'],'fin'=>$s['fin']];
update_option(Imagine\Site\Justificatifs::PREFIX.$id,$new,false);
if(Imagine\Site\Justificatifs::etat($id)!==$new)throw new RuntimeException('Migration failed');}
$out[$code]=Imagine\Site\Justificatifs::etat($id);});}echo wp_json_encode($out);''')
    assert set(migration['P-SOL-OK']) == {'categorie','decision','fin'}
    assert native == t.c17.state() and action == c.action()
    return save(label, {'owned_readback': hashes(OWNED), 'shared_preserved': hashes(SHARED),
        'native_preserved': True, 'action8793_preserved': True, 'profiles_readback': migration, 'failures': []})

def run(label):
    checks = {}; before = t.c17.state(); action = c.action(); shared = hashes(SHARED)
    # Reuse real nominal route; only its final-state/audit contract changes.
    checks['HTTP'] = t.run(label+'-http') == 0
    checks['B02_native'] = c.b02(label+'-b02') == 0
    reset = t.c17.reset()
    checks['reset_valide_exactement_trois_champs'] = set(reset['P-SOL-OK']) == {'categorie','decision','fin'}
    checks['native_exact'] = before == t.c17.state()
    checks['action8793_exact_pending101'] = action == c.action() and action['status']=='pending' and json.loads(action['args'])=={'subscription_id':101}
    checks['shared_exact'] = shared == hashes(SHARED)
    r = t.c17.profils.b00.wp('eval','require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";',check=False)
    assert not r['stderr']
    native = dict(json.loads(r['stdout']), exit=r['code'])
    t.c17.save(label+'-c09', native)
    checks['C09_382_sur_382'] = native['exit']==0 and native['total']==len(native['checks'])==382 and not native['failures'] and all(v is True for v in native['checks'].values())
    readback = hashes(OWNED)
    checks['owned_readback'] = readback == local_owned()
    old_profile = json.loads((PROOF/'red-complet.json').read_text(encoding='utf-8'))['reset_readback']['P-SOL-OK']
    uid_ok = t.c17.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]["P-SOL-OK"]);')
    checks['ancienne_decision_date_operateur_transferes_sans_reinventer'] = any(
        row['quand_utc']==old_profile['date_decision'] and row['qui_login']==old_profile['operateur']
        and row['apres']=={k:old_profile[k] for k in ['categorie','decision','fin']}
        for row in t.audit(uid_ok))
    source_paths = [ROOT/'wp'/n for n in OWNED] + [Path(__file__), ROOT/'wp/tests/demo/c17_http.py', ROOT/'wp/tests/demo/c17-corrections.py', ROOT/'wp/outils/demo/c17.py', ROOT/'wp/outils/demo/c17-unit.py', ROOT/'wp/plugins/imagine-site/tests/JustificatifReglesTest.php']
    final = save(label, {'status':'PRET_INSTRUCTION5' if all(checks.values()) else 'ECHEC', 'checks':checks,
        'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],
        'owned_readback':readback, 'shared':shared, 'native_after':t.c17.state(), 'action8793':c.action(),
        'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
        'reset_readback':reset, 'scope_excludes':['C19','C20','C21'], 'historical_receipts_untouched':True})
    return int(bool(final['failures']))

def journal_failure(label):
    import base64
    before = t.c17.state(); planned = c.action()
    uid = t.c17.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]["P-SOL-ATT"]);')
    source = t.stored(uid); accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    abo=t.h.login(accounts['E-ABO']);owner=t.h.login(accounts['P-SOL-ATT']);opened=t.form(abo,uid)
    injection = r'namespace Imagine\Site; function add_option($key,$value,$deprecated="",$autoload=null){if(str_starts_with($key,\Imagine\Pilotage\Administration\Reglages::JOURNAL))return false;return \add_option($key,$value,$deprecated,$autoload);}'
    checks={}
    try:
        refused=t.c17.wp('eval(base64_decode('+json.dumps(base64.b64encode(injection.encode()).decode())+'));$id='+str(uid)+';$refused=false;'
            'try{Imagine\\Site\\Justificatifs::verrou($id,static function()use($id){$s=Imagine\\Site\\Justificatifs::etat($id);'
            '$new=Imagine\\Site\\JustificatifRegles::decider($s,"valide","2027-12-31","e-abo",gmdate("Y-m-d\\TH:i:s\\Z"));'
            'Imagine\\Site\\Justificatifs::supprimerFichier($s);update_option(Imagine\\Site\\Justificatifs::PREFIX.$id,$new,false);});}'
            'catch(Throwable $e){$refused=str_contains($e->getMessage(),"Journal indisponible");}echo wp_json_encode($refused);')
        current=t.stored(uid)
        checks['journal_indisponible_refus_explicite']=refused
        checks['option_restauree_pas_de_fausse_decision']=current['state']==source['state'] and t.absent(source['path'])
        checks['compte_indisponible_sans_lien_mort']='Document indisponible' in t.form(owner) and 'imagine_justificatif=' not in t.form(owner)
        checks['ancien_formulaire_HTTP_refuse']=t.decision(abo,opened)[0]==409 and t.stored(uid)==current
    finally:
        reset=t.c17.reset()
        checks['reset_deux_profils']=reset['P-SOL-ATT']['decision']=='en_attente' and set(reset['P-SOL-OK'])=={'categorie','decision','fin'}
        checks['native_exact']=before==t.c17.state() and planned==c.action()
    result=save(label, {'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],
        'injection':'process-local namespaced add_option; real C10 hook, WP option rollback, disk deletion and stale HTTP form'})
    return int(bool(result['failures']))

def seal(label):
    result = json.loads((PROOF/'green-final.json').read_text(encoding='utf-8'))
    assert not result['failures'] and all(result['checks'].values())
    for p,h in result['source_sha256'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h, p
    assert hashes(OWNED)==result['owned_readback'] and hashes(SHARED)==result['shared']
    assert t.c17.state()==result['native_after'] and c.action()==result['action8793']
    receipts = {}
    for name in ['green-final-http','green-final-b02','green-final-c09']:
        r=json.loads((PROOF/(name+'.json')).read_text(encoding='utf-8'))
        assert r['total']==len(r['checks']) and not r['failures'] and all(v is True for v in r['checks'].values())
        receipts[name]={'checks':r['total'],'failures':[]}
    r=json.loads((PROOF/'journal-failure.json').read_text(encoding='utf-8'))
    assert r['total']==len(r['checks']) and not r['failures'] and all(v is True for v in r['checks'].values())
    receipts['journal-failure']={'checks':r['total'],'failures':[]}
    for name in ['unit-green','unit-root']:
        r=json.loads((PROOF/(name+'.json')).read_text(encoding='utf-8'))
        assert r['exit']==0 and r['removed']
        m=re.search(r'OK \((\d+) tests?, (\d+) assertions?\)',r['stdout']);assert m
        receipts[name]={'tests':int(m[1]),'assertions':int(m[2]),'removed':True}
    text=(PROOF/'rejouer.log').read_text(encoding='utf-8-sig')
    markers=re.findall(r'^T01_RESULT (\{[^\r\n]+\})',text,re.M);assert len(markers)==1
    canonical=json.loads(markers[0]);assert canonical['pass']
    assert 'T01 IMAGE READY' in (PROOF/'preparer-image.log').read_text(encoding='utf-8-sig')
    return save(label, {'status':'PRET_C17_INSTRUCTIONS_1_A_5','failures':[], 'receipts':receipts,
        'canonical_T01':canonical,'source_sha256':result['source_sha256'],'owned_readback':result['owned_readback'],
        'shared_contract_preserved':result['shared'],'native_exact':True,'action8793_exact':result['action8793'],
        'arbitrage':'A-FAIRE-2 26/11/2026 4h30 consigne 0; trois champs dossier, audit C10',
        'visual_approval':False,'historical_proofs_rewritten':False})

if __name__=='__main__':
    t.c17.profils.guard('imagine-test-demo')
    mode=sys.argv[1];label=sys.argv[2] if len(sys.argv)>2 else mode
    outcome={'baseline':baseline,'deploy':deploy,'run':run,'journal-failure':journal_failure,'seal':seal}[mode](label)
    sys.exit(outcome if isinstance(outcome,int) else 0)
