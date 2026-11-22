"""C05 correction packet: real PHP only in owned disposable containers."""
import argparse
import datetime
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import re
import sys
import tarfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
PACKET = os.environ.get('IMAGINE_C05_PACKET', 'fusion-22nov-1458')
assert re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', PACKET)
OUT = ROOT / 'production/C-05/replays' / PACKET


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c03 = load('c05_standard', ROOT / 'wp/tests/robots-runner/run.py')
b = c03.bench
b.OUT = OUT
b.STATE = OUT / 'standard-state.json'
b.LABEL = 'org.imagine.c05-standard-runner'
original_payload = b.payload
c05 = load('c05_offline', HERE / 'run.py')
c05.OUT = OUT
c05.STATE = OUT / 'e2e-state.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(directory):
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(directory.rglob('*'))
            if p.is_file() and 'vendor' not in p.parts and '__pycache__' not in p.parts}


def save(name, data):
    file = OUT / name
    assert not file.exists(), 'Never overwrite evidence: ' + str(file)
    file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def protected():
    directories = ['wp/plugins/imagine-connecteur', 'wp/plugins/imagine-pilotage/src/Numeros',
                   'wp/plugins/imagine-pilotage/src/Acces', 'wp/plugins/imagine-pilotage/tests/Acces',
                   'wp/plugins/imagine-pilotage/src/Envoi', 'wp/plugins/imagine-pilotage/tests/Envoi',
                   'production/C-06', 'production/C-07', 'wp/tests/acces-runner', 'wp/tests/envoi-runner']
    result = {}
    for directory in directories:
        result.update(inventory(ROOT / directory))
    for file in ['wp/plugins/imagine-pilotage/composer.json', 'wp/plugins/imagine-pilotage/composer.lock',
                 'wp/plugins/imagine-pilotage/README.md']:
        result[file] = sha(ROOT / file)
    return result


def payload():
    data, files = original_payload()
    stream = io.BytesIO(data)
    source = ROOT / 'wp/plugins/imagine-connecteur/src'
    with tarfile.open(fileobj=stream, mode='a') as archive:
        for file in sorted(source.glob('*.php')):
            content = file.read_bytes()
            name = 'connecteur/' + file.name
            info = tarfile.TarInfo(name)
            info.size = len(content)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(content))
            files[name] = hashlib.sha256(content).hexdigest()
    return stream.getvalue(), files


b.payload = payload


def standard_run(name, filter_value=None):
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', name)
    assert not (OUT / (name + '.json')).exists(), 'Immutable receipt'
    container = json.loads(b.STATE.read_text())['container']
    assert not b.info(container)['NetworkSettings']['Networks']
    b.call(['exec', container, 'rm', '-f', '/tmp/result.xml'])
    sys.argv = [str(__file__), 'run', '--name', name]
    if filter_value:
        assert re.fullmatch(r'[A-Za-z0-9_]+', filter_value)
        sys.argv += ['--filter', filter_value]
    b.main()


def close_standard():
    name = json.loads(b.STATE.read_text())['container']
    b.info(name)  # Positive ownership, including if preparation failed before disconnection.
    b.call(['rm', '-f', name])
    result = b.call(['inspect', name], check=False)
    assert result.returncode and 'no such object' in result.stderr.decode().lower()
    save('standard-cleanup.json', {'container': name, 'owned_removed': True,
                                  'diagnostic': result.stderr.decode().strip()})
    b.STATE.unlink()


def verify():
    assert not b.STATE.exists() and not c05.STATE.exists()
    assert protected() == json.loads((OUT / 'protected-before.json').read_text()), 'Protected inventory drift'
    standard = json.loads((OUT / 'final.json').read_text())
    assert all(standard[k] == 0 for k in ['exit_code', 'psr12_exit_code', 'syntax_exit_code',
                                        'composer_validate_exit_code'])
    assert standard['source_sha256'] == payload()[1]
    tree = ET.parse(OUT / 'final.xml').getroot()
    suites = tree.find('testsuite').findall('testsuite')
    counts = {s.attrib['name']: {k: int(s.attrib[k]) for k in
                               ['tests', 'assertions', 'failures', 'errors', 'skipped']} for s in suites}
    assert {'Numeros', 'Robots', 'Entreprise', 'Acces', 'Envoi', 'Echeancier'} <= counts.keys()
    assert counts['Echeancier']['tests'] >= 380
    cases = [t.attrib['name'] for s in suites if s.attrib['name'] == 'Echeancier' for t in s.iter('testcase')]
    assert any('CloturesEgalesJonction' in n for n in cases)
    assert any('09Avril' in n for n in cases)
    e2e = json.loads((OUT / 'final-e2e.json').read_text())
    assert e2e['exit_code'] == e2e['syntax_exit'] == 0
    assert e2e['source_sha256'] == c05.payload()[1]
    assert e2e['runner_sha256'] == sha(HERE / 'run.py')
    result = json.loads((OUT / 'final-e2e-result.json').read_text())
    assert result['exit_code'] == 0 and 'error' not in result
    assert all(c['pass'] for c in result['checks'])
    assert [r['versions']['hpos'] for r in result['runs']] == [False, True]
    totals = {'subscriptions': 0, 'initial_orders': 0, 'renewal_orders': 0, 'scenario_checks': 0,
              'envelope_checks': len(result['checks'])}
    for run in result['runs']:
        assert run['failed'] == 0 and run['error'] is None and all(c['pass'] for c in run['checks'])
        totals['scenario_checks'] += len(run['checks'])
        names = [c['check'] for c in run['checks']]
        assert names.count('admin_anonymous_wp_die_translated') == 1
        assert names.count('equal_block_boundary_refused_before_orders') == 1
        for key in ['admin_option_readback_each_value', 'admin_margin_changes_engine', 'admin_policy_changes_projection']:
            assert names.count(key) == 12
        for scenario in run['scenarios']:
            rows = scenario['rows']
            assert len(rows) == 8 and scenario['renewals'] == 7
            instants = [datetime.datetime.fromisoformat(r['date']) for r in rows]
            assert all(a < z for a, z in zip(instants, instants[1:]))
            assert len({r['order_id'] for r in rows}) == len({r['numero'] for r in rows}) == 8
            for cycle in (1, 2):
                assert [r['rang'] for r in rows if r['cycle'] == cycle] == [1, 2, 3, 4]
            assert scenario['first_window_payment_dates'] == (5 if '04-09' in scenario['commande'] else 4)
            for row in rows[1:]:
                assert row['native_action_timestamp'] == int(datetime.datetime.fromisoformat(row['date']).timestamp())
            totals['subscriptions'] += 1
            totals['initial_orders'] += 1
            totals['renewal_orders'] += scenario['renewals']
    assert totals['subscriptions'] == 8 and totals['initial_orders'] == 8 and totals['renewal_orders'] == 56
    absent = []
    for file in ['standard-cleanup.json', 'cleanup.json']:
        cleanup = json.loads((OUT / file).read_text())
        assert cleanup['owned_removed']
        probe = b.call(['inspect', cleanup['container']], check=False)
        assert probe.returncode and 'no such object' in probe.stderr.decode().lower()
        absent.append({'container': cleanup['container'], 'absent': True, 'diagnostic': probe.stderr.decode().strip()})
    summary = {'verified_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'standard_suites': counts, 'e2e': totals, 'owned_containers_absent': absent,
               'protected_inventory_unchanged': True, 'production_authorized': False,
               'bootstrap_wired': False, 'q1_sepa_open': True,
               'source_sha256': payload()[1], 'runner_sha256': sha(pathlib.Path(__file__)),
               'c05_artifact_sha256': {**inventory(ROOT / 'wp/tests/echeancier-runner'),
                                      **{p.relative_to(ROOT).as_posix(): sha(p) for p in
                                         sorted((ROOT / 'production/C-05').glob('*.md'))}}}
    if (OUT / 'verification.json').exists():
        old = json.loads((OUT / 'verification.json').read_text())
        for key in summary:
            if key != 'verified_at_utc':
                assert summary[key] == old[key], 'Seal drift: ' + key
    else:
        save('verification.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in
                      ['source_sha256', 'runner_sha256', 'c05_artifact_sha256']}, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['prepare', 'run', 'e2e-prepare', 'e2e', 'close', 'e2e-close', 'verify'])
    p.add_argument('--name', default='final')
    p.add_argument('--filter')
    a = p.parse_args()
    if a.action == 'prepare':
        assert not OUT.exists(), 'Choose a fresh IMAGINE_C05_PACKET'
        OUT.mkdir(parents=True)
        save('protected-before.json', protected())
        c03.prepare()
    elif a.action == 'run':
        standard_run(a.name, a.filter)
    elif a.action == 'close':
        close_standard()
    elif a.action in ['e2e-prepare', 'e2e', 'e2e-close']:
        action = {'e2e-prepare': 'prepare', 'e2e-close': 'close'}.get(a.action, 'e2e')
        if action == 'e2e':
            assert not (OUT / (a.name + '.json')).exists(), 'Immutable receipt'
        sys.argv = [str(HERE / 'run.py'), action, '--name', a.name]
        c05.main()
    else:
        verify()


if __name__ == '__main__':
    main()
