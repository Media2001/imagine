<?php
/** B-01 : inventaire et recette en lecture seule, sans export des mots de passe. */

declare(strict_types=1);

namespace Imagine\Demo\B01;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Recette réservée au site fictif local B-00.');
}
$checks = [];
wp_set_current_user(0);
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['name' => $name, 'ok' => $ok];
};
$check('thème Imagine actif', get_stylesheet() === 'imagine');
$check('sortie unique chargeable', function_exists('Imagine\\Theme\\imagine_article_body'));
$check('locale française déjà réglée B00', get_locale() === 'fr_FR');
$check('pile réelle WordPress 7', version_compare(get_bloginfo('version'), '7.0', '>='));
$check('contenu installation déjà purgé B00', get_post(1) === null && get_post(2) === null && get_comment(1) === null);
$issues = get_posts(['post_type' => 'imagine_numero', 'numberposts' => -1, 'orderby' => 'ID', 'order' => 'ASC']);
$articles = get_posts(['post_type' => 'post', 'numberposts' => -1, 'orderby' => 'ID', 'order' => 'ASC']);
$map = static fn (\WP_Post $p): array => ['id' => $p->ID, 'url' => get_permalink($p), 'title' => $p->post_title];
$issueRows = [];
foreach ($issues as $issue) {
    $members = get_posts(['post_type' => 'post', 'numberposts' => -1, 'meta_key' => 'imagine_numero_id',
        'meta_value' => $issue->ID, 'orderby' => 'ID', 'order' => 'ASC']);
    $issueRows[] = $map($issue) + ['date' => get_post_meta($issue->ID, 'imagine_sortie', true),
        'type' => get_post_meta($issue->ID, 'imagine_type', true), 'articles' => array_map($map, $members),
        'pdf' => wp_get_attachment_url((int) get_post_meta($issue->ID, 'imagine_pdf_id', true))];
    $b00 = array_filter($members, static fn ($p) => get_post_meta($p->ID, 'imagine_demo_key', true) !== '');
    $check('quatre articles B00 du numéro ' . $issue->ID, count($b00) === 4);
    $check('numéro publié avec date valide ' . $issue->ID, \Imagine\Site\NumeroPublication::valid(get_post_meta($issue->ID, 'imagine_sortie', true)));
}
usort($issueRows, static fn ($a, $b) => [$b['date'], $b['id']] <=> [$a['date'], $a['id']]);
$articleRows = [];
foreach ($articles as $post) {
    $GLOBALS['post'] = $post;
    setup_postdata($post);
    ob_start();
    \Imagine\Theme\imagine_article_body();
    $body = ob_get_clean();
    $reserved = (bool) get_post_meta($post->ID, 'imagine_reserve', true);
    $check('sortie anonyme article ' . $post->ID, $reserved
        ? !str_contains($body, 'CONTENU_FICTIF_RESERVE_') && !str_contains($body, $post->post_content)
        : str_contains($body, 'CONTENU_FICTIF_OUVERT_'));
    $check('mot de passe natif retiré B00 ' . $post->ID, $post->post_password === '');
    $articleRows[] = $map($post) + ['issue' => (int) get_post_meta($post->ID, 'imagine_numero_id', true),
        'reserved' => $reserved, 'excerpt' => $post->post_excerpt, 'author' => get_the_author(),
        'date' => $post->post_date, 'key' => get_post_meta($post->ID, 'imagine_demo_key', true),
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
$check('garde emails sans envoi', apply_filters('pre_wp_mail', null, []) === false);
$http = apply_filters('pre_http_request', false, [], 'https://example.org');
$check('garde HTTP sans requête distante', is_wp_error($http) && $http->get_error_code() === 'imagine_demo_offline');
$check('indexation refusée', get_option('blog_public') === '0');
$result = ['scope' => 'imagine-test-demo', 'base' => home_url('/'), 'checks' => $checks,
    'wordpress' => get_bloginfo('version'), 'locale' => get_locale(),
    'manifest' => get_option('imagine_demo_manifest'), 'c08_fixture' => get_option('imagine_c08_fixture'),
    'issues' => $issueRows, 'articles' => $articleRows, 'themes' => $themes,
    'events' => array_map($map, get_posts(['post_type' => 'imagine_evenement', 'numberposts' => -1])),
    'partners' => array_map($map, get_posts(['post_type' => 'imagine_partenaire', 'numberposts' => -1])),
    'page' => get_permalink(get_option('imagine_demo_manifest')['demo-calendrier']),
    'archives' => array_map('get_post_type_archive_link', ['imagine_numero', 'imagine_evenement', 'imagine_partenaire'])];
echo wp_json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
if (in_array(false, array_column($checks, 'ok'), true)) {
    \WP_CLI::halt(1);
}
