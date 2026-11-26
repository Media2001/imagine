"""C21: scoped native privacy adapter installation and test entrypoints."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
sys.dont_write_bytecode = True
import c19
ROOT = c19.ROOT
PROOF = ROOT / 'production/C-21'
wp = c19.wp
BLOCK = "require_once __DIR__ . '/ConfidentialiteRegles.php';\nrequire_once __DIR__ . '/Confidentialite.php';\nConfidentialite::register();\n\n"

def save(label, data):
    if not label.replace('-', '').isalnum():
        raise ValueError('Invalid receipt label')
    PROOF.mkdir(parents=True, exist_ok=True)
    path = PROOF / (label + '.json')
    if path.exists():
        raise RuntimeError('Receipt exists: ' + str(path))
    path.write_text(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(), scope='imagine-test-demo', **data), ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'receipt': path.name, 'checks': data.get('checks'), 'failures': data.get('failures')}))
    return data

def targets():
    return { 'plugins/imagine-site/' + n: ROOT / 'wp/plugins/imagine-site' / n for n in ('ConfidentialiteRegles.php', 'Confidentialite.php', 'EnvoiNatif.php', 'imagine-site.php') }

def hashes(names):
    return wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(names)) + ',true) as $n){$p=WP_CONTENT_DIR."/".$n;$out[$n]=is_file($p)?hash_file("sha256",$p):null;}echo wp_json_encode($out);')

def fixture(phase):
    path = ROOT / 'wp/tests/demo/c21-runtime.php'
    name = 'imagine-demo-build/c21-runtime.php'
    c19.c18.c17.profils.b00.upload(name, path.read_bytes())
    assert hashes([name])[name] == hashlib.sha256(path.read_bytes()).hexdigest()
    return wp('$phase=' + json.dumps(phase) + ';require WP_CONTENT_DIR."/' + name + '";')

def baseline(label):
    return save(label, {'native': c19.c18.state(), 'source_before': hashes(list(targets())), 'registration': fixture('registration')})

def deploy(label):
    before = json.loads((PROOF / ('baseline-observer.json' if (PROOF / 'baseline-observer.json').exists() else 'baseline.json')).read_text(encoding='utf-8'))
    actual = hashes(list(targets()))
    for name, p in targets().items():
        allowed = {before['source_before'][name], hashlib.sha256(p.read_bytes()).hexdigest()}
        for receipt in PROOF.glob('installation*.json'):
            prior = json.loads(receipt.read_text(encoding='utf-8'))
            if prior.get('scope') != 'imagine-test-demo':
                raise RuntimeError('Foreign receipt')
            allowed.add(prior.get('source_readback', {}).get(name))
        if name in ('plugins/imagine-site/Confidentialite.php', 'plugins/imagine-site/imagine-site.php'):
            successor = json.loads((ROOT / 'production/C-22/installation-final-V2.json').read_text(encoding='utf-8'))
            assert successor['scope'] == 'imagine-test-demo' and successor['native_preserved'] is True
            allowed.add(successor['source_readback'][name])
        if actual[name] not in allowed:
            raise RuntimeError('Source drift: ' + name)
    native = c19.c18.state()
    for name, path in targets().items():
        c19.c18.c17.profils.b00.upload(name, path.read_bytes())
    readback = hashes(list(targets()))
    assert readback == {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in targets().items()}
    assert native == c19.c18.state(), 'State drift during code-only install'
    return save(label, {'source_readback': readback, 'native_preserved': True, 'registration': fixture('registration')})

def security(label):
    before = c19.c18.state()
    source = ROOT / 'wp/tests/demo/c21-security.php'
    name = 'imagine-demo-build/c21-security.php'
    c19.c18.c17.profils.b00.upload(name, source.read_bytes())
    assert hashes([name])[name] == hashlib.sha256(source.read_bytes()).hexdigest()
    result = wp('require WP_CONTENT_DIR."/imagine-demo-build/c21-security.php";')
    result['checks'].update(wp(r'''echo wp_json_encode([
        'mail_coupe'=>apply_filters('pre_wp_mail',null,['to'=>['fictif@example.org']])===false,
        'HTTP_externe_coupe'=>is_wp_error(apply_filters('pre_http_request',false,[],'https://example.org/')),
        'passerelles_coupees'=>apply_filters('woocommerce_available_payment_gateways',[])===[],
        'fixture_absente'=>get_option('imagine_c21_fixture',null)===null && !get_user_by('login','imagine-c21-fictif')
    ]);'''))
    result['checks']['native_inchange'] = before == c19.c18.state()
    result['total'] = len(result['checks'])
    result['failures'] = [k for k,v in result['checks'].items() if v is not True]
    save(label, result)
    assert not result['failures']
    return result


def failures(label):
    before = c19.c18.state()
    name = 'imagine-demo-build/c21-failures.php'
    source = ROOT / 'wp/tests/demo/c21-failures.php'
    c19.c18.c17.profils.b00.upload(name, source.read_bytes())
    assert hashes([name])[name] == hashlib.sha256(source.read_bytes()).hexdigest()
    result = wp('require WP_CONTENT_DIR."/imagine-demo-build/c21-failures.php";')
    result['checks']['native_inchange'] = before == c19.c18.state()
    result['total'] = len(result['checks'])
    result['failures'] = [k for k,v in result['checks'].items() if v is not True]
    save(label, result)
    assert not result['failures']
    return result


def schedule_business():
    return wp(r'''global $wpdb;$a=$wpdb->prefix.'actionscheduler_actions';$l=$wpdb->prefix.'actionscheduler_logs';
$actions=$wpdb->get_results("SELECT * FROM $a WHERE hook<>'wcs_report_update_cache' ORDER BY action_id",ARRAY_A);
$logs=$wpdb->get_results("SELECT l.* FROM $l l INNER JOIN $a a ON a.action_id=l.action_id WHERE a.hook<>'wcs_report_update_cache' ORDER BY l.log_id",ARRAY_A);
echo wp_json_encode(['sha256'=>hash('sha256',serialize([$actions,$logs])),
'action8793'=>$wpdb->get_row("SELECT action_id,hook,status,args,scheduled_date_gmt FROM $a WHERE action_id=8793",ARRAY_A)]);''')


def regressions(label):
    paths = ['c20-regressions.php', 'c20-native.php', 'c08-runtime.php', 'c13-runtime.php', 'c09-runtime.php']
    names = ['imagine-demo-build/' + p for p in paths]
    actual = hashes(names)
    assert actual == {n: hashlib.sha256((ROOT / 'wp/tests/demo' / p).read_bytes()).hexdigest() for n, p in zip(names, paths)}
    before = c19.c18.state()
    scheduled_before = schedule_business()
    native = wp('require WP_CONTENT_DIR."/imagine-demo-build/c20-regressions.php";')
    c09 = wp('require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";')
    after = c19.c18.state()
    scheduled_after = schedule_business()
    import copy
    a, b = copy.deepcopy(before), copy.deepcopy(after)
    for state in (a, b):
        for key in ('actionscheduler_actions', 'actionscheduler_logs'):
            state['native_fingerprints'].pop(key, None)
    assert a == b and scheduled_before == scheduled_after, 'Native business readback drift'
    assert all(not r['failures'] and r['all_tables_rollback_exact'] and r['total'] == len(r['checks']) for r in native.values())
    assert c09['total'] == len(c09['checks']) == 382 and not c09['failures'] and all(c09['checks'].values())
    return save(label, {'native': native, 'C09': c09, 'state_preserved_except_native_report_cache_jobs': True,
        'schedule_business': scheduled_after, 'sources_readback': actual})


if __name__ == '__main__':
    c19.c18.c17.profils.guard('imagine-test-demo')
    mode = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else mode
    if mode in ('baseline', 'deploy', 'regressions', 'security', 'failures'):
        globals()[mode](label)
    else:
        save(label, {'phase': mode, 'result': fixture(mode)})
