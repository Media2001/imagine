<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Lecture CRUD des liens présents ; aucun rapprochement par email ni bénéficiaire déduit du payeur. */
final class EnvoiRelations
{
    public static function beneficiaires(\WC_Subscription $sub): array
    {
        $gift = $sub->meta_exists('_recipient_user') || $sub->get_meta('_recipient_user_email_address') !== ''
            || (class_exists('WCS_Gifting') && \WCS_Gifting::is_gifted_subscription($sub));
        $plans = get_option('imagine_acces_plans', []);
        $groupPlans = array_keys(array_filter($plans, static fn ($type): bool => $type === 'groupe'));
        $memberships = get_posts(['post_type' => 'wc_user_membership', 'post_status' => 'any',
            'posts_per_page' => -1, 'orderby' => 'ID', 'order' => 'ASC',
            'meta_key' => '_subscription_id', 'meta_value' => (string) $sub->get_id()]);
        $group = [];
        foreach ($memberships as $post) {
            $membership = wc_memberships_get_user_membership($post->ID);
            if ($membership && ($plans[$membership->get_plan_id()] ?? null) === 'offert') {
                $gift = true;
            }
            if ($membership && in_array($membership->get_plan_id(), $groupPlans, true)) {
                $group[] = $membership;
            }
        }
        // Un groupe sans place attribuée reste identifiable par les produits du plan natif.
        $capacity = 0;
        foreach ($sub->get_items() as $item) {
            foreach ($plans as $planId => $type) {
                if ($type !== 'offert') {
                    continue;
                }
                $plan = wc_memberships_get_membership_plan($planId);
                if ($plan && in_array($item->get_product_id(), $plan->get_product_ids(), true)) {
                    $gift = true;
                }
            }
            foreach ($groupPlans as $planId) {
                $plan = wc_memberships_get_membership_plan($planId);
                if ($plan && in_array($item->get_product_id(), $plan->get_product_ids(), true)) {
                    $capacity += (int) $item->get_quantity();
                    break;
                }
            }
        }
        if (!$gift && !$group && !$capacity) {
            return ['origine' => 'abonnement', 'beneficiaires' => [], 'beneficiaires_resolus' => true];
        }
        if ($gift) {
            $raw = class_exists('WCS_Gifting') ? \WCS_Gifting::get_recipient_user($sub) : $sub->get_meta('_recipient_user');
            $valid = (is_string($raw) || is_int($raw)) && preg_match('/^[1-9][0-9]*$/D', (string) $raw)
                && (string) (int) $raw === (string) $raw;
            $id = $valid ? (int) $raw : 0;
            $user = $id ? get_userdata($id) : false;
            // L'adresse de livraison du cadeau appartient au destinataire, pas à la facturation du payeur.
            $p = self::adresse((string) $id, $sub->get_address('shipping'));
            return ['origine' => 'offert', 'beneficiaires' => $user ? [$p] : [],
                'beneficiaires_resolus' => (bool) $user && $group === [] && $capacity === 0,
                'relation_native' => ['recipient_user' => $raw]];
        }
        $people = $links = [];
        $resolved = $capacity > 0 && get_option('imagine_envoi_groupes', 'ferme') === 'liens_memberships';
        foreach ($group as $membership) {
            $id = (int) $membership->get_user_id();
            $links[] = ['membership_id' => $membership->get_id(), 'user_id' => $id,
                'etat' => $membership->get_status(), 'debut' => $membership->get_start_date(),
                'fin' => $membership->get_end_date()];
            if (!$membership->is_active()) {
                continue; // Une place non active n'est pas une attribution postale active.
            }
            if (!$id || !get_userdata($id) || isset($people[$id])) {
                $resolved = false;
                continue;
            }
            $customer = new \WC_Customer($id);
            $address = [];
            foreach (['first_name', 'last_name', 'address_1', 'address_2', 'postcode', 'city', 'country'] as $key) {
                $method = 'get_shipping_' . $key;
                $address[$key] = $customer->$method();
            }
            $people[$id] = self::adresse((string) $id, $address);
        }
        return ['origine' => 'groupe', 'beneficiaires' => array_values($people),
            'beneficiaires_resolus' => $resolved && count($people) <= $capacity, 'places' => $capacity,
            'relation_native' => $links];
    }

    private static function adresse(string $id, array $address): array
    {
        return ['id' => $id, 'nom' => trim(($address['first_name'] ?? '') . ' ' . ($address['last_name'] ?? '')),
            'rue' => $address['address_1'] ?? '', 'complement' => $address['address_2'] ?? '',
            'code_postal' => $address['postcode'] ?? '', 'ville' => $address['city'] ?? '', 'pays' => $address['country'] ?? ''];
    }

    public static function paiementInitial(\WC_Subscription $sub): ?int
    {
        $parent = $sub->get_parent_id() ? wc_get_order($sub->get_parent_id()) : null;
        if ($parent) {
            $refunds = wc_get_orders(['type' => 'shop_order_refund', 'parent' => $parent->get_id(), 'limit' => 1]);
            return $parent->is_paid() && !$refunds && $parent->get_customer_id() === $sub->get_customer_id()
                ? $parent->get_date_paid()?->getTimestamp() : null;
        }
        // WCS recopie le dernier règlement sur la souscription ; il ne prouve pas l'année initiale.
        return $sub->get_related_orders('ids', 'renewal') === [] ? $sub->get_date_paid()?->getTimestamp() : null;
    }

    public static function renouvellements(\WC_Subscription $sub): array
    {
        $rows = [];
        foreach ($sub->get_related_orders('all', 'renewal') as $order) {
            $date = $order->get_date_paid();
            $explicit = $order->get_meta('_imagine_envoi_bloc_debut');
            // Quatre échéances ne sont pas quatre années. Sans rang explicite, annuel 1 seulement.
            if ($explicit === '' && ($sub->get_billing_period() !== 'year' || (int) $sub->get_billing_interval() !== 1)) {
                continue;
            }
            $refunds = wc_get_orders(['type' => 'shop_order_refund', 'parent' => $order->get_id(), 'limit' => 1]);
            if (!$order->is_paid() || !$date || $refunds || $order->get_customer_id() !== $sub->get_customer_id()) {
                continue;
            }
            $rows[] = ['id' => (string) $order->get_id(),
                'debut' => $explicit !== '' ? $explicit : gmdate('Y-m-d H:i:s', $date->getTimestamp()),
                'paiement' => $date->getTimestamp()];
        }
        usort($rows, static fn (array $a, array $b): int => strcmp($a['debut'], $b['debut']));
        return $rows;
    }
}
