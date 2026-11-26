"""Scellement B08 après recette, sans secret ni empreinte d'orchestration."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
import subprocess
from pathlib import Path
import b08


def main():
    c25 = b08.c25
    c25.b06.guard()
    native = json.loads((b08.PROOF / 'recette-livraison.json').read_text(encoding='utf-8'))
    canon = json.loads((b08.PROOF / 'canonique.json').read_text(encoding='utf-8'))
    mutants = json.loads((b08.PROOF / 'mutations.json').read_text(encoding='utf-8'))
    assert len(native['checks']) > 25 and all(native['checks'].values())
    assert all(native['exact_restoration'].values()) and native['business_preserved'] and native['observer_removed']
    assert canon['exit'] == 0 and canon['results'][0]['tests'] == 1149 and canon['results'][0]['assertions'] == 36036
    assert len(mutants['results']) == 12 and all(r['failures'] > 0 and r['errors'] == 0 for r in mutants['results'])
    current_sources = b08.sources()
    for receipt in [native, canon, mutants]:
        assert all(current_sources.get(k) == v for k, v in receipt['sources'].items()), 'Sources de preuve périmées'
    fixture = json.loads((b08.PROOF / 'pages-menu.json').read_text(encoding='utf-8'))
    token = fixture['private_snapshot']
    raw = (Path(os.environ['TMPDIR']) / token['file']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == token['sha256']
    old = json.loads(raw)['payload']['database']
    now = b08.snapshot()
    unchanged = {k: old[k] == now[k] for k in ['users','usermeta','comments','commentmeta','wc_orders','wc_orders_meta','wc_order_addresses','wc_order_operational_data','woocommerce_order_items','woocommerce_order_itemmeta']}
    page_ids = {int(r['id']) for r in fixture['readback']}
    menu_ids = set(map(int, fixture['fixture']['items'].values()))
    owned = page_ids | menu_ids
    unchanged['posts_preexistants'] = [r for r in now['posts'] if int(r['ID']) not in owned] == old['posts']
    unchanged['postmeta_preexistants'] = [r for r in now['postmeta'] if int(r['post_id']) not in owned] == old['postmeta']
    allowed = {'imagine_b08_pages','imagine_b08_menu','theme_mods_imagine'}
    business_options = lambda db: [r for r in db['options'] if (r['option_name'].startswith('imagine_') or r['option_name'] == 'cron') and r['option_name'] not in allowed]
    unchanged['options_metier_preexistantes'] = business_options(old) == business_options(now)
    unchanged['actions_metier'] = c25.b06.state()['schedule_business'] == json.loads(raw)['payload']['business']['schedule_business']
    assert all(unchanged.values()), unchanged
    bootstrap = b08.wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/plugins/imagine-site/imagine-site.php"));')
    assert bootstrap.count(b08.BLOCK) == 1
    deploy = json.loads((b08.PROOF / 'deploiement.json').read_text(encoding='utf-8'))
    pre = deploy['private_snapshot']
    pre_raw = (Path(os.environ['TMPDIR']) / pre['file']).read_bytes()
    assert hashlib.sha256(pre_raw).hexdigest() == pre['sha256']
    original_boot = json.loads(pre_raw)['payload']['files']['plugins/imagine-site/imagine-site.php']
    assert bootstrap.replace(b08.BLOCK, '') == original_boot
    hashes = c25.b06.hashes(b08.NAMES)
    assert hashes == {n: hashlib.sha256((b08.ROOT / 'wp' / n).read_bytes()).hexdigest() for n in b08.NAMES}
    # Retirer uniquement notre exécutable de création ; les pages/menu restent.
    target = 'imagine-demo-build/b08-seed.php'
    remote_hash = c25.b06.hashes([target])[target]
    assert remote_hash == hashlib.sha256((b08.ROOT / 'wp/outils/demo/b08-seed.php').read_bytes()).hexdigest()
    command = 'import pathlib,json;p=pathlib.Path("/app/sites/imagine-test-demo/wp-content/imagine-demo-build/b08-seed.php");p.unlink();print(json.dumps(not p.exists()))'
    p = subprocess.run(['wsl.exe','docker','exec','staging-wp-dashboard','python','-c',command], capture_output=True, encoding='utf-8')
    assert p.returncode == 0 and json.loads(p.stdout) is True
    clean = b08.wp('echo wp_json_encode(["sujets"=>get_posts(["post_type"=>"imagine_sujet","post_status"=>"any","numberposts"=>-1,"fields"=>"ids"]),"configuration"=>Imagine\\Site\\Soutenir::configuration(),"observateur"=>file_exists(WP_CONTENT_DIR."/mu-plugins/b08-observer.php"),"seed"=>file_exists(WP_CONTENT_DIR."/imagine-demo-build/b08-seed.php")]);')
    assert clean == {'sujets': [], 'configuration': {'don': False, 'parts_url': ''}, 'observateur': False, 'seed': False}
    files = {**current_sources}
    for name in ['A-VOIR.md','NOTE.md','verifier.py']:
        path = b08.PROOF / name
        files[path.relative_to(b08.ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    proofs = {}
    for name in ['recette-livraison.json','canonique.json','mutations.json','preparation-image.json','standard-officiel.json','pages-menu.json','deploiement.json','horslive-final.log']:
        path = b08.PROOF / name
        proofs[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    b08.save('final', {'manifest': files, 'proofs': proofs, 'checks': unchanged, 'readback': hashes, 'bootstrap_additif_preserve': True, 'cleanup': clean, 'pages': len(page_ids), 'menu_items': len(menu_ids)})
    print(json.dumps({'checks': unchanged, 'cleanup': clean, 'pages': len(page_ids), 'menu_items': len(menu_ids)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
