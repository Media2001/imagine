"""Installer/rejouer C11 uniquement sur la démonstration fictive existante."""
from pathlib import Path
import argparse
import base64
import importlib.util
import io
import json
import sys
import subprocess
import re
import unittest
import c10
from b00_fixtures import fixture_data, dummy_pdf

ROOT = c10.ROOT
FILES = ['plugins/imagine-site/PdfNumero.php', 'plugins/imagine-site/Paywall.php',
         'themes/imagine/single-imagine_numero.php']
SHARED = ['imagine-site.php', 'Decouverte.php', 'DecouverteReglages.php', 'EnvoiNatif.php', 'ListeEnvoiAdmin.php']


def shared_state():
    # Relecture exacte et ciblée, sans reçu d'empreintes ni mutation C12/C13.
    paths = ['plugins/imagine-site/' + name for name in SHARED]
    code = '$out=[];foreach(json_decode(' + json.dumps(json.dumps(paths)) + ',true) as $p){$out[$p]=base64_encode(file_get_contents(WP_CONTENT_DIR . "/" . $p));}echo wp_json_encode($out);'
    files = json.loads(c10.b00.wp('eval', code)['stdout'])
    for rel, data in files.items():
        if base64.b64encode((ROOT / 'wp' / rel).read_bytes()).decode() != data:
            raise RuntimeError('État partagé distant/local différent : ' + rel)
    code = '''global $wpdb;$rows=$wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name IN ('imagine_c12_fixture','imagine_c13_fixture','imagine_decouverte_reglages') OR option_name LIKE 'imagine_decouverte_compte_%' OR option_name LIKE 'imagine_envoi_%' ORDER BY option_name",ARRAY_A);echo wp_json_encode($rows);'''
    return files, c10.b00.wp('eval', code)['stdout']


def run(check_only=False):
    site, before = c10.guard()
    shared = shared_state()
    unit = subprocess.run([sys.executable, str(ROOT / 'wp/outils/demo/c11-unit.py')],
                          capture_output=True, text=True, encoding='utf-8')
    print(unit.stdout + unit.stderr)
    counts = re.search(r'OK \((\d+) tests, (\d+) assertions\)', unit.stdout)
    if unit.returncode or not counts:
        raise RuntimeError('PHPUnit C11 échoué')
    if not check_only:
        c10.b00.remote('pdf-private-init')
        for issue in fixture_data()['issues']:
            c10.b00.remote('pdf-source', name=issue['slug'] + '.pdf', data=base64.b64encode(dummy_pdf(issue['label'])).decode())
        for rel in FILES:
            data = (ROOT / 'wp' / rel).read_bytes()
            if rel == 'plugins/imagine-site/Paywall.php':
                read = 'echo base64_encode(file_get_contents(WP_CONTENT_DIR . "/' + rel + '"));'
                current = base64.b64decode(c10.b00.wp('eval', read)['stdout'].strip())
                old = b"$now = new DateTimeImmutable(gmdate('Y-m-d H:i:s'), new DateTimeZone('UTC'));"
                corrected = b"$now = self::$requestInstant ??= new DateTimeImmutable(gmdate('Y-m-d H:i:s'), new DateTimeZone('UTC'));"
                if current != data and current.replace(old, corrected) != data:
                    raise RuntimeError('Paywall partagé a évolué : refus de perdre C12/C13')
            c10.b00.upload(rel, data)
            code = 'echo base64_encode(file_get_contents(WP_CONTENT_DIR . ' + json.dumps('/' + rel) + '));'
            if c10.b00.wp('eval', code)['stdout'].strip() != base64.b64encode(data).decode():
                raise RuntimeError('Fichier différent : ' + rel)
        c10.b00.upload('imagine-demo-build/c11-migrate.php', (ROOT / 'wp/outils/demo/c11-migrate.php').read_bytes())
        migrated = json.loads(c10.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c11-migrate.php";')['stdout'])
        if len(migrated) != 5 or not all(row['private'] for row in migrated):
            raise RuntimeError('Migration incomplète')
        print('Migration privée : 5 numéros, relus.')
    # Recettes ciblées : fonctions média du seed seulement, jamais de reseed B00 global.
    for rel, source in {
        'imagine-demo-build/b00-seed.php': ROOT / 'wp/outils/demo/b00-seed.php',
        'imagine-demo-build/c11-seed-runtime.php': ROOT / 'wp/tests/demo/c11-seed-runtime.php',
        'imagine-demo-build/c11-runtime.php': ROOT / 'wp/tests/demo/c11-runtime.php',
    }.items():
        data = source.read_bytes()
        c10.b00.upload(rel, data)
        code = '$p=WP_CONTENT_DIR . ' + json.dumps('/' + rel) + ';token_get_all(file_get_contents($p),TOKEN_PARSE);echo base64_encode(file_get_contents($p));'
        if c10.b00.wp('eval', code)['stdout'].strip() != base64.b64encode(data).decode():
            raise RuntimeError('Test/seed différent : ' + rel)
    runtime = {'phpunit': {'total': int(counts[1]), 'assertions': int(counts[2]), 'success': True,
                           'runner': 'wp/outils/demo/c11-unit.py', 'discovery_T01': False}}
    for name in ['c11-seed-runtime', 'c11-runtime']:
        result = c10.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/' + name + '.php";')
        checks = json.loads(result['stdout'])
        if result['stderr'] or not checks or not all(v is True for v in checks.values()):
            raise RuntimeError('Recette PHP échouée : ' + name)
        runtime[name] = checks
        print(name + ' : ' + str(len(checks)) + ' / ' + str(len(checks)))
    (ROOT / 'production/C-11/runtime.json').write_text(json.dumps(runtime, ensure_ascii=False, indent=2), encoding='utf-8')
    if before != c10.guard()[1]:
        raise RuntimeError('Manifeste B00 modifié')
    spec = importlib.util.spec_from_file_location('c11_faults', ROOT / 'wp/tests/demo/c11-faults.py')
    faults = importlib.util.module_from_spec(spec); spec.loader.exec_module(faults)
    faults.verify()
    spec = importlib.util.spec_from_file_location('c11_verify', ROOT / 'wp/tests/demo/c11-verifier.py')
    verify = importlib.util.module_from_spec(spec); spec.loader.exec_module(verify)
    verify.verify()
    # Wheels universelles gelées B01, en lecture seule : pas d'installation ni de réseau.
    sys.path[:0] = [str(p) for p in (ROOT / 'production/B-01/validation').glob('*.whl')]
    transcript = io.StringIO()
    local = unittest.TextTestRunner(stream=transcript, verbosity=1).run(
        unittest.defaultTestLoader.discover(str(ROOT / 'wp/tests/demo'), pattern='test_*.py'))
    runtime['local_unit'] = {'total': local.testsRun, 'success': local.wasSuccessful(),
                             'failures': [str(t) for t, _ in local.failures + local.errors]}
    runtime['shared_C12_C13_preserved'] = shared == shared_state()
    if not runtime['shared_C12_C13_preserved']:
        raise RuntimeError('État partagé C12/C13 modifié')
    (ROOT / 'production/C-11/runtime.json').write_text(json.dumps(runtime, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Unitaires locaux :', local.testsRun, '; succès :', local.wasSuccessful())
    if not local.wasSuccessful():
        print(transcript.getvalue())
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    run(parser.parse_args().check_only)
