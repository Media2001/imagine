"""Construction B-00 : cible fixe, sans destruction, sans secret dans le dépôt."""
from pathlib import Path
import time
import json
import base64
import subprocess
from urllib.error import HTTPError
from urllib.request import Request, urlopen

API = 'http://localhost:7000'


def request_api(method, path, payload=None):
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


def ensure_site(api=request_api, sleep=time.sleep):
    try:
        site = api('GET', '/api/sites/' + SLUG)
    except HTTPError as error:
        if error.code != 404:
            raise
        site = retry_busy(lambda: api('POST', '/api/sites', {
            'name': SLUG, 'template_slug': 'sandbox-wp-minimal', 'php_version': '8.3',
            'client_name': None, 'target_domain': None}), sleep)
    validate_target(site['slug'])
    for _ in range(180):
        if site['status'] == 'running':
            return site
        if site['status'] not in ('creating', 'starting', 'provisioning'):
            raise RuntimeError('Site non opérationnel : ' + site['status'])
        sleep(5)
        site = api('GET', '/api/sites/' + SLUG)
    raise TimeoutError('Création normale non terminée après 15 minutes')


class StagingBusy(RuntimeError):
    pass


def retry_busy(operation, sleep=time.sleep):
    for attempt in range(4):
        try:
            return operation()
        except StagingBusy:
            if attempt == 3:
                raise
            sleep(300)


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
    code = Path(__file__).with_name('b00_remote.py').read_text(encoding='utf-8')
    result = subprocess.run(['wsl.exe', 'docker', 'exec', '-i', 'staging-wp-dashboard', 'python', '-c', code],
                            input=json.dumps({'action': action, **payload}), capture_output=True,
                            text=True, encoding='utf-8', timeout=900)
    if result.returncode:
        raise RuntimeError('Échec du transport ciblé B-00 (code %d)' % result.returncode)
    return json.loads(result.stdout)


def upload(path, content):
    return remote('write', path=path, data=base64.b64encode(content).decode())


def wp(*args, check=True):
    result = remote('wp', args=list(args))
    if check and result['code']:
        raise RuntimeError('WP-CLI : ' + result['stderr'][-2500:])
    return result
