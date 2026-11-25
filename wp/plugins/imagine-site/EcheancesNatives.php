<?php

declare(strict_types=1);

namespace Imagine\Site;

/** CRUD Woo/WCS uniquement : pas de registre de paiements ni d'IBAN lu. */
final class EcheancesNatives
{
    /** C09 laisse les passerelles vides : ces deux identifiants NATIFS ne sont
     * interprétés que sur cette démonstration locale explicitement fictive.
     * En dehors d'elle, une méthode absente reste inconnue et ne permet rien.
     */
    public static function fictif(object $object, string $key): bool
    {
        if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo'
            || home_url() !== 'http://192.168.129.32:8085' || $object->get_meta('imagine_demo_fictif') !== '1'
            || $object->get_meta('_imagine_c09_fixture') !== $key) {
            return false;
        }
        $fixture = get_option('imagine_c09_fixture', []);
        return (int) ($fixture['users'][$key] ?? 0) === (int) $object->get_customer_id()
            && in_array($object->get_id(), [$fixture['orders'][$key] ?? 0, $fixture['subscriptions'][$key] ?? 0], true);
    }

    public static function methode(object $object): string
    {
        $method = (string) $object->get_payment_method();
        if ($method !== '') {
            return $method;
        }
        return self::fictif($object, 'A-VIR') ? 'bacs'
            : (self::fictif($object, 'A-PAPIER') ? 'imagine_papier' : '');
    }

    public static function commande(object $order): array
    {
        return ['id' => $order->get_id(), 'abonne' => trim($order->get_billing_first_name() . ' ' . $order->get_billing_last_name()),
            'montant' => $order->get_total(), 'devise' => $order->get_currency(), 'etat' => $order->get_status(),
            'methode' => self::methode($order), 'paye' => $order->is_paid(),
            'date_payee' => $order->get_date_paid()?->getTimestamp() ?? 0,
            'creation' => $order->get_date_created()?->getTimestamp() ?? 0];
    }

    public static function virement(int $id): object
    {
        $order = wc_get_order($id);
        if (!$order || $order->get_type() !== 'shop_order' || $order->get_refunds() !== []
            || EcheancesRegles::paiements([self::commande($order)], 'virements') === []) {
            throw new \LogicException('Virement natif impayé requis.');
        }
        $related = wcs_get_subscriptions_for_order($id, ['order_type' => ['parent', 'renewal']]);
        if (!array_filter($related, static fn ($sub) => (int) $sub->get_customer_id() === (int) $order->get_customer_id())) {
            throw new \LogicException('Propriétaire incohérent.');
        }
        return $order;
    }

    public static function lire(string $view, int $days): array
    {
        if (!function_exists('wc_get_orders') || !function_exists('wcs_get_subscriptions')) {
            throw new \RuntimeException('WooCommerce Subscriptions indisponible.');
        }
        if (!in_array($days, [30, 90, 180], true)) {
            throw new \InvalidArgumentException('Période invalide.');
        }
        $rows = [];
        if (in_array($view, ['attente', 'virements', 'echecs'], true)) {
            // Pagination, aucune limite silencieuse. Relations et paiement natifs.
            for ($page = 1; ; $page++) {
                $orders = wc_get_orders(['type' => 'shop_order', 'status' => ['pending', 'on-hold', 'failed'],
                    'limit' => 100, 'page' => $page, 'orderby' => 'ID', 'order' => 'ASC']);
                foreach ($orders as $order) {
                    $related = wcs_get_subscriptions_for_order($order->get_id(), ['order_type' => ['parent', 'renewal']]);
                    $sameOwner = array_filter($related, static fn ($sub) => (int) $sub->get_customer_id() === (int) $order->get_customer_id());
                    if ($sameOwner !== []) {
                        $rows[] = self::commande($order);
                    }
                }
                if (count($orders) < 100) {
                    break;
                }
            }
            return EcheancesRegles::paiements($rows, $view);
        }
        if (!in_array($view, ['echeances', 'mandats'], true)) {
            throw new \InvalidArgumentException('Vue invalide.');
        }
        for ($page = 1; ; $page++) {
            $subs = wcs_get_subscriptions(['subscriptions_per_page' => 100, 'paged' => $page,
                'subscription_status' => ['active', 'pending-cancel', 'on-hold', 'pending'], 'orderby' => 'ID', 'order' => 'ASC']);
            foreach ($subs as $sub) {
                $reference = self::fictif($sub, 'A-PAPIER') ? 'A-PAPIER' : (string) $sub->get_meta('imagine_mandat_reference');
                $renewals = [];
                if ($view === 'mandats' && self::methode($sub) === 'imagine_papier') {
                    foreach ($sub->get_related_orders('all', 'renewal') as $order) {
                        // Relation WCS + même propriétaire, jamais une commande parent
                        // ni une passerelle explicitement différente du mandat papier.
                        if ($order->get_type() === 'shop_order' && $order->get_refunds() === []
                            && (int) $order->get_customer_id() === (int) $sub->get_customer_id()
                            && in_array((string) $order->get_payment_method(), ['', 'imagine_papier'], true)) {
                            $renewals[] = self::commande($order);
                        }
                    }
                }
                $rows[] = ['id' => $sub->get_id(), 'type' => 'souscription', 'renouvellements' => $renewals, 'abonne' => trim($sub->get_billing_first_name() . ' ' . $sub->get_billing_last_name()),
                    'etat' => $sub->get_status(), 'prochaine' => (int) $sub->get_time('next_payment'), 'fin' => (int) $sub->get_time('end'),
                    'methode' => self::methode($sub), 'montant' => $sub->get_total(), 'devise' => $sub->get_currency(), 'reference' => $reference];
            }
            if (count($subs) < 100) {
                break;
            }
        }
        return $view === 'mandats' ? EcheancesRegles::mandats($rows, time(), $days) : EcheancesRegles::echeances($rows, time(), $days);
    }
}
