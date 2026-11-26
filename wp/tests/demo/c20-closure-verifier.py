"""Read-only C20 acceptance for the explicit 26 November 07:30 reduced scope."""
from datetime import datetime, timezone
import importlib.util
import json
import re


def run(v, seal=False):
    root, proof = v.ROOT, v.PROOF
    read = lambda name: json.loads((proof / name).read_text(encoding='utf-8'))
    contracts = v.local_contracts()
    preserved = read('closure-preservation-V2.json')
    for name, expected in preserved.items():
        # The parent's orchestration lock is only an end-of-work witness, never a replay gate.
        if name == '.hermes-2.lock':
            continue
        assert v.digest(root / name) == expected, 'Preserved artifact changed: ' + name
    native = read('closure-0730-native-green-second-V2.json')
    assert native['checks'] and all(value is True for value in native['checks'].values()) and not native['failures']
    assert native['checks']['pending_cancel_paid_term_before_cutoff_excludes_only_this_subscription']
    assert native['fresh_profiles_actions_exact'] and native['effects'] == []
    assert not native['four']['result']['supported'] and native['four']['result']['C05_block_end'] is None
    assert native['four']['result']['before'] == native['four']['result']['after']
    assert not native['carte']['result']['resumption']['can_resume']
    assert native['carte']['result']['resumption']['products_unavailable']
    assert read('native-final-blocked-second-V2.json')['failures'] == ['pending_cancel_shipping_unchanged']
    ui = read('closure-0730-ui-second-V2.json')
    assert ui['total'] == len(ui['checks']) == 18 and not ui['failures'] and all(ui['checks'].values())
    assert ui['profiles_actions_unchanged']
    reg = read('closure-0730-regressions-second-V2.json')
    for name, total in [('C08', 30), ('C13', 24)]:
        value = reg['native'][name]
        assert value['total'] == len(value['checks']) == total and not value['failures']
        assert all(value['checks'].values()) and value['all_tables_rollback_exact']
    assert reg['C09']['total'] == len(reg['C09']['checks']) == 382 and not reg['C09']['failures']
    assert all(reg['C09']['checks'].values()) and reg['fresh_profiles_actions_exact']
    # The latest canonical suite is C21's already-executed suite; no test package added by this closure.
    log = (root / 'production/C-21/rejouer-final.log').read_text(encoding='utf-8-sig')
    markers = re.findall(r'^T01_RESULT (\{[^\r\n]+\})', log, re.M)
    assert len(markers) == 1
    canonical = json.loads(markers[0])
    assert canonical['pass'] and not any(canonical[k] for k in ('failures', 'errors', 'skipped'))
    # Recheck C21's own exact contracts, installed successor bytes and absent disposable accounts.
    spec = importlib.util.spec_from_file_location('c21_closure_readback', root / 'wp/tests/demo/c21-verifier.py')
    c21 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c21)
    c21.run()
    v.c20.c20.profils.guard('imagine-test-demo')
    current = v.c20.snapshot()
    assert current['profiles'] == read('adapter-red-before-second-V2.json')['profiles']
    assert current['profiles'] == read('closure-0730-native-green-after-second-V2.json')['profiles']
    action = [a for a in current['profiles']['A-PAPIER']['actions'] if str(a['action_id']) == '8793']
    assert len(action) == 1 and current['profiles']['A-PAPIER']['id'] == 101
    assert action[0]['status'] == 'pending' and action[0]['scheduled_date_gmt'] == '2026-11-26 02:13:28'
    names = list(v.BLOCKS) + ['wp/plugins/imagine-site/Renouvellement.php',
        'wp/plugins/imagine-site/RenouvellementRegles.php', 'wp/plugins/imagine-site/EnvoiNatif.php']
    remote = v.c20.wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps([n.removeprefix('wp/') for n in names])) + ',true) as $n){$out["wp/".$n]=hash_file("sha256",WP_CONTENT_DIR."/".$n);}echo wp_json_encode($out);')
    assert remote == {n: v.digest(root / n) for n in names}
    probe_path = 'imagine-demo-build/c20-second-native.php'
    probe_hash = v.c20.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR.' + json.dumps('/' + probe_path) + '));')
    assert probe_hash == native['source_sha256'] == v.digest(root / 'wp/tests/demo/c20-second-native.php')
    assert (proof / 'PRET').is_file()
    pret = (proof / 'PRET').read_text(encoding='utf-8')
    assert 'PERIMETRE_REDUIT_0730' in pret and 'imagine_non_renouvellement_confirme' in pret
    owned = names + ['wp/outils/demo/c20-second.py', 'wp/tests/demo/c20-second-native.php',
        'wp/tests/demo/c20-verifier.py', 'wp/tests/demo/c20-closure-verifier.py',
        'production/C-20/A-VOIR.md', 'production/C-20/natif.md', 'production/C-20/PRET',
        'files/rapports/2026-11-26-07h54-V2.md']
    receipts = ['closure-preservation-V2.json', 'closure-0730-native-green-second-V2.json',
        'closure-0730-native-green-before-second-V2.json', 'closure-0730-native-green-after-second-V2.json',
        'closure-0730-ui-second-V2.json', 'closure-0730-regressions-second-V2.json']
    data = {'status': 'PRET_TECHNIQUE_C20_PERIMETRE_REDUIT_0730', 'scope': 'imagine-test-demo',
        'source_sha256': {n: v.digest(root / n) for n in owned},
        'receipt_sha256': {n: v.digest(proof / n) for n in receipts},
        'deployed_source_sha256': remote, 'successor_contracts': contracts,
        'native_checks': len(native['checks']), 'ui_checks': ui['total'],
        'C08': 30, 'C13': 24, 'C09': 382, 'canonical': canonical,
        'profiles_actions_exact': True, 'action_8793_exact': True,
        'historical_red_preserved': True, 'functional_code_unchanged': True,
        'C21_preserved_and_verified': True, 'C05_margin_unchanged_absent': True,
        'deferred': ['nonrenew_button', 'confirmation', 'imagine_non_renouvellement_confirme', 'four_native_end_proof'],
        'visual_approval': False, 'real_deployment_authorized': False, 'PRET': True}
    target = proof / 'final-closure-0730-successor-V2.json'
    if seal:
        assert not target.exists(), 'Never overwrite a historical seal'
        target.write_text(json.dumps(dict(data, at=datetime.now(timezone.utc).isoformat()), ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        previous = json.loads(target.read_text(encoding='utf-8')); previous.pop('at')
        assert previous == data, 'Closure seal differs'
    print(json.dumps({k: value for k, value in data.items() if k not in ('source_sha256', 'receipt_sha256', 'deployed_source_sha256', 'successor_contracts')}, ensure_ascii=False))
    return data
