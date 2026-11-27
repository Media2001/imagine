<?php

declare(strict_types=1);

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new RuntimeException('B14 cible refusée');
}
$issue = Imagine\Site\Accueil::numero();
$free = $issue ? Imagine\Site\Accueil::libre($issue) : null;
if (!$free || !get_post_thumbnail_id($issue)) {
    throw new RuntimeException('B14 numéro/reportage/couverture fictifs absents');
}
$prior = get_option('imagine_b14_fixture');
if ($prior) {
    if ($prior['article'] !== $free->ID || get_post_thumbnail_id($free) !== $prior['image']) {
        throw new RuntimeException('B14 illustration divergente');
    }
    echo wp_json_encode($prior);
    return;
}
$oldImage = get_post_thumbnail_id($free);
if (!$oldImage) {
    set_post_thumbnail($free->ID, get_post_thumbnail_id($issue));
}
$data = ['issue' => $issue->ID, 'article' => $free->ID, 'image' => get_post_thumbnail_id($free), 'old_image' => $oldImage];
update_option('imagine_b14_fixture', $data, false);
if (get_option('imagine_b14_fixture') !== $data || !$data['image']) {
    throw new RuntimeException('B14 fixture non relue');
}
echo wp_json_encode($data);
