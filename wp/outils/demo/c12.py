"""C12, cible fictive unique ; aucun constructeur global, aucune preuve hors C12."""
import argparse
import base64
import json
from pathlib import Path
import c10

ROOT = c10.ROOT
FILES = ['plugins/imagine-site/Decouverte.php', 'plugins/imagine-site/DecouverteReglages.php',
         'plugins/imagine-site/Paywall.php', 'plugins/imagine-site/imagine-site.php']


def upload(rel, source):
    data = source.read_bytes()
    c10.b00.upload(rel, data)
    code = '$p=WP_CONTENT_DIR . ' + json.dumps('/' + rel) + ';token_get_all(file_get_contents($p),TOKEN_PARSE);echo base64_encode(file_get_contents($p));'
    if c10.b00.wp('eval', code)['stdout'].strip() != base64.b64encode(data).decode():
        raise RuntimeError('Readback différent : ' + rel)


def runtime():
    upload('imagine-demo-build/c12-runtime.php', ROOT / 'wp/tests/demo/c12-runtime.php')
    result = c10.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c12-runtime.php";', check=False)
    checks = json.loads(result['stdout'])
    print('C12 PHP :', sum(v is True for v in checks.values()), '/', len(checks), '; échecs :', [k for k, v in checks.items() if v is not True])
    if result['code'] or result['stderr'] or not all(v is True for v in checks.values()):
        raise SystemExit(1)
    return checks


def run(tests_only=False):
    c10.guard()  # Identité read-only AVANT toute écriture cible.
    if not tests_only:
        for rel in FILES:
            upload(rel, ROOT / 'wp' / rel)
        for name in ['c12-seed.php', 'c12-profils.php', 'c09-seed.php', 'c09-profils.json']:
            upload('imagine-demo-build/' + name, ROOT / 'wp/outils/demo' / name)
        c10.b00.wp('eval', '(static function(){require WP_CONTENT_DIR . "/imagine-demo-build/c12-seed.php";})();')
        c10.b00.wp('eval', 'require_once WP_CONTENT_DIR . "/imagine-demo-build/c12-profils.php";$f=get_option("imagine_c09_fixture");foreach(["V-DEC","V-DEC-FIN"] as $k){Imagine\\Demo\\C12\\profil($f["users"][$k],$k);}echo "ok";')
        result = json.loads(c10.b00.wp('eval', '$f=get_option("imagine_c09_fixture");$out=[];foreach(["V-DEC","V-DEC-FIN"] as $k){$id=$f["users"][$k];$out[$k]=["verified"=>get_user_meta($id,"imagine_email_confirme",true)==="1","state"=>Imagine\\Site\\Decouverte::etat($id)];}echo wp_json_encode($out);')['stdout'])
        if not all(row['verified'] for row in result.values()) or result['V-DEC-FIN']['state'] is None:
            raise RuntimeError('Profils C12 non relus')
    runtime()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tests-only', action='store_true')
    run(parser.parse_args().tests_only)
