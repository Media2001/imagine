<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Attribution locale : aucune remise, aucun droit et aucun transport. */
final class CodesSuivis
{
    public const OPTION = 'imagine_codes_suivis';
    public const SESSION = 'imagine_code_suivi';
    public const CANDIDAT = '_imagine_code_suivi_candidat';
    public const META = '_imagine_code_suivi';
    public const SCELLE = '_imagine_code_suivi_scelle';

    public static function register(): void
    {
        add_shortcode('imagine_bienvenue', static fn (): string => '<p><a href="'
            . esc_url(Navigation::abonnementUrl()) . '">' . esc_html__('S’abonner', 'imagine-site') . '</a></p>');
        add_action('template_redirect', static function (): void {
            if (!is_page('bienvenue') || ($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'GET') {
                return;
            }
            nocache_headers();
            if (isset($_GET['code']) && is_string($_GET['code'])) {
                self::retenir(wp_unslash($_GET['code']));
            }
        });
        add_action('woocommerce_checkout_create_order', [self::class, 'candidat'], 20, 2);
        add_action('woocommerce_payment_complete', [self::class, 'payer'], 30);
        add_action('woocommerce_order_status_changed', static fn (int $id) => self::payer($id), 30);
    }

    public static function configuration(): array
    {
        return CodesSuivisRegles::liste(get_option(self::OPTION, [])) ?? [];
    }

    public static function retenir(mixed $code): void
    {
        $valid = CodesSuivisRegles::retenir($code, self::configuration());
        if ($valid === null || !function_exists('WC')) {
            return;
        }
        if (!WC()->session) {
            WC()->initialize_session();
        }
        WC()->session->set(self::SESSION, $valid);
        WC()->session->set_customer_session_cookie(true);
    }

    public static function candidat(\WC_Order $order, array $data): void
    {
        if ($order->get_created_via() !== 'checkout' || $order->meta_exists(self::SCELLE) || $order->meta_exists(self::CANDIDAT)) {
            return;
        }
        $session = function_exists('WC') && WC()->session ? WC()->session->get(self::SESSION) : null;
        if (!CodesSuivisRegles::instantane($session)) {
            return;
        }
        // Revalidation de la liste au moment de la commande. Le code imprimé
        // n'est pas une entrée de prix ; le candidat n'est pas une conversion.
        $valid = CodesSuivisRegles::retenir($session['code'], self::configuration());
        if ($valid !== null) {
            $order->update_meta_data(self::CANDIDAT, $valid);
        }
    }

    public static function verrou(int $id): string
    {
        global $wpdb;
        return 'imagine_c30_' . substr(hash('sha256', DB_NAME . ':' . $wpdb->prefix . ':' . $id), 0, 40);
    }

    public static function payer(int $id): void
    {
        global $wpdb;
        $lock = self::verrou($id);
        if ((int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 3)', $lock)) !== 1) {
            return;
        }
        try {
            $order = wc_get_order($id);
            if (
                !$order || $order->get_type() !== 'shop_order' || $order->get_created_via() !== 'checkout'
                || !$order->is_paid() || !$order->get_date_paid() || $order->meta_exists(self::SCELLE)
            ) {
                return;
            }
            $value = $order->get_meta(self::CANDIDAT);
            if (!CodesSuivisRegles::instantane($value)) {
                return;
            }
            $order->update_meta_data(self::META, $value);
            $order->update_meta_data(self::SCELLE, '1');
            $order->delete_meta_data(self::CANDIDAT);
            $order->save_meta_data();
            $read = wc_get_order($id);
            if ($read->get_meta(self::META) !== $value || $read->get_meta(self::SCELLE) !== '1') {
                throw new \RuntimeException('Attribution non persistée.');
            }
        } finally {
            $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
        }
    }

    public static function compter(string $du, string $au): array|\WP_Error
    {
        foreach ([$du, $au] as $date) {
            $parsed = \DateTimeImmutable::createFromFormat('!Y-m-d', $date, new \DateTimeZone('UTC'));
            if (!$parsed || $parsed->format('Y-m-d') !== $date) {
                return new \WP_Error('imagine_c30_dates', __('Période invalide.', 'imagine-site'));
            }
        }
        if ($du > $au) {
            return new \WP_Error('imagine_c30_dates', __('Période invalide.', 'imagine-site'));
        }
        $counts = [];
        try {
            for ($page = 1; ; $page++) {
                $orders = wc_get_orders(['type' => 'shop_order', 'status' => ['processing', 'completed'], 'limit' => 50, 'page' => $page, 'orderby' => 'ID', 'order' => 'ASC']);
                foreach ($orders as $order) {
                    $date = $order->get_date_paid();
                    $value = $order->get_meta(self::META);
                    $day = $date ? gmdate('Y-m-d', $date->getTimestamp()) : '';
                    if ($order->is_paid() && $day >= $du && $day <= $au && CodesSuivisRegles::instantane($value)) {
                        $counts[$value['code']] = ($counts[$value['code']] ?? 0) + 1;
                    }
                }
                if (count($orders) < 50) {
                    break;
                }
            }
        } catch (\Throwable) {
            return new \WP_Error('imagine_c30_lecture', __('Lecture impossible.', 'imagine-site'));
        }
        ksort($counts);
        return $counts;
    }
}
