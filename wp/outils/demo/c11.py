"""Installer/rejouer C11 uniquement sur la démonstration fictive existante."""
from pathlib import Path
import argparse
import base64
import importlib.util
import json
import c10
from b00_fixtures import fixture_data, dummy_pdf

ROOT = c10.ROOT
FILES = ['plugins/imagine-site/PdfNumero.php', 'plugins/imagine-site/Paywall.php',
         'plugins/imagine-site/imagine-site.php', 'themes/imagine/single-imagine_numero.php']


def run(check_only=False):
    site, before = c10.guard()
    if not check_only:
        c10.b00.remote('pdf-private-init')
        for issue in fixture_data()['issues']:
            c10.b00.remote('pdf-source', name=issue['slug'] + '.pdf', data=base64.b64encode(dummy_pdf(issue['label'])).decode())
        for rel in FILES:
            data = (ROOT / 'wp' / rel).read_bytes()
            c10.b00.upload(rel, data)
            code = 'echo base64_encode(file_get_contents(WP_CONTENT_DIR . ' + json.dumps('/' + rel) + '));'
            if c10.b00.wp('eval', code)['stdout'].strip() != base64.b64encode(data).decode():
                raise RuntimeError('Fichier différent : ' + rel)
        c10.b00.upload('imagine-demo-build/c11-migrate.php', (ROOT / 'wp/outils/demo/c11-migrate.php').read_bytes())
        migrated = json.loads(c10.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c11-migrate.php";')['stdout'])
        if len(migrated) != 5 or not all(row['private'] for row in migrated):
            raise RuntimeError('Migration incomplète')
        print('Migration privée : 5 numéros, relus.')
    if before != c10.guard()[1]:
        raise RuntimeError('Manifeste B00 modifié')
    spec = importlib.util.spec_from_file_location('c11_verify', ROOT / 'wp/tests/demo/c11-verifier.py')
    verify = importlib.util.module_from_spec(spec); spec.loader.exec_module(verify)
    verify.verify()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    run(parser.parse_args().check_only)
