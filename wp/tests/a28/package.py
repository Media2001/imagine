"""A28 package assembly only. Never reseals another lot or writes orchestration."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'production/A-28'
PACKET = BASE / 'preuves/final'
SCRATCH = Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a28-work')
spec = importlib.util.spec_from_file_location('a28_package_verifier', BASE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
OWN_CHANGED = {'wp/outils/staging/lib.php', 'wp/outils/staging/command.php', 'wp/outils/staging/form-policy.json',
               'wp/outils/staging-court/inside.py', 'wp/outils/staging-court/run.py',
               'wp/outils/staging-court/table_policy.py', 'wp/outils/staging-court/README.md'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding='utf-8')


def setup():
    PACKET.mkdir(parents=True, exist_ok=False)
    before = SCRATCH / 'baseline-native-5'
    v.runner_contract(before, ROOT, baseline=True)
    v.native_contract(v.load(before / 'native.json'), baseline=True)
    shutil.copytree(before, PACKET / 'before')
    original = (SCRATCH / 'original/wp/outils/staging-court/README.md').read_bytes()
    lines = (BASE / 'readme-ajout.txt').read_bytes()
    current = (ROOT / 'wp/outils/staging-court/README.md').read_bytes()
    assert len(lines.splitlines(keepends=True)) == 3 and current == original + lines
    blocks = re.findall(rb'```[^\n]*\n.*?```', original, re.S)
    contract = {'lines': [line.decode('utf-8') for line in lines.splitlines(keepends=True)],
                'commands': [b.decode('utf-8') for b in blocks], 'baseline_readme_sha256': hashlib.sha256(original).hexdigest()}
    v.readme_contract(current, contract['lines'], contract['commands'])
    write(BASE / 'readme-contract.json', contract)
    sources = []
    for filename, url in [
        ('flamingo-readme.txt', 'https://raw.githubusercontent.com/rocklobster-in/flamingo/master/readme.txt'),
        ('flamingo-inbound.txt', 'https://raw.githubusercontent.com/rocklobster-in/flamingo/master/includes/class-inbound-message.php'),
        ('flamingo-contact.txt', 'https://raw.githubusercontent.com/rocklobster-in/flamingo/master/includes/class-contact.php'),
        ('fluent.html', 'https://developers.fluentforms.com/database/'),
    ]:
        path = SCRATCH / filename
        sources.append({'url': url, 'sha256': digest(path), 'bytes': path.stat().st_size,
                        'retrieved_utc': datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).isoformat(),
                        'scratch_handle': str(path)})
    write(BASE / 'official-sources.json', {'sources': sources, 'standard': 'standard.md',
        'cf7_direct_page': 'WAF interstitial rejected; official publisher README used instead'})
    red = []
    for folder, expected in [('red-unit', 1), ('red-native-boundary', 1), ('red-nonform-regression', 1), ('green-unit', 0)]:
        path = SCRATCH / folder
        runner = v.load(path / 'runner.json')
        red.append({'handle': str(path / 'runner.json'), 'sha256': digest(path / 'runner.json'),
                    'observed_command_exits': [r['exit'] for r in runner['commands']], 'expected_exit': expected,
                    'status': runner['status'], 'cleanup': runner['cleanup']})
    for key in ('red-policy', 'red-verifier'):
        path = SCRATCH / (key + '.stderr.log')
        red.append({'handle': str(path), 'sha256': digest(path), 'contains_real_assertion_failure': b'AssertionError' in path.read_bytes()})
    write(PACKET / 'red-green.json', {'experiments_kept_outside_repository': True, 'receipts': red,
        'final_green_and_real_mutation_witnesses': ['native/utf8/native.json', 'native/cp1252/native.json'], 'before_correction': 'before/native.json'})


def scope():
    baseline = v.load(SCRATCH / 'baseline.json')
    changed = sorted(rel for rel, old in baseline.items() if not (ROOT / rel).is_file() or digest(ROOT / rel) != old)
    forbidden = [rel for rel in changed if rel not in OWN_CHANGED]
    concurrent = []
    # The parent's A29 append to its own shared audit README is a concurrent-owner change, not A28.
    shared = 'wp/tests/a02-audit/README.md'
    if shared in forbidden:
        body = (ROOT / shared).read_bytes()
        delta_path = ROOT / 'production/A-29/readme-ajout.txt'
        if delta_path.is_file():
            delta = delta_path.read_bytes()
            if delta and body.endswith(delta) and hashlib.sha256(body[:-len(delta)]).hexdigest() == baseline[shared]:
                concurrent.append({'file': shared, 'owner': 'parent/A29', 'qualified_exact_append_sha256': hashlib.sha256(delta).hexdigest()})
                forbidden.remove(shared)
    added = []
    for area in ['wp/outils', 'wp/tests', 'production/A-23', 'production/A-24', 'production/A-25', 'production/A-26', 'production/A-27']:
        for p in (ROOT / area).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc' and not p.is_symlink():
                rel = p.relative_to(ROOT).as_posix()
                if rel not in baseline and rel not in OWN_CHANGED and not rel.startswith(('wp/tests/a28/', 'wp/tests/a29/', 'wp/outils/bascule/a29/')):
                    added.append(rel)
    original = (SCRATCH / 'original/wp/outils/staging-court/README.md').read_bytes()
    lines = (BASE / 'readme-ajout.txt').read_bytes()
    contract = v.load(BASE / 'readme-contract.json')
    body = (ROOT / 'wp/outils/staging-court/README.md').read_bytes()
    ced_same = all((ROOT / rel).read_bytes() == (SCRATCH / 'original' / rel).read_bytes()
                   for rel in ('wp/outils/staging/README.md', 'production/A-01/notes.md'))
    result = {'baseline_files': len(baseline), 'changed_owned_files': sorted(set(changed) & OWN_CHANGED),
        'out_of_scope_changed': forbidden, 'out_of_scope_added': sorted(added), 'concurrent_owner_changes': concurrent,
        'readme_exact_three_lines': body == original + lines and len(lines.splitlines()) == 3,
        'ced_commands_unchanged': ced_same and re.findall(rb'```[^\n]*\n.*?```', original, re.S) == re.findall(rb'```[^\n]*\n.*?```', body, re.S),
        'common_guardian_unchanged': digest(ROOT / 'wp/outils/bascule/stream_guard.py') == baseline['wp/outils/bascule/stream_guard.py'],
        'common_guardian_sha256': digest(ROOT / 'wp/outils/bascule/stream_guard.py'),
        'old_packets_A23_A27_preserved': all(digest(ROOT / rel) == old for rel, old in baseline.items() if rel.startswith(tuple('production/A-' + str(n) + '/' for n in range(23, 28)))),
        'measured_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    assert not forbidden and not added and result['ced_commands_unchanged'] and result['readme_exact_three_lines']
    write(PACKET / 'scope.json', result)


def integration_review():
    rows = []
    for n in range(23, 28):
        relative = f'wp/tests/a{n}/verify.py' if n < 26 else f'production/A-{n}/verify.py'
        argv = [sys.executable, '-B', str(ROOT / relative)]
        p = subprocess.run(argv, cwd=ROOT, env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'},
                           capture_output=True, timeout=120)
        for stream, raw in [('stdout', p.stdout), ('stderr', p.stderr)]:
            (PACKET / ('historical-a' + str(n) + '.' + stream + '.log')).write_bytes(raw)
        row = {'lot': 'A-' + str(n), 'command': argv, 'exit': p.returncode,
               'historical_packet_untouched': True, 'stdout_sha256': hashlib.sha256(p.stdout).hexdigest(),
               'stderr_sha256': hashlib.sha256(p.stderr).hexdigest()}
        try:
            data = json.loads(p.stdout)
            row['failed_checks'] = [c['check'] for c in data.get('checks', []) if c.get('status') != 'PASS']
            row['code'] = data.get('code')
        except ValueError:
            row['code'] = 'NON_JSON_HISTORICAL_VERIFIER'
        rows.append(row)
    write(PACKET / 'dependency-invalidations.json', {'read_only_observations': rows,
        'import_sources': {rel: digest(ROOT / rel) for rel in sorted(OWN_CHANGED) if (ROOT / rel).is_file()},
        'decision': 'No reseal. Parent owns harness dependency update, native replay and new gates, particularly A25 old clear-message expectation.'})


def seal():
    assert not (BASE / 'manifest.json').exists(), 'A28_ALREADY_SEALED'
    v.runner_contract(PACKET / 'before', ROOT, baseline=True)
    v.native_contract(v.load(PACKET / 'before/native.json'), baseline=True)
    v.matrix_contract(PACKET / 'native', ROOT, v.load(PACKET / 'before/runner.json')['source_manifest'])
    v.gates_contract(PACKET / 'gates', ROOT)
    review = v.load(PACKET / 'dependency-invalidations.json')
    assert all(digest(ROOT / rel) == old for rel, old in review['import_sources'].items())
    scope()
    write(BASE / 'manifest.json', {'lot': 'A-28', 'packet': v.PACKET.as_posix(), 'files': v.inventory(ROOT)})
    print(json.dumps(v.verify()))


def main():
    parser = argparse.ArgumentParser()
    phase = parser.add_mutually_exclusive_group(required=True)
    phase.add_argument('--setup', action='store_true')
    phase.add_argument('--seal', action='store_true')
    phase.add_argument('--review', action='store_true')
    args = parser.parse_args()
    if args.setup:
        setup()
    elif args.review:
        integration_review()
    else:
        seal()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
