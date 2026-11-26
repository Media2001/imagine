<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Lecture CRUD Woo/WCS, sans sauvegarde, relevé postal, note ou miroir. */
final class ExtractionsNatives
{
    public static function lire(string $id, array $request): array
    {
        $filters = ExtractionsRegles::filtres($id, $request);
        $definition = ExtractionsRegles::definition($id);
        if (!function_exists('wcs_get_subscriptions')) {
            throw new \RuntimeException('Subscriptions indisponible.');
        }
        $rows = [];
        for ($page = 1;; $page++) {
            $subscriptions = wcs_get_subscriptions($definition['requete'] + [
                'subscriptions_per_page' => 100, 'paged' => $page, 'orderby' => 'ID', 'order' => 'ASC',
            ]);
            foreach ($subscriptions as $sub) {
                $user = get_userdata($sub->get_customer_id());
                if (!$user) {
                    throw new \LogicException('Titulaire natif absent : extraction refusée.');
                }
                $dates = array_filter(
                    [(int) $sub->get_time('next_payment'), (int) $sub->get_time('end')],
                    static fn (int $date): bool => $date > 0
                );
                $row = [
                    'abonnement_id' => (string) $sub->get_id(), 'compte_id' => (string) $user->ID,
                    'prenom' => (string) $user->first_name, 'nom' => (string) $user->last_name,
                    'email' => get_user_meta($user->ID, SansEmail::META, true) === '1' ? '' : (string) $user->user_email,
                    'destinataire' => trim($sub->get_shipping_first_name() . ' ' . $sub->get_shipping_last_name()),
                    'rue' => $sub->get_shipping_address_1(), 'complement' => $sub->get_shipping_address_2(),
                    'code_postal' => $sub->get_shipping_postcode(), 'ville' => $sub->get_shipping_city(),
                    'pays' => $sub->get_shipping_country(),
                    'formule' => implode(', ', array_map(static fn ($item): string => $item->get_name(), array_values($sub->get_items()))),
                    'mode_paiement' => EcheancesNatives::methode($sub), 'etat' => MonCompte::etat($sub),
                    'echeance_utc' => $dates === [] ? '' : gmdate('Y-m-d H:i:s', min($dates)),
                ];
                $rows[] = $row;
            }
            if (count($subscriptions) < 100) {
                break;
            }
        }
        return ExtractionsRegles::selectionner($id, $filters, $rows);
    }
}
