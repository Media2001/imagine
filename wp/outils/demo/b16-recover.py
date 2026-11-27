import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import b13
p=Path('C:/Users/Ced/AppData/Local/Temp/b11-private-ucqihuv4/snapshot.json')
s=json.loads(p.read_text(encoding='utf-8'))
assert s['label']=='browser-essai-V2',s['label']
s=s['payload']
code='''global $wpdb;$s='''+b13.php(s)+''';foreach($s['posts'] as $id=>$row){$wpdb->delete($wpdb->postmeta,['post_id'=>$id]);foreach($s['meta'][$id] as $m){$wpdb->insert($wpdb->postmeta,$m);}wp_set_post_terms((int)$id,$s['terms'][$id],'post_tag');clean_post_cache($id);}foreach(get_terms(['taxonomy'=>'post_tag','hide_empty'=>false,'name'=>'FICTIF B16 mot-clé']) as $t){wp_delete_term($t->term_id,'post_tag');}foreach($s['sessions'] as $id=>$rows){$wpdb->delete($wpdb->usermeta,['user_id'=>$id,'meta_key'=>'session_tokens']);foreach($rows as $r){$wpdb->insert($wpdb->usermeta,$r);}}wp_cache_flush();echo wp_json_encode(true);'''
r=b13.b11.b10.b09.b08.c25.b06.profils.b00.wp('eval',code,check=False)
print(r)
