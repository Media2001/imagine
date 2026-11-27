<?php

declare(strict_types=1);

// Témoin temporaire uniquement sur le site fictif ; le coupe-circuit B00 reste intact.
if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    return;
}
// Observateur passif : aucun filtre d'éditeur, de formulaire ou de réglage autorisé.
// Lecture de la décision du coupe-circuit APRÈS son inscription ; ne la modifie pas.
add_action('muplugins_loaded', static function (): void {
    add_filter('pre_http_request', static function ($value) {
        $phase = $_GET['b11_observe'] ?? ($_SERVER['HTTP_X_IMAGINE_B11_OBSERVE'] ?? 'ambiance');
        if (is_string($phase) && preg_match('/\A[a-z0-9-]+\z/D', $phase)) {
            $counts = get_option('imagine_b11_observations', []);
            $suffix = is_wp_error($value) && $value->get_error_code() === 'imagine_demo_offline' ? '_blocked' : '_NOT_BLOCKED';
            $key = $phase . $suffix;
            $counts[$key] = ($counts[$key] ?? 0) + 1;
            update_option('imagine_b11_observations', $counts, false);
        }
        return $value;
    }, PHP_INT_MAX, 1);
});
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http', 'pre_oembed_result' => 'oembed'] as $hook => $kind) {
    add_filter($hook, static function ($value, $args = null, $url = null) use ($kind) {
        $phase = $_GET['b11_observe'] ?? ($_SERVER['HTTP_X_IMAGINE_B11_OBSERVE'] ?? 'ambiance');
        if (!is_string($phase) || !preg_match('/\A[a-z0-9-]+\z/D', $phase)) {
            $phase = 'ambiance';
        }
        $counts = get_option('imagine_b11_observations', []);
        $key = $phase . '_' . $kind;
        $counts[$key] = ($counts[$key] ?? 0) + 1;
        if ($kind === 'http' && $phase !== 'ambiance') {
            $stack = debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 40);
            $subject = false;
            $novamira = false;
            foreach ($stack as $frame) {
                $subject = $subject || in_array(basename($frame['file'] ?? ''), ['Medias.php', 'MediasRegles.php', 'AudioNumero.php'], true);
                $novamira = $novamira || (($frame['function'] ?? '') === 'Novamira\\Pro\\license_api_get');
            }
            // Jamais de query string : l'environnement tiers peut y mettre une licence.
            $counts['destinations'][] = ['phase' => $phase, 'host' => is_string($url) ? parse_url($url, PHP_URL_HOST) : null,
                'subject_b11' => $subject, 'ambient_novamira_update' => $novamira,
                'path' => is_string($url) ? parse_url($url, PHP_URL_PATH) : null,
                'stack' => $novamira ? [] : array_values(array_unique(array_map(static fn ($frame) => ($frame['class'] ?? '') . ($frame['type'] ?? '') . ($frame['function'] ?? ''), $stack)))];
        }
        update_option('imagine_b11_observations', $counts, false);
        return $value;
    }, -1000, 3);
}
