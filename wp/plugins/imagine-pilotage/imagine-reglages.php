<?php
/**
 * Plugin Name: Imagine — réglages
 * Description: Réunit les adaptateurs d’administration C05, C06 et C07, sans modifier les moteurs.
 * Version: 0.1.0
 * Requires PHP: 8.2
 * Text Domain: imagine-pilotage
 */
declare(strict_types=1);
namespace Imagine\Pilotage\Administration;
if (!defined('ABSPATH')) {
    exit;
}
// Point d’entrée dédié C10 : ne remplace aucun bootstrap des autres lots.
spl_autoload_register(static function (string $class): void {
    $prefix = 'Imagine\\Pilotage\\';
    if (str_starts_with($class, $prefix)) {
        $path = __DIR__ . '/src/' . str_replace('\\', '/', substr($class, strlen($prefix))) . '.php';
        if (is_file($path)) {
            require_once $path;
        }
    }
});
(new Reglages())->brancher();
