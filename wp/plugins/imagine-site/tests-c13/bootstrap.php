<?php

declare(strict_types=1);

spl_autoload_register(static function (string $class): void {
    foreach (
        ['Imagine\\Pilotage\\' => dirname(__DIR__, 2) . '/imagine-pilotage/src/',
        'Imagine\\Connecteur\\' => dirname(__DIR__, 2) . '/imagine-connecteur/src/'] as $prefix => $root
    ) {
        if (str_starts_with($class, $prefix)) {
            require $root . str_replace('\\', '/', substr($class, strlen($prefix))) . '.php';
            return;
        }
    }
});
require_once dirname(__DIR__) . '/EnvoiRegles.php';
