"""Readback/seal for C05 SEPA; reuse corrections.py, never rewrite a PHP bench."""
import collections
import datetime
import hashlib
import importlib.util
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('c05_sepa_base', HERE / 'corrections.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
ROOT, OUT = c.ROOT, c.OUT


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def verify():
    assert not c.b.STATE.exists() and not c.c05.STATE.exists(), 'Clean up both owned runners first'
    baseline = read('protected-before.json')
    assert c.protected() == baseline, 'Protected sibling inventory drift'
    standard = read('final.json')
    for key in ['exit_code', 'psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code']:
        assert standard[key] == 0, key
    assert standard['source_sha256'] == c.payload()[1], 'Final standard sources stale'
    assert standard['network_disconnected'] and standard['no_mounts'] and standard['no_ports']
    old = json.loads((ROOT / 'production/C-05/replays/fusion-22nov-1458/final.json').read_text())['source_sha256']
    current = standard['source_sha256']
    changed = sorted(p for p in old.keys() | current.keys() if old.get(p) != current.get(p))
    assert set(changed) == {
        'src/Echeancier/Reglages.php', 'src/Echeancier/ReglagesAdministration.php',
        'src/Echeancier/README.md', 'tests/Echeancier/ConfirmationPremierSepaTest.php',
    }, changed
    xml = ET.parse(OUT / 'final.xml').getroot()
    suites = xml.find('testsuite').findall('testsuite')
    counts = {s.attrib['name']: {k: int(s.attrib[k]) for k in
              ['tests', 'assertions', 'failures', 'errors', 'skipped']} for s in suites}
    assert set(counts) == {'Numeros', 'Robots', 'Entreprise', 'Acces', 'Envoi', 'Echeancier'}
    assert all(s[k] == 0 for s in counts.values() for k in ['failures', 'errors', 'skipped'])
    sepa_cases = [t for t in xml.iter('testcase') if t.attrib.get('class', '').endswith('ConfirmationPremierSepaTest')]
    assert len(sepa_cases) == 19, 'SEPA suite not fully discovered'
    sepa_names = [t.attrib['name'] for t in sepa_cases]
    for name in ['MargeConfirmationPremierSepaAppliqueeParDefaut', 'DeuxPositionsDecodees',
                 'PremierSepaAttendMarge', 'SansMargeRetientConfirmation', 'ConfirmationAnterieure',
                 'MargeNonConfiguree', 'SansMargeNeRendPasPlanifiable']:
        assert any(name in n for n in sepa_names), name
    for data in ['dst-printemps', 'dst-automne', '29-fevrier', 'egal-cloture', 'sans-confirmation', 'confirmation-tardive']:
        assert any(data in n for n in sepa_names), data
    e2e = read('final-e2e.json')
    assert e2e['exit_code'] == e2e['syntax_exit'] == 0
    assert e2e['source_sha256'] == c.c05.payload()[1], 'Final e2e source drift'
    assert e2e['runner_sha256'] == c.sha(HERE / 'run.py')
    for phase in ['safety_before', 'safety_after']:
        safety = e2e[phase]
        assert safety['network'] == 'none' and safety['mounts'] == safety['ports'] == []
        assert not safety['privileged'] and safety['no_new_privileges'] and 'ALL' in safety['cap_drop']
    result = read('final-e2e-result.json')
    assert result['exit_code'] == 0 and 'error' not in result
    assert all(x['pass'] for x in result['checks'])
    assert [r['versions']['hpos'] for r in result['runs']] == [False, True]
    totals = collections.Counter(envelope_checks=len(result['checks']))
    for run in result['runs']:
        assert run['failed'] == 0 and run['error'] is None and all(x['pass'] for x in run['checks'])
        names = collections.Counter(x['check'] for x in run['checks'])
        for name in ['sepa_admin_field_present', 'sepa_admin_default_with_margin', 'sepa_old_option_defaults_with_margin']:
            assert names[name] == 1, name
        for name in ['sepa_admin_persisted_readback', 'sepa_admin_decoded_readback', 'sepa_admin_selection_rendered',
                     'sepa_admin_changes_paid_projection', 'sepa_not_paid_before_effective_date',
                     'sepa_paid_at_effective_date', 'sepa_paid_before_closure_policy',
                     'sepa_no_confirmation_never_paid', 'sepa_late_confirmation_never_anticipated']:
            assert names[name] == 2, name
        assert names['sepa_invalid_keeps_previous'] == 10
        totals['checks'] += len(run['checks'])
        totals['sepa_checks'] += sum(x['check'].startswith('sepa_') for x in run['checks'])
        for scenario in run['scenarios']:
            rows = scenario['rows']
            assert len(rows) == 8 and scenario['renewals'] == 7
            instants = [datetime.datetime.fromisoformat(x['date']) for x in rows]
            assert all(a < b for a, b in zip(instants, instants[1:]))
            assert len({x['order_id'] for x in rows}) == len({x['numero'] for x in rows}) == 8
            for cycle in [1, 2]:
                assert [x['rang'] for x in rows if x['cycle'] == cycle] == [1, 2, 3, 4]
            assert scenario['first_window_payment_dates'] == (5 if '04-09' in scenario['commande'] else 4)
            for row in rows[1:]:
                assert row['native_action_timestamp'] == int(datetime.datetime.fromisoformat(row['date']).timestamp())
            totals['subscriptions'] += 1
            totals['initial_orders'] += 1
            totals['renewal_orders'] += scenario['renewals']
    assert totals['subscriptions'] == 8 and totals['initial_orders'] == 8 and totals['renewal_orders'] == 56
    red = {}
    for suffix in ['defaut', 'positions', 'date', 'sans-marge', 'confirmation', 'marge-obligatoire', 'chronologie']:
        key = 'red-sepa-' + suffix
        red[key] = read(key + '.json')['exit_code']
        assert red[key] != 0
    red['red-sepa-admin'] = read('red-sepa-admin.json')['exit_code']
    assert red['red-sepa-admin'] != 0
    refused = read('red-sepa-admin-result.json')['checks']
    assert any(x['check'] == 'classic:scenario' and not x['pass'] and
               x['detail']['error']['message'].startswith('sepa_admin_field_present:') for x in refused)
    absent = []
    for file in ['standard-cleanup.json', 'cleanup.json']:
        cleanup = read(file)
        assert cleanup['owned_removed']
        probe = c.b.call(['inspect', cleanup['container']], check=False)
        diagnostic = probe.stderr.decode().strip()
        assert probe.returncode and 'no such object' in diagnostic.lower()
        absent.append({'container': cleanup['container'], 'absent': True, 'diagnostic': diagnostic})
    summary = {
        'verified_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'standard_suites': counts,
        'total_tests': sum(x['tests'] for x in counts.values()),
        'total_assertions': sum(x['assertions'] for x in counts.values()),
        'sepa_unit_tests': len(sepa_cases), 'e2e': dict(totals),
        'red_exit_codes': red, 'changed_plugin_paths_since_previous_packet': changed,
        'protected_files': len(baseline), 'protected_inventory_unchanged': True,
        'owned_containers_absent': absent, 'bootstrap_wired': False, 'q1_sepa_open': False,
        'production_authorized': False, 'real_payment_exercised': False,
        'source_sha256': current,
        'artifacts_sha256': {**c.inventory(HERE), **{p.relative_to(ROOT).as_posix(): c.sha(p)
                             for p in sorted((ROOT / 'production/C-05').glob('*.md'))}},
        'proof_sha256': {p.name: c.sha(p) for p in sorted(OUT.iterdir()) if p.is_file()
                         and p.name not in ['verification.json', 'remise.json']},
    }
    target = OUT / 'verification.json'
    if target.exists():
        previous = read('verification.json')
        assert {k: v for k, v in summary.items() if k != 'verified_at_utc'} == {
            k: v for k, v in previous.items() if k != 'verified_at_utc'}, 'Seal drift'
    else:
        c.save('verification.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in
                      ['source_sha256', 'artifacts_sha256', 'proof_sha256']}, indent=2))
    print('verification.json SHA-256:', c.sha(target))


if __name__ == '__main__':
    assert c.PACKET != 'fusion-22nov-1458', 'Select a new IMAGINE_C05_PACKET'
    c.verify = verify
    c.main()
