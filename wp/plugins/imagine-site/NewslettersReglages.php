<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Même écran, groupe Settings API et journal C10 ; aucune bibliothèque close modifiée. */
final class NewslettersReglages
{
    private static bool $restoring = false;

    public static function register(): void
    {
        add_action('admin_init', static function (): void {
            register_setting('imagine_reglages', Newsletters::CATALOGUE, ['type' => 'array',
                'sanitize_callback' => [self::class, 'nettoyerCatalogue'], 'show_in_rest' => false]);
            register_setting('imagine_reglages', Newsletters::CREATION, ['type' => 'string',
                'sanitize_callback' => [self::class, 'nettoyerCreation'], 'show_in_rest' => false]);
        }, 40);
        add_action('admin_menu', static function (): void {
            global $wp_filter;
            $hook = get_plugin_page_hookname('imagine-reglages', 'imagine');
            foreach (($wp_filter[$hook]->callbacks ?? []) as $priority => $callbacks) {
                foreach ($callbacks as $callback) {
                    $fn = $callback['function'];
                    remove_action($hook, $fn, $priority);
                    add_action($hook, static function () use ($fn): void {
                        ob_start(); $fn(); $html = ob_get_clean();
                        $end = strpos($html, '</form>');
                        if ($end !== false && (str_contains($html, 'value="imagine_reglages"')
                            || str_contains($html, "value='imagine_reglages'"))) {
                            $html = substr_replace($html, self::champs(), $end, 0);
                        }
                        echo $html;
                    }, $priority);
                }
            }
        }, 140);
        add_action('updated_option', static fn ($key, $old, $new) => self::journal($key, $old, $new), 20, 3);
        add_action('added_option', static fn ($key, $new) => self::journal($key, null, $new), 20, 2);
    }

    public static function nettoyerCatalogue(mixed $value): array
    {
        if ($value === null) {
            return Newsletters::catalogue(); // Ancien formulaire : ne pas effacer.
        }
        try {
            if (!is_array($value)) {
                throw new \InvalidArgumentException();
            }
            $rows = [];
            foreach ($value as $row) {
                if (!is_array($row)) {
                    throw new \InvalidArgumentException();
                }
                if (($row['id'] ?? '') === '') {
                    continue; // Ligne vide = suppression explicite dans l'interface.
                }
                $row['principale'] = match ($row['principale'] ?? false) {
                    '1', true => true, '0', false => false,
                    default => throw new \InvalidArgumentException(),
                };
                $rows[] = $row;
            }
            return NewslettersRegles::catalogue($rows);
        } catch (\InvalidArgumentException) {
            add_settings_error(Newsletters::CATALOGUE, 'imagine_newsletters_catalogue_invalide',
                __('Catalogue invalide : valeur conservée. Identifiants uniques et une seule principale requis.', 'imagine-site'));
            return Newsletters::catalogue();
        }
    }

    public static function nettoyerCreation(mixed $value): string
    {
        if ($value === null) {
            return get_option(Newsletters::CREATION, 'non') === 'oui' ? 'oui' : 'non';
        }
        if (!in_array($value, ['non', 'oui'], true)) {
            add_settings_error(Newsletters::CREATION, 'imagine_newsletters_creation_invalide',
                __('Réglage invalide : inscription par défaut fermée.', 'imagine-site'));
            return 'non';
        }
        return $value;
    }

    public static function champs(): string
    {
        ob_start();
        echo '<h2>' . esc_html__('Newsletters', 'imagine-site') . '</h2><p>'
            . esc_html__('Données du catalogue. Pour ajouter une newsletter, remplir la dernière ligne puis enregistrer. Pour retirer une lettre, vider son identifiant. Ne pas réutiliser un identifiant pour une autre lettre.', 'imagine-site') . '</p>';
        echo '<table class="widefat" id="imagine-newsletters-reglages"><thead><tr>';
        foreach (['Identifiant stable', 'Intitulé', 'Présentation', 'Principale'] as $label) {
            echo '<th scope="col">' . esc_html__($label, 'imagine-site') . '</th>';
        }
        echo '</tr></thead><tbody>';
        $rows = Newsletters::catalogue();
        $rows[] = ['id' => '', 'titre' => '', 'presentation' => '', 'principale' => false];
        foreach ($rows as $i => $row) {
            echo '<tr>';
            foreach (['id', 'titre', 'presentation', 'principale'] as $key) {
                $name = Newsletters::CATALOGUE . '[' . $i . '][' . $key . ']';
                $id = 'imagine-newsletter-' . $i . '-' . $key;
                echo '<td><label class="screen-reader-text" for="' . esc_attr($id) . '">'
                    . esc_html($key . ' ' . ($i + 1)) . '</label>';
                if ($key === 'principale') {
                    echo '<select id="' . esc_attr($id) . '" name="' . esc_attr($name) . '">';
                    foreach (['0' => __('Non', 'imagine-site'), '1' => __('Oui', 'imagine-site')] as $v => $label) {
                        echo '<option value="' . esc_attr((string) $v) . '"' . selected((int) $row[$key], (int) $v, false)
                            . '>' . esc_html($label) . '</option>';
                    }
                    echo '</select>';
                } else {
                    echo '<input id="' . esc_attr($id) . '" name="' . esc_attr($name) . '" value="'
                        . esc_attr($row[$key]) . '" maxlength="' . ($key === 'id' ? '50' : ($key === 'titre' ? '150' : '500')) . '">';
                }
                echo '</td>';
            }
            echo '</tr>';
        }
        echo '</tbody></table><p><label for="imagine-newsletters-creation">'
            . esc_html__('Inscrire par défaut à la principale à la création du compte', 'imagine-site') . '</label> <select id="imagine-newsletters-creation" name="'
            . esc_attr(Newsletters::CREATION) . '">';
        foreach (['non' => __('Non — défaut prudent', 'imagine-site'), 'oui' => __('Oui — à confirmer par Imagine', 'imagine-site')] as $v => $label) {
            echo '<option value="' . esc_attr($v) . '"' . selected(get_option(Newsletters::CREATION, 'non'), $v, false) . '>' . esc_html($label) . '</option>';
        }
        echo '</select></p><p>' . esc_html__('Question pour Imagine : à la création du compte, souhaitez-vous cette inscription et avec quel consentement explicite ? Le réglage ne prouve aucun consentement et ne modifie pas les comptes existants. Aucun envoi ni raccord Brevo.', 'imagine-site') . '</p>';
        return ob_get_clean();
    }

    private static function journal(string $key, mixed $old, mixed $new): void
    {
        if (self::$restoring || $old === $new || !in_array($key, [Newsletters::CATALOGUE, Newsletters::CREATION], true)) {
            return;
        }
        $user = wp_get_current_user();
        $journal = \Imagine\Pilotage\Administration\Reglages::JOURNAL . str_replace('-', '', wp_generate_uuid4());
        $event = ['quand_utc' => gmdate('Y-m-d\TH:i:s\Z'), 'qui_id' => $user->ID,
            'qui_login' => $user->ID ? $user->user_login : 'systeme', 'option' => $key, 'avant' => $old, 'apres' => $new];
        if (add_option($journal, $event, '', false) && get_option($journal) === $event) {
            return;
        }
        self::$restoring = true;
        try {
            $old === null ? delete_option($key) : update_option($key, $old, false);
            if (get_option($key, null) !== $old) {
                wp_die(esc_html__('Restauration des newsletters impossible.', 'imagine-site'), '', ['response' => 500]);
            }
        } finally {
            self::$restoring = false;
        }
        add_settings_error($key, 'imagine_newsletters_journal', __('Journal indisponible : réglage inchangé.', 'imagine-site'));
    }
}
