<?php

declare(strict_types=1);

namespace Imagine\Tests\Demo;

$checks = [];
function check(string $name, bool $ok): void
{
    global $checks;
    $checks[$name] = $ok;
}

check('modele_numero', post_type_exists('imagine_numero'));
check('modele_evenement', post_type_exists('imagine_evenement'));
check('modele_partenaire', post_type_exists('imagine_partenaire'));
check('modele_thematique', taxonomy_exists('imagine_thematique'));
$manifest = get_option('imagine_demo_manifest', []);
check('manifeste_present', count($manifest) > 0);
$calendar = get_option('imagine_demo_calendrier', []);
check('calendrier_trois_ans', count($calendar) === 15);
$years = [];
foreach ($calendar as $entry) {
    $year = substr($entry['sortie'], 0, 4);
    $years[$year] = ($years[$year] ?? 0) + 1;
    check('cloture_avant_sortie_' . $entry['code'], $entry['cloture'] < $entry['sortie']);
}
check('cinq_parutions_par_an', count($years) === 3 && array_unique(array_values($years)) === [5]);
$issues = get_posts(['post_type' => 'imagine_numero', 'numberposts' => -1, 'meta_key' => 'imagine_demo_key']);
check('cinq_numeros', count($issues) === 5);
$hs = 0;
foreach ($issues as $issue) {
    $hs += (int) (get_post_meta($issue->ID, 'imagine_type', true) === 'hors-serie');
    $articles = get_posts(['post_type' => 'post', 'numberposts' => -1, 'meta_key' => 'imagine_numero_id', 'meta_value' => $issue->ID]);
    check('quatre_articles_' . $issue->ID, count($articles) === 4);
    $reserved = array_filter($articles, fn ($p) => get_post_meta($p->ID, 'imagine_reserve', true) === '1');
    check('trois_reserves_' . $issue->ID, count($reserved) === 3);
    foreach ($articles as $article) {
        check('texte_long_' . $article->ID, strlen($article->post_content) > strlen($article->post_excerpt) * 3);
    }
    $cover = get_post_thumbnail_id($issue->ID);
    check('couverture_png_' . $issue->ID, $cover > 0 && str_starts_with((string) file_get_contents(get_attached_file($cover)), "\x89PNG"));
    $pdf = (int) get_post_meta($issue->ID, 'imagine_pdf_id', true);
    check('pdf_factice_' . $issue->ID, $pdf > 0 && str_starts_with((string) file_get_contents(get_attached_file($pdf)), '%PDF-1.4'));
}
check('un_hors_serie', $hs === 1);
foreach (['imagine_evenement' => 2, 'imagine_partenaire' => 2] as $type => $count) {
    check($type . '_count', count(get_posts(['post_type' => $type, 'numberposts' => -1])) === $count);
}
check('trois_thematiques', count(get_terms(['taxonomy' => 'imagine_thematique', 'hide_empty' => false])) === 3);
check('woocommerce_charge', class_exists('WooCommerce'));
check('subscriptions_charge', class_exists('WC_Subscriptions') && function_exists('wcs_create_subscription'));
check('memberships_charge', function_exists('wc_memberships') && wc_memberships() instanceof \WC_Memberships);
check('bibliotheque_pilotage', class_exists('Imagine\\Pilotage\\Numeros\\Moteur'));
check('bibliotheque_connecteur', class_exists('Imagine\\Connecteur\\Event'));
check('email_coupe', wp_mail('b00@example.org', 'TEST FICTIF', 'Ne doit pas sortir') === false);
$http = wp_remote_get('https://example.org/b00-egress-test');
check('http_externe_coupe', is_wp_error($http) && $http->get_error_code() === 'imagine_demo_offline');
check('aucune_passerelle', class_exists('WC_Payment_Gateways') && WC()->payment_gateways()->get_available_payment_gateways() === []);
check('pas_de_compte_woo', !get_option('woocommerce_helper_data', []));
check('pas_indexable', get_option('blog_public') === '0');
check('accueil_statique', get_option('show_on_front') === 'page');
check('compte_fictif', (bool) get_user_by('login', 'imagine-demo-redaction'));
check('wp_7_0_x', preg_match('/^7\.0\.\d+$/', get_bloginfo('version')) === 1);
check('woo_11_1_min', defined('WC_VERSION') && version_compare(WC_VERSION, '11.1', '>='));
$failures = array_keys(array_filter($checks, fn ($ok) => !$ok));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . "\n";
if ($failures !== []) {
    WP_CLI::halt(1);
}
