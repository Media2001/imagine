<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Raccord B07 natif : aucun billet, transport, quota ou droit de lecture. */
final class Agenda
{
    public const INSCRIPTION = 'imagine_inscription';
    public const TYPES = ['sortie' => 'Sortie de numéro', 'rencontre' => 'Rencontre gratuite', 'partenaire' => 'Événement partenaire'];

    public static function register(): void
    {
        add_action('init', [self::class, 'types']);
        add_action('admin_post_imagine_agenda', [self::class, 'recevoir']);
        add_action('admin_post_nopriv_imagine_agenda', [self::class, 'recevoir']);
        add_action('add_meta_boxes', [self::class, 'boites']);
        add_action('save_post_imagine_evenement', [self::class, 'sauver'], 10, 2);
    }

    public static function types(): void
    {
        register_post_type(self::INSCRIPTION, [
            'label' => __('Inscriptions aux événements', 'imagine-site'), 'public' => false,
            'publicly_queryable' => false, 'exclude_from_search' => true, 'show_in_rest' => false,
            'show_ui' => true, 'show_in_menu' => 'edit.php?post_type=imagine_evenement', 'can_export' => false,
            'supports' => [], 'map_meta_cap' => false, 'rewrite' => false, 'query_var' => false,
            'capabilities' => array_fill_keys(['edit_post', 'read_post', 'delete_post', 'edit_posts', 'edit_others_posts',
                'publish_posts', 'read_private_posts', 'delete_posts', 'delete_private_posts', 'delete_published_posts',
                'delete_others_posts', 'edit_private_posts', 'edit_published_posts'], 'manage_options') + ['create_posts' => 'do_not_allow'],
        ]);
        foreach (['imagine_type', 'imagine_date', 'imagine_heure', 'imagine_lieu', 'imagine_url_partenaire'] as $key) {
            register_post_meta('imagine_evenement', $key, [
                'type' => 'string', 'single' => true, 'show_in_rest' => true,
                'sanitize_callback' => $key === 'imagine_url_partenaire' ? 'esc_url_raw' : 'sanitize_text_field',
                'auth_callback' => static fn ($allowed, $meta, $id) => current_user_can('edit_post', (int)$id),
            ]);
        }
    }

    public static function evenement(int $id): ?array
    {
        $p = get_post($id);
        if (!$p || $p->post_type !== 'imagine_evenement' || $p->post_status !== 'publish' || $p->post_password !== '') {
            return null;
        }
        $type = (string)get_post_meta($id, 'imagine_type', true);
        $raw = get_post_meta($id, 'imagine_date', true) . ' ' . get_post_meta($id, 'imagine_heure', true);
        $date = \DateTimeImmutable::createFromFormat('!Y-m-d H:i', $raw, wp_timezone());
        if (!isset(self::TYPES[$type]) || !$date || $date->format('Y-m-d H:i') !== $raw) {
            return null;
        }
        return ['id' => $id, 'type' => $type, 'debut' => $date->getTimestamp(), 'iso' => $date->format(DATE_ATOM),
            'date' => $raw, 'lieu' => (string)get_post_meta($id, 'imagine_lieu', true),
            'url' => (string)get_post_meta($id, 'imagine_url_partenaire', true),
            'nom' => $p->post_title, 'description' => trim(wp_strip_all_tags($p->post_content))];
    }

    public static function ouvert(int $id): bool
    {
        $e = self::evenement($id);
        return $e !== null && AgendaRegles::inscription($e['type'], $e['debut'], time());
    }

    public static function groupes(): array
    {
        $groups = ['futurs' => [], 'passes' => []];
        foreach (get_posts(['post_type' => 'imagine_evenement', 'post_status' => 'publish', 'numberposts' => -1]) as $p) {
            $e = self::evenement($p->ID);
            if ($e) { $groups[$e['debut'] > time() ? 'futurs' : 'passes'][] = $e; }
        }
        foreach ($groups as &$rows) {
            usort($rows, static fn ($a, $b) => [$a['debut'], $a['id']] <=> [$b['debut'], $b['id']]);
        }
        return $groups;
    }

    /** Une projection par rendu : ne jamais réexécuter un shortcode pour le JSON-LD. */
    public static function projection(int $id): array
    {
        $post = get_post($id);
        $html = $post ? str_replace(']]>', ']]&gt;', apply_filters('the_content', get_the_content(null, false, $post))) : '';
        return ['html' => $html, 'description' => trim(html_entity_decode(wp_strip_all_tags($html), ENT_QUOTES | ENT_HTML5, 'UTF-8'))];
    }

    public static function schema(int $id, ?array $projection = null): array
    {
        $e = self::evenement($id);
        if (!$e) { return []; }
        $projection ??= self::projection($id);
        return ['@context' => 'https://schema.org', '@type' => 'Event', 'name' => $e['nom'],
            'startDate' => $e['iso'], 'location' => ['@type' => 'Place', 'name' => $e['lieu']],
            'description' => $projection['description'], 'url' => get_permalink($id)];
    }

    /** Même résultat et même redirection pour une création et son rejeu. */
    public static function inscrire(int $id, string $nom, string $email, bool $consentement): bool
    {
        $email = AgendaRegles::email($email);
        $nom = sanitize_text_field($nom);
        if (!self::ouvert($id) || !$nom || mb_strlen($nom) > 200 || !is_email($email) || strlen($email) > 254) {
            return false;
        }
        global $wpdb;
        $lock = AgendaRegles::cle($id, $email);
        if ((int)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 3)', $lock)) !== 1) { return false; }
        try {
            // Relire après l'attente : un événement peut avoir commencé entre-temps.
            if (!self::ouvert($id)) { return false; }
            $ids = self::inscriptions($email, $id);
            if ($ids === null) { return false; }
            if ($ids) { return true; }
            $new = wp_insert_post(['post_type' => self::INSCRIPTION, 'post_status' => 'private',
                'post_title' => sprintf(__('Inscription — événement %d', 'imagine-site'), $id),
                'post_parent' => $id, 'post_author' => 0,
                'meta_input' => ['imagine_agenda_email' => $email, 'imagine_agenda_nom' => $nom,
                    'imagine_agenda_consentement' => $consentement ? '1' : '0',
                    'imagine_agenda_date' => gmdate(DATE_ATOM)]], true);
            if (is_wp_error($new) || !$new) { return false; }
            if (get_post_meta($new, 'imagine_agenda_email', true) !== $email
                || get_post_meta($new, 'imagine_agenda_nom', true) !== $nom
                || get_post_meta($new, 'imagine_agenda_consentement', true) !== ($consentement ? '1' : '0')) {
                wp_delete_post($new, true);
                return false;
            }
            return true;
        } finally {
            $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
        }
    }

    /** null signifie échec de lecture, jamais une liste vide. */
    public static function inscriptions(string $email, int $evenement = 0): ?array
    {
        global $wpdb;
        $sql = "SELECT DISTINCT p.ID FROM {$wpdb->posts} p INNER JOIN {$wpdb->postmeta} m ON m.post_id=p.ID"
            . " WHERE p.post_type=%s AND m.meta_key='imagine_agenda_email' AND m.meta_value=%s";
        $args = [self::INSCRIPTION, AgendaRegles::email($email)];
        if ($evenement) { $sql .= ' AND p.post_parent=%d'; $args[] = $evenement; }
        $sql .= ' ORDER BY p.ID';
        $ids = $wpdb->get_col($wpdb->prepare($sql, ...$args));
        return $wpdb->last_error !== '' ? null : array_map('intval', $ids);
    }

    public static function recevoir(): void
    {
        nocache_headers();
        $id = isset($_POST['evenement']) && is_scalar($_POST['evenement']) ? absint($_POST['evenement']) : 0;
        $nonce = $_POST['imagine_agenda_nonce'] ?? '';
        if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !is_string($nonce) || !wp_verify_nonce($nonce, 'imagine_agenda_' . $id)) {
            wp_die(esc_html__('Demande refusée.', 'imagine-site'), '', ['response' => 403]);
        }
        $nom = $_POST['nom'] ?? ''; $email = $_POST['email'] ?? '';
        if (!is_string($nom) || !is_string($email) || !self::inscrire($id, wp_unslash($nom), wp_unslash($email), ($_POST['consentement'] ?? '') === '1')) {
            wp_die(esc_html__('Inscription indisponible ou données invalides.', 'imagine-site'), '', ['response' => 400]);
        }
        wp_safe_redirect(add_query_arg('inscription', 'enregistree', get_permalink($id)), 303);
        exit;
    }

    public static function formulaire(int $id): void
    {
        if (!self::ouvert($id)) { return; }
        if (($_GET['inscription'] ?? '') === 'enregistree') {
            echo '<p role="status">' . esc_html__('Votre demande a été enregistrée. Aucun email n’est envoyé.', 'imagine-site') . '</p>';
        }
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" id="imagine-agenda-inscription">';
        echo '<input type="hidden" name="action" value="imagine_agenda"><input type="hidden" name="evenement" value="' . esc_attr((string)$id) . '">';
        wp_nonce_field('imagine_agenda_' . $id, 'imagine_agenda_nonce');
        echo '<p><label>' . esc_html__('Nom', 'imagine-site') . ' <input name="nom" required maxlength="200" autocomplete="name"></label></p>';
        echo '<p><label>' . esc_html__('Adresse email', 'imagine-site') . ' <input type="email" name="email" required maxlength="254" autocomplete="email"></label></p>';
        echo '<p><label><input type="checkbox" name="consentement" value="1"> ' . esc_html__('J’accepte d’être recontacté au sujet de cet événement.', 'imagine-site') . '</label></p>';
        echo '<p>' . esc_html__('Nom et email sont conservés pour cette inscription, sans création de compte ni inscription à une newsletter.', 'imagine-site') . ' <a href="' . esc_url(get_privacy_policy_url()) . '">' . esc_html__('Confidentialité', 'imagine-site') . '</a></p>';
        echo '<button type="submit">' . esc_html__('M’inscrire gratuitement', 'imagine-site') . '</button></form>';
    }

    public static function boites(): void
    {
        add_meta_box('imagine-agenda-champs', __('Événement', 'imagine-site'), static function ($post): void {
            wp_nonce_field('imagine_agenda_champs', 'imagine_agenda_champs_nonce');
            echo '<p><label>' . esc_html__('Type', 'imagine-site') . ' <select name="imagine_type">';
            foreach (self::TYPES as $value => $label) {
                echo '<option value="' . esc_attr($value) . '"' . selected(get_post_meta($post->ID, 'imagine_type', true), $value, false) . '>' . esc_html__($label, 'imagine-site') . '</option>';
            }
            echo '</select></label></p>';
            foreach (['imagine_date' => ['Date', 'date'], 'imagine_heure' => ['Heure locale du site', 'time'], 'imagine_lieu' => ['Lieu', 'text'], 'imagine_url_partenaire' => ['Lien du partenaire', 'url']] as $key => [$label, $type]) {
                echo '<p><label>' . esc_html__($label, 'imagine-site') . ' <input type="' . esc_attr($type) . '" name="' . esc_attr($key) . '" value="' . esc_attr((string)get_post_meta($post->ID, $key, true)) . '"></label></p>';
            }
        }, 'imagine_evenement');
        add_meta_box('imagine-agenda-personne', __('Inscription enregistrée', 'imagine-site'), static function ($post): void {
            if (!current_user_can('manage_options')) { return; }
            echo '<dl id="imagine-agenda-admin">';
            foreach (['imagine_agenda_nom' => 'Nom', 'imagine_agenda_email' => 'Adresse email', 'imagine_agenda_consentement' => 'Consentement à être recontacté (1 = oui, 0 = non)', 'imagine_agenda_date' => 'Date UTC'] as $key => $label) {
                echo '<dt>' . esc_html__($label, 'imagine-site') . '</dt><dd>' . esc_html((string)get_post_meta($post->ID, $key, true)) . '</dd>';
            }
            echo '<dt>' . esc_html__('Événement', 'imagine-site') . '</dt><dd>' . esc_html(get_the_title($post->post_parent)) . '</dd></dl>';
        }, self::INSCRIPTION);
    }

    public static function sauver(int $id, \WP_Post $post): void
    {
        $nonce = $_POST['imagine_agenda_champs_nonce'] ?? '';
        if (wp_is_post_revision($id) || (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) || !current_user_can('edit_post', $id)
            || !is_string($nonce) || !wp_verify_nonce($nonce, 'imagine_agenda_champs')) { return; }
        foreach (['imagine_type', 'imagine_date', 'imagine_heure', 'imagine_lieu', 'imagine_url_partenaire'] as $key) {
            if (isset($_POST[$key]) && is_string($_POST[$key])) {
                $value = wp_unslash($_POST[$key]);
                update_post_meta($id, $key, $key === 'imagine_url_partenaire' ? esc_url_raw($value, ['http', 'https']) : sanitize_text_field($value));
            }
        }
    }
}
