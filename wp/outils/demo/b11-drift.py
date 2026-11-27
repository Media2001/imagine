import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'wp/outils/demo'))
import b11
from playwright.sync_api import sync_playwright
proof=json.loads((b11.OUT/'recette-01.json').read_text())
snapshot=json.loads(Path(proof['private_snapshot']['file']).read_text())['payload']
current=b11.state();print('DIFF_KEYS',[k for k in current if current[k]!=snapshot['business'].get(k)])
for k in current:
    if current[k]!=snapshot['business'].get(k):print(k,json.dumps(current[k],ensure_ascii=False)[:1400],json.dumps(snapshot['business'][k],ensure_ascii=False)[:1400])
print(json.dumps(b11.wp('''$p=get_post(3454);echo wp_json_encode(['editor'=>use_block_editor_for_post($p),'type'=>get_post_type_object('post')->show_in_rest]);''')))
