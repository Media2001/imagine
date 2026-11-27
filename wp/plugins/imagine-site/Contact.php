<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Proposition locale privée, jamais envoyée ni rapprochée d'un compte au dépôt. */
final class Contact
{
    public const TYPE = 'imagine_contact';
    public const CHAMPS = ['nom' => 'Nom', 'email' => 'Adresse email', 'texte' => 'Message',
        'consentement' => 'Consentement au recontact (1 = oui, 0 = non)', 'date' => 'Date UTC'];

    public static function register(): void
    {
        add_action('init', [self::class, 'types']);
        add_action('admin_post_imagine_contact', [self::class, 'recevoir']);
        add_action('admin_post_nopriv_imagine_contact', [self::class, 'recevoir']);
        add_action('add_meta_boxes', static function (): void {
            add_meta_box('imagine-contact-prive', __('Message enregistré localement', 'imagine-site'), static function ($post): void {
                if (!current_user_can('manage_options')) {
                    return;
                }
                foreach (self::CHAMPS as $key => $label) {
                    echo '<p><strong>' . esc_html(__($label, 'imagine-site')) . '</strong><br>'
                        . nl2br(esc_html((string)get_post_meta($post->ID, 'imagine_contact_' . $key, true))) . '</p>';
                }
            }, self::TYPE);
        });
    }

    public static function types(): void
    {
        register_post_type(self::TYPE, [
            'label' => __('Messages de contact', 'imagine-site'), 'public' => false,
            'publicly_queryable' => false, 'exclude_from_search' => true, 'show_in_rest' => false,
            'show_ui' => true, 'show_in_menu' => true, 'can_export' => false, 'supports' => [],
            'map_meta_cap' => false, 'rewrite' => false, 'query_var' => false,
            'capabilities' => array_fill_keys(['edit_post', 'read_post', 'delete_post', 'edit_posts', 'edit_others_posts',
                'publish_posts', 'read_private_posts', 'delete_posts', 'delete_private_posts', 'delete_published_posts',
                'delete_others_posts', 'edit_private_posts', 'edit_published_posts'], 'manage_options') + ['create_posts' => 'do_not_allow'],
        ]);
    }

    public static function enregistrer(string $nom, string $email, string $texte, bool $consentement): bool
    {
        $nom = sanitize_text_field($nom);
        $email = SujetRegles::email($email);
        $texte = sanitize_textarea_field($texte);
        if (!SujetRegles::valide($nom, $email, $texte)) {
            return false;
        }
        $meta = ['imagine_contact_nom' => $nom, 'imagine_contact_email' => $email,
            'imagine_contact_texte' => $texte, 'imagine_contact_consentement' => $consentement ? '1' : '0',
            'imagine_contact_date' => gmdate(DATE_ATOM)];
        $id = wp_insert_post(['post_type' => self::TYPE, 'post_status' => 'private',
            'post_title' => __('Message de contact', 'imagine-site'), 'post_content' => '',
            'post_author' => 0, 'post_parent' => 0, 'meta_input' => wp_slash($meta)], true);
        if (is_wp_error($id) || !$id) {
            return false;
        }
        foreach ($meta as $key => $value) {
            if (get_post_meta($id, $key, true) !== $value) {
                wp_delete_post($id, true);
                return false;
            }
        }
        return true;
    }

    public static function traiter(array $post): string
    {
        $valid = isset($post['_b09'], $post['nom'], $post['email'], $post['contact'])
            && is_string($post['_b09']) && is_string($post['nom']) && is_string($post['email']) && is_string($post['contact'])
            && wp_verify_nonce(wp_unslash($post['_b09']), 'imagine_contact');
        return $valid && self::enregistrer(wp_unslash($post['nom']), wp_unslash($post['email']), wp_unslash($post['contact']), ($post['consentement'] ?? '') === '1')
            ? __('Votre demande de contact a été enregistrée localement. Aucun email n’est envoyé.', 'imagine-site')
            : __('Demande refusée : vérifiez le formulaire et réessayez.', 'imagine-site');
    }

    public static function recevoir(): void
    {
        nocache_headers();
        if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
            wp_die(esc_html(__('Demande refusée.', 'imagine-site')), '', ['response' => 405]);
        }
        $message = self::traiter($_POST);
        $ok = $message === __('Votre demande de contact a été enregistrée localement. Aucun email n’est envoyé.', 'imagine-site');
        $pages = get_option('imagine_b09_pages', []);
        $target = (int)($pages['contact'] ?? 0);
        if (!$target) {
            wp_die(esc_html($message));
        }
        wp_safe_redirect(add_query_arg('contact', $ok ? 'enregistree' : 'refusee', get_permalink($target)), 303);
        exit;
    }

    /** null est une lecture en erreur, pas une collection vide. */
    public static function ids(string $email): ?array
    {
        global $wpdb;
        $ids = $wpdb->get_col($wpdb->prepare("SELECT DISTINCT p.ID FROM {$wpdb->posts} p INNER JOIN {$wpdb->postmeta} m ON m.post_id=p.ID WHERE p.post_type=%s AND m.meta_key='imagine_contact_email' AND m.meta_value=%s ORDER BY p.ID", self::TYPE, SujetRegles::email($email)));
        return $wpdb->last_error !== '' ? null : array_map('intval', $ids);
    }

    public static function formulaire(): string
    {
        ob_start();
        if (in_array($_GET['contact'] ?? '', ['enregistree', 'refusee'], true)) {
            echo '<p role="status">' . esc_html($_GET['contact'] === 'enregistree'
                ? __('Votre demande de contact a été enregistrée localement. Aucun email n’est envoyé.', 'imagine-site')
                : __('Demande refusée : vérifiez le formulaire et réessayez.', 'imagine-site')) . '</p>';
        }
        echo '<form id="imagine-contact" method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="imagine_contact">';
        wp_nonce_field('imagine_contact', '_b09');
        echo '<p><label>' . esc_html(__('Nom', 'imagine-site')) . ' <input name="nom" required maxlength="200" autocomplete="name"></label></p>';
        echo '<p><label>' . esc_html(__('Adresse email', 'imagine-site')) . ' <input type="email" name="email" required maxlength="254" autocomplete="email"></label></p>';
        echo '<p><label>' . esc_html(__('Message', 'imagine-site')) . ' <textarea name="contact" required maxlength="10000"></textarea></label></p>';
        echo '<p><label><input type="checkbox" name="consentement" value="1"> ' . esc_html(__('J’accepte d’être recontacté au contact de cette demande de contact.', 'imagine-site')) . '</label></p>';
        echo '<p>' . esc_html(__('Ces données sont conservées localement, uniquement pour le traitement de votre demande de contact.', 'imagine-site'))
            . ' <a href="' . esc_url(get_privacy_policy_url()) . '">' . esc_html(__('Confidentialité', 'imagine-site')) . '</a></p>';
        echo '<button type="submit">' . esc_html(__('Enregistrer le message', 'imagine-site')) . '</button></form>';
        return (string)ob_get_clean();
    }
}
