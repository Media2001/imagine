"""Non-régression C08 : invariants B00 et pages B01, preuves exclusivement C08."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c08
spec = importlib.util.spec_from_file_location('http_c08', Path(__file__).with_name('c08-verifier.py'))
http = importlib.util.module_from_spec(spec)
spec.loader.exec_module(http)
from b01_html import validate_html


def run():
    site, before = c08.guard()
    base = site['url'].rstrip('/')
    checks, pages = {}, {}
    c08.b00.upload('imagine-demo-build/b00-snapshot.php', Path(__file__).with_name('b00-snapshot.php').read_bytes())
    snapshot = json.loads(c08.b00.wp('eval', 'require ABSPATH . "wp-content/imagine-demo-build/b00-snapshot.php";')['stdout'])
    initial = json.loads((c08.ROOT / 'production/B-00/tests/b00-snapshot-initial.json').read_text(encoding='utf-8'))
    checks['snapshot_b00_exact_ids_slugs_textes_medias'] = snapshot == initial
    checks['b00_sans_doublon'] = snapshot['duplicates'] == []
    checks['b00_manifeste_complet'] = snapshot['total_tagged'] == snapshot['manifest_posts']
    libraries = {}
    for name in ['imagine-pilotage', 'imagine-connecteur']:
        for file in (c08.ROOT / 'wp/plugins' / name / 'src').rglob('*.php'):
            libraries['plugins/' + name + '/src/' + file.relative_to(c08.ROOT / 'wp/plugins' / name / 'src').as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    code = '$names=json_decode(' + json.dumps(json.dumps(list(libraries))) + ',true);$out=[];foreach($names as $name){$out[$name]=hash_file("sha256",WP_CONTENT_DIR . "/" . $name);}echo wp_json_encode($out);'
    actual = json.loads(c08.b00.wp('eval', code)['stdout'])
    checks['bibliotheques_closes_octets_exacts'] = libraries == actual
    for key, row in snapshot['rows'].items():
        if key.startswith('user:'):
            continue
        url = row.get('file_url') or row['url']
        if not url.startswith(base + '/'):
            raise RuntimeError('URL B00 hors cible')
        meta, text = http.fetch(base, url[len(base):])
        checks[key + ':200'] = meta['status'] == 200
        pages[key] = meta
        if 'reserve-' in key:
            checks[key + ':reserve_absent'] = 'CONTENU_FICTIF_RESERVE_' not in text and http.WITNESS not in text
        if not row.get('file_url') and row.get('type') not in ['attachment']:
            # Les ressources non HTML ne sont pas passées au validateur structurel.
            if 'text/html' in meta['headers'].get('content-type', ''):
                checks[key + ':html_semantique'] = not validate_html(text)
    for key, path, status in [('accueil', '/', 200), ('kiosque', '/numeros/', 200), ('agenda', '/evenements/', 200),
                              ('partenaires', '/partenaires/', 200), ('recherche', '/?s=fictif', 200),
                              ('404', '/c08-inexistant-xyz/', 404), ('article-c08', '/c08-article-reserve-article/', 200)]:
        meta, text = http.fetch(base, path)
        pages[key] = meta
        checks[key + ':status'] = meta['status'] == status
        checks[key + ':html5'] = not validate_html(text)
        checks[key + ':aucun_corps_reserve'] = http.WITNESS not in text and 'CONTENU_FICTIF_RESERVE_' not in text
    credentials = json.loads((Path.home() / '.imagine-demo/c08-identifiants.json').read_text(encoding='utf-8'))
    client = http.login(base, credentials['accounts']['actif'])
    meta, full = http.fetch(base, '/demo-2026-t1-reserve-1/', client)
    checks['article_b00_abonne_complet'] = meta['status'] == 200 and 'CONTENU_FICTIF_RESERVE_DEMO-2026-T1_1' in full
    checks['manifeste_b00_final_exact'] = c08.guard()[1] == before
    failures = [k for k, v in checks.items() if not v]
    record = {'scope': c08.b00.SLUG, 'total': len(checks), 'passed': len(checks)-len(failures), 'failures': failures,
              'checks': checks, 'pages': pages, 'library_php_files': len(libraries), 'library_sha256': actual,
              'baseline_tagged_objects': snapshot['total_tagged']}
    (c08.PROOF / 'regression.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: record[k] for k in ['scope', 'total', 'passed', 'failures', 'library_php_files', 'baseline_tagged_objects']}, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    run()
