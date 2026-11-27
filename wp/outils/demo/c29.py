"""C29: bounded local pure/native acceptance, unique fictitious demo."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'production/C-29'
OUT.mkdir(exist_ok=True)
BLOCK = "// C29 — projection en lecture seule, aucun connecteur.\nrequire_once __DIR__ . '/ContactBrevoRegles.php';\nrequire_once __DIR__ . '/ContactBrevo.php';\nContactBrevo::register();\n\n"
FILES = ['plugins/imagine-site/'+n for n in ['ContactBrevoRegles.php','ContactBrevo.php','imagine-site.php']]

def save(label, data):
    with (OUT/(label+'.json')).open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def docker(*args):
    return subprocess.run(['wsl.exe','-d','Ubuntu','--','docker',*args],capture_output=True,encoding='utf-8')

def pure(label):
    r = docker('run','--rm','--pull','never','--network','none','--read-only',
        '--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly',
        '--entrypoint','php','imagine-tests-t01:1','/repo/wp/tests/demo/c29-pure.php')
    save(label, {'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'sources':sources()})
    print(r.stdout,r.stderr)
    return r.returncode

def state():
    import c19
    data=c19.state()
    # Exact additional admin-bootstrap expiry refreshes witnessed in http-first-V2.
    # No business option or scheduler row is excluded.
    volatile=['_transient_timeout_novamira_update_info',
        '_transient_timeout_as_is_ensure_recurring_actions_scheduled',
        '_transient_timeout_woocommerce_admin_settings_payments_has_providers_with_incentive']
    for key in volatile:data['option_fingerprints'].pop(key,None)
    data['all_options_fingerprint']=hashlib.sha256(json.dumps(data['option_fingerprints'],sort_keys=True).encode()).hexdigest()
    data['additional_bootstrap_cache_expiries']=volatile
    return data

def native(label):
    import b11
    identity = b11.guard()
    import c19
    before = c19.state()
    source = (ROOT/'wp/tests/demo/c29-runtime.php').read_text(encoding='utf-8').split('<?php',1)[1]
    expected = (ROOT/'wp/tests/demo/c29-attendus.php').read_text(encoding='utf-8').split('<?php',1)[1]
    source = source.replace("require __DIR__ . '/c29-attendus.php'", 'eval('+b11.php(expected)+')')
    code = 'global $wpdb;if(wp_using_ext_object_cache()){throw new RuntimeException("Cache externe refuse");}foreach([$wpdb->posts,$wpdb->postmeta,$wpdb->options,$wpdb->usermeta] as $t){$s=$wpdb->get_row($wpdb->prepare("SHOW TABLE STATUS WHERE Name=%s",$t),ARRAY_A);if($s["Engine"]!=="InnoDB"){throw new RuntimeException("InnoDB requis");}}$wpdb->query("START TRANSACTION");try{eval('+b11.php(source)+');}finally{$wpdb->query("ROLLBACK");wp_cache_flush();}'
    r = b11.b10.b09.b08.c25.b06.profils.b00.wp('eval',code,check=False)
    after = c19.state()
    restored = after == before
    save(label, {'identity':identity,'native':r,'business_preserved':restored,'strict_before':before,'strict_after':after,'sources':sources()})
    if r['code']==0:
        data=json.loads(r['stdout']); print(json.dumps({'exit':0,'total':data['total'],'checks':data['checks'],'restored':restored},ensure_ascii=False))
    else: print(json.dumps(r,ensure_ascii=False))
    assert restored
    return r['code']

def deploy(label):
    import b11
    identity=b11.guard(); before=b11.state()
    old=b11.wp('$o=[];foreach('+b11.php(FILES)+' as $n){$p=WP_CONTENT_DIR."/".$n;$o[$n]=is_file($p)?hash_file("sha256",$p):null;}echo wp_json_encode($o);')
    raw=(ROOT/'wp'/FILES[-1]).read_bytes()
    assert raw.count(BLOCK.encode())==1
    allowed={hashlib.sha256(raw).hexdigest(),hashlib.sha256(raw.replace(BLOCK.encode(),b'',1)).hexdigest()}
    assert old[FILES[-1]] in allowed, 'Bootstrap divergent'
    for n in FILES:
        b11.upload(n,(ROOT/'wp'/n).read_bytes())
    import b06
    actual=b06.hashes(FILES)
    assert actual=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in FILES}
    assert before==b11.state()
    save(label,{'identity':identity,'before':old,'readback':actual,'business_preserved':True})
    print('C29 readback exact',len(actual))

def sources():
    paths=[ROOT/'wp'/n for n in FILES]
    paths += [ROOT/'wp/plugins/imagine-site'/n for n in ['Newsletters.php','NewslettersRegles.php','Personnalisation.php','PersonnalisationRegles.php','Cooperateurs.php','EnvoiRelations.php','TableauBordAdmin.php','SansEmail.php']]
    for pattern in ['wp/outils/demo/c29*.py','wp/tests/demo/c29*','wp/plugins/imagine-site/tests/ContactBrevoC29Test.php','wp/plugins/imagine-site/tests/fixtures/c29-cases.php']:
        paths += [p for p in ROOT.glob(pattern) if p.is_file()]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}

def seed(label):
    import b11
    identity=b11.guard(); before=state()
    f=b11.wp('echo wp_json_encode(get_option("imagine_c09_fixture"));')
    mapping={str(v):k for k,v in f['tariffs'].items()}
    old=b11.wp('echo wp_json_encode(get_option(Imagine\\Site\\ContactBrevo::TARIFS,null));')
    assert old in [None,mapping], 'Configuration existante differente : pas de remplacement'
    actual=b11.wp('update_option(Imagine\\Site\\ContactBrevo::TARIFS,'+b11.php(mapping)+',false);echo wp_json_encode(get_option(Imagine\\Site\\ContactBrevo::TARIFS));')
    assert actual==mapping
    after=state()
    for k in before:
        if k not in ['all_options_fingerprint','option_fingerprints']:assert before[k]==after[k],k
    delta={k for k in before['option_fingerprints'].keys()|after['option_fingerprints'].keys() if before['option_fingerprints'].get(k)!=after['option_fingerprints'].get(k)}
    assert delta<= {'imagine_brevo_tarifs'}
    save(label,{'identity':identity,'mapping':mapping,'exact_changed_option_names':sorted(delta),'profiles_roles_actions_unchanged':True,'idempotent':old==actual})
    print('Tarifs fictifs C09 configures et relus, aucune fiche stockee')

def gate(action,label):
    scripts={'image':'preparer-image.ps1','replay':'rejouer.ps1'}
    command=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'wp/tests'/scripts[action])]
    with (OUT/(label+'.log')).open('xb') as stream:
        r=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    save(label,{'command':command,'exit':r.returncode,'log':label+'.log'})
    print('\n'.join((OUT/(label+'.log')).read_text(encoding='utf-8',errors='replace').splitlines()[-18:]))
    return r.returncode

if __name__ == '__main__':
    if sys.argv[1]=='seed': seed(sys.argv[2]); raise SystemExit(0)
    if sys.argv[1] in ['image','replay']: raise SystemExit(gate(sys.argv[1],sys.argv[2]))
    if sys.argv[1]=='deploy': deploy(sys.argv[2]); raise SystemExit(0)
    if sys.argv[1]=='native': raise SystemExit(native(sys.argv[2]))
    if sys.argv[1]=='pure': raise SystemExit(pure(sys.argv[2]))
    if sys.argv[1]=='inspect':
        r=docker('run','--rm','--pull','never','--network','none','--read-only','--entrypoint','php','imagine-tests-t01:1','-r','echo getcwd(),PHP_EOL; foreach(["/opt","/opt/t01"] as $p){if(is_dir($p)){echo $p,":",implode(",",array_diff(scandir($p),[".",".."])),PHP_EOL;}}')
        print(r.stdout,r.stderr)
