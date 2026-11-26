<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Formulaire facultatif local. Aucun transport et aucune inscription implicite. */
final class Personnalisation
{
    public const CATALOGUE = 'imagine_personnalisation_questions';
    public const META = 'imagine_personnalisation_reponses';
    public const CONSENTEMENT = 'imagine_personnalisation_consentement';
    public const ACCROCHE = 'imagine_personnalisation_attributs_modifies';
    public const APRES_INSCRIPTION_ACHAT = 'imagine_personnalisation_apres_inscription_achat';

    public static function register(): void
    {
        add_action('woocommerce_account_dashboard', [self::class, 'compte'], 40);
        add_action('admin_post_imagine_personnalisation', [self::class, 'traiter']);
        add_action('admin_post_nopriv_imagine_personnalisation', [self::class, 'traiter']);
        // APRES_INSCRIPTION_ACHAT : emplacement réservé au futur tunnel, aucun écouteur.
    }

    public static function catalogue(): array
    {
        try { return PersonnalisationRegles::catalogue(get_option(self::CATALOGUE, [])); }
        catch (\InvalidArgumentException) { return []; }
    }

    public static function reponses(int $id): array
    {
        $value = get_user_meta($id, self::META, true);
        return is_array($value) ? $value : [];
    }

    public static function consentement(int $id): array
    {
        $value = get_user_meta($id, self::CONSENTEMENT, true);
        return is_array($value) ? $value : [];
    }

    public static function version(int $id): string
    {
        return hash('sha256', serialize([self::catalogue(), self::reponses($id), self::consentement($id)]));
    }

    /** Un futur connecteur doit relire cette projection, jamais les métadonnées brutes. */
    public static function attributsConnecteur(int $id): array
    {
        $newsletter = false;
        foreach (Newsletters::catalogue() as $row) {
            $newsletter = $newsletter || (Newsletters::preferences($id)[$row['id']]['choix'] ?? null) === true;
        }
        if (!PersonnalisationRegles::transmissible(self::consentement($id), $newsletter, Newsletters::admissible($id))) {
            return [];
        }
        $active = [];
        foreach (self::catalogue() as $row) {
            $value = self::reponses($id)[$row['id']] ?? null;
            if (is_array($value)) {
                $choices = array_values(array_intersect($value['choix'] ?? [], array_column($row['choix'], 'id')));
                if ($choices) { $active[$row['id']] = ['choix' => $choices, 'date_utc' => $value['date_utc']]; }
            }
        }
        return $active;
    }

    public static function enregistrer(int $id, array $answers, ?bool $consent, string $version, string $mode = 'reponses'): void
    {
        if (!$id || $id !== get_current_user_id() || !in_array($mode, ['reponses', 'consentement', 'effacer'], true)
            || ($mode === 'consentement' && (!Newsletters::admissible($id) || $consent === null))) {
            throw new \RuntimeException('Compte ou opération refusés.');
        }
        global $wpdb;
        $lock = 'imagine_personnalisation_' . $id;
        if ((int)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 3)', $lock)) !== 1) {
            throw new \RuntimeException('Formulaire occupé.');
        }
        try {
            wp_cache_delete($id, 'user_meta');
            if (!hash_equals(self::version($id), $version)) { throw new \RuntimeException('Formulaire périmé.'); }
            $key = $mode === 'consentement' ? self::CONSENTEMENT : self::META;
            $old = $mode === 'consentement' ? self::consentement($id) : self::reponses($id);
            $now = gmdate('Y-m-d\TH:i:s\Z');
            $new = $mode === 'consentement'
                ? (($old['accord'] ?? null) === $consent ? $old : ['accord' => $consent, 'date_utc' => $now])
                : PersonnalisationRegles::repondre(self::catalogue(), $old, $answers, $now, $mode === 'effacer');
            if ($old !== $new) {
                $ok = $new ? update_user_meta($id, $key, $new) : delete_user_meta($id, $key);
                wp_cache_delete($id, 'user_meta');
                $actual = $mode === 'consentement' ? self::consentement($id) : self::reponses($id);
                if (!$ok || $actual !== $new) { throw new \RuntimeException('Personnalisation non enregistrée.'); }
                $eligible = self::attributsConnecteur($id);
                if ($eligible) { do_action(self::ACCROCHE, $id, $eligible); }
            }
        } finally { $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock)); }
    }

    public static function traiter(): void
    {
        nocache_headers();
        $id = get_current_user_id(); $post = wp_unslash($_POST);
        if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST' || !$id
            || !is_string($post['compte'] ?? null) || $post['compte'] !== (string)$id
            || !is_string($post['_wpnonce'] ?? null) || !wp_verify_nonce($post['_wpnonce'], 'imagine_personnalisation_' . $id)
            || !is_string($post['version'] ?? null) || !is_string($post['mode'] ?? null)
            || !is_array($post['reponses'] ?? []) || !in_array($post['consentement'] ?? '0', ['0', '1'], true)) {
            wp_die(esc_html__('Personnalisation refusée.', 'imagine-site'), '', ['response' => 403]);
        }
        try {
            $answers = $post['reponses'] ?? [];
            foreach ($answers as &$values) {
                if (!is_array($values)) { throw new \InvalidArgumentException(); }
                $values = array_values(array_filter($values, static fn ($v) => $v !== ''));
            }
            unset($values);
            self::enregistrer($id, $answers, ($post['consentement'] ?? '0') === '1', $post['version'], $post['mode']);
        } catch (\Throwable) {
            wp_die(esc_html__('Personnalisation inchangée : rechargez le formulaire.', 'imagine-site'), '', ['response' => 409]);
        }
        wp_safe_redirect(wc_get_page_permalink('myaccount') . '#ma-personnalisation', 303); exit;
    }

    private static function debutFormulaire(int $id, string $mode): void
    {
        echo '<form method="post" data-personnalisation-mode="' . esc_attr($mode) . '" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field('imagine_personnalisation_' . $id);
        foreach (['action' => 'imagine_personnalisation', 'compte' => (string)$id, 'version' => self::version($id), 'mode' => $mode] as $key => $value) {
            echo '<input type="hidden" name="' . esc_attr($key) . '" value="' . esc_attr($value) . '">';
        }
    }

    public static function compte(): void
    {
        $id = get_current_user_id(); if (!$id) { return; }
        echo '<section id="ma-personnalisation"><h2>' . esc_html__('Personnalisez ce que vous recevez', 'imagine-site') . '</h2><p>'
            . esc_html__('Facultatif. Questions entièrement fictives : rien ne part, aucun email ne sera envoyé. Ne pas répondre ne bloque rien.', 'imagine-site') . '</p>';
        self::debutFormulaire($id, 'reponses');
        foreach (self::catalogue() as $row) {
            $saved = self::reponses($id)[$row['id']] ?? [];
            echo '<fieldset data-question="' . esc_attr($row['id']) . '"><legend>' . esc_html($row['titre']) . '</legend>';
            if (!$row['multiple']) {
                echo '<label><input type="radio" name="reponses[' . esc_attr($row['id']) . '][]" value=""'
                    . checked(empty($saved['choix']), true, false) . '> ' . esc_html__('Ne pas répondre', 'imagine-site') . '</label> ';
            }
            foreach ($row['choix'] as $choice) {
                echo '<label><input type="' . ($row['multiple'] ? 'checkbox' : 'radio') . '" name="reponses[' . esc_attr($row['id'])
                    . '][]" value="' . esc_attr($choice['id']) . '"' . checked(in_array($choice['id'], $saved['choix'] ?? [], true), true, false)
                    . '> ' . esc_html($choice['titre']) . '</label> ';
            }
            if ($saved) { echo '<p><time datetime="' . esc_attr($saved['date_utc']) . '">' . esc_html($saved['date_utc']) . '</time></p>'; }
            echo '</fieldset>';
        }
        echo '<button type="submit">' . esc_html__('Enregistrer mes réponses', 'imagine-site') . '</button></form>';
        self::debutFormulaire($id, 'effacer');
        echo '<button type="submit">' . esc_html__('Effacer toutes mes réponses', 'imagine-site') . '</button></form>';
        if (Newsletters::admissible($id)) {
            self::debutFormulaire($id, 'consentement');
            $consent = self::consentement($id);
            echo '<p><label><input type="checkbox" name="consentement" value="1"' . checked(($consent['accord'] ?? false), true, false) . '> '
                . esc_html__('J’accepte que ces réponses servent à personnaliser les envois que je reçois', 'imagine-site') . '</label></p>';
            if ($consent) {
                echo '<p>' . esc_html($consent['accord'] ? __('Accord donné', 'imagine-site') : __('Accord retiré', 'imagine-site'))
                    . ' — <time datetime="' . esc_attr($consent['date_utc']) . '">' . esc_html($consent['date_utc']) . '</time></p>';
            }
            echo '<button type="submit">' . esc_html__('Enregistrer mon consentement', 'imagine-site') . '</button></form>';
        } else {
            echo '<p data-personnalisation-sans-email>' . esc_html__('Compte sans email : les réponses restent sur le site, sans consentement aux envois.', 'imagine-site') . '</p>';
        }
        echo '</section>';
    }
}
