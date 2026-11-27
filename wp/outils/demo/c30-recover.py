import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import c30 as owner
import b13
owner.guard()
s=json.loads(Path('C:/Users/Ced/AppData/Local/Temp/b11-private-pfnv6szo/snapshot.json').read_text(encoding='utf-8'))
assert s['label']=='browser-essai2-V2-sessions'
before={r['session_key']:r for r in s['payload']}
current=b13.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));')
after={r['session_key']:r for r in current}
changed=[k for k in before.keys()|after.keys() if before.get(k)!=after.get(k)]
print('sessions changées à restaurer',len(changed))
for key in changed:
    print('identité numérique' if key.isdigit() else 'session invitée', 'préexistante', key in before, 'actuelle',key in after,'champs', [k for k in (before.get(key) or after[key]) if (before.get(key) or {}).get(k)!=(after.get(key) or {}).get(k)], 'code_present', 'imagine_code_suivi' in after.get(key,{}).get('session_value',''), 'taille',len(after.get(key,{}).get('session_value','')))
for key in changed:
    row=before.get(key)
    code='global $wpdb;$wpdb->delete($wpdb->prefix."woocommerce_sessions",["session_key"=>'+b13.php(key)+']);'
    if row is not None:code+='$wpdb->insert($wpdb->prefix."woocommerce_sessions",'+b13.php(row)+');'
    code+='echo wp_json_encode(true);'
    assert b13.wp(code)
readback=b13.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_key",ARRAY_A));')
assert readback==s['payload']
b13.save(owner,sys.argv[1] if len(sys.argv)>1 else 'recovery-sessions-V2',{'changed':len(changed),'restored':True,'private_snapshot':str(s['label'])})
print('sessions exactes restaurées',len(readback))
