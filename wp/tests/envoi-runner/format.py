"""C-07 export settings: isolated receipts, no sibling writes or parent lock ownership."""
import importlib.util
import json
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('c07_format_corrections', HERE / 'corrections.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
b = c.b
OUT = c.OUT
ROOT = c.ROOT


def owned_inventory():
    paths = []
    for directory in ['wp/plugins/imagine-pilotage/src/Envoi',
                      'wp/plugins/imagine-pilotage/tests/Envoi', 'wp/tests/envoi-runner']:
        paths += [p for p in (ROOT / directory).rglob('*') if p.is_file()]
    paths += [ROOT / 'production/C-07/notes.md', ROOT / 'production/C-07/PRET',
              ROOT / 'production/C-07/format-export-2026-11-22.md']
    return {p.relative_to(ROOT).as_posix(): c.digest(p) for p in sorted(paths) if p.is_file()}


def sync():
    name, _ = c.owned()
    data, hashes = c.runner.payload()
    b.call(['exec', name, 'rm', '-rf', '/work/src', '/work/tests'])
    b.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/work'], data)
    return hashes


def test(stage, test_filter=None):
    hashes = sync()
    args = ['php', 'vendor/bin/phpunit', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation',
            '--testsuite', 'Envoi', '--log-junit', '/tmp/c07-format.xml']
    if test_filter:
        assert test_filter.isidentifier(), 'Simple filters only across WSL'
        args += ['--filter', test_filter]
    c.command(stage, args, junit='/tmp/c07-format.xml')
    c.save(stage + '-sources.json', hashes)


def check():
    seal = json.loads((OUT / 'format-seal.json').read_text(encoding='utf-8'))
    assert seal['owned_sha256'] == owned_inventory(), 'Owned source drift'
    assert seal['c04_sha256'] == c.inventory(ROOT / 'wp/plugins/imagine-connecteur'), 'C04 drift'
    assert all(c.digest(OUT / p) == h for p, h in seal['evidence_sha256'].items()), 'Evidence drift'
    cleanup = json.loads((OUT / 'cleanup.json').read_text(encoding='utf-8'))
    result = b.call(['inspect', cleanup['container']], check=False)
    diagnostic = (result.stdout + result.stderr).decode(errors='replace')
    assert result.returncode != 0 and ('no such object' in diagnostic.lower()
                                      or 'no such container' in diagnostic.lower())
    assert not b.STATE.exists()
    counts = {}
    import xml.etree.ElementTree as ET
    for key in ['final', 'envoi-strict', 'c04-strict']:
        suite = ET.parse(OUT / (key + '.xml')).getroot().find('testsuite')
        counts[key] = {k: int(suite.attrib[k]) for k in ['tests', 'assertions', 'failures', 'errors', 'skipped']}
        assert all(counts[key][k] == 0 for k in ['failures', 'errors', 'skipped'])
        receipt = json.loads((OUT / (key + '.json')).read_text(encoding='utf-8'))
        assert receipt['exit_code'] == 0
    assert counts['c04-strict'] == {'tests': 37, 'assertions': 224, 'failures': 0, 'errors': 0, 'skipped': 0}
    final = json.loads((OUT / 'final.json').read_text(encoding='utf-8'))
    assert all(final[k] == 0 for k in ['psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code'])
    summary = {'time_utc': c.now(), 'counts': counts, 'container_absent': cleanup['container'],
               'owned_files_verified': len(seal['owned_sha256']),
               'c04_files_unchanged': len(seal['c04_sha256']),
               'evidence_files_verified': len(seal['evidence_sha256'])}
    if not (OUT / 'format-verification.json').exists():
        c.save('format-verification.json', summary)
    print('VERIFIED', json.dumps(summary))


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'prepare':
        assert not OUT.exists(), 'Fresh packet required'
        OUT.mkdir(parents=True)
        c.save('c04-before.json', c.inventory(ROOT / 'wp/plugins/imagine-connecteur'))
        c.runner.c03.prepare()
    elif action == 'test':
        test(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif action == 'strict':
        c.strict()
    elif action == 'close':
        # Ownership checks, but cleanup must remain possible after a preparation failure.
        name = json.loads(b.STATE.read_text(encoding='utf-8'))['container']
        b.info(name)
        b.call(['rm', '-f', name])
        result = b.call(['inspect', name], check=False)
        diagnostic = (result.stdout + result.stderr).decode(errors='replace')
        assert result.returncode != 0 and ('no such object' in diagnostic.lower()
                                          or 'no such container' in diagnostic.lower())
        c.save('cleanup.json', {'container': name, 'owned_runner_removed': True,
                               'inspect_exit_code': result.returncode, 'inspect_diagnostic': diagnostic})
        b.STATE.unlink()
        print('REMOVED', name, diagnostic)
    elif action == 'seal':
        assert not b.STATE.exists()
        c04 = c.inventory(ROOT / 'wp/plugins/imagine-connecteur')
        assert c04 == json.loads((OUT / 'c04-before.json').read_text(encoding='utf-8'))
        c.save('format-seal.json', {'time_utc': c.now(), 'owned_sha256': owned_inventory(), 'c04_sha256': c04,
                                  'evidence_sha256': {p.name: c.digest(p) for p in sorted(OUT.iterdir())
                                                      if p.is_file() and p.name != 'format-verification.json'}})
        check()
    elif action == 'check':
        check()
    else:
        raise SystemExit('Expected prepare, test, strict, close, seal or check')
