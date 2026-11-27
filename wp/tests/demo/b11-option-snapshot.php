<?php

declare(strict_types=1);

// Lecture seule : aucun register_setting/update_option, aucune normalisation des lignes présentes.
// Les cinq défauts vivent dans les appels get_option des propriétaires, pas dans Settings API.
// WP-CLI ne charge pas les helpers admin dont admin_init natif dépend.
require_once ABSPATH . 'wp-admin/includes/admin.php';
require_once WC_ABSPATH . 'includes/admin/wc-admin-functions.php';
do_action('admin_init');
$registered = get_registered_settings();
$defaults = [
    'imagine_decouverte_reglages' => [Imagine\Site\Decouverte::defauts(), 'C-12', 'Decouverte.php', 'get_option(self::OPTION, self::defauts())'],
    'imagine_decouverte_relecture' => ['fermee', 'C-12', 'DecouverteReglages.php', "get_option(Decouverte::RELECTURE, 'fermee')"],
    'imagine_solidaire_categories' => [['à préciser'], 'C-17', 'JustificatifsReglages.php', "get_option(self::OPTION, ['à préciser'])"],
    'imagine_newsletters_creation' => ['non', 'C-22', 'Newsletters.php', "get_option(self::CREATION, 'non')"],
    'imagine_retractation_reglages' => [['jours' => 14, 'origine' => 'paiement'], 'C-25', 'Retractation.php', "get_option(self::OPTION, ['jours' => 14, 'origine' => 'paiement'])"],
];
global $wpdb;
$out = [];
foreach ($GLOBALS['b11_option_names'] as $name) {
    if (!isset($registered[$name]) || $registered[$name]['group'] !== 'imagine_reglages') {
        throw new RuntimeException('Option non enregistrée dans le groupe livré : ' . $name);
    }
    $hasDefault = array_key_exists('default', $registered[$name]);
    $default = $registered[$name]['default'] ?? null;
    $source = $hasDefault ? 'Settings API default' : null;
    $owner = null;
    if (isset($defaults[$name])) {
        [$default, $owner, $file, $anchor] = $defaults[$name];
        if (!str_contains(file_get_contents(WP_CONTENT_DIR . '/plugins/imagine-site/' . $file), $anchor)) {
            throw new RuntimeException('Défaut propriétaire non retrouvé : ' . $name);
        }
        $hasDefault = true;
        $source = $file . ': ' . $anchor;
    }
    $rows = $wpdb->get_results($wpdb->prepare("SELECT option_value FROM {$wpdb->options} WHERE option_name=%s", $name), ARRAY_A);
    if ($wpdb->last_error !== '' || count($rows) > 1 || (!$rows && !$hasDefault)) {
        throw new RuntimeException('Option absente sans défaut fiable ou lecture impossible : ' . $name);
    }
    $value = get_option($name, $default);
    $out[$name] = [
        'present' => count($rows) === 1,
        'effective_value' => $value,
        'effective_sha256' => hash('sha256', serialize($value)),
        'raw_sha256' => $rows ? hash('sha256', serialize(maybe_unserialize($rows[0]['option_value']))) : null,
        'default_known' => $hasDefault,
        'default_value' => $default,
        'default_sha256' => $hasDefault ? hash('sha256', serialize($default)) : null,
        'default_source' => $source,
        'settings_api_default_declared' => array_key_exists('default', $registered[$name]),
        'owner' => $owner,
    ];
}
return $out;
