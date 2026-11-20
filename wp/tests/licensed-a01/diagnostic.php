<?php
declare(strict_types=1);
require_once '/subject/lib.php';require_once '/subject/files.php';require_once '/subject/pdo-store.php';require_once '/subject/runtime-probe.php';
$result=['stage'=>'start'];
try {
 $result['stage']='bridge';$w=require '/opt/e2e/worker-bridge.php';
 $result['stage']='construct';$e=new Imagine\Staging\Engine($w['store'],$w['context'],$w['prefix'],$w['context']['table_decisions']??[]);
 $result['stage']='files-before';$files=new Imagine\Staging\Files($w['root']);$files->verify();
 $result['stage']='engine';$r=$e->verifier($w['probe']);$result['issues']=$r['issues'];
 $result['stage']='files-after';$files->verify();$result['stage']='complete';
} catch(Throwable $e) {
 $msg=$e->getMessage();$result['tag']=preg_match('/^[A-Z_]+$/D',$msg)?$msg:'REDACTED';$result['exception']=get_class($e);$result['file']=basename($e->getFile());$result['line']=$e->getLine();
}
echo 'E2E_JSON='.json_encode($result,JSON_THROW_ON_ERROR)."\n";
