<?php
/** Observateur temporaire B07 : compte les tentatives, ne masque aucun transport. */
declare(strict_types=1);
$empty = ['mail' => 0, 'http' => 0, 'agenda_mail' => 0, 'agenda_http' => 0, 'transport_mail' => 0, 'transport_http' => 0];
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http'] as $hook => $key) {
    add_filter($hook, static function ($pre) use ($key, $empty) {
        $counts = get_option('imagine_b07_observer', $empty);
        $counts[$key]++;
        foreach (debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS) as $frame) {
            if (str_starts_with($frame['class'] ?? '', 'Imagine\\Site\\Agenda')) { $counts['agenda_' . $key]++; break; }
        }
        update_option('imagine_b07_observer', $counts, false);
        return $pre;
    }, -10000);
}
foreach (['phpmailer_init' => 'transport_mail', 'http_api_debug' => 'transport_http'] as $hook => $key) {
    add_action($hook, static function () use ($key, $empty): void {
        $counts = get_option('imagine_b07_observer', $empty);
        $counts[$key]++;
        update_option('imagine_b07_observer', $counts, false);
    }, -10000);
}
