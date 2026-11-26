<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Réglage additif C10 ; réserves sans identité conservées à l'effacement. */
final class PersonnalisationReglages
{
    private static bool $restoring = false;
    private static ?array $preimage = null;

    public static function register(): void
    {
        add_action('admin_init', static function (): void {
            register_setting('imagine_reglages', Personnalisation::CATALOGUE, ['type' => 'array',
                'sanitize_callback' => [self::class, 'nettoyer'], 'show_in_rest' => false]);
        }, 45);
        add_action('admin_menu', static function (): void {
            global $wp_filter;
            $hook = get_plugin_page_hookname('imagine-reglages', 'imagine');
            foreach (($wp_filter[$hook]->callbacks ?? []) as $priority => $callbacks) {
                foreach ($callbacks as $callback) {
                    $fn = $callback['function']; remove_action($hook, $fn, $priority);
                    add_action($hook, static function () use ($fn): void {
                        ob_start(); $fn(); $html = ob_get_clean(); $end = strpos($html, '</form>');
                        if ($end !== false && (str_contains($html, 'value="imagine_reglages"')
                            || str_contains($html, "value='imagine_reglages'"))) {
                            $html = substr_replace($html, self::champs(), $end, 0);
                        }
                        echo $html;
                    }, $priority);
                }
            }
        }, 145);
        add_action('delete_user_meta', static function ($metaIds, $id, $key): void {
            if ($key === Personnalisation::META) {
                foreach (get_user_meta((int)$id, $key, false) as $answers) { self::reserverReponses($answers); }
            }
        }, 10, 3);
        add_action('updated_option', static fn ($key, $old, $new) => self::journal($key, $old, $new), 25, 3);
        add_action('added_option', static fn ($key, $new) => self::journal($key, null, $new), 25, 2);
    }

    public static function nettoyer(mixed $value): array
    {
        // Seule l'inverse interne de cette préimage vérifiée évite les réserves.
        if (self::$restoring && self::$preimage !== null && $value === self::$preimage) {
            return self::$preimage;
        }
        if ($value === null) { return Personnalisation::catalogue(); }
        try {
            if (!is_array($value)) { throw new \InvalidArgumentException(); }
            $rows = [];
            foreach ($value as $row) {
                if (!is_array($row)) { throw new \InvalidArgumentException(); }
                if (($row['id'] ?? '') === '') { continue; }
                $row['multiple'] = match ($row['multiple'] ?? false) {
                    '1', true => true, '0', false => false, default => throw new \InvalidArgumentException(),
                };
                if (is_string($row['choix'] ?? null)) {
                    $row['choix'] = json_decode($row['choix'], true, 32, JSON_THROW_ON_ERROR);
                }
                $rows[] = $row;
            }
            $rows = PersonnalisationRegles::catalogue($rows);
            $current = Personnalisation::catalogue();
            self::reserver($current);
            global $wpdb;
            $values = $wpdb->get_col($wpdb->prepare("SELECT meta_value FROM {$wpdb->usermeta} WHERE meta_key=%s", Personnalisation::META));
            if ($wpdb->last_error) { throw new \InvalidArgumentException('Historique indisponible.'); }
            foreach ($values as $v) { self::reserverReponses(maybe_unserialize($v)); }
            $events = $wpdb->get_col($wpdb->prepare("SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE %s",
                $wpdb->esc_like(\Imagine\Pilotage\Administration\Reglages::JOURNAL) . '%'));
            if ($wpdb->last_error) { throw new \InvalidArgumentException('Journal indisponible.'); }
            foreach ($events as $v) {
                $event = maybe_unserialize($v);
                if (is_array($event) && ($event['option'] ?? '') === Personnalisation::CATALOGUE) {
                    foreach (['avant', 'apres'] as $side) { self::reserver(PersonnalisationRegles::catalogue($event[$side] ?? [])); }
                }
            }
            $questions = array_column($current, 'id'); $choices = [];
            foreach ($current as $row) { foreach ($row['choix'] as $c) { $choices[$c['id']] = $row['id']; } }
            foreach ($rows as $row) {
                if (!in_array($row['id'], $questions, true) && get_option(self::cle('q', $row['id']), false)) {
                    throw new \InvalidArgumentException('Question réservée.');
                }
                foreach ($row['choix'] as $c) {
                    if (($choices[$c['id']] ?? null) !== $row['id'] && get_option(self::cle('c', $c['id']), false)) {
                        throw new \InvalidArgumentException('Choix réservé.');
                    }
                }
            }
            return $rows;
        } catch (\InvalidArgumentException | \JsonException) {
            add_settings_error(Personnalisation::CATALOGUE, 'imagine_personnalisation_invalide',
                __('Questions invalides : valeur conservée. Choix fermés et identifiants uniques, jamais réutilisés après retrait.', 'imagine-site'));
            return Personnalisation::catalogue();
        }
    }

    public static function reserverReponses(mixed $answers): void
    {
        if (!is_array($answers)) { throw new \InvalidArgumentException('Historique invalide.'); }
        foreach ($answers as $qid => $answer) {
            if (!PersonnalisationRegles::id($qid) || !is_array($answer) || !is_array($answer['choix'] ?? null)) {
                throw new \InvalidArgumentException('Historique invalide.');
            }
            self::marquer('q', $qid);
            foreach ($answer['choix'] as $cid) {
                if (!PersonnalisationRegles::id($cid)) { throw new \InvalidArgumentException('Choix historique invalide.'); }
                self::marquer('c', $cid);
            }
        }
    }

    private static function cle(string $kind, string $id): string { return 'imagine_personnalisation_reserve_' . $kind . '_' . $id; }

    private static function marquer(string $kind, string $id): void
    {
        $key = self::cle($kind, $id);
        if (!get_option($key, false) && !add_option($key, '1', '', false) && !get_option($key, false)) {
            throw new \InvalidArgumentException('Réservation indisponible.');
        }
    }

    private static function reserver(array $rows): void
    {
        foreach ($rows as $row) {
            self::marquer('q', $row['id']);
            foreach ($row['choix'] as $choice) { self::marquer('c', $choice['id']); }
        }
    }

    private static function journal(string $key, mixed $old, mixed $new): void
    {
        if (self::$restoring || $old === $new || $key !== Personnalisation::CATALOGUE) { return; }
        $user = wp_get_current_user();
        $name = \Imagine\Pilotage\Administration\Reglages::JOURNAL . str_replace('-', '', wp_generate_uuid4());
        $event = ['quand_utc' => gmdate('Y-m-d\TH:i:s\Z'), 'qui_id' => $user->ID,
            'qui_login' => $user->ID ? $user->user_login : 'systeme', 'option' => $key, 'avant' => $old, 'apres' => $new];
        try {
            self::reserver(PersonnalisationRegles::catalogue($old ?? []));
            self::reserver(PersonnalisationRegles::catalogue($new));
            if (add_option($name, $event, '', false) && get_option($name) === $event) { return; }
        } catch (\InvalidArgumentException) { /* La configuration n'est pas utilisable sans réserve. */ }
        self::$preimage = $old === null ? null : PersonnalisationRegles::catalogue($old);
        if (self::$preimage !== $old) {
            wp_die(esc_html__('Préimage de personnalisation invalide.', 'imagine-site'), '', ['response' => 500]);
        }
        self::$restoring = true;
        try {
            $old === null ? delete_option($key) : update_option($key, $old, false);
            if (get_option($key, null) !== $old) {
                wp_die(esc_html__('Restauration de la personnalisation impossible.', 'imagine-site'), '', ['response' => 500]);
            }
        } finally { self::$restoring = false; self::$preimage = null; }
        add_settings_error($key, 'imagine_personnalisation_journal', __('Journal ou réserve indisponible : réglage inchangé.', 'imagine-site'));
    }

    public static function champs(): string
    {
        ob_start();
        echo '<section id="imagine-personnalisation-reglages"><h2>' . esc_html__('Questions de personnalisation', 'imagine-site') . '</h2><p>'
            . esc_html__('Questions fictives, facultatives. Identifiants stables : jamais réutilisables après retrait. Pour ajouter une question, remplir la dernière ligne ; pour retirer, vider son identifiant. Les choix sont une liste JSON d’objets id et titre, sans champ libre pour le lecteur.', 'imagine-site') . '</p>';
        $rows = Personnalisation::catalogue(); $rows[] = ['id' => '', 'titre' => '', 'multiple' => false, 'choix' => []];
        foreach ($rows as $i => $row) {
            echo '<fieldset><legend>' . esc_html(sprintf(__('Question %d', 'imagine-site'), $i + 1)) . '</legend>';
            foreach (['id' => __('Identifiant', 'imagine-site'), 'titre' => __('Intitulé', 'imagine-site'),
                'multiple' => __('Plusieurs choix possibles', 'imagine-site'), 'choix' => __('Choix fermés (JSON)', 'imagine-site')] as $key => $label) {
                $id = 'imagine-personnalisation-' . $i . '-' . $key;
                $name = Personnalisation::CATALOGUE . '[' . $i . '][' . $key . ']';
                echo '<p><label for="' . esc_attr($id) . '">' . esc_html($label) . '</label> ';
                if ($key === 'multiple') {
                    echo '<select id="' . esc_attr($id) . '" name="' . esc_attr($name) . '">';
                    foreach (['0' => __('Non', 'imagine-site'), '1' => __('Oui', 'imagine-site')] as $v => $text) {
                        echo '<option value="' . esc_attr((string)$v) . '"' . selected((int)$row[$key], (int)$v, false) . '>' . esc_html($text) . '</option>';
                    }
                    echo '</select>';
                } elseif ($key === 'choix') {
                    echo '<textarea id="' . esc_attr($id) . '" name="' . esc_attr($name) . '" rows="3" cols="65">'
                        . esc_textarea(wp_json_encode($row[$key], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)) . '</textarea>';
                } else {
                    echo '<input id="' . esc_attr($id) . '" name="' . esc_attr($name) . '" value="' . esc_attr($row[$key]) . '" maxlength="' . ($key === 'id' ? '50' : '150') . '">';
                }
                echo '</p>';
            }
            echo '</fieldset>';
        }
        echo '</section>'; return ob_get_clean();
    }
}
