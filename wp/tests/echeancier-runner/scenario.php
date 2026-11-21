<?php

declare(strict_types=1);

use Imagine\Pilotage\Echeancier\Planificateur;
use Imagine\Pilotage\Echeancier\RaccordManuel;
use Imagine\Pilotage\Numeros\Activation;
use Imagine\Pilotage\Numeros\Moteur;
use Automattic\WooCommerce\Utilities\OrderUtil;

define('IMAGINE_C05_FIXTURE', true);
require '/work/wp/plugins/imagine-pilotage/tests/Echeancier/run.php';

function c05Check(string $name, bool $pass, mixed $detail = null): void
{
    $GLOBALS['imagine_c05_checks'][] = ['check' => $name, 'pass' => $pass, 'detail' => $detail];
    if (!$pass) {
        throw new RuntimeException($name . ': ' . json_encode($detail));
    }
}

function c05Related(WC_Subscription $subscription): array
{
    return array_map('intval', $subscription->get_related_orders('ids', 'renewal'));
}

$checks = [];
$scenarios = [];
$error = null;
try {
    c05Check('real_subscriptions_loaded', class_exists('WC_Subscriptions_Manager'));
    c05Check('mail_and_http_blocked', apply_filters('pre_wp_mail', null, []) === false);
    $source = new Moteur(c05Calendrier());
    $planner = new Planificateur($source);
    $adapter = new RaccordManuel();
    $product = new WC_Product_Subscription();
    $product->set_name('FICTION C05 — fraction synthétique');
    $product->set_regular_price('10');
    $product->update_meta_data('_subscription_price', '10');
    $product->update_meta_data('_subscription_period', 'month');
    $product->update_meta_data('_subscription_period_interval', '3');
    $product->update_meta_data('_subscription_length', '0');
    $product->save();
    foreach (['2027-02-20 12:00:00', '2027-04-10 12:00:00', '2027-10-11 12:00:00'] as $dateCommande) {
        $first = c05Annee($dateCommande);
        $startNext = $first->finNumerique();
        $second = $source->renouveler($first, $startNext)->activer($startNext, Activation::Paiement);
        $plan1 = $planner->planifier($first, $first->finNumerique(), 7);
        $plan2 = $planner->planifier($second, $second->finNumerique(), 7);
        $all = [...$plan1, ...$plan2];
        $parent = wc_create_order([
            'status' => 'pending', 'created_via' => 'imagine_c05_fixture',
            'customer_id' => (int) get_user_by('login', 'c05-fiction')->ID,
        ]);
        $parent->add_product($product, 1);
        $parent->set_billing_email('c05-fiction@example.org');
        $parent->set_currency('EUR');
        $parent->set_date_created($first->debut);
        $parent->calculate_totals();
        $parent->save();
        $subscription = wcs_create_subscription([
            'order_id' => $parent->get_id(), 'status' => 'pending',
            'date_created' => gmdate('Y-m-d H:i:s', time() - 60),
            'billing_period' => 'month', 'billing_interval' => 3,
            'start_date' => $first->debut->setTimezone(new DateTimeZone('UTC'))->format('Y-m-d H:i:s'),
        ]);
        c05Check('created_subscription', $subscription instanceof WC_Subscription, is_wp_error($subscription) ? $subscription->get_error_message() : null);
        $subscription->add_product($product, 1);
        $subscription->set_currency('EUR');
        $subscription->set_billing_email('c05-fiction@example.org');
        $subscription->set_requires_manual_renewal(true);
        $subscription->set_payment_method('');
        $subscription->calculate_totals();
        $subscription->update_meta_data('imagine_c05_fixture', 'yes');
        $subscription->save();
        $initialRefuse = false;
        try {
            $adapter->positionner($subscription, $all[0]);
        } catch (LogicException $e) {
            $initialRefuse = str_contains($e->getMessage(), 'renouvellement');
        }
        c05Check('initial_cannot_be_scheduled_as_renewal', $initialRefuse);
        $subscription->set_requires_manual_renewal(false);
        $subscription->save();
        $automatiqueRefuse = false;
        try {
            $adapter->positionner($subscription, $all[1]);
        } catch (LogicException $e) {
            $automatiqueRefuse = str_contains($e->getMessage(), 'manuels fictifs');
        }
        c05Check('automatic_payment_subscription_refused', $automatiqueRefuse);
        $subscription->set_requires_manual_renewal(true);
        $subscription->set_payment_method('imagine_c05_not_a_gateway');
        $subscription->save();
        $gatewayRefuse = false;
        try {
            $adapter->positionner($subscription, $all[1]);
        } catch (LogicException $e) {
            $gatewayRefuse = str_contains($e->getMessage(), 'manuels fictifs');
        }
        c05Check('nonempty_gateway_id_refused', $gatewayRefuse);
        $subscription->set_payment_method('');
        $subscription->set_requires_manual_renewal(true);
        $subscription->save();
        $parent->save();
        $parent->payment_complete(); // Woo transition only: no payment gateway call.
        $subscription = wcs_get_subscription($subscription->get_id());
        if (!$subscription->has_status('active')) {
            $subscription->update_status('active');
        }
        $rows = [[
            'cycle' => 1, 'rang' => 1, 'initial' => true, 'numero' => $all[0]->numero->id,
            'date' => $all[0]->date->format(DATE_ATOM), 'order_id' => $parent->get_id(),
            'date_paid' => wc_get_order($parent->get_id())->get_date_paid()->format(DATE_ATOM),
        ]];
        foreach (array_slice($all, 1) as $index => $v) {
            $cycle = $index < 3 ? 1 : 2;
            $adapter->positionner($subscription, $v);
            $adapter->positionner($subscription, $v); // Same target must not duplicate an AS action.
            $subscription = wcs_get_subscription($subscription->get_id());
            c05Check('native_next_payment_exact', $subscription->get_time('next_payment') === $v->date->getTimestamp(), $v->date->format(DATE_ATOM));
            $ids = as_get_scheduled_actions([
                'hook' => 'woocommerce_scheduled_subscription_payment',
                'args' => ['subscription_id' => $subscription->get_id()],
                'status' => 'pending', 'per_page' => 20,
            ], 'ids');
            c05Check('one_native_action_after_replay', count($ids) === 1, $ids);
            $actionId = (int) $ids[0];
            $action = ActionScheduler::store()->fetch_action($actionId);
            $scheduled = $action->get_schedule()->get_date()->getTimestamp();
            c05Check('native_action_date_exact', $scheduled === $v->date->getTimestamp(), $scheduled);
            $before = c05Related($subscription);
            // Accelerated fixture: execute only this owned future action; never run a queue or alter a clock.
            ActionScheduler::runner()->process_action($actionId, 'imagine-c05-offline-fixture');
            $after = c05Related(wcs_get_subscription($subscription->get_id()));
            $new = array_values(array_diff($after, $before));
            c05Check('real_manual_renewal_created', count($new) === 1, $new);
            c05Check('action_completed', ActionScheduler::store()->get_status($actionId) === 'complete');
            $renewal = wc_get_order($new[0]);
            c05Check('pending_not_paid_before_validation', $renewal->has_status('pending') && !$renewal->is_paid(), $renewal->get_status());
            c05Check('native_relationship', wcs_order_contains_renewal($renewal));
            $renewal->update_meta_data('imagine_c05_cycle', $cycle);
            $renewal->update_meta_data('imagine_c05_rang', $v->rang);
            $renewal->update_meta_data('imagine_c05_numero', $v->numero->id);
            $renewal->update_meta_data('imagine_c05_date', $v->date->format(DATE_ATOM));
            $renewal->save();
            $renewal->payment_complete(); // Local fixture acceptance, not a financial transaction.
            $renewal = wc_get_order($renewal->get_id());
            $subscription = wcs_get_subscription($subscription->get_id());
            c05Check('synthetic_validation_paid_and_active', $renewal->is_paid() && $subscription->has_status('active'));
            c05Check('confirmation_has_real_wc_paid_date', $renewal->get_date_paid() !== null);
            // Validation executes now in accelerated mode; actual paid timestamp is not forged as a due date.
            // Reprocessing an already completed action is NOT done; cursor identity is order+cycle+rank.
            $rows[] = [
                'cycle' => $cycle, 'rang' => $v->rang, 'initial' => false, 'numero' => $v->numero->id,
                'date' => $v->date->format(DATE_ATOM), 'order_id' => $renewal->get_id(),
                'date_paid' => $renewal->get_date_paid()->format(DATE_ATOM),
                'action_id' => $actionId, 'native_action_timestamp' => $scheduled,
                'status' => $renewal->get_status(),
            ];
        }
        c05Check('seven_real_renewals', count(c05Related($subscription)) === 7);
        c05Check('no_gateway_and_manual', $subscription->is_manual() && $subscription->get_payment_method() === '');
        foreach ([1, 2] as $cycle) {
            $subset = array_values(array_filter($rows, static fn (array $r): bool => $r['cycle'] === $cycle));
            c05Check('four_positions_cycle_' . $cycle, count($subset) === 4);
            $left = $cycle === 1 ? $first->debut : $second->debut;
            $right = $cycle === 1 ? $first->finNumerique() : $second->finNumerique();
            c05Check('four_in_anniversary_window_' . $cycle, count(array_filter(
                $rows,
                static fn (array $r): bool => c05Date($r['date']) >= $left && c05Date($r['date']) < $right
            )) === 4);
        }
        // Do not leave a fabricated ninth amount queued after the finite two-year demonstration.
        $adapter->arreterProjection($subscription);
        $subscription = wcs_get_subscription($subscription->get_id());
        c05Check('projection_stopped_without_cancelling_contract', $subscription->get_time('next_payment') === 0 && $subscription->has_status('active'));
        $remaining = as_get_scheduled_actions([
            'hook' => 'woocommerce_scheduled_subscription_payment',
            'args' => ['subscription_id' => $subscription->get_id()], 'status' => 'pending',
        ], 'ids');
        c05Check('no_ninth_native_action', $remaining === []);
        $subscription->delete_meta_data('imagine_c05_fixture');
        $subscription->save();
        $refused = false;
        try {
            $adapter->positionner($subscription, $all[1]);
        } catch (LogicException $e) {
            $refused = str_contains($e->getMessage(), 'fictifs C05');
        }
        c05Check('non_fixture_refused_without_write', $refused && wcs_get_subscription($subscription->get_id())->get_time('next_payment') === 0);
        $scenarios[] = ['commande' => $dateCommande, 'subscription_id' => $subscription->get_id(),
                         'rows' => $rows, 'renewals' => count(c05Related($subscription))];
    }
} catch (Throwable $e) {
    $error = ['class' => $e::class, 'message' => $e->getMessage(), 'line' => $e->getLine()];
}
$checks = $GLOBALS['imagine_c05_checks'] ?? [];
$failed = count(array_filter($checks, static fn (array $c): bool => !$c['pass'])) + (int) ($error !== null);
echo 'C05_JSON=' . json_encode([
    'versions' => ['wordpress' => get_bloginfo('version'), 'woocommerce' => WC_VERSION,
                  'subscriptions' => WC_Subscriptions::$version, 'php' => PHP_VERSION,
                  'hpos' => OrderUtil::custom_orders_table_usage_is_enabled()],
    'margin_fixture_only' => 7, 'amount_fixture_only' => '10.00',
    'checks' => $checks, 'scenarios' => $scenarios, 'failed' => $failed, 'error' => $error,
    'execution' => 'owned future AS actions invoked explicitly; scheduled instants verified; local confirmations at real execution time; no clock or gateway',
], JSON_UNESCAPED_UNICODE) . "\n";
