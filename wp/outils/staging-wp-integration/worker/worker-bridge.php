<?php
declare(strict_types=1);
// Included by native Command only AFTER its Store/Engine classes are available.
// No WordPress bootstrap here: the probe closure is strictly deferred.
require_once __DIR__.'/bridge-common.php';
$r = workerRequest();
$root = '/var/www/html';
if (is_link($root.'/.imagine-staging-offline')
    || file_get_contents($root.'/.imagine-staging-offline') !== "OFFLINE_COPY\n"
    || !preg_match('/^[a-zA-Z0-9_]+_$/D', $r['prefix'] ?? '')) throw new RuntimeException('REFUS');
$context = workerContext($r);
Imagine\Staging\Guard::context($context);
$store = new Imagine\Staging\PdoStore(workerPdo($r), $context);
return ['context'=>$context, 'prefix'=>$r['prefix'], 'root'=>$root, 'store'=>$store,
    'probe'=>static function () use ($r): array {
        $process = proc_open(['php','-d','display_errors=0','-d','log_errors=0',__DIR__.'/runtime-probe-worker.php'],
            [0=>['pipe','r'],1=>['pipe','w'],2=>['file','/dev/null','w']], $pipes, null,
            ['PATH'=>'/usr/bin:/bin','WP_ENVIRONMENT_TYPE'=>'staging']);
        if (!is_resource($process)) throw new RuntimeException('REFUS');
        fwrite($pipes[0], json_encode($r, JSON_THROW_ON_ERROR)); fclose($pipes[0]);
        $json = stream_get_contents($pipes[1],16385); fclose($pipes[1]);
        $rc = proc_close($process);
        if ($rc !== 0 || strlen($json) > 16384) throw new RuntimeException('REFUS');
        return json_decode($json,true,32,JSON_THROW_ON_ERROR);
    }];
