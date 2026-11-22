<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Envoi;

/** Doublures locales aux tests ; aucune fonction WordPress globale ni persistance native prétendue. */
final class AdministrationFictive
{
    public static mixed $option = null;
    public static array $appels = [];
    public static bool $autorise = true;
}

function get_option(string $nom, mixed $defaut = false): mixed
{
    return AdministrationFictive::$option ?? $defaut;
}

function add_settings_error(...$arguments): void
{
    AdministrationFictive::$appels['erreur'][] = $arguments;
}

function __(string $texte, string $domaine): string
{
    return $texte;
}

function add_action(...$arguments): void
{
    AdministrationFictive::$appels['action'][] = $arguments;
}

function add_options_page(...$arguments): void
{
    AdministrationFictive::$appels['menu'][] = $arguments;
}

function register_setting(...$arguments): void
{
    AdministrationFictive::$appels['reglage'][] = $arguments;
}

function add_settings_section(...$arguments): void
{
    AdministrationFictive::$appels['section'][] = $arguments;
}

function add_settings_field(...$arguments): void
{
    AdministrationFictive::$appels['champ'][] = $arguments;
}

function current_user_can(string $capacite): bool
{
    return $capacite === 'manage_options' && AdministrationFictive::$autorise;
}

function esc_html(string $valeur): string
{
    return htmlspecialchars($valeur, ENT_QUOTES, 'UTF-8');
}

function esc_attr(string $valeur): string
{
    return esc_html($valeur);
}

function esc_textarea(string $valeur): string
{
    return esc_html($valeur);
}

function settings_errors(string $groupe): void
{
    AdministrationFictive::$appels['afficher_erreurs'][] = $groupe;
}

function settings_fields(string $groupe): void
{
    AdministrationFictive::$appels['nonce'][] = $groupe;
}

function do_settings_sections(string $page): void
{
    foreach (AdministrationFictive::$appels['champ'] as $champ) {
        if ($champ[3] === $page) {
            ($champ[2])();
        }
    }
}

function submit_button(): void
{
    AdministrationFictive::$appels['bouton'][] = true;
}
