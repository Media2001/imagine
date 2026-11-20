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
                || !in_array(count($args), [3, 5], true) || $args[1] !== '--worker-bridge'
                || !is_file($args[2]) || is_link($args[2])
                || (count($args) === 5 && ($args[3] !== '--table-decisions' || !is_file($args[4]) || is_link($args[4])))) {
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
            $decisions = $worker['table_decisions'] ?? [];
            if (count($args) === 5) {
                if ($decisions || !empty($worker['context']['table_decisions'])) {
                    throw new \RuntimeException('DECISIONS_AMBIGUES');
                }
                $decisions = json_decode(file_get_contents($args[4]), true, 32, JSON_THROW_ON_ERROR);
                if (!is_array($decisions)) {
                    throw new \RuntimeException('DECISIONS_INVALIDES');
                }
            }
            $engine = new Engine($worker['store'], $worker['context'], $worker['prefix'] ?? '', $decisions);
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
                    $report['files'] = $files->inventory();
                    $report['warnings'] = array_values(array_unique(array_merge($report['warnings'], $report['files']['warnings'])));
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
