"""B04 : prérequis factuels, aucune création ni publication de produit/article."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('b04_inventory_work',HERE/'b04-work.py')
work=importlib.util.module_from_spec(spec)
spec.loader.exec_module(work)
work.guard()
result=work.wp(r'''
global $wpdb;
$out=['products'=>[], 'published_products'=>0, 'issues'=>[], 'max_articles_in_issue'=>0];
foreach($wpdb->get_results($wpdb->prepare("SELECT ID,post_status FROM {$wpdb->posts} WHERE post_type=%s ORDER BY ID",'product'),ARRAY_A) as $row){
 $p=wc_get_product((int)$row['ID']);
 $out['products'][]=['id'=>(int)$row['ID'],'status'=>$row['post_status'],'type'=>$p?$p->get_type():null,
 'numero'=>$p?$p->get_meta(Imagine\Site\AchatsNumeros::PRODUIT,true,'edit'):null,'price_present'=>$p?$p->get_price()!=='':null];
 if($row['post_status']==='publish'){$out['published_products']++;}
}
foreach(get_posts(['post_type'=>'imagine_numero','post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC']) as $issue){
 $count=(int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(DISTINCT p.ID) FROM {$wpdb->posts} p JOIN {$wpdb->postmeta} m ON m.post_id=p.ID WHERE p.post_type=%s AND p.post_status=%s AND m.meta_key=%s AND m.meta_value=%s",'post','publish','imagine_numero_id',(string)$issue->ID));
 $out['issues'][]=['id'=>$issue->ID,'url'=>get_permalink($issue),'articles'=>$count];$out['max_articles_in_issue']=max($out['max_articles_in_issue'],$count);
}
echo wp_json_encode($out);
''')
result.update(scope='imagine-test-demo',at=datetime.now(timezone.utc).isoformat())
result['product_count']=len(result['products'])
result['issue_count']=len(result['issues'])
result['article_count']=sum(i['articles'] for i in result['issues'])
result['candidate_sha256']=work.digest(work.PROOF/'catalogue-candidat.php')
(work.PROOF/'blocage-catalogue.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['scope','published_products','product_count','issue_count','article_count','max_articles_in_issue']}))
