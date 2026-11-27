import sys
sys.dont_write_bytecode = True
import json
import b13
print(json.dumps(b13.wp('''echo wp_json_encode(['articles'=>array_map(static fn($p)=>['id'=>$p->ID,'url'=>get_permalink($p),'excerpt'=>$p->post_excerpt,'issue'=>get_post_meta($p->ID,'imagine_numero_id',true),'reserved'=>get_post_meta($p->ID,'imagine_reserve',true)],get_posts(['post_type'=>'post','numberposts'=>-1])),'tags'=>get_terms(['taxonomy'=>'post_tag','hide_empty'=>false])]);'''),ensure_ascii=False))
