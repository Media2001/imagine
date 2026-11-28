"""Restaure la page Cart auto-migrée par Woo depuis sa vraie préimage fictive privée."""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c31 as o
import b13
snapshot = Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/c25-private-4jwegy93/snapshot.json')
archive = json.loads(snapshot.read_text(encoding='utf-8'))
assert archive['scope'] == 'imagine-test-demo'
original = next(r for r in archive['payload']['database']['posts'] if r['ID'] == '7')
assert original['post_name'] == 'cart' and original['post_modified'] == '2026-11-23 13:14:33'
o.guard()
current = o.wp('global $wpdb;echo wp_json_encode($wpdb->get_row("SELECT * FROM {$wpdb->posts} WHERE ID=7",ARRAY_A));')
assert current['post_modified'] == '2026-11-28 04:22:20'
private = b13.b11.private('corrections-cart-avant-restauration-V2', {'row':current})
o.wp('global $wpdb;$row=' + o.php(original) + ';unset($row["ID"]);$wpdb->update($wpdb->posts,$row,["ID"=>7]);clean_post_cache(7);echo wp_json_encode(true);')
assert o.wp('global $wpdb;echo wp_json_encode($wpdb->get_row("SELECT * FROM {$wpdb->posts} WHERE ID=7",ARRAY_A));') == original
baseline = json.loads((o.OUT / 'corrections-commande-essai6-V2.json').read_text(encoding='utf-8'))['before']
after = b13.c29.state()
stable = all(baseline[k] == after[k] for k in baseline if k not in ['option_fingerprints','all_options_fingerprint'])
delta = {k for k in baseline['option_fingerprints'].keys() | after['option_fingerprints'].keys() if baseline['option_fingerprints'].get(k) != after['option_fingerprints'].get(k)}
b13.save(o, 'corrections-cart-restaure-V2', {'exact_cart_preimage_restored':True,'stable_business':stable,'before':baseline,'after':after,'option_delta':sorted(delta),'private':private})
print(json.dumps({'stable_business':stable,'option_delta':sorted(delta)}))
assert stable and delta <= {'_transient_timeout_imagine_b13_thematiques','_transient_imagine_b13_thematiques','_transient_wp_styles_for_blocks'}
