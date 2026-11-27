<?php

declare(strict_types=1);

// Atteignabilité par lecture du raccord réellement installé ; aucune session ni préférence modifiée.
require_once ABSPATH . 'wp-admin/includes/template.php';
require_once ABSPATH . 'wp-admin/includes/screen.php';
require_once ABSPATH . 'wp-admin/includes/post.php';
wp_set_current_user((int) get_users(['role' => 'administrator', 'number' => 1])[0]->ID);
$fixture = get_option('imagine_b11_fixture');
$bridge = new ReflectionFunction('the_block_editor_meta_boxes');
$lines = file($bridge->getFileName());
$source = implode('', array_slice($lines, $bridge->getStartLine() - 1, $bridge->getEndLine() - $bridge->getStartLine() + 1));
$renderer = new ReflectionFunction('do_meta_boxes');
$renderLines = file($renderer->getFileName());
$renderSource = implode('', array_slice($renderLines, $renderer->getStartLine() - 1, $renderer->getEndLine() - $renderer->getStartLine() + 1));
$checks = [
    'bridge_offers_advanced_location' => str_contains($source, "array( 'side', 'normal', 'advanced' )"),
    'bridge_offers_box_ids_to_editor' => str_contains($source, 'setAvailableMetaBoxesPerLocation'),
    'native_renderer_compatible_by_default' => str_contains($renderSource, '$block_compatible = true;'),
];
$rows = [];
foreach ([$fixture['issue'], $fixture['article']] as $id) {
    $post = get_post($id);
    set_current_screen($post->post_type);
    $screen = get_current_screen();
    $screen->is_block_editor(use_block_editor_for_post($post));
    do_action('add_meta_boxes', $post->post_type, $post);
    do_action('add_meta_boxes_' . $post->post_type, $post);
    global $wp_meta_boxes;
    $boxes = apply_filters('filter_block_editor_meta_boxes', $wp_meta_boxes);
    $box = $boxes[$screen->id]['advanced']['default']['imagine-medias'] ?? null;
    $args = $box['args'] ?? [];
    $checks['declared_' . $id] = is_array($box) && $box['callback'] === [Imagine\Site\Medias::class, 'champs'];
    $checks['offered_in_delivered_editor_' . $id] = $screen->is_block_editor()
        && !($args['__back_compat_meta_box'] ?? false)
        && ($args['__block_editor_compatible_meta_box'] ?? true);
    $checks['editor_can_edit_' . $id] = current_user_can('edit_post', $id);
    ob_start();
    do_meta_boxes($screen, 'advanced', $post);
    $html = ob_get_clean();
    $checks['native_fields_rendered_' . $id] = str_contains($html, 'id="b11-video"')
        && str_contains($html, 'id="b11-podcast"') && str_contains($html, 'name="_imagine_medias_nonce"');
    $rows[] = ['id' => $id, 'post_type' => $post->post_type, 'editor' => 'block',
        'location' => 'advanced', 'priority' => 'default', 'callback_args' => $box['args'] ?? null,
        'proposed_by_native_bridge' => $checks['offered_in_delivered_editor_' . $id]];
}
echo wp_json_encode(['method' => 'installed native bridge code + actual registration/render; not UI save',
    'checks' => $checks, 'editors' => $rows, 'core' => [
        'bridge' => ['file' => str_replace(ABSPATH, '', $bridge->getFileName()), 'first' => $bridge->getStartLine(), 'last' => $bridge->getEndLine(), 'sha256' => hash('sha256', $source)],
        'renderer' => ['file' => str_replace(ABSPATH, '', $renderer->getFileName()), 'first' => $renderer->getStartLine(), 'last' => $renderer->getEndLine(), 'sha256' => hash('sha256', $renderSource)],
    ], 'declaration_patch_required' => !array_reduce($checks, static fn ($all, $ok) => $all && $ok, true)]);
