<?php

declare(strict_types=1);

namespace Imagine\Tests\Demo\Snapshot;

if (!defined('WP_CLI') || !WP_CLI) {
    exit;
}
$manifest = get_option('imagine_demo_manifest', []);
$rows = [];
foreach ($manifest as $key => $id) {
    if (str_starts_with($key, 'user:')) {
        $user = get_user_by('ID', $id);
        $rows[$key] = ['id' => $id, 'login' => $user->user_login, 'email' => $user->user_email, 'roles' => $user->roles];
    } elseif (str_starts_with($key, 'term:')) {
        $term = get_term($id, 'imagine_thematique');
        $rows[$key] = ['id' => $id, 'slug' => $term->slug, 'name' => $term->name, 'url' => get_term_link($term)];
    } else {
        $post = get_post($id);
        $meta = [];
        foreach (get_post_meta($id) as $field => $values) {
            if (str_starts_with($field, 'imagine_') || in_array($field, ['_thumbnail_id', '_wp_attached_file'], true)) {
                $meta[$field] = $values;
            }
        }
        ksort($meta);
        $rows[$key] = ['id' => $id, 'type' => $post->post_type, 'slug' => $post->post_name,
            'title' => $post->post_title, 'content_sha256' => hash('sha256', $post->post_content),
            'excerpt_sha256' => hash('sha256', $post->post_excerpt), 'protected' => $post->post_password !== '',
            'url' => get_permalink($id), 'meta' => $meta];
        if ($post->post_type === 'attachment') {
            $rows[$key]['file_sha256'] = hash_file('sha256', get_attached_file($id));
            $rows[$key]['file_url'] = wp_get_attachment_url($id);
        }
    }
}
// Inventaire indépendant du manifeste : détecte aussi des objets hors manifeste ou doublons.
global $wpdb;
$duplicates = $wpdb->get_results("SELECT meta_value AS fixture_key, COUNT(*) AS qty FROM {$wpdb->postmeta} WHERE meta_key = 'imagine_demo_key' GROUP BY meta_value HAVING COUNT(*) > 1", ARRAY_A);
$totalTagged = (int) $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->postmeta} WHERE meta_key = 'imagine_demo_key'");
echo wp_json_encode(['rows' => $rows, 'calendar' => get_option('imagine_demo_calendrier'), 'duplicates' => $duplicates,
    'total_tagged' => $totalTagged, 'manifest_posts' => count(array_filter(array_keys($manifest), fn ($key) => !str_contains($key, ':')))], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . "\n";
