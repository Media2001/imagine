<?php

declare(strict_types=1);

namespace Imagine\Site;

/** CRUD natif, démo uniquement ; aucun paiement ni adhésion créés. */
final class CommandeNative
{
    public const OWNED = '_imagine_c16_fixture';

    public static function garde(): void
    {
        if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo'
            || home_url() !== 'http://192.168.129.32:8085' || !function_exists('wcs_create_subscription')
            || !has_filter('pre_wp_mail') || !has_filter('pre_http_request')) {
            throw new \RuntimeException('Démonstration fictive hors ligne requise.');
        }
        if (apply_filters('pre_wp_mail', null, ['to' => 'temoin@example.org', 'headers' => []]) !== false
            || !is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
            || apply_filters('woocommerce_available_payment_gateways', []) !== []) {
            throw new \RuntimeException('Coupe-circuits requis.');
        }
    }

    public static function produits(): array
    {
        $ids = array_values(get_option('imagine_c09_fixture', [])['tariffs'] ?? []);
        $ids = array_merge($ids, get_posts(['post_type' => 'product', 'post_status' => 'publish',
            'posts_per_page' => -1, 'fields' => 'ids', 'meta_key' => AchatsNumeros::PRODUIT]));
        $out = [];
        foreach (array_unique($ids) as $id) {
            $p = wc_get_product($id);
            if ($p && in_array($p->get_status(), ['publish', 'private'], true)
                && ($p->is_type('subscription') || AchatsNumeros::numero($p) > 0)) {
                $out[$p->get_id()] = $p;
            }
        }
        return $out;
    }

    public static function empreinte(object $p): string
    {
        return hash('sha256', wp_json_encode([$p->get_id(), $p->get_price(), $p->get_status(), $p->get_type(),
            $p->get_meta('_subscription_period'), $p->get_meta('_subscription_period_interval'),
            $p->get_meta('_subscription_length'), AchatsNumeros::numero($p)]));
    }

    public static function recherche(string $query): array
    {
        if ($query === '') {
            return [];
        }
        $query = mb_strtolower($query);
        $found = [];
        // Petite démonstration : paginer plutôt qu'une limite silencieuse de résultats.
        for ($page = 1; ; $page++) {
            $users = get_users(['number' => 100, 'paged' => $page, 'orderby' => 'ID', 'order' => 'ASC']);
            foreach ($users as $user) {
                $text = implode(' ', [$user->display_name, $user->user_email, $user->user_login,
                    get_user_meta($user->ID, 'first_name', true), get_user_meta($user->ID, 'last_name', true),
                    get_user_meta($user->ID, 'billing_city', true), get_user_meta($user->ID, 'shipping_city', true)]);
                if (str_contains(mb_strtolower($text), $query)) {
                    $found[] = $user;
                }
            }
            if (count($users) < 100) {
                return $found;
            }
        }
    }

    public static function clientExistant(array $client): ?object
    {
        if ($client['mode'] === 'existant') {
            $user = get_userdata($client['id']);
            if (!$user) {
                throw new \InvalidArgumentException('Compte disparu.');
            }
            return $user;
        }
        if ($client['mode'] === 'direct') {
            $user = get_user_by('login', 'imagine-vente-directe');
            if ($user && get_user_meta($user->ID, self::OWNED, true) !== '1') {
                throw new \RuntimeException('Collision vente directe.');
            }
            return $user ?: null;
        }
        return $client['email'] !== '' ? (get_user_by('email', $client['email']) ?: null) : null;
    }

    private static function creerClient(array $client): object
    {
        $user = self::clientExistant($client);
        if ($user) {
            return $user; // Ni email, ni nom, ni adresse du compte existant modifiés.
        }
        $direct = $client['mode'] === 'direct';
        $suffix = str_replace('-', '', wp_generate_uuid4());
        $email = $direct ? 'vente-directe@sans-email.imagine.invalid'
            : ($client['sans_email'] ? $suffix . '@sans-email.imagine.invalid' : $client['email']);
        $id = wp_insert_user(['user_login' => $direct ? 'imagine-vente-directe' : 'imagine-c16-' . $suffix,
            'user_email' => $email, 'display_name' => $direct ? 'Vente directe — fictif' : $client['nom'],
            'user_pass' => wp_generate_password(48, true, true), 'role' => 'customer',
            'meta_input' => [self::OWNED => '1', SansEmail::META => ($direct || $client['sans_email']) ? '1' : '0']]);
        if (is_wp_error($id)) {
            throw new \RuntimeException('Compte non créé.');
        }
        return get_userdata($id);
    }

    /** Appel sous verrou de brouillon ; le verrou email protège deux référents. */
    public static function creer(array $draft): array
    {
        self::garde();
        $products = self::produits();
        $p = $products[$draft['commande']['produit']] ?? null;
        if (!$p || self::empreinte($p) !== $draft['empreinte']) {
            throw new \RuntimeException('Catalogue modifié : recommencer la confirmation.');
        }
        global $wpdb;
        $client = $draft['client'];
        $identity = $client['mode'] === 'direct' ? 'vente-directe'
            : ($client['mode'] === 'existant' ? 'id:' . $client['id'] : ($client['email'] ?: $draft['token']));
        $lock = 'imagine_c16_email_' . substr(hash('sha256', DB_NAME . ':' . $wpdb->prefix . ':' . $identity), 0, 40);
        if ((string) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 5)', $lock)) !== '1') {
            throw new \RuntimeException('Client en cours de traitement.');
        }
        try {
            $user = self::creerClient($client);
            $order = wc_create_order(['customer_id' => $user->ID, 'status' => 'pending', 'created_via' => 'imagine-c16']);
            if (is_wp_error($order)) {
                throw new \RuntimeException('Commande non créée.');
            }
            self::remplir($order, $user, $draft['commande']);
            $order->add_product($p, 1);
            $order->calculate_totals(false);
            $order->save();
            $sid = null;
            if ($p->is_type('subscription')) {
                $start = gmdate('Y-m-d H:i:s');
                $sub = wcs_create_subscription(['order_id' => $order->get_id(), 'customer_id' => $user->ID,
                    'status' => 'pending', 'start_date' => $start,
                    'billing_period' => \WC_Subscriptions_Product::get_period($p),
                    'billing_interval' => \WC_Subscriptions_Product::get_interval($p)]);
                if (is_wp_error($sub)) {
                    throw new \RuntimeException('Souscription non créée : relire la commande.');
                }
                self::remplir($sub, $user, $draft['commande']);
                $sub->set_requires_manual_renewal(true);
                $sub->add_product($p, 1);
                $sub->calculate_totals(false);
                $end = \WC_Subscriptions_Product::get_expiration_date($p, $start);
                if ($end) {
                    $sub->update_dates(['end' => $end], 'gmt');
                }
                $sub->save();
                $sid = $sub->get_id();
            }
            $order->add_order_note(sprintf(__('C16 — Commande fictive en attente, encodée par %s (#%d), le %s UTC. Aucun paiement validé.', 'imagine-site'),
                wp_get_current_user()->user_login, get_current_user_id(), gmdate('Y-m-d H:i:s')), false, true);
            return ['commande' => $order->get_id(), 'souscription' => $sid, 'client' => $user->ID];
        } finally {
            $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
        }
    }

    private static function remplir(object $object, object $user, array $data): void
    {
        $object->set_created_via('imagine-c16');
        $object->update_meta_data(self::OWNED, '1');
        $object->update_meta_data('imagine_demo_fictif', '1');
        $object->set_address($data['adresse'], 'shipping');
        $object->set_address($data['adresse'] + ['email' => $user->user_email], 'billing');
        $object->set_currency(get_woocommerce_currency());
        $object->set_payment_method($data['paiement']); // Descripteur seulement, jamais process_payment().
        $object->set_payment_method_title($data['paiement'] === 'bacs' ? __('Virement', 'imagine-site') : __('Mandat papier', 'imagine-site'));
        $object->set_transaction_id('');
        $object->set_date_paid(null);
        $object->set_date_completed(null);
        $object->set_status('pending');
        $object->save();
    }
}
