<?php
declare(strict_types=1);
use Imagine\Site\AgendaRegles;
$source=dirname(__DIR__,2).'/plugins/imagine-site/AgendaRegles.php';
if (!is_file($source)) { echo json_encode(['failure'=>'AgendaRegles absente : règle non implémentée']); exit(1); }
require $source;
$checks=[];
foreach (['sortie','rencontre'] as $type) {
 $checks[$type.'_futur']=AgendaRegles::inscription($type, 200, 100);
 $checks[$type.'_passe']=!AgendaRegles::inscription($type, 99, 100);
 $checks[$type.'_borne']=!AgendaRegles::inscription($type, 100, 100);
}
$checks['partenaire']=!AgendaRegles::inscription('partenaire',200,100);
$checks['inconnu']=!AgendaRegles::inscription('autre',200,100);
$checks['date_absente']=!AgendaRegles::inscription('sortie',0,100);
$checks['email_normalise']=AgendaRegles::email(' FICTIF@EXAMPLE.ORG ')==='fictif@example.org';
$checks['cle_doublon']=AgendaRegles::cle(42,' FICTIF@EXAMPLE.ORG ')===AgendaRegles::cle(42,'fictif@example.org');
$checks['autre_evenement']=AgendaRegles::cle(42,'fictif@example.org')!==AgendaRegles::cle(43,'fictif@example.org');
$checks['cle_mysql_max64']=strlen(AgendaRegles::cle(42,'fictif@example.org'))<=64;
$checks['cle_sans_email']=!str_contains(AgendaRegles::cle(42,'fictif@example.org'),'fictif');
$fail=array_keys(array_filter($checks,fn($v)=>!$v));
echo json_encode(['total'=>count($checks),'checks'=>$checks,'failures'=>$fail]); exit($fail?1:0);
