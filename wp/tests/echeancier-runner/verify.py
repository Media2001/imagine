"""Verify Option A receipts, current source bytes and exact owned cleanup."""
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
    p.add_argument('--unit', default='reprise-final-unit')
    p.add_argument('--e2e', default='reprise-final-e2e')
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
    assert unit['failed'] == 0 and unit['tests'] == len(unit['results'])
    assert unit['assertions'] > 0 and all(t['pass'] for t in unit['results'])
    test_names = [test['test'] for test in unit['results']]
    assert len(test_names) == len(set(test_names))
    assert sum(name.startswith('annee_complete_') for name in test_names) == 365
    assert all(name in test_names for name in (
        'option_a_accepte_cinq_dates_dans_fenetre_numerique',
        'reglage_marge_sans_defaut_refuse_planification',
        'reglage_rejet_reste_du_defaut_et_abandon_explicite',
        'reglage_tarif_fige_bloc_defaut_et_courant_seulement_impayes',
        'reglages_option_decode_strict_et_matrice_complete'))
    assert len(unit['accepted_five_date_command_dates']) == 28
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
        assert [s['commande'] for s in run['scenarios']] == [
            '2027-02-20 12:00:00', '2027-04-09 12:00:00', '2027-04-10 12:00:00', '2027-04-11 12:00:00']
        assert all(c['pass'] for c in run['checks'])
        check_names = collections.Counter(c['check'] for c in run['checks'])
        for name in ('admin_option_readback_each_value', 'admin_margin_changes_engine', 'admin_policy_changes_projection'):
            assert check_names[name] == 12
        for name in ('admin_not_public_rest', 'admin_no_default_margin', 'admin_missing_margin_blocks_engine',
                     'admin_form_standard_nonce', 'admin_anonymous_form_denied',
                     'admin_invalid_preserves_previous_option', 'admin_clear_margin_keeps_unconfigured'):
            assert check_names[name] == 1
        total_checks += len(run['checks'])
        storage_ids = []
        for scenario in run['scenarios']:
            rows = scenario['rows']
            assert len(rows) == 8 and scenario['renewals'] == 7
            assert collections.Counter(row['cycle'] for row in rows) == {1: 4, 2: 4}
            assert len({row['order_id'] for row in rows}) == 8
            assert sum(row['initial'] for row in rows) == 1
            assert len({row['numero'] for row in rows}) == 8
            instants = [datetime.datetime.fromisoformat(row['date']) for row in rows]
            assert all(left < right for left, right in zip(instants, instants[1:]))
            for cycle in (1, 2):
                assert [row['rang'] for row in rows if row['cycle'] == cycle] == [1, 2, 3, 4]
            assert scenario['first_window_payment_dates'] == (5 if '2027-04-09' in scenario['commande'] else 4)
            storage_ids.extend(row['order_id'] for row in rows)
            for row in rows[1:]:
                expected = int(datetime.datetime.fromisoformat(row['date']).timestamp())
                assert row['native_action_timestamp'] == expected
                assert row['status'] in ('processing', 'completed')
            total_initial += 1
            total_renewals += scenario['renewals']
            scenarios.append({'storage': 'hpos' if run['versions']['hpos'] else 'classic',
                              'commande': scenario['commande'], 'subscription_id': scenario['subscription_id'],
                              'first_window_payment_dates': scenario['first_window_payment_dates'],
                              'initial_order_id': rows[0]['order_id'],
                              'renewal_order_ids': [row['order_id'] for row in rows[1:]]})
        assert len(storage_ids) == len(set(storage_ids)), 'Order reused across scenarios'
    assert total_initial == 8 and total_renewals == 56
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
    sources = read(ROOT / 'production/C-05/sources/review-2026-11-22.json')
    assert len(sources) == 8 and all(s['status'] == 200 and s['quote'] for s in sources)
    owned = []
    for directory in ('wp/plugins/imagine-pilotage/src/Echeancier', 'wp/plugins/imagine-pilotage/tests/Echeancier',
                      'wp/tests/echeancier-runner', 'production/C-05'):
        owned += [f for f in (ROOT / directory).rglob('*') if f.is_file() and f.name != 'verification.json']
    result = {'verified_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'technical_evidence_verified': True, 'acceptance_complete': True,
              'PRET_present': (ROOT / 'production/C-05/PRET').exists(), 'blockers': [],
              'production_authorized': False, 'shared_bootstrap_wired': False,
              'parent_seam': '(new Imagine\\Pilotage\\Echeancier\\ReglagesAdministration())->enregistrer();',
              'tests': unit['tests'], 'assertions': unit['assertions'], 'failed': unit['failed'],
              'accepted_five_date_example': example,
              'accepted_five_date_daily_commands_of_365': len(unit['accepted_five_date_command_dates']),
              'scenario_checks': total_checks, 'envelope_checks': len(real['checks']),
              'storage_runs': len(real['runs']), 'subscriptions': len(scenarios),
              'initial_orders': total_initial, 'real_manual_renewal_orders': total_renewals,
              'total_orders': total_initial + total_renewals, 'scenarios': scenarios,
              'c01_unchanged_inventory_and_sha256': c01, 'exact_owned_resources_absent': absent,
              'source_receipts': [a.unit, a.e2e],
              'artifact_sha256': {f.relative_to(ROOT).as_posix(): sha(f) for f in sorted(owned)}}
    (OUT / 'verification.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('artifact_sha256', 'scenarios', 'c01_unchanged_inventory_and_sha256')}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
