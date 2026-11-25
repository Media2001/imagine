"""C15 targeted deploy and evidence: existing fictitious demo only, never theme."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import base64
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
import profils

ROOT = profils.b00.ROOT
PROOF = ROOT / 'production/C-15'
FILES = ['EcheancesRegles.php', 'EcheancesNatives.php', 'EcheancesAdmin.php', 'imagine-site.php']


def wp(code, check=True):
    raw = profils.b00.wp('eval', code, check=check)
    if raw['stderr']:
        raise RuntimeError('PHP warning/error; no private output logged')
    return json.loads(raw['stdout'])


def save(name, value):
    PROOF.mkdir(parents=True, exist_ok=True)
    (PROOF / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def upload(target, source):
    data = source.read_bytes()
    profils.b00.upload(target, data)
    readback = wp('$p=WP_CONTENT_DIR.' + json.dumps('/' + target) + ';token_get_all(file_get_contents($p),TOKEN_PARSE);echo wp_json_encode(hash_file("sha256",$p));')
    if readback != hashlib.sha256(data).hexdigest():
        raise RuntimeError('Readback mismatch: ' + target)
    return readback


def runtime(label):
    profils.guard('imagine-test-demo')
    upload('imagine-demo-build/c15-runtime.php', ROOT / 'wp/tests/demo/c15-runtime.php')
    checks = wp('require WP_CONTENT_DIR . "/imagine-demo-build/c15-runtime.php";')
    save(label, {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo', 'checks': checks, 'total': len(checks), 'failures': [k for k, v in checks.items() if v is not True]})
    print(json.dumps(checks, ensure_ascii=False))
    if not checks or not all(v is True for v in checks.values()):
        raise SystemExit(1)
    return checks


def deploy():
    profils.guard('imagine-test-demo')
    # Bootstrap: don't overwrite a concurrent or unknown change.
    remote = wp('echo wp_json_encode(base64_encode(file_get_contents(WP_PLUGIN_DIR."/imagine-site/imagine-site.php")));')
    local = (ROOT / 'wp/plugins/imagine-site/imagine-site.php').read_bytes()
    block = b"require_once __DIR__ . '/EcheancesRegles.php';\nrequire_once __DIR__ . '/EcheancesNatives.php';\nrequire_once __DIR__ . '/EcheancesAdmin.php';\nEcheancesAdmin::register();\n\n"
    if base64.b64decode(remote) not in (local, local.replace(block, b'')):
        raise RuntimeError('Concurrent bootstrap differs; no overwrite')
    hashes = {name: upload('plugins/imagine-site/' + name, ROOT / 'wp/plugins/imagine-site' / name) for name in FILES}
    save('installation', {'scope': 'imagine-test-demo', 'sha256_readback': hashes, 'theme_uploaded': False})


def load_test(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'wp/tests/demo' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--deploy', action='store_true')
    p.add_argument('--http', action='store_true')
    p.add_argument('--label', default='runtime')
    args = p.parse_args()
    if args.deploy:
        deploy()
    runtime(args.label)
    if args.http:
        load_test('c15-http').verify()
