<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Écran natif ; seul effet d'une extraction : un événement de métadonnées. */
final class ExtractionsAdmin
{
    public const CAP = 'imagine_extraire_abonnes';
    public const PAGE = 'imagine-extractions';
    public const ACTION = 'imagine_extraire_abonnes';
    public const JOURNAL = 'imagine_extraction_journal_';

    public static function autorise(): bool
    {
        return current_user_can('manage_options') || current_user_can(self::CAP);
    }

    private static function t(string $text): string
    {
        return __($text, 'imagine-site');
    }

    private static function verifier(): void
    {
        if (!self::autorise()) {
            wp_die(self::t('Extraction réservée au Référent abonnements.'), '', ['response' => 403]);
        }
    }

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 120);
        add_action('admin_init', static function (): void {
            if (($_GET['page'] ?? null) === self::PAGE) {
                self::verifier();
            }
        });
        add_filter('woocommerce_prevent_admin_access', static function (bool $prevent): bool {
            global $pagenow;
            return $pagenow === 'admin.php' && ($_GET['page'] ?? null) === self::PAGE && self::autorise() ? false : $prevent;
        });
        add_action('admin_post_' . self::ACTION, [self::class, 'exporter']);
        add_action('admin_post_nopriv_' . self::ACTION, [self::class, 'exporter']);
    }

    public static function menu(): void
    {
        if (self::autorise()) {
            add_submenu_page(
                'imagine',
                self::t('Extractions'),
                self::t('Extractions'),
                current_user_can('manage_options') ? 'manage_options' : self::CAP,
                self::PAGE,
                [self::class, 'page']
            );
        }
    }

    private static function id(array $request): string
    {
        $id = $request['extraction'] ?? 'localite';
        if (!is_string($id)) {
            throw new \InvalidArgumentException('Extraction invalide.');
        }
        ExtractionsRegles::definition($id);
        return $id;
    }

    public static function jeton(string $id, array $filters): string
    {
        return self::ACTION . ':' . hash('sha256', json_encode([$id, ExtractionsRegles::filtres($id, $filters)], JSON_THROW_ON_ERROR));
    }

    public static function journal(): array
    {
        global $wpdb;
        return array_map('maybe_unserialize', $wpdb->get_col($wpdb->prepare(
            "SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_id DESC LIMIT 50",
            $wpdb->esc_like(self::JOURNAL) . '%'
        )));
    }

    /** Ne mémorise ni sélection, ni identité d'abonné, ni contenu du CSV. */
    public static function preparer(string $id, array $filters): array
    {
        self::verifier();
        $rows = ExtractionsNatives::lire($id, $filters);
        if (!class_exists(\Imagine\Connecteur\CsvProtection::class)) {
            throw new \RuntimeException('Protection CSV indisponible.');
        }
        $user = wp_get_current_user();
        $event = ['qui_id' => $user->ID, 'qui_login' => $user->user_login,
            'quand_utc' => gmdate('Y-m-d\TH:i:s\Z'), 'extraction' => $id, 'lignes' => count($rows)];
        $key = self::JOURNAL . str_replace('-', '', wp_generate_uuid4());
        if (!add_option($key, $event, '', false) || get_option($key) !== $event) {
            throw new \RuntimeException('Journal indisponible : export refusé.');
        }
        return $rows;
    }

    public static function exporter(): void
    {
        self::verifier();
        if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
            header('Allow: POST');
            wp_die(self::t('Extraction par POST uniquement.'), '', ['response' => 405]);
        }
        try {
            $request = wp_unslash($_POST);
            $id = self::id($request);
            $filters = ExtractionsRegles::filtres($id, $request);
        } catch (\Throwable) {
            wp_die(self::t('Extraction ou filtres invalides.'), '', ['response' => 400]);
        }
        if (!isset($_POST['_wpnonce']) || !is_string($_POST['_wpnonce'])) {
            wp_die(self::t('Jeton absent ou invalide.'), '', ['response' => 403]);
        }
        check_admin_referer(self::jeton($id, $filters));
        try {
            $rows = self::preparer($id, $filters);
            $stream = fopen('php://output', 'wb');
            if ($stream === false) {
                throw new \RuntimeException('Flux indisponible.');
            }
        } catch (\Throwable) {
            wp_die(self::t('Extraction refusée : données natives ou journal indisponibles.'), '', ['response' => 409]);
        }
        nocache_headers();
        header('Cache-Control: private, no-store, no-cache, must-revalidate, max-age=0');
        header('Content-Type: text/csv; charset=UTF-8');
        header('Content-Disposition: attachment; filename="extraction-' . $id . '.csv"');
        header('X-Content-Type-Options: nosniff');
        ExtractionsRegles::csv($stream, $id, $rows);
        fclose($stream);
        exit;
    }

    public static function page(): void
    {
        self::verifier();
        nocache_headers();
        header('Cache-Control: private, no-store, no-cache, must-revalidate, max-age=0');
        echo '<div class="wrap"><h1>' . esc_html(self::t('Extractions')) . '</h1>';
        echo '<p>' . esc_html(self::t('Lecture seule. Une ligne par abonnement natif, tous états compris ; un compte peut donc avoir plusieurs lignes. Aucun email ni appel sortant.')) . '</p>';
        try {
            $request = wp_unslash($_GET);
            $id = self::id($request);
            $definition = ExtractionsRegles::definition($id);
            echo '<form method="get" action="' . esc_url(admin_url('admin.php')) . '"><input type="hidden" name="page" value="' . esc_attr(self::PAGE) . '">';
            echo '<label for="imagine-extraction">' . esc_html(self::t('Extraction')) . '</label> <select id="imagine-extraction" name="extraction">';
            foreach (ExtractionsRegles::catalogue() as $key => $report) {
                echo '<option value="' . esc_attr($key) . '"' . selected($id, $key, false)
                    . ($report['disponible'] ? '' : ' disabled="disabled"') . '>' . esc_html(self::t($report['titre'])) . '</option>';
            }
            echo '</select> ';
            submit_button(self::t('Choisir l’extraction'), 'secondary', '', false);
            echo '</form><h2>' . esc_html(self::t($definition['titre'])) . '</h2>';
            echo '<form method="get" action="' . esc_url(admin_url('admin.php')) . '"><input type="hidden" name="page" value="' . esc_attr(self::PAGE) . '">';
            echo '<input type="hidden" name="extraction" value="' . esc_attr($id) . '">';
            foreach ($definition['filtres'] as $key => $spec) {
                if (!array_key_exists($key, $request) && isset($spec['defaut'])) {
                    $request[$key] = gmdate('Y-m-d', strtotime($spec['defaut']));
                }
                $value = is_string($request[$key] ?? null) ? $request[$key] : '';
                echo '<p><label for="imagine-filtre-' . esc_attr($key) . '">' . esc_html(self::t($spec['label'])) . '</label> ';
                if ($spec['type'] === 'select') {
                    echo '<select id="imagine-filtre-' . esc_attr($key) . '" name="' . esc_attr($key) . '">';
                    foreach ($spec['options'] as $option => $label) {
                        echo '<option value="' . esc_attr($option) . '"' . selected($value, $option, false) . '>' . esc_html(self::t($label)) . '</option>';
                    }
                    echo '</select>';
                } else {
                    echo '<input id="imagine-filtre-' . esc_attr($key) . '" type="' . esc_attr($spec['type']) . '" name="' . esc_attr($key) . '" value="' . esc_attr($value) . '" maxlength="80">';
                }
                echo '</p>';
            }
            submit_button(self::t('Afficher le nombre de lignes'), 'secondary');
            echo '</form>';
            $filters = ExtractionsRegles::filtres($id, $request);
            $rows = ExtractionsNatives::lire($id, $filters);
            echo '<h2>' . esc_html(self::t('Aperçu')) . '</h2><p><strong data-imagine-extraction-nombre="' . count($rows) . '">' . esc_html(sprintf(self::t('%d lignes'), count($rows))) . '</strong></p>';
            echo '<p>' . esc_html(self::t('Le téléchargement relit les mêmes filtres sur l’état natif courant : le nombre peut changer entre aperçu et téléchargement. Pays et code postal : correspondance exacte sur la livraison de l’abonnement. Échéance UTC : première date native non vide entre prochain paiement et fin ; aucune date ni âge recalculé. État : projection existante de Mon compte, pas une décision d’accès. Mode vide : non renseigné, jamais un paiement déduit. Sur cette démo, C15 reconnaît seulement les marqueurs fictifs existants A-VIR et A-PAPIER.')) . '</p>';
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr(self::ACTION) . '"><input type="hidden" name="extraction" value="' . esc_attr($id) . '">';
            foreach ($filters as $key => $value) {
                echo '<input type="hidden" name="' . esc_attr($key) . '" value="' . esc_attr($value) . '">';
            }
            wp_nonce_field(self::jeton($id, $filters));
            submit_button(self::t('Télécharger le CSV'));
            echo '</form>';
        } catch (\Throwable) {
            echo '<div class="notice notice-error"><p>' . esc_html(self::t('Extraction indisponible : vérifier les filtres et les données natives. Aucun fichier produit.')) . '</p></div>';
        }
        echo '<h2>' . esc_html(self::t('Journal des extractions — cinquante dernières, sans purge')) . '</h2><table class="widefat striped"><thead><tr>';
        foreach (['Opérateur', 'Date UTC', 'Extraction', 'Lignes'] as $label) {
            echo '<th scope="col">' . esc_html(self::t($label)) . '</th>';
        }
        echo '</tr></thead><tbody>';
        foreach (self::journal() as $event) {
            echo '<tr><td>' . esc_html($event['qui_login'] . ' (#' . $event['qui_id'] . ')') . '</td><td>' . esc_html($event['quand_utc']) . '</td><td>' . esc_html($event['extraction']) . '</td><td>' . esc_html((string) $event['lignes']) . '</td></tr>';
        }
        echo '</tbody></table></div>';
    }
}
