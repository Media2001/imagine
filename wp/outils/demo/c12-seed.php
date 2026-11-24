<?php
/** Fixtures C12 seulement ; aucun reset commercial ou d'un autre profil. */
declare(strict_types=1);
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085') {
    throw new RuntimeException('Cible C12 refusée.');
}
$ids = [];
$manifest = get_option('imagine_demo_manifest');
// Un seul témoin désigné par numéro existant ; un autre article du T4 reste réservé.
$selection = ['un' => ['demo-2026-t4', true], 'deux' => ['demo-2026-t3', true],
    'trois' => ['demo-2026-t2', true], 'non-designe' => ['demo-2026-t4', false]];
foreach ($selection as $label => [$issueSlug, $designated]) {
    $issue = $manifest[$issueSlug];
    $slug = 'c12-decouverte-' . $label;
    $existing = get_page_by_path($slug, OBJECT, 'post');
    if ($existing && get_post_meta($existing->ID, '_imagine_c12_fixture', true) !== $label) {
        throw new RuntimeException('Collision article C12.');
    }
    $id = wp_insert_post(['ID' => $existing->ID ?? 0, 'post_type' => 'post', 'post_status' => 'publish',
        'post_title' => 'Découverte fictive C12 — ' . $label, 'post_name' => $slug,
        'post_date' => '2020-01-01 12:00:00', 'post_date_gmt' => '2020-01-01 11:00:00',
        'post_content' => '<p>Le texte réservé C12 ' . $label . ' révèle des comètes turquoise entièrement fictives.</p>',
        'post_excerpt' => 'Extrait public de la démonstration C12 ' . $label . '.',
        'meta_input' => ['_imagine_c12_fixture' => $label, 'imagine_reserve' => true,
            'imagine_numero_id' => $issue, 'imagine_decouverte' => $designated]], true);
    if (is_wp_error($id)) { throw new RuntimeException('Article C12 impossible.'); }
    $ids[$label] = $id;
    if ((int) get_post_meta($id, 'imagine_numero_id', true) !== $issue
        || (get_post_meta($id, 'imagine_decouverte', true) === '1') !== $designated) {
        throw new RuntimeException('Désignation C12 non relue.');
    }
}
update_option('imagine_c12_fixture', $ids, false);
if (get_option('imagine_c12_fixture') !== $ids) { throw new RuntimeException('Fixture C12 non relue.'); }
echo wp_json_encode($ids);
