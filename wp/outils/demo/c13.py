"""C13 : cible unique, pas de reset, secrets hors dépôt, preuves proportionnées."""
import argparse
import base64
import importlib.util
import json
from pathlib import Path
import c10

ROOT = c10.ROOT
FILES = ['plugins/imagine-site/EnvoiNatif.php', 'plugins/imagine-site/ListeEnvoiAdmin.php',
         'plugins/imagine-site/imagine-site.php']


def upload(rel, source):
    data = source.read_bytes()
    c10.b00.upload(rel, data)
    out = c10.b00.wp('eval', '$p=WP_CONTENT_DIR . ' + json.dumps('/' + rel) + ';token_get_all(file_get_contents($p),TOKEN_PARSE);echo base64_encode(file_get_contents($p));')
    if out['stderr'] or out['stdout'].strip() != base64.b64encode(data).decode():
        raise RuntimeError('Relecture différente : ' + rel)


def runtime():
    upload('imagine-demo-build/c13-runtime.php', ROOT / 'wp/tests/demo/c13-runtime.php')
    out = c10.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c13-runtime.php";', check=False)
    if out['code'] or out['stderr']:
        raise RuntimeError('Recette PHP C13 : ' + out['stderr'])
    checks = json.loads(out['stdout'])
    print(json.dumps({'PHP': checks}, ensure_ascii=False))
    if not checks or not all(v is True for v in checks.values()):
        raise RuntimeError('Assertions C13 rouges')
    return checks


def run(deploy=False, php_only=False):
    _, before = c10.guard()  # Sonde read-only avant toute mutation de la cible.
    if deploy:
        for rel in FILES:
            upload(rel, ROOT / 'wp' / rel)
        upload('imagine-demo-build/c13-fixture.php', ROOT / 'wp/outils/demo/c13-fixture.php')
        seed = c10.b00.wp('eval', '(static function(){require WP_CONTENT_DIR . "/imagine-demo-build/c13-fixture.php";})();')
        if seed['stderr']:
            raise RuntimeError('Avertissement à l’initialisation C13')
        print('Témoins natifs C13 relus :', seed['stdout'].strip())
    checks = {'PHP': runtime()}
    if not php_only:
        path = ROOT / 'wp/tests/demo/c13-http.py'
        spec = importlib.util.spec_from_file_location('c13_http', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        checks['HTTP'] = mod.verify()
        checks['manifestes_preserves'] = before == c10.guard()[1]
        if not checks['manifestes_preserves']:
            raise RuntimeError('Manifeste protégé différent')
        (ROOT / 'production/C-13/resultats.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
        print('C13 :', sum(len(v) for v in checks.values() if isinstance(v, dict)), 'assertions PHP/HTTP ; manifestes préservés')
    return checks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deploy', action='store_true')
    parser.add_argument('--php-only', action='store_true')
    args = parser.parse_args()
    run(args.deploy, args.php_only)
