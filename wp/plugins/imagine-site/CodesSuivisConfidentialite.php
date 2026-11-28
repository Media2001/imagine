<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Déclaration additive C21 ; candidats et conversions, sans source du compte. */
final class CodesSuivisConfidentialite
{
    public static function register(): void
    {
        add_filter('wp_privacy_personal_data_exporters', static function (array $items): array {
            $items['imagine-codes-suivis'] = ['exporter_friendly_name' => __('Codes suivis', 'imagine-site'), 'callback' => [self::class, 'exporter']];
            return $items;
        }, 170);
        add_filter('wp_privacy_personal_data_erasers', static function (array $items): array {
            $items['imagine-codes-suivis'] = ['eraser_friendly_name' => __('Codes suivis', 'imagine-site'), 'callback' => [self::class, 'effacer']];
            return $items;
        }, 170);
    }

    private static function commandes(string $email, int $page): array
    {
        if (!is_email($email)) {
            return [];
        }
        $user = get_user_by('email', $email);
        // Deux flux natifs disjoints ; leur union est ordonnée avant pagination.
        // Ne pas filtrer par méta : son effacement ne doit pas déplacer la page suivante.
        $selectors = [['customer_id' => 0, 'billing_email' => $email]];
        if ($user) {
            $selectors[] = ['customer_id' => (int) $user->ID];
        }
        global $wpdb;
        $ids = [];
        $page = max(1, $page);
        foreach ($selectors as $selector) {
            for ($part = 1; $part <= $page; $part++) {
                $wpdb->last_error = '';
                $batch = wc_get_orders($selector + ['type' => 'shop_order', 'return' => 'ids',
                    'limit' => 50, 'page' => $part, 'orderby' => 'ID', 'order' => 'ASC']);
                if ($wpdb->last_error !== '' || !is_array($batch)) {
                    throw new \RuntimeException('Lecture impossible');
                }
                foreach ($batch as $id) { $ids[(int) $id] = (int) $id; }
                if (count($batch) < 50) { break; }
            }
        }
        ksort($ids, SORT_NUMERIC);
        $orders = [];
        foreach (array_slice(array_values($ids), ($page - 1) * 50, 50) as $id) {
            $order = wc_get_order($id);
            if (!$order) { throw new \RuntimeException('Commande illisible'); }
            $orders[] = $order;
        }
        return $orders;
    }

    public static function exporter(string $email, int $page = 1): array|\WP_Error
    {
        try {
            $orders = self::commandes($email, $page);
            $data = [];
            foreach ($orders as $order) {
                foreach ([CodesSuivis::META, CodesSuivis::CANDIDAT] as $key) {
                    $value = $order->get_meta($key);
                    if (CodesSuivisRegles::instantane($value)) {
                        $data[] = ['group_id' => 'imagine-codes-suivis', 'group_label' => __('Codes suivis', 'imagine-site'),
                            'item_id' => 'imagine-c30-' . $order->get_id() . $key,
                            'data' => [['name' => __('Code', 'imagine-site'), 'value' => $value['code']],
                                ['name' => __('Libellé', 'imagine-site'), 'value' => $value['libelle']]]];
                    }
                }
            }
            return ['data' => $data, 'done' => count($orders) < 50];
        } catch (\Throwable) {
            return new \WP_Error('imagine_c30_export', __('Export incomplet.', 'imagine-site'));
        }
    }

    public static function effacer(string $email, int $page = 1): array
    {
        $result = ['items_removed' => false, 'items_retained' => false, 'messages' => [], 'done' => false];
        try {
            $orders = self::commandes($email, $page);
            foreach ($orders as $order) {
                global $wpdb;
                $lock = CodesSuivis::verrou($order->get_id());
                if ((int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 3)', $lock)) !== 1) {
                    throw new \RuntimeException('Verrou indisponible');
                }
                try {
                    $order = wc_get_order($order->get_id());
                    if ($order->meta_exists(CodesSuivis::META) || $order->meta_exists(CodesSuivis::CANDIDAT)) {
                        $order->delete_meta_data(CodesSuivis::META);
                        $order->delete_meta_data(CodesSuivis::CANDIDAT);
                        $order->update_meta_data(CodesSuivis::SCELLE, '1');
                        $order->save_meta_data();
                        $read = wc_get_order($order->get_id());
                        if ($read->meta_exists(CodesSuivis::META) || $read->meta_exists(CodesSuivis::CANDIDAT)) {
                            throw new \RuntimeException('Effacement non persisté');
                        }
                        $result['items_removed'] = true;
                    }
                } finally {
                    $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
                }
            }
            $result['done'] = count($orders) < 50;
        } catch (\Throwable) {
            $result['items_retained'] = true;
            $result['messages'][] = __('Effacement incomplet.', 'imagine-site');
        }
        return $result;
    }
}
