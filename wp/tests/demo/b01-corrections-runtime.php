<?php
/** B01 corrections: real WP calls, own temporary objects only, no C08/C09 reseed. */
declare(strict_types=1);
namespace Imagine\Tests\Demo\B01Corrections;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('B01 fixed local demo only.');
}
$checks=[];
$check=static function(string $name,bool $ok) use (&$checks):void {$checks[]=['name'=>$name,'ok'=>$ok];};
$collision=static fn($url,$type)=>home_url('/');
add_filter('post_type_archive_link',$collision,10,2);
ob_start(); \Imagine\Theme\imagine_navigation(); $nav=ob_get_clean();
remove_filter('post_type_archive_link',$collision,10);
$check('two identical archive URLs preserve all seven navigation entries',substr_count($nav,'<li')===7 && str_contains($nav,'Kiosque') && str_contains($nav,'Agenda') && str_contains($nav,'Partenaires'));
$check('navigation has stable slug identity',str_contains($nav,'data-imagine-nav="kiosque"') && str_contains($nav,'data-imagine-nav="agenda"'));
$GLOBALS['post']=get_post(get_option('imagine_demo_manifest')['demo-events-2']);
ob_start(); \Imagine\Theme\imagine_date('imagine_date'); $date=ob_get_clean();
$check('localized date with original ISO datetime',str_contains($date,'11 décembre 2026') && str_contains($date,'datetime="2026-12-11"'));
$check('target actual WP7 and French locale',version_compare(get_bloginfo('version'),'7.0','>=') && get_locale()==='fr_FR');
$ids=[];
try {
    $missing=wp_insert_post(['post_type'=>'imagine_numero','post_status'=>'publish','post_title'=>'B01 TEMP no date'],true);
    if (!is_wp_error($missing)) {$ids[]=$missing;}
    $check('publication without date refused',is_wp_error($missing) || get_post_status($missing)!=='publish');
    $invalid=wp_insert_post(['post_type'=>'imagine_numero','post_status'=>'publish','post_title'=>'B01 TEMP invalid date','meta_input'=>['imagine_sortie'=>'2026-02-30']],true);
    if (!is_wp_error($invalid)) {$ids[]=$invalid;}
    $check('impossible date refuses publication',is_wp_error($invalid) || get_post_status($invalid)!=='publish');
    $valid=wp_insert_post(['post_type'=>'imagine_numero','post_status'=>'publish','post_title'=>'B01 TEMP dated','meta_input'=>['imagine_sortie'=>'2026-12-11']],true);
    if (!is_wp_error($valid)) {$ids[]=$valid;}
    $check('dated issue publishes',!is_wp_error($valid) && get_post_status($valid)==='publish');
    if (!is_wp_error($valid)) {
        delete_post_meta($valid,'imagine_sortie');
        $check('cannot remove date from published issue',get_post_meta($valid,'imagine_sortie',true)==='2026-12-11');
        update_post_meta($valid,'imagine_sortie','');
        $check('cannot empty date on published issue',get_post_meta($valid,'imagine_sortie',true)==='2026-12-11');
        update_post_meta($valid,'imagine_sortie','2027-01-15');
        $check('valid date update allowed',get_post_meta($valid,'imagine_sortie',true)==='2027-01-15');
    }
    $draft=wp_insert_post(['post_type'=>'imagine_numero','post_status'=>'draft','post_title'=>'B01 TEMP draft'],true);
    if (!is_wp_error($draft)) {$ids[]=$draft;}
    $check('undated draft allowed',!is_wp_error($draft) && get_post_status($draft)==='draft');
    $prepared=(object)['post_type'=>'imagine_numero','post_status'=>'publish'];
    $request=new \WP_REST_Request('POST','/wp/v2/imagine_numero');
    $request->set_param('status','publish');
    $result=apply_filters('rest_pre_insert_imagine_numero',$prepared,$request);
    $check('REST publication without date returns explicit 400',is_wp_error($result) && ($result->get_error_data()['status']??null)===400);
} finally {
    foreach($ids as $id) {wp_delete_post($id,true);}
    wp_reset_postdata();
}
echo wp_json_encode(['checks'=>$checks,'temporary_objects_removed'=>array_map(static fn($id)=>get_post($id)===null,$ids)],JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE);
if (in_array(false,array_column($checks,'ok'),true)) {\WP_CLI::halt(1);}
