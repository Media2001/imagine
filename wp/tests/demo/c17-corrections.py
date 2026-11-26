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
        status,_,_ = t.decision(abo, opened)
        checks['ancien_formulaire_referent_refuse_409'] = status == 409 and t.stored(uid) == current
        status,_,_ = t.upload(owner, t.form(owner), t.dummy_pdf('C17 nouveau fictif'))
        checks['nouveau_depot_repare'] = status == 200 and t.stored(uid)['exists'] and 'indisponible' not in t.stored(uid)['state']
        evidence = {'before':old,'after_failed_write':current,'old_form_status':status}
    finally:
        t.c17.reset()
        checks['etat_natif_preserve'] = before == t.c17.state()
        checks['action8793_exacte_pending101_preservee'] = action() == planned and planned['status'] == 'pending' and '101' in planned['args']
    return save(label, {'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True], 'evidence':evidence,'fault_injection':'process-local namespaced fopen returns false; real old file deletion and persistent WP option + HTTP stale form'})

if __name__ == '__main__':
    t.c17.profils.guard('imagine-test-demo')
    mode = sys.argv[1]
    fn = {'b02': b02, 'replacement': replacement, 'deploy': deploy}[mode]
    sys.exit(fn(sys.argv[2] if len(sys.argv)>2 else mode))
