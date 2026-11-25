"""Current C16 readback; --strict-global retains the known historical C09 failure."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c16


def run():
    c16.profils.guard('imagine-test-demo')
    p = c16.PROOF
    load = lambda name: json.loads((p / name).read_text(encoding='utf-8'))
    installation = load('installation.json')
    payload = {}
    for name, digest in installation['sha256_readback'].items():
        demo = name in ['c09-seed.php', 'c16-reset.php']
        source = c16.ROOT / ('wp/outils/demo' if demo else 'wp/plugins/imagine-site') / name
        target = ('imagine-demo-build/' if demo else 'plugins/imagine-site/') + name
        actual = c16.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR.' + json.dumps('/' + target) + '));')
        assert actual == digest == hashlib.sha256(source.read_bytes()).hexdigest(), 'Payload drift: ' + name
        payload[source.relative_to(c16.ROOT).as_posix()] = digest
    http, focused = load('http-gates.json'), load('unit-gates.json')
    assert http['total'] == len(http['checks']) and not http['failures'] and all(v is True for v in http['checks'].values())
    assert focused['exit'] == 0 and focused['removed']
    focused_xml = focused['stdout'].split('C16_JUNIT', 1)[1].strip()
    focused_tree = ET.fromstring(focused_xml)
    assert not list(focused_tree.iter('failure')) + list(focused_tree.iter('error')) + list(focused_tree.iter('skipped'))
    focused_cases = list(focused_tree.iter('testcase'))
    focused_counts = {'tests': len(focused_cases), 'assertions': sum(int(c.get('assertions', 0)) for c in focused_cases)}
    b04 = c16.ROOT / 'production/B-04'
    unit = json.loads((b04 / 'unit-portabilite-c16.json').read_text(encoding='utf-8'))
    assert unit['isolation_verified'] and unit['owned_container_removed'] and len(unit['runs']) == 3
    assert all(r['exit'] == 0 for r in unit['runs'])
    suites = {}
    for label in ['root', 'c12', 'b04']:
        tree = ET.parse(b04 / ('junit-' + label + '-portabilite-c16.xml')).getroot()
        assert not list(tree.iter('failure')) + list(tree.iter('error')) + list(tree.iter('skipped'))
        cases = list(tree.iter('testcase'))
        suites[label] = {'tests': len(cases), 'assertions': sum(int(c.get('assertions', 0)) for c in cases)}
        if label == 'b04':
            status = [c for c in cases if c.get('name') == 'testDeliveredFunctionAloneMapsAllFourCodesAndBothDiscoveryReasons']
            assert len(status) == 1 and int(status[0].get('assertions')) == 55
    log = (p / 'rejouer-t01-gates-final.log').read_text(encoding='utf-8')
    markers = re.findall(r'^T01_RESULT (\{[^\r\n]+\})', log, re.M)
    assert len(markers) == 1
    canonical = json.loads(markers[0])
    assert canonical['pass'] and canonical['failures'] == canonical['errors'] == canonical['skipped'] == 0
    assert 'T01 NETTOYAGE EN ECHEC' not in log and 'REJEU :' in log and log.rstrip().endswith('PASS')
    preparation = (p / 'preparer-image-gates.log').read_text(encoding='utf-8')
    assert 'T01 IMAGE READY' in preparation and 'T01 IMAGE PACKAGE : imagine-site' in preparation
    raw = c16.profils.b00.wp('eval', 'require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";', check=False)
    assert not raw['stderr']
    c09 = json.loads(raw['stdout'])
    c16.save('c09-non-regression-gates', c09)
    assert c09['total'] == len(c09['checks'])
    spec = importlib.util.spec_from_file_location('c16_gates_diagnostic', c16.ROOT / 'wp/outils/demo/c16-gates-diagnostic.py')
    diagnostic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(diagnostic)
    now = c16.wp(diagnostic.CODE)
    c16.save('gates-c09-final-readback', now)
    semantic = lambda d: {k: v for k, v in d.items() if k != 'at'}
    unchanged = semantic(load('gates-c09-diagnostic.json')) == semantic(load('gates-c09-after-http.json')) == semantic(now)
    historical = False
    if c09['failures'] == ['A-PAPIER:action_native_planifiee_ou_absente_selon_statut']:
        actions = [a for a in now['actions'] if a['id'] == 8103]
        assert len(actions) == 1
        action = actions[0]
        canceled = [l['date'] for l in action['logs'] if l['message'] == 'action canceled']
        historical = (unchanged and now['id'] == 101 and now['status'] == 'active'
            and now['manual'] is True and now['gateway'] == '' and now['scheduled'] is False
            and now['related_renewals'] == [] and now['next_payment'] == '2026-11-25 19:01:50'
            and action['status'] == 'canceled' and action['scheduled'] == now['next_payment']
            and canceled == ['2026-11-25 20:38:22']
            and datetime.fromisoformat(canceled[0]).replace(tzinfo=timezone.utc) < datetime.fromisoformat(installation['at']))
    assert not c09['failures'] or historical, 'Unclassified native C09 regression; C16 not ready'
    assert raw['code'] == (1 if c09['failures'] else 0)
    rest = c16.wp('$o=[];foreach(["shop_order","shop_subscription"] as $type){foreach(wc_get_orders(["type"=>$type,"limit"=>-1,"status"=>"any","meta_key"=>"_imagine_c16_fixture","meta_value"=>"1"]) as $v){$o[]=$v->get_id();}}echo wp_json_encode(["objects"=>$o,"users"=>get_users(["fields"=>"ID","meta_key"=>"_imagine_c16_fixture","meta_value"=>"1"])]);')
    assert rest == {'objects': [], 'users': []}
    evidence = ['installation.json', 'unit-gates.json', 'http-gates.json', 'reset.json',
        'rejouer-t01-gates-red.log', 'rejouer-t01-gates-final.log', 'preparer-image-gates.log',
        'gates-c09-diagnostic.json', 'gates-c09-after-http.json', 'gates-c09-policy.json', 'c09-non-regression-gates.json']
    result = {'at': datetime.now(timezone.utc).isoformat(),
        'status': 'PRET_TECHNIQUE_C16_RESERVE_C09_HISTORIQUE' if historical else 'GATES_TECHNIQUES_VERTS',
        'PRET_present': (p / 'PRET').exists(), 'payload_sha256_readback': payload,
        'c16_unit_exit': focused['exit'], 'c16_unit': focused_counts, 'plugin_suites': suites,
        'http_checks': http['total'], 'http_failures': http['failures'],
        'created_then_deleted': http['created_then_deleted'], 'preparation_verified': True,
        'canonical_T01': canonical, 'C09_checks': c09['total'], 'C09_failures': c09['failures'],
        'C09_native_exit': raw['code'], 'strict_global_exit': 2 if c09['failures'] else 0,
        'global_all_green': not c09['failures'], 'historical_C09_nonblocking_for_C16': historical,
        'A_PAPIER_unchanged_before_after_C16_http': unchanged,
        'historical_reason': 'Action 8103 canceled 2026-11-25 20:38:22 UTC, before C16 deployment; not naturally consumed. No rescheduling or subscription change executed.',
        'native_cleanup_readback': rest, 'blockers_C16': [],
        'evidence_sha256': {name: hashlib.sha256((p / name).read_bytes()).hexdigest() for name in evidence}}
    c16.save('final', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if '--strict-global' in sys.argv and c09['failures'] else 0


if __name__ == '__main__':
    sys.exit(run())
