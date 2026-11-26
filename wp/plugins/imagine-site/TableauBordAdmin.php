<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Écran sans formulaire, script, cache persistant, journal ou mutation de capacité. */
final class TableauBordAdmin
{
    public const CAP = 'imagine_voir_tableau_bord';
    public const PAGE = 'imagine-tableau-de-bord';

    private static function t(string $text): string
    {
        return __($text, 'imagine-site');
    }

    public static function autorise(): bool
    {
        return current_user_can('manage_options') || current_user_can(self::CAP);
    }

    private static function verifier(): void
    {
        if (!self::autorise()) {
            wp_die(self::t('Tableau de bord réservé au Référent abonnements.'), '', ['response' => 403]);
        }
    }

    public static function register(): void
    {
        // Méta-capacité WP dédiée : les deux droits des sources, sans mutation du rôle C09.
        add_filter('map_meta_cap', static function (array $caps, string $cap): array {
            return $cap === self::CAP ? ['imagine_extraire_abonnes', 'imagine_gerer_echeances'] : $caps;
        }, 10, 2);
        add_action('admin_menu', [self::class, 'menu'], 120);
        add_action('admin_init', static function (): void {
            if (($_GET['page'] ?? null) === self::PAGE) {
                self::verifier();
                if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'GET' && ($_SERVER['REQUEST_METHOD'] ?? '') !== 'HEAD') {
                    header('Allow: GET, HEAD');
                    wp_die(self::t('Tableau de bord en lecture seule.'), '', ['response' => 405]);
                }
            }
        });
        add_filter('woocommerce_prevent_admin_access', static function (bool $prevent): bool {
            global $pagenow;
            return $pagenow === 'admin.php' && ($_GET['page'] ?? null) === self::PAGE && self::autorise() ? false : $prevent;
        });
    }

    public static function menu(): void
    {
        if (self::autorise()) {
            add_submenu_page(
                'imagine',
                self::t('Tableau de bord'),
                self::t('Tableau de bord'),
                current_user_can('manage_options') ? 'manage_options' : self::CAP,
                self::PAGE,
                [self::class, 'page']
            );
        }
    }

    public static function page(): void
    {
        self::verifier();
        nocache_headers();
        header('Cache-Control: private, no-store, no-cache, must-revalidate, max-age=0');
        echo '<div class="wrap" data-imagine-tableau><h1>' . esc_html(self::t('Tableau de bord')) . '</h1>';
        echo '<p>' . esc_html(self::t('Lecture seule — nombres calculés à l’affichage sur les données natives. Démonstration fictive ; aucune personne identifiée, aucun email, aucune tâche planifiée ni appel sortant.')) . '</p>';
        echo '<p>' . esc_html(sprintf(self::t('Lecture UTC : %s. Les valeurs reflètent l’état courant, pas un instantané comptable figé.'), gmdate('Y-m-d H:i:s'))) . '</p>';
        try {
            // Calcul complet avant tout chiffre : une source absente ne devient jamais zéro.
            $metrics = TableauBordNatives::lire();
            foreach ($metrics as $id => $metric) {
                echo '<section data-imagine-indicateur="' . esc_attr($id) . '"><h2>' . esc_html(self::t($metric['titre'])) . '</h2>';
                echo '<table class="widefat striped"><thead><tr><th scope="col">' . esc_html(self::t('Mesure')) . '</th><th scope="col">' . esc_html(self::t('Nombre')) . '</th></tr></thead><tbody>';
                foreach ($metric['valeurs'] as $key => $number) {
                    $label = $metric['libelles'][$key] ?? (string) $key;
                    echo '<tr><th scope="row">' . esc_html(self::t($label)) . '</th><td data-imagine-mesure="' . esc_attr((string) $key) . '">' . esc_html((string) $number) . '</td></tr>';
                }
                echo '</tbody></table><p>' . esc_html(self::t($metric['phrase'])) . '</p></section>';
            }
        } catch (\Throwable) {
            echo '<div class="notice notice-error"><p>' . esc_html(self::t('Indicateurs indisponibles : lecture native impossible. Aucun nombre de remplacement.')) . '</p></div>';
        }
        echo '<h2>' . esc_html(self::t('À venir — à discuter à l’atelier')) . '</h2><table class="widefat"><thead><tr><th scope="col">' . esc_html(self::t('Indicateur')) . '</th><th scope="col">' . esc_html(self::t('Ce qui manque')) . '</th></tr></thead><tbody>';
        $future = [
            'Par tarif' => 'Grille tarifaire non arrêtée.',
            'Par moyen de paiement' => 'Distinction mode/moyen à arrêter à l’atelier.',
            'Taux de rétention annuel' => 'Définition à arrêter à l’atelier.',
            'Non-renouvellements et motifs déclarés' => 'Recueil des motifs et définition du suivi non raccordés.',
            'Passages de l’accès découverte à l’abonnement' => 'Lien de conversion non enregistré.',
            'Part du tarif solidaire et de soutien' => 'Grille et rattachement tarifaire non arrêtés ; un justificatif ne prouve pas un tarif.',
            'Étiquettes de persona' => 'Questions et étiquettes non arrêtées.',
        ];
        foreach ($future as $title => $missing) {
            echo '<tr class="description" style="color:#646970;background:#f0f0f1" data-imagine-a-venir><th scope="row">' . esc_html(self::t($title)) . ' — ' . esc_html(self::t('à venir')) . '</th><td>' . esc_html(self::t($missing)) . '</td></tr>';
        }
        echo '</tbody></table></div>';
    }
}
