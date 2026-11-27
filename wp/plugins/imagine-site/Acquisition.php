<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Déclarations locales indexées par commande, hors des charges utiles Woo/Odoo/newsletter. */
final class Acquisition
{
    public const OPTION = 'imagine_acquisition_choix';
    public const REPONSE = 'imagine_acquisition_reponse_';
    public const VUE = 'imagine_acquisition_vue_';
    public const SOURCE = 'imagine_source_acquisition';

    public static function register(): void
    {
        add_action('woocommerce_thankyou', [self::class, 'question'], 30);
        add_action('admin_post_imagine_acquisition', [self::class, 'recevoir']);
        add_action('admin_post_nopriv_imagine_acquisition', [self::class, 'recevoir']);
    }

    public static function configuration(): array
    {
        return AcquisitionRegles::liste(get_option(self::OPTION, [])) ?? [];
    }

    public static function eligible(mixed $order, int $actor): bool
    {
        return $order instanceof \WC_Order && $order->get_type() === 'shop_order'
            && AcquisitionRegles::eligible(
                $actor,
                (int) $order->get_customer_id(),
                $order->is_paid(),
                $order->get_date_paid() !== null,
                $order->get_created_via()
            );
    }

    public static function question(int $id): void
    {
        $order = wc_get_order($id);
        $choices = self::configuration();
        $key = $_GET['key'] ?? null;
        if (
            !is_order_received_page() || !self::eligible($order, get_current_user_id()) || !$choices
            || !is_string($key) || !hash_equals($order->get_order_key(), wp_unslash($key))
            || get_option(self::REPONSE . $id, null) !== null
        ) {
            return;
        }
        // Une seule proposition, même sans réponse : aucun rappel, popup, cookie ni script.
        $seen = ['commande' => $id, 'compte' => get_current_user_id(), 'date' => gmdate('Y-m-d\TH:i:s\Z')];
        if (!add_option(self::VUE . $id, $seen, '', false)) {
            return;
        }
        nocache_headers();
        echo '<section id="imagine-acquisition"><h2>' . esc_html__('Comment nous avez-vous connus ?', 'imagine-site') . '</h2><p>'
            . esc_html__('Facultatif. Votre commande est confirmée, sans réponse obligatoire. Aucun rappel.', 'imagine-site') . '</p>'
            . '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">'
            . '<input type="hidden" name="action" value="imagine_acquisition">'
            . '<input type="hidden" name="commande" value="' . $id . '">';
        wp_nonce_field('imagine_acquisition:' . $id, '_c27', false);
        echo '<p><label for="imagine-acquisition-choix">' . esc_html__('Votre réponse (facultative)', 'imagine-site')
            . '</label><br><select id="imagine-acquisition-choix" name="choix"><option value="">'
            . esc_html__('Je préfère ne pas répondre', 'imagine-site') . '</option>';
        foreach ($choices as $value => $label) {
            echo '<option value="' . esc_attr($value) . '">' . esc_html($label) . '</option>';
        }
        echo '</select></p><p><button type="submit">' . esc_html__('Enregistrer ma réponse', 'imagine-site') . '</button> '
            . '<a href="' . esc_url(wc_get_page_permalink('myaccount')) . '">' . esc_html__('Continuer sans répondre', 'imagine-site')
            . '</a></p></form></section>';
    }

    public static function recevoir(): void
    {
        $id = $_POST['commande'] ?? null;
        $choice = $_POST['choix'] ?? null;
        $nonce = $_POST['_c27'] ?? null;
        if (
            ($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST' || !is_string($id) || !preg_match('/^[1-9][0-9]*$/D', $id)
            || !is_string($choice) || !is_string($nonce)
            || !wp_verify_nonce(wp_unslash($nonce), 'imagine_acquisition:' . $id)
            || !self::eligible(wc_get_order((int) $id), get_current_user_id())
        ) {
            wp_die(esc_html__('Réponse refusée.', 'imagine-site'), '', ['response' => 403]);
        }
        if ($choice !== '' && is_wp_error(self::repondre((int) $id, get_current_user_id(), wp_unslash($choice)))) {
            wp_die(esc_html__('Réponse refusée ou déjà enregistrée.', 'imagine-site'), '', ['response' => 403]);
        }
        wp_safe_redirect(wc_get_page_permalink('myaccount'));
        exit;
    }

    /** L'unicité SQL de l'option ferme aussi deux requêtes concurrentes. Aucune édition exposée. */
    public static function repondre(int $id, int $actor, string $choice): bool|\WP_Error
    {
        if (!self::eligible(wc_get_order($id), $actor)) {
            return new \WP_Error('imagine_acquisition_refuse');
        }
        global $wpdb;
        $lock = 'imagine_c27_' . substr(hash('sha256', DB_NAME . ':' . $wpdb->prefix . ':' . $actor), 0, 40);
        if ((int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 3)', $lock)) !== 1) {
            return new \WP_Error('imagine_acquisition_occupee');
        }
        $key = self::REPONSE . $id;
        try {
            wp_cache_delete($key, 'options');
            wp_cache_delete(self::VUE . $id, 'options');
            wp_cache_delete('notoptions', 'options');
            wp_cache_delete($actor, 'user_meta');
            $choices = self::configuration();
            $wpdb->last_error = '';
            $seen = get_option(self::VUE . $id, null);
            if ($wpdb->last_error !== '' || (is_array($seen) && ($seen['etat'] ?? '') === 'effacee')) {
                return new \WP_Error('imagine_acquisition_refuse');
            }
            if (!self::eligible(wc_get_order($id), $actor) || !isset($choices[$choice]) || get_option($key, null) !== null) {
                return new \WP_Error('imagine_acquisition_refuse');
            }
            if ($wpdb->query('START TRANSACTION') === false) {
                throw new \RuntimeException('Transaction indisponible');
            }
            $record = ['commande' => $id, 'compte' => $actor, 'date' => gmdate('Y-m-d\TH:i:s\Z'),
                'choix' => $choice, 'libelle' => $choices[$choice]];
            if (!add_option($key, $record, '', false) || get_option($key) !== $record) {
                throw new \RuntimeException('Réponse non enregistrée');
            }
            $source = self::sourceFiable($actor);
            if (is_wp_error($source)) {
                throw new \RuntimeException('Lecture de la source impossible');
            }
            // Une ligne existante, même vide, n'est jamais remplacée. Lecture hors cache.
            if ($source === []) {
                update_user_meta($actor, self::SOURCE, wp_slash($record));
                if (self::sourceFiable($actor) !== [$record]) {
                    throw new \RuntimeException('Source non enregistrée');
                }
            }
            if ($wpdb->query('COMMIT') === false) {
                throw new \RuntimeException('Validation impossible');
            }
            return true;
        } catch (\Throwable) {
            $wpdb->query('ROLLBACK');
            wp_cache_delete($key, 'options');
            wp_cache_delete('notoptions', 'options');
            wp_cache_delete($actor, 'user_meta');
            return new \WP_Error('imagine_acquisition_ecriture');
        } finally {
            $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
        }
    }

    /** [] signifie absence SQL prouvée ; une erreur n'est jamais une absence. */
    public static function sourceFiable(int $owner): array|\WP_Error
    {
        global $wpdb;
        wp_cache_delete($owner, 'user_meta');
        $wpdb->last_error = '';
        $rows = $wpdb->get_results($wpdb->prepare(
            "SELECT meta_value FROM {$wpdb->usermeta} WHERE user_id = %d AND meta_key = %s",
            $owner,
            self::SOURCE
        ), ARRAY_A);
        if ($wpdb->last_error !== '' || !is_array($rows)) {
            return new \WP_Error('imagine_acquisition_source_lecture');
        }
        return array_map(static fn (array $row): mixed => maybe_unserialize($row['meta_value']), $rows);
    }
}
