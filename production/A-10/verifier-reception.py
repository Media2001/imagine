"""Read-only, parent-executable reception verification for A10/A11/A12/A13."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]


def read(key):
    return json.loads((REPO/key).read_text(encoding='utf8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def execute(arguments):
    proc = subprocess.run([sys.executable, '-B', *arguments], cwd=REPO,
                          capture_output=True, text=True, encoding='utf8', timeout=180)
    require(proc.returncode == 0, 'VERIFIER_FAILED:'+str(arguments)+':'+proc.stdout[-1000:]+proc.stderr[-1000:])
    return json.loads(proc.stdout)


def main():
    common = read('production/A-10/reception-common.json')
    require(common['exit_code'] == 0, 'COMMON_NOT_GREEN')
    receipt = read('production/A-11/preparer-image-parent.json')
    require(receipt['exit_code'] == 0, 'PARENT_PREPARATION_NOT_GREEN')
    require(digest(REPO/receipt['log']) == receipt['sha256'] == common['parent_log_sha256'], 'PARENT_LOG_DRIFT')
    require(digest(REPO/'wp/tests/preparer-image.ps1') == common['preparation_script_sha256'], 'PREPARATION_SCRIPT_DRIFT')
    log = (REPO/receipt['log']).read_text(encoding='utf8')
    require('T01 IMAGE READY :' in log and 'PREPARATION T01 : image verifiee '+common['prepared_image_id'] in log, 'IMAGE_READY_RECEIPT_MISSING')
    for relative, sha in common['protected_sources'].items():
        require((REPO/relative).is_file() and digest(REPO/relative) == sha, 'PROTECTED_SOURCE_DRIFT:'+relative)
    spec = importlib.util.spec_from_file_location('reception_a10', REPO/'wp/tests/a10/verifier.py')
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    require(v.readme_original_digest((REPO/'wp/tests/a02-audit/README.md').read_bytes(), (REPO/'production/A-10/readme-ajout.txt').read_bytes()) == v.A02_README_SHA256, 'README_CONTRACT')
    image = json.loads(v.r.b.call(['image', 'inspect', 'imagine-tests-t01:1']).stdout)[0]
    require(image['Id'] == common['prepared_image_id'] and image['Config']['Labels'].get('org.imagine.t01-image') == '1', 'PREPARED_IMAGE_DRIFT')
    require(not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts'), 'PREPARED_IMAGE_UNSAFE')
    manifests = {}
    for lot, filename in [('A-10', 'manifest.json'), ('A-11', 'manifest.json'), ('A-12', 'manifeste-final.json'), ('A-13', 'manifeste.json')]:
        payload = read('production/'+lot+'/'+filename)
        if lot == 'A-13':
            rows = payload['fichiers']
            files = {row['chemin']: row['sha256'] for row in rows}
            require(len(files) == len(rows) == payload['nombre_fichiers'], 'A13_MANIFEST_DUPLICATE_OR_COUNT')
            for row in rows:
                require((REPO/row['chemin']).stat().st_size == row['octets'], 'A13_SIZE_DRIFT')
        else:
            files = {key: (value['sha256'] if isinstance(value, dict) else value) for key, value in payload['files'].items()}
            if 'file_count' in payload:
                require(len(files) == payload['file_count'], lot+':FILE_COUNT')
        for relative, sha in files.items():
            require((REPO/relative).is_file() and digest(REPO/relative) == sha, lot+':MANIFEST_DRIFT:'+relative)
        require(payload.get('status', payload.get('verdict')) == 'PRET', lot+':STATUS_NOT_PRET')
        pret = (REPO/'production'/lot/'PRET').read_text(encoding='utf8').splitlines()[0]
        expected_pret = 'PRET'+payload['run_id'] if lot == 'A-10' else ('PRET'+Path(payload['packet']).name if lot == 'A-11' else 'PRET')
        require(pret == expected_pret, lot+':PRET_POINTER_INVALID')
        # Every current delivery file must be sealed; only self and non-circular verification are excluded.
        exclusions = set(payload.get('excluded_dynamic', []))
        for path in (REPO/'production'/lot).rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            key = path.relative_to(REPO).as_posix()
            if lot == 'A-10' and 'preuves' in path.parts and payload['run_id'] not in path.parts:
                continue  # Historical packets are explicitly not current.
            require(key in files or key in exclusions, lot+':UNSEALED_FILE:'+key)
        manifests[lot] = payload
    a10 = execute(['wp/tests/a10/verifier.py'])
    a11_packet = manifests['A-11']['packet']
    a11_dirs = sorted(p.relative_to(REPO).as_posix() for p in (REPO/'production/A-11/preuves').iterdir() if p.is_dir())
    require(a11_dirs == [a11_packet], 'A11_NOT_ONE_FINAL_PACKET')
    source11 = read(a11_packet+'/sources.json')
    current11 = {p.relative_to(REPO).as_posix(): digest(p) for root in [REPO/'wp/tests/a11', REPO/'wp/outils/bascule/a11'] for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    require(source11 == current11, 'A11_EXACT_SOURCE_INVENTORY_DRIFT')
    runner11 = read(a11_packet+'/runner.json')
    require(any(c['check'] == 'native' and c['status'] == 'PASS' for c in runner11['checks']), 'A11_NATIVE_MISSING')
    missing11 = v.r.b.call(['inspect', runner11['container']], check=False)
    require(missing11.returncode != 0 and re.search(r'no such (object|container)', missing11.stderr, re.I) is not None, 'A11_OWNED_RUNNER_NOT_ABSENT')
    a11 = execute(['wp/tests/a11/verifier.py', a11_packet])
    a12_dirs = sorted(p.name for p in (REPO/'production/A-12/preuves').iterdir() if p.is_dir())
    require(a12_dirs == ['final'], 'A12_NOT_ONE_FINAL_PACKET')
    a12 = execute(['wp/tests/a12/verify.py', 'production/A-12/preuves/final'])
    a13 = read('production/A-13/reception-verification.json')
    require(a13['suite']['tests'] == 35 and all(a13['suite'][k] == 0 for k in ['echecs', 'erreurs', 'ignores']), 'A13_SUITE_FAILED')
    require([row['code'] for row in a13['cli']] == [0, 1, 2] and all(row['fichier_source_inchange'] for row in a13['cli']), 'A13_CLI_FAILED')
    regression = subprocess.run([sys.executable, '-B', 'wp/tests/a10/test_readme_contract.py'], cwd=REPO, capture_output=True, text=True, timeout=30)
    require(regression.returncode == 0, 'README_ADVERSARIAL_REGRESSIONS_FAILED')
    print(json.dumps({'exit_code': 0, 'lots': ['A-10', 'A-11', 'A-12', 'A-13'],
                      'status': 'PRET', 'readme_original_and_exact_appends': True,
                      'readme_regression_tests': 4, 'parent_image_preparation': 'verified',
                      'manifest_files': {lot: len(m.get('files', m.get('fichiers', []))) for lot, m in manifests.items()},
                      'A10': a10, 'A11': a11, 'A12': {'counts': a12['counts'], 'checks': len(a12['checks']), 'exit_code': a12['exit_code']},
                      'A13': {'tests': a13['suite']['tests'], 'cli_exit_codes': [row['code'] for row in a13['cli']]}}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'exit_code': 1, 'error': str(exc)}, ensure_ascii=False))
        sys.exit(1)
