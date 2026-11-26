"""C21: scoped native privacy adapter installation and test entrypoints."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
sys.dont_write_bytecode = True
import c19
ROOT = c19.ROOT
PROOF = ROOT / 'production/C-21'
wp = c19.wp
BLOCK = "require_once __DIR__ . '/ConfidentialiteRegles.php';\nrequire_once __DIR__ . '/Confidentialite.php';\nConfidentialite::register();\n\n"

def save(label, data):
    if not label.replace('-', '').isalnum():
        raise ValueError('Invalid receipt label')
    PROOF.mkdir(parents=True, exist_ok=True)
    path = PROOF / (label + '.json')
    if path.exists():
        raise RuntimeError('Receipt exists: ' + str(path))
    path.write_text(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(), scope='imagine-test-demo', **data), ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'receipt': path.name, 'checks': data.get('checks'), 'failures': data.get('failures')}))
    return data

def targets():
    return { 'plugins/imagine-site/' + n: ROOT / 'wp/plugins/imagine-site' / n for n in ('ConfidentialiteRegles.php', 'Confidentialite.php', 'EnvoiNatif.php', 'imagine-site.php') }

def hashes(names):
    return wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(names)) + ',true) as $n){$p=WP_CONTENT_DIR."/".$n;$out[$n]=is_file($p)?hash_file("sha256",$p):null;}echo wp_json_encode($out);')

def fixture(phase):
    path = ROOT / 'wp/tests/demo/c21-runtime.php'
    name = 'imagine-demo-build/c21-runtime.php'
    c19.c18.c17.profils.b00.upload(name, path.read_bytes())
    assert hashes([name])[name] == hashlib.sha256(path.read_bytes()).hexdigest()
    return wp('$phase=' + json.dumps(phase) + ';require WP_CONTENT_DIR."/' + name + '";')

def baseline(label):
    return save(label, {'native': c19.c18.state(), 'source_before': hashes(list(targets())), 'registration': fixture('registration')})

def deploy(label):
    before = json.loads((PROOF / 'baseline.json').read_text(encoding='utf-8'))
    actual = hashes(list(targets()))
    for name, p in targets().items():
        allowed = {before['source_before'][name], hashlib.sha256(p.read_bytes()).hexdigest()}
        if actual[name] not in allowed:
            raise RuntimeError('Source drift: ' + name)
    native = c19.c18.state()
    for name, path in targets().items():
        c19.c18.c17.profils.b00.upload(name, path.read_bytes())
    readback = hashes(list(targets()))
    assert readback == {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in targets().items()}
    assert native == c19.c18.state(), 'State drift during code-only install'
    return save(label, {'source_readback': readback, 'native_preserved': True, 'registration': fixture('registration')})

if __name__ == '__main__':
    c19.c18.c17.profils.guard('imagine-test-demo')
    mode = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else mode
    if mode in ('baseline', 'deploy'):
        globals()[mode](label)
    else:
        save(label, {'phase': mode, 'result': fixture(mode)})
