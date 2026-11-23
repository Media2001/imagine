<?php
/** B-01 : inventaire et recette en lecture seule, sans export des mots de passe. */

declare(strict_types=1);

namespace Imagine\Demo\B01;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Recette réservée au site fictif local B-00.');
}
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['name' => $name, 'ok' => $ok];
};
$check('thème Imagine actif', get_stylesheet() === 'imagine');
$check('sortie unique chargeable', function_exists('Imagine\\Theme\\imagine_article_body'));
$issues = get_posts(['post_type' => 'imagine_numero', 'numberposts' => -1, 'meta_key' => 'imagine_sortie',
    'orderby' => ['meta_value' => 'DESC', 'ID' => 'DESC']]);
$articles = get_posts(['post_type' => 'post', 'numberposts' => -1, 'meta_key' => 'imagine_demo_key', 'orderby' => 'ID', 'order' => 'ASC']);
$map = static fn (\WP_Post $p): array => ['id' => $p->ID, 'url' => get_permalink($p), 'title' => $p->post_title];
$issueRows = [];
foreach ($issues as $issue) {
    $members = get_posts(['post_type' => 'post', 'numberposts' => -1, 'meta_key' => 'imagine_numero_id',
        'meta_value' => $issue->ID, 'orderby' => 'ID', 'order' => 'ASC']);
    $issueRows[] = $map($issue) + ['date' => get_post_meta($issue->ID, 'imagine_sortie', true),
        'type' => get_post_meta($issue->ID, 'imagine_type', true), 'articles' => array_map($map, $members),
        'pdf' => wp_get_attachment_url((int) get_post_meta($issue->ID, 'imagine_pdf_id', true))];
    $check('quatre articles du numéro ' . $issue->ID, count($members) === 4);
}
$articleRows = [];
foreach ($articles as $post) {
    $GLOBALS['post'] = $post;
    setup_postdata($post);
    ob_start();
    \Imagine\Theme\imagine_article_body();
    $body = ob_get_clean();
    $reserved = (bool) get_post_meta($post->ID, 'imagine_reserve', true);
    $check('sortie anonyme article ' . $post->ID, $reserved
        ? !str_contains($body, 'CONTENU_FICTIF_RESERVE_') && str_contains($body, 'post_password')
        : str_contains($body, 'CONTENU_FICTIF_OUVERT_'));
    if ($reserved) {
        require_once ABSPATH . WPINC . '/class-phpass.php';
        $_COOKIE['wp-postpass_' . COOKIEHASH] = (new \PasswordHash(8, true))->HashPassword($post->post_password);
        ob_start();
        \Imagine\Theme\imagine_article_body();
        $authorized = ob_get_clean();
        $check('sortie native autorisée complète ' . $post->ID, str_contains($authorized, 'CONTENU_FICTIF_RESERVE_') && str_contains($authorized, 'Scène fictive 5.'));
        unset($_COOKIE['wp-postpass_' . COOKIEHASH]);
    }
    $articleRows[] = $map($post) + ['issue' => (int) get_post_meta($post->ID, 'imagine_numero_id', true),
        'reserved' => $reserved, 'excerpt' => $post->post_excerpt, 'author' => get_the_author(),
        'terms' => wp_get_post_terms($post->ID, 'imagine_thematique', ['fields' => 'ids'])];
}
wp_reset_postdata();
$themes = [];
foreach (get_terms(['taxonomy' => 'imagine_thematique', 'hide_empty' => true]) as $term) {
    $members = get_posts(['post_type' => 'post', 'numberposts' => -1, 'tax_query' => [[
        'taxonomy' => 'imagine_thematique', 'field' => 'term_id', 'terms' => [$term->term_id],
    ]]]);
    $themes[] = ['id' => $term->term_id, 'url' => get_term_link($term), 'title' => $term->name,
        'articles' => array_map($map, $members)];
}
$check('emails sortants bloqués', wp_mail('b01-fictif@example.org', 'Test fictif B-01', 'Test sans envoi') === false);
$check('HTTP distant bloqué', is_wp_error(wp_remote_get('https://example.org')));
$check('indexation refusée', get_option('blog_public') === '0');
$result = ['scope' => 'imagine-test-demo', 'base' => home_url('/'), 'checks' => $checks,
    'issues' => $issueRows, 'articles' => $articleRows, 'themes' => $themes,
    'events' => array_map($map, get_posts(['post_type' => 'imagine_evenement', 'numberposts' => -1])),
    'partners' => array_map($map, get_posts(['post_type' => 'imagine_partenaire', 'numberposts' => -1])),
    'page' => get_permalink(get_option('imagine_demo_manifest')['demo-calendrier']),
    'archives' => array_map('get_post_type_archive_link', ['imagine_numero', 'imagine_evenement', 'imagine_partenaire'])];
echo wp_json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
if (in_array(false, array_column($checks, 'ok'), true)) {
    \WP_CLI::halt(1);
}
