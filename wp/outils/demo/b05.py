"""B05 scoped code install and immutable receipts, fictional target only."""
from pathlib import Path
from datetime import datetime, timezone
import base64, copy, hashlib, json, re, subprocess, sys
sys.dont_write_bytecode = True
import c21
import profils
ROOT = profils.b00.ROOT
PROOF = ROOT / 'production/B-05'
wp = c21.wp
BLOCK = "require_once __DIR__ . '/Partenaires.php';\nPartenaires::register();\n\n"
NAMES = ['plugins/imagine-site/Partenaires.php', 'themes/imagine/functions.php',
         'themes/imagine/archive-imagine_partenaire.php']
# Shared plugin bootstrap is read by contract only; never deployed by B05 corrections.


def save(label, data):
    assert re.fullmatch(r'[a-zA-Z0-9-]+', label)
    PROOF.mkdir(parents=True, exist_ok=True)
    path = PROOF / (label + '.json')
    assert not path.exists(), 'Receipt already exists: ' + str(path)
    path.write_text(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(), scope='imagine-test-demo', **data), ensure_ascii=False, indent=2), encoding='utf-8')
    return data


def php_json(value):
    return 'json_decode(base64_decode("' + base64.b64encode(json.dumps(value, ensure_ascii=False).encode()).decode() + '"),true)'


def normalize(state):
    value = copy.deepcopy(state)
    for key in ('actionscheduler_actions', 'actionscheduler_logs'):
        value['native_fingerprints'].pop(key, None)
    return value


def state():
    return {'native': normalize(c21.c19.c18.state()), 'schedule_business': c21.schedule_business()}


def hashes(names=NAMES):
    return c21.hashes(names)


def baseline(label):
    profils.guard('imagine-test-demo')
    data = save(label, {'state': state(), 'source_before': hashes(), 'inventory': wp('echo wp_json_encode(["manifest"=>get_option("imagine_demo_manifest"),"partners"=>get_posts(["post_type"=>"imagine_partenaire","numberposts"=>-1,"post_status"=>"publish"])]);')})
    print(json.dumps({'receipt': label, 'partners': [(x['ID'],x['post_title']) for x in data['inventory']['partners']]}))


def deploy(label):
    profils.guard('imagine-test-demo')
    baseline = json.loads((PROOF / 'baseline.json').read_text(encoding='utf-8'))
    before = hashes()
    for name in NAMES:
        source = ROOT / 'wp' / name
        if not source.is_file():
            continue
        allowed = {baseline['source_before'][name], hashlib.sha256(source.read_bytes()).hexdigest()}
        for receipt in PROOF.glob('installation-*.json'):
            allowed.add(json.loads(receipt.read_text(encoding='utf-8'))['source_readback'].get(name))
        assert before[name] in allowed, 'Source drift: ' + name
    native = state()
    expected = {}
    for name in NAMES:
        source = ROOT / 'wp' / name
        if source.is_file():
            profils.b00.upload(name, source.read_bytes())
            expected[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    actual = hashes(list(expected))
    assert actual == expected
    assert native == state()
    save(label, {'source_before': before, 'source_readback': actual, 'native_preserved': True})
    print('B05 installation verified: ' + str(len(actual)) + ' files; native unchanged')


def runtime(label):
    profils.guard('imagine-test-demo')
    source = ROOT / 'wp/tests/demo/b05-runtime.php'
    name = 'imagine-demo-build/b05-runtime.php'
    profils.b00.upload(name, source.read_bytes())
    assert hashes([name])[name] == hashlib.sha256(source.read_bytes()).hexdigest()
    before = state()
    result = profils.b00.wp('eval', 'require WP_CONTENT_DIR."/' + name + '";', check=False)
    native = json.loads(result['stdout'])
    native.update(exit=result['code'], stderr=result['stderr'], state_preserved=before == state())
    save(label, native)
    print(json.dumps(native, ensure_ascii=False))
    assert not native['failures'] and not native['exit'] and not native['stderr'] and native['state_preserved']


def command(args, name):
    path = PROOF / name
    assert not path.exists()
    p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    path.write_text(p.stdout + p.stderr, encoding='utf-8')
    print(name, 'exit', p.returncode, (p.stdout + p.stderr)[-2200:])
    assert p.returncode == 0, name
    return p.stdout


if __name__ == '__main__':
    assert sys.argv[1] in ('baseline', 'deploy', 'runtime')
    globals()[sys.argv[1]](sys.argv[2])
