"""B03 : recette finale en lecture seule hors upload du seul test PHP B03."""
from pathlib import Path
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROOF = ROOT / 'production/B-03'
sys.path.insert(0, str(HERE))


def module(filename):
    spec = importlib.util.spec_from_file_location('b03_final_' + filename.replace('-', '_'), HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load(name):
    return json.loads((PROOF / name).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    work = module('b03-work.py')
    work.guard()
    # New receipt namespace: never rewrite the failed historical gate or baseline.
    run_proof = PROOF / 'reconciliation-c15' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run_proof.mkdir(parents=True, exist_ok=False)
    preservation_guard = module('b03-preservation.py')
    historical_before = load('corrections-before.json')
    linked_before = preservation_guard.links(ROOT)
    documentary_checks, c15_sources, c15_local_documents = preservation_guard.documentary(ROOT)
    current_start = {'at': datetime.now(timezone.utc).isoformat(),
                     'remote': work.wp(historical_before['snapshot_php']),
                     'local': preservation_guard.local_snapshot(ROOT)}
    (run_proof / 'current-before.json').write_text(json.dumps(current_start, indent=2), encoding='utf-8')
    semantic = module('c15-action.py')  # snapshot() only; NEVER action/reset.
    native_before = semantic.snapshot()
    work.PROOF = run_proof
    deployed = dict(load('deploy-corrections.json')['expected'])
    amendment = load('deploy-reduced-motion.json')
    assert amendment['before'] == {k: deployed[k] for k in amendment['expected']}
    assert set(amendment['expected']) == {'themes/imagine/assets/reading.css'}
    deployed.update(amendment['expected'])
    expected = {'themes/imagine/' + rel: digest(ROOT / 'wp/themes/imagine' / rel) for rel in work.FILES}
    actual = work.readback(list(expected))
    checks = {'theme_local_deploye_exact': actual == expected and all(expected[k] == v for k, v in deployed.items()),
              'depot_limite_aux_deux_assets': set(deployed) == {'themes/imagine/assets/reading.css', 'themes/imagine/assets/reading.js'}}
    runtime_path = 'imagine-demo-build/b03-runtime.php'
    checks['PHP_B03_test_deploye_exact'] = work.readback([runtime_path])[runtime_path] == digest(HERE / 'b03-runtime.php')
    if not checks['PHP_B03_test_deploye_exact']:
        raise RuntimeError('B03 runtime differs; no upload performed')
    php = work.wp('require WP_CONTENT_DIR."/' + runtime_path + '";')
    php.update(at=datetime.now(timezone.utc).isoformat(), scope='imagine-test-demo', phase='corrections')
    (run_proof / 'php-corrections.json').write_text(json.dumps(php, ensure_ascii=False, indent=2), encoding='utf-8')
    http_runner = module('b03-http.py')
    http_runner.PROOF = run_proof
    http = http_runner.run('corrections')
    node = subprocess.run(['node', '--test', '--test-reporter=tap', str(HERE / 'b03-reading.test.cjs')],
                          capture_output=True, text=True, encoding='utf-8')
    (run_proof / 'js-corrections-green.txt').write_text(node.stdout + node.stderr, encoding='utf-8')
    checks['JS_execution_sans_echec'] = node.returncode == 0
    node_tests = int(re.search(r'^# tests (\d+)$', node.stdout, re.M)[1])
    node_pass = int(re.search(r'^# pass (\d+)$', node.stdout, re.M)[1])
    checks['JS_tous_passes'] = node_tests == node_pass and node_tests > 0
    regression_runner = module('b03-regression.py')
    regression_runner.PROOF = run_proof
    regression_runner.run()
    regression = json.loads((run_proof / 'local-regression.json').read_text(encoding='utf-8'))
    local = regression['current_contract']
    checks['regression_locale'] = local['tests'] > 0 and not any(local[k] for k in ['failures', 'errors', 'skipped'])
    guard_tests = subprocess.run([sys.executable, '-B', str(HERE / 'b03-preservation-test.py')], capture_output=True, text=True, encoding='utf-8')
    (run_proof / 'preservation-unit.txt').write_text(guard_tests.stdout + guard_tests.stderr, encoding='utf-8')
    checks['garde_preservation_contre_exemples'] = guard_tests.returncode == 0
    historical = regression['original_b01']
    checks['B01_seule_assertion_historique_obsolete'] = historical['failures'] == 1 and historical['errors'] == 0 and 'assertFalse(list(THEME.rglob' in historical['output']
    # Pas de rejouer.ps1 : son balayage global d'orphelins risquerait un autre worker.
    # Même exécuteur canonique T01, conteneur propre --rm, aucun site monté.
    command = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none',
               '--read-only', '--mount', 'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly',
               '--tmpfs', '/tmp:rw,nosuid,nodev,size=512m,mode=1777', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
               '--user', '65534:65534', '--pids-limit', '128', '--memory', '768m', '--cpus', '2', '--no-healthcheck',
               '--log-driver', 'none', '--label', 'org.imagine.b03=regression', '--entrypoint', 'timeout',
               'imagine-tests-t01:1', '600', 'php', '/repo/wp/tests/t01/executer.php']
    native = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=650)
    (run_proof / 't01-release.txt').write_text(native.stdout + native.stderr, encoding='utf-8')
    matches = re.findall(r'^T01_RESULT (.+)$', native.stdout, re.M)
    t01 = json.loads(matches[0]) if len(matches) == 1 else {}
    checks['T01_canonique_hors_ligne'] = native.returncode == 0 and t01.get('pass') is True and all(t01[k] == 0 for k in ['failures', 'errors', 'skipped'])
    checks['preparation_image_executee'] = 'PREPARATION T01 : image verifiee sha256:' in (PROOF / 'preparer-image.txt').read_text(encoding='utf-8', errors='replace')
    checks['PHP_sans_echec'] = not php['failures']
    checks['HTTP_sans_echec'] = not http['failures']
    baseline = load('http-red.json')
    for visitor in ['a-carte', 'anonyme']:
        checks['corps_C08_inchange:' + visitor] = baseline['responses'][visitor]['body_sha256'] == http['responses'][visitor]['body_sha256']
    browser = load('browser-colors-corrections.json')
    checks['navigateur_corrections'] = bool(browser['checks']) and not browser['failures'] and all(v is True for v in browser['checks'].values())
    browser_count = len(browser['checks'])
    for name, value in browser['source_sha256'].items():
        checks['liaison_preuve_navigateur:' + name] = value == expected['themes/imagine/assets/' + name]
    # Existing deployed C09 test is read back byte-for-byte, then required read-only.
    c09_path = 'imagine-demo-build/c09-payments.php'
    checks['C09_test_deploye_exact'] = work.readback([c09_path])[c09_path] == digest(HERE / 'c09-payments.php')
    if not checks['C09_test_deploye_exact']:
        raise RuntimeError('C09 test bytes differ; no automatic upload authorized')
    raw = work.c08.b00.wp('eval', 'require WP_CONTENT_DIR."/' + c09_path + '";', check=False)
    if raw['stderr']:
        raise RuntimeError('C09 readback warning; private output withheld')
    c09 = json.loads(raw['stdout'])
    c09.update(exit=raw['code'], at=datetime.now(timezone.utc).isoformat())
    (run_proof / 'c09-native-readback.json').write_text(json.dumps(c09, indent=2), encoding='utf-8')
    checks['C09_149_natifs_frais'] = c09['exit'] == 0 and c09['total'] == 149 and len(c09['checks']) == 149 and not c09['failures'] and all(v is True for v in c09['checks'].values())
    native_after = semantic.snapshot()
    checks['etat_metier_natif_exact_avant_apres_rejeu'] = native_before == native_after
    current_end = {'at': datetime.now(timezone.utc).isoformat(),
                   'remote': work.wp(historical_before['snapshot_php']),
                   'local': preservation_guard.local_snapshot(ROOT)}
    (run_proof / 'current-after.json').write_text(json.dumps(current_end, indent=2), encoding='utf-8')
    scoped_checks, preservation = preservation_guard.compare(historical_before, current_start, current_end, deployed, c15_sources, c15_local_documents)
    checks.update(scoped_checks)
    checks.update(documentary_checks)
    checks['reçus_historiques_et_C15_intacts'] = linked_before == preservation_guard.links(ROOT)
    preservation.update(scope='imagine-test-demo', at=datetime.now(timezone.utc).isoformat(),
                        checks={**scoped_checks, **documentary_checks}, linked_sha256=linked_before,
                        current_before_sha256=digest(run_proof / 'current-before.json'),
                        current_after_sha256=digest(run_proof / 'current-after.json'),
                        semantic_before_sha256=hashlib.sha256(json.dumps(native_before, sort_keys=True).encode()).hexdigest(),
                        semantic_after_sha256=hashlib.sha256(json.dumps(native_after, sort_keys=True).encode()).hexdigest(),
                        semantic_scope='C15 snapshot(): fixture, seed, roles, discovery, order status/paid/amount/method/customer/addresses, subscription status/start/end/next/shipping, membership status/start/end; no user table hashes or audit-note rollback')
    (run_proof / 'preservation-reconciliation.json').write_text(json.dumps(preservation, ensure_ascii=False, indent=2), encoding='utf-8')
    sources = [ROOT / 'wp' / path for path in expected]
    sources += sorted(p for p in HERE.glob('b03-*') if p.is_file()) + [HERE / 'test_b03_contract.py']
    documents = [PROOF / p for p in ['A-VOIR.md', 'RAPPORT.md', 'besoins-designer.md', 'REJOUER.md']]
    checks['documents_requis'] = all(p.is_file() and p.stat().st_size > 0 for p in documents)
    # Ne jamais imprimer de valeur privée ni de corps HTTP authentifié.
    secrets = []
    def collect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if 'password' in key and isinstance(item, str): secrets.append(item.encode())
                else: collect(item)
        elif isinstance(value, list):
            for item in value: collect(item)
    for name in ['identifiants.json', 'c08-identifiants.json']:
        collect(json.loads((Path.home() / '.imagine-demo' / name).read_text(encoding='utf-8')))
    candidates = [p for p in PROOF.rglob('*') if p.is_file()] + sources
    leak_count = sum(any(secret and secret in p.read_bytes() for secret in secrets) for p in candidates)
    checks['aucun_mot_de_passe_prive_dans_livrables'] = leak_count == 0
    script = (ROOT / 'wp/themes/imagine/assets/reading.js').read_bytes()
    css_tokens = (ROOT / 'wp/themes/imagine/assets/tokens.css').read_text(encoding='utf-8')
    contrast = {}
    def luminance(color):
        rgb = [int(color[i:i+2], 16)/255 for i in [0, 2, 4]]
        linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        return sum(v*w for v,w in zip(linear, [.2126, .7152, .0722]))
    for theme in ['light', 'sepia', 'dark']:
        values = [luminance(re.search(r'--imagine-reading-' + theme + '-' + role + r':\s*#([0-9a-fA-F]{6});', css_tokens)[1]) for role in ['paper', 'ink']]
        contrast[theme] = (max(values)+.05)/(min(values)+.05)
    checks['fonds_AA'] = all(v >= 4.5 for v in contrast.values())
    correction = ROOT / 'corrections/B-03.md'
    checks['verification_apres_correction'] = datetime.fromisoformat(current_start['at']).timestamp() > correction.stat().st_mtime
    checks['verification_apres_C15_termine'] = datetime.fromisoformat(current_start['at']).timestamp() > (ROOT / 'production/C-15/PRET').stat().st_mtime
    failures = [k for k,v in checks.items() if v is not True]
    evidence = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo', 'status': 'VERIFIED' if not failures else 'FAILED',
                'counts': {'php_B03': php['total'], 'HTTP': http['total'], 'JS': node_tests, 'local_regression': local['tests'],
                           'T01': t01, 'C09_native': c09['total'], 'browser_anonyme_assertions': browser_count, 'final_checks': len(checks)},
                'checks': checks, 'failures': failures, 'remote_sha256': actual,
                'correction_sha256': digest(correction),
                'script_bytes': len(script), 'script_gzip_bytes': len(gzip.compress(script, mtime=0)),
                'reading_words_per_minute': http['reading_words_per_minute'], 'contrast_ratios': contrast, 'python': sys.executable,
                'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
                'documents_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in documents},
                'evidence_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in
                    [PROOF / n for n in ['deploy-corrections.json', 'deploy-reduced-motion.json', 'browser-colors-corrections.json', 'preparer-image.txt']]
                    + [run_proof / n for n in ['php-corrections.json', 'http-corrections.json', 'js-corrections-green.txt', 't01-release.txt', 'local-regression.json', 'preservation-reconciliation.json', 'current-before.json', 'current-after.json', 'c09-native-readback.json', 'preservation-unit.txt']]},
                'limits': ['Navigateur réel anonyme seulement ; a-carte prouvé par vrais cookies HTTP et logique JS testée hors navigateur.',
                           preservation['reservation'],
                           'Snapshots exacts limites aux quatre tables historiques non-utilisateur et aux fichiers plugins/theme ; options et metier natif verifies separement par snapshot semantique. Aucun paiement/action/reset C15 rejoue.',
                           'Ancienne assertion B01 sans aucun JS obsolète ; une adaptation B03 en mémoire, test historique intact.',
                           'PRET est prêt à relire, pas une approbation visuelle ou une mise en production.']}
    (run_proof / 'verification-finale.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    pointer = {'status': evidence['status'], 'at': evidence['at'],
               'receipt': (run_proof / 'verification-finale.json').relative_to(ROOT).as_posix(),
               'sha256': digest(run_proof / 'verification-finale.json'),
               'historical_failed_receipt_preserved': 'production/B-03/verification-finale.json'}
    (PROOF / 'reconciliation-c15-current.json').write_text(json.dumps(pointer, indent=2), encoding='utf-8')
    print(json.dumps({k:evidence[k] for k in ['status', 'counts', 'failures', 'script_bytes', 'script_gzip_bytes', 'contrast_ratios']}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)
    return evidence


if __name__ == '__main__':
    run()
