"""C14 : installation ciblée et recette réelle sur imagine-test-demo seulement."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import base64
import importlib.util
import json
import re
import subprocess
import sys
import c10

ROOT = c10.ROOT
PROOF = ROOT / 'production/C-14'
CODE = ['AchatNumero.php', 'AchatsNumeros.php', 'Paywall.php', 'imagine-site.php']


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'wp/tests/demo' / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def wp(code, check=True):
    r = c10.b00.wp('eval', code, check=False)
    if r['code'] or r['stderr']:
        if check:
            raise RuntimeError('Recette PHP C14 : ' + r['stderr'][-2000:] + r['stdout'][-1500:])
        return r
    return json.loads(r['stdout'])


def upload(rel, source):
    data = source.read_bytes()
    c10.b00.upload(rel, data)
    actual = c10.b00.wp('eval', '$p=WP_CONTENT_DIR . ' + json.dumps('/' + rel) + ';'
        + ('token_get_all(file_get_contents($p),TOKEN_PARSE);' if rel.endswith('.php') else '')
        + 'echo base64_encode(file_get_contents($p));')['stdout'].strip()
    if actual != base64.b64encode(data).decode():
        raise RuntimeError('Relecture différente : ' + rel)


def preserve():
    return wp('''$out=[];global $wpdb;
foreach(['imagine_c08_fixture','imagine_c09_fixture','imagine_demo_manifest','imagine_acces_plans','imagine_c12_fixture','imagine_c13_fixture'] as $k){$out[$k]=get_option($k);}
$out['policies']=$wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE 'imagine_decouverte_%' OR option_name LIKE 'imagine_envoi_%' OR option_name IN ('imagine_acces_reglages','imagine_c05_reglages','imagine_envoi_colonnes_export') ORDER BY option_name",ARRAY_A);
$out['files']=[];foreach(['imagine-site/Decouverte.php','imagine-site/DecouverteReglages.php','imagine-site/EnvoiNatif.php','imagine-site/ListeEnvoiAdmin.php','imagine-site/PdfNumero.php'] as $p){$out['files'][$p]=hash_file('sha256',WP_PLUGIN_DIR . '/' . $p);}
foreach(['imagine-pilotage','imagine-connecteur'] as $d){foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator(WP_PLUGIN_DIR . '/' . $d,FilesystemIterator::SKIP_DOTS)) as $f){if($f->isFile()){$out['files'][substr($f->getPathname(),strlen(WP_PLUGIN_DIR)+1)]=hash_file('sha256',$f->getPathname());}}}ksort($out['files']);echo wp_json_encode($out);''')


def pure():
    cmd = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none',
           '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534',
           '--mount', 'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly', '--entrypoint', 'php',
           'imagine-tests-t01:1', '/repo/wp/tests/demo/c14-unit.php']
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=120)
    if result.returncode or result.stderr:
        raise RuntimeError(result.stdout + result.stderr)
    checks = json.loads(result.stdout)
    if not checks or not all(v is True for v in checks.values()):
        raise RuntimeError('Règle pure C14 en échec')
    return checks


def run(deploy=False):
    PROOF.mkdir(parents=True, exist_ok=True)
    c10.guard()
    before = preserve()
    results = {'scope': 'imagine-test-demo', 'at': datetime.now(timezone.utc).isoformat(), 'pure': pure()}
    if deploy:
        # Le bootstrap en place doit être exactement C13 + l'ajout ciblé C14.
        rel = 'plugins/imagine-site/imagine-site.php'
        old = base64.b64decode(c10.b00.wp('eval', 'echo base64_encode(file_get_contents(WP_CONTENT_DIR . "/' + rel + '"));')['stdout'])
        data = (ROOT / 'wp' / rel).read_bytes()
        addition = b"require_once __DIR__ . '/AchatNumero.php';\nrequire_once __DIR__ . '/AchatsNumeros.php';\nAchatsNumeros::register();\n\n"
        if old != data and old != data.replace(addition, b''):
            raise RuntimeError('Bootstrap partagé divergent, refus de perdre C13')
        for name in CODE:
            upload('plugins/imagine-site/' + name, ROOT / 'wp/plugins/imagine-site' / name)
        for name in ['c14-profil.php', 'c09-seed.php', 'c09-profils.json']:
            upload('imagine-demo-build/' + name, ROOT / 'wp/outils/demo' / name)
        results['profil'] = wp('require_once WP_CONTENT_DIR . "/imagine-demo-build/c14-profil.php";$f=get_option("imagine_c09_fixture");echo wp_json_encode(Imagine\\Demo\\C14\\profil($f["users"]["P-NUMERO"],wc_get_order($f["orders"]["P-NUMERO"])));')
    for name in CODE:
        expected = base64.b64encode((ROOT / 'wp/plugins/imagine-site' / name).read_bytes()).decode()
        actual = c10.b00.wp('eval', 'echo base64_encode(file_get_contents(WP_PLUGIN_DIR . ' + json.dumps('/imagine-site/' + name) + '));')['stdout'].strip()
        if actual != expected:
            raise RuntimeError('Code C14 distant/local différent : ' + name)
    for name in ['c14-runtime.php', 'c09-runtime.php']:
        upload('imagine-demo-build/' + name, ROOT / 'wp/tests/demo' / name)
    results['native'] = wp('require WP_CONTENT_DIR . "/imagine-demo-build/c14-runtime.php";')
    print('C14 natif :', sum(v is True for v in results['native'].values()), '/', len(results['native']), flush=True)
    if not all(v is True for v in results['native'].values()):
        (PROOF / 'echec.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
        raise RuntimeError('Échecs C14 natifs : ' + str([k for k,v in results['native'].items() if v is not True]))
    results['http'] = module('c14_http', 'c14-http.py').verify()
    for key, filename in [('C08', 'c08-runtime.php'), ('C11', 'c11-runtime.php')]:
        upload('imagine-demo-build/' + filename, ROOT / 'wp/tests/demo' / filename)
        value = wp('require WP_CONTENT_DIR . "/imagine-demo-build/' + filename + '";')
        if key == 'C08':
            if value['failures']:
                raise RuntimeError('Régression C08 : ' + str(value['failures']))
            results[key] = {'total': value['total'], 'failures': value['failures']}
        else:
            if not all(v is True for v in value.values()):
                raise RuntimeError('Régression C11')
            results[key] = value
    c09 = wp('require WP_CONTENT_DIR . "/imagine-demo-build/c09-runtime.php";', check=False)
    # La recette entière C09 contient des échéances anciennes qui peuvent avoir expiré.
    if isinstance(c09, dict) and 'stdout' in c09:
        c09 = json.loads(c09['stdout'])
    results['C09'] = {'total': c09['total'], 'failures': c09['failures']}
    if c09['failures']:
        raise RuntimeError('Régression C09 : ' + str(c09['failures']))
    after = preserve()
    results['shared_C08_C09_C10_C11_C12_C13_preserved'] = before == after
    if before != after:
        raise RuntimeError('État partagé modifié : ' + str([k for k in before if before[k] != after[k]]))
    results['status'] = 'VERT'
    results['total'] = sum(len(results[k]) for k in ['pure', 'native', 'http', 'C11']) + results['C08']['total'] + results['C09']['total']
    (PROOF / 'resultats.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print('C14 VERT :', results['total'], 'contrôles/tests ;', PROOF / 'resultats.json')
    return results


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--deploy', action='store_true', help='Installation ciblée et V-NUM ; défaut = rejeu sans reset')
    run(p.parse_args().deploy)
