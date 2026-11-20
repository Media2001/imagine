"""C-02 final offline artifact verification, not independent review or GO."""
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'production/C-02/tests'
PLUGIN = ROOT / 'wp/plugins/imagine-pilotage'
BASES = ['production/C-01', 'production/C-03', 'production/C-04',
         'wp/plugins/imagine-pilotage', 'wp/plugins/imagine-connecteur',
         'wp/tests/numeros-runner', 'wp/tests/robots-runner', 'wp/tests/connecteur-runner',
         'docs', 'doctrine', 'prompts', 'briefs']
REPORT = ROOT / 'files/rapports/2026-11-20-17h21-C-02.md'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def passed(receipt):
    for k in ['exit_code', 'psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code']:
        assert receipt[k] == 0, (k, receipt[k])
    for k in ['network_disconnected', 'no_mounts', 'no_ports', 'container_source_verified']:
        assert receipt[k] is True, k


def junit(path, suite=None):
    root = ET.parse(path).getroot()
    assert not any(list(root.iter(tag)) for tag in ['failure', 'error', 'skipped'])
    if suite:
        root = next(s for s in root.iter('testsuite') if s.attrib.get('name') == suite)
    cases = list(root.iter('testcase'))
    assert cases
    if 'tests' in root.attrib:
        assert int(root.attrib['tests']) == len(cases)
    return {'tests': len(cases), 'assertions': sum(int(c.attrib.get('assertions', 0)) for c in cases)}


before = read('protected-before.json')
assert len(before) == 377
current = {p.relative_to(ROOT).as_posix(): digest(p) for base in BASES
           for p in (ROOT / base).rglob('*') if p.is_file()}
shared = {'wp/plugins/imagine-pilotage/README.md', 'wp/plugins/imagine-pilotage/phpunit.xml'}
assert all(current.get(p) == h for p, h in before.items() if p not in shared), 'Protected source/evidence drift'
allowed = ('wp/plugins/imagine-pilotage/src/Entreprise/', 'wp/plugins/imagine-pilotage/tests/Entreprise/')
new = set(current) - set(before)
assert len(new) == 7 and all(p.startswith(allowed) for p in new), new
assert not set(before) - set(current)
readme = (PLUGIN / 'README.md').read_bytes()
assert readme.count('## C-02 —'.encode()) == 1
assert hashlib.sha256(readme.split('## C-02 —'.encode())[0]).hexdigest() == before['wp/plugins/imagine-pilotage/README.md']
line = b'        <testsuite name="Entreprise"><directory>tests/Entreprise</directory></testsuite>\n'
xml = (PLUGIN / 'phpunit.xml').read_bytes()
assert xml.count(line) == 1
assert hashlib.sha256(xml.replace(line, b'')).hexdigest() == before['wp/plugins/imagine-pilotage/phpunit.xml']

final = read('final.json')
passed(final)
assert final['php'] == '8.2.36' and final['processes_before_suite'] == ['sleep']
assert final['runner_sha256'] == digest(ROOT / 'wp/tests/numeros-runner/run.py')
files = {p.relative_to(PLUGIN).as_posix(): digest(p) for p in PLUGIN.rglob('*')
         if p.is_file() and p.name != '.gitkeep' and 'vendor' not in p.parts}
assert files == final['source_sha256'], 'Final tested bytes/inventory do not match delivery'
c04 = read('c04-regression.json')
passed(c04)
connector = ROOT / 'wp/plugins/imagine-connecteur'
c04_files = {p.relative_to(connector).as_posix(): digest(p) for p in connector.rglob('*')
             if p.is_file() and p.name != '.gitkeep' and 'vendor' not in p.parts}
assert c04_files == c04['source_sha256']
assert c04['runner_sha256'] == digest(pathlib.Path(__file__).with_name('regression_c04.py'))
for stage in ['canonique', 'normalisation', 'controles', 'traduction', 'recherche']:
    assert read('red-' + stage + '.json')['exit_code'] != 0
    passed(read('green-' + stage + '.json'))

counts = {lot: junit(OUT / 'final.xml', suite) for lot, suite in
          [('C-01', 'Numeros'), ('C-02', 'Entreprise'), ('C-03', 'Robots')]}
counts['C-04'] = junit(OUT / 'c04-regression.xml')
assert counts['C-02'] == {'tests': 41, 'assertions': 19560}
assert junit(OUT / 'final.xml') == {'tests': 169, 'assertions': 19860}
total = {k: sum(v[k] for v in counts.values()) for k in ['tests', 'assertions']}
assert total == {'tests': 191, 'assertions': 20021}

example = read('exemple.json')
assert example['exit_code'] == 0 and example['network_disconnected']
assert example['readme_sha256'] == digest(PLUGIN / 'README.md')
assert example['runner_sha256'] == digest(pathlib.Path(__file__).with_name('exemple.py'))
assert json.loads((OUT / 'exemple.log').read_text(encoding='utf-8')) == example['result']
assert example['result']['valide'] and not example['result']['recherche_disponible']
assert example['result']['denomination'] is None

cleanup = read('cleanup.json')
assert cleanup['owned_runner_removed'] and not (OUT / 'runner-state.json').exists()
assert re.fullmatch(r'imagine-c02-[a-f0-9]{12}', cleanup['container'])
p = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'inspect', cleanup['container']],
                   capture_output=True, timeout=30)
assert p.returncode != 0 and b'no such object:' in p.stderr.lower(), 'Owned runner still exists or Docker unavailable'
preparation = read('preparation.json')
assert preparation['composer_install_exit'] == 0 and preparation['host_lock_unchanged']
assert preparation['networks_after_preparation'] == {} and preparation['label'] == 'org.imagine.c02-runner'

for path in (PLUGIN / 'src/Entreprise').glob('*.php'):
    text = path.read_text(encoding='utf-8')
    assert 'declare(strict_types=1);' in text and 'namespace Imagine\\Pilotage\\Entreprise;' in text
    assert not re.search(r'\b(?:curl_\w+|file_get_contents|fopen|fsockopen|stream_socket_client|dns_get_record|'
                         r'gethostbyname|exec|shell_exec|system|passthru)\s*\(', text)
    assert not re.search(r'\$_(?:SERVER|GET|POST|REQUEST)|https?://', text)

notes = (ROOT / 'production/C-02/notes.md').read_text(encoding='utf-8')
recipe = (OUT / 'rapport.md').read_text(encoding='utf-8')
report = REPORT.read_text(encoding='utf-8')
marker = (ROOT / 'production/C-02/PRET').read_text(encoding='utf-8')
assert 'Décision 8 reste ouverte' in notes and 'non vérifiées' in notes
assert 'Aucune recherche Web' in notes and 'Numéros étrangers' in notes
for term in ['BCE', 'VIES', 'authentification', 'quotas', 'licence', 'coût']:
    assert term in notes
assert 'R-06 complet non exécuté' in recipe and '191' in recipe and '20 021' in recipe
assert '41 tests / 19 560' in report and '191 tests / 20 021' in report
assert 'GO' in marker and REPORT.relative_to(ROOT).as_posix() in marker
assert not (ROOT / 'production/C-02/GO.md').exists()

records = [REPORT, PLUGIN / 'README.md', PLUGIN / 'phpunit.xml']
for base in ['production/C-02', 'wp/tests/entreprise-runner',
             'wp/plugins/imagine-pilotage/src/Entreprise', 'wp/plugins/imagine-pilotage/tests/Entreprise']:
    records += [p for p in (ROOT / base).rglob('*') if p.is_file()]
excluded = {'artifact-verification.json', 'fichiers-livres.json', 'runner-state.json'}
assert not any('__pycache__' in p.parts or p.suffix == '.pyc' for p in records)
manifest = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(set(records)) if p.name not in excluded}
manifest_path = OUT / 'fichiers-livres.json'
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
result = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'status': 'VERIFIED_LOCAL', 'verification_kind': 'deterministic artifact check after final writes',
          'suites': counts, 'total': total, 'protected_initial_files': len(before),
          'protected_unchanged_nonshared_files': len(before) - len(shared),
          'protected_inventory_and_hashes_unchanged': True, 'shared_original_bytes_reconstructed': True,
          'final_tested_source_inventory_and_hashes_match': True, 'readme_php_example_executed': True,
          'application_network_calls': 'none', 'registry_research': 'none; documentation leads unverified',
          'owned_runner_removed_and_absence_read_back': True, 'independent_review': False,
          'go': False, 'deployed': False, 'decision_8': 'open',
          'manifest_files': len(manifest), 'manifest_sha256': digest(manifest_path),
          'checker_sha256': digest(pathlib.Path(__file__))}
verification_path = OUT / 'artifact-verification.json'
verification_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
assert json.loads(verification_path.read_text(encoding='utf-8')) == result
assert json.loads(manifest_path.read_text(encoding='utf-8')) == manifest
assert all(digest(ROOT / path) == expected for path, expected in manifest.items())
print(json.dumps(result, ensure_ascii=False, indent=2))
