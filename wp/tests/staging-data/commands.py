"""CLI sur fixtures synthétiques seulement. Aucun serveur ni donnée réelle."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

php = os.environ['PHP_BIN']
base = Path(__file__).resolve().parents[2] / 'outils' / 'staging'
tests = Path(__file__).resolve().parent
scratch = os.environ['IMAGINE_TEST_SCRATCH']


def invoke(phase, args=(), env=None, secret=''):
    return subprocess.run([php, '-n', str(base / phase), *args], input=secret,
                          text=True, capture_output=True, env=env or os.environ.copy())


r = invoke('neutraliser')
assert r.returncode != 0
assert 'STAGING_REFUSE' in r.stdout
with tempfile.TemporaryDirectory(prefix='imagine-synthetic-cli-', dir=scratch) as d:
    root = Path(d)
    (root / 'wp-content').mkdir()
    (root / '.imagine-staging-offline').write_bytes(b'OFFLINE_COPY\n')
    bridge = root / 'synthetic-bridge.php'
    bridge.write_text("""<?php
require %s;
$context = ['environment'=>'staging','isolated'=>true,'restored'=>true,'database'=>'invented_staging','target_url'=>'https://invented.test','production_hosts'=>['production.invalid']];
return ['context'=>$context, 'store'=>fixture(), 'prefix'=>'x_', 'root'=>%s];
""" % (json.dumps(str(tests / 'fixtures.php').replace('\\', '/')),
       json.dumps(str(root).replace('\\', '/'))), encoding='utf-8')
    env = dict(os.environ, WP_ENVIRONMENT_TYPE='staging')
    args = ['--worker-bridge', str(bridge)]
    r = invoke('neutraliser', args, env)
    if r.returncode != 0:
        debug = 'require ' + json.dumps(str(base / 'command.php').replace('\\', '/')) + '; $worker = require ' + json.dumps(str(bridge).replace('\\', '/')) + '; $engine = new Imagine\\Staging\\Engine($worker["store"], $worker["context"], "x_"); $files = new Imagine\\Staging\\Files($worker["root"]); $files->purge(); $engine->neutraliser();'
        diagnostic = subprocess.run([php, '-n', '-r', debug], capture_output=True, text=True, env=env)
        raise AssertionError(diagnostic.stdout + diagnostic.stderr)
    assert json.loads(r.stdout)['ok'] is True
    secret = 'SYNTHETIC-test-password-2026'
    r = invoke('anonymiser', args, env, secret + '\n')
    assert r.returncode == 0, r.stdout + r.stderr
    assert secret not in r.stdout + r.stderr
    r = invoke('verifier', args, env)
    assert r.returncode != 0, 'La fixture non anonymisée doit échouer sans sonde'
    assert secret not in r.stdout + r.stderr
    r = invoke('anonymiser', args, env, 'short\n')
    assert r.returncode != 0
    r = invoke('neutraliser', args, dict(env, WP_ENVIRONMENT_TYPE='production'))
    assert r.returncode == 78
    r = subprocess.run([php, '-n', str(tests / 'mu-plugin.php')], capture_output=True,
                       env=dict(os.environ, IMAGINE_SYNTHETIC_ENV='production'))
    assert r.returncode == 78
print('OK 10 assertions CLI')
