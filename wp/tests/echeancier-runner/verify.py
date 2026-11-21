"""Verify current C05 receipts and exact cleanup; acceptance stays BLOCKED."""
import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'production/C-05/preuves'
DOCKER = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker']


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--unit', default='final-unit-3')
    p.add_argument('--e2e', default='final-e2e-3')
    a = p.parse_args()
    assert all(re.fullmatch('[a-z0-9-]{1,64}', s) for s in (a.unit, a.e2e))
    receipts = [read(OUT / (n + '.json')) for n in (a.unit, a.e2e)]
    for receipt in receipts:
        assert receipt['exit_code'] == receipt['syntax_exit'] == 0
        assert receipt['container_sources_verified']
        assert receipt['runner_sha256'] == sha(ROOT / 'wp/tests/echeancier-runner/run.py')
        for rel, digest in receipt['source_sha256'].items():
            assert sha(ROOT / rel) == digest, 'Current source drift: ' + rel
        for phase in ('safety_before', 'safety_after'):
            safety = receipt[phase]
            assert safety['network'] == 'none' and not safety['mounts'] and not safety['ports']
            assert not safety['privileged'] and safety['no_new_privileges'] and 'ALL' in safety['cap_drop']
    assert receipts[0]['source_sha256'] == receipts[1]['source_sha256']
    unit = read(OUT / (a.unit + '-result.json'))
    assert unit['failed'] == 0 and unit['tests'] == len(unit['results']) == 376
    assert unit['assertions'] == 1473 and all(t['pass'] for t in unit['results'])
    assert len(unit['blocked_renewal_command_dates']) == 28
    example = unit['counterexample']
    begin = datetime.datetime.fromisoformat(example['commande'])
    end = datetime.datetime.fromisoformat(example['anniversaire'])
    assert len([x for x in example['dates'] if begin <= datetime.datetime.fromisoformat(x) < end]) == 5
    assert example['count_in_first_anniversary_window'] == 5
    real = read(OUT / (a.e2e + '-result.json'))
    assert real['exit_code'] == 0 and 'error' not in real and len(real['runs']) == 2
    assert all(c['pass'] for c in real['checks'])
    storage = [r['versions']['hpos'] for r in real['runs']]
    assert storage == [False, True]
    total_initial = total_renewals = total_checks = 0
    scenarios = []
    for run in real['runs']:
        assert run['failed'] == 0 and run['error'] is None
        assert len(run['scenarios']) == 3 and len(run['checks']) == 230
        assert all(c['pass'] for c in run['checks'])
        total_checks += len(run['checks'])
        for scenario in run['scenarios']:
            rows = scenario['rows']
            assert len(rows) == 8 and scenario['renewals'] == 7
            assert collections.Counter(row['cycle'] for row in rows) == {1: 4, 2: 4}
            assert len({row['order_id'] for row in rows}) == 8
            assert sum(row['initial'] for row in rows) == 1
            for row in rows[1:]:
                expected = int(datetime.datetime.fromisoformat(row['date']).timestamp())
                assert row['native_action_timestamp'] == expected
                assert row['status'] in ('processing', 'completed')
            total_initial += 1
            total_renewals += scenario['renewals']
            scenarios.append({'storage': 'hpos' if run['versions']['hpos'] else 'classic',
                              'commande': scenario['commande'], 'subscription_id': scenario['subscription_id'],
                              'initial_order_id': rows[0]['order_id'],
                              'renewal_order_ids': [row['order_id'] for row in rows[1:]]})
    assert total_initial == 6 and total_renewals == 42 and total_checks == 460
    original = read(OUT / 'red-initial.json')['source_sha256']
    c01 = {rel: digest for rel, digest in original.items() if '/src/Numeros/' in rel}
    assert len(c01) == 7
    actual_inventory = {(ROOT / 'wp/plugins/imagine-pilotage/src/Numeros' / f.name).relative_to(ROOT).as_posix()
                        for f in (ROOT / 'wp/plugins/imagine-pilotage/src/Numeros').glob('*.php')}
    assert set(c01) == actual_inventory
    assert all(sha(ROOT / rel) == digest for rel, digest in c01.items())
    names = set()
    for file in OUT.glob('*.json'):
        data = read(file)
        if isinstance(data, dict) and data.get('safety_before'):
            name = data['safety_before']['container']
            assert re.fullmatch('imagine-c05-[a-f0-9]{12}', name)
            names.add(name)
    absent = []
    for name in sorted(names):
        probe = subprocess.run(DOCKER + ['inspect', name], capture_output=True, text=True, timeout=30)
        assert probe.returncode and 'no such object' in probe.stderr.lower(), name + ' not verifiably absent'
        absent.append({'container': name, 'absent': True, 'diagnostic': probe.stderr.strip()})
    assert absent and read(OUT / 'cleanup.json')['owned_removed']
    assert not (OUT / 'runner-state.json').exists()
    assert not (ROOT / 'production/C-05/PRET').exists()
    sources = read(ROOT / 'production/C-05/sources/retrieval.json')
    assert len(sources) == 6 and all(s['status'] == 200 and s['quote'] for s in sources)
    owned = []
    for directory in ('wp/plugins/imagine-pilotage/src/Echeancier', 'wp/plugins/imagine-pilotage/tests/Echeancier',
                      'wp/tests/echeancier-runner', 'production/C-05'):
        owned += [f for f in (ROOT / directory).rglob('*') if f.is_file() and f.name != 'verification.json']
    result = {'verified_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'technical_evidence_verified': True, 'acceptance_complete': False, 'PRET_present': False,
              'blocker': 'Common first renewal may precede anniversary: five payment dates in first date-to-date year',
              'tests': unit['tests'], 'assertions': unit['assertions'], 'failed': unit['failed'],
              'counterexample': example, 'blocked_daily_commands_of_365': len(unit['blocked_renewal_command_dates']),
              'scenario_checks': total_checks, 'storage_runs': len(real['runs']), 'subscriptions': len(scenarios),
              'initial_orders': total_initial, 'real_manual_renewal_orders': total_renewals,
              'total_orders': total_initial + total_renewals, 'scenarios': scenarios,
              'c01_unchanged_inventory_and_sha256': c01, 'exact_owned_resources_absent': absent,
              'source_receipts': [a.unit, a.e2e],
              'artifact_sha256': {f.relative_to(ROOT).as_posix(): sha(f) for f in sorted(owned)}}
    (OUT / 'verification.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('artifact_sha256', 'scenarios', 'c01_unchanged_inventory_and_sha256')}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
