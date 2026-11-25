<?php

declare(strict_types=1);

namespace Imagine\Theme;

/** Présentation pure de la décision C06/C08, jamais un calcul de droits. */
function imagine_access_status(array $decision): array
{
    $code = 'reserve';
    if (($decision['complet'] ?? false) === true) {
        $code = match ($decision['motif'] ?? '') {
            'contenu_ouvert' => 'libre',
            'decouverte_duree', 'decouverte_articles' => 'decouverte',
            default => 'ouvert',
        };
    }
    $label = match ($code) {
        'libre' => __('Libre', 'imagine'),
        'decouverte' => __('Découverte', 'imagine'),
        'ouvert' => __('Ouvert pour vous', 'imagine'),
        default => __('Réservé', 'imagine'),
    };
    return ['code' => $code, 'label' => $label];
}

/** Published, purchasable native C14 product only; no rights inferred here. */
function imagine_issue_product(int $issue): string
{
    if (!function_exists('wc_get_product') || !class_exists('Imagine\\Site\\AchatsNumeros')) {
        return '';
    }
    $products = get_posts([
        'post_type' => 'product', 'post_status' => 'publish', 'numberposts' => -1,
        'meta_key' => \Imagine\Site\AchatsNumeros::PRODUIT, 'meta_value' => $issue,
        'orderby' => 'ID', 'order' => 'ASC',
    ]);
    foreach ($products as $post) {
        $product = wc_get_product($post->ID);
        if (\Imagine\Site\AchatsNumeros::numero($product) === $issue
            && $product->is_purchasable() && $product->is_in_stock()) {
            return $product->get_permalink();
        }
    }
    return '';
}

/** Only the explicitly owned fictive B04 product can be previewed through Woo's native page.
 * Store/cart/checkout visibility settings and every other product remain untouched.
 */
function imagine_demo_product_preview(bool $excluded): bool
{
    if ($excluded) {
        return true;
    }
    return wp_get_environment_type() === 'local'
        && get_option('imagine_demo_site') === 'imagine-test-demo'
        && rtrim(home_url(), '/') === 'http://192.168.129.32:8085'
        && in_array($_SERVER['REQUEST_METHOD'] ?? '', ['GET', 'HEAD'], true)
        && is_singular('product')
        && get_post_meta(get_queried_object_id(), '_imagine_b04_fixture', true) === 'product-v1';
}
add_filter('woocommerce_coming_soon_exclude', __NAMESPACE__ . '\\imagine_demo_product_preview');

/** Public catalogue metadata only: never derive an excerpt from article content. */
function imagine_catalogue_articles(array $articles, array $statuses = [], int $heading = 2, string $id = ''): void
{
    if ($articles === []) {
        echo '<p>' . esc_html__('Aucun article pour le moment.', 'imagine') . '</p>';
        return;
    }
    $tag = $heading === 3 ? 'h3' : 'h2';
    echo '<ul class="imagine-list"' . ($id !== '' ? ' id="' . esc_attr($id) . '"' : '') . '>';
    foreach ($articles as $article) {
        $status = $statuses[$article->ID] ?? imagine_access_status(class_exists('Imagine\\Site\\Paywall')
            ? \Imagine\Site\Paywall::decision($article) : []);
        echo '<li data-imagine-id="' . esc_attr((string) $article->ID) . '"><' . $tag . '><a href="'
            . esc_url(get_permalink($article)) . '">' . esc_html(get_the_title($article)) . '</a></' . $tag . '>';
        echo '<p data-imagine-access="' . esc_attr($status['code']) . '">' . esc_html($status['label']) . '</p>';
        $excerpt = mb_substr(trim(wp_strip_all_tags(strip_shortcodes($article->post_excerpt))), 0, 320);
        if ($excerpt !== '') {
            echo '<p>' . esc_html($excerpt) . '</p>';
        }
        $terms = get_the_terms($article->ID, 'imagine_thematique');
        if (is_array($terms)) {
            echo '<p>' . esc_html__('Thématiques :', 'imagine') . ' ';
            $links = [];
            foreach ($terms as $term) {
                $url = get_term_link($term);
                if (!is_wp_error($url)) {
                    $links[] = '<a href="' . esc_url($url) . '">' . esc_html($term->name) . '</a>';
                }
            }
            echo implode(', ', $links) . '</p>';
        }
        $issue = get_post((int) get_post_meta($article->ID, 'imagine_numero_id', true));
        if ($issue && $issue->post_type === 'imagine_numero' && $issue->post_status === 'publish') {
            echo '<p>' . esc_html__('Dans le numéro :', 'imagine') . ' <a href="' . esc_url(get_permalink($issue))
                . '">' . esc_html(get_the_title($issue)) . '</a></p>';
        }
        echo '</li>';
    }
    echo '</ul>';
}
