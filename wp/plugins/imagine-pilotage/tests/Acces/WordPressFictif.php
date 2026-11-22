<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Acces;

/** Doubles de contrat uniquement : aucun WordPress ni stockage réel. */
final class WordPressFictif
{
    public static array $appels = [];
    public static mixed $option = null;
    public static bool $autorise = true;
    public static bool $panne = false;

    public static function reinitialiser(): void
    {
        self::$appels = [];
        self::$option = null;
        self::$autorise = true;
        self::$panne = false;
    }
}

namespace Imagine\Pilotage\Acces;

use Imagine\Pilotage\Tests\Acces\WordPressFictif as Banc;

function add_action(string $hook, callable $callback): void
{
    Banc::$appels['hooks'][$hook] = $callback;
}

function add_options_page(string $titre, string $menu, string $capacite, string $slug, callable $callback): void
{
    Banc::$appels['menu'] = compact('titre', 'menu', 'capacite', 'slug', 'callback');
}

function register_setting(string $groupe, string $option, array $args): void
{
    Banc::$appels['setting'] = compact('groupe', 'option', 'args');
}

function add_settings_section(string $id, string $titre, callable $callback, string $page): void
{
    Banc::$appels['section'] = compact('id', 'titre', 'callback', 'page');
}

function add_settings_field(
    string $id,
    string $titre,
    callable $callback,
    string $page,
    string $section,
    array $args,
): void {
    Banc::$appels['champs'][$id] = compact('titre', 'callback', 'page', 'section', 'args');
}

function get_option(string $option, mixed $defaut = false): mixed
{
    Banc::$appels['lectures'][] = $option;
    if (Banc::$panne) {
        throw new \RuntimeException('Stockage fictif indisponible');
    }
    return Banc::$option ?? $defaut;
}

function current_user_can(string $capacite): bool
{
    Banc::$appels['capacite'] = $capacite;
    return Banc::$autorise;
}

function __(string $texte, string $domaine): string
{
    Banc::$appels['traductions'][] = [$texte, $domaine];
    return $texte;
}

function esc_attr(string $texte): string
{
    return htmlspecialchars($texte, ENT_QUOTES, 'UTF-8');
}

function esc_html(string $texte): string
{
    return htmlspecialchars($texte, ENT_QUOTES, 'UTF-8');
}

function settings_fields(string $groupe): void
{
    // On vérifie la délégation au cœur, sans simuler la sécurité d'un nonce.
    Banc::$appels['fields_group'] = $groupe;
}

function settings_errors(string $option): void
{
    Banc::$appels['errors_option'] = $option;
}

function do_settings_sections(string $page): void
{
    Banc::$appels['sections_page'] = $page;
    foreach (Banc::$appels['champs'] as $champ) {
        ($champ['callback'])($champ['args']);
    }
}

function submit_button(): void
{
    Banc::$appels['submit_button'] = true;
}
