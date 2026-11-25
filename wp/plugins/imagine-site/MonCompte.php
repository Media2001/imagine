<?php

declare(strict_types=1);

namespace Imagine\Site;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Numeros\Moteur;
use Imagine\Pilotage\Echeancier\ReglagesAdministration;

require_once __DIR__ . '/MonCompteRegles.php';

/** Lecture seule : tableau de bord Woo, pas de nouvelle source de droits ou de facture. */
final class MonCompte
{
    public static function register(): void
    {
        add_action('woocommerce_account_dashboard', [self::class, 'afficher']);
        // Le relevé postal des sauvegardes appartient à EnvoiNatif, sans doublon B02.
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

    public static function etat(\WC_Subscription $sub): string
    {
        $available = function_exists('wc_memberships_get_user_memberships');
        $pending = false;
        if ($sub->has_status('on-hold') && $available) {
            foreach (wc_memberships_get_user_memberships($sub->get_customer_id(), ['status' => 'any']) ?? [] as $member) {
                if ((int) get_post_meta($member->get_id(), '_subscription_id', true) === $sub->get_id()
                    && in_array($member->get_status(), ['pending', 'delayed'], true)) {
                    $pending = true;
                }
            }
        }
        return __(MonCompteRegles::etat([
            'status' => $sub->get_status(), 'end' => $sub->get_date('end', 'gmt'),
            'method' => $sub->get_payment_method(), 'membership_pending' => $pending,
            'memberships_available' => $available,
            'grace_from' => (string) $sub->get_meta('_imagine_acces_grace_debut'),
            'grace_until' => (string) $sub->get_meta('_imagine_acces_grace_fin'),
        ], new DateTimeImmutable('now', new DateTimeZone('UTC'))), 'imagine-site');
    }

    /** Le seul paramètre d'identité est la session WP. Aucun ID venant de GET/POST. */
    public static function donnees(): array
    {
        $user = get_current_user_id();
        if (!$user) {
            return [];
        }
        $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
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
            $source = ['owner' => $user, 'period' => $sub->get_billing_period(), 'interval' => $sub->get_billing_interval(),
                'start' => $sub->get_date('start', 'gmt'), 'total' => $sub->get_total(), 'currency' => $sub->get_currency(),
                'renouvellements' => EnvoiRelations::renouvellements($sub), 'orders' => []];
            $related = array_unique([$sub->get_parent_id(), ...array_values($sub->get_related_orders('ids', 'renewal'))]);
            foreach ($related as $id) {
                $order = $id ? wc_get_order($id) : null;
                if (!$order) {
                    continue;
                }
                $source['orders'][] = ['id' => (int) $order->get_id(), 'owner' => (int) $order->get_customer_id(),
                    'initial' => (int) $id === (int) $sub->get_parent_id(),
                    'created' => $order->get_date_created() ? gmdate('Y-m-d H:i:s', $order->get_date_created()->getTimestamp()) : '',
                    'paid' => $order->is_paid(), 'paid_at' => $order->get_date_paid() ? gmdate('Y-m-d H:i:s', $order->get_date_paid()->getTimestamp()) : '',
                    'status' => $order->get_status(), 'total' => $order->get_total(), 'currency' => $order->get_currency(),
                    'bloc_debut' => (string) $order->get_meta('_imagine_envoi_bloc_debut')];
                if ((int) $order->get_customer_id() === $user && $order->has_status('failed')) {
                    $row['echec'] = true;
                    if ($order->needs_payment()) {
                        $row['regulariser'] = $order->get_checkout_payment_url();
                    }
                }
            }
            // Les quatre emplacements et paiements ne dépendent pas du calendrier postal.
            $projection = MonCompteRegles::projeter($source, $now);
            try {
                $engine = new Moteur(EnvoiNatif::calendrier());
                $margin = null;
                try {
                    $margin = (new ReglagesAdministration())->lire()->margeJours;
                } catch (\Throwable) {
                    // Réglage obligatoire inexploitable : aucune date théorique inventée.
                }
                $projection = MonCompteRegles::projeter($source, $now, $engine, $margin);
            } catch (\Throwable) {
                // Référence absente/invalide : conserver les positions et règlements déjà lus.
            }
            $out['abonnements'][] = array_replace($row, $projection);
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
