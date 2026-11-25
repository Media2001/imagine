"""Read-only final A05 correction verification. No PHP on host, no Git."""
import datetime
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    receipt = json.loads((HERE / 'full-native-final.json').read_text())
    assert receipt['exit_code'] == 0 and receipt['duration_seconds'] > 0
    output = json.loads(receipt['stdout'])
    proof = pathlib.Path(output['output'])
    runner = json.loads((proof / 'runner.json').read_text())
    inner = json.loads((proof / 'result.json').read_text())
    assert runner['exit_code'] == inner['exit_code'] == 0
    assert all(row['ok'] for row in runner['checks'] + inner['checks'])
    unit = (proof / 'unit.log').read_text()
    tests = int(re.search(r'Ran (\d+) tests', unit)[1])
    assert tests == 21 and unit.rstrip().endswith('OK') and 'FAIL' not in unit
    sources = json.loads((proof / 'sources.json').read_text())
    drift = [name for name, sha in sources.items() if digest(ROOT / name) != sha]
    assert not drift, drift
    baseline = json.loads((HERE / 'baseline.json').read_text())['sha256']
    historical = {name:sha for name,sha in baseline.items() if name.startswith('production/A-05/preuves/')}
    assert all((ROOT / name).is_file() and digest(ROOT / name) == sha for name,sha in historical.items())
    own = {'wp/outils/bascule/a05/clean.py', 'wp/outils/bascule/nettoyer.md', 'wp/tests/a05/test_clean.py', 'wp/tests/a05/inside.py'}
    changes = [name for name,sha in baseline.items() if name.startswith('wp/') and (not (ROOT / name).is_file() or digest(ROOT / name) != sha)]
    assert own <= set(changes)
    protected = {name:sha for name,sha in baseline.items() if name.startswith(('wp/tests/a02-audit/', 'wp/tests/a03-non-regression/', 'wp/tests/a04/', 'wp/outils/bascule/a03/', 'wp/outils/bascule/a04/', 'wp/plugins/imagine-non-regression/'))}
    protected_drift = [name for name,sha in protected.items() if digest(ROOT / name) != sha]
    assert not protected_drift, protected_drift
    accepted_a04 = json.loads((ROOT / 'production/A-04/preuves/eb2aea037769/sources.json').read_text())
    accepted_a04_drift = [name for name,sha in accepted_a04.items() if digest(ROOT / name) != sha]
    assert not accepted_a04_drift, accepted_a04_drift
    stages = {}
    for point in ['P1', 'P2', 'P3', 'M1']:
        stages[point] = {}
        for stage,expected in [('red',1),('green',0)]:
            record = json.loads((HERE / (point+'-'+stage+'.json')).read_text())
            assert record['exit_code'] == expected
            result = json.loads(record['stdout'])
            assert all(row['ok'] for row in result['checks'] if row['check'] != 'unit')
            stages[point][stage] = {'evidence':str(pathlib.Path(result['output']).relative_to(ROOT)).replace('\\','/'), 'duration_seconds':record['duration_seconds'], 'exit_code':record['exit_code']}
    all_cases = {}
    expected_cases = {'P1-'+str(active)+'-'+str(reverse) for active in [True,False] for reverse in [False,True]}
    expected_cases |= {'P1-multiple-removals', 'P2-slash-retirer', 'P2-slash-desactiver', 'P2-hash-retirer', 'P2-hash-desactiver', 'P3-False', 'P3-True'}
    comparisons = {}
    for storage in ['classic', 'hpos']:
        rows = json.loads((proof / (storage+'-corrections.json')).read_text())
        assert len(rows) == 22 and {(row['case'],row['mode']) for row in rows} == {(case,mode) for case in expected_cases for mode in ['dry-run','real']}
        assert all(row['exit'] == 1 and row['stderr'] == row['expected']+'\n' and row['before'] == row['after'] and not row['state_created'] for row in rows)
        all_cases[storage] = len(rows)
        absent = json.loads((proof / (storage+'-absent-dry-run.json')).read_text())
        assert absent['operations'] == [] and len(absent['information']) == 5
        assert all(row['status'] == 'nommé, absent' for row in absent['information'])
        fingerprints = json.loads((proof / (storage+'-dry-fingerprints.json')).read_text())
        assert fingerprints['before_database'] == fingerprints['after_database'] and fingerprints['before_files'] == fingerprints['after_files']
        comparisons[storage] = json.loads((proof / (storage+'-comparison.json')).read_text())
        assert comparisons[storage]['native_exit'] == 0 and comparisons[storage]['anormal'] == 0 and comparisons[storage]['changes'] == []
        keys = {row['check'] for row in inner['checks'] if row['ok']}
        for name in ['actual_sigkill','actual_resume','repeat_zero_effect','fresh_second_pass_zero_effect','correction_M1_information_only','correction_M1_real_noop','correction_native_header_slash','correction_native_header_hash']:
            assert storage+':'+name in keys
    spec = importlib.util.spec_from_file_location('a05_final_runner', ROOT / 'wp/tests/a05/run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    remaining = module.bench.call(['ps','-a','--filter','label='+module.LABEL,'--format','{{.Names}}'])
    assert remaining.stdout.strip() == '', remaining.stdout
    result = {
        'verified_at':datetime.datetime.now().astimezone().isoformat(),
        'evidence':proof.relative_to(ROOT).as_posix(), 'unit_tests':tests,
        'integration_checks':len(inner['checks']), 'runner_checks':len(runner['checks']),
        'source_files_checked':len(sources), 'source_drift':drift,
        'historical_evidence_files_unchanged':len(historical),
        'protected_dependency_files_unchanged':len(protected),
        'accepted_a04_sources_verified':len(accepted_a04), 'accepted_a04_drift':accepted_a04_drift,
        'own_changed_files':sorted(own),
        'concurrent_out_of_scope_drift_not_touched':sorted(set(changes)-own),
        'native_correction_refusals':all_cases, 'native_a03':comparisons,
        'full_duration_seconds':receipt['duration_seconds'], 'tdd':stages,
        'new_test_package':False, 't01_preparation_required':False,
        't01_note':'Only cases added to the existing A05 Python package; no Composer/test package added. Historical T01 results are not claimed as fresh.',
        'a05_containers_remaining':[], 'exit_code':0,
    }
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__ == '__main__':
    main()
