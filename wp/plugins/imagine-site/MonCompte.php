<?php

declare(strict_types=1);

namespace Imagine\Site;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Numeros\Moteur;
use Imagine\Pilotage\Echeancier\{Planificateur, ReglagesAdministration};

/** Lecture seule : tableau de bord Woo, pas de nouvelle source de droits ou de facture. */
final class MonCompte
{
    public static function register(): void
    {
        add_action('woocommerce_account_dashboard', [self::class, 'afficher']);
        // Subscriptions émet son propre object_type, pas after_order_object_save.
        // Réutilise le relevé C13 append-only et dédupliqué, sans changer C13/C07.
        // Raccord limité au formulaire client B02 : ne pas modifier les autres saves C13/C14.
        add_action('woocommerce_after_subscription_object_save', static function ($sub): void {
            if ($sub instanceof \WC_Subscription && did_action('woocommerce_customer_save_address') > 0
                && get_current_user_id() > 0 && (int) $sub->get_customer_id() === get_current_user_id()) {
                EnvoiNatif::relever($sub);
            }
        });
        add_action('template_redirect', static function (): void {
            if (function_exists('is_account_page') && is_account_page()) {
                nocache_headers();
                header('Cache-Control: private, no-store, no-cache, must-revalidate, max-age=0');
            }
        });
        // La lecture/édition du magazine concerne uniquement le titulaire, pas un ID fourni.
        add_filter('woocommerce_subscriptions_can_user_edit_subscription_address',
            static fn (bool $allowed, $sub, int $user): bool => $allowed && (int) $sub->get_customer_id() === $user, 10, 3);
    }

    private static function date(string $value): ?DateTimeImmutable
    {
        $date = DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $value, new DateTimeZone('UTC'));
        return $date && $date->format('Y-m-d H:i:s') === $value ? $date : null;
    }

    public static function etat(\WC_Subscription $sub): string
    {
        $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
        $end = self::date($sub->get_date('end', 'gmt'));
        if ($sub->has_status(['expired', 'cancelled']) || ($end && $end <= $now)) {
            return __('Expiré', 'imagine-site');
        }
        if ($sub->has_status(['active', 'pending-cancel'])) {
            return __('Actif', 'imagine-site');
        }
        if ($sub->has_status('pending')) {
            return __('Virement en attente de validation', 'imagine-site');
        }
        if ($sub->has_status('on-hold')) {
            $members = wc_memberships_get_user_memberships($sub->get_customer_id(), ['status' => 'any']) ?? [];
            foreach ($members as $member) {
                if ((int) get_post_meta($member->get_id(), '_subscription_id', true) === $sub->get_id()
                    && in_array($member->get_status(), ['pending', 'delayed'], true)) {
                    return __('Virement en attente de validation', 'imagine-site');
                }
            }
            $from = self::date((string) $sub->get_meta('_imagine_acces_grace_debut'));
            $until = self::date((string) $sub->get_meta('_imagine_acces_grace_fin'));
            if ($from && $until && $from <= $now && $now < $until) {
                return __('En délai de grâce', 'imagine-site');
            }
        }
        return __('Suspendu', 'imagine-site');
    }

    /** Renouvellements réellement rattachés, pas un calendrier de paiements deviné. */
    private static function echeances(\WC_Subscription $sub, Moteur $engine, $year): array
    {
        $positions = [];
        try {
            $margin = (new ReglagesAdministration())->lire()->margeJours;
            $positions = (new Planificateur($engine))->planifier($year, $margin);
        } catch (\Throwable) {
            // Marge obligatoire absente ou calendrier incomplet : positions nommées seulement.
        }
        $rows = [];
        for ($i = 1; $i <= 4; $i++) {
            $position = $positions[$i - 1] ?? null;
            $order = $i === 1 ? wc_get_order($sub->get_parent_id()) : null;
            if ($order && (int) $order->get_customer_id() !== get_current_user_id()) {
                $order = null;
            }
            $state = __('État de paiement non raccordé', 'imagine-site');
            if ($order) {
                $state = $order->has_status('failed') ? __('Échouée', 'imagine-site')
                    : ($order->is_paid() && $order->get_date_paid() ? __('Payée', 'imagine-site')
                        : __('Non réglée — commande native en attente', 'imagine-site'));
            }
            $rows[] = ['rang' => $i, 'numero' => $position?->numero->id,
                'date' => $position?->date->format('Y-m-d'), 'etat' => $state,
                'montant' => $order?->get_total(), 'devise' => $order?->get_currency()];
        }
        return $rows;
    }

    /** Le seul paramètre d'identité est la session WP. Aucun ID venant de GET/POST. */
    public static function donnees(): array
    {
        $user = get_current_user_id();
        if (!$user) {
            return [];
        }
        $out = ['user' => $user, 'abonnements' => [], 'numeros' => [], 'factures' => []];
        foreach (wcs_get_users_subscriptions($user) as $sub) {
            if ((int) $sub->get_customer_id() !== $user) {
                continue;
            }
            $items = array_map(static fn ($item): string => $item->get_name(), array_values($sub->get_items()));
            $row = ['id' => $sub->get_id(), 'formule' => implode(', ', $items), 'etat' => self::etat($sub),
                'premier' => null, 'dernier' => null, 'restants' => null,
                'prochaine' => $sub->get_date('next_payment', 'gmt'), 'montant' => $sub->get_total(),
                'devise' => $sub->get_currency(), 'paiement' => $sub->get_payment_method() !== ''
                    ? $sub->get_payment_method_title() : __('Moyen de paiement non raccordé', 'imagine-site'),
                'manuel' => $sub->get_requires_manual_renewal(), 'echeances' => [], 'echec' => false,
                'vue' => $sub->get_view_order_url(), 'adresse' => $sub->get_address('shipping'),
                'edition_adresse' => add_query_arg('subscription', $sub->get_id(), wc_get_endpoint_url('edit-address', 'shipping', wc_get_page_permalink('myaccount')))];
            try {
                $engine = new Moteur(EnvoiNatif::calendrier());
                $start = self::date($sub->get_date('start', 'gmt'));
                if (!$start) {
                    throw new \RuntimeException('Début natif absent');
                }
                $year = $engine->ouvrir($start);
                $row['premier'] = $engine->premier($year)?->id;
                $row['dernier'] = $engine->dernier($year)?->id;
                // Aucun historique d'activation/réactivation C01 natif n'est branché ici.
                // Ne pas transformer l'état administratif actif en paiement ou numéros restants.
                if ($sub->get_billing_period() === 'month' && (int) $sub->get_billing_interval() === 3) {
                    $row['echeances'] = self::echeances($sub, $engine, $year);
                }
            } catch (\Throwable) {
                // Les emplacements restent nommés, jamais des nombres fabriqués.
            }
            $related = array_unique([$sub->get_parent_id(), ...array_values($sub->get_related_orders('ids', 'renewal'))]);
            foreach ($related as $id) {
                $order = wc_get_order($id);
                if ($order && (int) $order->get_customer_id() === $user && $order->has_status('failed')) {
                    $row['echec'] = true;
                    if ($order->needs_payment()) {
                        $row['regulariser'] = $order->get_checkout_payment_url();
                    }
                }
            }
            $out['abonnements'][] = $row;
        }
        foreach (get_posts(['post_type' => 'imagine_numero', 'post_status' => 'publish', 'posts_per_page' => -1,
            'meta_key' => 'imagine_sortie', 'orderby' => 'meta_value', 'order' => 'DESC']) as $issue) {
            if (Paywall::decisionPdf($issue)['complet']) {
                $out['numeros'][] = ['id' => $issue->ID, 'titre' => get_the_title($issue),
                    'url' => get_permalink($issue), 'pdf' => PdfNumero::url($issue->ID)];
            }
        }
        return $out;
    }

    public static function afficher(): void
    {
        $compte = self::donnees();
        if (!$compte) {
            return;
        }
        $template = get_theme_file_path('/parts/mon-compte.php');
        if (is_file($template)) {
            require $template;
        }
    }
}
