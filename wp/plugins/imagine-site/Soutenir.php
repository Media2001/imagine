<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Deux réglages fermés ; jamais de traitement financier ni d'appel à CoopHub. */
final class Soutenir
{
    public const OPTION = 'imagine_soutenir';

    public static function configuration(): array
    {
        $value = get_option(self::OPTION, []);
        return ['don' => is_array($value) && ($value['don'] ?? false) === true,
            'parts_url' => is_array($value) && self::url($value['parts_url'] ?? null) ? $value['parts_url'] : ''];
    }

    private static function url(mixed $url): bool
    {
        return is_string($url) && ($url === '' || (filter_var($url, FILTER_VALIDATE_URL)
            && in_array(parse_url($url, PHP_URL_SCHEME), ['https', 'http'], true)
            && parse_url($url, PHP_URL_USER) === null && parse_url($url, PHP_URL_PASS) === null));
    }

    public static function nettoyer(mixed $value): array
    {
        if (!is_array($value) || !in_array($value['don'] ?? null, ['0', '1', false, true], true)
            || !self::url($value['parts_url'] ?? null)) {
            add_settings_error(self::OPTION, 'imagine_soutenir_invalide', __('Réglages invalides : valeurs conservées.', 'imagine-site'));
            return self::configuration();
        }
        return ['don' => in_array($value['don'], ['1', true], true), 'parts_url' => $value['parts_url']];
    }

    public static function rendre(): string
    {
        $config = self::configuration();
        $subscribe = get_page_by_path('s-abonner');
        $html = '<div id="imagine-soutenir"><section><h2>' . esc_html(__('abonnement', 'imagine-site')) . '</h2>';
        if ($subscribe) {
            $html .= '<p><a href="' . esc_url(get_permalink($subscribe->ID)) . '">' . esc_html(__("S'abonner", 'imagine-site')) . '</a></p>';
        }
        $html .= '</section>';
        if ($config['don']) {
            $html .= '<section><h2>' . esc_html(__('don ponctuel ou récurrent', 'imagine-site')) . '</h2><p>'
                . esc_html(__('Emplacement de démonstration, sans paiement.', 'imagine-site')) . '</p></section>';
        }
        $html .= '<section><h2>' . esc_html(__('bénévolat', 'imagine-site')) . '</h2></section><section><h2>';
        $label = esc_html(__('prise de parts', 'imagine-site'));
        $html .= $config['parts_url'] !== '' ? '<a href="' . esc_url($config['parts_url']) . '" rel="sponsored">' . $label . '</a>' : $label;
        return $html . '</h2></section></div>';
    }

    public static function champs(): string
    {
        $value = self::configuration();
        return '<h2>' . esc_html(__('Soutenir — démonstration sans paiement', 'imagine-site')) . '</h2>'
            . '<p><input type="hidden" name="imagine_soutenir[don]" value="0"><label><input type="checkbox" name="imagine_soutenir[don]" value="1"'
            . checked($value['don'], true, false) . '> ' . esc_html(__('Afficher l’emplacement don (sans paiement)', 'imagine-site')) . '</label></p>'
            . '<p><label>' . esc_html(__('Adresse de prise de parts (vide par défaut)', 'imagine-site'))
            . ' <input type="url" name="imagine_soutenir[parts_url]" value="' . esc_attr($value['parts_url']) . '"></label></p>';
    }

    public static function register(): void
    {
        add_action('admin_init', static function (): void {
            register_setting('imagine_soutenir', self::OPTION, ['type' => 'array', 'show_in_rest' => false, 'sanitize_callback' => [self::class, 'nettoyer']]);
        });
        add_action('admin_menu', static function (): void {
            add_options_page(__('Soutenir', 'imagine-site'), __('Soutenir', 'imagine-site'), 'manage_options', 'imagine-soutenir', static function (): void {
                if (!current_user_can('manage_options')) {
                    return;
                }
                echo '<div class="wrap"><form action="options.php" method="post">';
                settings_fields('imagine_soutenir');
                settings_errors(self::OPTION);
                echo self::champs();
                submit_button();
                echo '</form></div>';
            });
        });
    }
}
