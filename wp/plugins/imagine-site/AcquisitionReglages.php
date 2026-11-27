<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Section C10 additive, à la même place que C22/C24/C25 en attente du choix visuel. */
final class AcquisitionReglages
{
    private static bool $restoring = false;
    private static mixed $preimage = null;

    public static function register(): void
    {
        add_action('added_option', static fn ($key, $new) => self::journal($key, null, $new), 27, 2);
        add_action('updated_option', static fn ($key, $old, $new) => self::journal($key, $old, $new), 27, 3);
        add_action('admin_init', static function (): void {
            register_setting('imagine_reglages', Acquisition::OPTION, ['type' => 'array', 'show_in_rest' => false,
                'sanitize_callback' => [self::class, 'nettoyer']]);
        }, 55);
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
                            $html = substr_replace($html, self::champs(), $end, 0);
                        }
                        echo $html;
                    }, $priority);
                }
            }
        }, 155);
    }

    public static function nettoyer(mixed $value): array
    {
        if (self::$restoring && $value === self::$preimage) {
            return self::$preimage;
        }
        if (is_string($value)) {
            $rows = [];
            foreach (preg_split('/\r\n|\n|\r/', $value) as $line) {
                if (trim($line) === '') {
                    continue;
                }
                $parts = explode('|', $line, 2);
                if (count($parts) !== 2 || isset($rows[$parts[0]])) {
                    $rows = null;
                    break;
                }
                $rows[$parts[0]] = $parts[1];
            }
            $value = $rows;
        }
        $valid = AcquisitionRegles::liste($value);
        if ($valid !== null) {
            return $valid;
        }
        add_settings_error(Acquisition::OPTION, 'imagine_acquisition_liste', __('Liste invalide : valeur précédente conservée.', 'imagine-site'));
        return Acquisition::configuration();
    }

    private static function journal(string $key, mixed $old, mixed $new): void
    {
        if (self::$restoring || $key !== Acquisition::OPTION || $old === $new) {
            return;
        }
        $user = wp_get_current_user();
        $name = 'imagine_reglages_journal_' . str_replace('-', '', wp_generate_uuid4());
        $event = ['quand_utc' => gmdate('Y-m-d\TH:i:s\Z'), 'qui_id' => $user->ID,
            'qui_login' => $user->ID ? $user->user_login : 'systeme', 'option' => $key, 'avant' => $old, 'apres' => $new];
        if (add_option($name, $event, '', false) && get_option($name) === $event) {
            return;
        }
        self::$restoring = true;
        self::$preimage = $old;
        try {
            $old === null ? delete_option($key) : update_option($key, $old, false);
            if (get_option($key, null) !== $old) {
                wp_die(esc_html__('Journal et restauration indisponibles.', 'imagine-site'), '', ['response' => 500]);
            }
        } finally {
            self::$restoring = false;
            self::$preimage = null;
        }
        add_settings_error($key, 'imagine_acquisition_journal', __('Journal indisponible : liste inchangée.', 'imagine-site'));
    }

    public static function champs(): string
    {
        $lines = [];
        foreach (Acquisition::configuration() as $key => $label) {
            $lines[] = $key . '|' . $label;
        }
        return '<section id="imagine-acquisition-reglages"><h2>' . esc_html__('Comment nous avez-vous connus ?', 'imagine-site') . '</h2><p>'
            . esc_html__('Une réponse par ligne : identifiant|libellé. 20 choix maximum, identifiants de 1 à 40 caractères (lettres minuscules, chiffres, tirets), libellés de 80 caractères maximum. Liste vide : aucune question. Démonstration fictive uniquement.', 'imagine-site')
            . '</p><p><label for="imagine-acquisition-liste">' . esc_html__('Réponses fermées après paiement', 'imagine-site')
            . '</label><br><textarea id="imagine-acquisition-liste" name="imagine_acquisition_choix" rows="5" cols="65">'
            . esc_textarea(implode("\n", $lines)) . '</textarea></p></section>';
    }
}
