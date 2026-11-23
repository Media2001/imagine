"""Transport strictement limité à imagine-test-demo, exécuté dans le dashboard."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys

SLUG = 'imagine-test-demo'
WP = 'wp-' + SLUG
CONTENT = Path('/app/sites') / SLUG / 'wp-content'
payload = json.load(sys.stdin)
action = payload['action']
if action == 'write':
    rel = Path(payload['path'])
    if rel.is_absolute() or '..' in rel.parts or rel.parts[0] not in ('mu-plugins', 'plugins', 'themes', 'imagine-demo-build'):
        raise ValueError('Écriture hors périmètre')
    path = CONTENT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(payload['data']))
    for parent in [path, *path.parents]:
        if parent == CONTENT.parent:
            break
        os.chown(parent, 33, 33)
    print(json.dumps({'written': str(rel)}))
elif action == 'wp':
    args = payload['args']
    if not args or args[0] not in ('core', 'plugin', 'theme', 'option', 'rewrite', 'eval-file', 'eval', 'language'):
        raise ValueError('Commande hors périmètre')
    r = subprocess.run(['docker', 'exec', '--user', 'www-data', WP, 'wp', *args], capture_output=True, text=True)
    print(json.dumps({'code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}))
elif action == 'credentials':
    import api.models as models
    site = models.get_site(SLUG)
    # Les secrets ne sortent que sur le pipe privé du constructeur, jamais dans un rapport.
    print(json.dumps({'admin_user': site['wp_admin_user'], 'admin_password': site['wp_admin_password']}))
elif action == 'seed-secret':
    r = subprocess.run(['docker', 'exec', '-i', '--user', 'www-data', WP, 'sh', '-c',
        'umask 077; mkdir -p /var/www/.imagine-demo; cat > /var/www/.imagine-demo/seed-secret.json'],
        input=json.dumps(payload['secret']), capture_output=True, text=True)
    print(json.dumps({'code': r.returncode}))
else:
    raise ValueError('Action inconnue')
