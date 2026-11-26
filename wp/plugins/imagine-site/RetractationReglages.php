<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Deux réglages C10 et un champ de date sur la commande ; aucun changement de paiement. */
final class RetractationReglages
{
    public static function register(): void
    {
        add_action('admin_init', static function (): void {
            register_setting('imagine_reglages', Retractation::OPTION, ['type' => 'array', 'show_in_rest' => false, 'sanitize_callback' => [self::class, 'nettoyer']]);
        }, 50);
        add_action('admin_menu', static function (): void {
            global $wp_filter;
            $hook = get_plugin_page_hookname('imagine-reglages', 'imagine');
            foreach (($wp_filter[$hook]->callbacks ?? []) as $priority => $callbacks) {
                foreach ($callbacks as $callback) {
                    $fn = $callback['function'];
                    remove_action($hook, $fn, $priority);
                    add_action($hook, static function () use ($fn): void {
                        ob_start();
                        $fn();
                        $html = ob_get_clean();
                        $end = strpos($html, '</form>');
                        if ($end !== false && (str_contains($html, 'value="imagine_reglages"') || str_contains($html, "value='imagine_reglages'"))) {
                            $html = substr_replace($html, self::champs(), $end, 0);
                        }
                        echo $html;
                    }, $priority);
                }
            }
        }, 150);
        add_action('woocommerce_admin_order_data_after_order_details', static function ($order): void {
            echo '<p><label for="imagine-c25-date">' . esc_html__('Début manuel du délai de rétractation (UTC)', 'imagine-site') . '</label>'
                . '<input type="date" id="imagine-c25-date" name="imagine_c25_date" value="' . esc_attr((string)$order->get_meta(Retractation::MANUELLE)) . '"></p>';
            wp_nonce_field('imagine_c25_date', '_imagine_c25_date');
        });
        add_action('woocommerce_process_shop_order_meta', [self::class, 'sauverDate'], 50, 1);
    }

    public static function nettoyer(mixed $value): array
    {
        if (is_array($value) && count($value) === 2 && isset($value['jours'], $value['origine'])
            && (is_int($value['jours']) || (is_string($value['jours']) && preg_match('/^[1-9][0-9]{0,2}$/D', $value['jours'])))) {
            $value['jours'] = (int)$value['jours'];
            if (RetractationRegles::valide($value)) {
                return $value;
            }
        }
        add_settings_error(Retractation::OPTION, 'imagine_retractation_invalide', __('Réglage de rétractation invalide : valeur conservée.', 'imagine-site'));
        return Retractation::configuration();
    }

    public static function sauverDate(int $id): void
    {
        if (!current_user_can('manage_woocommerce') || !isset($_POST['imagine_c25_date'], $_POST['_imagine_c25_date'])
            || !is_string($_POST['imagine_c25_date']) || !is_string($_POST['_imagine_c25_date'])
            || !wp_verify_nonce(wp_unslash($_POST['_imagine_c25_date']), 'imagine_c25_date')) {
            return;
        }
        $value = wp_unslash($_POST['imagine_c25_date']);
        if ($value !== '' && Retractation::dateManuelle($value) === null) {
            return;
        }
        $order = wc_get_order($id);
        if ($order && $order->get_type() === 'shop_order') {
            $order->update_meta_data(Retractation::MANUELLE, $value);
            $order->save_meta_data();
        }
    }

    public static function champs(): string
    {
        $config = Retractation::configuration();
        return '<section id="imagine-retractation-reglages"><h2>' . esc_html__('Rétractation — demande seule', 'imagine-site') . '</h2><p>'
            . esc_html__('Valeurs de démonstration, à valider par Imagine et son conseil juridique. Aucun effet automatique sur le paiement, l’abonnement ou les accès.', 'imagine-site')
            . '</p><p><label for="imagine-c25-jours">' . esc_html__('Délai en jours (1 à 365)', 'imagine-site')
            . '</label> <input id="imagine-c25-jours" type="number" min="1" max="365" name="imagine_retractation_reglages[jours]" value="' . (int)$config['jours'] . '"></p>'
            . '<p><label for="imagine-c25-origine">' . esc_html__('Point de départ', 'imagine-site') . '</label> <select id="imagine-c25-origine" name="imagine_retractation_reglages[origine]">'
            . '<option value="paiement"' . selected($config['origine'], 'paiement', false) . '>' . esc_html__('Date de la commande payée', 'imagine-site') . '</option>'
            . '<option value="manuelle"' . selected($config['origine'], 'manuelle', false) . '>' . esc_html__('Date manuelle sur la commande', 'imagine-site') . '</option></select></p></section>';
    }
}
