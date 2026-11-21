"""Seal/check C-06 evidence after the final PHP run and owned cleanup."""
import ast
import datetime
import hashlib
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
from run import ROOT, bench, shared_inventory


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_files():
    files = []
    for directory in [bench.PLUGIN / 'src/Acces', bench.PLUGIN / 'tests/Acces',
                      ROOT / 'wp/tests/acces-runner', bench.OUT]:
        files += [p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                  and p.name != 'artifact-verification.json' and p.name != 'runner-state.json']
    files += [ROOT / 'production/C-06' / name for name in ['notes.md', 'sources-officielles.json', 'PRET']]
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(set(files))}


def verify():
    receipt = json.loads((bench.OUT / 'final.json').read_text(encoding='utf-8'))
    for key in ['exit_code', 'psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code']:
        assert receipt[key] == 0, key
    for key in ['network_disconnected', 'no_mounts', 'no_ports', 'container_source_verified',
                'shared_sources_unchanged']:
        assert receipt[key] is True, key
    assert receipt['processes_before_suite'] == ['sleep']
    assert receipt['wrapper_sha256'] == digest(ROOT / 'wp/tests/acces-runner/run.py')
    assert receipt['runner_sha256'] == digest(ROOT / 'wp/tests/numeros-runner/run.py')
    assert json.loads((bench.OUT / 'shared-before.json').read_text(encoding='utf-8')) == shared_inventory()
    for relative, expected in receipt['source_sha256'].items():
        assert digest(bench.PLUGIN / relative) == expected, relative
    owned = {p.relative_to(bench.PLUGIN).as_posix()
             for directory in ['src/Acces', 'tests/Acces']
             for p in (bench.PLUGIN / directory).rglob('*') if p.is_file()}
    recorded = {p for p in receipt['source_sha256'] if p.startswith(('src/Acces/', 'tests/Acces/'))}
    assert owned == recorded
    xml = ET.parse(bench.OUT / 'final.xml').getroot()
    top = xml.find('testsuite')
    suites = list(top.findall('testsuite'))
    assert {s.attrib['name'] for s in suites} == {'Acces', 'Numeros', 'Robots', 'Entreprise'}
    counts = {}
    for suite in suites:
        attributes = suite.attrib
        for key in ['errors', 'failures', 'skipped']:
            assert int(attributes[key]) == 0, attributes
        assert len(suite.findall('.//testcase')) == int(attributes['tests']) > 0
        counts[attributes['name']] = {key: int(attributes[key]) for key in ['tests', 'assertions']}
    for key in ['tests', 'assertions']:
        assert int(top.attrib[key]) == sum(row[key] for row in counts.values())
    assert xml.findall('.//failure') == [] and xml.findall('.//error') == []
    assert not bench.STATE.exists()
    cleanup = json.loads((bench.OUT / 'cleanup.json').read_text(encoding='utf-8'))
    assert cleanup['owned_runner_removed'] is True and cleanup['shared_sources_unchanged'] is True
    absent = bench.call(['inspect', cleanup['container']], check=False)
    text = (absent.stdout + absent.stderr).decode(errors='replace').lower()
    assert absent.returncode != 0 and ('no such object' in text or 'no such container' in text)
    preparation = json.loads((bench.OUT / 'preparation.json').read_text(encoding='utf-8'))
    assert preparation['label'] == bench.LABEL
    assert preparation['networks_after_preparation'] == {} and preparation['composer_install_exit'] == 0
    banned = re.compile(r'\b(?:time|microtime|hrtime|file_get_contents|file_put_contents|fopen|curl_exec|'
                        r'gethostbyaddr|dns_get_record|eval|exec|shell_exec|header|sleep)\s*\(|'
                        r'\$_(?:SERVER|SESSION|COOKIE|GET|POST)|\b(?:wp_|wc_)\w+\s*\(')
    for path in (bench.PLUGIN / 'src/Acces').glob('*.php'):
        code = path.read_text(encoding='utf-8')
        assert 'declare(strict_types=1);' in code
        assert 'namespace Imagine\\Pilotage\\Acces;' in code
        assert not banned.search(code), path
    for path in (ROOT / 'wp/tests/acces-runner').glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    return counts


def main():
    assert sys.argv[1:] in (['seal'], ['check'])
    counts = verify()
    target = bench.OUT / 'artifact-verification.json'
    files = current_files()
    if sys.argv[1] == 'seal':
        assert not target.exists(), 'Never overwrite an existing sealed packet'
        target.write_text(json.dumps({
            'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'status': 'PASS', 'scope': 'C-06 technical evidence only; not independent review or GO',
            'suites': counts, 'sha256': files, 'protected_shared_files': len(shared_inventory()),
            'container_absence_verified': True, 'pure_php_static_guard': True,
            'reviewer_approval': False, 'production_authorized': False
        }, indent=2), encoding='utf-8')
    sealed = json.loads(target.read_text(encoding='utf-8'))
    assert sealed['sha256'] == files, 'Post-seal artifact drift'
    assert sealed['suites'] == counts and sealed['status'] == 'PASS'
    print(json.dumps({'status': 'PASS', 'suites': counts, 'sealed_files': len(files),
                      'evidence': str(target), 'container_absent': True}, indent=2))


if __name__ == '__main__':
    main()
