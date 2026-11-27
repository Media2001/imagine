<?php

declare(strict_types=1);

// Vrai WordPress sous transaction : témoin du contrôle d'écriture, PAS une recette UI.
$f = get_option('imagine_b11_fixture');
$checks = [];
$rows = [];
foreach ([$f['issue'], $f['article']] as $id) {
    $before = [get_post_meta($id, '_imagine_video', true), get_post_meta($id, '_imagine_podcast', true)];
    $video = 'https://video-fictive.example.invalid/B11_WRITE_WITNESS?post=' . $id;
    $podcast = 'https://podcast-fictif.example.invalid/B11_WRITE_WITNESS?post=' . $id;
    $checks['changed_inputs_' . $id] = $video !== $before[0] && $podcast !== $before[1];
    $checks['native_changed_' . $id] = Imagine\Site\Medias::enregistrer($id, $video, $podcast)
        && get_post_meta($id, '_imagine_video', true) === $video
        && get_post_meta($id, '_imagine_podcast', true) === $podcast;
    $checks['native_clear_' . $id] = Imagine\Site\Medias::enregistrer($id, '', '')
        && get_post_meta($id, '_imagine_video', true) === ''
        && get_post_meta($id, '_imagine_podcast', true) === '';
    $mutant = static function ($value, $postId, $key) use ($id) {
        return (int) $postId === (int) $id && in_array($key, ['_imagine_video', '_imagine_podcast'], true) ? true : $value;
    };
    add_filter('update_post_metadata', $mutant, PHP_INT_MAX, 3);
    try {
        $result = Imagine\Site\Medias::enregistrer($id, $video, $podcast);
        $actual = [get_post_meta($id, '_imagine_video', true), get_post_meta($id, '_imagine_podcast', true)];
        $checks['real_no_persist_detected_' . $id] = $result === false && $actual === ['', ''];
        $rows[] = ['id' => $id, 'attempted' => [$video, $podcast], 'actual' => $actual, 'returned' => $result];
    } finally {
        remove_filter('update_post_metadata', $mutant, PHP_INT_MAX);
    }
}
echo wp_json_encode(['boundary' => 'native API under rollback, NOT delivered editor', 'checks' => $checks, 'mutations' => $rows]);
