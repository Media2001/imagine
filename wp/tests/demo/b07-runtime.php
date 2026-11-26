<?php
declare(strict_types=1);
use Imagine\Site\Agenda;
$checks=[];
$check=static function(string $n,bool $v) use (&$checks):void {$checks[$n]=$v;};
$check('adaptateur_agenda_charge',class_exists(Agenda::class));
if (!class_exists(Agenda::class)) { echo wp_json_encode(['checks'=>$checks,'failures'=>array_keys($checks),'total'=>count($checks)]); exit(1); }
$f=get_option('imagine_b07_fixture');
foreach ($f as $type=>$id) {
 $e=Agenda::evenement((int)$id);
 $check($type.'_champs_reels',$e!==null && $e['lieu']!=='' && $e['debut']>0);
 $check($type.'_inscription',Agenda::ouvert((int)$id)===in_array($type,['rencontre','sortie'],true));
}
$cpt=get_post_type_object('imagine_inscription');
$private=static fn($o)=>$o!==null&&!$o->public&&!$o->show_in_rest&&!$o->publicly_queryable&&$o->exclude_from_search;
$check('inscriptions_privees', $private($cpt));
$bad=clone $cpt;$bad->show_in_rest=true;$check('mutation_inscriptions_REST',!$private($bad));
$noexport=static fn($o)=>$o!==null&&!$o->can_export;
$check('aucun_export_inscrits',$noexport($cpt));
$bad=clone $cpt;$bad->can_export=true;$check('mutation_export_inscrits',!$noexport($bad));
$check('admin_restreint',$cpt!==null&&$cpt->cap->edit_posts==='manage_options');
$ex=apply_filters('wp_privacy_personal_data_exporters',[]);
$er=apply_filters('wp_privacy_personal_data_erasers',[]);
$check('callbacks_additifs',isset($ex['imagine-agenda'],$er['imagine-agenda'],$ex['imagine-personnalisation'],$ex['imagine-site']));
$fail=array_keys(array_filter($checks,static fn($v)=>!$v));
echo wp_json_encode(['total'=>count($checks),'checks'=>$checks,'failures'=>$fail]); exit($fail?1:0);
