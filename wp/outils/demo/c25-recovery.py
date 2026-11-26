"""Récupération C25 : recherche d'une préimage date par digest exact, aucune date inventée."""
import sys
sys.dont_write_bytecode = True
import json
import os
import hashlib
from pathlib import Path
import c25
receipt = json.loads((c25.PROOF / 'recette-02-V2.json').read_text(encoding='utf-8'))
raw = (Path(os.environ['TMPDIR']) / receipt['private_snapshot']['file']).read_bytes()
assert hashlib.sha256(raw).hexdigest() == receipt['private_snapshot']['sha256']
saved = json.loads(raw)['payload']
before = c25.private('recovery-preimage', {'database': c25.snapshot(), 'business': c25.b06.state()})
goals = {k: saved['business']['native']['commandes'][str(k)] for k in [88, 94]}
code = '''$goals=''' + c25.php(goals) + ''';$out=[];foreach($goals as $id=>$goal){$o=wc_get_order((int)$id);$data=$o->get_data();$data['meta_data']=array_values(array_filter($data['meta_data'],static fn($m)=>$m->key!=='_imagine_retractation_debut'));$date=clone $data['date_modified'];$found=null;$end=strtotime('2026-11-26 21:53:31 UTC');$start=strtotime('2026-11-23 00:00:00 UTC');for($t=$end;$t>=$start;$t--){$date->setTimestamp($t);$data['date_modified']=$date;if(hash('sha256',serialize($data))===$goal){$found=gmdate('Y-m-d H:i:s',$t);break;}}$out[$id]=['matched'=>$found!==null,'date'=>$found];}echo wp_json_encode($out);'''
matched = c25.wp(code)
print(json.dumps(matched))
assert all(v['matched'] for v in matched.values()), 'Aucune mutation sans préimage égale au digest initial'
result = c25.wp('''global $wpdb;foreach(''' + c25.php(matched) + ''' as $id=>$row){$wpdb->delete($wpdb->prefix.'wc_orders_meta',['order_id'=>$id,'meta_key'=>'_imagine_retractation_debut']);$wpdb->update($wpdb->prefix.'wc_orders',['date_updated_gmt'=>$row['date']],['id'=>$id]);wp_cache_flush();}echo wp_json_encode(true);''')
after = c25.b06.state()
c25.save('recovery-metier-V2', {'private_snapshot': before, 'matched_dates_by_original_digest': matched, 'business_equal_original': after == saved['business']})
print('BUSINESS EQUAL ORIGINAL', after == saved['business'])
assert after == saved['business']
