<?php

declare(strict_types=1);

// The prebuilt image supplies dependencies, never the source under test.
spl_autoload_register(static function (string $class): void {
    $prefix = 'Imagine\\Site\\';
    if (str_starts_with($class, $prefix)) {
        $path = dirname(__DIR__, 2) . '/plugins/imagine-site/'
            . str_replace('\\', '/', substr($class, strlen($prefix))) . '.php';
        if (is_file($path)) {
            require $path;
        }
    }
});
