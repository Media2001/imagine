"""Verify scoped current receipts, excluding unrelated lots."""
import hashlib
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[3]
lot = sys.argv[1]
OUT = ROOT / 'production' / lot / 'tests-21nov'
plugin = ROOT / 'wp/plugins' / ('imagine-connecteur' if lot == 'C-04' else 'imagine-pilotage')
r = json.loads((OUT / 'final.json').read_text())
assert all(r[k] == 0 for k in ('exit_code', 'psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code'))
assert all(r[k] for k in ('network_disconnected', 'no_mounts', 'no_ports', 'container_source_verified'))
assert r['processes_before_suite'] == ['sleep']
scopes = {'C-03': 'Robots', 'C-01': 'Numeros', 'C-02': 'Entreprise'}
name = scopes.get(lot)
shared = {'README.md', 'phpunit.xml', 'composer.json', 'composer.lock'}
if lot == 'C-03':
    shared.add('config/robots.php')
paths = {p.relative_to(plugin).as_posix() for base in (['src/' + name, 'tests/' + name] if name else ['src', 'tests', 'examples'])
         for p in (plugin / base).rglob('*.php')} | shared
manifest = {}
for rel in sorted(paths):
    digest = hashlib.sha256((plugin / rel).read_bytes()).hexdigest()
    assert r['source_sha256'][rel] == digest, 'Source drift: ' + rel
    manifest[rel] = digest
root = ET.parse(OUT / 'final.xml').getroot()
assert not any(list(root.iter(tag)) for tag in ('failure', 'error', 'skipped'))
cases = list(root.iter('testcase'))
counts = {'tests': len(cases), 'assertions': sum(int(c.get('assertions', 0)) for c in cases)}
assert counts['tests']
assert json.loads((OUT / 'cleanup.json').read_text())['owned_runner_removed']
assert not (OUT / 'runner-state.json').exists()
result = {'status': 'PASS', 'lot': lot, 'scope': name or 'connecteur', 'suite_complete': counts, 'sha256': manifest}
(OUT / 'artifact-verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({'status': 'PASS', 'lot': lot, **counts}))
