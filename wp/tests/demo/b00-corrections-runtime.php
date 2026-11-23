<?php
/** Assertions B00 d'arbitrage ; ne modifie ni droits ni comptes des autres lots. */
declare(strict_types=1);
namespace Imagine\Tests\Demo\Corrections;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive B00 requise.');
}
$checks = [];
$checks['locale_fr_FR'] = get_locale() === 'fr_FR';
$checks['theme_imagine'] = get_stylesheet() === 'imagine';
$checks['c08_present'] = class_exists('Imagine\\Site\\Paywall');
$data = apply_filters('wp_insert_post_data', ['post_type' => 'post', 'post_password' => 'fictif-test'], [], [], false);
$checks['password_article_supprime_des_enregistrement'] = $data['post_password'] === '';
$data = apply_filters('wp_insert_post_data', ['post_type' => 'page', 'post_password' => 'fictif-test'], [], [], false);
$checks['password_page_non_modifie'] = $data['post_password'] === 'fictif-test';
global $wpdb;
$checks['articles_sans_password_en_base'] = (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type='post' AND post_password<>''") === 0;
$checks['installation_hello_world_absent'] = !$wpdb->get_var("SELECT ID FROM {$wpdb->posts} WHERE ID=1 AND post_type='post' AND post_name='hello-world' AND post_title='Hello world!'");
$checks['installation_sample_page_absente'] = !$wpdb->get_var("SELECT ID FROM {$wpdb->posts} WHERE ID=2 AND post_type='page' AND post_name='sample-page' AND post_title='Sample Page'");
$checks['installation_commentaire_absent'] = !$wpdb->get_var("SELECT comment_ID FROM {$wpdb->comments} WHERE comment_ID=1 AND comment_author='A WordPress Commenter' AND comment_author_email='wapuu@wordpress.example'");
$f = get_option('imagine_c08_fixture');
$checks['c08_deux_articles_sur_numero_b00'] = count(get_posts(['post_type' => 'post', 'numberposts' => -1, 'meta_key' => 'imagine_numero_id', 'meta_value' => get_option('imagine_demo_manifest')['demo-2026-t1']])) === 6;
$failures = array_keys(array_filter($checks, static fn ($ok) => !$ok));
echo wp_json_encode(['total' => count($checks), 'checks' => $checks, 'failures' => $failures]);
if ($failures) { \WP_CLI::halt(1); }
