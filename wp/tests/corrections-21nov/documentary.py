"""Offline A-00 documentary suite, run in an unmounted disposable container."""
import datetime
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'production/A-00/tests-21nov'
OUT.mkdir(parents=True, exist_ok=True)
files = ['couverture-extensions.md', 'sources-officielles.json', 'registre-citations.json']
payload = {name: (ROOT / 'production/A-00' / name).read_text(encoding='utf-8') for name in files}
code = r'''
import datetime, json, re, urllib.parse
p = PAYLOAD
text = p['couverture-extensions.md']
sources = json.loads(p['sources-officielles.json'])['sources']
register = json.loads(p['registre-citations.json'])['sources']
checks = []
def check(name, value):
    checks.append({'name': name, 'pass': bool(value)})
check('19 sections in order', re.findall(r'^## (\d+)\.', text, re.M) == list(map(str, range(1,20))))
check('19 summary rows', re.findall(r'^\| (\d+) \|', text, re.M) == list(map(str, range(1,20))))
check('38 sources contiguous', [s['id'] for s in sources] == list(range(1,39)))
check('register same IDs', [s['id'] for s in register] == list(range(1,39)))
for source, record in zip(sources, register):
    sid = source['id']
    check(f'source {sid} official domain', urllib.parse.urlparse(source['url']).hostname in {
        'woocommerce.com', 'docs.stripe.com', 'rankmath.com', 'docs.nexcess.com', 'developers.google.com'})
    check(f'source {sid} historical retrieval date', source['retrieved_at'].startswith('2026-11-20'))
    check(f'source {sid} URL in delivered text', source['url'].rstrip('/') in text)
    check(f'source {sid} quote register agrees', source['extraits_exacts'] == [q['text'] for q in record['quotes']])
    check(f'source {sid} at least one excerpt cited', any(q in text for q in source['extraits_exacts']))
    for i, quote in enumerate(source['extraits_exacts']):
        check(f'source {sid} archived excerpt {i} nonempty', isinstance(quote, str) and bool(quote.strip()))
for section in re.split(r'^## \d+\.', text, flags=re.M)[1:20]:
    check('section has source reference', re.search(r'\[\d+\]', section) is not None)
for word in ['Divergence brief / cahier', 'Attribution via inscription gratuite : doute',
             'cellules et en-têtes', 'quatre numéros réguliers par année',
             'Note d\'articulation pour besoins 4, 6 et 15',
             'user-agent seul insuffisant selon le §4.4', 'sans import CSV des abonnés en ligne',
             'Proposition à relire', 'aucune mise en œuvre']:
    check('correction ' + word, word in text)
check('old attribution removed', 'user-agent seul interdit par la doctrine' not in text)
check('unproven discovery removed', 'et une attribution via inscription gratuite ;' not in text)
start = datetime.date(2027,2,20)
end = datetime.date(2028,2,20)
dates = [start] + [datetime.date(y,m,10) for y in [2027,2028] for m in [1,4,7,10]
                  if start < datetime.date(y,m,10) < end]
check('synthetic counterexample five payments', len(dates) == 5)
result = {'status': 'PASS' if all(c['pass'] for c in checks) else 'FAIL',
          'checks': checks, 'passed': sum(c['pass'] for c in checks), 'total': len(checks),
          'failed': sum(not c['pass'] for c in checks), 'functional_extension_tests': 0,
          'scope': 'offline consistency with archived excerpts, not independent source retrieval',
          'counterexample_dates': [d.isoformat() for d in dates]}
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(0 if result['status'] == 'PASS' else 1)
'''.replace('p = PAYLOAD', 'p = ' + repr(payload))
command = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '-i',
           '--name', 'imagine-a00-doc-21nov', '--label', 'org.imagine.a00-documentary=true',
           '--network', 'none', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
           '--memory', '256m', '--pids-limit', '64', '--entrypoint', 'python3',
           'imagine-staging-e2e-public:644662e9cc4f', '-']
proc = subprocess.run(command, input=code.encode(), capture_output=True, timeout=120)
(OUT / 'documentary.log').write_bytes(proc.stdout + proc.stderr)
if proc.returncode:
    print(proc.stdout.decode(errors='replace'), proc.stderr.decode(errors='replace'))
    raise SystemExit(proc.returncode)
result = json.loads(proc.stdout)
result['input_sha256'] = {f: hashlib.sha256((ROOT / 'production/A-00' / f).read_bytes()).hexdigest() for f in files}
result['time_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
inspect = subprocess.run(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'inspect', 'imagine-a00-doc-21nov'], capture_output=True)
assert inspect.returncode != 0
result['cleanup_verified'] = True
(OUT / 'documentary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k != 'checks'}, ensure_ascii=False, indent=2))
