<?php
declare(strict_types=1);
ini_set('display_errors','0'); ini_set('log_errors','0');
try {
    require __DIR__.'/bridge-common.php';
    $r = workerRequest();
    require '/workflow/wp/outils/staging/lib.php';
    Imagine\Staging\Guard::context(workerContext($r));
    // The Python wrapper has checked every byte against the image-only tree.
    // Native Engine invokes this process only AFTER its offline DB/file checks.
    ob_start();
    define('WP_USE_THEMES', false);
    require '/var/www/html/wp-load.php';
    require '/workflow/wp/outils/staging/runtime-probe.php';
    $proof = Imagine\Staging\runtimeProbe();
    ob_end_clean();
    print(json_encode($proof, JSON_THROW_ON_ERROR));
} catch (Throwable) {
    while (ob_get_level()) ob_end_clean();
    print('{}'); exit(78);
}
