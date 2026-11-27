<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
while (have_posts()) :
    the_post();
    $issue = get_post();
    $articles = (new \WP_Query([
        'post_type' => 'post', 'post_status' => 'publish', 'posts_per_page' => -1,
        'meta_key' => 'imagine_numero_id', 'meta_value' => $issue->ID,
        'orderby' => ['menu_order' => 'ASC', 'ID' => 'ASC'], 'no_found_rows' => true,
    ]))->posts;
    $statuses = [];
    $free = imagine_issue_free_article($issue);
    foreach ($articles as $article) {
        $statuses[$article->ID] = imagine_access_status(class_exists('Imagine\\Site\\Paywall')
            ? \Imagine\Site\Paywall::decisionListe($article) : []);

    }
    $issueDecision = class_exists('Imagine\\Site\\Paywall') ? \Imagine\Site\Paywall::decisionPdf($issue) : [];
    $covered = class_exists('Imagine\\Site\\Paywall') && \Imagine\Site\Paywall::couvreNumero($issue);
    $productUrl = $covered ? '' : imagine_issue_product($issue->ID);
    $pdf = '';
    // La possession ne sert qu'au bouton : C11 reste seul juge de la lecture actuelle.
    if (($issueDecision['complet'] ?? false) === true && class_exists('Imagine\\Site\\PdfNumero')) {
        try {
            \Imagine\Site\PdfNumero::path($issue->ID);
            $pdf = \Imagine\Site\PdfNumero::url($issue->ID);
        } catch (\Throwable) {
            // No existence hint when missing or unavailable.
        }
    }
    ?>
<article>
    <h1><?php the_title(); ?></h1>
    <div class="imagine-cover"><?php echo get_the_post_thumbnail($issue->ID, 'medium'); ?></div>
    <?php imagine_date('imagine_sortie'); ?>
    <p class="imagine-issue-presentation"><?php echo esc_html($issue->post_excerpt); ?></p>
    <?php echo class_exists('Imagine\\Site\\Medias') ? \Imagine\Site\Medias::rendre($issue) : ''; ?>
    <?php if ($free) : ?>
    <section aria-labelledby="imagine-free-article" data-imagine-free-article="<?php echo esc_attr((string) $free->ID); ?>">
        <h2 id="imagine-free-article"><?php esc_html_e('À lire en accès libre', 'imagine'); ?></h2>
        <p><a href="<?php echo esc_url(get_permalink($free)); ?>"><?php echo esc_html(get_the_title($free)); ?></a></p>
    </section>
    <?php endif; ?>
    <section aria-labelledby="imagine-contents">
        <h2 id="imagine-contents"><?php esc_html_e('Sommaire détaillé', 'imagine'); ?></h2>
        <?php imagine_catalogue_articles($articles, $statuses, 3, 'imagine-contents-list', false); ?>
    </section>
    <section aria-labelledby="imagine-audio-contents">
        <h2 id="imagine-audio-contents"><?php esc_html_e('Sommaire audio', 'imagine'); ?></h2>
        <?php echo class_exists('Imagine\\Site\\AudioNumero') ? \Imagine\Site\AudioNumero::lecteur($issue) : ''; ?>
    </section>
    <?php if ($productUrl !== '') : ?>
    <p><a data-imagine-buy href="<?php echo esc_url($productUrl); ?>"><?php esc_html_e('Acheter ce numéro', 'imagine'); ?></a></p>
    <?php endif; ?>
    <?php if ($pdf !== '') : ?>
    <p><a data-imagine-pdf href="<?php echo esc_url($pdf); ?>"><?php esc_html_e('Télécharger le PDF du numéro', 'imagine'); ?></a></p>
    <?php endif; ?>
</article>
<?php endwhile; ?>
<?php get_footer(); ?>
