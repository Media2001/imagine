"""Verify acquired C-01/C-04/C-02 proofs without rerunning unchanged suites."""
import hashlib
import json
import pathlib
import xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parents[3]
rows = []
for lot, directory in [('C-01', 'Numeros'), ('C-04', None), ('C-02', 'Entreprise')]:
    out = ROOT / 'production' / lot / 'tests-21nov'
    plugin = ROOT / 'wp/plugins' / ('imagine-connecteur' if lot == 'C-04' else 'imagine-pilotage')
    receipt = json.loads((out / 'final.json').read_text())
    assert all(receipt[k] == 0 for k in ('exit_code', 'psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code'))
    paths = {p.relative_to(plugin).as_posix() for base in (['src/' + directory, 'tests/' + directory] if directory else ['src', 'tests', 'examples'])
             for p in (plugin / base).rglob('*.php')}
    paths |= {'composer.json', 'composer.lock', 'phpunit.xml'}
    for rel in paths:
        assert hashlib.sha256((plugin / rel).read_bytes()).hexdigest() == receipt['source_sha256'][rel], (lot, rel)
    root = ET.parse(out / 'final.xml').getroot()
    assert not any(list(root.iter(tag)) for tag in ['failure', 'error', 'skipped'])
    suite = next(s for s in root.iter('testsuite') if s.get('name') == directory) if directory else root
    cases = list(suite.iter('testcase'))
    assert json.loads((out / 'cleanup.json').read_text())['owned_runner_removed']
    assert not (out / 'runner-state.json').exists()
    rows.append({'lot': lot, 'unchanged_scoped_sources': len(paths), 'tests': len(cases),
                 'assertions': sum(int(c.get('assertions', 0)) for c in cases), 'status': 'PASS'})
# Shared README evolved under the C-03 correction; validate its latest tested snapshot instead.
pilotage = ROOT / 'wp/plugins/imagine-pilotage'
c03 = json.loads((ROOT / 'production/C-03/tests-21nov/final.json').read_text())
assert hashlib.sha256((pilotage / 'README.md').read_bytes()).hexdigest() == c03['source_sha256']['README.md']
composition = json.loads((ROOT / 'production/C-04/tests-21nov/composition.json').read_text())
for name, digest in composition['C02_container_sources_match_checkout'].items():
    assert hashlib.sha256((pilotage / 'src/Entreprise' / name).read_bytes()).hexdigest() == digest
result = {'status': 'PASS', 'lots': rows, 'no_test_rerun': True,
          'shared_README_currently_covered_by': 'C-03/tests-21nov/final.json', 'C04_real_C02_composition_unchanged': True}
(ROOT / 'files/rapports/2026-11-21-preuves-acquises.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
