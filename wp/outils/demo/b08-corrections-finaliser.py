"""Sceller B08 corrigé après exécutions réelles ; aucun PRET automatique."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
import b08


def main():
    b08.c25.b06.guard()
    before = json.loads((b08.PROOF / 'corrections-final-deploiement.json').read_text(encoding='utf-8'))
    token = before['private_snapshot']
    raw = (Path(os.environ['TMPDIR']) / token['file']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == token['sha256']
    payload = json.loads(raw)['payload']
    old, now = payload['database'], b08.snapshot()
    fixture = json.loads((b08.PROOF / 'corrections-final-pages-menu.json').read_text(encoding='utf-8'))
    prior = json.loads((b08.PROOF / 'pages-menu.json').read_text(encoding='utf-8'))
    assert fixture['fixture'] == prior['fixture'] and fixture['readback'] == prior['readback'], 'Identités/URL des pages et du menu changées'
    owned = {int(p['id']) for p in fixture['readback']} | set(map(int, fixture['fixture']['items'].values()))
    checks = {k: old[k] == now[k] for k in ['users', 'usermeta', 'comments', 'commentmeta', 'wc_orders', 'wc_orders_meta', 'wc_order_addresses', 'wc_order_operational_data', 'woocommerce_order_items', 'woocommerce_order_itemmeta']}
    checks['posts_hors_lot'] = [r for r in old['posts'] if int(r['ID']) not in owned] == [r for r in now['posts'] if int(r['ID']) not in owned]
    checks['postmeta_hors_lot'] = [r for r in old['postmeta'] if int(r['post_id']) not in owned] == [r for r in now['postmeta'] if int(r['post_id']) not in owned]
    checks['navigation'] = old['navigation'] == now['navigation']
    opts = lambda db: [r for r in db['options'] if r['option_name'].startswith('imagine_') or r['option_name'] == 'cron']
    checks['options_metier'] = opts(old) == opts(now)
    checks['actions_metier'] = payload['business']['schedule_business'] == b08.c25.b06.state()['schedule_business']
    checks['bootstrap_preserve'] = before['bootstrap_preserved'] == b08.c25.b06.hashes(list(before['bootstrap_preserved']))
    hashes = b08.c25.b06.hashes(b08.NAMES)
    checks['octets_livres'] = hashes == {n: hashlib.sha256((b08.ROOT / 'wp' / n).read_bytes()).hexdigest() for n in b08.NAMES}
    syntax = b08.wp('$v=[];foreach(' + b08.php(b08.NAMES) + ' as $n){token_get_all(file_get_contents(WP_CONTENT_DIR."/".$n),TOKEN_PARSE);$v[$n]=true;}echo wp_json_encode($v);')
    checks['syntaxe_php_native'] = all(syntax.values())
    assert all(checks.values()), checks
    target = 'imagine-demo-build/b08-seed.php'
    assert b08.c25.b06.hashes([target])[target] == hashlib.sha256((b08.ROOT / 'wp/outils/demo/b08-seed.php').read_bytes()).hexdigest()
    code = 'import pathlib,json;p=pathlib.Path("/app/sites/imagine-test-demo/wp-content/imagine-demo-build/b08-seed.php");p.unlink();print(json.dumps(not p.exists()))'
    p = subprocess.run(['wsl.exe', 'docker', 'exec', 'staging-wp-dashboard', 'python', '-c', code], capture_output=True, encoding='utf-8')
    assert p.returncode == 0 and json.loads(p.stdout) is True
    clean = b08.wp('echo wp_json_encode(["sujets"=>get_posts(["post_type"=>"imagine_sujet","post_status"=>"any","numberposts"=>-1,"fields"=>"ids"]),"configuration"=>Imagine\\Site\\Soutenir::configuration(),"observateur"=>file_exists(WP_CONTENT_DIR."/mu-plugins/b08-observer.php"),"seed"=>file_exists(WP_CONTENT_DIR."/imagine-demo-build/b08-seed.php")]);')
    assert clean == {'sujets': [], 'configuration': {'don': False, 'parts_url': ''}, 'observateur': False, 'seed': False}
    manifest = b08.sources()
    for name in ['A-VOIR.md', 'NOTE.md', 'verifier.py', 'verifier-corrections.py']:
        path = b08.PROOF / name
        manifest[path.relative_to(b08.ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    proofs = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in b08.PROOF.glob('corrections-final-*') if p.is_file()}
    for name in ['corrections-red-slash.log', 'corrections-red-https.log', 'corrections-red-reprise.json', 'corrections-red-cibles-oracle.json', 'corrections-standard-officiel.json']:
        proofs[name] = hashlib.sha256((b08.PROOF / name).read_bytes()).hexdigest()
    readme = (b08.ROOT / 'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    sections = {lot: hashlib.sha256(re.search(r'^## ' + lot + r' — .*?(?=^## |\Z)', readme, re.M | re.S).group(0).encode()).hexdigest() for lot in ['B-06', 'B-07', 'B-08']}
    b08.save('corrections-final', {'manifest': manifest, 'proofs': proofs, 'checks': checks, 'cleanup': clean, 'pages': len(fixture['readback']), 'menu_items': len(fixture['fixture']['items']), 'readback': hashes, 'readme_sections': sections})
    p = subprocess.run([sys.executable, '-B', str(b08.PROOF / 'verifier.py')], capture_output=True, encoding='utf-8')
    print(p.stdout + p.stderr)
    assert p.returncode == 0


if __name__ == '__main__':
    main()
