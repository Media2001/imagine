"""Corrections B08 : seules écritures sur la démonstration fictive gardée."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path
import b08


def remove_remote(names):
    code = 'import pathlib,json;root=pathlib.Path("/app/sites/imagine-test-demo/wp-content");names=' + repr(names) + ';[(root/n).unlink() for n in names];print(json.dumps(all(not (root/n).exists() for n in names)))'
    p = subprocess.run(['wsl.exe', 'docker', 'exec', 'staging-wp-dashboard', 'python', '-c', code], capture_output=True, encoding='utf-8')
    assert p.returncode == 0 and json.loads(p.stdout) is True


def runtime(label, case='reprise', mutation=''):
    b08.c25.b06.guard()
    before = b08.snapshot()
    business = b08.c25.b06.state()
    durable = b08.c25.private(label, {'database': before, 'business': business})
    names = ['imagine-demo-build/b08-seed.php', 'imagine-demo-build/b08-seed-' + case + '.php']
    assert all(not v for v in b08.wp('$v=[];foreach(' + b08.php(names) + ' as $n){$v[$n]=file_exists(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($v);').values())
    result = {}
    try:
        for name, source in zip(names, [b08.ROOT / 'wp/outils/demo/b08-seed.php', b08.ROOT / ('wp/tests/demo/b08-seed-' + case + '.php')]):
            raw = source.read_bytes()
            if source.name == 'b08-seed.php' and mutation:
                mutations = {
                    'item-etranger': ("throw new RuntimeException('Item étranger');", '/* témoin de garde retirée */', 1),
                    'cible-absente': ("$pageUrl(wc_get_page_id('myaccount'))", "wc_get_page_permalink('myaccount')", 1),
                }
                old, new, count = mutations[mutation]
                assert old in raw.decode('utf-8')
                raw = raw.decode('utf-8').replace(old, new, count).encode('utf-8')
            b08.c25.b06.profils.b00.upload(name, raw)
        result = b08.wp('require WP_CONTENT_DIR."/' + names[1] + '";')
    finally:
        remove_remote(names)
        after = b08.snapshot()
        exact = {k: before[k] == after[k] for k in before if k not in ['options', 'actionscheduler_actions', 'actionscheduler_logs', 'actionscheduler_groups', 'actionscheduler_claims']}
        opts = lambda db: [r for r in db['options'] if r['option_name'].startswith('imagine_') or r['option_name'] == 'cron']
        exact['options_metier'] = opts(before) == opts(after)
        equal = business == b08.c25.b06.state()
        b08.save(label, {**result, 'mutation': mutation, 'private_snapshot': durable, 'exact_restoration': exact, 'business_preserved': equal})
        print(json.dumps({**result, 'exact_restoration': exact, 'business_preserved': equal}, ensure_ascii=False))
        assert all(exact.values()) and equal
    assert result.get('checks') and all(v is True for v in result['checks'].values()), result


def deploy(label):
    identity = b08.c25.b06.guard()
    names = ['plugins/imagine-site/Sujet.php', 'plugins/imagine-site/Soutenir.php']
    old = b08.c25.b06.hashes(names)
    baseline = json.loads((b08.PROOF / 'deploiement.json').read_text(encoding='utf-8'))['readback']
    assert all(old[n] in [baseline[n], hashlib.sha256((b08.ROOT / 'wp' / n).read_bytes()).hexdigest()] for n in names), 'Dérive distante'
    before = b08.c25.b06.state()
    durable = b08.c25.private(label, {'files': b08.wp('$v=[];foreach(' + b08.php(names) + ' as $n){$v[$n]=file_get_contents(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($v);'), 'database': b08.snapshot()})
    boot = b08.c25.b06.hashes(['plugins/imagine-site/imagine-site.php'])
    for n in names:
        b08.c25.b06.profils.b00.upload(n, (b08.ROOT / 'wp' / n).read_bytes())
    actual = b08.c25.b06.hashes(names)
    assert actual == {n: hashlib.sha256((b08.ROOT / 'wp' / n).read_bytes()).hexdigest() for n in names}
    assert boot == b08.c25.b06.hashes(list(boot))
    assert before == b08.c25.b06.state()
    b08.save(label, {'identity': identity, 'readback': actual, 'bootstrap_preserved': boot, 'business_preserved': True, 'private_snapshot': durable})
    print('B08 : deux fichiers relus, bootstrap et métier préservés')


if __name__ == '__main__':
    assert sys.argv[1] in ['runtime', 'deploy']
    globals()[sys.argv[1]](*sys.argv[2:])
