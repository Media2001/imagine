<?php

declare(strict_types=1);

namespace Imagine\Staging;

require_once __DIR__ . '/lib.php';
require_once __DIR__ . '/files.php';
require_once __DIR__ . '/pdo-store.php';
require_once __DIR__ . '/runtime-probe.php';

final class Command
{
    public static function run(string $phase, array $args): int
    {
        ini_set('display_errors', '0');
        ini_set('log_errors', '0'); // Les exceptions SQL peuvent contenir des valeurs : jamais de journal brut.
        try {
            if (PHP_SAPI !== 'cli' || getenv('WP_ENVIRONMENT_TYPE') !== 'staging'
                || count($args) !== 3 || $args[1] !== '--worker-bridge'
                || !is_file($args[2]) || is_link($args[2])) {
                throw new \RuntimeException('REFUS');
            }
            // Code de confiance fourni par le worker, pas un wp-config et pas des données importées.
            ob_start();
            try {
                $worker = require $args[2];
            } finally {
                ob_end_clean();
            }
            if (!is_array($worker) || !($worker['store'] ?? null) instanceof Store) {
                throw new \RuntimeException('REFUS');
            }
            Guard::context($worker['context'] ?? []);
            $engine = new Engine($worker['store'], $worker['context'], $worker['prefix'] ?? '');
            $files = new Files($worker['root'] ?? '');
            switch ($phase) {
                case 'neutraliser':
                    $files->purge();
                    $engine->neutraliser();
                    break;
                case 'anonymiser':
                    $files->verify();
                    $line = stream_get_contents(STDIN, 75);
                    if ($line === false || !feof(STDIN)) {
                        throw new \RuntimeException('REFUS');
                    }
                    $secret = preg_replace('/\r?\n$/D', '', $line) ?? '';
                    if (str_contains($secret, "\n") || str_contains($secret, "\r")) {
                        throw new \RuntimeException('REFUS');
                    }
                    $engine->anonymiser($secret);
                    unset($secret, $line);
                    break;
                case 'verifier':
                    $files->verify();
                    $report = $engine->verifier($worker['probe'] ?? null);
                    $files->verify();
                    print(json_encode($report, JSON_THROW_ON_ERROR) . "\n");
                    return $report['ok'] ? 0 : 1;
                default:
                    throw new \RuntimeException('REFUS');
            }
            print("{\"ok\":true,\"scope\":\"offline-data-only\"}\n");
            return 0;
        } catch (\Throwable) {
            // Pas de message d'exception, de chemin, d'adresse, d'argument, de secret ou de contenu de ligne.
            print("{\"ok\":false,\"issues\":[\"STAGING_REFUSE\"]}\n");
            return 78;
        }
    }
}
