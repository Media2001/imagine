"""Verify C-03 delivered bytes, real JUnit receipts and protected siblings offline."""
import datetime
import hashlib
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'production/C-03/tests'
PLUGIN = ROOT / 'wp/plugins/imagine-pilotage'
BASES = ['production/C-01', 'production/C-04', 'wp/plugins/imagine-connecteur',
         'wp/tests/numeros-runner', 'wp/tests/connecteur-runner', 'wp/plugins/imagine-pilotage']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def passed(receipt, keys):
    assert all(receipt[key] == 0 for key in keys), receipt
    assert receipt['network_disconnected'] and receipt['no_mounts'] and receipt['no_ports']
    assert receipt['container_source_verified']


def junit(path, name=None):
    root = ET.parse(path).getroot()
    if name is not None:
        root = next(e for e in root.iter('testsuite') if e.attrib.get('name') == name)
    cases = list(root.iter('testcase'))
    assert cases and not list(root.iter('failure')) and not list(root.iter('error'))
    assert not list(root.iter('skipped'))
    if 'tests' in root.attrib:
        assert int(root.attrib['tests']) == len(cases)
    return {'tests': len(cases), 'assertions': sum(int(c.attrib.get('assertions', 0)) for c in cases)}


before = read('protected-before.json')
current = {p.relative_to(ROOT).as_posix(): digest(p) for base in BASES
           for p in (ROOT / base).rglob('*') if p.is_file()}
shared = {'wp/plugins/imagine-pilotage/README.md', 'wp/plugins/imagine-pilotage/phpunit.xml'}
assert all(current.get(p) == h for p, h in before.items() if p not in shared), 'Protected sibling changed'
new = set(current) - set(before)
allowed = ('wp/plugins/imagine-pilotage/src/Robots/', 'wp/plugins/imagine-pilotage/tests/Robots/')
assert all(p.startswith(allowed) or p == 'wp/plugins/imagine-pilotage/config/robots.php' for p in new), new
readme = (PLUGIN / 'README.md').read_bytes().split(b'\n## C-03')[0].rstrip(b'\r\n') + b'\n'
assert hashlib.sha256(readme).hexdigest() == before['wp/plugins/imagine-pilotage/README.md']
xml = (PLUGIN / 'phpunit.xml').read_bytes()
xml = xml.replace(b'        <testsuite name="Robots"><directory>tests/Robots</directory></testsuite>\n', b'')
assert hashlib.sha256(xml).hexdigest() == before['wp/plugins/imagine-pilotage/phpunit.xml']
final = read('final.json')
passed(final, ['exit_code', 'psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code'])
assert final['processes_before_suite'] == ['sleep']
for path, expected in final['source_sha256'].items():
    assert digest(PLUGIN / path) == expected, 'Final tested source drift: ' + path
copied = {p.relative_to(PLUGIN).as_posix() for p in PLUGIN.rglob('*')
          if p.is_file() and p.name != '.gitkeep' and 'vendor' not in p.parts}
assert copied == set(final['source_sha256']), 'Final source inventory drift'
config = read('configuration.json')
passed(config, ['psr12_exit_code', 'syntax_exit_code'])
assert digest(PLUGIN / 'config/robots.php') == config['config_sha256']
c04 = read('c04-regression.json')
passed(c04, ['exit_code', 'psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code'])
for path, expected in c04['source_sha256'].items():
    assert digest(ROOT / 'wp/plugins/imagine-connecteur' / path) == expected
assert digest(ROOT / 'wp/tests/numeros-runner/run.py') == final['runner_sha256']
assert digest(pathlib.Path(__file__).with_name('extra_checks.py')) == config['runner_sha256']
assert digest(pathlib.Path(__file__).with_name('regression_c04.py')) == c04['runner_sha256']
assert read('cleanup.json')['owned_runner_removed']
assert not (OUT / 'runner-state.json').exists()
for p in (PLUGIN / 'src/Robots').glob('*.php'):
    text = p.read_text(encoding='utf-8')
    assert 'declare(strict_types=1);' in text
    assert 'namespace Imagine\\Pilotage\\Robots;' in text
    assert not re.search(r'\$_SERVER|\b(?:gethostbyaddr|dns_get_record|curl_exec|file_get_contents|getallheaders|time|hrtime)\s*\(', text)
counts = {'C-01': junit(OUT / 'final.xml', 'Numeros'), 'C-03': junit(OUT / 'final.xml', 'Robots'),
          'C-04': junit(OUT / 'c04-regression.xml')}
totals = {key: sum(value[key] for value in counts.values()) for key in ('tests', 'assertions')}
records = [ROOT / 'files/rapports/2026-11-20-17h07.md']
assert records[0].is_file(), 'Missing French delivery report'
for base in ['production/C-03', 'wp/tests/robots-runner']:
    records += [p for p in (ROOT / base).rglob('*') if p.is_file()]
records += [PLUGIN / 'README.md', PLUGIN / 'phpunit.xml', PLUGIN / 'config/robots.php']
records += list((PLUGIN / 'src/Robots').glob('*.php')) + list((PLUGIN / 'tests/Robots').glob('*.php'))
excluded = {'artifact-verification.json', 'fichiers-livres.json', 'runner-state.json'}
manifest = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(set(records)) if p.name not in excluded}
(OUT / 'fichiers-livres.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
result = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'PASS',
          'suites': counts, 'total': totals, 'protected_original_files': len(before) - len(shared),
          'protected_inventory_and_hashes_unchanged': True, 'shared_files_only_C03_appendix_and_suite': True,
          'final_tested_sources_match_delivery': True, 'network_test_calls': 'none; injected fake DNS only',
          'configuration_psr12_syntax_ok': True, 'owned_runner_cleanup_verified': True,
          'manifest_files': len(manifest), 'manifest_sha256': digest(OUT / 'fichiers-livres.json'),
          'checker_sha256': digest(pathlib.Path(__file__))}
(OUT / 'artifact-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
