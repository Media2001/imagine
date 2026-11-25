<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Un écran sous le menu Imagine existant, droit dédié C09. */
final class EcheancesAdmin
{
    public const CAP = 'imagine_gerer_echeances';
    public const PAGE = 'imagine-echeances';
    public const EXPORT = 'imagine_exporter_mandats';
    public const RECU = 'imagine_virement_recu';

    private static function t(string $text): string
    {
        return __($text, 'imagine-site');
    }

    public static function autorise(): bool
    {
        return current_user_can('manage_options') || current_user_can(self::CAP);
    }

    public static function register(): void
    {
        foreach ([self::EXPORT => 'exporter'] as $action => $method) {
            add_action('admin_post_' . $action, [self::class, $method]);
            add_action('admin_post_nopriv_' . $action, [self::class, $method]);
        }
        add_action('admin_menu', [self::class, 'menu'], 110);
        add_filter('woocommerce_prevent_admin_access', static function (bool $prevent): bool {
            global $pagenow;
            return $pagenow === 'admin.php' && ($_GET['page'] ?? '') === self::PAGE && self::autorise() ? false : $prevent;
        });
    }

    public static function menu(): void
    {
        if (self::autorise()) {
            // C10 et C13 enregistrent le même parent pour des capacités différentes.
            // Garder seulement son entrée accessible ; aucun nouveau menu principal.
            global $menu;
            $kept = false;
            foreach ($menu as $index => $entry) {
                if (($entry[2] ?? '') === 'imagine') {
                    if ($kept || !current_user_can($entry[1])) {
                        unset($menu[$index]);
                    } else {
                        $kept = true;
                    }
                }
            }
            add_submenu_page('imagine', self::t('Échéances'), self::t('Échéances'),
                current_user_can('manage_options') ? 'manage_options' : self::CAP, self::PAGE, [self::class, 'page']);
        }
    }

    private static function verifier(): void
    {
        if (!self::autorise()) {
            wp_die(self::t('Accès réservé au référent administratif.'), '', ['response' => 403]);
        }
    }

    public static function periode(array $request): int
    {
        $value = $request['jours'] ?? '30';
        if (!is_string($value) || !in_array($value, ['30', '90', '180'], true)) {
            throw new \InvalidArgumentException('Période invalide.');
        }
        return (int) $value;
    }

    private static function requete(string $nonceAction): void
    {
        self::verifier();
        if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
            header('Allow: POST');
            wp_die(self::t('Requête POST uniquement.'), '', ['response' => 405]);
        }
        $nonce = $_POST['_wpnonce'] ?? null;
        if (!is_string($nonce) || !wp_verify_nonce($nonce, $nonceAction)) {
            wp_die(self::t('Jeton de sécurité invalide.'), '', ['response' => 403]);
        }
    }

    public static function exporter(): void
    {
        self::verifier();
        try {
            $days = self::periode($_POST);
        } catch (\Throwable) {
            wp_die(self::t('Période invalide.'), '', ['response' => 400]);
        }
        self::requete(self::EXPORT . ':' . $days);
        try {
            $rows = EcheancesNatives::lire('mandats', $days);
        } catch (\Throwable) {
            wp_die(self::t('Export indisponible.'), '', ['response' => 409]);
        }
        nocache_headers();
        header('Cache-Control: private, no-store, no-cache, must-revalidate, max-age=0');
        header('Content-Type: text/csv; charset=UTF-8');
        header('X-Content-Type-Options: nosniff');
        header('Content-Disposition: attachment; filename="mandats-papier.csv"');
        $stream = fopen('php://output', 'w');
        EcheancesRegles::csv($stream, $rows);
        fclose($stream);
        exit;
    }

    public static function page(): void
    {
        self::verifier();
        nocache_headers();
        $labels = ['echeances' => self::t('Arrivent à échéance'), 'attente' => self::t('Paiements en attente'),
            'virements' => self::t('Virements à valider'), 'mandats' => self::t('Prélèvements sur mandat papier à lancer'),
            'echecs' => self::t('Paiements échoués')];
        try {
            $days = self::periode($_GET);
            $view = $_GET['vue'] ?? 'echeances';
            if (!is_string($view) || !isset($labels[$view])) {
                throw new \InvalidArgumentException('Vue invalide.');
            }
            $rows = EcheancesNatives::lire($view, $days);
        } catch (\Throwable) {
            wp_die(self::t('Données ou filtres indisponibles. Aucune opération effectuée.'), '', ['response' => 400]);
        }
        echo '<div class="wrap"><h1>' . esc_html(self::t('Échéances')) . '</h1><nav class="nav-tab-wrapper" aria-label="' . esc_attr(self::t('Vues des échéances')) . '">';
        foreach ($labels as $key => $label) {
            echo '<a class="nav-tab' . ($view === $key ? ' nav-tab-active' : '') . '" href="'
                . esc_url(add_query_arg(['page' => self::PAGE, 'vue' => $key, 'jours' => $days], admin_url('admin.php'))) . '">' . esc_html($label) . '</a>';
        }
        echo '</nav><h2>' . esc_html($labels[$view]) . '</h2><form method="get"><input type="hidden" name="page" value="' . esc_attr(self::PAGE) . '">'
            . '<input type="hidden" name="vue" value="' . esc_attr($view) . '"><label for="imagine-jours">' . esc_html(self::t('Période à partir de maintenant (UTC)')) . '</label> '
            . '<select id="imagine-jours" name="jours">';
        foreach ([30, 90, 180] as $period) {
            echo '<option value="' . esc_attr((string) $period) . '"' . selected($period, $days, false) . '>'
                . esc_html(sprintf(self::t('%d jours'), $period)) . '</option>';
        }
        echo '</select> ';
        submit_button(self::t('Afficher'), 'secondary', '', false);
        echo '</form><p>' . esc_html(self::t('États natifs uniquement. Les paiements en attente et échoués restent visibles sans limite d’ancienneté. Aucun délai de retard ni droit d’accès n’est calculé ici.')) . '</p>';
        if (get_option('imagine_demo_site') === 'imagine-test-demo') {
            echo '<div class="notice notice-warning inline"><p>' . esc_html(self::t('Démonstration fictive hors ligne : A-VIR et A-PAPIER sont identifiés par leurs marqueurs natifs C09, sans passerelle. A-PAPIER est la référence fictive du mandat, pas une donnée bancaire. Aucun email ni appel sortant.')) . '</p></div>';
        }
        echo '<table class="widefat striped"><thead><tr>';
        foreach ([self::t('Abonné'), self::t('Objet natif'), self::t('État'), self::t('Montant'), self::t('Échéance / création (UTC)'), self::t('Référence du mandat')] as $label) {
            echo '<th scope="col">' . esc_html($label) . '</th>';
        }
        echo '</tr></thead><tbody>';
        foreach ($rows as $row) {
            echo '<tr data-imagine-echeance="' . esc_attr((string) $row['id']) . '"><td>' . esc_html($row['abonne']) . '</td><td>#'
                . esc_html((string) $row['id']) . '</td><td>' . esc_html($row['etat']) . '</td><td>'
                . esc_html($row['montant'] . ' ' . $row['devise']) . '</td><td>' . esc_html(gmdate('Y-m-d H:i:s', $row['echeance'] ?? $row['creation']))
                . '</td><td>' . esc_html($view === 'mandats' ? $row['reference'] : '—') . '</td></tr>';
        }
        if ($rows === []) {
            echo '<tr><td colspan="6">' . esc_html(self::t('Aucun résultat dans cette vue.')) . '</td></tr>';
        }
        echo '</tbody></table>';
        if ($view === 'mandats') {
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr(self::EXPORT)
                . '"><input type="hidden" name="jours" value="' . esc_attr((string) $days) . '">';
            wp_nonce_field(self::EXPORT . ':' . $days);
            submit_button(self::t('Exporter les mandats papier (CSV)'));
            echo '</form>';
        }
        echo '</div>';
    }
}
