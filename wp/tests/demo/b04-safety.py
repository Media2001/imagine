"""Non-mutating safety checks of the demo guards and exact preview boundary."""
from pathlib import Path
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('w',HERE/'b04-work.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
w.guard()
result=w.wp(r'''
$f=get_option('imagine_b04_fixture');$checks=[];
$checks['pas_de_passerelle']=apply_filters('woocommerce_available_payment_gateways',['canary'=>new stdClass()])===[];
$checks['courriel_bloque_sans_envoi']=apply_filters('pre_wp_mail',null,[])===false;
$checks['reseau_WP_bloque_sans_requete']=is_wp_error(apply_filters('pre_http_request',false,[],'https://example.org/b04-never-called'));
$checks['store_reste_coming_soon']=get_option('woocommerce_coming_soon')==='yes';
$old=$GLOBALS['wp_query'];$method=$_SERVER['REQUEST_METHOD']??null;
$q=new WP_Query(['post_type'=>'product','p'=>(int)$f['product']]);$GLOBALS['wp_query']=$q;
$_SERVER['REQUEST_METHOD']='GET';$checks['preview_GET_own_product']=Imagine\Theme\imagine_demo_product_preview(false)===true;
$_SERVER['REQUEST_METHOD']='HEAD';$checks['preview_HEAD_own_product']=Imagine\Theme\imagine_demo_product_preview(false)===true;
$_SERVER['REQUEST_METHOD']='POST';$checks['preview_POST_ferme']=Imagine\Theme\imagine_demo_product_preview(false)===false;
$_SERVER['REQUEST_METHOD']='GET';
$GLOBALS['wp_query']=new WP_Query(['post_type'=>'product','p'=>271,'post_status'=>'private']);
$checks['ancien_produit_prive_pas_exempte']=Imagine\Theme\imagine_demo_product_preview(false)===false;
$GLOBALS['wp_query']=new WP_Query(['post_type'=>'page','p'=>wc_get_page_id('checkout')]);
$checks['checkout_pas_exempte']=Imagine\Theme\imagine_demo_product_preview(false)===false;
$checks['exemption_native_autrui_preservee']=Imagine\Theme\imagine_demo_product_preview(true)===true;
$GLOBALS['wp_query']=$old;
if($method===null){unset($_SERVER['REQUEST_METHOD']);}else{$_SERVER['REQUEST_METHOD']=$method;}
$all=get_posts(['post_type'=>array_keys(get_post_types()),'post_status'=>array_keys(get_post_stati()),'numberposts'=>-1,'fields'=>'ids']);
$checks['witness_retire']=empty($f['witness'])&&empty($f['articles']);
echo wp_json_encode(['total'=>count($checks),'checks'=>$checks,'failures'=>array_keys(array_filter($checks,static fn($v)=>$v!==true))]);
''')
(w.PROOF/'safety.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
if result['failures']:raise SystemExit(1)
