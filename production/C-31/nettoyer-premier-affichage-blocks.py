"""Nettoyage exact des effets natifs du premier affichage Woo Blocks de la recette C31."""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c31 as o
import b13
before = json.loads((o.OUT / 'corrections-commande-essai6-V2.json').read_text(encoding='utf-8'))['before']
o.guard()
actual = o.wp('global $wpdb;echo wp_json_encode(["revision"=>$wpdb->get_row("SELECT ID,post_parent,post_type,post_title,post_modified FROM {$wpdb->posts} WHERE ID=4241",ARRAY_A),"note"=>$wpdb->get_row("SELECT note_id,name,date_created FROM {$wpdb->prefix}wc_admin_notes WHERE note_id=2",ARRAY_A)]);')
assert actual['revision'] == {'ID':'4241','post_parent':'7','post_type':'revision','post_title':'Cart','post_modified':'2026-11-28 04:22:20'}
assert actual['note'] == {'note_id':'2','name':'wc-admin-order-withdrawal-feature','date_created':'2026-11-28 03:22:20'}
assert 'woocommerce_order_withdrawal_inbox_notification_created' not in before['option_fingerprints']
o.wp('global $wpdb;$wpdb->delete($wpdb->postmeta,["post_id"=>4241]);$wpdb->delete($wpdb->posts,["ID"=>4241]);$wpdb->delete($wpdb->prefix."wc_admin_note_actions",["note_id"=>2]);$wpdb->delete($wpdb->prefix."wc_admin_notes",["note_id"=>2]);delete_option("woocommerce_order_withdrawal_inbox_notification_created");wp_cache_flush();echo wp_json_encode(true);')
check = o.wp('global $wpdb;echo wp_json_encode(["revision"=>$wpdb->get_var("SELECT ID FROM {$wpdb->posts} WHERE ID=4241"),"note"=>$wpdb->get_var("SELECT note_id FROM {$wpdb->prefix}wc_admin_notes WHERE note_id=2"),"actions"=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}wc_admin_note_actions WHERE note_id=2"),"flag"=>get_option("woocommerce_order_withdrawal_inbox_notification_created",null)]);')
assert check == {'revision':None,'note':None,'actions':0,'flag':None}
after = b13.c29.state()
delta = {k for k in before['option_fingerprints'].keys() | after['option_fingerprints'].keys() if before['option_fingerprints'].get(k) != after['option_fingerprints'].get(k)}
stable = all(before[k] == after[k] for k in before if k not in ['option_fingerprints','all_options_fingerprint'])
b13.save(o, 'corrections-nettoyage-blocks-V2', {'before':before,'after':after,'stable_business':stable,'option_delta':sorted(delta),'removed':actual,'readback':check})
print(json.dumps({'stable_business':stable,'option_delta':sorted(delta),'readback':check}))
assert stable and delta <= {'_transient_timeout_imagine_b13_thematiques','_transient_imagine_b13_thematiques','_transient_wp_styles_for_blocks'}
