"""B03 : dépôt ciblé du thème et exécution PHP, jamais de reseed."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/B-03'
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c08

FILES = ['assets/reading.js', 'assets/reading.css', 'assets/tokens.css', 'inc/reading.php', 'single.php', 'functions.php']


def wp(code):
    result = c08.b00.wp('eval', code)
    if result['stderr']:
        raise RuntimeError('Avertissement PHP B03 (sortie privée non reproduite)')
    return json.loads(result['stdout'])


def guard():
    site, state = c08.guard()
    if site['url'].rstrip('/') != 'http://192.168.129.32:8085' or wp('echo wp_json_encode(get_stylesheet());') != 'imagine':
        raise RuntimeError('Site ou thème B03 inattendu')
    return site, state


def deploy(phase):
    guard()
    sources = {('themes/imagine/' + rel): ROOT / 'wp/themes/imagine' / rel for rel in FILES if (ROOT / 'wp/themes/imagine' / rel).exists()}
    paths = json.dumps(json.dumps(list(sources)))
    old = wp('$out=[];foreach(json_decode(' + paths + ',true) as $f){$p=WP_CONTENT_DIR."/".$f;$out[$f]=file_exists($p)?base64_encode(file_get_contents($p)):null;}echo wp_json_encode($out);')
    PROOF.mkdir(parents=True, exist_ok=True)
    backup = PROOF / ('theme-before-' + phase + '.json')
    if not backup.exists():
        backup.write_text(json.dumps(old, indent=2), encoding='utf-8')
    expected = {}
    for path, source in sources.items():
        data = source.read_bytes()
        expected[path] = hashlib.sha256(data).hexdigest()
        c08.b00.upload(path, data)
    actual = readback(list(sources))
    if actual != expected:
        raise RuntimeError('Octets B03 distants différents')
    result = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo', 'phase': phase,
              'expected': expected, 'actual': actual, 'exact': actual == expected, 'files': len(expected), 'php_parsed': sum(p.endswith('.php') for p in expected)}
    (PROOF / ('deploy-' + phase + '.json')).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'phase': phase, 'files': len(expected), 'exact': actual == expected}))
    return result


def readback(paths):
    return wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(paths)) + ',true) as $f){$p=WP_CONTENT_DIR."/".$f;if(str_ends_with($f,".php")){token_get_all(file_get_contents($p),TOKEN_PARSE);}$out[$f]=hash_file("sha256",$p);}echo wp_json_encode($out);')


def runtime(phase):
    guard()
    source = ROOT / 'wp/tests/demo/b03-runtime.php'
    remote = 'imagine-demo-build/b03-runtime.php'
    c08.b00.upload(remote, source.read_bytes())
    assert readback([remote])[remote] == hashlib.sha256(source.read_bytes()).hexdigest()
    result = wp('require WP_CONTENT_DIR . "/' + remote + '";')
    result.update(at=datetime.now(timezone.utc).isoformat(), scope='imagine-test-demo', phase=phase)
    PROOF.mkdir(parents=True, exist_ok=True)
    (PROOF / ('php-' + phase + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    if result['failures']:
        raise SystemExit(1)
    return result


if __name__ == '__main__':
    {'deploy': deploy, 'php': runtime}[sys.argv[1]](sys.argv[2])
