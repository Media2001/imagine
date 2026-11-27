<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
while (have_posts()) :
    the_post();
    $product = function_exists('wc_get_product') ? wc_get_product(get_the_ID()) : null;
    $pack = $product && $product->meta_exists(\Imagine\Site\PacksThematiques::PRODUIT);
    if (!$pack) {
        if (function_exists('wc_get_template_part')) {
            wc_get_template_part('content', 'single-product');
        }
        continue;
    }
    $GLOBALS['product'] = $product;
    $issues = \Imagine\Site\PacksThematiques::numeros($product);
    ?>
    <article class="imagine-article" data-imagine-pack="<?php echo esc_attr((string) $product->get_id()); ?>">
        <h1><?php the_title(); ?></h1>
        <p><?php esc_html_e('Pack thématique — démonstration entièrement fictive.', 'imagine'); ?></p>
        <p><?php esc_html_e('Les numéros inclus sont figés au paiement. Un numéro déjà possédé ne donne pas de remise.', 'imagine'); ?></p>
        <ul class="imagine-list">
            <?php foreach ($issues as $id) : ?>
                <li data-imagine-numero="<?php echo esc_attr((string) $id); ?>">
                    <h2><a href="<?php echo esc_url(get_permalink($id)); ?>"><?php echo esc_html(get_the_title($id)); ?></a></h2>
                    <div class="imagine-cover"><?php echo get_the_post_thumbnail($id, 'medium'); ?></div>
                    <p><time datetime="<?php echo esc_attr((string) get_post_meta($id, 'imagine_sortie', true)); ?>"><?php echo esc_html((string) get_post_meta($id, 'imagine_sortie', true)); ?></time></p>
                </li>
            <?php endforeach; ?>
        </ul>
        <p data-imagine-pack-prix><?php esc_html_e('Prix fictif :', 'imagine'); ?> <?php echo wp_kses_post($product->get_price_html()); ?></p>
        <?php if ($issues !== []) : ?>
            <?php woocommerce_template_single_add_to_cart(); ?>
        <?php else : ?>
            <p><?php esc_html_e('Pack indisponible : aucun ensemble de numéros valide.', 'imagine'); ?></p>
        <?php endif; ?>
    </article>
<?php endwhile;
get_footer();
