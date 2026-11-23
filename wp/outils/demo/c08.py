"""C08 : installation ciblée et preuves, jamais de création ni de reseed B00."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parent))
import construire as b00

ROOT = b00.ROOT
PROOF = ROOT / 'production/C-08'
GUARD = 'echo wp_json_encode(["environment"=>wp_get_environment_type(),"demo"=>get_option("imagine_demo_site"),"manifest"=>get_option("imagine_demo_manifest")]);'


def guard():
    site = b00.request_api('GET', '/api/sites/' + b00.SLUG)
    b00.validate_target(site['slug'])
    if site['status'] != 'running':
        raise RuntimeError('Le site fictif doit déjà tourner.')
    state = json.loads(b00.wp('eval', GUARD)['stdout'])
    if state['environment'] != 'local' or state['demo'] != b00.SLUG:
        raise RuntimeError('Garde locale fictive absente; aucune écriture.')
    return site, state


def run(tests_only=False, seed=False):
    site, before = guard()
    PROOF.mkdir(parents=True, exist_ok=True)
    record = {'scope': b00.SLUG, 'at': datetime.now(timezone.utc).isoformat(), 'url': site['url']}
    files = {}
    if not tests_only:
        for source in sorted((ROOT / 'wp/plugins/imagine-site').rglob('*.php')):
            files['plugins/imagine-site/' + source.relative_to(ROOT / 'wp/plugins/imagine-site').as_posix()] = source
        # Point de sortie seul + blocs; pas de redéploiement B01 global.
        files['themes/imagine/functions.php'] = ROOT / 'wp/themes/imagine/functions.php'
        for source in sorted((ROOT / 'wp/themes/imagine/parts').glob('paywall-*.php')):
            files['themes/imagine/parts/' + source.name] = source
    files['imagine-demo-build/c08-runtime.php'] = ROOT / 'wp/tests/demo/c08-runtime.php'
    if seed:
        credential_path = b00.validate_credentials_path(Path.home() / '.imagine-demo/c08-identifiants.json')
        if credential_path.exists():
            credentials = json.loads(credential_path.read_text(encoding='utf-8'))
        else:
            credentials = {'url': site['url'], 'accounts': {key: {'login': 'imagine-c08-' + key, 'password': secrets.token_urlsafe(24)}
                           for key in ['actif', 'grace', 'sans-droit']}}
            credential_path.parent.mkdir(parents=True, exist_ok=True)
            credential_path.write_text(json.dumps(credentials, ensure_ascii=False, indent=2), encoding='utf-8')
            os.chmod(credential_path, 0o600)
        base = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))
        base['c08_accounts'] = credentials['accounts']
        if b00.remote('seed-secret', secret=base)['code']:
            raise RuntimeError('Secret fictif non transmis.')
        files['imagine-demo-build/c08-seed.php'] = ROOT / 'wp/outils/demo/c08-seed.php'
        record['credentials_file'] = str(credential_path)
    hashes = {}
    for rel, source in files.items():
        data = source.read_bytes()
        hashes[rel] = hashlib.sha256(data).hexdigest()
        b00.upload(rel, data)
    code = '$files=json_decode(' + json.dumps(json.dumps(list(files))) + ',true);$out=[];foreach($files as $f){$p=WP_CONTENT_DIR . "/" . $f;token_get_all(file_get_contents($p),TOKEN_PARSE);$out[$f]=hash_file("sha256",$p);}echo wp_json_encode($out);'
    actual = json.loads(b00.wp('eval', code)['stdout'])
    if hashes != actual:
        raise RuntimeError('Readback des fichiers divergent.')
    record['files_sha256'] = actual
    record['file_count'] = len(actual)
    if seed:
        record['fixture'] = json.loads(b00.wp('eval', 'require ABSPATH . "wp-content/imagine-demo-build/c08-seed.php";')['stdout'])
    result = b00.wp('eval', 'require ABSPATH . "wp-content/imagine-demo-build/c08-runtime.php";', check=False)
    record['runtime'] = result
    after = json.loads(b00.wp('eval', GUARD)['stdout'])
    record['b00_manifest_unchanged'] = before == after
    record['status'] = 'VERIFIED' if not result['code'] and before == after else 'RED' if tests_only else 'FAILED'
    target = PROOF / ('red-runtime.json' if tests_only else 'installation.json')
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False, indent=2))
    if result['code'] or before != after:
        raise SystemExit(1)
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tests-only', action='store_true')
    parser.add_argument('--seed', action='store_true')
    args = parser.parse_args()
    run(args.tests_only, args.seed)
