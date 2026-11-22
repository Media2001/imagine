<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Echeancier;

use Imagine\Pilotage\Tests\Echeancier\WordPressFictif as Banc;

function current_user_can(string $capacite): bool
{
    Banc::$appels['capacite'] = $capacite;
    return false;
}

function __(string $texte, string $domaine): string
{
    Banc::$appels['traduction'] = [$texte, $domaine];
    return 'TRADUIT : ' . $texte;
}

function wp_die(string $message): never
{
    Banc::$appels['wp_die'] = $message;
    throw new \RuntimeException('WP_DIE_TEST');
}
