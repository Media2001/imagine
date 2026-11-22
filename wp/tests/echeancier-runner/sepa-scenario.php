<?php

declare(strict_types=1);

use Imagine\Pilotage\Echeancier\ReglagesAdministration;

/** Réglage réel WP, sans débit, expédition, droits ou modification de date de paiement. */
function c05SepaScenario(ReglagesAdministration $admin): void
{
    wp_set_current_user(get_user_by('login', 'c05-fiction')->ID);
    ob_start();
    $admin->afficher();
    $html = ob_get_clean();
    c05Check('sepa_admin_field_present', str_contains($html, '[confirmation_premier_sepa]'));
    $settings = get_registered_settings()[ReglagesAdministration::OPTION];
    c05Check('sepa_admin_default_with_margin', $settings['default']['confirmation_premier_sepa'] === 'avec_marge');
    c05Check('sepa_old_option_defaults_with_margin', $admin->lire()->confirmationPremierSepa === 'avec_marge');
    foreach (['avec_marge', 'sans_marge'] as $position) {
        update_option(ReglagesAdministration::OPTION, [
            'marge_jours' => '7', 'apres_rejet' => 'restent_dues', 'tarif' => 'fige_bloc',
            'confirmation_premier_sepa' => $position,
        ], false);
        c05Check('sepa_admin_persisted_readback', get_option(ReglagesAdministration::OPTION)['confirmation_premier_sepa'] === $position);
        $reglages = $admin->lire();
        c05Check('sepa_admin_decoded_readback', $reglages->confirmationPremierSepa === $position);
        ob_start();
        $admin->afficher();
        $html = ob_get_clean();
        c05Check('sepa_admin_selection_rendered', preg_match('/value="' . $position . '"\s+selected/', $html) === 1);
        $commande = c05Date('2027-04-09 12:00:00');
        $confirmation = c05Date('2027-04-09 13:00:00');
        $paye = $reglages->premierSepaPayeLe($commande, $confirmation);
        $attendu = $position === 'avec_marge' ? c05Date('2027-04-16 12:00:00') : $confirmation;
        c05Check('sepa_admin_changes_paid_projection', $paye == $attendu, [
            'position' => $position, 'commande' => $commande->format(DATE_ATOM),
            'confirmation_fixture' => $confirmation->format(DATE_ATOM), 'paye_le' => $paye?->format(DATE_ATOM),
        ]);
        c05Check('sepa_not_paid_before_effective_date', $paye > $attendu->modify('-1 microsecond'));
        c05Check('sepa_paid_at_effective_date', $paye <= $attendu);
        c05Check('sepa_paid_before_closure_policy', ($paye < c05Date('2027-04-10')) === ($position === 'sans_marge'));
        c05Check('sepa_no_confirmation_never_paid', $reglages->premierSepaPayeLe($commande, null) === null);
        $late = c05Date('2027-04-19 14:00:00');
        c05Check('sepa_late_confirmation_never_anticipated', $reglages->premierSepaPayeLe($commande, $late) == $late);
        $before = get_option(ReglagesAdministration::OPTION);
        foreach (['inconnu', '', null, true, []] as $invalid) {
            update_option(ReglagesAdministration::OPTION, [
                'marge_jours' => '7', 'confirmation_premier_sepa' => $invalid,
            ], false);
            c05Check('sepa_invalid_keeps_previous', get_option(ReglagesAdministration::OPTION) === $before);
        }
    }
    // Aucun réglage ne modifie une commande ou une action : la projection reste pure.
    update_option(ReglagesAdministration::OPTION, [
        'marge_jours' => '7', 'apres_rejet' => 'restent_dues', 'tarif' => 'fige_bloc',
        'confirmation_premier_sepa' => 'avec_marge',
    ], false);
    wp_set_current_user(0);
}
