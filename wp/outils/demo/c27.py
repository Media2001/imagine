"""C27 — une cible fictive, préimages privées et lectures après écriture."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path
import b09
ROOT = b09.ROOT
PROOF = ROOT / 'production/C-27'
wp, php = b09.wp, b09.php
guard = b09.b08.c25.b06.guard
snapshot = b09.b08.snapshot
private = b09.b08.c25.private
state = b09.b08.c25.b06.state
upload = b09.b08.c25.b06.profils.b00.upload
NAMES = ['plugins/imagine-site/' + n for n in ['AcquisitionRegles.php', 'Acquisition.php', 'AcquisitionReglages.php', 'AcquisitionConfidentialite.php', 'AcquisitionAdmin.php']]
BLOCK = "// C27 — déclaration facultative après paiement seulement.\n" + ''.join("require_once __DIR__ . '/" + n.split('/')[-1] + "';\n" for n in NAMES) + 'Acquisition::register();\nAcquisitionReglages::register();\nAcquisitionConfidentialite::register();\nAcquisitionAdmin::register();\n\n'


def sources():
    paths = [ROOT/'wp'/n for n in NAMES]
    for pattern in ['wp/plugins/imagine-site/tests/Acquisition*', 'wp/outils/demo/c27*', 'wp/tests/demo/c27*']:
        paths += [p for p in ROOT.glob(pattern) if p.is_file()]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if p.is_file()}


def save(label, data):
    PROOF.mkdir(exist_ok=True)
    path = PROOF/(label+'.json')
    assert not path.exists(), path
    path.write_text(json.dumps({'scope':'imagine-test-demo', 'sources':sources(), **data}, ensure_ascii=False, indent=2), encoding='utf-8')


def local(label, mutation=''):
    command = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--user', '65534:65534', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--mount', 'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly', '--tmpfs', '/tmp:rw,nosuid,nodev,size=512m,mode=1777', '--entrypoint', 'php', 'imagine-tests-t01:1', '/repo/wp/tests/demo/c27-horslive.php']
    if mutation:
        command.append(mutation)
    p = subprocess.run(command, capture_output=True, encoding='utf-8')
    text = p.stdout+p.stderr
    path=PROOF/(label+'.log'); assert not path.exists(); path.write_text(text,encoding='utf-8')
    save(label, {'command':command, 'exit':p.returncode, 'log':path.name, 'log_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    print(text)
    return p.returncode


def deploy(label):
    identity=guard()
    boot='plugins/imagine-site/imagine-site.php'
    local=(ROOT/'wp'/boot).read_text(encoding='utf-8')
    assert local.count(BLOCK)==1
    old=wp('$v=[];foreach('+php(NAMES+[boot])+' as $n){$p=WP_CONTENT_DIR."/".$n;$v[$n]=is_file($p)?file_get_contents($p):null;}echo wp_json_encode($v);')
    assert old[boot] in [local,local.replace(BLOCK,'')], 'Bootstrap divergent'
    before=state(); durable=private('c27-'+label,{'database':snapshot(),'business':before,'files':old})
    for name in NAMES:
        allowed=[None,(ROOT/'wp'/name).read_text(encoding='utf-8')]
        for proof in PROOF.glob('deploy*.json'):
            prior=json.loads(proof.read_text(encoding='utf-8')).get('readback',{}).get(name)
            if old[name] is not None and hashlib.sha256(old[name].encode()).hexdigest()==prior:
                allowed.append(old[name])
        assert old[name] in allowed, 'Dérive: '+name
        upload(name,(ROOT/'wp'/name).read_bytes())
    upload(boot,(ROOT/'wp'/boot).read_bytes())
    hashes=b09.b08.c25.b06.hashes(NAMES+[boot])
    assert hashes=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in NAMES+[boot]}
    assert before==state()
    save(label,{'identity':identity,'private_snapshot':durable,'readback':hashes,'business_preserved':True})
    print('C27 déployé et relu, état métier inchangé')


if __name__=='__main__':
    assert sys.argv[1] in ['local','deploy']
    result=globals()[sys.argv[1]](*sys.argv[2:])
    if isinstance(result,int): raise SystemExit(result)
