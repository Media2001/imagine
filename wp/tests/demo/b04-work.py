"""B04 transport ciblé, sans seed, sans plugin ni fixture persistante."""
from pathlib import Path
from datetime import datetime, timezone
import base64
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROOF = ROOT / 'production/B-04'
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c08
FILES = ['functions.php', 'inc/catalogue.php', 'single-imagine_numero.php', 'archive-imagine_numero.php', 'taxonomy-imagine_thematique.php']

def wp(code):
    r = c08.b00.wp('eval', code)
    if r['stderr']:
        raise RuntimeError('Avertissement PHP ; sortie privée non reproduite')
    return json.loads(r['stdout'])

def guard():
    site, state = c08.guard()
    assert site['url'].rstrip('/') == 'http://192.168.129.32:8085'
    assert wp('echo wp_json_encode(get_stylesheet());') == 'imagine'
    PROOF.mkdir(parents=True, exist_ok=True)
    return site, state

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def readback(paths):
    return wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(paths)) + ',true) as $f){$p=WP_CONTENT_DIR."/".$f;$out[$f]=is_file($p)?hash_file("sha256",$p):null;}echo wp_json_encode($out);')

def deploy(phase):
    guard()
    paths = ['themes/imagine/' + p for p in FILES if (ROOT / 'wp/themes/imagine' / p).is_file()]
    old = wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(paths)) + ',true) as $f){$p=WP_CONTENT_DIR."/".$f;$out[$f]=is_file($p)?base64_encode(file_get_contents($p)):null;}echo wp_json_encode($out);')
    backup = PROOF / ('theme-before-' + phase + '.json')
    assert not backup.exists(), 'Ne pas écraser une préimage'
    backup.write_text(json.dumps(old, indent=2), encoding='utf-8')
    expected = {p:digest(ROOT / 'wp' / p) for p in paths}
    # Lint avec le vrai runtime avant de remplacer les fichiers actifs.
    for path in paths:
        source = ROOT / 'wp' / path
        candidate = 'imagine-demo-build/b04-lint-' + source.name
        c08.b00.upload(candidate, source.read_bytes())
        assert wp('token_get_all(file_get_contents(WP_CONTENT_DIR . "/' + candidate + '"),TOKEN_PARSE);echo "true";') is True
    for path in paths:
        c08.b00.upload(path, (ROOT / 'wp' / path).read_bytes())
    actual = readback(paths)
    assert actual == expected
    result = {'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','expected':expected,'actual':actual,'exact':True,'files':len(paths)}
    (PROOF / ('deploy-' + phase + '.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'phase':phase,'files':len(paths),'exact':True}))
    return result

def runtime(phase):
    guard()
    source = HERE / 'b04-runtime.php'
    target = 'imagine-demo-build/b04-runtime.php'
    c08.b00.upload(target, source.read_bytes())
    assert readback([target])[target] == digest(source)
    result = wp('require WP_CONTENT_DIR . "/' + target + '";')
    result.update(at=datetime.now(timezone.utc).isoformat(),scope='imagine-test-demo')
    (PROOF / ('php-' + phase + '.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
    if result['failures']: raise SystemExit(1)
    return result

if __name__ == '__main__':
    {'deploy':deploy,'php':runtime}[sys.argv[1]](sys.argv[2])
