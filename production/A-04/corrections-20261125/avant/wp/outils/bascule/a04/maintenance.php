<?php

/**
 * Plugin Name: Imagine — maintenance persistante A04
 * Description: À retirer par l'opérateur seulement après la réception complète.
 */

declare(strict_types=1);

namespace Imagine\Bascule;

if (!defined('WP_CLI') || WP_CLI !== true) {
    http_response_code(503);
    header('Retry-After: 3600');
    exit('Maintenance Imagine en cours.');
}
