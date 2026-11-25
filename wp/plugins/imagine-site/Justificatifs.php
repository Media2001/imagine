<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Raccord documentaire natif. Aucun appel Woo, email ou service externe. */
final class Justificatifs
{
    public const CAP = 'imagine_traiter_justificatifs';
    public const PREFIX = 'imagine_justificatif_';
    public const PAGE = 'imagine-justificatifs';

    public static function register(): void
    {
        foreach (['deposer', 'decider'] as $action) {
            add_action('admin_post_imagine_justificatif_' . $action, [self::class, $action]);
            add_action('admin_post_nopriv_imagine_justificatif_' . $action, [self::class, $action]);
        }
        add_action('template_redirect', [self::class, 'servir'], -101);
        add_action('admin_menu', static function (): void {
            add_submenu_page('imagine', __('Justificatifs solidaires', 'imagine-site'),
                __('Justificatifs solidaires', 'imagine-site'), self::CAP, self::PAGE, [self::class, 'page']);
        }, 120);
        add_filter('woocommerce_prevent_admin_access', static function (bool $prevent): bool {
            global $pagenow;
            return $pagenow === 'admin.php' && ($_GET['page'] ?? '') === self::PAGE && current_user_can(self::CAP)
                ? false : $prevent;
        });
    }

    public static function etat(int $user): array
    {
        $value = get_option(self::PREFIX . $user, []);
        if (!is_array($value)) {
            throw new \RuntimeException('État documentaire invalide.');
        }
        return $value;
    }

    public static function version(array $state): string
    {
        return hash('sha256', serialize($state));
    }

    /** Même frontière hors document root, droits 0700/0600 et noms aléatoires que C11. */
    public static function chemin(array $state): string
    {
        $blob = $state['blob'] ?? '';
        if (!is_string($blob) || !preg_match('/\A[a-f0-9]{32}\z/D', $blob)) {
            throw new \RuntimeException('Référence documentaire invalide.');
        }
        $path = PdfNumero::directory() . '/c17-' . $blob . '.bin';
        if (is_link($path)) {
            throw new \RuntimeException('Lien documentaire refusé.');
        }
        return $path;
    }

    public static function verrou(int $user, callable $operation): mixed
    {
        global $wpdb;
        if ($user < 1 || !get_userdata($user)) {
            throw new \RuntimeException('Compte indisponible.');
        }
        $key = 'imagine_c17_' . get_current_blog_id() . '_' . $user;
        if ((int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 5)', $key)) !== 1) {
            throw new \RuntimeException('Document occupé, réessayez.');
        }
        try {
            // Ne pas conserver une lecture d'option faite avant l'attente du verrou.
            wp_cache_delete(self::PREFIX . $user, 'options');
            return $operation();
        } finally {
            $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $key));
        }
    }

    private static function enregistrer(int $user, array $state): void
    {
        update_option(self::PREFIX . $user, $state, false);
        wp_cache_delete(self::PREFIX . $user, 'options');
        if (self::etat($user) !== $state) {
            throw new \RuntimeException('État documentaire non enregistré.');
        }
    }

    public static function supprimerFichier(array $state): void
    {
        if (!isset($state['blob'])) {
            return;
        }
        $path = self::chemin($state);
        clearstatcache(true, $path);
        if (file_exists($path) && (!is_file($path) || !unlink($path))) {
            throw new \RuntimeException('Suppression du document impossible : aucune décision enregistrée.');
        }
        clearstatcache(true, $path);
        if (file_exists($path) || is_link($path)) {
            throw new \RuntimeException('Document encore présent.');
        }
    }

    /** Utilisé aussi par les deux seules fixtures C09 ; le contrôleur exige un upload PHP natif. */
    public static function recevoir(int $user, string $categorie, string $bytes, string $version): array
    {
        JustificatifRegles::mime($bytes);
        $new = JustificatifRegles::depot($categorie, JustificatifsReglages::categories());
        return self::verrou($user, static function () use ($user, $new, $bytes, $version): array {
            $old = self::etat($user);
            if (!hash_equals(self::version($old), $version)) {
                throw new \RuntimeException('État modifié : rechargez la page.');
            }
            // Validation avant retrait, jamais deux fichiers persistants pour un compte.
            self::supprimerFichier($old);
            $new['blob'] = bin2hex(random_bytes(16));
            $path = self::chemin($new);
            $handle = @fopen($path, 'xb');
            if (!$handle) {
                throw new \RuntimeException('Stockage privé indisponible.');
            }
            try {
                if (!chmod($path, 0600) || fwrite($handle, $bytes) !== strlen($bytes) || !fflush($handle)) {
                    throw new \RuntimeException('Écriture documentaire refusée.');
                }
                fclose($handle);
                $handle = false;
                if (hash_file('sha256', $path) !== hash('sha256', $bytes)) {
                    throw new \RuntimeException('Document écrit différent.');
                }
                self::enregistrer($user, $new);
            } catch (\Throwable $e) {
                if (is_resource($handle)) {
                    fclose($handle);
                }
                self::supprimerFichier($new);
                throw $e;
            }
            return $new;
        });
    }

    private static function texte(array $input, string $key): string
    {
        if (!isset($input[$key]) || !is_string($input[$key])) {
            throw new \InvalidArgumentException('Champ invalide.');
        }
        return wp_unslash($input[$key]);
    }

    private static function requete(string $action): void
    {
        PdfNumero::privateHeaders();
        if (!get_current_user_id() || ($action === 'decider' && !current_user_can(self::CAP))) {
            wp_die(esc_html__('Accès refusé.', 'imagine-site'), '', ['response' => 403]);
        }
        if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
            header('Allow: POST');
            wp_die(esc_html__('Requête POST uniquement.', 'imagine-site'), '', ['response' => 405]);
        }
        $nonce = $_POST['_wpnonce'] ?? null;
        if (!is_string($nonce) || !wp_verify_nonce($nonce, 'imagine_justificatif_' . $action)) {
            wp_die(esc_html__('Jeton de sécurité invalide.', 'imagine-site'), '', ['response' => 403]);
        }
    }

    public static function deposer(): void
    {
        self::requete('deposer');
        try {
            $file = $_FILES['justificatif'] ?? null;
            if (!is_array($file) || ($file['error'] ?? -1) !== UPLOAD_ERR_OK
                || !is_string($file['tmp_name'] ?? null) || !is_uploaded_file($file['tmp_name'])
                || filesize($file['tmp_name']) > JustificatifRegles::MAX) {
                throw new \InvalidArgumentException('Fichier manquant ou trop volumineux (5 Mio maximum).');
            }
            $bytes = file_get_contents($file['tmp_name']);
            if (!is_string($bytes)) {
                throw new \RuntimeException('Lecture du dépôt impossible.');
            }
            self::recevoir(get_current_user_id(), self::texte($_POST, 'categorie'), $bytes, self::texte($_POST, 'version'));
        } catch (\Throwable) {
            wp_die(esc_html__('Dépôt refusé. Vérifiez le type, la taille, la catégorie et rechargez la page avant de réessayer.', 'imagine-site'), '', ['response' => 409]);
        }
        wp_safe_redirect(wc_get_page_permalink('myaccount') . '#imagine-compte-factures', 303);
        exit;
    }

    public static function decider(): void
    {
        self::requete('decider');
        try {
            $id = self::texte($_POST, 'titulaire');
            if (!preg_match('/\A[1-9][0-9]*\z/D', $id) || self::texte($_POST, 'confirmer') !== 'oui') {
                throw new \InvalidArgumentException('Confirmation requise.');
            }
            self::verrou((int) $id, static function () use ($id): void {
                $old = self::etat((int) $id);
                if (!hash_equals(self::version($old), self::texte($_POST, 'version'))) {
                    throw new \RuntimeException('Document remplacé ou décision déjà prise.');
                }
                $new = JustificatifRegles::decider($old, self::texte($_POST, 'decision'),
                    self::texte($_POST, 'fin'), wp_get_current_user()->user_login, gmdate('Y-m-d\TH:i:s\Z'));
                self::supprimerFichier($old);
                self::enregistrer((int) $id, $new);
            });
        } catch (\Throwable) {
            wp_die(esc_html__('Décision refusée. Vérifiez la date, confirmez et rechargez la file.', 'imagine-site'), '', ['response' => 409]);
        }
        wp_safe_redirect(admin_url('admin.php?page=' . self::PAGE), 303);
        exit;
    }

    public static function url(int $user, array $state): string
    {
        return add_query_arg(['imagine_justificatif' => $user, 'version' => $state['blob']], home_url('/'));
    }

    public static function servir(): void
    {
        if (!isset($_GET['imagine_justificatif'])) {
            return;
        }
        PdfNumero::privateHeaders();
        $id = $_GET['imagine_justificatif'];
        if (!is_string($id) || !preg_match('/\A[1-9][0-9]*\z/D', $id)) {
            wp_die(esc_html__('Document indisponible.', 'imagine-site'), '', ['response' => 404]);
        }
        if (!get_current_user_id() || (get_current_user_id() !== (int) $id && !current_user_can(self::CAP))) {
            wp_die(esc_html__('Accès refusé.', 'imagine-site'), '', ['response' => 403]);
        }
        if (!in_array($_SERVER['REQUEST_METHOD'] ?? '', ['GET', 'HEAD'], true)) {
            header('Allow: GET, HEAD');
            wp_die(esc_html__('Méthode refusée.', 'imagine-site'), '', ['response' => 405]);
        }
        try {
            self::verrou((int) $id, static function () use ($id): void {
                $state = self::etat((int) $id);
                if (($state['decision'] ?? '') !== 'en_attente'
                    || !hash_equals($state['blob'], self::texte($_GET, 'version'))) {
                    throw new \RuntimeException('Document indisponible.');
                }
                $bytes = @file_get_contents(self::chemin($state));
                if (!is_string($bytes)) {
                    throw new \RuntimeException('Document absent.');
                }
                $mime = JustificatifRegles::mime($bytes);
                status_header(200);
                header('Content-Type: ' . $mime, true);
                header('Content-Disposition: attachment; filename="justificatif.' . match ($mime) {
                    'application/pdf' => 'pdf', 'image/png' => 'png', default => 'jpg',
                } . '"', true);
                header("Content-Security-Policy: sandbox; default-src 'none'", true);
                header('Content-Length: ' . strlen($bytes), true);
                if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'HEAD') {
                    echo $bytes;
                }
            });
        } catch (\Throwable) {
            wp_die(esc_html__('Document indisponible.', 'imagine-site'), '', ['response' => 404]);
        }
        exit;
    }

    public static function compte(): void
    {
        $id = get_current_user_id();
        if (!$id) {
            return;
        }
        $s = self::etat($id);
        $label = match ($s['decision'] ?? '') {
            'en_attente' => __('En attente', 'imagine-site'),
            'valide' => sprintf(__('Validé jusqu’au %s', 'imagine-site'), $s['fin']),
            'refuse' => __('Refusé', 'imagine-site'), default => __('Aucun', 'imagine-site'),
        };
        echo '<div data-imagine-justificatif><h3>' . esc_html__('Tarif solidaire — justificatif', 'imagine-site')
            . '</h3><p role="status">' . esc_html($label) . '</p>';
        if (($s['decision'] ?? '') === 'en_attente') {
            echo '<p><a href="' . esc_url(self::url($id, $s)) . '">' . esc_html__('Télécharger mon dépôt protégé', 'imagine-site') . '</a></p>';
        }
        echo '<p id="imagine-justificatif-aide">' . esc_html__('Masquez votre numéro de registre national. PDF, JPEG ou PNG uniquement, 5 Mio maximum. Le fichier est supprimé dès validation ou refus ; un nouveau dépôt remplace le précédent. Aucun changement de prix ou de droits dans cet écran.', 'imagine-site') . '</p>';
        echo '<form method="post" enctype="multipart/form-data" action="' . esc_url(admin_url('admin-post.php')) . '">';
        echo '<input type="hidden" name="action" value="imagine_justificatif_deposer"><input type="hidden" name="version" value="' . esc_attr(self::version($s)) . '">';
        wp_nonce_field('imagine_justificatif_deposer');
        echo '<p><label for="imagine-justificatif-categorie">' . esc_html__('Catégorie', 'imagine-site') . '</label> <select id="imagine-justificatif-categorie" name="categorie" required>';
        foreach (JustificatifsReglages::categories() as $c) {
            echo '<option value="' . esc_attr($c) . '">' . esc_html($c) . '</option>';
        }
        echo '</select></p><p><label for="imagine-justificatif-fichier">' . esc_html__('Nouveau justificatif', 'imagine-site') . '</label> <input id="imagine-justificatif-fichier" type="file" name="justificatif" accept="application/pdf,image/jpeg,image/png" aria-describedby="imagine-justificatif-aide" required></p>';
        echo '<button type="submit">' . esc_html__('Déposer ou remplacer mon justificatif', 'imagine-site') . '</button></form></div>';
    }

    public static function page(): void
    {
        if (!current_user_can(self::CAP)) {
            wp_die(esc_html__('Accès refusé.', 'imagine-site'), '', ['response' => 403]);
        }
        global $wpdb;
        $page = max(1, (int) ($_GET['paged'] ?? 1));
        $names = $wpdb->get_col($wpdb->prepare(
            "SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s AND option_value LIKE %s ORDER BY option_id LIMIT 21 OFFSET %d",
            $wpdb->esc_like(self::PREFIX) . '%', '%s:8:"decision";s:10:"en_attente";%', ($page - 1) * 20
        ));
        $more = count($names) > 20;
        echo '<div class="wrap" data-imagine-file-justificatifs><h1>' . esc_html__('Justificatifs solidaires — en attente', 'imagine-site') . '</h1><p>'
            . esc_html__('Documents personnels protégés. La confirmation supprime le fichier du disque. Aucun prix ni accès modifié.', 'imagine-site') . '</p>';
        if (!$names) {
            echo '<p>' . esc_html__('Aucun justificatif en attente.', 'imagine-site') . '</p>';
        }
        foreach (array_slice($names, 0, 20) as $name) {
            $id = (int) substr($name, strlen(self::PREFIX));
            $s = self::etat($id);
            $u = get_userdata($id);
            if (!$u || ($s['decision'] ?? '') !== 'en_attente') {
                continue;
            }
            echo '<article data-imagine-justificatif-titulaire="' . esc_attr((string) $id) . '"><h2>' . esc_html($u->display_name)
                . '</h2><p>' . esc_html($s['categorie']) . ' — <a href="' . esc_url(self::url($id, $s)) . '">'
                . esc_html__('Télécharger le fichier protégé', 'imagine-site') . '</a></p>';
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="imagine_justificatif_decider">';
            echo '<input type="hidden" name="titulaire" value="' . esc_attr((string) $id) . '"><input type="hidden" name="version" value="' . esc_attr(self::version($s)) . '">';
            wp_nonce_field('imagine_justificatif_decider');
            echo '<p><label>' . esc_html__('Date de fin (obligatoire pour valider)', 'imagine-site') . ' <input type="date" name="fin" min="' . esc_attr(gmdate('Y-m-d')) . '"></label></p>';
            echo '<p><label><input type="checkbox" name="confirmer" value="oui" required> ' . esc_html__('Je confirme la décision et la suppression définitive du fichier.', 'imagine-site') . '</label></p>';
            echo '<button type="submit" name="decision" value="valide">' . esc_html__('Valider', 'imagine-site') . '</button> <button type="submit" name="decision" value="refuse">' . esc_html__('Refuser', 'imagine-site') . '</button></form></article>';
        }
        foreach ([$page > 1 ? $page - 1 : 0 => __('Précédente', 'imagine-site'), $more ? $page + 1 : 0 => __('Suivante', 'imagine-site')] as $number => $label) {
            if ($number) {
                echo '<p><a href="' . esc_url(admin_url('admin.php?page=' . self::PAGE . '&paged=' . $number)) . '">' . esc_html($label) . '</a></p>';
            }
        }
        echo '</div>';
    }
}
