<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Inventaire des seuls cookies observés par la recette C32, sans valeur. */
final class Cookies
{
    /** @return list<array{nom:string,motif:string,origine:string,geste:string,duree:string,usage:string}> */
    public static function liste(): array
    {
        $rows = [];
        foreach (['sbjs_migrations', 'sbjs_current_add', 'sbjs_first_add', 'sbjs_current', 'sbjs_first', 'sbjs_udata', 'sbjs_session'] as $name) {
            $rows[] = self::ligne($name, preg_quote($name, '~'), 'WooCommerce — attribution d’origine', 'Simple lecture, scripts actifs', $name === 'sbjs_session' ? '30 minutes' : 'Session du navigateur', 'Mesure — attribution d’origine des commandes');
        }
        $rows[] = self::ligne('wp_woocommerce_session_[hash]', 'wp_woocommerce_session_[a-f0-9]{32}', 'WooCommerce', 'Code suivi connu (C-30), panier ou connexion', '2 jours (réglage natif par défaut)', 'Fonctionnement — session et panier');
        foreach (['woocommerce_items_in_cart', 'woocommerce_cart_hash'] as $name) {
            $rows[] = self::ligne($name, $name, 'WooCommerce', 'Ajout au panier', 'Session du navigateur', 'Fonctionnement — panier');
        }
        $rows[] = self::ligne('wordpress_test_cookie', 'wordpress_test_cookie', 'WordPress', 'Ouverture de la connexion', 'Session du navigateur', 'Fonctionnement — test des cookies');
        $rows[] = self::ligne('wordpress_[hash]', 'wordpress_[a-f0-9]{32}', 'WordPress', 'Connexion réussie sur cette démonstration HTTP', 'Session du navigateur sans « Se souvenir de moi » ; validité serveur : 2 jours', 'Fonctionnement — authentification');
        $rows[] = self::ligne('wordpress_logged_in_[hash]', 'wordpress_logged_in_[a-f0-9]{32}', 'WordPress', 'Connexion réussie', 'Session du navigateur sans « Se souvenir de moi » ; validité serveur : 2 jours', 'Fonctionnement — authentification');
        $rows[] = self::ligne('wp_lang', 'wp_lang', 'WordPress', 'Choix de langue sur la connexion', 'Session du navigateur', 'Fonctionnement — langue de connexion');
        return $rows;
    }

    private static function ligne(string $name, string $pattern, string $origin, string $gesture, string $duration, string $usage): array
    {
        return ['nom' => $name, 'motif' => $pattern, 'origine' => $origin, 'geste' => $gesture, 'duree' => $duration, 'usage' => $usage];
    }

    /** @param list<string> $names @return list<string> */
    public static function inconnus(array $names): array
    {
        return array_values(array_filter($names, static function (string $name): bool {
            foreach (self::liste() as $row) {
                if (preg_match('~\A(?:' . $row['motif'] . ')\z~D', $name) === 1) {
                    return false;
                }
            }
            return true;
        }));
    }

    public static function register(): void
    {
        add_filter('the_content', [self::class, 'contenu'], 40);
    }

    public static function contenu(string $content): string
    {
        $pages = get_option(AutresPages::OPTION, []);
        if (!is_singular('page') || !in_the_loop() || !is_main_query() || get_the_ID() !== (int) ($pages['cookies'] ?? 0)) {
            return $content;
        }
        $html = '<div data-imagine-cookies><table><caption>' . esc_html__('Cookies observés sur la démonstration', 'imagine-site') . '</caption><thead><tr>';
        foreach (['Nom ou motif', 'Déposé par', 'À quel geste', 'Durée', 'Usage'] as $heading) {
            $html .= '<th scope="col">' . esc_html__($heading, 'imagine-site') . '</th>';
        }
        $html .= '</tr></thead><tbody>';
        foreach (self::liste() as $row) {
            $html .= '<tr><th scope="row"><code>' . esc_html($row['nom']) . '</code></th>';
            foreach (['origine', 'geste', 'duree', 'usage'] as $key) {
                $html .= '<td>' . esc_html__($row[$key], 'imagine-site') . '</td>';
            }
            $html .= '</tr>';
        }
        return $content . $html . '</tbody></table></div>';
    }
}
