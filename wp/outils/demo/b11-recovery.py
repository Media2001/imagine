import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'wp/outils/demo'))
import b11
b11.guard()
r=b11.wp('''global $wpdb;echo wp_json_encode(['post'=>$wpdb->get_row("SELECT * FROM {$wpdb->posts} WHERE ID=3455",ARRAY_A),'postmeta'=>$wpdb->get_results("SELECT * FROM {$wpdb->postmeta} WHERE meta_id=22540",ARRAY_A),'usermeta'=>$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE umeta_id IN (14063,14064) ORDER BY umeta_id",ARRAY_A)]);''')
assert r['post']['post_type']=='wp_global_styles' and r['post']['post_name']=='wp-global-styles-imagine'
assert [(x['post_id'],x['meta_key']) for x in r['postmeta']]==[('11','_edit_lock')]
assert [(x['user_id'],x['meta_key']) for x in r['usermeta']]==[('1','meta-box-order_product'),('1','wp_persisted_preferences')]
s=b11.private('recovery-01',r)
b11.wp('''global $wpdb;$wpdb->delete($wpdb->posts,['ID'=>3455,'post_type'=>'wp_global_styles']);$wpdb->delete($wpdb->postmeta,['meta_id'=>22540,'post_id'=>11,'meta_key'=>'_edit_lock']);foreach([14063,14064] as $id){$wpdb->delete($wpdb->usermeta,['umeta_id'=>$id,'user_id'=>1]);}clean_post_cache(3455);clean_post_cache(11);clean_user_cache(1);echo wp_json_encode(true);''')
p=json.loads((b11.OUT/'recette-01.json').read_text());expected=json.loads(Path(p['private_snapshot']['file']).read_text())['payload']['business']
actual=b11.state()
checks={k:actual[k]==expected[k] for k in expected}
for name in ['posts','postmeta']:
    checks[name]=actual['native']['native_fingerprints'][name]==expected['native']['native_fingerprints'][name]
checks['usermeta_count']=actual['native']['native_fingerprints']['usermeta']['count']==expected['native']['native_fingerprints']['usermeta']['count']
b11.save('recovery-01',{'business_exactly_restored':actual==expected,'checks':checks,'private_snapshot':s,'limit':'Ancienne préférence administrateur modifiée avant la préimage complète : empreinte usermeta résiduelle, non reconstruite. Aucune restauration inventée.','cleaned_owned_request_artifacts':{'global_styles':3455,'edit_lock':22540,'admin_preferences':[14063,14064]}})
print('B11 première recette : posts et postmeta restaurés ; empreinte usermeta résiduelle déclarée')
