"""Non-régression C14 sans réinitialiser les autres profils ni écrire leurs rapports."""
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
import c14
import c12


def run():
    c14.c10.guard()
    before = c14.preserve()
    results = {'scope': 'imagine-test-demo', 'status': 'EN_COURS'}
    path = c14.PROOF / 'regressions.json'
    def save():
        path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    save()
    for key in ['c11', 'c12']:
        command = [sys.executable, str(c14.ROOT / 'wp/outils/demo' / (key + '-unit.py'))]
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=240)
        counts = re.search(r'OK \((\d+) tests?, (\d+) assertions?\)', result.stdout)
        if result.returncode or not counts:
            print(result.stdout + result.stderr)
            raise RuntimeError('PHPUnit ' + key + ' en échec')
        results[key + '_phpunit'] = {'tests': int(counts[1]), 'assertions': int(counts[2]), 'exit': result.returncode}
        print(key + ' PHPUnit :', int(counts[1]), 'tests ;', int(counts[2]), 'assertions', flush=True)
        save()
    results['C12_native'] = c12.runtime()
    save()
    results['C12_HTTP'] = c14.module('c14_c12_http_regression', 'c12-http.py').verify()
    save()
    sys.path[:0] = [str(p) for p in (c14.ROOT / 'production/B-01/validation').glob('*.whl')]
    transcript = io.StringIO()
    local = unittest.TextTestRunner(stream=transcript, verbosity=1).run(
        unittest.defaultTestLoader.discover(str(c14.ROOT / 'wp/tests/demo'), pattern='test_*.py'))
    results['local'] = {'tests': local.testsRun, 'success': local.wasSuccessful()}
    if not local.wasSuccessful():
        print(transcript.getvalue())
        save()
        raise RuntimeError('Unitaires locaux en échec')
    results['shared_preserved'] = before == c14.preserve()
    if not results['shared_preserved']:
        save()
        raise RuntimeError('Non-régression : état partagé différent')
    results['status'] = 'VERT'
    results['total'] = sum(results[k + '_phpunit']['tests'] for k in ['c11', 'c12']) + len(results['C12_native']) + len(results['C12_HTTP']) + local.testsRun
    save()
    print('Non-régression C14 VERT :', results['total'], 'tests/contrôles ;', path)


if __name__ == '__main__':
    run()
