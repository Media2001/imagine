"""Reprise ciblée du premier parcours B07 : une préférence UI admin créée par Woo."""
import sys
sys.dont_write_bytecode=True
import os,json,hashlib
from pathlib import Path
import b07
b07.b06.guard()
paths=[p for p in Path(os.environ['TMPDIR']).glob('b07-private-*/snapshot.json') if json.loads(p.read_text(encoding='utf-8'))['label']=='recette-V2']
assert len(paths)==1
old=json.loads(paths[0].read_text(encoding='utf-8'))['payload']
uid=old['accounts']['admin'];key='meta-box-order_product'
prior=[r for r in old['database']['usermeta'] if int(r['user_id'])==uid and r['meta_key']==key]
assert prior==[]
current=b07.wp('global $wpdb;echo wp_json_encode($wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key=%s",'+str(uid)+','+b07.php(key)+'),ARRAY_A));')
assert len(current)==1
snap=b07.private('recuperation-interface',current)
r=b07.wp('global $wpdb;$rows='+b07.php(current)+';foreach($rows as $r){$now=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE umeta_id=%d",$r["umeta_id"]),ARRAY_A);if($now!==$r)throw new RuntimeException("Dérive");$wpdb->delete($wpdb->usermeta,["umeta_id"=>$r["umeta_id"]]);}wp_cache_delete('+str(uid)+',"user_meta");echo wp_json_encode(!metadata_exists("user",'+str(uid)+','+b07.php(key)+'));')
restored=b07.b06.state()==old['business']
b07.save('recuperation-interface-V2',{'business_restored':restored,'exact_target_absent':r,'private_snapshot':snap,'difference':'Préférence UI native meta-box-order_product ajoutée au compte fictif administrateur à sa première visite ; remise à absence initiale. Sessions et wc_last_active hors état métier.'})
print({'business_restored':restored,'readback':r});assert restored and r
