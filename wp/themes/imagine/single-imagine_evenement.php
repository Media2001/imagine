<?php

declare(strict_types=1);

namespace Imagine\Theme;

use Imagine\Site\Agenda;

get_header();
while (have_posts()) : the_post();
    $id = get_the_ID();
    $event = Agenda::evenement($id);
    $projection = Agenda::projection($id);
?>
<article id="evenement-<?php echo esc_attr((string)$id); ?>">
    <h1><?php the_title(); ?></h1>
    <?php if ($event) : ?>
    <p><?php echo esc_html(Agenda::libellesTypes()[$event['type']]); ?></p>
    <p><time datetime="<?php echo esc_attr($event['iso']); ?>"><?php echo esc_html($event['date']); ?></time></p>
    <p><?php echo esc_html($event['lieu']); ?></p>
    <?php endif; ?>
    <?php echo $projection['html']; ?>
    <?php if ($event && $event['type'] === 'partenaire') : ?>
        <p><span><?php esc_html_e('Partenariat', 'imagine'); ?></span></p>
        <?php if ($event['url'] !== '' && preg_match('~^https?://~i', $event['url'])) : ?>
        <p><a href="<?php echo esc_url($event['url']); ?>" rel="sponsored noopener noreferrer"><?php esc_html_e('Voir l’événement chez le partenaire', 'imagine'); ?></a></p>
        <?php endif; ?>
    <?php elseif ($event && $event['debut'] <= time()) : ?>
        <p><?php esc_html_e('Événement passé — inscriptions closes.', 'imagine'); ?></p>
    <?php else : Agenda::formulaire($id); endif; ?>
    <?php if ($event) : ?>
    <script type="application/ld+json"><?php echo wp_json_encode(Agenda::schema($id, $projection), JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_UNESCAPED_UNICODE); ?></script>
    <?php endif; ?>
    <p><a href="<?php echo esc_url(get_post_type_archive_link('imagine_evenement')); ?>"><?php esc_html_e('Retour à l’agenda', 'imagine'); ?></a></p>
</article>
<?php endwhile; get_footer(); ?>
