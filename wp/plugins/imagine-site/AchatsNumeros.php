<?php

declare(strict_types=1);

namespace Imagine\Site;

use DateTimeImmutable;
use DateTimeZone;

/** Raccord CRUD Woo, sans table miroir ni rapprochement par adresse email. */
final class AchatsNumeros
{
    public const PRODUIT = 'imagine_achat_numero_id';
    public const LIGNE = '_imagine_achat_numero_id';
    public const REMBOURSEMENT = 'imagine_achat_remboursement';

    public static function reglages(): void
    {
        register_setting('imagine_achats', self::REMBOURSEMENT, [
            'type' => 'string',
            'sanitize_callback' => static fn ($value): string => $value === 'ligne' ? 'ligne' : 'commande',
        ]);
        add_settings_section(
            'imagine_achats',
            __('Achats de numéros', 'imagine-site'),
            '__return_false',
            'imagine-achats'
        );
        add_settings_field(
            self::REMBOURSEMENT,
            __('Portée des remboursements', 'imagine-site'),
            static function (): void {
                echo '<select name="' . esc_attr(self::REMBOURSEMENT) . '">';
                $labels = ['commande' => __('Toute la commande (défaut prudent)', 'imagine-site'),
                    'ligne' => __('Seulement les lignes remboursées', 'imagine-site')];
                foreach ($labels as $value => $label) {
                    echo '<option value="' . esc_attr($value) . '" '
                        . selected(get_option(self::REMBOURSEMENT, 'commande'), $value, false)
                        . '>' . esc_html($label) . '</option>';
                }
                echo '</select><p>' . esc_html__(
                    'À confirmer par Imagine. Par ligne : un partiel non ventilé ne retire aucun numéro ; '
                    . 'un remboursement complet ferme toujours tout.',
                    'imagine-site'
                ) . '</p>';
            },
            'imagine-achats',
            'imagine_achats'
        );
    }

    public static function ecran(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Accès refusé.', 'imagine-site'));
        }
        echo '<div class="wrap"><h1>' . esc_html__('Achats de numéros', 'imagine-site')
            . '</h1><form method="post" action="options.php">';
        settings_fields('imagine_achats');
        do_settings_sections('imagine-achats');
        submit_button();
        echo '</form></div>';
    }

    private static function identifiant(mixed $value): int
    {
        return (is_int($value) || is_string($value))
            && preg_match('/\A[1-9][0-9]*\z/D', (string) $value)
            && (string) (int) $value === (string) $value ? (int) $value : 0;
    }

    public static function numero($product): int
    {
        if (
            !$product instanceof \WC_Product || !$product->is_type('simple')
            || $product->get_status() === 'trash'
        ) {
            return 0;
        }
        $id = self::identifiant($product->get_meta(self::PRODUIT, true, 'edit'));
        $issue = $id ? get_post($id) : null;
        return $issue && $issue->post_type === 'imagine_numero' && $issue->post_status === 'publish' ? $id : 0;
    }

    /** Figé seulement à la création. Zéro interdit le rétro-octroi d'un ancien produit. */
    public static function instantane($item): void
    {
        if ($item instanceof \WC_Order_Item_Product && !$item->get_id() && !$item->meta_exists(self::LIGNE)) {
            $item->add_meta_data(self::LIGNE, self::numero($item->get_product()), true);
        }
    }

    public static function droits(int $client): array
    {
        if ($client <= 0 || !function_exists('wc_get_orders')) {
            return [];
        }
        $rights = [];
        $page = 1;
        do {
            $result = wc_get_orders(['type' => 'shop_order', 'customer_id' => $client,
                'status' => ['wc-processing', 'wc-completed'], 'limit' => 50,
                'paged' => $page++, 'paginate' => true, 'return' => 'objects', 'orderby' => 'ID', 'order' => 'ASC']);
            if (!is_object($result) || !isset($result->orders, $result->max_num_pages)) {
                throw new \RuntimeException('Lecture des achats indisponible.');
            }
            foreach ($result->orders as $order) {
                if (
                    !$order instanceof \WC_Order || $order->get_type() !== 'shop_order'
                    || (int) $order->get_customer_id() !== $client
                ) {
                    throw new \RuntimeException('Propriétaire de commande incohérent.');
                }
                $paid = $order->get_date_paid('edit');
                $acquired = $paid
                    ? (new DateTimeImmutable('@' . $paid->getTimestamp()))->setTimezone(new DateTimeZone('UTC'))
                    : null;
                $refunds = wc_get_orders(['type' => 'shop_order_refund', 'parent' => $order->get_id(),
                    'limit' => -1, 'return' => 'objects']);
                $refundedLines = [];
                $amount = 0.0;
                foreach ($refunds as $refund) {
                    if (!$refund instanceof \WC_Order_Refund || $refund->get_parent_id() !== $order->get_id()) {
                        throw new \RuntimeException('Remboursement natif incohérent.');
                    }
                    $amount += (float) $refund->get_amount();
                    foreach ($refund->get_items('line_item') as $refundedItem) {
                        $lineId = self::identifiant($refundedItem->get_meta('_refunded_item_id', true, 'edit'));
                        if ($lineId > 0) {
                            $refundedLines[$lineId] = true;
                        }
                    }
                }
                $complete = $refunds !== [] && (float) $order->get_total() > 0
                    && $amount >= (float) $order->get_total();
                foreach ($order->get_items('line_item') as $item) {
                    $snapshot = self::identifiant($item->get_meta(self::LIGNE, true, 'edit'));
                    // C28 : la même ligne commerciale peut porter plusieurs instantanés.
                    foreach (apply_filters('imagine_achat_instantanes', [$snapshot], $item) as $snapshot) {
                        $snapshot = self::identifiant($snapshot);
                        $issue = $snapshot ? get_post($snapshot) : null;
                        $right = AchatNumero::droit($client, [
                            'client' => (int) $order->get_customer_id(), 'etat' => $order->get_status('edit'),
                            'payee' => $order->is_paid(), 'acquis' => $acquired,
                            'remboursement' => AchatNumero::remboursement(
                                get_option(self::REMBOURSEMENT, 'commande'),
                                $refunds !== [],
                                $complete,
                                isset($refundedLines[$item->get_id()])
                            ),
                            'instantane' => $snapshot,
                            'publie' => $issue && $issue->post_type === 'imagine_numero'
                                && $issue->post_status === 'publish',
                            'quantite' => $item->get_quantity(),
                        ]);
                        if ($right !== null) {
                            $rights[] = $right;
                        }
                    }
                }
            }
        } while ($page <= (int) $result->max_num_pages);
        return $rights;
    }

    public static function champ(): void
    {
        global $product_object;
        $options = ['0' => __('Aucun accès au numéro', 'imagine-site')];
        $issues = get_posts(['post_type' => 'imagine_numero', 'post_status' => 'publish',
            'numberposts' => -1, 'orderby' => 'ID', 'order' => 'DESC']);
        foreach ($issues as $issue) {
            $options[(string) $issue->ID] = $issue->post_title . ' (#' . $issue->ID . ')';
        }
        woocommerce_wp_select(['id' => self::PRODUIT, 'label' => __('Numéro à l’unité', 'imagine-site'),
            'value' => $product_object ? $product_object->get_meta(self::PRODUIT, true, 'edit') : '0',
            'options' => $options, 'wrapper_class' => 'show_if_simple',
            'description' => __('Modèle provisoire : un seul numéro, articles et PDF.', 'imagine-site') . ' '
                . __('Réaffecter ou vider : seuls les achats suivants changent.', 'imagine-site')]);
    }

    public static function enregistrer($product): void
    {
        // Le nonce et la capacité natifs Woo sont vérifiés avant ce hook ; défense explicite.
        if (!current_user_can('edit_post', $product->get_id()) || !isset($_POST[self::PRODUIT])) {
            return;
        }
        $id = self::identifiant(wp_unslash($_POST[self::PRODUIT]));
        $issue = $id ? get_post($id) : null;
        if (
            $product->is_type('simple') && $issue && $issue->post_type === 'imagine_numero'
            && $issue->post_status === 'publish'
        ) {
            $product->update_meta_data(self::PRODUIT, $id);
            // C28 : déliement symétrique, y compris formulaire programmatique partiel.
            $product->delete_meta_data('imagine_pack_numeros');
        } else {
            $product->delete_meta_data(self::PRODUIT);
        }
    }

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'reglages']);
        add_action('admin_menu', static function (): void {
            add_options_page(
                __('Achats de numéros', 'imagine-site'),
                __('Achats de numéros', 'imagine-site'),
                'manage_options',
                'imagine-achats',
                [self::class, 'ecran']
            );
        });
        add_action('woocommerce_before_order_item_object_save', [self::class, 'instantane'], 10, 1);
        add_action('woocommerce_product_options_general_product_data', [self::class, 'champ']);
        add_action('woocommerce_admin_process_product_object', [self::class, 'enregistrer']);
        add_filter('woocommerce_hidden_order_itemmeta', static function (array $keys): array {
            $keys[] = self::LIGNE;
            return $keys;
        });
    }
}
