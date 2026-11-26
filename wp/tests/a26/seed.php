<?php

declare(strict_types=1);

// Fixture-only seeding, before SELECT credentials and confinement. No real plugin is impersonated as a qualification.
require '/subject/a26/Analysis.php';
$families = [];
$active = get_option('active_plugins', []);
foreach (Imagine\ThirdParties\Analysis::plugins() as $path => $family) {
    if (isset($families[$family])) {
        continue;
    }
    $families[$family] = $path;
    $file = WP_PLUGIN_DIR . '/' . $path;
    if (!is_dir(dirname($file))) {
        mkdir(dirname($file), 0755, true);
    }
    file_put_contents($file, "<?php\n/* Plugin Name: A26 invented inert adapter fixture */\n");
    $active[] = $path;
}
update_option('active_plugins', $active);
update_option('googlesitekit_analytics-4_settings', ['measurementID' => 'A26_ID_PRIVATE_CANARY',
    'client_id' => 'A26_SCRUB_PRIVATE_CANARY']);
$publish = static function (string $content, string $date = '2026-01-01 00:00:00', string $type = 'post', string $status = 'publish'): int {
    return (int) wp_insert_post(['post_type' => $type, 'post_status' => $status,
        'post_title' => 'A26_TITLE_PRIVATE_CANARY', 'post_content' => $content,
        'post_date' => $date, 'post_date_gmt' => $date]);
};
// Clean all ordinary public posts inherited from the unrelated fixture, not commerce.
global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->posts} WHERE post_type IN ('post','page','wp_block','imagine_numero')");
register_post_type('imagine_numero', ['public' => true]);
$issues = [];
for ($i = 1; $i <= 11; $i++) {
    $issues[] = $publish('', sprintf('2025-%02d-01 00:00:00', $i), 'imagine_numero');
}
$old = $publish('<iframe src="https://www.youtube.com/embed/A26_VIDEO_PRIVATE_CANARY"></iframe>', '2024-01-01 00:00:00');
update_post_meta($old, 'imagine_numero_id', $issues[0]);
$video = $publish('<!-- wp:embed {"url":"https://youtu.be/A26_BLOCK_PRIVATE_CANARY","type":"video","providerNameSlug":"youtube"} -->'
    . '<figure><div>https://youtu.be/A26_BLOCK_PRIVATE_CANARY</div></figure><!-- /wp:embed -->');
update_post_meta($video, 'imagine_numero_id', $issues[10]);
$other = $publish('<iframe src="https://A26_DOMAIN_PRIVATE_CANARY.invalid/embed"></iframe>'
    . '<img src="https://A26_DOMAIN_PRIVATE_CANARY.invalid/pixel"><a href="https://vimeo.com/123">not embedded</a>');
update_post_meta($other, 'imagine_numero_id', $issues[9]);
foreach ([[$old, 0], [$video, 10], [$other, 9]] as [$article, $number]) {
    wp_update_post(['ID' => $article, 'post_parent' => $issues[$number]]);
}
register_taxonomy('a26_issue', ['post'], ['public' => false]);
for ($i = 0; $i < 11; $i++) {
    $term = wp_insert_term('a26-invented-' . $i, 'a26_issue');
    update_term_meta($term['term_id'], 'a26_date', sprintf('2025-%02d-01 00:00:00', $i + 1));
    foreach ([[$old, 0], [$video, 10], [$other, 9]] as [$article, $number]) {
        if ($number === $i) {
            wp_set_object_terms($article, [(int) $term['term_id']], 'a26_issue');
        }
    }
}
$publish('<iframe src="https://vimeo.com/A26_DRAFT_PRIVATE_CANARY"></iframe>', '2026-01-01 00:00:00', 'post', 'draft');
$publish('[embed]https://vimeo.com/123[/embed]', '2023-01-01 00:00:00');
$block = $publish('<iframe src="https://open.spotify.com/embed/track/A26_AUDIO_PRIVATE_CANARY"></iframe>', '2023-01-01 00:00:00', 'wp_block');
$publish('<!-- wp:block {"ref":' . $block . '} /-->', '2023-01-01 00:00:00');
// Import dangerous() blanks this whole content: all source service counts must become unknown.
$publish('<iframe src="https://www.youtube.com/embed/A26_THIRD_PRIVATE_CANARY"></iframe> pi_a26fictiononly', '2022-01-01 00:00:00');
$mu = WPMU_PLUGIN_DIR . '/a26-register.php';
file_put_contents($mu, "<?php add_action('init', static function () { register_post_type('imagine_numero', ['public'=>true]); });\n");
echo 'A26_SEED_OK';
