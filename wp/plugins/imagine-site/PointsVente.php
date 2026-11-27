<?php

declare(strict_types=1);

namespace Imagine\Site;

use InvalidArgumentException;
use RuntimeException;
use Throwable;

final class PointsVente
{
    public const TYPE = 'imagine_vente';
    public const ACTIFS = 'imagine_vente_actifs';
    public const CONFIG = 'imagine_vente_configuration';
    public const NETTOYAGE = 'imagine_vente_nettoyage';

    public static function register(): void
    {
        add_action('init', static function (): void {
            register_post_type(self::TYPE, [
                'label' => __('Points de vente', 'imagine-site'), 'public' => false,
                'publicly_queryable' => false, 'exclude_from_search' => true, 'show_in_rest' => false,
                'show_ui' => false, 'rewrite' => false, 'query_var' => false, 'can_export' => false,
                'supports' => ['title'],
            ]);
        });
        add_action('admin_menu', static function (): void {
            add_options_page(__('Points de vente', 'imagine-site'), __('Points de vente', 'imagine-site'),
                'manage_options', 'imagine-points-vente', [self::class, 'administration']);
        });
        add_filter('the_content', static function (string $content): string {
            if (is_singular('page') && in_the_loop() && is_main_query()
                && get_the_ID() === (int) get_option('imagine_b10_page', 0)
            ) {
                $query = isset($_GET['localite']) && is_string($_GET['localite']) ? wp_unslash($_GET['localite']) : '';
                return $content . self::afficher(mb_substr($query, 0, 500));
            }
            return $content;
        }, 30);
    }

    public static function carte(mixed $value): string
    {
        return $value === '1' ? '1' : '0';
    }

    public static function configuration(): array
    {
        $defaults = ['mapping' => ['nom' => 'enseigne', 'adresse' => 'rue', 'localite' => 'ville', 'postal' => 'cp'],
            'separateur' => ';', 'carte' => '0'];
        $value = get_option(self::CONFIG, $defaults);
        if (!is_array($value)) {
            return $defaults;
        }
        $value['carte'] = self::carte($value['carte'] ?? null);
        return $value + $defaults;
    }

    public static function lignes(): array
    {
        $rows = [];
        foreach (get_option(self::ACTIFS, []) as $id) {
            $post = get_post((int) $id);
            $row = get_post_meta((int) $id, 'imagine_vente_ligne', true);
            if (!$post || $post->post_type !== self::TYPE || !is_array($row)
                || array_diff(self::champsRequis(), array_keys($row)) !== []
            ) {
                throw new RuntimeException('liste_illisible');
            }
            $rows[] = array_intersect_key($row, array_flip([...PointsVenteRegles::REQUIS, ...PointsVenteRegles::FACULTATIFS]));
        }
        return $rows;
    }

    private static function champsRequis(): array
    {
        return PointsVenteRegles::REQUIS;
    }

    private static function retenirNettoyage(array $ids): void
    {
        $pending = array_values(array_unique(array_merge(get_option(self::NETTOYAGE, []), $ids)));
        update_option(self::NETTOYAGE, $pending, false);
        if (get_option(self::NETTOYAGE) !== $pending) {
            throw new RuntimeException('reprise_refusee');
        }
    }

    private static function nettoyer(): bool
    {
        $remaining = [];
        $active = get_option(self::ACTIFS, []);
        foreach (get_option(self::NETTOYAGE, []) as $id) {
            // Un arrêt avant bascule peut avoir laissé des IDs encore actifs dans la reprise.
            if (in_array($id, $active, true) || !get_post((int) $id)) {
                continue;
            }
            if (get_post_type((int) $id) !== self::TYPE || !wp_delete_post((int) $id, true)
                || get_post((int) $id)
            ) {
                $remaining[] = $id;
            }
        }
        update_option(self::NETTOYAGE, $remaining, false);
        return $remaining === [] && get_option(self::NETTOYAGE) === [];
    }

    public static function importer(string $csv, array $mapping, string $separateur): array
    {
        $result = PointsVenteRegles::charger($csv, $mapping, $separateur);
        if ($result['lignes'] === []) {
            return ['pris' => 0, 'refus' => $result['refus']];
        }
        if (!add_option('imagine_vente_import_en_cours', '1', '', false)) {
            throw new RuntimeException('import_en_cours');
        }
        $created = [];
        $switched = false;
        try {
            $old = get_option(self::ACTIFS, []);
            try {
                $identical = self::lignes() === $result['lignes'];
            } catch (RuntimeException $e) {
                $identical = false;
            }
            if ($identical) {
                $clean = self::nettoyer();
                return ['pris' => count($result['lignes']), 'refus' => $result['refus']]
                    + ($clean ? [] : ['remplace' => false, 'nettoyage_complet' => false]);
            }
            foreach ($result['lignes'] as $row) {
                $id = wp_insert_post(['post_type' => self::TYPE, 'post_status' => 'private',
                    'post_title' => wp_slash($row['nom']), 'post_content' => '', 'post_excerpt' => '',
                    'post_author' => 0, 'post_parent' => 0,
                    'meta_input' => wp_slash(['imagine_vente_ligne' => $row])], true);
                if (is_wp_error($id) || !$id) {
                    throw new RuntimeException('stockage_refuse');
                }
                $created[] = (int) $id;
                if (get_post_meta($id, 'imagine_vente_ligne', true) !== $row) {
                    throw new RuntimeException('stockage_refuse');
                }
            }
            // Persister la reprise AVANT de retirer les anciens IDs de la liste active.
            self::retenirNettoyage($old);
            update_option(self::ACTIFS, $created, false);
            if (get_option(self::ACTIFS) !== $created) {
                throw new RuntimeException('bascule_refusee');
            }
            $switched = true;
            $clean = self::nettoyer();
            return ['pris' => count($created), 'refus' => $result['refus']]
                + ($clean ? [] : ['remplace' => true, 'nettoyage_complet' => false]);
        } finally {
            if (!$switched) {
                // Une suppression de préparation peut elle aussi échouer : conserver sa reprise.
                self::retenirNettoyage($created);
                foreach ($created as $id) {
                    wp_delete_post($id, true);
                }
            }
            delete_option('imagine_vente_import_en_cours');
        }
    }

    public static function afficher(string $query): string
    {
        $html = '<form method="get"><label for="imagine-localite">' . esc_html__('Localité ou code postal exact', 'imagine-site')
            . '</label> <input id="imagine-localite" name="localite" value="' . esc_attr($query) . '"> <button type="submit">'
            . esc_html__('Rechercher', 'imagine-site') . '</button></form>';
        try {
            $rows = PointsVenteRegles::rechercher(self::lignes(), $query);
            $html .= '<p role="status">' . esc_html(sprintf(__('%d points de vente', 'imagine-site'), count($rows))) . '</p>';
            $html .= '<ul id="imagine-points-vente">';
            foreach ($rows as $row) {
                $html .= '<li><strong>' . esc_html($row['nom']) . '</strong><br>' . esc_html($row['adresse']) . '<br>'
                    . esc_html($row['postal'] . ' ' . $row['localite']);
                foreach (['personne' => __('Contact', 'imagine-site'), 'telephone' => __('Téléphone', 'imagine-site')] as $key => $label) {
                    if (array_key_exists($key, self::configuration()['mapping']) && isset($row[$key]) && $row[$key] !== '') {
                        $html .= '<br>' . esc_html($label . ' : ' . $row[$key]);
                    }
                }
                $html .= '</li>';
            }
            $html .= '</ul>';
        } catch (Throwable $e) {
            $html .= '<p role="status">' . esc_html__('Liste temporairement indisponible.', 'imagine-site') . '</p>';
        }
        if (self::configuration()['carte'] === '1') {
            $html .= '<div id="imagine-carte-emplacement" role="region" aria-label="' . esc_attr__('Emplacement de la carte', 'imagine-site')
                . '"><p>' . esc_html__('Carte non raccordée — aucun fournisseur choisi.', 'imagine-site') . '</p></div>';
        }
        return $html;
    }

    public static function libelleRefus(string $code): string
    {
        return match ($code) {
            'nombre_colonnes' => __('Nombre de colonnes incorrect.', 'imagine-site'),
            'champ_requis' => __('Champ obligatoire manquant.', 'imagine-site'),
            'syntaxe_csv' => __('Syntaxe CSV incorrecte.', 'imagine-site'),
            'doublon' => __('Ligne en double.', 'imagine-site'),
            'champ_invalide' => __('Champ invalide.', 'imagine-site'),
            default => __('Ligne refusée.', 'imagine-site'),
        };
    }

    public static function administration(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Accès refusé.', 'imagine-site'), '', ['response' => 403]);
        }
        $config = self::configuration();
        echo '<div class="wrap"><h1>' . esc_html__('Points de vente', 'imagine-site') . '</h1>';
        if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
            try {
                if (!isset($_POST['_b10']) || !is_string($_POST['_b10'])
                    || !wp_verify_nonce(wp_unslash($_POST['_b10']), 'imagine_points_vente')
                ) {
                    throw new InvalidArgumentException('nonce');
                }
                if (($_POST['b10_action'] ?? '') === 'enregistrer') {
                    $raw = isset($_POST['mapping']) && is_string($_POST['mapping']) ? wp_unslash($_POST['mapping']) : '';
                    $mapping = json_decode($raw, true, 16, JSON_THROW_ON_ERROR);
                    if (!is_array($mapping)) {
                        throw new InvalidArgumentException('mapping');
                    }
                    PointsVenteRegles::mapping($mapping);
                    $delimiter = isset($_POST['separateur']) && is_string($_POST['separateur']) ? wp_unslash($_POST['separateur']) : '';
                    if (!in_array($delimiter, [';', ',', "\t"], true)) {
                        throw new InvalidArgumentException('separateur');
                    }
                    $config = ['mapping' => $mapping, 'separateur' => $delimiter, 'carte' => self::carte($_POST['carte'] ?? null)];
                    update_option(self::CONFIG, $config, false);
                    if (get_option(self::CONFIG) !== $config) {
                        throw new RuntimeException('configuration');
                    }
                    echo '<p role="status">' . esc_html__('Configuration enregistrée.', 'imagine-site') . '</p>';
                } elseif (($_POST['b10_action'] ?? '') === 'importer') {
                    $file = $_FILES['csv'] ?? [];
                    if (($file['error'] ?? -1) !== UPLOAD_ERR_OK || !is_string($file['tmp_name'] ?? null)
                        || !is_uploaded_file($file['tmp_name']) || filesize($file['tmp_name']) > 2097152
                    ) {
                        throw new InvalidArgumentException('fichier');
                    }
                    $csv = file_get_contents($file['tmp_name']);
                    if ($csv === false) {
                        throw new RuntimeException('lecture');
                    }
                    $result = self::importer($csv, $config['mapping'], $config['separateur']);
                    echo '<p role="status">' . esc_html(sprintf(__('%1$d lignes prises ; %2$d refusées.', 'imagine-site'), $result['pris'], count($result['refus']))) . '</p><ul>';
                    foreach ($result['refus'] as $refusal) {
                        echo '<li>' . esc_html(sprintf(__('Ligne %1$d : %2$s', 'imagine-site'), $refusal['ligne'], self::libelleRefus($refusal['motif']))) . '</li>';
                    }
                    echo '</ul>';
                } else {
                    throw new InvalidArgumentException('action');
                }
            } catch (Throwable $e) {
                echo '<p role="alert">' . esc_html__('Opération refusée : vérifier le nonce, la correspondance ou le CSV. Aucune donnée du fichier n’est reproduite.', 'imagine-site') . '</p>';
            }
        }
        echo '<form method="post">';
        wp_nonce_field('imagine_points_vente', '_b10');
        echo '<p><label for="imagine-mapping">' . esc_html__('Correspondance JSON (nom, adresse, localite, postal ; personne et telephone facultatifs)', 'imagine-site') . '</label><br>';
        echo '<textarea id="imagine-mapping" name="mapping" rows="8" cols="70">' . esc_textarea(wp_json_encode($config['mapping'], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)) . '</textarea></p>';
        echo '<p><label>' . esc_html__('Séparateur', 'imagine-site') . ' <select name="separateur">';
        foreach ([';' => ';', ',' => ',', "\t" => __('Tabulation', 'imagine-site')] as $value => $label) {
            echo '<option value="' . esc_attr($value) . '"' . selected($config['separateur'], $value, false) . '>' . esc_html($label) . '</option>';
        }
        echo '</select></label></p><p><label>' . esc_html__('Afficher une carte', 'imagine-site') . ' <select name="carte">';
        foreach (['0' => __('Non (défaut)', 'imagine-site'), '1' => __('Oui : emplacement sans tiers', 'imagine-site')] as $value => $label) {
            echo '<option value="' . esc_attr((string) $value) . '"' . selected($config['carte'], (string) $value, false) . '>' . esc_html($label) . '</option>';
        }
        echo '</select></label></p><button name="b10_action" value="enregistrer">' . esc_html__('Enregistrer', 'imagine-site') . '</button></form>';
        echo '<h2>' . esc_html__('Remplacer la liste par un CSV UTF-8', 'imagine-site') . '</h2><p>' . esc_html__('Le fichier n’est pas conservé. Enregistrer la correspondance avant le chargement.', 'imagine-site') . '</p><form method="post" enctype="multipart/form-data">';
        wp_nonce_field('imagine_points_vente', '_b10');
        echo '<label>' . esc_html__('Fichier CSV', 'imagine-site') . ' <input type="file" name="csv" accept=".csv,text/csv" required></label> <button name="b10_action" value="importer">'
            . esc_html__('Charger et remplacer', 'imagine-site') . '</button></form></div>';
    }
}
