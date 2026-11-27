<?php

declare(strict_types=1);

namespace Imagine\Site;

final class CodesSuivisAdmin
{
    private static bool $restoring = false;

    public static function register(): void
    {
        add_action('admin_init', static function (): void {
            register_setting('imagine_codes_suivis', CodesSuivis::OPTION, ['type' => 'array', 'show_in_rest' => false, 'sanitize_callback' => [self::class, 'nettoyer']]);
        });
        add_action('admin_menu', static function (): void {
            add_options_page(__('Codes suivis', 'imagine-site'), __('Codes suivis', 'imagine-site'), 'manage_options', 'imagine-codes-suivis', [self::class, 'reglages']);
            if (TableauBordAdmin::autorise()) {
                add_submenu_page('imagine', __('Codes suivis', 'imagine-site'), __('Codes suivis', 'imagine-site'),
                    current_user_can('manage_options') ? 'manage_options' : TableauBordAdmin::CAP, 'imagine-codes-nombres', [self::class, 'nombres']);
            }
        }, 126);
        add_filter('woocommerce_prevent_admin_access', static function (bool $prevent): bool {
            global $pagenow;
            return $pagenow === 'admin.php' && ($_GET['page'] ?? null) === 'imagine-codes-nombres' && TableauBordAdmin::autorise() ? false : $prevent;
        });
        add_action('added_option', static fn ($key, $new) => self::journal($key, null, $new), 30, 2);
        add_action('updated_option', static fn ($key, $old, $new) => self::journal($key, $old, $new), 30, 3);
    }

    public static function nettoyer(mixed $value): array
    {
        if (self::$restoring) {
            return is_array($value) ? $value : [];
        }
        if (is_string($value)) {
            $rows = [];
            foreach (preg_split('/\r\n|\n|\r/', $value) as $line) {
                if (trim($line) === '') { continue; }
                $parts = explode('|', $line, 2);
                if (count($parts) !== 2 || isset($rows[$parts[0]])) { $rows = null; break; }
                $rows[$parts[0]] = $parts[1];
            }
            $value = $rows;
        }
        $valid = is_array($value) && count($value) <= 50 ? CodesSuivisRegles::liste($value) : null;
        if ($valid !== null) { return $valid; }
        add_settings_error(CodesSuivis::OPTION, 'imagine_c30_liste', __('Liste invalide : ancienne liste conservée.', 'imagine-site'));
        return CodesSuivis::configuration();
    }

    private static function journal(string $key, mixed $old, mixed $new): void
    {
        if (self::$restoring || $key !== CodesSuivis::OPTION || $old === $new) { return; }
        $user = wp_get_current_user();
        $name = 'imagine_reglages_journal_' . str_replace('-', '', wp_generate_uuid4());
        $event = ['quand_utc' => gmdate('Y-m-d\TH:i:s\Z'), 'qui_id' => $user->ID, 'qui_login' => $user->ID ? $user->user_login : 'systeme', 'option' => $key, 'avant' => $old, 'apres' => $new];
        $written = add_option($name, $event, '', false);
        wp_cache_delete($name, 'options');
        if ($written && get_option($name) === $event) { return; }
        self::$restoring = true;
        try {
            $old === null ? delete_option($key) : update_option($key, $old, false);
            if (get_option($key, null) !== $old) {
                wp_die(esc_html__('Journal et restauration indisponibles.', 'imagine-site'), '', ['response' => 500]);
            }
        } finally { self::$restoring = false; }
        add_settings_error($key, 'imagine_c30_journal', __('Journal indisponible : liste inchangée.', 'imagine-site'));
    }

    public static function reglages(): void
    {
        if (!current_user_can('manage_options')) { wp_die('', '', ['response' => 403]); }
        $lines = [];
        foreach (CodesSuivis::configuration() as $code => $label) { $lines[] = $code . '|' . $label; }
        echo '<div class="wrap"><h1>' . esc_html__('Codes suivis — aucun avantage financier', 'imagine-site') . '</h1>';
        echo '<form method="post" action="options.php">';
        settings_fields('imagine_codes_suivis');
        echo '<p><label for="imagine-c30-liste">' . esc_html__('Un code|libellé interne par ligne. 50 codes maximum, code de 1 à 40 caractères minuscules, chiffres ou tirets ; libellé de 80 caractères. Liste vide : aucun code retenu.', 'imagine-site') . '</label></p>';
        echo '<textarea id="imagine-c30-liste" name="imagine_codes_suivis" rows="6" cols="70">' . esc_textarea(implode("\n", $lines)) . '</textarea>';
        submit_button();
        echo '</form></div>';
    }

    public static function nombres(): void
    {
        if (!TableauBordAdmin::autorise()) { wp_die('', '', ['response' => 403]); }
        nocache_headers();
        $du = isset($_GET['du']) && is_string($_GET['du']) ? wp_unslash($_GET['du']) : gmdate('Y-m-01');
        $au = isset($_GET['au']) && is_string($_GET['au']) ? wp_unslash($_GET['au']) : gmdate('Y-m-d');
        echo '<div class="wrap"><h1>' . esc_html__('Codes suivis et acquisition déclarée', 'imagine-site') . '</h1>';
        echo '<form method="get"><input type="hidden" name="page" value="imagine-codes-nombres">';
        echo '<label>' . esc_html__('Du', 'imagine-site') . '<input type="date" name="du" value="' . esc_attr($du) . '"></label> ';
        echo '<label>' . esc_html__('Au', 'imagine-site') . '<input type="date" name="au" value="' . esc_attr($au) . '"></label> ';
        echo '<button type="submit">' . esc_html__('Afficher', 'imagine-site') . '</button></form>';
        echo '<h2>' . esc_html__('Codes des commandes payées, date de paiement UTC incluse', 'imagine-site') . '</h2>';
        $counts = CodesSuivis::compter($du, $au);
        if (is_wp_error($counts)) {
            echo '<p role="alert">' . esc_html__('Lecture impossible ou période invalide.', 'imagine-site') . '</p>';
        } else {
            echo '<table><thead><tr><th>' . esc_html__('Code', 'imagine-site') . '</th><th>' . esc_html__('Nombre', 'imagine-site') . '</th></tr></thead><tbody>';
            foreach ($counts as $code => $count) { echo '<tr><th>' . esc_html($code) . '</th><td>' . (int)$count . '</td></tr>'; }
            echo '</tbody></table>';
        }
        echo '<h2>' . esc_html__('Réponses volontaires de C-27, date de déclaration UTC incluse', 'imagine-site') . '</h2>';
        $rows = AcquisitionConfidentialite::lignes();
        $declared = is_wp_error($rows) ? null : AcquisitionRegles::compter($rows, $du, $au);
        if ($declared === null) {
            echo '<p role="alert">' . esc_html__('Lecture impossible ou période invalide.', 'imagine-site') . '</p>';
        } else {
            echo '<ul>';
            foreach ($declared as $row) { echo '<li>' . esc_html($row['libelle']) . ' : ' . (int)$row['nombre'] . '</li>'; }
            echo '</ul>';
        }
        echo '</div>';
    }
}
