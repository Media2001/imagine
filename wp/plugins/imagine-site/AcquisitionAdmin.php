<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Nombres seuls, à côté de C19 et avec ses mêmes droits. Aucun journal de consultation. */
final class AcquisitionAdmin
{
    public const PAGE = 'imagine-acquisition';

    public static function register(): void
    {
        add_action('admin_menu', static function (): void {
            if (TableauBordAdmin::autorise()) {
                add_submenu_page('imagine', __('Acquisition déclarée', 'imagine-site'), __('Acquisition déclarée', 'imagine-site'),
                    current_user_can('manage_options') ? 'manage_options' : TableauBordAdmin::CAP, self::PAGE, [self::class, 'page']);
            }
        }, 125);
        add_filter('woocommerce_prevent_admin_access', static function (bool $prevent): bool {
            global $pagenow;
            return $pagenow === 'admin.php' && ($_GET['page'] ?? null) === self::PAGE && TableauBordAdmin::autorise() ? false : $prevent;
        });
    }

    public static function page(): void
    {
        if (!TableauBordAdmin::autorise()) {
            wp_die(esc_html__('Nombres réservés au Référent abonnements.', 'imagine-site'), '', ['response' => 403]);
        }
        if (!in_array($_SERVER['REQUEST_METHOD'] ?? 'GET', ['GET', 'HEAD'], true)) {
            wp_die(esc_html__('Lecture seule.', 'imagine-site'), '', ['response' => 405]);
        }
        nocache_headers();
        $from = isset($_GET['du']) && is_string($_GET['du']) ? wp_unslash($_GET['du']) : gmdate('Y-m-01');
        $until = isset($_GET['au']) && is_string($_GET['au']) ? wp_unslash($_GET['au']) : gmdate('Y-m-d');
        echo '<div class="wrap" id="imagine-acquisition-nombres"><h1>' . esc_html__('Acquisition déclarée', 'imagine-site') . '</h1><p>'
            . esc_html__('Réponses volontaires par période de déclaration (UTC, bornes incluses). Aucune identité, aucun rapprochement avec la navigation. Les réponses effacées ne sont plus comptées ; un ancien libellé reste distinct après modification de la liste.', 'imagine-site')
            . '</p><form method="get"><input type="hidden" name="page" value="imagine-acquisition"><p>'
            . '<label for="imagine-acquisition-du">' . esc_html__('Du', 'imagine-site') . '</label> <input id="imagine-acquisition-du" type="date" name="du" value="' . esc_attr($from) . '"> '
            . '<label for="imagine-acquisition-au">' . esc_html__('Au', 'imagine-site') . '</label> <input id="imagine-acquisition-au" type="date" name="au" value="' . esc_attr($until) . '"> '
            . '<button type="submit" class="button">' . esc_html__('Afficher', 'imagine-site') . '</button></p></form>';
        $rows = AcquisitionConfidentialite::lignes();
        try {
            $counts = is_wp_error($rows) ? null : AcquisitionRegles::compter($rows, $from, $until);
        } catch (\Throwable) {
            $counts = null;
        }
        if ($counts === null) {
            echo '<p role="alert">' . esc_html__('Période invalide ou lecture impossible : aucun nombre affiché.', 'imagine-site') . '</p></div>';
            return;
        }
        echo '<table class="widefat striped"><thead><tr><th scope="col">' . esc_html__('Réponse', 'imagine-site')
            . '</th><th scope="col">' . esc_html__('Nombre', 'imagine-site') . '</th></tr></thead><tbody>';
        foreach ($counts as $row) {
            echo '<tr><th scope="row">' . esc_html($row['libelle']) . '</th><td data-acquisition="' . esc_attr($row['choix']) . '">'
                . (int) $row['nombre'] . '</td></tr>';
        }
        echo '</tbody></table>';
        if ($counts === []) {
            echo '<p>' . esc_html__('Aucune déclaration sur cette période.', 'imagine-site') . '</p>';
        }
        echo '</div>';
    }
}
