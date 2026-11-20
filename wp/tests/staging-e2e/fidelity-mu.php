<?php

declare(strict_types=1);

// Synthetic site's own MU configuration: it MUST survive subject cleanup unchanged.
namespace Imagine\E2E;

add_filter('rwmb_meta_boxes', static function (array $boxes): array {
    $boxes[] = [
        'id' => 'imagine_e2e_editorial', 'title' => 'Champs éditoriaux fictifs', 'post_types' => ['post'],
        'fields' => [
            ['id' => 'imagine_e2e_issue', 'name' => 'Numéro fictif', 'type' => 'text'],
            ['id' => 'imagine_e2e_sections', 'name' => 'Rubriques fictives', 'type' => 'text', 'clone' => true],
        ],
    ];
    return $boxes;
});
