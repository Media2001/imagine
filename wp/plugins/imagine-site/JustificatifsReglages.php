<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Extension C10 par hooks, même formulaire Settings API, pas de bibliothèque modifiée. */
final class JustificatifsReglages
{
    public const OPTION = 'imagine_solidaire_categories';
    private static bool $restoring = false;

    public static function categories(): array
    {
        return JustificatifRegles::categories(get_option(self::OPTION, ['à préciser']));
    }

    public static function nettoyer(mixed $value): array
    {
        if ($value === null) {
            return self::categories();
        }
        try {
            return JustificatifRegles::categories($value);
        } catch (\InvalidArgumentException) {
            add_settings_error(self::OPTION, 'imagine_categories_invalides', __('Catégories invalides : liste conservée.', 'imagine-site'));
            return self::categories();
        }
    }

    public static function register(): void
    {
        add_action('admin_init', static function (): void {
            register_setting('imagine_reglages', self::OPTION, ['type' => 'array',
                'sanitize_callback' => [self::class, 'nettoyer'], 'show_in_rest' => false]);
        }, 35);
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
                            $field = '<h2>' . esc_html__('Justificatifs du tarif solidaire', 'imagine-site') . '</h2><p><label for="imagine-solidaire-categories">'
                                . esc_html__('Catégories — une par ligne (à confirmer par Imagine)', 'imagine-site') . '</label></p><textarea id="imagine-solidaire-categories" name="'
                                . esc_attr(self::OPTION) . '" rows="4" cols="45">' . esc_textarea(implode("\n", self::categories())) . '</textarea><p>'
                                . esc_html__('Défaut : à préciser. Ce réglage ne change ni prix, ni abonnement, ni accès. Les décisions anciennes conservent leur catégorie.', 'imagine-site') . '</p>';
                            $html = substr_replace($html, $field, $end, 0);
                        }
                        echo $html;
                    }, $priority);
                }
            }
        }, 121);
        add_action('updated_option', static fn ($key, $old, $new) => self::journal($key, $old, $new), 20, 3);
        add_action('added_option', static fn ($key, $new) => self::journal($key, null, $new), 20, 2);
    }

    private static function journal(string $key, mixed $old, mixed $new): void
    {
        if ($key !== self::OPTION || self::$restoring || $old === $new) {
            return;
        }
        $u = wp_get_current_user();
        if (
            add_option(
                \Imagine\Pilotage\Administration\Reglages::JOURNAL . str_replace('-', '', wp_generate_uuid4()),
                ['quand_utc' => gmdate('Y-m-d\TH:i:s\Z'), 'qui_id' => $u->ID, 'qui_login' => $u->ID ? $u->user_login : 'systeme',
                'option' => $key,
                'avant' => $old,
                'apres' => $new],
                '',
                false
            )
        ) {
            return;
        }
        self::$restoring = true;
        try {
            $old === null ? delete_option($key) : update_option($key, $old, false);
            if (get_option($key, null) !== $old) {
                wp_die(esc_html__('Échec de restauration des catégories.', 'imagine-site'), '', ['response' => 500]);
            }
        } finally {
            self::$restoring = false;
        }
        add_settings_error($key, 'imagine_categories_journal', __('Journal indisponible : catégories inchangées.', 'imagine-site'));
    }
}
