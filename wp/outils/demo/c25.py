"""C25 : cible unique, snapshots privés durables, reçus immuables."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import b06

ROOT = b06.ROOT
PROOF = ROOT / 'production/C-25'
wp = b06.wp
php = b06.b05.php_json
NAMES = ['plugins/imagine-site/' + n for n in ['RetractationRegles.php', 'Retractation.php', 'RetractationReglages.php', 'RetractationConfidentialite.php']]
BLOCK = "// C25 — demande seule, sans effet financier ni accès.\nrequire_once __DIR__ . '/RetractationRegles.php';\nrequire_once __DIR__ . '/Retractation.php';\nrequire_once __DIR__ . '/RetractationReglages.php';\nrequire_once __DIR__ . '/RetractationConfidentialite.php';\nRetractation::register();\nRetractationReglages::register();\nRetractationConfidentialite::register();\n\n"


def save(label, data):
    PROOF.mkdir(exist_ok=True)
    path = PROOF / (label + '.json')
    assert not path.exists(), path
    path.write_text(json.dumps(dict(scope='imagine-test-demo', at=datetime.now(timezone.utc).isoformat(), **data), ensure_ascii=False, indent=2), encoding='utf-8')


def private(label, payload):
    folder = Path(tempfile.mkdtemp(prefix='c25-private-', dir=os.environ['TMPDIR']))
    path = folder / 'snapshot.json'
    raw = json.dumps(dict(scope='imagine-test-demo', label=label, payload=payload), ensure_ascii=False).encode()
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(path, 0o600)
    assert path.read_bytes() == raw
    return {'file': folder.name + '/snapshot.json', 'sha256': hashlib.sha256(raw).hexdigest(), 'private': True}


def snapshot():
    return wp('''global $wpdb;$out=[];foreach(['users','usermeta','posts','postmeta','comments','commentmeta','options'] as $name){$table=$wpdb->$name;$out[$name]=$wpdb->get_results("SELECT * FROM $table",ARRAY_A);if($wpdb->last_error){throw new RuntimeException('Snapshot incomplet');}}foreach($wpdb->get_col("SHOW TABLES LIKE '{$wpdb->prefix}actionscheduler_%'") as $table){$out[$table]=$wpdb->get_results("SELECT * FROM `$table`",ARRAY_A);}echo wp_json_encode($out);''')


def local(label, mutation=''):
    PROOF.mkdir(exist_ok=True)
    path = PROOF / (label + '.log')
    assert not path.exists()
    cmd = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--user', '65534:65534', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--mount', 'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly', '--tmpfs', '/tmp:rw,nosuid,nodev,size=512m,mode=1777', '--entrypoint', 'php', 'imagine-tests-t01:1', '/repo/wp/tests/demo/c25-horslive.php']
    if mutation:
        cmd.append(mutation)
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    path.write_text(p.stdout + p.stderr, encoding='utf-8')
    print(p.stdout + p.stderr)
    print('C25 EXIT', p.returncode)
    return p.returncode


def identity(label):
    save(label, {'identity': b06.guard(), 'versions': wp('global $wpdb;echo wp_json_encode(["wc"=>WC_VERSION,"db"=>$wpdb->db_version()]);')})


def deploy(label):
    identity = b06.guard()
    bootstrap = 'plugins/imagine-site/imagine-site.php'
    local_source = (ROOT / 'wp' / bootstrap).read_text(encoding='utf-8')
    old = wp('$out=[];foreach(' + php(NAMES + [bootstrap]) + ' as $n){$p=WP_CONTENT_DIR."/".$n;$out[$n]=is_file($p)?file_get_contents($p):null;}echo wp_json_encode($out);')
    assert old[bootstrap] in [local_source, local_source.replace(BLOCK, '')], 'Bootstrap distant divergent'
    before = b06.state()
    durable = private(label, {'files': old, 'database': snapshot(), 'business': before})
    for name in NAMES:
        assert old[name] is None or old[name] == (ROOT / 'wp' / name).read_text(encoding='utf-8'), 'Dérive C25'
        b06.profils.b00.upload(name, (ROOT / 'wp' / name).read_bytes())
    parsed = wp('$out=[];foreach(' + php(NAMES) + ' as $n){token_get_all(file_get_contents(WP_CONTENT_DIR."/".$n),TOKEN_PARSE);$out[$n]=true;}echo wp_json_encode($out);')
    assert all(parsed.values())
    assert wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/' + bootstrap + '"));') == old[bootstrap]
    b06.profils.b00.upload(bootstrap, (ROOT / 'wp' / bootstrap).read_bytes())
    actual = b06.hashes(NAMES + [bootstrap])
    assert actual == {n: hashlib.sha256((ROOT / 'wp' / n).read_bytes()).hexdigest() for n in NAMES + [bootstrap]}
    assert before == b06.state()
    save(label, {'identity': identity, 'private_snapshot': durable, 'readback': actual, 'business_preserved': True})


def gates(kind, label):
    script = {'prepare': 'wp/tests/preparer-image.ps1', 'regression': 'wp/tests/rejouer.ps1'}[kind]
    cmd = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script]
    path = PROOF / (label + '.log')
    assert not path.exists()
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace')
    text = result.stdout + result.stderr
    path.write_text(text, encoding='utf-8')
    print(text[-2000:])
    save(label, {'command': cmd, 'exit': result.returncode, 'log': path.name, 'log_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'results': [json.loads(line[11:]) for line in text.splitlines() if line.startswith('T01_RESULT ')]})
    assert result.returncode == 0


if __name__ == '__main__':
    assert sys.argv[1] in ['local', 'identity', 'deploy', 'gates']
    result = globals()[sys.argv[1]](*sys.argv[2:])
    if isinstance(result, int):
        raise SystemExit(result)
