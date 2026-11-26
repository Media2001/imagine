<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Préférences locales ; la synchronisation et la double confirmation restent non raccordées. */
final class Newsletters
{
    public const CATALOGUE = 'imagine_newsletters_catalogue';
    public const CREATION = 'imagine_newsletters_creation';
    public const META = 'imagine_newsletters_preferences';

    public static function register(): void
    {
        add_action('woocommerce_account_dashboard', [self::class, 'compte'], 30);
        add_action('admin_post_imagine_newsletters', [self::class, 'traiter']);
        add_action('admin_post_nopriv_imagine_newsletters', [self::class, 'traiter']);
        add_action('user_register', [self::class, 'creation'], 30);
        add_shortcode('imagine_newsletters', [self::class, 'page']);
    }

    public static function catalogue(): array
    {
        try {
            return NewslettersRegles::catalogue(get_option(self::CATALOGUE, []));
        } catch (\InvalidArgumentException) {
            return []; // Aucune inscription à une liste invalide.
        }
    }

    public static function admissible(int $id): bool
    {
        $u = get_userdata($id);
        return $u && is_email($u->user_email) && !str_ends_with(strtolower($u->user_email), '.invalid')
            && get_user_meta($id, SansEmail::META, true) !== '1';
    }

    public static function preferences(int $id): array
    {
        $value = get_user_meta($id, self::META, true);
        return is_array($value) ? $value : [];
    }

    public static function version(int $id): string
    {
        return hash('sha256', serialize([self::catalogue(), self::preferences($id)]));
    }

    public static function enregistrer(int $id, array $selected, string $version): void
    {
        if (!$id || $id !== get_current_user_id() || !self::admissible($id)) {
            throw new \RuntimeException('Compte refusé.');
        }
        global $wpdb;
        $lock = 'imagine_newsletters_' . $id;
        if ((int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 3)', $lock)) !== 1) {
            throw new \RuntimeException('Préférences occupées.');
        }
        try {
            wp_cache_delete($id, 'user_meta');
            if (!hash_equals(self::version($id), $version)) {
                throw new \RuntimeException('Formulaire périmé : rechargez vos préférences.');
            }
            $old = self::preferences($id);
            $new = NewslettersRegles::choisir(self::catalogue(), $old, $selected, gmdate('Y-m-d\TH:i:s\Z'), 'lecteur');
            if ($new !== $old) {
                if (!update_user_meta($id, self::META, $new) || self::preferences($id) !== $new) {
                    throw new \RuntimeException('Préférences non enregistrées.');
                }
                // Point d'accroche seulement : aucun abonné/transport n'est enregistré par ce lot.
                do_action('imagine_newsletters_preferences_modifiees', $id, $new, $old);
            }
        } finally {
            $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
        }
    }

    public static function creation(int $id): void
    {
        if (get_option(self::CREATION, 'non') !== 'oui' || !self::admissible($id)
            || metadata_exists('user', $id, self::META)) {
            return;
        }
        $main = array_column(array_filter(self::catalogue(), static fn ($r) => $r['principale']), 'id');
        if (!$main) {
            return;
        }
        $new = NewslettersRegles::choisir(self::catalogue(), [], $main, gmdate('Y-m-d\TH:i:s\Z'), 'defaut_creation');
        if (!add_user_meta($id, self::META, $new, true) || self::preferences($id) !== $new) {
            throw new \RuntimeException('Préférence initiale non enregistrée.');
        }
        // Ne signifie jamais consentement explicite ou double confirmation Brevo.
        do_action('imagine_newsletters_preferences_modifiees', $id, $new, []);
    }

    public static function url(): string
    {
        return wc_get_page_permalink('myaccount') . '#mes-newsletters';
    }

    public static function traiter(): void
    {
        nocache_headers();
        $id = get_current_user_id();
        $post = wp_unslash($_POST);
        if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST' || !$id
            || !isset($post['compte'], $post['_wpnonce'], $post['version'])
            || !is_scalar($post['compte']) || (string) $id !== (string) $post['compte']
            || !is_string($post['_wpnonce']) || !wp_verify_nonce($post['_wpnonce'], 'imagine_newsletters_' . $id)
            || !is_string($post['version']) || !is_array($post['choix'] ?? [])) {
            wp_die(esc_html__('Modification des newsletters refusée.', 'imagine-site'), '', ['response' => 403]);
        }
        try {
            $selected = $post['choix'] ?? [];
            foreach ($selected as $value) {
                if (!is_string($value)) {
                    throw new \InvalidArgumentException();
                }
            }
            self::enregistrer($id, $selected, $post['version']);
        } catch (\Throwable) {
            wp_die(esc_html__('Préférences non modifiées : rechargez le formulaire et réessayez.', 'imagine-site'), '', ['response' => 409]);
        }
        wp_safe_redirect(self::url(), 303);
        exit;
    }

    public static function compte(): void
    {
        $id = get_current_user_id();
        if (!$id) {
            return;
        }
        if (!self::admissible($id)) {
            echo '<p data-imagine-newsletters-sans-email>' . esc_html__(
                'Ce compte sans email ne propose pas de préférences de newsletters.', 'imagine-site'
            ) . '</p>';
            return;
        }
        echo '<section id="mes-newsletters"><h2>' . esc_html__('Mes newsletters', 'imagine-site') . '</h2><p>'
            . esc_html__('Vos choix restent sur ce site de démonstration. Aucun email ni confirmation ne sera envoyé.', 'imagine-site') . '</p>';
        $catalogue = self::catalogue();
        if (!$catalogue) {
            echo '<p>' . esc_html__('Aucune newsletter proposée pour le moment.', 'imagine-site') . '</p></section>';
            return;
        }
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field('imagine_newsletters_' . $id);
        echo '<input type="hidden" name="action" value="imagine_newsletters"><input type="hidden" name="compte" value="'
            . esc_attr((string) $id) . '"><input type="hidden" name="version" value="' . esc_attr(self::version($id)) . '">';
        $prefs = self::preferences($id);
        foreach ($catalogue as $row) {
            $state = $prefs[$row['id']] ?? null;
            echo '<p><label><input type="checkbox" name="choix[]" value="' . esc_attr($row['id']) . '"'
                . checked($state['choix'] ?? false, true, false) . '> ' . esc_html($row['titre']) . '</label><br>'
                . esc_html($row['presentation']) . '<br><small>';
            if ($state) {
                echo esc_html($state['choix'] ? __('Choisi', 'imagine-site') : __('Non choisi', 'imagine-site')) . ' — <time datetime="'
                    . esc_attr($state['date_utc']) . '">' . esc_html($state['date_utc']) . '</time>';
                if ($state['origine'] === 'defaut_creation') {
                    echo ' — ' . esc_html__('réglage à la création, pas un consentement explicite', 'imagine-site');
                }
            } else {
                echo esc_html__('Aucun choix enregistré.', 'imagine-site');
            }
            echo '</small></p>';
        }
        echo '<button type="submit">' . esc_html__('Enregistrer mes newsletters', 'imagine-site') . '</button></form></section>';
    }

    public static function page(): string
    {
        $html = '<div data-imagine-newsletters-catalogue>';
        foreach (self::catalogue() as $row) {
            $html .= '<section data-newsletter="' . esc_attr($row['id']) . '"><h2>' . esc_html($row['titre'])
                . '</h2><p>' . esc_html($row['presentation']) . '</p></section>';
        }
        if (is_user_logged_in()) {
            $html .= self::admissible(get_current_user_id()) ? '<p><a href="' . esc_url(self::url()) . '">'
                . esc_html__('Gérer mes newsletters', 'imagine-site') . '</a></p>' : '<p>'
                . esc_html__('Ce compte sans email ne propose pas de préférences de newsletters.', 'imagine-site') . '</p>';
        } else {
            $html .= '<aside id="imagine-newsletters-inscription-brevo"><h2>' . esc_html__('Inscription aux newsletters — à venir', 'imagine-site')
                . '</h2><p>' . esc_html__('Emplacement du futur formulaire Brevo et de sa double confirmation. Aucune inscription possible ici pour le moment.', 'imagine-site') . '</p></aside>';
        }
        return $html . '</div>';
    }
}
