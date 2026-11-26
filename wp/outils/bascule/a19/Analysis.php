<?php

declare(strict_types=1);

namespace Imagine\SubscriptionCoherence;

final class Analysis
{
    public static function technical(string $value): string
    {
        return preg_match('/\A[a-z][a-z0-9_-]{0,79}\z/D', $value) ? $value : 'autre';
    }

    public static function analyse(array $subscriptions, array $memberships, int $asOf): array
    {
        $buckets = ['cross' => [], 'subscriptions_without_membership' => [],
            'memberships_without_subscription' => [], 'memberships_missing_subscription' => [],
            'multiple_active_membership_accounts_by_plan' => [], 'automatic_without_saved_payment' => [],
            'automatic_payment_reference_unknown' => [], 'manual_by_gateway' => []];
        $add = static function (string $kind, array $fields) use (&$buckets): void {
            $key = json_encode($fields, JSON_THROW_ON_ERROR);
            $buckets[$kind][$key] ??= array_merge($fields, ['count' => 0]);
            $buckets[$kind][$key]['count']++;
        };
        $linked = [];
        $activeMembers = [];
        $membershipStates = ['active', 'complimentary', 'free_trial', 'delayed', 'paused', 'pending',
            'expired', 'cancelled', 'draft'];
        $subscriptionStates = ['active', 'on-hold', 'pending', 'pending-cancel', 'cancelled',
            'expired', 'switched', 'draft'];
        foreach ($memberships as $membership) {
            $plan = (int) $membership['plan'];
            $status = in_array($membership['status'], $membershipStates, true) ? $membership['status'] : 'autre';
            $subId = (int) $membership['subscription'];
            if ($subId <= 0) {
                $add('memberships_without_subscription', ['plan' => $plan, 'status' => $status]);
            } elseif (!isset($subscriptions[$subId])) {
                $add('memberships_missing_subscription', ['plan' => $plan, 'status' => $status]);
            } else {
                $linked[$subId] = true;
                $subStatus = $subscriptions[$subId]['status'];
                $subStatus = in_array($subStatus, $subscriptionStates, true) ? $subStatus : 'autre';
                $add('cross', ['plan' => $plan, 'subscription_status' => $subStatus, 'membership_status' => $status]);
            }
            if ($status === 'active' && (int) $membership['user'] > 0) {
                $user = (int) $membership['user'];
                $activeMembers[$plan][$user] = ($activeMembers[$plan][$user] ?? 0) + 1;
            }
        }
        $activeSubs = [];
        $pastNextPayment = 0;
        $withoutPaidOrder = 0;
        foreach ($subscriptions as $id => $subscription) {
            $status = in_array($subscription['status'], $subscriptionStates, true)
                ? $subscription['status'] : 'autre';
            $gateway = $subscription['gateway'] === '' ? 'aucune' : self::technical($subscription['gateway']);
            if (!isset($linked[$id])) {
                $add('subscriptions_without_membership', ['status' => $status]);
            }
            if ($subscription['manual']) {
                $add('manual_by_gateway', ['gateway' => $gateway]);
            }
            if ($status !== 'active') {
                continue;
            }
            if ((int) $subscription['user'] > 0) {
                $user = (int) $subscription['user'];
                $activeSubs[$user] = ($activeSubs[$user] ?? 0) + 1;
            }
            if (!$subscription['manual']) {
                if ($subscription['reference'] === 'absent') {
                    $add('automatic_without_saved_payment', ['gateway' => $gateway]);
                } elseif ($subscription['reference'] !== 'present') {
                    $add('automatic_payment_reference_unknown', ['gateway' => $gateway]);
                }
            }
            $pastNextPayment += (int) ($subscription['next'] > 0 && $subscription['next'] < $asOf);
            $withoutPaidOrder += (int) !$subscription['paid'];
        }
        $duplicateMemberAccounts = [];
        foreach ($activeMembers as $plan => $users) {
            foreach ($users as $user => $count) {
                if ($count > 1) {
                    $duplicateMemberAccounts[$user] = true;
                    $add('multiple_active_membership_accounts_by_plan', ['plan' => $plan]);
                }
            }
        }
        $result = [];
        foreach ($buckets as $kind => $rows) {
            $rows = array_values($rows);
            usort($rows, static fn (array $a, array $b): int => array_values($a) <=> array_values($b));
            $result[$kind] = $rows;
        }
        $result['multiple_active_subscription_accounts'] = count(array_filter($activeSubs, static fn ($n) => $n > 1));
        $result['multiple_active_membership_accounts'] = count($duplicateMemberAccounts);
        $result['active_past_next_payment'] = $pastNextPayment;
        $result['active_without_paid_order'] = $withoutPaidOrder;
        $result['definitions'] = [
            'cross' => 'Chaque adhesion explicitement liee compte une fois, par plan et couple detats.',
            'subscriptions_without_membership' => 'Abonnements sans aucune adhesion portant leur lien, par etat.',
            'memberships_without_subscription' => 'Adhesions sans lien numerique positif, par plan et etat.',
            'memberships_missing_subscription' => 'Adhesions avec lien positif vers un abonnement absent du magasin lu.',
            'multiple_active_subscription_accounts' => 'Comptes non invites avec plus dun abonnement de strict etat actif.',
            'multiple_active_membership_accounts' => 'Comptes distincts avec plusieurs adhesions actives au meme plan.',
            'multiple_active_membership_accounts_by_plan' => 'Comptes distincts par plan, pas nombre dadhesions en trop.',
            'automatic_without_saved_payment' => 'Actifs declares automatiques sans passerelle ou reference native requise.',
            'automatic_payment_reference_unknown' => 'Actifs declares automatiques sans adaptateur de reference connu.',
            'active_past_next_payment' => 'Actifs avec prochain paiement UTC positif strictement avant la reference.',
            'active_without_paid_order' => 'Actifs sans commande liee avec date payee ou statut natif paye.',
            'manual_by_gateway' => 'Tous etats non supprimes ; renouvellement manuel declare, par passerelle.',
        ];
        return $result;
    }
}
