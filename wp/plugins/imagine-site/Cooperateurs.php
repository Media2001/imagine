<?php

declare(strict_types=1);

namespace Imagine\Site;

/** B06 : attribut administratif ; aucun raccord à Memberships ni au droit des articles. */
final class Cooperateurs
{
    public const META = 'imagine_cooperateur';
    public const PAGE = 'imagine_cooperateurs_page';
    public const ACCROCHE = 'imagine_cooperateur_modifie';

    public static function register(): void
    {
        add_action('show_user_profile', [self::class, 'fiche']);
        add_action('edit_user_profile', [self::class, 'fiche']);
        foreach (['personal_options_update', 'edit_user_profile_update'] as $hook) {
            add_action($hook, static function (int $id): void {
                if (!isset($_POST['imagine_cooperateur_present'])) {
                    return;
                }
                try {
                    self::enregistrer($id);
                } catch (\Throwable) {
                    wp_die(esc_html__('Statut coopérateur non modifié : rechargez la fiche.', 'imagine-site'), '', ['response' => 403]);
                }
            });
        }
        add_action('woocommerce_account_dashboard', [self::class, 'compte'], 25);
    }

    public static function administration(): bool
    {
        return CooperateursRegles::administration(wp_get_current_user()->roles);
    }

    public static function autorise(): bool
    {
        return CooperateursRegles::lecture(get_user_meta(get_current_user_id(), self::META, true),
            wp_get_current_user()->roles, is_user_logged_in());
    }

    public static function fiche(\WP_User $user): void
    {
        if (!self::administration() || !current_user_can('edit_user', $user->ID)) {
            return;
        }
        $state = get_user_meta($user->ID, self::META, true);
        echo '<h2>' . esc_html__('Espace coopérateurs', 'imagine-site') . '</h2><table class="form-table"><tr><th>'
            . esc_html__('Coopérateur', 'imagine-site') . '</th><td>';
        wp_nonce_field('imagine_cooperateur_' . $user->ID, 'imagine_cooperateur_nonce');
        echo '<input type="hidden" name="imagine_cooperateur_present" value="1"><label><input type="checkbox" name="imagine_cooperateur_oui" value="1"'
            . checked(is_array($state) && ($state['cooperateur'] ?? false) === true, true, false) . '> '
            . esc_html__('Ouvrir l’espace coopérateurs, jamais les articles', 'imagine-site') . '</label>';
        if (is_array($state)) {
            echo '<p>' . esc_html__('Source : administration', 'imagine-site') . ' — <time>' . esc_html($state['date_utc'] ?? '') . '</time></p>';
        }
        echo '</td></tr></table>';
    }

    public static function enregistrer(int $id): void
    {
        $nonce = $_POST['imagine_cooperateur_nonce'] ?? null;
        if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST' || !self::administration()
            || !get_userdata($id) || !current_user_can('edit_user', $id)
            || !is_string($nonce) || !wp_verify_nonce($nonce, 'imagine_cooperateur_' . $id)
            || ($_POST['imagine_cooperateur_present'] ?? '') !== '1'
            || (isset($_POST['imagine_cooperateur_oui']) && $_POST['imagine_cooperateur_oui'] !== '1')) {
            throw new \RuntimeException('Modification refusée.');
        }
        global $wpdb;
        $lock = 'imagine_cooperateur_' . $id;
        if ((int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s,3)', $lock)) !== 1) {
            throw new \RuntimeException('Statut occupé.');
        }
        try {
            wp_cache_delete($id, 'user_meta');
            $old = get_user_meta($id, self::META, true);
            $existed = metadata_exists('user', $id, self::META);
            $oui = isset($_POST['imagine_cooperateur_oui']);
            if ((!$existed && !$oui) || (is_array($old) && ($old['cooperateur'] ?? null) === $oui
                && ($old['source'] ?? '') === 'administration')) {
                return;
            }
            $new = ['cooperateur' => $oui, 'source' => 'administration', 'date_utc' => gmdate('Y-m-d\TH:i:s\Z')];
            if (!update_user_meta($id, self::META, $new) || get_user_meta($id, self::META, true) !== $new) {
                throw new \RuntimeException('Statut non enregistré.');
            }
            $u = wp_get_current_user();
            $row = ['quand_utc' => $new['date_utc'], 'qui_id' => $u->ID, 'qui_login' => $u->user_login,
                'option' => self::META . '_' . $id, 'avant' => $existed ? $old : null, 'apres' => $new];
            $key = \Imagine\Pilotage\Administration\Reglages::JOURNAL . str_replace('-', '', wp_generate_uuid4());
            if (!add_option($key, $row, '', false) || get_option($key) !== $row) {
                $existed ? update_user_meta($id, self::META, $old) : delete_user_meta($id, self::META);
                wp_cache_delete($id, 'user_meta');
                if (get_user_meta($id, self::META, true) !== $old) {
                    throw new \RuntimeException('Restauration du statut impossible.');
                }
                throw new \RuntimeException('Journal indisponible.');
            }
            // Point nommé pour un futur raccord ; aucun écouteur/transport enregistré ici.
            do_action(self::ACCROCHE, $id, $new, $old);
        } finally {
            $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
        }
    }

    /** Journal C10/C17 commun, événements B06 ciblés uniquement. */
    public static function audits(int $id): array
    {
        global $wpdb;
        $prefix = \Imagine\Pilotage\Administration\Reglages::JOURNAL;
        $rows = $wpdb->get_results($wpdb->prepare("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_id", $wpdb->esc_like($prefix) . '%'));
        $out = [];
        foreach ($rows as $row) {
            $value = maybe_unserialize($row->option_value);
            if (is_array($value) && ($value['option'] ?? '') === self::META . '_' . $id) {
                $out[$row->option_name] = $value;
            }
        }
        return $out;
    }

    public static function compte(): void
    {
        if (!is_user_logged_in()) {
            return;
        }
        $s = get_user_meta(get_current_user_id(), self::META, true);
        $oui = CooperateursRegles::lecture($s, [], true);
        echo '<section id="mon-statut-cooperateur"><h2>' . esc_html__('Mon statut de coopérateur', 'imagine-site') . '</h2><p>'
            . esc_html($oui ? __('Coopérateur : oui', 'imagine-site') : __('Coopérateur : non', 'imagine-site'));
        if (is_array($s)) {
            echo ' — ' . esc_html__('Source : administration', 'imagine-site') . ' — <time>' . esc_html($s['date_utc'] ?? '') . '</time>';
        }
        echo '</p>';
        if (self::autorise() && ($id = (int) get_option(self::PAGE))) {
            echo '<p><a href="' . esc_url(get_permalink($id)) . '">' . esc_html__('Espace coopérateurs', 'imagine-site') . '</a></p>';
        }
        echo '</section>';
    }
}
