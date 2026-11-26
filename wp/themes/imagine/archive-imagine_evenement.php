<?php

declare(strict_types=1);

namespace Imagine\Theme;

get_header();
?>
<h1><?php esc_html_e('Agenda', 'imagine'); ?></h1>
<?php
foreach (\Imagine\Site\Agenda::groupes() as $group => $events) {
    echo '<section id="agenda-' . esc_attr($group) . '"><h2>' . ($group === 'futurs' ? esc_html__('À venir', 'imagine') : esc_html__('Événements passés', 'imagine')) . '</h2><ul>';
    foreach ($events as $event) {
        echo '<li data-evenement="' . esc_attr((string)$event['id']) . '"><a href="' . esc_url(get_permalink($event['id'])) . '">' . esc_html($event['nom']) . '</a> — <time datetime="' . esc_attr($event['iso']) . '">' . esc_html($event['date']) . '</time> — ' . esc_html__($event['type'] === 'partenaire' ? 'Événement partenaire' : \Imagine\Site\Agenda::TYPES[$event['type']], 'imagine-site') . ' — ' . esc_html($event['lieu']) . '</li>';
    }
    echo '</ul></section>';
}
get_footer();
