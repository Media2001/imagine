<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Une liste éditoriale et un instantané de ligne Woo ; C14 décide seul des droits. */
final class PacksThematiques
{
    public const PRODUIT = 'imagine_pack_numeros';
    public const CANDIDAT = '_imagine_pack_candidat';
    public const LIGNE = '_imagine_pack_paye';

    public static function numeros($product): array
    {
        if (!$product instanceof \WC_Product || !$product->is_type('simple')
            || $product->get_status() !== 'publish') {
            return [];
        }
        $ids = PacksRegles::numeros($product->get_meta(self::PRODUIT, true, 'edit'));
        if ($ids === null) {
            return [];
        }
        foreach ($ids as $id) {
            $post = get_post($id);
            if (!$post || $post->post_type !== 'imagine_numero' || $post->post_status !== 'publish') {
                return [];
            }
        }
        return $ids;
    }

    /** Marque l'éligibilité, PAS la liste du panier ; aucune reprise des anciennes lignes. */
    public static function candidat($item): void
    {
        if ($item instanceof \WC_Order_Item_Product && !$item->get_id()
            && !$item->meta_exists(self::CANDIDAT)) {
            $product = $item->get_product();
            $item->add_meta_data(self::CANDIDAT, $product instanceof \WC_Product
                && $product->is_type('simple') && $product->meta_exists(self::PRODUIT) ? 1 : 0, true);
        }
    }

    public const ANOMALIE = 'imagine_pack_anomalie';
    private static ?\WeakMap $captures = null;

    public static function achetable(bool $allowed, $product): bool
    {
        return $allowed && !($product instanceof \WC_Product
            && $product->meta_exists(self::PRODUIT) && self::numeros($product) === []);
    }

    public static function ajouter(bool $allowed, $productId): bool
    {
        if (!self::achetable(true, wc_get_product($productId))) {
            wc_add_notice(__('Pack indisponible : un numéro inclus n’est plus disponible.', 'imagine-site'), 'error');
            return false;
        }
        return $allowed;
    }

    public static function panier(): void
    {
        if (!WC()->cart) {
            return;
        }
        foreach (WC()->cart->get_cart() as $line) {
            // Relecture, pas l'objet éventuellement mémorisé dans la session panier.
            self::ajouter(true, $line['product_id']);
        }
    }

    /** Prépare seulement la transition non payé -> payé, jamais une reprise tardive. */
    public static function preparer($order): void
    {
        if (!$order instanceof \WC_Order || $order->get_type() !== 'shop_order') {
            return;
        }
        self::$captures ??= new \WeakMap();
        unset(self::$captures[$order]);
        if (!$order->is_paid() || !$order->get_date_paid('edit')) {
            return;
        }
        $persisted = $order->get_id() ? new \WC_Order($order->get_id()) : null;
        if ($persisted && $persisted->get_date_paid('edit')) {
            return;
        }
        $captures = [];
        foreach ($order->get_items('line_item') as $item) {
            self::candidat($item);
            if ((string) $item->get_meta(self::CANDIDAT, true, 'edit') !== '1') {
                continue;
            }
            $ids = self::numeros(wc_get_product($item->get_product_id()));
            if ($ids === []) {
                throw new \RuntimeException(__('Paiement refusé : pack indisponible.', 'imagine-site'));
            }
            $captures[spl_object_id($item)] = ['numeros' => $ids,
                'paye_le' => $order->get_date_paid('edit')->getTimestamp(),
                'produit' => (int) $item->get_product_id()];
        }
        self::$captures[$order] = $captures;
    }

    /** Après persistance, consomme la capture éphémère ; ne lit jamais le produit. */
    public static function payer($order): void
    {
        if (!$order instanceof \WC_Order || $order->get_type() !== 'shop_order'
            || !$order->is_paid() || !$order->get_date_paid('edit')) {
            return;
        }
        $captures = self::$captures[$order] ?? [];
        if (self::$captures !== null) {
            unset(self::$captures[$order]);
        }
        foreach ($order->get_items('line_item') as $item) {
            if ((string) $item->get_meta(self::CANDIDAT, true, 'edit') !== '1') {
                continue;
            }
            if (!$item->meta_exists(self::LIGNE) && isset($captures[spl_object_id($item)])
                && !$item->meta_exists(self::ANOMALIE)) {
                $item->add_meta_data(self::LIGNE, $captures[spl_object_id($item)], true);
                $item->save();
            }
            $snapshot = $item->get_meta(self::LIGNE, true, 'edit');
            if ((PacksRegles::instantane($snapshot) === []
                || ((int) $item->get_product_id() > 0 && ($snapshot['produit'] ?? null) !== (int) $item->get_product_id())
                || ($snapshot['paye_le'] ?? null) !== $order->get_date_paid('edit')->getTimestamp())
                && !$item->meta_exists(self::ANOMALIE)) {
                // Visible dans la ligne d'administration ; aucune réparation automatique.
                $item->add_meta_data(self::ANOMALIE, __('Instantané du pack absent ou non fiable : accès fermé, vérification manuelle requise.', 'imagine-site'), true);
                $item->save();
            }
        }
    }

    /** Expansion d'une seule ligne commerciale AVANT la décision et le remboursement C14. */
    public static function instantanes(array $existing, $item): array
    {
        if (!$item instanceof \WC_Order_Item_Product
            || (string) $item->get_meta(self::CANDIDAT, true, 'edit') !== '1') {
            return $existing;
        }
        if ($item->meta_exists(self::ANOMALIE)) {
            return [];
        }
        $snapshot = $item->get_meta(self::LIGNE, true, 'edit');
        if ((int) $item->get_product_id() > 0 && ($snapshot['produit'] ?? null) !== (int) $item->get_product_id()) {
            return [];
        }
        $order = $item->get_order();
        if (!$order || !$order->get_date_paid('edit')
            || ($snapshot['paye_le'] ?? null) !== $order->get_date_paid('edit')->getTimestamp()) {
            return [];
        }
        return PacksRegles::instantane($item->get_meta(self::LIGNE, true, 'edit'));
    }

    public static function champ(): void
    {
        global $product_object;
        $selected = $product_object ? (PacksRegles::numeros($product_object->get_meta(self::PRODUIT, true, 'edit')) ?? []) : [];
        echo '<div class="options_group show_if_simple"><p class="form-field"><label for="imagine-pack-numeros">'
            . esc_html__('Pack : numéros inclus', 'imagine-site') . '</label>';
        echo '<input type="hidden" name="imagine_pack_present" value="1">';
        echo '<select id="imagine-pack-numeros" name="' . esc_attr(self::PRODUIT) . '[]" multiple size="6">';
        foreach (get_posts(['post_type' => 'imagine_numero', 'post_status' => 'publish',
            'numberposts' => -1, 'orderby' => 'ID', 'order' => 'ASC']) as $post) {
            echo '<option value="' . esc_attr((string) $post->ID) . '"'
                . selected(in_array($post->ID, $selected, true), true, false) . '>'
                . esc_html(get_the_title($post)) . '</option>';
        }
        echo '</select><span class="description">' . esc_html__(
            'Un prix pour le pack. Liste figée au paiement ; aucun changement pour les achats passés. Un numéro déjà possédé ne donne pas de remise.',
            'imagine-site'
        ) . '</span></p></div>';
    }

    public static function enregistrer($product): void
    {
        // Le formulaire natif Woo vérifie son nonce avant cet appel.
        if (!$product instanceof \WC_Product || !current_user_can('edit_post', $product->get_id())
            || !isset($_POST['imagine_pack_present'])) {
            return;
        }
        $ids = PacksRegles::numeros(wp_unslash($_POST[self::PRODUIT] ?? []));
        if ($ids === null) {
            \WC_Admin_Meta_Boxes::add_error(__('Pack refusé : liste de numéros invalide.', 'imagine-site'));
            return;
        }
        foreach ($ids as $id) {
            $post = get_post($id);
            if (!$post || $post->post_type !== 'imagine_numero' || $post->post_status !== 'publish') {
                \WC_Admin_Meta_Boxes::add_error(__('Pack refusé : numéro indisponible.', 'imagine-site'));
                return;
            }
        }
        if ($product->is_type('simple') && $ids !== []) {
            $product->update_meta_data(self::PRODUIT, $ids);
            $product->delete_meta_data(AchatsNumeros::PRODUIT);
        } else {
            $product->delete_meta_data(self::PRODUIT);
        }
    }

    public static function register(): void
    {
        add_action('woocommerce_before_order_item_object_save', [self::class, 'candidat']);
        add_filter('woocommerce_is_purchasable', [self::class, 'achetable'], 10, 2);
        add_filter('woocommerce_add_to_cart_validation', [self::class, 'ajouter'], 10, 2);
        add_action('woocommerce_check_cart_items', [self::class, 'panier']);
        add_action('woocommerce_before_order_object_save', [self::class, 'preparer']);
        add_action('woocommerce_after_order_object_save', [self::class, 'payer']);
        add_filter('imagine_achat_instantanes', [self::class, 'instantanes'], 10, 2);
        add_action('woocommerce_product_options_general_product_data', [self::class, 'champ']);
        add_action('woocommerce_admin_process_product_object', [self::class, 'enregistrer'], 20);
        add_filter('woocommerce_product_single_add_to_cart_text', static function (string $text, $product): string {
            return self::numeros($product) !== [] ? __('Acheter ce pack', 'imagine-site') : $text;
        }, 10, 2);
        add_filter('woocommerce_hidden_order_itemmeta', static function (array $keys): array {
            return [...$keys, self::CANDIDAT, self::LIGNE];
        });
    }
}
