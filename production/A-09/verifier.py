"""A09 parent verifier. Read-only by default; --replay owns one fresh HTTP runner.
No PHP on host, no staging API, no Git, no dependency installation.
"""
import argparse
import csv
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import urlsplit
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
LOT = ROOT/'production/A-09'
LABEL = 'org.imagine.a09-redirections'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf8'))


def verify_hashes(values):
    for name, expected in values.items():
        path = ROOT/name
        require(not pathlib.PurePosixPath(name).is_absolute() and '..' not in pathlib.PurePosixPath(name).parts, 'unsafe manifest path')
        require(path.is_file() and not path.is_symlink() and sha(path) == expected, 'hash drift: '+name)


def docker(args):
    command = (['wsl.exe', '-d', 'Ubuntu', '--', 'docker'] if sys.platform == 'win32' else ['docker'])+args
    return subprocess.run(command, capture_output=True, text=True, encoding='utf8', errors='replace', timeout=40)


def assert_no_owned_runner():
    result = docker(['ps', '-aq', '--filter', 'label='+LABEL])
    require(result.returncode == 0 and not result.stdout.strip(), 'Docker unavailable or A09 runner still present: '+result.stdout+result.stderr)


def verify_isolation(info, name):
    h = info['HostConfig']
    require(info['Name'] == '/'+name and info['Config']['Labels'].get(LABEL) == name, 'ownership mismatch')
    require(h['NetworkMode'] == 'none' and not h['Privileged'] and not h.get('Binds') and not info['Mounts'], 'runner network/mount mismatch')
    require(not h.get('PortBindings') and not info['Config'].get('ExposedPorts') and not info['NetworkSettings'].get('Ports'), 'runner exposed a port')
    require(not (set(info['NetworkSettings'].get('Networks', {}))-{'none'}), 'runner external network')
    require('ALL' in h['CapDrop'] and any(s.startswith('no-new-privileges') for s in h['SecurityOpt']), 'runner security mismatch')


def verify_packet(packet, expected_tests):
    require(packet.resolve().is_relative_to((LOT/'preuves').resolve()), 'proof outside A09')
    runner = read_json(packet/'runner.json')
    require(runner['exit_code'] == 0 and all(c['ok'] for c in runner['checks']), 'runner not green')
    checks = {c['check'] for c in runner['checks']}
    require(checks == {'isolation_before', 'tests', 'isolation_after', 'cleanup_exact_owned', 'sources_unchanged'}, 'runner checks incomplete')
    verify_hashes(read_json(packet/'sources.json'))
    for phase in ['before', 'after']:
        verify_isolation(read_json(packet/('inspect-'+phase+'.json')), runner['container'])
    log = (packet/'tests.log').read_text(encoding='utf8')
    tests = re.findall(r'^(test_\w+) \([^\n]+\) \.\.\. ok$', log, re.M)
    count = re.search(r'^Ran (\d+) tests? in ', log, re.M)
    require(count and int(count[1]) == expected_tests == len(tests) and log.rstrip().endswith('OK'), 'test discovery/count failure')
    require(len(set(tests)) == len(tests), 'duplicate test names')
    reports = {}
    for path in packet.glob('*/rapport.json'):
        data = read_json(path)
        reports[path.parent.name] = data
        require(data['schema'] == 'imagine-a09-report-v1' and data['read_only'] is True, 'report schema')
        require(data['total'] == len(data['rows']) and data['nonconformes'] == sum(bool(r['issues']) for r in data['rows']), 'report totals')
        with (path.parent/'nonconformes.csv').open(encoding='utf-8-sig', newline='') as stream:
            bad = list(csv.DictReader(stream))
        require(len(bad) == data['nonconformes'], 'CSV total')
        require('Code observé' in (path.parent/'rapport.md').read_text(encoding='utf8'), 'human report missing diagnostics')
        receipt = read_json(packet/(path.parent.name+'-cli.json'))
        require(receipt['exit'] == int(bool(bad)) and receipt['site_unchanged'] is True, 'CLI verdict or site drift')
        base = urlsplit(data['base_url'])
        require(data['requests'] == len(receipt['events']), 'request counter mismatch')
        require(all(e['method'] == 'GET' and e['port'] == base.port for e in receipt['events']), 'other origin/method visited')
        for row in data['rows']:
            require(all((urlsplit(t['url']).scheme, urlsplit(t['url']).netloc) == (base.scheme, base.netloc) for t in row['trace']), 'trace left origin')
        require(all(b['at']-a['at'] >= 0.08 for a, b in zip(receipt['events'], receipt['events'][1:])), 'rate not bounded')
    expected = {'conforme', 'mauvais-code', 'mauvaise-cible', 'cible-404', 'cible-503', 'timeout', 'source-200', 'sans-location', 'double-location', 'chaines-boucles', 'externes', 'variantes', 'csv-sur'}
    require(set(reports) == expected, 'missing HTTP acceptance reports')
    conform = reports['conforme']['rows'][0]
    require(reports['conforme']['nonconformes'] == 0 and conform['hops'] == 1 and conform['observed_code'] == 301 and conform['final_status'] == 200, 'conformity proof')
    for name, issue in [('mauvais-code', 'mauvais_code'), ('mauvaise-cible', 'mauvaise_cible'), ('cible-404', 'cible_non_200'), ('cible-503', 'cible_non_200'), ('timeout', 'delai_depasse'), ('source-200', 'mauvais_code'), ('sans-location', 'redirection_invalide'), ('double-location', 'redirection_invalide')]:
        require(issue in reports[name]['rows'][0]['issues'] and reports[name]['nonconformes'] == 1 and reports[name]['rows'][1]['issues'] == [], 'HTTP defect/remainder not proven: '+name)
    chain = reports['chaines-boucles']['rows']
    require('chaine' in chain[0]['issues'] and chain[0]['hops'] == 2 and chain[0]['final_status'] == 200, 'chain not proven')
    require('boucle' in chain[1]['issues'] and 'boucle' in chain[2]['issues'] and 'limite_sauts' in chain[3]['issues'], 'loop or bound not proven')
    require(all('cible_externe' in r['issues'] for r in reports['externes']['rows']) and 'chaine' in reports['externes']['rows'][1]['issues'], 'external first/later not proven')
    require(read_json(packet/'external-trap.json')['received_requests'] == [], 'other-origin trap visited')
    invalid = read_json(packet/'invalid-plan-no-request.json')
    require(len(invalid['cases']) == 5 and invalid['requests'] == [], 'invalid plan emitted request')
    for name in invalid['cases']:
        data = read_json(packet/(name+'-cli.json'))
        require(data['exit'] == 2 and data['events'] == [] and data['site_unchanged'] is True, 'invalid plan preflight failed')
    variants = reports['variantes']
    require(variants['nonconformes'] == 0 and {r['observed_code'] for r in variants['rows']} == {301, 302, 303, 307, 308}, 'supported codes not proven')
    for path in packet.glob('*-cli.json'):
        data = read_json(path)
        require(data['site_unchanged'] is True and 'Traceback' not in data['stderr'], 'HTTP receipt failure: '+path.name)
        if data['exit'] == 2:
            require(data['events'] == [], 'preflight emitted HTTP: '+path.name)
    return {'packet': packet.name, 'tests': len(tests), 'http_reports': len(reports), 'runner': runner['container'], 'requests': sum(r['requests'] for r in reports.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', action='store_true', help='fresh owned disconnected runner; writes only A09 proof directory')
    parser.add_argument('--pre-pret', action='store_true', help='verify before PRET is created')
    args = parser.parse_args()
    try:
        manifest = read_json(LOT/'manifeste.json')
        require(manifest['schema'] == 'imagine-a09-delivery-v1' and manifest['production_authorized'] is False, 'manifest schema/scope')
        verify_hashes(manifest['sources'])
        verify_hashes(manifest['evidence'])
        baseline = read_json(LOT/'baseline.json')
        verify_hashes(baseline)
        prep = read_json(LOT/'preparer-image.json')
        require(prep['exit_code'] == 0 and prep['script_unchanged'] is True and prep['script_sha256'] == sha(ROOT/'wp/tests/preparer-image.ps1') and prep['log_sha256'] == sha(LOT/'preparer-image.log'), 'preparation receipt not genuine/current')
        prep_log = (LOT/'preparer-image.log').read_text(encoding='utf8', errors='replace')
        require('T01 IMAGE READY' in prep_log and 'PREPARATION T01 : image verifiee sha256:' in prep_log, 'prepared image not verified')
        with (ROOT/'wp/outils/bascule/plan-redirections.exemple.csv').open(encoding='utf8', newline='') as stream:
            example = list(csv.DictReader(stream))
        require(len(example) == 3 and all(re.search(r'ficti(?:f|ve)', r['ancienne']) and re.search(r'ficti(?:f|ve)', r['cible']) for r in example), 'example not exactly three fictitious rows')
        for name in manifest['sources']:
            if name.endswith('.py') or name.endswith('/tester-redirections'):
                compile((ROOT/name).read_text(encoding='utf8'), name, 'exec')
        assert_no_owned_runner()
        result = verify_packet(LOT/'preuves'/manifest['proof'], manifest['tests'])
        for cycle in manifest['tdd_cycles']:
            red, green = [read_json(LOT/'preuves'/cycle[k]/'runner.json') for k in ['red', 'green']]
            require(red['exit_code'] != 0 and green['exit_code'] == 0, 'TDD receipt mismatch')
            require(any(c['check'] == 'tests' and c['ok'] is False for c in red['checks']), 'RED did not execute tests')
            require(any(c['check'] == 'cleanup_exact_owned' and c['ok'] is True for c in red['checks']), 'RED cleanup missing')
        if not args.pre_pret:
            text = (LOT/'PRET').read_text(encoding='utf8')
            require(sha(LOT/'manifeste.json') in text and manifest['proof'] in text, 'PRET not bound to manifest/proof')
        replay = None
        if args.replay:
            command = [sys.executable, '-B', str(ROOT/'wp/tests/a09/run.py')]
            run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf8', errors='replace', timeout=400)
            require(run.returncode == 0, 'fresh replay failed: '+run.stdout+run.stderr)
            replay = verify_packet(pathlib.Path(json.loads(run.stdout)['output']), manifest['tests'])
            verify_hashes(manifest['sources'])
            verify_hashes(baseline)
        assert_no_owned_runner()
        print(json.dumps({'exit_code': 0, 'scope': 'A09 dedicated Python/real HTTP suite; not a global T01 replay or staging acceptance', 'proof': result, 'replay': replay, 'protected_sources': len(baseline), 'manifest_sha256': sha(LOT/'manifeste.json'), 'cleanup': 'no A09-owned runner', 'production_authorized': False}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({'exit_code': 1, 'error': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    sys.exit(main())
