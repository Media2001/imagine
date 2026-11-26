<?php
/** Observateur temporaire B07 : compte les tentatives, ne masque aucun transport. */
declare(strict_types=1);
foreach (['pre_wp_mail' => 'mail', 'pre_http_request' => 'http'] as $hook => $key) {
    add_filter($hook, static function ($pre) use ($key) {
        $counts = get_option('imagine_b07_observer', ['mail' => 0, 'http' => 0]);
        $counts[$key]++;
        update_option('imagine_b07_observer', $counts, false);
        return $pre;
    }, -10000);
}
