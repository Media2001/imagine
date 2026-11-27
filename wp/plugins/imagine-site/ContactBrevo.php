<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Lecture native à la demande ; ni cache persistant ni transport. */
final class ContactBrevo
{
    public const PAGE = 'imagine-contact-brevo';
    public const TARIFS = 'imagine_brevo_tarifs';

    public static function register(): void
    {
        // Le raccord de l'écran arrive avec sa réception dédiée.
    }

    public static function fiche(int $id): array
    {
        $user = get_userdata($id);
        return ContactBrevoRegles::fiche([
            'existe' => (bool)$user, 'email_recevable' => $user && Newsletters::admissible($id),
            'email' => $user ? $user->user_email : '', 'catalogue' => array_column(Newsletters::catalogue(), 'id'),
            'preferences' => Newsletters::preferences($id), 'abonnements' => [], 'beneficiaire' => false,
            'cooperateur' => false, 'tarifs_autorises' => [],
            'personnalisation' => Personnalisation::attributsConnecteur($id),
        ]);
    }
}
