"""Final bounded evidence audit; no Git or existing-site inspection."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]

def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

php = []
for lot in ['C-03', 'C-04']:
    out = ROOT / 'production' / lot / 'tests-21nov'
    receipt = json.loads((out / 'final.json').read_text())
    assert all(receipt[k] == 0 for k in ['exit_code', 'psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code'])
    plugin = ROOT / 'wp/plugins' / ('imagine-connecteur' if lot == 'C-04' else 'imagine-pilotage')
    for path, expected in receipt['source_sha256'].items():
        assert digest(plugin / path) == expected, (lot, path)
    root = ET.parse(out / 'final.xml').getroot()
    assert not any(list(root.iter(tag)) for tag in ['failure', 'error', 'skipped'])
    cases = list(root.iter('testcase'))
    php.append({'lot': lot, 'tests': len(cases), 'assertions': sum(int(c.get('assertions',0)) for c in cases)})
    assert read(f'production/{lot}/tests-21nov/cleanup.json')['owned_runner_removed']
assert read('files/rapports/2026-11-21-preuves-acquises.json')['status'] == 'PASS'
initial = ROOT / 'production/C-03/tests-21nov/premier-pret-avant-arbitrages'
assert '172 tests' in (initial / 'PRET').read_text(encoding='utf-8')
assert '184 tests' in (ROOT / 'production/C-03/PRET').read_text(encoding='utf-8')
assert read('production/C-03/tests-21nov/premier-pret-avant-arbitrages/final.json')['exit_code'] == 0

doc = read('production/A-00/tests-21nov/documentary.json')
assert doc['status'] == 'PASS' and doc['passed'] == doc['total'] == 281
for path, expected in doc['input_sha256'].items():
    assert digest(ROOT / 'production/A-00' / path) == expected

run = 'production/A-01/tests-21nov/d1cc212680fd'
a01 = read(run + '/result.json')
assert a01['status'] == 'PASS' and a01['passed'] == len(a01['checks']) == 18 and a01['failed'] == 0
assert a01['owned_container_removed'] and not a01['full_staging_ready']
assert len(a01['runs']) == 2 and {r['storage'] for r in a01['runs']} == {'classic','hpos'}
assert a01['unit_results']['archive']['receipt']['tests'] == 12
assert a01['unit_results']['harness']['receipt']['tests_run'] == 17
assert a01['unit_results']['data']['receipt']['ok']
for path, expected in read(run + '/sources.json').items():
    assert digest(ROOT / path) == expected, path
assert digest(ROOT / 'wp/outils/staging-court/run.py') == a01['runner_sha256']
assert not (ROOT / 'production/A-01/PRET').exists()
assert (ROOT / 'production/A-01/BLOQUE-21nov.md').is_file()

native = read('wp/tests/staging-e2e/evidence/9ff611303d90/result.json')
assert native['exit_code'] == 0
counts = {state: sum(c['status']==state for c in native['checks']) for state in ['PASS','FAIL','NOT_TESTED']}
assert counts == {'PASS':131,'FAIL':0,'NOT_TESTED':2}
assert all(c['status']=='PASS' for c in read('wp/tests/staging-e2e/evidence/9ff611303d90/journal.json')['checks'])
for path, expected in read('wp/tests/staging-e2e/evidence/9ff611303d90/subject-source.json').items():
    assert digest(ROOT / 'wp/outils/staging' / path) == expected

labels = ['org.imagine.correction-' + s for s in ['c-03','c-01','c-04','c-02','a-00']]
labels += ['org.imagine.a00-documentary', 'org.imagine.a01-court']
docker = ['wsl.exe','-d','Ubuntu','--','docker'] if os.name == 'nt' else ['docker']
for label in labels:
    p = subprocess.run(docker + ['ps','-a','--filter','label='+label,'--format','{{.Names}}'], capture_output=True, timeout=30)
    assert p.returncode == 0 and not p.stdout.strip(), (label,p.stdout)
ready = ['C-03','C-01','C-04','C-02','A-00']
assert all((ROOT / 'production' / lot / 'PRET').is_file() for lot in ready)
result = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'evidence_audit': 'PASS', 'task_status': 'PARTIAL_A01_BLOCKED', 'ready_for_review': ready,
          'PHP_distinct_suites': php,
          'PHP_total': {k:sum(r[k] for r in php) for k in ['tests','assertions']},
          'A00_documentary_checks': doc['total'], 'A01_roundtrip_checks':18,
          'A01_archive_tests':12, 'A01_harness_tests':17,
          'A01_data_cases':a01['unit_results']['data']['receipt']['cases'],
          'A01_data_assertions':a01['unit_results']['data']['receipt']['assertions'],
          'A01_native_e2e':counts, 'first_C03_PRET_history_preserved':True,
          'owned_labels_empty':labels, 'A01_no_false_PRET':True}
(ROOT / 'files/rapports/2026-11-21-verification-finale.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
