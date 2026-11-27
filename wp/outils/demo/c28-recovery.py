"""Récupération ciblée du seul premier essai C28, sans action C09 touchée."""
import sys
sys.dont_write_bytecode=True
import json
import hashlib
import c28
c28.guard()
receipt=json.loads((c28.OUT/'recette-01-nettoyage.json').read_text(encoding='utf-8'))
rows=c28.wp('''global $wpdb;$a=$wpdb->prefix.'actionscheduler_actions';$l=$wpdb->prefix.'actionscheduler_logs';$ids=[9145,9146];$out=[];foreach($ids as $id){$r=$wpdb->get_row($wpdb->prepare("SELECT * FROM $a WHERE action_id=%d",$id),ARRAY_A);if(!$r||$r['status']!=='pending'||!in_array($r['hook'],['woocommerce_admin/stored_state_setup_for_products/async/run_remote_notifications','woocommerce_run_product_attribute_lookup_update_callback'],true)||!in_array($r['args'],['[]','[3592,2]'],true)){throw new RuntimeException('C28 reprise refusée');}$out['actions'][]=$r;$out['logs']=array_merge($out['logs']??[],$wpdb->get_results($wpdb->prepare("SELECT * FROM $l WHERE action_id=%d",$id),ARRAY_A));}echo wp_json_encode($out);''')
snap=c28.private('C28-actions-recette-01',rows)
c28.wp('''global $wpdb;foreach([9145,9146] as $id){$wpdb->delete($wpdb->prefix.'actionscheduler_logs',['action_id'=>$id]);$wpdb->delete($wpdb->prefix.'actionscheduler_actions',['action_id'=>$id]);}echo wp_json_encode(true);''')
after=c28.state()
assert after==receipt['before']
name='mu-plugins/imagine-c28-demo.php'
assert c28.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+name+'"));') is False
c28.upload(name,(c28.ROOT/'wp/outils/demo/c28-demo.php').read_bytes())
assert c28.hashes([name])[name]==hashlib.sha256((c28.ROOT/'wp/outils/demo/c28-demo.php').read_bytes()).hexdigest()
c28.save('recuperation-01',{'removed_exact_created_actions':[9145,9146],'private_snapshot':snap,'business_restored_to_first_recipe_before':after==receipt['before'],'demo_only_coming_soon_exception':{'file':name,'sha256':c28.hashes([name])[name]},'woocommerce_coming_soon_option_unchanged':True})
print('Premier essai restauré exactement ; exception de fiche C28 fictive relue.')
