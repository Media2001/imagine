"""Initialisation idempotente du seul écran fictif C30."""
import sys
sys.dont_write_bytecode=True
import c30 as owner
import b13
owner.guard()
code='''$slug='bienvenue';$id=(int)get_option('imagine_c30_page',0);if(!$id){$collision=get_page_by_path($slug);if($collision){throw new RuntimeException('Collision page');}$id=wp_insert_post(wp_slash(['post_type'=>'page','post_status'=>'publish','post_title'=>'Bienvenue','post_name'=>$slug,'post_content'=>'[imagine_bienvenue]','post_excerpt'=>'']),true);if(is_wp_error($id)){throw new RuntimeException('Page non créée');}update_option('imagine_c30_page',$id,false);}if(get_post($id)->post_name!==$slug || get_post($id)->post_content!=='[imagine_bienvenue]'){throw new RuntimeException('Page divergente');}$codes=['fictif-affiche'=>'FICTIF Affiche','fictif-magazine'=>'FICTIF Magazine','fictif-evenement'=>'FICTIF Événement'];$old=get_option(Imagine\\Site\\CodesSuivis::OPTION,null);if($old===null){update_option(Imagine\\Site\\CodesSuivis::OPTION,$codes,false);}elseif($old!==$codes){throw new RuntimeException('Réglages divergents');}echo wp_json_encode(['id'=>$id,'url'=>get_permalink($id),'codes'=>Imagine\\Site\\CodesSuivis::configuration()]);'''
a=owner.wp(code);b=owner.wp(code)
assert a==b
b13.save(owner,sys.argv[1],{'seed':a,'idempotent':True})
print(a)
