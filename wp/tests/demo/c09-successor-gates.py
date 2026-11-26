"""Read-only C17/C18 successor gates after the authorized C09 calendar repair.

Historical receipts remain evidence of their own instant. Current probes use the
exact post-repair baseline and never grant an arbitrary baseline exception.
"""
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import importlib
import json
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
repair = importlib.import_module('c09-papier')
c18 = repair.c18
ROOT = c18.ROOT
baseline_contract = repair.baseline_contract


def repair_receipt():
    receipt = json.loads(repair.RECEIPT.read_text(encoding='utf-8'))
    repair.validate_receipt(receipt)
    return receipt


def historical_files(lot):
    return {p.relative_to(ROOT).as_posix(): repair.digest(p)
            for p in sorted((ROOT / 'production' / lot).rglob('*'))
            if p.is_file() and '-V2' not in p.name}


def run(lot):
    assert lot in ('C-17', 'C-18')
    c18.c17.profils.guard('imagine-test-demo')
    proof = ROOT / 'production' / lot
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    historical_before = historical_files(lot)
    old = json.loads((proof / 'final.json').read_text(encoding='utf-8'))
    receipt = repair_receipt()
    before = c18.state()
    current = before if lot == 'C-18' else {k:v for k,v in before.items() if k != 'native_fingerprints'}
    if lot == 'C-18':
        baseline = json.loads((proof / 'installation.json').read_text(encoding='utf-8'))['baseline']
    else:
        baseline = json.loads(sorted(proof.glob('installation-*.json'))[0].read_text(encoding='utf-8'))['before']
    bridge = baseline_contract(baseline, current, receipt)
    checks = {'authorized_baseline_exact': True}
    # Verify all previously pinned functional sources. Only these two gates have
    # changed; neither plugin nor theme code was modified for the repair.
    changed_gates = {'wp/tests/demo/c17-verifier.py', 'wp/tests/demo/c18-verifier.py'}
    sources_checked = {}
    for name, expected in old['source_sha256'].items():
        if name in changed_gates:
            continue
        actual = repair.digest(ROOT / name)
        if lot == 'C-17' and name == 'wp/plugins/imagine-site/imagine-site.php':
            c18_historical = json.loads((ROOT / 'production/C-18/final.json').read_text(encoding='utf-8'))
            assert actual == c18_historical['source_sha256'][name], 'C18 shared bootstrap successor drift'
        else:
            assert actual == expected, 'Functional source drift: ' + name
        sources_checked[name] = actual
    checks['historical_functional_sources_unchanged'] = True
    hashes = c18.readback() if lot == 'C-18' else c18.c17.readback()
    checks['deployed_source_readback_exact'] = True
    native = repair.native()
    assert native['exit'] == 0 and native['total'] == len(native['checks']) == 382
    assert not native['failures'] and all(v is True for v in native['checks'].values())
    checks['native_C09_382_sur_382'] = True
    runtime = None
    csvs = {}
    if lot == 'C-18':
        # No upload, code installation or fixture reset; execute deployed probe.
        source = ROOT / 'wp/tests/demo/c18-runtime.php'
        actual = c18.wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR."/imagine-demo-build/c18-runtime.php"));')
        assert actual == repair.digest(source)
        runtime = c18.wp('require WP_CONTENT_DIR."/imagine-demo-build/c18-runtime.php";')
        assert runtime['checks'] and all(v is True for v in runtime['checks'].values())
        checks['C18_runtime_natif_lecture_seule'] = True
        http = json.loads((proof / 'http-final.json').read_text(encoding='utf-8'))
        assert http['total'] == len(http['checks']) and http['failures'] == []
        for entry in http['exports']:
            path = proof / entry['csv']
            with path.open(encoding='utf-8', newline='') as stream:
                rows = list(csv.DictReader(stream))
            assert len(rows) == entry['rows']
            assert repair.digest(path) == old['CSV_reopened'][path.name]['sha256']
            csvs[path.name] = {'rows': len(rows), 'sha256': repair.digest(path)}
        assert len(csvs) == len(http['exports']) == 9
        checks['neuf_CSV_historiques_rouverts_non_reecrits'] = True
    after = c18.state()
    assert after == before == receipt['after'], 'Read-only gate changed native state'
    checks['native_before_after_exact'] = True
    assert historical_files(lot) == historical_before
    checks['historical_receipts_exactly_preserved'] = True
    result = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo',
        'status': 'VERIFIED_SUCCESSOR_C09_RESTAURE', 'lot': lot, 'read_only': True,
        'checks': checks, 'total': len(checks), 'failures': [], 'authorized_baseline_successor': bridge,
        'before': before, 'after': after, 'global_C09_green': True,
        'native_C09': native, 'native_C18_current': runtime,
        'deployed_sha256_readback': hashes, 'historical_functional_sources_sha256': sources_checked,
        'historical_receipts_sha256': historical_before,
        'historical_tests_not_replayed': old['receipts'], 'CSV_reopened': csvs,
        'current_gate_source_sha256': {n:repair.digest(ROOT/n) for n in changed_gates},
        'visual_approval': False, 'fixture_reset': False}
    path = proof / ('verification-successeur-' + stamp + '-V2.json')
    repair.save_new(path, result)
    assert historical_files(lot) == historical_before
    print(json.dumps({'lot':lot,'status':result['status'],'checks':len(checks),'C09':'382/382',
        'C18_native_checks':len(runtime['checks']) if runtime else None, 'CSV_reopened':len(csvs),
        'historical_receipts_preserved':True,'proof':path.relative_to(ROOT).as_posix()},ensure_ascii=False))
    return result
