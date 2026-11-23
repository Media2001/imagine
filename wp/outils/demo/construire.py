"""Construction B-00 : cible fixe, sans destruction, sans secret dans le dépôt."""
from pathlib import Path
import time
import json
import base64
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from b00_fixtures import fixture_data, cover_png, dummy_pdf
from urllib.error import HTTPError
from urllib.request import Request, urlopen

API = 'http://localhost:7000'


def request_api(method, path, payload=None):
    return retry_busy(lambda: _request_api(method, path, payload), mutation=method != 'GET')


def _request_api(method, path, payload=None):
    if path not in ('/api/sites', '/api/sites/imagine-test-demo'):
        raise ValueError('Route hors périmètre')
    request = Request(API + path, data=json.dumps(payload).encode() if payload is not None else None,
                      headers={'Content-Type': 'application/json'}, method=method)
    try:
        with urlopen(request, timeout=60) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code in (409, 423):
            raise StagingBusy('Outil occupé') from None
        raise


def ensure_site(api=None, sleep=None):
    sleep = sleep or time.sleep
    # Une seule boucle de reprise par appel, y compris avec un transport injecté.
    raw_api = api or _request_api
    def call(method, path, payload=None):
        return retry_busy(lambda: raw_api(method, path, payload), sleep, mutation=method != 'GET')
    try:
        site = call('GET', '/api/sites/' + SLUG)
    except HTTPError as error:
        if error.code != 404:
            raise
        site = call('POST', '/api/sites', {
            'name': SLUG, 'template_slug': 'sandbox-wp-minimal', 'php_version': '8.3',
            'client_name': None, 'target_domain': None})
    validate_target(site['slug'])
    for _ in range(180):
        if site['status'] == 'running':
            return site
        if site['status'] not in ('creating', 'starting', 'provisioning'):
            raise RuntimeError('Site non opérationnel : ' + site['status'])
        sleep(5)
        site = call('GET', '/api/sites/' + SLUG)
    raise TimeoutError('Création normale non terminée après 15 minutes')


class StagingBusy(RuntimeError):
    pass


def retry_busy(operation, sleep=None, mutation=True):
    """Mutations : 3 reprises à 5 min ; lectures : jusqu'à 12 reprises à 5 s.

    Une lecture durablement refusée s'arrête proprement, sans boucle infinie.
    Aucun appelant n'enveloppe une seconde fois ce transport.
    """
    sleep = sleep or time.sleep
    retries, delay = (3, 300) if mutation else (12, 5)
    for attempt in range(retries + 1):
        try:
            return operation()
        except StagingBusy:
            if attempt == retries:
                kind = 'mutation (trois reprises à cinq minutes)' if mutation else 'lecture (douze reprises à cinq secondes)'
                raise StagingBusy('Outil occupé : ' + kind + ' épuisées ; aucune opération forcée') from None
            sleep(delay)


SLUG = 'imagine-test-demo'
ROOT = Path(__file__).resolve().parents[3]


def validate_target(slug):
    if slug != SLUG:
        raise ValueError('Seul imagine-test-demo est autorisé')


def validate_credentials_path(path):
    path = Path(path).resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError('Les identifiants doivent rester hors dépôt')
    return path


def remote(action, **payload):
    return retry_busy(lambda: _remote(action, **payload), mutation=action not in ('credentials', 'requirements'))


def _remote(action, **payload):
    code = Path(__file__).with_name('b00_remote.py').read_text(encoding='utf-8')
    result = subprocess.run(['wsl.exe', 'docker', 'exec', '-i', 'staging-wp-dashboard', 'python', '-c', code],
                            input=json.dumps({'action': action, **payload}), capture_output=True,
                            text=True, encoding='utf-8', timeout=900)
    if result.returncode:
        raise RuntimeError('Échec du transport ciblé B-00 (code %d)' % result.returncode)
    data = json.loads(result.stdout)
    if data.get('busy') is True or data.get('status_code') in (409, 423) or data.get('code') in (409, 423):
        raise StagingBusy('Transport ciblé occupé')
    return data


def upload(path, content):
    return remote('write', path=path, data=base64.b64encode(content).decode())


def wp(*args, check=True):
    result = remote('wp', args=list(args))
    if check and result['code']:
        raise RuntimeError('WP-CLI : ' + result['stderr'][-2500:])
    return result


def activate_theme():
    """Branchement B-01 seul : aucun reseed ni installation d'extension B-00."""
    import hashlib
    site = request_api('GET', '/api/sites/' + SLUG)
    validate_target(site['slug'])
    if site['status'] != 'running':
        raise RuntimeError('Le site fictif doit déjà être démarré ; aucune création B-01')
    guard_code = 'echo wp_json_encode(["environment"=>wp_get_environment_type(),"demo"=>get_option("imagine_demo_site"),"manifest"=>get_option("imagine_demo_manifest")]);'
    before = json.loads(wp('eval', guard_code)['stdout'])
    if before.get('environment') != 'local' or before.get('demo') != SLUG:
        raise RuntimeError('La garde fictive locale B-00 manque ; aucune écriture du thème')
    theme = ROOT / 'wp/themes/imagine'
    if not (theme / 'style.css').is_file() or not (theme / 'index.php').is_file():
        raise RuntimeError('Le thème B-01 est incomplet')
    hashes = {}
    for source in sorted(theme.rglob('*')):
        if source.is_file() and source.suffix in ('.php', '.css', '.js', '.json', '.html', '.svg', '.png', '.woff2'):
            rel = source.relative_to(theme).as_posix()
            content = source.read_bytes()
            hashes[rel] = hashlib.sha256(content).hexdigest()
            upload('themes/imagine/' + rel, content)
    # Parse chaque fichier PHP avant activation, puis relis les octets exacts.
    verify_code = '$files=json_decode(' + json.dumps(json.dumps(list(hashes))) + ',true);$out=[];foreach($files as $f){$p=WP_CONTENT_DIR . "/themes/imagine/" . $f;if(str_ends_with($f,".php")){token_get_all(file_get_contents($p),TOKEN_PARSE);}$out[$f]=hash_file("sha256",$p);}echo wp_json_encode($out);'
    actual = json.loads(wp('eval', verify_code)['stdout'])
    if hashes != actual:
        raise RuntimeError('Le thème téléversé diffère de la source')
    activated = wp('theme', 'activate', 'imagine')
    after = json.loads(wp('eval', guard_code)['stdout'])
    active = wp('eval', 'echo get_stylesheet();')['stdout'].strip()
    if active != 'imagine' or before != after:
        raise RuntimeError('Activation non relue ou manifeste B-00 modifié')
    return {'scope': SLUG, 'url': site.get('url'), 'active_theme': active, 'activation': activated,
            'files_sha256': actual, 'php_parsed': sum(name.endswith('.php') for name in hashes),
            'b00_manifest_unchanged': True, 'file_count': len(hashes)}


def run_theme_only():
    from datetime import datetime, timezone
    proof = ROOT / 'production/B-01'
    proof.mkdir(parents=True, exist_ok=True)
    result = {'scope': SLUG, 'at': datetime.now(timezone.utc).isoformat()}
    try:
        result.update(activate_theme())
        result['status'] = 'VERIFIED'
    except Exception as error:
        result.update(status='BLOCKED', error=str(error))
        raise
    finally:
        (proof / 'installation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def run_build(label='construction'):
    from datetime import datetime, timezone
    import hashlib
    import os
    import secrets

    proof = ROOT / 'production/B-00'
    proof.mkdir(parents=True, exist_ok=True)
    record = {'started_at': datetime.now(timezone.utc).isoformat(), 'scope': SLUG, 'label': label, 'steps': []}
    def save():
        (proof / ('b00-' + label + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    def step(name, result):
        record['steps'].append({'name': name, 'result': result})
        save()
        print(name, ': OK', flush=True)
    try:
        try:
            before = request_api('GET', '/api/sites/' + SLUG)
            existed = True
        except HTTPError as error:
            if error.code != 404:
                raise
            existed = False
        site = ensure_site()
        step('creation-normale-ou-reprise', {**{k: site.get(k) for k in ['slug', 'status', 'url', 'port', 'template_slug', 'created_at']}, 'already_present': existed})
        tools = Path(__file__).resolve().parent
        upload('mu-plugins/imagine-demo-offline.php', (tools / 'imagine-demo-offline.php').read_bytes())
        step('garde-hors-ligne-avant-extensions', wp('eval', 'echo json_encode(["mail" => wp_mail("demo@example.org", "test fictif", "test"), "http" => is_wp_error(wp_remote_get("https://example.org"))]);'))
        credentials_path = validate_credentials_path(Path.home() / '.imagine-demo/identifiants.json')
        credentials_path.parent.mkdir(parents=True, exist_ok=True)
        credentials = json.loads(credentials_path.read_text(encoding='utf-8')) if credentials_path.exists() else {}
        credentials.update(remote('credentials'))
        credentials.setdefault('editor_user', 'imagine-demo-redaction')
        credentials.setdefault('editor_password', secrets.token_urlsafe(24))
        credentials.setdefault('article_password', secrets.token_urlsafe(24))
        credentials['url'] = site['url']
        credentials_path.write_text(json.dumps(credentials, ensure_ascii=False, indent=2), encoding='utf-8')
        os.chmod(credentials_path, 0o600)
        sent = remote('seed-secret', secret=credentials)
        if sent.get('code') != 0:
            raise RuntimeError('Secret local non transmis')
        record['credentials_file'] = str(credentials_path)
        print('Identifiants de test hors dépôt : ' + str(credentials_path), flush=True)
        requirements = remote('requirements')
        expected = {'woocommerce-subscriptions': '9.4.1', 'woocommerce-memberships': '1.30.3'}
        if any(requirements[k]['headers']['Version'] != v for k, v in expected.items()):
            raise RuntimeError('Les ZIP premium ont changé : minima et compatibilité à relire')
        step('versions-et-minima-zip-ced', requirements)
        current = wp('core', 'version')['stdout'].strip()
        if current != '7.0.9':
            step('wordpress-7.0.9', wp('core', 'update', '--version=7.0.9', '--force'))
            step('wordpress-base', wp('core', 'update-db'))
        plugins = json.loads(wp('plugin', 'list', '--format=json')['stdout'])
        versions = {p['name']: p['version'] for p in plugins}
        if versions.get('woocommerce') != '11.2.2':
            url = 'https://downloads.wordpress.org/plugin/woocommerce.11.2.2.zip'
            with urlopen(url, timeout=120) as response:
                package = response.read()
            step('woocommerce-source-primaire', {'source': url, 'sha256': hashlib.sha256(package).hexdigest()})
            upload('imagine-demo-build/woocommerce.11.2.2.zip', package)
            step('woocommerce-installation', wp('plugin', 'install', 'wp-content/imagine-demo-build/woocommerce.11.2.2.zip', '--force', '--activate'))
        else:
            step('woocommerce-actif', wp('plugin', 'activate', 'woocommerce'))
        for name, version in expected.items():
            if versions.get(name) != version:
                step(name + '-installation', wp('plugin', 'install', '/premium-plugins/' + name + '.zip', '--force', '--activate'))
            else:
                step(name + '-actif', wp('plugin', 'activate', name))
        # Les seules bibliothèques closes nécessaires sont copiées en lecture seule depuis src/.
        for name in ('imagine-pilotage', 'imagine-connecteur'):
            for source in sorted((ROOT / 'wp/plugins' / name / 'src').rglob('*.php')):
                upload('plugins/' + name + '/src/' + source.relative_to(ROOT / 'wp/plugins' / name / 'src').as_posix(), source.read_bytes())
        plugin = ROOT / 'wp/plugins/imagine-site'
        for source in sorted(plugin.rglob('*.php')):
            upload('plugins/imagine-site/' + source.relative_to(plugin).as_posix(), source.read_bytes())
        step('imagine-site-actif', wp('plugin', 'activate', 'imagine-site'))
        data = fixture_data()
        snapshot_source = ROOT / 'wp/tests/demo/b00-snapshot.php'
        upload('imagine-demo-build/b00-snapshot.php', snapshot_source.read_bytes())
        previous_snapshot = json.loads(wp('eval', 'require ABSPATH . "wp-content/imagine-demo-build/b00-snapshot.php";')['stdout'])
        upload('imagine-demo-build/b00-fixture.json', json.dumps(data, ensure_ascii=False).encode())
        for issue in data['issues']:
            upload('imagine-demo-build/assets/' + issue['slug'] + '.png', cover_png(issue['label'], issue['color']))
            upload('imagine-demo-build/assets/' + issue['slug'] + '.pdf', dummy_pdf(issue['label']))
        upload('imagine-demo-build/b00-seed.php', (tools / 'b00-seed.php').read_bytes())
        step('adresses-lisibles', wp('rewrite', 'structure', '/%postname%/'))
        seeded = wp('eval', 'require ABSPATH . "wp-content/imagine-demo-build/b00-seed.php";')
        step('contenus-fictifs-reconstruits', json.loads(seeded['stdout']))
        # Après le seed : la garde fictive existe aussi lors d'une construction neuve.
        theme = ROOT / 'wp/themes/imagine'
        if (theme / 'style.css').is_file():
            step('theme-imagine', activate_theme())
        else:
            step('theme-par-defaut-en-attente-de-B01', wp('theme', 'list', '--status=active', '--format=json'))
        upload('imagine-demo-build/b00-recette.php', (ROOT / 'wp/tests/demo/b00-recette.php').read_bytes())
        tested = wp('eval', 'require ABSPATH . "wp-content/imagine-demo-build/b00-recette.php";', check=False)
        step('recette-runtime', tested)
        if tested['code']:
            raise RuntimeError('La recette réelle échoue ; voir la preuve, aucun PRET')
        step('pile-finale', {'wordpress': wp('core', 'version')['stdout'].strip(),
                            'plugins': json.loads(wp('plugin', 'list', '--format=json')['stdout'])})
        snapshot = json.loads(wp('eval', 'require ABSPATH . "wp-content/imagine-demo-build/b00-snapshot.php";')['stdout'])
        step('snapshot-identifiants-contenus-medias', snapshot)
        if snapshot['duplicates'] or snapshot['total_tagged'] != snapshot['manifest_posts']:
            raise RuntimeError('Inventaire divergent ou doublons')
        if previous_snapshot['rows'] and previous_snapshot != snapshot:
            raise RuntimeError('Reconstruction non identique : identifiants, contenus ou adresses modifiés')
        step('idempotence-interne', {'compared_to_existing': bool(previous_snapshot['rows']), 'identical': previous_snapshot == snapshot if previous_snapshot['rows'] else None})
        record['status'] = 'VERIFIED_RUNTIME'
        record['finished_at'] = datetime.now(timezone.utc).isoformat()
        save()
        return record
    except Exception as error:
        record['status'] = 'BLOCKED'
        record['error'] = str(error)
        save()
        raise


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='B-00 — imagine-test-demo seulement, sans destruction')
    parser.add_argument('--preuve', choices=['construction', 'reconstruction'], default='construction')
    parser.add_argument('--theme-only', action='store_true', help='B-01 seul, site existant, preuves dans production/B-01')
    args = parser.parse_args()
    if args.theme_only:
        run_theme_only()
    else:
        run_build(args.preuve)
