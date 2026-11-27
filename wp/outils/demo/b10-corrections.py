"""Corrections B10 seulement : déploiement ciblé et commandes parentes inchangées."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
import b10


def deploy(label):
    identity = b10.guard()
    before = b10.state()
    names = b10.FILES[:-1]
    old = b10.wp('$r=[];foreach(' + b10.php(names) + ' as $n){$r[$n]=file_get_contents(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($r);')
    baseline = json.loads((b10.OUT/'reception.json').read_text(encoding='utf-8'))['sha256']
    for name in names:
        assert hashlib.sha256(old[name].encode()).hexdigest() in {baseline['wp/'+name], hashlib.sha256((b10.ROOT/'wp'/name).read_bytes()).hexdigest()}
    durable = b10.b09.b08.c25.b06.private_snapshot(label, {'files': old, 'business': before})
    bootstrap = b10.b09.b08.c25.b06.hashes([b10.FILES[-1]])
    for name in names:
        b10.upload(name, (b10.ROOT/'wp'/name).read_bytes())
    hashes = b10.b09.b08.c25.b06.hashes(names)
    assert hashes == {n: hashlib.sha256((b10.ROOT/'wp'/n).read_bytes()).hexdigest() for n in names}
    assert before == b10.state()
    assert bootstrap == b10.b09.b08.c25.b06.hashes([b10.FILES[-1]])
    b10.save(label, {'identity': identity, 'private_snapshot': durable, 'readback': hashes, 'business_preserved': True, 'bootstrap_unchanged': True})
    print('B10 : deux classes déployées et relues ; bootstrap et état métier inchangés')


def gate(action, label):
    scripts = {'image': 'preparer-image.ps1', 'regression': 'rejouer.ps1'}
    assert action in scripts
    path = b10.OUT/(label+'.log')
    assert not path.exists()
    command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(b10.ROOT/'wp/tests'/scripts[action])]
    with path.open('xb') as stream:
        result = subprocess.run(command, cwd=b10.ROOT, stdout=stream, stderr=subprocess.STDOUT)
    b10.save(label, {'command': command, 'exit': result.returncode, 'log': path.name})
    print('\n'.join(path.read_bytes().decode('utf-8', 'replace').splitlines()[-12:]))
    return result.returncode


if __name__ == '__main__':
    if sys.argv[1] == 'deploy':
        deploy(sys.argv[2])
    else:
        raise SystemExit(gate(*sys.argv[1:]))
