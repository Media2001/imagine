<?php

declare(strict_types=1);
namespace Imagine\Site;

/** Écran natif et contrôleur d'export : capacité indépendante du nonce. */
final class ListeEnvoiAdmin
{
    public const CAP = 'imagine_exporter_liste_envoi';
    public const PAGE = 'imagine-liste-envoi';
    public const ACTION = 'imagine_exporter_liste_envoi';
    public const JOURNAL = 'imagine_envoi_export_journal_';

    public static function autorise(): bool
    {
        return current_user_can('manage_options') || current_user_can(self::CAP);
    }
}
