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
FILES = ['EcheancesRegles.php', 'EcheancesNatives.php', 'EcheancesAdmin.php']


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
    # C15 is already wired: never write the shared B02 bootstrap.
    remote = wp('echo wp_json_encode([hash_file("sha256",WP_PLUGIN_DIR."/imagine-site/imagine-site.php"),class_exists("Imagine\\\\Site\\\\EcheancesRegles"),class_exists("Imagine\\\\Site\\\\EcheancesNatives"),class_exists("Imagine\\\\Site\\\\EcheancesAdmin")]);')
    if remote[1:] != [True, True, True]:
        raise RuntimeError('C15 bootstrap absent; no shared-file overwrite permitted')
    hashes = {name: upload('plugins/imagine-site/' + name, ROOT / 'wp/plugins/imagine-site' / name) for name in FILES}
    after = wp('echo wp_json_encode(hash_file("sha256",WP_PLUGIN_DIR."/imagine-site/imagine-site.php"));')
    if after != remote[0]:
        raise RuntimeError('Concurrent bootstrap changed during upload; C15 did not write it')
    save('installation', {'scope': 'imagine-test-demo', 'sha256_readback': hashes, 'theme_uploaded': False, 'bootstrap_written': False, 'bootstrap_preserved': after == remote[0]})


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
