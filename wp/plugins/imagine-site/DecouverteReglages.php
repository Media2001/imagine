<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Extension de l'écran C10 par hooks ; aucun fichier de la bibliothèque close modifié. */
final class DecouverteReglages
{
    private static bool $restoring = false;

    public static function register(): void
    {
        add_action('admin_init', static function (): void {
            register_setting('imagine_reglages', Decouverte::OPTION, [
                'type' => 'array', 'sanitize_callback' => [self::class, 'nettoyer'], 'show_in_rest' => false,
            ]);
            register_setting('imagine_reglages', Decouverte::RELECTURE, [
                'type' => 'string', 'default' => 'fermee',
                'sanitize_callback' => [self::class, 'nettoyerRelecture'], 'show_in_rest' => false,
            ]);
        }, 30);
        add_action('admin_menu', static function (): void {
            global $wp_filter;
            $hook = get_plugin_page_hookname('imagine-reglages', 'imagine');
            // C10 ne propose pas do_settings_sections : envelopper son rendu uniquement,
            // sans remplacer sa logique, sa capacité, son formulaire ni son nonce natif.
            foreach (($wp_filter[$hook]->callbacks ?? []) as $priority => $callbacks) {
                foreach ($callbacks as $callback) {
                    $fn = $callback['function'];
                    if (is_array($fn) && $fn[0] instanceof \Imagine\Pilotage\Administration\Reglages && $fn[1] === 'page') {
                        remove_action($hook, $fn, $priority);
                        add_action($hook, static function () use ($fn): void {
                            ob_start();
                            $fn();
                            $html = ob_get_clean();
                            $start = strpos($html, '<h2>' . esc_html__('Accès', 'imagine-pilotage') . '</h2>');
                            $end = $start === false ? false : strpos($html, '</table>', $start);
                            if ($end !== false) {
                                $html = substr_replace($html, self::champs(), $end, 0);
                            }
                            echo $html;
                        }, $priority);
                    }
                }
            }
        }, 99);
        add_action('updated_option', static fn ($key, $old, $new) => self::journal($key, $old, $new), 20, 3);
        add_action('added_option', static fn ($key, $new) => self::journal($key, null, $new), 20, 2);
    }

    public static function nettoyer(mixed $value): array
    {
        $old = Decouverte::reglages();
        // Un ancien formulaire C10 sans ces champs ne les remet jamais à zéro.
        if ($value === null) {
            return $old;
        }
        if (is_array($value) && count($value) === 5
            && !array_diff(array_keys(Decouverte::defauts()), array_keys($value))) {
            foreach (['jours', 'nombre'] as $key) {
                if (is_string($value[$key]) && preg_match('/^[1-9][0-9]{0,2}$/D', $value[$key])) {
                    $value[$key] = (int) $value[$key];
                }
            }
            if (is_string($value['numeros'])) {
                $list = trim($value['numeros']);
                $value['numeros'] = $list === '' ? [] : array_map('trim', explode(',', $list));
            }
            if (Decouverte::valide($value)) {
                foreach ($value['numeros'] as $id) {
                    if (get_post_type((int) $id) !== 'imagine_numero') {
                        add_settings_error(Decouverte::OPTION, 'imagine_decouverte_numero', __('Numéro inconnu : découverte inchangée.', 'imagine-site'));
                        return $old;
                    }
                }
                return $value;
            }
        }
        add_settings_error(Decouverte::OPTION, 'imagine_decouverte_invalide', __('Réglage découverte invalide : ancienne valeur conservée.', 'imagine-site'));
        return $old;
    }

    public static function nettoyerRelecture(mixed $value): string
    {
        $old = get_option(Decouverte::RELECTURE, 'fermee');
        $old = in_array($old, ['fermee', 'rester_lisible'], true) ? $old : 'fermee';
        if ($value === null) {
            return $old; // Formulaire antérieur : aucune ouverture implicite.
        }
        if (in_array($value, ['fermee', 'rester_lisible'], true)) {
            return $value;
        }
        add_settings_error(Decouverte::RELECTURE, 'imagine_decouverte_relecture_invalide', __('Relecture invalide : ancienne valeur conservée.', 'imagine-site'));
        return $old;
    }

    private static function champs(): string
    {
        $values = Decouverte::reglages();
        $fields = [
            'ouverture' => [__('Découverte — ouverture', 'imagine-site'), ['fermee' => __('Fermée (défaut)', 'imagine-site'),
                'premiere_lecture' => __('Première lecture admissible d’un compte vérifié', 'imagine-site')]],
            'forme' => [__('Découverte — forme', 'imagine-site'), ['articles' => __('Nombre d’articles', 'imagine-site'), 'duree' => __('Durée', 'imagine-site')]],
            'jours' => [__('Découverte — durée (1 à 365 jours)', 'imagine-site'), null],
            'nombre' => [__('Découverte — nombre (1 à 100 articles)', 'imagine-site'), null],
            'numeros' => [__('Découverte — périmètre : identifiants des numéros séparés par des virgules', 'imagine-site'), null],
        ];
        ob_start();
        foreach ($fields as $key => [$label, $choices]) {
            $id = 'imagine-decouverte-' . $key;
            $attrs = ' id="' . esc_attr($id) . '" name="' . esc_attr(Decouverte::OPTION . '[' . $key . ']') . '" aria-describedby="' . esc_attr($id . '-aide') . '"';
            echo '<tr class="imagine-reglage imagine-decouverte"><th scope="row"><label for="' . esc_attr($id) . '">' . esc_html($label) . '</label></th><td>';
            if ($choices) {
                echo '<select' . $attrs . '>';
                foreach ($choices as $value => $text) {
                    echo '<option value="' . esc_attr($value) . '"' . selected($values[$key], $value, false) . '>' . esc_html($text) . '</option>';
                }
                echo '</select>';
            } else {
                echo '<input type="' . ($key === 'numeros' ? 'text' : 'number') . '"' . $attrs
                    . ($key === 'numeros' ? '' : ' min="1" max="' . ($key === 'jours' ? '365' : '100') . '" step="1"')
                    . ' value="' . esc_attr($key === 'numeros' ? implode(',', $values[$key]) : (string) $values[$key]) . '">';
            }
            echo '<p class="description" id="' . esc_attr($id . '-aide') . '"><strong>' . esc_html__('À confirmer par Imagine', 'imagine-site') . '</strong><br>'
                . esc_html__('Défaut : fermée, 2 articles ou 7 jours, aucun numéro. Articles seulement, jamais de PDF. Les paramètres sont figés à l’ouverture du compte ; les modifier ne recrédite pas les comptes déjà ouverts. Fermer suspend tous les accès découverte. Vérification email fictive sur la démo.', 'imagine-site') . '</p></td></tr>';
        }
        echo '<tr class="imagine-reglage imagine-decouverte"><th scope="row"><label for="imagine-decouverte-relecture">'
            . esc_html__('Découverte — relecture après quota', 'imagine-site') . '</label></th><td>';
        echo '<select id="imagine-decouverte-relecture" name="' . esc_attr(Decouverte::RELECTURE) . '" aria-describedby="imagine-decouverte-relecture-aide">';
        foreach (['fermee' => __('Se refermer (défaut prudent)', 'imagine-site'), 'rester_lisible' => __('Rester lisible pour les articles déjà ouverts', 'imagine-site')] as $value => $label) {
            echo '<option value="' . esc_attr($value) . '"' . selected(get_option(Decouverte::RELECTURE, 'fermee'), $value, false) . '>' . esc_html($label) . '</option>';
        }
        echo '</select><p class="description" id="imagine-decouverte-relecture-aide"><strong>'
            . esc_html__('À confirmer par Imagine', 'imagine-site') . '</strong><br>'
            . esc_html__('Question ouverte : choix courant prudent fermé, pas une contrainte du moteur C06. Ce réglage courant agit aussi sur les comptes déjà ouverts, sans recrédit. Désignation éditoriale et périmètres initial/courant restent requis ; aucun nouveau texte ni PDF. La fin du mode durée reste exclue.', 'imagine-site')
            . '</p></td></tr>';
        return ob_get_clean();
    }

    /** Même journal visible C10, après persistance ; refus si l'audit ne peut être écrit. */
    private static function journal(string $key, mixed $old, mixed $new): void
    {
        if (self::$restoring || !in_array($key, [Decouverte::OPTION, Decouverte::RELECTURE], true) || $old === $new) {
            return;
        }
        $user = wp_get_current_user();
        if (add_option(\Imagine\Pilotage\Administration\Reglages::JOURNAL . str_replace('-', '', wp_generate_uuid4()), [
            'quand_utc' => gmdate('Y-m-d\TH:i:s\Z'), 'qui_id' => $user->ID,
            'qui_login' => $user->ID ? $user->user_login : 'systeme', 'option' => $key,
            'avant' => $old, 'apres' => $new,
        ], '', false)) {
            return;
        }
        self::$restoring = true;
        try {
            $old === null ? delete_option($key) : update_option($key, $old);
            if (get_option($key, null) !== $old) {
                wp_die(esc_html__('Échec de restauration découverte : vérifier le réglage.', 'imagine-site'), '', ['response' => 500]);
            }
        } finally {
            self::$restoring = false;
        }
        add_settings_error($key, 'imagine_decouverte_journal', __('Journal indisponible : découverte inchangée.', 'imagine-site'));
    }
}
