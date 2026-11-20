<?php
declare(strict_types=1);
ini_set('display_errors','0'); ini_set('log_errors','0');
try {
    require __DIR__.'/bridge-common.php';
    require '/workflow/wp/outils/staging/lib.php';
    $r = workerRequest();
    Imagine\Staging\Guard::context(workerContext($r));
    $pdo = workerPdo($r);
    if ($pdo->query('SHOW FULL TABLES')->fetch()) throw new RuntimeException('FRESH');
    $plan = $r['sql_plan'];
    if (!preg_match('/^[a-zA-Z0-9_]+_$/D', $plan['prefix'])) throw new RuntimeException('PREFIX');
    foreach ($plan['statements'] as $sql) $pdo->exec($sql);
    $table = '`'.$plan['prefix'].'options`';
    $pdo->beginTransaction();
    $write = $pdo->prepare('UPDATE '.$table.' SET option_value=? WHERE option_name=?');
    foreach (['home','siteurl'] as $key) {
        $read = $pdo->prepare('SELECT option_value FROM '.$table.' WHERE option_name=?');
        $read->execute([$key]);
        if (count($read->fetchAll(PDO::FETCH_COLUMN)) !== 1) throw new RuntimeException('URL');
        $write->execute([$r['staging_url'], $key]);
    }
    // Only the reviewed core theme is present in the clean image tree.
    foreach (['template','stylesheet'] as $key) $write->execute(['twentytwentyfive', $key]);
    $pdo->commit();
    foreach (['home','siteurl'] as $key) {
        $read->execute([$key]);
        if ($read->fetchAll(PDO::FETCH_COLUMN) !== [$r['staging_url']]) throw new RuntimeException('URL');
    }
    print("{\"ok\":true}\n");
} catch (Throwable) {
    print("{\"ok\":false}\n"); exit(78);
}
