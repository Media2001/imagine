import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'wp/outils/demo'))
import b11
from playwright.sync_api import sync_playwright
proof=json.loads((b11.OUT/'recette-01.json').read_text())
snapshot=json.loads(Path(proof['private_snapshot']['file']).read_text())['payload']
current=b11.state();print('DIFF_KEYS',[k for k in current if current[k]!=snapshot['business'].get(k)])
def diff(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        for key in set(a)|set(b):diff(a.get(key),b.get(key),path+'/'+str(key))
    elif a!=b:print('DIFF',path,repr(a)[:300],repr(b)[:300])
diff(snapshot['business'],current)
print(json.dumps(b11.wp('''global $wpdb;echo wp_json_encode(['posts'=>$wpdb->get_results("SELECT ID,post_type,post_name,post_parent,post_status,post_title FROM {$wpdb->posts} ORDER BY ID DESC LIMIT 4",ARRAY_A),'meta'=>$wpdb->get_results("SELECT meta_id,post_id,meta_key FROM {$wpdb->postmeta} ORDER BY meta_id DESC LIMIT 4",ARRAY_A),'user'=>$wpdb->get_results("SELECT umeta_id,user_id,meta_key FROM {$wpdb->usermeta} ORDER BY umeta_id DESC LIMIT 4",ARRAY_A)]);'''),ensure_ascii=False))
