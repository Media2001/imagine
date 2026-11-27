<?php

declare(strict_types=1);

use Imagine\Site\{ContactBrevo, Newsletters, Personnalisation, Cooperateurs};

if (!class_exists(ContactBrevo::class)) {
    fwrite(STDERR, "C29 adaptateur absent\n"); exit(1);
}
$fixture = get_option('imagine_c09_fixture');
$users = $fixture['users'];
$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) { throw new RuntimeException($name); }
};
$check('fiche_native', ContactBrevo::fiche((int)$users['A-CARTE'])['raison'] !== 'compte_absent');
echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
