<?php

declare(strict_types=1);

namespace Imagine\Site;

final class DomainesRefusesReglages
{
    private static bool $restoring = false;

    public static function register(): void
    {
        add_action('admin_init', static function (): void {
            register_setting('imagine_domaines_refuses', DomainesRefuses::OPTION, ['type' => 'array', 'show_in_rest' => false, 'sanitize_callback' => [self::class, 'nettoyer']]);
        });
        add_action('admin_menu', static function (): void {
            add_options_page(__('Adresses à l’inscription', 'imagine-site'), __('Adresses à l’inscription', 'imagine-site'), 'manage_options', 'imagine-domaines-refuses', [self::class, 'page']);
        });
        add_action('added_option', static fn ($key, $new) => self::journal($key, null, $new), 31, 2);
        add_action('updated_option', static fn ($key, $old, $new) => self::journal($key, $old, $new), 31, 3);
    }

    public static function nettoyer(mixed $value): array
    {
        if (self::$restoring) { return is_array($value) ? $value : []; }
        $valid = DomainesRefusesRegles::liste($value);
        if ($valid !== null) { return $valid; }
        add_settings_error(DomainesRefuses::OPTION, 'imagine_c31_liste', __('Liste de domaines invalide : ancienne liste conservée.', 'imagine-site'));
        return DomainesRefuses::configuration();
    }

    private static function journal(string $key, mixed $old, mixed $new): void
    {
        if (self::$restoring || $key !== DomainesRefuses::OPTION || $old === $new) { return; }
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
        add_settings_error($key, 'imagine_c31_journal', __('Journal indisponible : liste inchangée.', 'imagine-site'));
    }

    public static function page(): void
    {
        if (!current_user_can('manage_options')) { wp_die('', '', ['response' => 403]); }
        echo '<div class="wrap"><h1>' . esc_html__('Adresses à l’inscription', 'imagine-site') . '</h1><form method="post" action="options.php">';
        settings_fields('imagine_domaines_refuses');
        echo '<p><label for="imagine-c31-liste">' . esc_html__('Un domaine exact par ligne. Liste vide : aucune restriction. Sous-domaines non inclus, sauf ligne explicite. Liste tenue manuellement, aucun service externe.', 'imagine-site') . '</label></p>';
        echo '<textarea id="imagine-c31-liste" name="imagine_domaines_refuses" rows="8" cols="70">' . esc_textarea(implode("\n", DomainesRefuses::configuration())) . '</textarea>';
        submit_button();
        echo '</form></div>';
    }
}
