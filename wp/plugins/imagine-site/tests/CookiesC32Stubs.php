<?php

declare(strict_types=1);

namespace Imagine\Site;

// Ce fichier n'est chargé que par un test PHPUnit C32 en processus séparé.
function get_option(string $name, mixed $default = false): mixed
{
    return $name === AutresPages::OPTION ? ['cookies' => 32] : $default;
}

function is_singular(string $type): bool
{
    return $type === 'page';
}

function in_the_loop(): bool
{
    return true;
}

function is_main_query(): bool
{
    return true;
}

function get_the_ID(): int
{
    return $GLOBALS['c32_page_id'] ?? 32;
}

function esc_html(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function esc_html__(string $text, string $domain): string
{
    $allowed = ['Cookies observés sur la démonstration', 'Nom ou motif', 'Déposé par', 'À quel geste', 'Durée', 'Usage'];
    if ($domain !== 'imagine-site' || !in_array($text, $allowed, true)) {
        throw new \RuntimeException('Une donnée a été envoyée à la traduction');
    }
    $GLOBALS['c32_translated'][] = $text;
    return esc_html($text);
}
