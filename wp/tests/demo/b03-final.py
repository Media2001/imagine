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
    deployed = load('deploy-release.json')['expected']
    expected = {path: digest(ROOT / 'wp' / path) for path in deployed}
    actual = work.readback(list(expected))
    checks = {'theme_local_deploye_exact': actual == expected == deployed,
              'depot_limite_au_theme': all(p.startswith('themes/imagine/') for p in deployed)}
    php = work.runtime('release')
    http = module('b03-http.py').run('release')
    node = subprocess.run(['node', '--test', '--test-reporter=tap', str(HERE / 'b03-reading.test.cjs')],
                          capture_output=True, text=True, encoding='utf-8')
    (PROOF / 'js-release.txt').write_text(node.stdout + node.stderr, encoding='utf-8')
    checks['JS_execution_sans_echec'] = node.returncode == 0
    node_tests = int(re.search(r'^# tests (\d+)$', node.stdout, re.M)[1])
    node_pass = int(re.search(r'^# pass (\d+)$', node.stdout, re.M)[1])
    checks['JS_tous_passes'] = node_tests == node_pass and node_tests > 0
    module('b03-regression.py').run()
    regression = load('local-regression.json')
    local = regression['current_contract']
    checks['regression_locale'] = local['tests'] > 0 and not any(local[k] for k in ['failures', 'errors', 'skipped'])
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
    (PROOF / 't01-release.txt').write_text(native.stdout + native.stderr, encoding='utf-8')
    matches = re.findall(r'^T01_RESULT (.+)$', native.stdout, re.M)
    t01 = json.loads(matches[0]) if len(matches) == 1 else {}
    checks['T01_canonique_hors_ligne'] = native.returncode == 0 and t01.get('pass') is True and all(t01[k] == 0 for k in ['failures', 'errors', 'skipped'])
    checks['preparation_image_executee'] = 'PREPARATION T01 : image verifiee sha256:' in (PROOF / 'preparer-image.txt').read_text(encoding='utf-8', errors='replace')
    checks['PHP_sans_echec'] = not php['failures']
    checks['HTTP_sans_echec'] = not http['failures']
    baseline = load('http-red.json')
    for visitor in ['a-carte', 'anonyme']:
        checks['corps_C08_inchange:' + visitor] = baseline['responses'][visitor]['body_sha256'] == http['responses'][visitor]['body_sha256']
    browser_count = 0
    for receipt in ['browser-narrow-final.json', 'browser-wide-final.json']:
        row = load(receipt)
        checks[receipt] = not row['failures'] and all(v is True for v in row['checks'].values())
        browser_count += len(row['checks'])
    # Le dernier changement n'était qu'un reformatage de l'enqueue PHP.
    # Les octets réellement exercés au navigateur restent identiques à la release.
    browser_deploy = load('deploy-final.json')['actual']
    for rel in ['assets/reading.js', 'assets/reading.css', 'assets/tokens.css', 'single.php']:
        key = 'themes/imagine/' + rel
        checks['liaison_preuve_navigateur:' + rel] = browser_deploy[key] == expected[key]
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
    failures = [k for k,v in checks.items() if v is not True]
    evidence = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo', 'status': 'VERIFIED' if not failures else 'FAILED',
                'counts': {'php_B03': php['total'], 'HTTP': http['total'], 'JS': node_tests, 'local_regression': local['tests'],
                           'T01': t01, 'browser_anonyme_assertions': browser_count, 'final_checks': len(checks)},
                'checks': checks, 'failures': failures, 'remote_sha256': actual,
                'script_bytes': len(script), 'script_gzip_bytes': len(gzip.compress(script, mtime=0)),
                'reading_words_per_minute': 200, 'contrast_ratios': contrast,
                'source_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sources},
                'documents_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in documents},
                'evidence_sha256': {name: digest(PROOF / name) for name in ['deploy-release.json', 'php-release.json', 'http-release.json', 'js-release.txt', 't01-release.txt', 'local-regression.json', 'browser-narrow-final.json', 'browser-wide-final.json', 'preparer-image.txt']},
                'limits': ['Navigateur réel anonyme seulement ; a-carte prouvé par vrais cookies HTTP et logique JS testée hors navigateur.',
                           'Ancienne assertion B01 sans aucun JS obsolète ; une adaptation B03 en mémoire, test historique intact.',
                           'PRET est prêt à relire, pas une approbation visuelle ou une mise en production.']}
    (PROOF / 'verification-finale.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:evidence[k] for k in ['status', 'counts', 'failures', 'script_bytes', 'script_gzip_bytes', 'contrast_ratios']}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)
    return evidence


if __name__ == '__main__':
    run()
