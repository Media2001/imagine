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


if __name__ == '__main__':
    assert sys.argv[1] in ['local', 'identity']
    result = globals()[sys.argv[1]](*sys.argv[2:])
    if isinstance(result, int):
        raise SystemExit(result)
