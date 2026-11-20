"""CLI sur fixtures synthétiques seulement. Aucun serveur ni donnée réelle."""
import json
import ast
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
    for refusal in ('IMAGINE_SYNTHETIC_OPEN_HOSTS', 'IMAGINE_SYNTHETIC_OPEN_HTTP', 'IMAGINE_SYNTHETIC_CRON'):
        r = subprocess.run([php, '-n', str(tests / 'mu-plugin.php')], capture_output=True,
                           env=dict(os.environ, **{refusal: 'yes'}))
        assert r.returncode == 78, refusal
    # Vraie chaîne de processus CLI, état synthétique persistant, aucune base réelle.
    state = root / 'synthetic-state.json'
    bridge.write_text("""<?php
require %s;
$context = ['environment'=>'staging','isolated'=>true,'restored'=>true,'database'=>'invented_staging','target_url'=>'https://invented.test','production_hosts'=>['production.invalid']];
$store = fixture();
$state = %s;
if (is_file($state)) { $saved = json_decode(file_get_contents($state), true, 32, JSON_THROW_ON_ERROR); $store->tables = $saved['tables']; $store->columns = $saved['columns']; }
else { $store->columns['synthetic_contacts'] = ['id','email','phone']; $store->tables['synthetic_contacts'] = [['id'=>1,'email'=>'contact@outside.invalid','phone'=>'SYNTHETIC']]; }
register_shutdown_function(static function () use ($store, $state) { file_put_contents($state, json_encode(['tables'=>$store->tables,'columns'=>$store->columns], JSON_THROW_ON_ERROR)); });
$probe = static fn () => ['mail_blocked'=>true, 'http_blocked'=>true, 'subscriptions_present'=>false, 'subscriptions_staging'=>null, 'environment_staging'=>true, 'cron_disabled'=>true, 'as_async_disabled'=>true, 'as_runner_disabled'=>true, 'gateways_disabled'=>true]; // UNIT ONLY: pas une preuve runtime.
return ['context'=>$context, 'store'=>$store, 'prefix'=>'x_', 'root'=>%s, 'probe'=>$probe];
""" % (json.dumps(str(tests / 'fixtures.php').replace('\\', '/')),
       json.dumps(str(state).replace('\\', '/')),
       json.dumps(str(root).replace('\\', '/'))), encoding='utf-8')
    assert invoke('neutraliser', args, env).returncode == 0
    assert invoke('anonymiser', args, env, secret + '\n').returncode == 0
    r = invoke('verifier', args, env)
    assert r.returncode == 1 and 'TABLE_PERSONNELLE_A_TRANCHER' in json.loads(r.stdout)['issues']
    report = json.loads(r.stdout)
    assert report['unknown_tables'][0]['rows'] == 1
    assert 'contact@outside.invalid' not in r.stdout and 'SYNTHETIC' not in r.stdout
    decisions = root / 'synthetic-decisions.json'
    decisions.write_text(json.dumps({'synthetic_contacts': {'action': 'anonymiser', 'columns': ['email', 'phone']}}), encoding='utf-8')
    with_decisions = [*args, '--table-decisions', str(decisions)]
    r = invoke('anonymiser', with_decisions, env, secret + '\n')
    assert r.returncode == 0, r.stdout + r.stderr
    r = invoke('verifier', with_decisions, env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(r.stdout)['ok'] is True and 'files' in json.loads(r.stdout)
    saved = json.loads(state.read_text(encoding='utf-8'))
    assert saved['tables']['synthetic_contacts'][0]['email'] == 'abonne-1@example.org'
    assert saved['tables']['synthetic_contacts'][0]['phone'] == ''
    saved['tables']['x_wc_orders'][0]['billing_email'] = 'trap@outside.invalid'
    state.write_text(json.dumps(saved), encoding='utf-8')
    r = invoke('verifier', with_decisions, env)
    assert r.returncode == 1 and 'EMAIL_EXTERNE' in json.loads(r.stdout)['issues']
    assert 'trap@outside.invalid' not in r.stdout
    decisions.write_text('{invalid', encoding='utf-8')
    assert invoke('neutraliser', with_decisions, env).returncode == 78
count = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(Path(__file__).read_text(encoding='utf-8')))) + 2  # three executions of loop assertion
print(f'OK {count} assertions CLI')
