"""Seal only B04's portable test-path delta, retaining original native proofs."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
sys.dont_write_bytecode = True
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
MANIFEST = P / 'verification-portabilite-c16.json'
FIXTURE = 'wp/plugins/imagine-site/tests/b04-status-fixture.php'
README = 'wp/plugins/imagine-site/README.md'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if '--check' in sys.argv:
        data = json.loads(MANIFEST.read_text(encoding='utf-8'))
        for kind in ['sources_sha256', 'evidence_sha256']:
            for path, expected in data[kind].items():
                assert digest(ROOT / path) == expected, path
        print(json.dumps({'verified': True, 'scope': data['scope'], 'phpunit': data['phpunit'],
            'canonical_T01': data['canonical_T01'], 'instructions': data['technical_instructions_completed']}))
        return
    oldpath = P / 'verification-corrections-finale.json'
    old = json.loads(oldpath.read_text(encoding='utf-8'))
    # No backdating or refresh of the accepted native/visual matrices.
    for group in ['evidence_sha256', 'screenshots_sha256']:
        for path, expected in old[group].items():
            assert digest(ROOT / path) == expected, path
    sources = {}
    for path, expected in old['sources_sha256'].items():
        actual = digest(ROOT / path)
        if path not in [FIXTURE, README]:
            assert actual == expected, 'Unexpected B04 code drift: ' + path
        sources[path] = actual
    sources['production/B-04/sceller-portabilite.py'] = digest(Path(__file__))
    unit = json.loads((P / 'unit-portabilite-c16.json').read_text(encoding='utf-8'))
    assert unit['isolation_verified'] and unit['owned_container_removed'] and len(unit['runs']) == 3
    assert all(r['exit'] == 0 for r in unit['runs'])
    suites = {}
    evidence = [oldpath, P / 'unit-portabilite-c16.json', P / 'unit-portabilite-c16.log']
    for label in ['root', 'c12', 'b04']:
        path = P / ('junit-' + label + '-portabilite-c16.xml')
        tree = ET.parse(path).getroot()
        assert not list(tree.iter('error')) + list(tree.iter('failure')) + list(tree.iter('skipped'))
        cases = list(tree.iter('testcase'))
        suites[label] = {'tests': len(cases), 'assertions': sum(int(c.get('assertions', 0)) for c in cases)}
        if label == 'b04':
            assert suites[label] == old['phpunit']['b04']
            selected = [c for c in cases if c.get('name') == 'testDeliveredFunctionAloneMapsAllFourCodesAndBothDiscoveryReasons']
            assert len(selected) == 1 and int(selected[0].get('assertions')) == 55
        evidence += [path, P / ('phpunit-' + label + '-portabilite-c16.log')]
    c16 = ROOT / 'production/C-16'
    canonical_log = c16 / 'rejouer-t01-gates-final.log'
    markers = re.findall(r'^T01_RESULT (\{[^\r\n]+\})', canonical_log.read_text(encoding='utf-8'), re.M)
    assert len(markers) == 1
    canonical = json.loads(markers[0])
    assert canonical['pass'] and not any(canonical[k] for k in ['failures', 'errors', 'skipped'])
    prep = c16 / 'preparer-image-gates.log'
    assert 'T01 IMAGE READY' in prep.read_text(encoding='utf-8')
    evidence += [canonical_log, prep, c16 / 'rejouer-t01-gates-red.log']
    sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
    import c16 as transport
    transport.profils.guard('imagine-test-demo')
    names = list(old['native_sources'])
    native = transport.wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(names)) + ',true) as $name){$out[$name]=hash_file("sha256",WP_CONTENT_DIR."/".$name);}echo wp_json_encode($out);')
    assert native == old['native_sources'], 'Native B04 runtime drift'
    result = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'B04 test path portability only',
        'technical_instructions_completed': [1, 2, 3, 4, 5, 6],
        'visual_instruction_7': old['visual_instruction_7'],
        'change': FIXTURE, 'before_sha256': old['sources_sha256'][FIXTURE],
        'after_sha256': sources[FIXTURE], 'assertions_not_skipped_or_replaced': True,
        'readme_drift_already_due_to_C16_documentation': sources[README] != old['sources_sha256'][README],
        'native_sources_readback': native, 'native_matrices_replayed': False,
        'original_native_receipts_and_screenshots_hashes_verified': True,
        'phpunit': suites, 'canonical_T01': canonical,
        'sources_sha256': sources,
        'evidence_sha256': {path.relative_to(ROOT).as_posix(): digest(path) for path in evidence}}
    MANIFEST.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'verified': True, 'phpunit': suites, 'canonical_T01': canonical,
        'native_runtime_unchanged': True, 'manifest_sha256': digest(MANIFEST)}))


if __name__ == '__main__':
    main()
