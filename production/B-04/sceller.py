"""Seal/check actual B04 receipts and source hashes. No staging mutation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
PROOF=Path(__file__).resolve().parent
ROOT=PROOF.parents[1]
SOURCES=[
 'wp/plugins/imagine-site/Paywall.php','wp/plugins/imagine-site/Decouverte.php',
 'wp/plugins/imagine-site/README.md','wp/plugins/imagine-site/phpunit.b04.xml',
 'wp/plugins/imagine-site/tests/CatalogueTest.php','wp/plugins/imagine-site/tests/CatalogueStatusTest.php',
 'wp/plugins/imagine-site/tests/b04-adapter-fixture.php','wp/plugins/imagine-site/tests/b04-status-fixture.php',
 'wp/themes/imagine/inc/catalogue.php','wp/themes/imagine/single-imagine_numero.php',
 'wp/outils/demo/b04-preview.php','wp/outils/demo/b04-unit.py',
 'wp/tests/demo/b04-http.py','wp/tests/demo/b04-corrections.py','wp/tests/demo/b04-safety.py',
 'wp/tests/demo/b04-unit-bootstrap.php','wp/tests/demo/test_b04_http_contract.py',
]
RECEIPTS=['native-http-corrections-definitif.json','http-definitif.json','catalogue-definitif.json',
 'php-definitif.json','safety.json','queries-20.json','browser.json']
MANIFEST=PROOF/'verification-corrections-finale.json'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_receipts():
    newest=max((ROOT/p).stat().st_mtime for p in SOURCES)
    suites={}
    for name in RECEIPTS:
        p=PROOF/name
        d=json.loads(p.read_text(encoding='utf-8'))
        assert d['total']==len(d['checks']) and not d['failures'],name
        assert all(v is True for v in d['checks'].values()),name
        assert p.stat().st_mtime>=newest, 'Stale receipt '+name
        suites[name]={'total':d['total'],'failures':0}
    junit={}
    for label in ['root','c12','b04']:
        p=PROOF/('junit-'+label+'-definitif.xml')
        tree=ET.parse(p).getroot();cases=list(tree.iter('testcase'))
        assert not list(tree.iter('failure')) and not list(tree.iter('error')) and not list(tree.iter('skipped'))
        assert p.stat().st_mtime>=newest
        junit[label]={'tests':len(cases),'assertions':sum(int(c.get('assertions','0')) for c in cases)}
        if label=='b04':
            expected={'testDeliveredFunctionAloneMapsAllFourCodesAndBothDiscoveryReasons',
                'testOwnershipDoesNotBecomeAnotherPurchaseBeforeRelease',
                'testListingPredictsFirstReadWithoutOpeningOrConsuming',
                'testListingUsesDurationAndClosesInvalidVerificationDesignationAndFuture'}
            assert {c.get('name') for c in cases}==expected
    unit=json.loads((PROOF/'unit-definitif.json').read_text())
    assert unit['isolation_verified'] and unit['owned_container_removed'] and all(r['exit']==0 for r in unit['runs'])
    log=(PROOF/'python-contract-definitif.log').read_text()
    pytests=int(re.search(r'Ran (\d+) tests',log)[1]);assert log.rstrip().endswith('OK')
    lint=json.loads((PROOF/'phpcs-style-final.json').read_text());assert lint['totals']['errors']==0
    assert (PROOF/'phpcs-style-final.json').stat().st_mtime>=newest
    assert 'T01 IMAGE READY' in (PROOF/'preparer-image-corrections.log').read_text(errors='replace')
    return suites,junit,pytests

def main():
    suites,junit,pytests=validate_receipts()
    if '--check' in sys.argv:
        data=json.loads(MANIFEST.read_text())
        for key in ['sources_sha256','evidence_sha256','screenshots_sha256']:
            for path,expected in data[key].items():assert digest(ROOT/path)==expected,path
        assert data['native_controls']==sum(s['total'] for s in suites.values())
        print(json.dumps({'verified':True,'source_files':len(data['sources_sha256']),
            'native_controls':data['native_controls'],'phpunit_unique_tests':data['phpunit_unique_tests'],
            'python_tests':pytests},ensure_ascii=False))
        return
    sys.path.insert(0,str(ROOT/'wp/tests/demo'))
    spec=importlib.util.spec_from_file_location('b04_seal',ROOT/'wp/tests/demo/b04-corrections.py')
    c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    c.w.guard()
    expected={target:digest(ROOT/source) for target,source in c.FILES.items()}
    actual=c.w.readback(list(expected));assert actual==expected
    browser=json.loads((PROOF/'browser.json').read_text())
    screens=browser['screenshots'];assert len(screens)==len(set(screens))==16
    evidence=[*RECEIPTS,*['junit-'+s+'-definitif.xml' for s in ['root','c12','b04']],
        'unit-definitif.json','unit-definitif.log','python-contract-definitif.log',
        'phpcs-style-final.json','preparer-image-corrections.log','deploy-corrections-corrections-style.json',
        'style-whitespace-only.json','cleanup-corrections-style-lint.json']
    data={'scope':'imagine-test-demo','at':datetime.now(timezone.utc).isoformat(),
        'technical_instructions_completed':[1,2,3,4,5,6],
        'visual_instruction_7':'Statut kiosque conserve sans modification ; decision Ced attendue.',
        'suites':suites,'native_controls':sum(s['total'] for s in suites.values()),
        'phpunit':junit,'phpunit_unique_tests':sum(junit[s]['tests'] for s in ['root','c12']),
        'phpunit_unique_assertions':sum(junit[s]['assertions'] for s in ['root','c12']),
        'python_tests':pytests,'phpcs_errors':0,'native_source_readback_exact':True,
        'native_sources':actual,'sources_sha256':{p:digest(ROOT/p) for p in SOURCES},
        'evidence_sha256':{str((PROOF/p).relative_to(ROOT)).replace('\\','/'):digest(PROOF/p) for p in evidence},
        'screenshots_sha256':{p:digest(ROOT/p) for p in screens}}
    MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:data[k] for k in ['native_controls','phpunit_unique_tests','phpunit_unique_assertions','python_tests','phpcs_errors','native_source_readback_exact']},ensure_ascii=False))

if __name__=='__main__':main()
