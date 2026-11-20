<?php

declare(strict_types=1);

namespace Imagine\E2E;

if (!defined('ABSPATH') || wp_get_environment_type() !== 'staging') {
    throw new \RuntimeException('Synthetic isolated WordPress only');
}
$required = [
    'woocommerce/woocommerce.php', 'contact-form-7/wp-contact-form-7.php',
    'wordpress-seo/wp-seo.php', 'meta-box/meta-box.php',
];
$active = get_option('active_plugins', []);
$boot = [
    'wordpress' => did_action('wp_loaded') > 0,
    'woocommerce' => class_exists('WooCommerce'),
    'form' => class_exists('WPCF7_ContactForm'),
    'seo' => class_exists('WPSEO_Options'),
    'fields' => function_exists('rwmb_set_meta') && function_exists('rwmb_get_value'),
];
if (in_array(false, $boot, true) || array_diff($required, $active)) {
    throw new \RuntimeException('FIDELITY_PLUGIN_NOT_ACTIVE_OR_BOOTED');
}
if (getenv('E2E_FIDELITY_PHASE') === 'seed') {
    $form = \WPCF7_ContactForm::get_template(['title' => 'Formulaire fictif de fidélité']);
    $properties = $form->get_properties();
    $properties['form'] = '<label>Sujet fictif [text* sujet-fictif]</label> [submit "Tester sans envoi"]';
    $properties['mail']['recipient'] = 'formulaire@example.org';
    $properties['mail']['sender'] = 'Site fictif <formulaire@example.org>';
    $properties['additional_settings'] = "demo_mode: on\n";
    $form->set_properties($properties);
    $form->save();
    $post = wp_insert_post(['post_type' => 'post', 'post_status' => 'publish',
        'post_title' => 'Article fictif de fidélité', 'post_content' => 'Texte éditorial entièrement inventé.']);
    \WPSEO_Options::set('separator', 'sc-dash');
    \WPSEO_Options::set('title-post', '%%title%% %%sep%% Magazine fictif');
    update_post_meta($post, '_yoast_wpseo_title', 'Référencement fictif intact');
    rwmb_set_meta($post, 'imagine_e2e_issue', 'NUMERO-FICTIF-42');
    rwmb_set_meta($post, 'imagine_e2e_sections', ['Culture inventée', 'Écologie inventée']);
    update_option('imagine_e2e_fidelity', ['form' => $form->id(), 'post' => $post,
        'nested' => ['layout' => ['columns' => 3, 'accent' => 'prune'], 'enabled' => true]]);
}
$ids = get_option('imagine_e2e_fidelity');
if (!is_array($ids)) {
    throw new \RuntimeException('FIDELITY_SETTINGS_LOST');
}
$form = \WPCF7_ContactForm::get_instance($ids['form']);
if (!$form) {
    throw new \RuntimeException('FIDELITY_FORM_LOST');
}
$_SERVER['REQUEST_URI'] = '/synthetic-form/';
$html = $form->form_html();
$settings = [
    'form_properties' => $form->get_properties(),
    'form_title' => $form->title(),
    'seo_options' => array_combine(['wpseo', 'wpseo_titles', 'wpseo_social'],
        array_map('get_option', ['wpseo', 'wpseo_titles', 'wpseo_social'])),
    'seo_post_title' => get_post_meta($ids['post'], '_yoast_wpseo_title', true),
    'field_value' => rwmb_get_value('imagine_e2e_issue', [], $ids['post']),
    'clone_values' => rwmb_get_value('imagine_e2e_sections', [], $ids['post']),
    'field_configuration' => apply_filters('rwmb_meta_boxes', []),
    'nested_settings' => $ids,
    'article' => [get_post($ids['post'])->post_title, get_post($ids['post'])->post_content],
];
$digests = [];
foreach ($settings as $key => $value) {
    $digests[$key] = hash('sha256', serialize($value));
}
$versions = ['contact_form_7' => WPCF7_VERSION, 'yoast' => WPSEO_VERSION, 'meta_box' => RWMB_VER];
echo 'E2E_JSON=' . json_encode([
    'boot' => $boot, 'versions' => $versions, 'active_plugins' => $active,
    'settings_sha256' => $digests,
    'form_renders' => str_contains($html, '<form ') && str_contains($html, 'name="sujet-fictif"'),
    'field_reads' => $settings['field_value'] === 'NUMERO-FICTIF-42'
        && $settings['clone_values'] === ['Culture inventée', 'Écologie inventée'],
    'mu_sha256' => hash_file('sha256', WPMU_PLUGIN_DIR . '/imagine-e2e-fields.php'),
], JSON_THROW_ON_ERROR) . "\n";
