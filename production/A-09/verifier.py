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

def owned(name):
    return name.startswith(('production/A-09/','wp/tests/a09/','wp/outils/bascule/a09/')) or name in {'wp/outils/bascule/tester-redirections','wp/outils/bascule/tester-redirections.md','wp/outils/bascule/plan-redirections.exemple.csv'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf8'))


def verify_hashes(values):
    for name, expected in values.items():
        require(owned(name), 'outside A09 manifest: '+name)
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
    verify_hashes({n:h for n,h in read_json(packet/'sources.json').items() if owned(n)})
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
    expected = {'conforme', 'mauvais-code', 'mauvaise-cible', 'cible-404', 'cible-503', 'timeout', 'source-200', 'sans-location', 'double-location', 'chaines-boucles', 'externes', 'variantes', 'csv-sur', 'query-encoded', 'empty-query-location'}
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
    encoded = reports['query-encoded']
    require(encoded['nonconformes'] == 0 and encoded['requests'] == 6, 'R1 query conformity')
    query_events = read_json(packet/'query-encoded-cli.json')['events']
    exact = ['/ancien?u=%2Fpage', '/nouveau0?u=%2Fpage', '/x?q=deux%20mots', '/nouveau1?q=deux%20mots', '/trois?u=%2fpage&x=%61%5c%3f%23', '/nouveau2?u=%2fpage&x=%61%5c%3f%23']
    require([e['path'] for e in query_events] == exact, 'R1 changed query transport')
    for name, code in [('query-path-refusal', 'A09_PLAN_URL'), ('query-control-refusal', 'A09_PLAN_URL'), ('empty-query-conflict', 'A09_PLAN_EMPTY_QUERY'), ('empty-query-target', 'A09_PLAN_EMPTY_QUERY'), ('non-bmp-source', 'A09_PLAN_URL'), ('non-bmp-target', 'A09_PLAN_URL')]:
        receipt = read_json(packet/(name+'-cli.json'))
        require(receipt['exit'] == 2 and receipt['events'] == [] and code in receipt['stderr'] and 'mauvaise_cible' not in receipt['stdout'], 'correction preflight failure: '+name)
        require(not (packet/name/'rapport.json').exists(), 'refused plan produced a verdict: '+name)
    empty = reports['empty-query-location']['rows'][0]
    require(empty['issues'] == ['redirection_invalide'] and reports['empty-query-location']['requests'] == 1, 'empty observed query silently followed')
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
        verify_hashes({n:h for n,h in read_json(LOT/'historique-corrections.json').items() if owned(n)})
        baseline = read_json(LOT/'baseline.json')
        verify_hashes({n:h for n,h in baseline.items() if owned(n)})
        prior = read_json(LOT/'avant-corrections/baseline.json')
        transition = read_json(LOT/'transition-corrections.json')
        allowed = {'wp/tests/a02-audit/README.md', 'wp/outils/bascule/a08/sequence.py', 'wp/outils/bascule/repetition.md', 'wp/tests/a08/inside.py', 'wp/tests/a08/test_sequence.py'}
        require(set(transition['drift']) == allowed and all(prior[n] == d['old'] and baseline[n] == d['new'] for n,d in transition['drift'].items()), 'baseline transition not exact')
        require(all(n in baseline and (n in allowed or baseline[n] == h) for n,h in prior.items()), 'unapproved baseline refresh')
        extra = (b'Complement A-10 : php wp/outils/bascule/inventorier-codes --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/codes-date\n'
                 b'Lecture seule ; sortie soeur du rapport A-02, hors site et depot ; noms de codes autorises, emails comptes uniquement ; rejeu : python wp/tests/a10/run.py\n')
        data = (ROOT/'wp/tests/a02-audit/README.md').read_bytes()
        require(extra in data, 'shared README A10 two-line contract missing')
        prep = read_json(LOT/'preparer-image.json')
        require(prep['exit_code'] == 0 and prep['script_unchanged'] is True and prep['log_sha256'] == sha(LOT/'preparer-image.log'), 'preparation receipt not genuine/current')
        prep_log = (LOT/'preparer-image.log').read_text(encoding='utf8', errors='replace')
        require('T01 IMAGE READY' in prep_log and 'PREPARATION T01 : image verifiee sha256:' in prep_log, 'prepared image not verified')
        with (ROOT/'wp/outils/bascule/plan-redirections.exemple.csv').open(encoding='utf8', newline='') as stream:
            example = list(csv.DictReader(stream))
        require(len(example) == 3 and all(re.search(r'ficti(?:f|ve)', r['ancienne']) and re.search(r'ficti(?:f|ve)', r['cible']) for r in example), 'example not exactly three fictitious rows')
        for name in manifest['sources']:
            if name.endswith('.py') or name.endswith('/tester-redirections'):
                compile((ROOT/name).read_text(encoding='utf8'), name, 'exec')
        if args.replay: assert_no_owned_runner()
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
            verify_hashes({n:h for n,h in baseline.items() if owned(n)})
        if args.replay: assert_no_owned_runner()
        print(json.dumps({'exit_code': 0, 'scope': 'A09 dedicated Python/real HTTP archived suite; no Docker by default; not a fresh execution', 'proof': result, 'replay': replay, 'protected_sources': sum(owned(n) for n in baseline), 'manifest_sha256': sha(LOT/'manifeste.json'), 'cleanup': 'archived exact-owned cleanup receipt; live readback only with --replay', 'production_authorized': False}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({'exit_code': 1, 'error': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    sys.exit(main())
