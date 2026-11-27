<?php

declare(strict_types=1);

require __DIR__ . '/../../plugins/imagine-site/PiedPage.php';
$classes = ['menu-item', 'current-menu-item', 'current_page_parent', 'page_item', 'page-item-15', 'menu-item-15'];
$footer = (object)['theme_location' => 'imagine-footer'];
$header = (object)['theme_location' => 'imagine-principal'];
$item = new stdClass();
$checks = [
    'classes_footer_stables' => Imagine\Site\PiedPage::classes($classes, $item, $footer) === ['menu-item', 'menu-item-15'],
    'classes_header_inchangees' => Imagine\Site\PiedPage::classes($classes, $item, $header) === $classes,
    'aria_current_footer_absent' => Imagine\Site\PiedPage::attributs(['href' => '/', 'aria-current' => 'page'], $item, $footer) === ['href' => '/'],
    'aria_current_header_conserve' => Imagine\Site\PiedPage::attributs(['href' => '/', 'aria-current' => 'page'], $item, $header) === ['href' => '/', 'aria-current' => 'page'],
];
echo json_encode(['checks' => $checks]), "\n";
exit(in_array(false, $checks, true) ? 1 : 0);
