<?php
/** Instrumentation éphémère C24 ; aucune adresse ni contenu enregistré. */
declare(strict_types=1);
if (!defined('ABSPATH') || ($_SERVER['HTTP_X_IMAGINE_C24'] ?? '') !== 'recette-fictive') { return; }
add_action('plugins_loaded', static function (): void {
    if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') { return; }
    $counts = ['mail'=>0,'http'=>0,'personalisation_http'=>0,'http_blocked'=>0,'mail_blocked'=>0];
    add_filter('pre_wp_mail', static function ($r) use (&$counts) { $counts['mail']++;return $r; }, 1);
    add_filter('pre_http_request', static function ($r) use (&$counts) {
        $counts['http']++;
        foreach (debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS) as $frame) {
            if (str_contains($frame['file'] ?? '', '/imagine-site/Personnalisation')) { $counts['personalisation_http']++;break; }
        }
        return $r;
    }, 1);
    add_filter('pre_wp_mail', static function ($r) use (&$counts) { $counts['mail_blocked']+=(int)($r===false);return $r; }, PHP_INT_MAX);
    add_filter('pre_http_request', static function ($r) use (&$counts) { $counts['http_blocked']+=(int)is_wp_error($r);return $r; }, PHP_INT_MAX);
    add_action('shutdown', static function () use (&$counts): void {
        add_option('imagine_c24_observation_'.str_replace('-','',wp_generate_uuid4()),$counts,'',false);
    }, PHP_INT_MAX);
});
