"""Replayable B04-only native fixture; guard, upload and independent readback."""
from pathlib import Path
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('b04_work',ROOT/'wp/tests/demo/b04-work.py')
w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
w.guard()
action=sys.argv[1] if len(sys.argv)>1 else 'inspect'
assert action in ['product','witness','cleanup-witness','inspect']
p=ROOT/'wp/outils/demo/b04-fixture.php';target='imagine-demo-build/b04-fixture.php'
w.c08.b00.upload(target,p.read_bytes())
assert w.readback([target])[target]==w.digest(p)
code='require WP_CONTENT_DIR . "/'+target+'";'
before=w.wp('$GLOBALS["imagine_b04_action"]="inspect";'+code)
result=w.wp('$GLOBALS["imagine_b04_action"]='+json.dumps(action)+';'+code)
actual=w.wp('$GLOBALS["imagine_b04_action"]="inspect";'+code)
assert actual==result
if action=='cleanup-witness':
    ids=before['fixture'].get('articles',[])+([before['fixture']['witness']] if before['fixture'].get('witness') else [])
    assert w.wp('$out=[];foreach('+json.dumps(ids)+' as $id){$out[]=(get_post($id)===null)&&get_post_meta($id)===[];}echo wp_json_encode($out);')==[True]*len(ids)
    result['exact_owned_deleted_ids']=ids
result.update(scope='imagine-test-demo',readback_exact=True,action=action,source_sha256=w.digest(p))
phase=sys.argv[2] if len(sys.argv)>2 else action
(w.PROOF/('native-fixture-'+phase+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
