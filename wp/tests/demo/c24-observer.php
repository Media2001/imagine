<?php
/** Instrumentation éphémère C24 ; aucune adresse ni contenu enregistré. */
declare(strict_types=1);
if (!defined('ABSPATH') || ($_SERVER['HTTP_X_IMAGINE_C24'] ?? '') !== 'recette-fictive') { return; }
add_action('plugins_loaded', static function (): void {
    if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') { return; }
    $counts = ['mail'=>0,'http'=>0,'personalisation_http'=>0,'http_blocked'=>0,'mail_blocked'=>0,'journal_refused'=>0];
    if (($_SERVER['HTTP_X_IMAGINE_C24_FAILURE'] ?? '') === 'journal'
        && ($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
        add_filter('query', static function ($sql) use (&$counts) {
            global $wpdb;
            if (preg_match('/^INSERT\s+INTO/i', $sql) && str_contains($sql, $wpdb->options)
                && str_contains($sql, 'imagine_reglages_journal_') && str_contains($sql, 'imagine_personnalisation_questions')) {
                $counts['journal_refused']++; return '';
            }
            return $sql;
        }, PHP_INT_MAX);
    }
    if (($_SERVER['HTTP_X_IMAGINE_C24_FAILURE'] ?? '') === 'c10-section') {
        add_action('admin_menu', static function (): void {
            global $wp_filter;
            foreach (($wp_filter['admin_menu']->callbacks[145] ?? []) as $callback) {
                $fn=$callback['function'];
                if ($fn instanceof Closure && str_contains((new ReflectionFunction($fn))->getFileName(), '/imagine-site/PersonnalisationReglages.php')) {
                    remove_action('admin_menu', $fn, 145);
                }
            }
        }, 144);
    }
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
