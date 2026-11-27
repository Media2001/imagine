"""Retire exclusivement le premier squelette B09 vide pour refaire la preuve sur le seed final."""
import sys
sys.dont_write_bytecode=True
import json
import b09
b09.b08.c25.b06.guard()
r=json.loads((b09.PROOF/'pages-reprise.json').read_text(encoding='utf-8'))
before=b09.b08.snapshot()
durable=b09.b08.c25.private('b09-retrait-fixture-initiale',{'database':before,'business':b09.b08.c25.b06.state()})
code='''$expected=EXPECTED;$rows=ROWS;
if(get_option('imagine_b09_pages')!==$expected['pages'] || get_option('imagine_b09_menu')!==['menu'=>$expected['menu'],'items'=>$expected['items']]){throw new RuntimeException('Fixture B09 divergente');}
foreach($rows as $key=>$row){$p=get_post($row['id']);if(!$p||get_post_meta($p->ID,'imagine_b09_page',true)!==$key||$p->post_title!==$row['title']||$p->post_content!==$row['content']){throw new RuntimeException('Page B09 éditée : retrait refusé');}}
$items=wp_get_nav_menu_items($expected['menu']);if(count($items)!==5){throw new RuntimeException('Menu B09 divergent');}
foreach($items as $i){$key=get_post_meta($i->ID,'imagine_b09_menu_item',true);if(($expected['items'][$key]??0)!==$i->ID){throw new RuntimeException('Item B09 étranger');}}
if(!get_post(3)||get_post(3)->post_name!=='privacy-policy'){throw new RuntimeException('Brouillon natif absent');}
wp_delete_nav_menu($expected['menu']);foreach($expected['pages'] as $id){wp_delete_post($id,true);}
delete_option('imagine_b09_pages');delete_option('imagine_b09_menu');update_option('wp_page_for_privacy_policy',3);
$left=[];foreach([...array_values($expected['pages']),...array_values($expected['items'])] as $id){if(get_post($id)||get_post_meta($id)!==[]){$left[]=$id;}}
echo wp_json_encode(['removed'=>$left===[],'locations'=>get_nav_menu_locations(),'privacy'=>(int)get_option('wp_page_for_privacy_policy')]);'''.replace('EXPECTED',b09.php(r['fixture'])).replace('ROWS',b09.php(r['readback']))
result=b09.wp(code)
after=b09.b08.snapshot()
owned=set(r['fixture']['pages'].values())|set(r['fixture']['items'].values())
exact={k:before[k]==after[k] for k in ['users','usermeta','comments','commentmeta','wc_orders','wc_orders_meta','wc_order_addresses','wc_order_operational_data','woocommerce_order_items','woocommerce_order_itemmeta']}
for k,field in [('posts','ID'),('postmeta','post_id')]:
    exact[k+'_hors_B09']=[v for v in before[k] if int(v[field]) not in owned]==[v for v in after[k] if int(v[field]) not in owned]
b09.save('retrait-fixture-initiale',{'private_snapshot':durable,'readback':result,'foreign_preserved':exact,'removed_ids':sorted(owned)})
print(result,exact)
assert result['removed'] and result['locations']=={'imagine-principal':22} and all(exact.values())
