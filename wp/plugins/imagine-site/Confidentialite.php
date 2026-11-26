<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Uniquement des hooks des outils de confidentialité WordPress ; aucun écran parallèle. */
final class Confidentialite
{
    private const META = ['imagine_sans_email', 'imagine_email_confirme'];
    private const JOURNAL = 'imagine_reglages_journal_';
    private const JOURNAUX = [self::JOURNAL, 'imagine_extraction_journal_', 'imagine_envoi_export_journal_'];
    private const LIMIT = 50;

    public static function register(): void
    {
        add_filter('wp_privacy_personal_data_exporters', static function (array $exporters): array {
            // Aucun jeton ou référence de moyen de paiement dans une archive Imagine.
            unset($exporters['woocommerce-customer-tokens']);
            $exporters['imagine-site'] = [
                'exporter_friendly_name' => __('Données Imagine', 'imagine-site'),
                'callback' => [self::class, 'exporter'],
            ];
            return $exporters;
        }, 100);
        add_filter('wp_privacy_personal_data_erasers', static function (array $erasers): array {
            // Dernier : un nettoyage natif de souscription peut produire une observation C13.
            $erasers['imagine-site'] = [
                'eraser_friendly_name' => __('Données Imagine', 'imagine-site'),
                'callback' => [self::class, 'effacer'],
            ];
            return $erasers;
        }, 100);
        // Avant l'agrégateur natif (priorité 10), jamais après la génération de l'archive.
        add_filter('wp_privacy_personal_data_export_page', [self::class, 'filtrerPage'], 5, 7);
        add_action('wp_privacy_personal_data_export_file_created', [self::class, 'filtrerArchive'], 100, 5);
        foreach (['order', 'subscription'] as $type) {
            add_filter('woocommerce_privacy_export_' . $type . '_personal_data', [self::class, 'commerce'], 20, 2);
        }
        add_action('delete_user', [self::class, 'supprimerCompte'], 5);
        add_filter('imagine_envoi_conserver_observation', [self::class, 'conserverObservation'], 10, 2);
        add_filter('imagine_envoi_donnees_observation', [self::class, 'anonymiserObservation']);
    }

    /** Réutilise la demande d'effacement terminée native : pas de marqueur personnel ni durée ajoutée. */
    public static function conserverObservation(bool $conserver, array $data): bool
    {
        $id = (int) ($data['user'] ?? 0);
        if (!$conserver || !$id || !get_userdata($id)) {
            return false;
        }
        return !self::demandeTerminee($id);
    }

    private static function demandeTerminee(int $id): bool
    {
        global $wpdb;
        $done = $wpdb->get_var($wpdb->prepare(
            "SELECT ID FROM {$wpdb->posts} WHERE post_type='user_request' "
                . "AND post_name='remove_personal_data' AND post_status='request-completed' "
                . 'AND post_author=%d LIMIT 1',
            $id
        ));
        if ($wpdb->last_error) {
            throw new \RuntimeException('État de confidentialité indisponible.');
        }
        return $done !== null;
    }

    public static function anonymiserObservation(array $data): array
    {
        $ids = array_map('intval', array_column($data['beneficiaires'] ?? [], 'id'));
        $relations = $data['relation_native'] ?? [];
        if (isset($relations['recipient_user'])) {
            $ids[] = (int) $relations['recipient_user'];
        } else {
            $ids = array_merge($ids, array_map('intval', array_column($relations, 'user_id')));
        }
        foreach (array_unique($ids) as $id) {
            if ($id > 0 && self::demandeTerminee($id)) {
                $event = ConfidentialiteRegles::retirerPostal(['donnees' => $data], $id);
                if ($event !== null) {
                    $data = $event['donnees'];
                }
            }
        }
        return $data;
    }

    private static function user(string $email): ?\WP_User
    {
        if (!is_email($email)) {
            return null;
        }
        $user = get_user_by('email', $email);
        return $user instanceof \WP_User ? $user : null;
    }

    /** Valeurs techniques .invalid neutralisées dans tous les exports, même les champs natifs. */
    private static function texte(mixed $value): string
    {
        $text = is_scalar($value) || $value === null ? (string) $value : wp_json_encode($value, JSON_UNESCAPED_UNICODE);
        return preg_replace(
            '/[a-z0-9.!#$%&\x27*+\/=?^_`{|}~-]+@[a-z0-9.-]+\.invalid\b/i',
            '[sans adresse électronique]',
            $text
        );
    }

    public static function filtrerPage(
        mixed $response,
        int $index,
        string $email,
        int $page,
        int $request,
        bool $send,
        string $key
    ): mixed {
        if (!is_array($response) || !isset($response['data']) || !is_array($response['data'])) {
            return $response;
        }
        foreach ($response['data'] as &$row) {
            $row['data'] = array_values(array_filter($row['data'], static fn ($f): bool => !preg_match(
                '/password|mot de passe|token|jeton|payment.*(?:method|reference)|moyen de paiement|transaction'
                    . '|(?:^|\s)notes?(?:\s|$)|iban|card.*(?:number|last)|numéro.*carte/i',
                (string) ($f['name'] ?? '')
            )));
            foreach ($row['data'] as &$field) {
                $field['value'] = self::texte($field['value']);
            }
            unset($field);
        }
        unset($row);
        return $response;
    }

    /** WordPress ajoute lui-même l'email de la demande au titre et au groupe « À propos ». */
    public static function filtrerArchive(string $archive, string $url, string $html, int $request, string $json): void
    {
        $zip = new \ZipArchive();
        try {
            if ($zip->open($archive) !== true) {
                throw new \RuntimeException('Archive indisponible.');
            }
            foreach (['index.html' => $html, 'export.json' => $json] as $member => $path) {
                $bytes = file_get_contents($path);
                if (!is_string($bytes)) {
                    throw new \RuntimeException('Rapport indisponible.');
                }
                $filtered = self::texte($bytes);
                if (
                    $filtered !== $bytes
                    && (!$zip->addFromString($member, $filtered)
                        || file_put_contents($path, $filtered) !== strlen($filtered))
                ) {
                    throw new \RuntimeException('Rapport non neutralisé.');
                }
            }
            if (!$zip->close()) {
                throw new \RuntimeException('Archive non enregistrée.');
            }
        } catch (\Throwable $e) {
            @$zip->close();
            wp_delete_file($archive);
            wp_delete_file($html);
            wp_delete_file($json);
            throw new \RuntimeException('Export refusé : neutralisation des adresses techniques impossible.', 0, $e);
        }
    }

    /** Propriétés ajoutées aux commandes : aucune copie brute des metas ni des notes. */
    public static function commerce(array $fields, \WC_Order $order): array
    {
        $numbers = [];
        foreach ($order->get_items() as $item) {
            $n = $item->get_meta('_imagine_achat_numero_id');
            if ($n !== '') {
                $numbers[] = (string) $n;
            }
        }
        if ($numbers) {
            $fields[] = ['name' => __('Imagine — numéros achetés', 'imagine-site'), 'value' => implode(', ', $numbers)];
        }
        foreach ([
            '_imagine_envoi_bloc_debut' => 'Début de bloc postal',
            '_imagine_acces_grace_debut' => 'Début de grâce',
            '_imagine_acces_grace_fin' => 'Fin de grâce',
        ] as $key => $name) {
            $v = $order->get_meta($key);
            if ($v !== '') {
                $fields[] = ['name' => __($name, 'imagine-site'), 'value' => self::texte($v)];
            }
        }
        return $fields;
    }

    private static function options(array $prefixes): array
    {
        global $wpdb;
        $where = [];
        $params = [];
        foreach ($prefixes as $prefix) {
            $where[] = 'option_name LIKE %s';
            $params[] = $wpdb->esc_like($prefix) . '%';
        }
        $query = 'SELECT option_name,option_value FROM ' . $wpdb->options
            . ' WHERE ' . implode(' OR ', $where) . ' ORDER BY option_id';
        $rows = $wpdb->get_results($wpdb->prepare($query, ...$params), ARRAY_A);
        if ($wpdb->last_error) {
            throw new \RuntimeException('Lecture de confidentialité indisponible.');
        }
        return $rows;
    }

    private static function audit(array $row, int $id): bool
    {
        return (int) ($row['qui_id'] ?? 0) === $id || ($row['option'] ?? '') === Justificatifs::PREFIX . $id;
    }

    private static function draft(array $row, \WP_User $user): bool
    {
        $c = $row['client'] ?? [];
        return (int) ($c['id'] ?? 0) === $user->ID || (int) ($row['qui'] ?? 0) === $user->ID
            || (isset($c['email']) && strcasecmp((string) $c['email'], $user->user_email) === 0);
    }

    /** Liste de travaux personnels. L'effaceur relit toujours le début : aucun saut après retrait. */
    private static function records(\WP_User $user): array
    {
        $id = $user->ID;
        $records = [];
        foreach (self::META as $key) {
            if (metadata_exists('user', $id, $key)) {
                $records[] = ['kind' => 'meta', 'key' => $key, 'value' => get_user_meta($id, $key, true)];
            }
        }
        foreach ([Decouverte::key($id), Justificatifs::PREFIX . $id] as $key) {
            $v = get_option($key, null);
            if ($v !== null) {
                $records[] = [
                    'kind' => str_starts_with($key, Justificatifs::PREFIX) ? 'justificatif' : 'decouverte',
                    'key' => $key, 'value' => $v,
                ];
            }
        }
        $prefixes = [EnvoiNatif::RELEVE, EnvoiNatif::GEL, ...self::JOURNAUX, '_transient_imagine_c16_brouillon_'];
        foreach (self::options($prefixes) as $row) {
            $v = maybe_unserialize($row['option_value']);
            $key = $row['option_name'];
            if (!is_array($v)) {
                continue;
            }
            $kind = null;
            if (str_starts_with($key, EnvoiNatif::RELEVE) && ConfidentialiteRegles::postal($v, $id) !== null) {
                $kind = 'postal';
            } elseif (str_starts_with($key, EnvoiNatif::GEL)) {
                foreach ($v['observations'] ?? [] as $event) {
                    if (ConfidentialiteRegles::postal($event, $id) !== null) {
                        $kind = 'gel';
                        break;
                    }
                }
            } elseif (str_starts_with($key, '_transient_imagine_c16_brouillon_') && self::draft($v, $user)) {
                $kind = 'brouillon';
            } elseif (self::audit($v, $id)) {
                $kind = 'audit';
            }
            if ($kind !== null) {
                $records[] = ['kind' => $kind, 'key' => $key, 'value' => $v];
            }
        }
        return $records;
    }

    public static function exporter(string $email, int $page = 1): array|\WP_Error
    {
        $user = self::user($email);
        if (!$user || $page < 1) {
            return ['data' => [], 'done' => true];
        }
        try {
            $all = self::records($user);
            $data = [];
            foreach (array_slice($all, ($page - 1) * self::LIMIT, self::LIMIT) as $row) {
                $v = $row['value'];
                $kind = $row['kind'];
                $fields = [];
                if ($kind === 'meta') {
                    $fields = [$row['key'] => $v];
                } elseif ($kind === 'decouverte') {
                    $fields = array_intersect_key($v, array_flip(['debut', 'reglages', 'articles']));
                } elseif ($kind === 'justificatif') {
                    $fields = array_intersect_key($v, array_flip([
                        'categorie', 'decision', 'fin', 'indisponible',
                    ]));
                    if (isset($v['blob'])) {
                        $bytes = file_get_contents(Justificatifs::chemin($v));
                        if (!is_string($bytes)) {
                            throw new \RuntimeException('Document indisponible.');
                        }
                        $fields['Document déposé (base64)'] = base64_encode($bytes);
                    }
                } elseif ($kind === 'postal') {
                    $fields = ConfidentialiteRegles::postal($v, $user->ID);
                } elseif ($kind === 'gel') {
                    $fields = ['numero' => $v['numero'], 'cloture' => $v['cloture'], 'observations' => []];
                    foreach ($v['observations'] as $event) {
                        if (($p = ConfidentialiteRegles::postal($event, $user->ID)) !== null) {
                            $fields['observations'][] = $p;
                        }
                    }
                } elseif ($kind === 'audit') {
                    $fields = ['quand_utc' => $v['quand_utc'] ?? ''];
                    if (($v['option'] ?? '') === Justificatifs::PREFIX . $user->ID) {
                        $fields['opérateur'] = $v['qui_login'] ?? '';
                        foreach (['avant', 'apres'] as $side) {
                            $fields[$side] = array_intersect_key(
                                (array) ($v[$side] ?? []),
                                array_flip(['categorie', 'decision', 'fin'])
                            );
                        }
                    }
                    if ((int) ($v['qui_id'] ?? 0) === $user->ID) {
                        $fields['opérateur'] = $v['qui_login'] ?? '';
                        $fields += array_intersect_key($v, array_flip([
                            'extraction', 'numero', 'lignes', 'provisoire',
                        ]));
                    }
                } elseif ($kind === 'brouillon') {
                    $fields = ['etape' => $v['etape'] ?? '', 'client' => array_intersect_key(
                        $v['client'] ?? [],
                        array_flip(['id', 'mode', 'nom', 'prenom', 'email', 'sans_email'])
                    )];
                    $fields['commande'] = array_intersect_key(
                        $v['commande'] ?? [],
                        array_flip(['adresse', 'produit', 'mode_paiement'])
                    );
                }
                $pairs = [];
                foreach ($fields as $name => $value) {
                    $pairs[] = ['name' => (string) $name, 'value' => self::texte($value)];
                }
                $data[] = ['group_id' => 'imagine-' . $kind, 'group_label' => __('Imagine — ', 'imagine-site') . $kind,
                    'item_id' => 'imagine-' . hash('sha256', $row['key']), 'data' => $pairs];
            }
            return ['data' => $data, 'done' => $page * self::LIMIT >= count($all)];
        } catch (\Throwable) {
            return new \WP_Error('imagine_export_indisponible', __(
                'Export Imagine incomplet : réessayez après correction du stockage.',
                'imagine-site'
            ));
        }
    }

    /** Compare-and-swap explicite : exception de confidentialité sur le gel, sans réécrire son métier. */
    private static function replace(string $key, mixed $old, mixed $new): void
    {
        global $wpdb;
        if ($new === null) {
            $sql = $wpdb->prepare(
                "DELETE FROM {$wpdb->options} WHERE option_name=%s AND BINARY option_value=BINARY %s",
                $key,
                maybe_serialize($old)
            );
        } else {
            $sql = $wpdb->prepare(
                "UPDATE {$wpdb->options} SET option_value=%s "
                    . 'WHERE option_name=%s AND BINARY option_value=BINARY %s',
                maybe_serialize($new),
                $key,
                maybe_serialize($old)
            );
        }
        if ($wpdb->query($sql) !== 1) {
            throw new \RuntimeException('Donnée modifiée ou stockage indisponible.');
        }
        wp_cache_delete($key, 'options');
        wp_cache_delete('alloptions', 'options');
        wp_cache_delete('notoptions', 'options');
        if (get_option($key, null) !== $new) {
            throw new \RuntimeException('Effacement non relu.');
        }
    }

    private static function retirer(array $row, \WP_User $user): void
    {
        $id = $user->ID;
        $v = $row['value'];
        $key = $row['key'];
        $new = null;
        if ($row['kind'] === 'meta') {
            delete_user_meta($id, $key);
            if (metadata_exists('user', $id, $key)) {
                throw new \RuntimeException('Marqueur non effacé.');
            }
            return;
        }
        if ($row['kind'] === 'justificatif') {
            Justificatifs::verrou($id, static function () use ($key, $v): void {
                if (get_option($key, null) !== $v) {
                    throw new \RuntimeException('Dossier modifié.');
                }
                Justificatifs::supprimerFichier($v);
                self::replace($key, $v, null);
            });
            return;
        }
        if ($row['kind'] === 'postal') {
            $new = ConfidentialiteRegles::retirerPostal($v, $id);
        } elseif ($row['kind'] === 'gel') {
            $new = $v;
            $events = [];
            foreach ($v['observations'] as $event) {
                $next = ConfidentialiteRegles::retirerPostal($event, $id);
                if ($next === null) {
                    unset($new['blocs'][(string) $event['donnees']['id']]);
                } else {
                    $events[] = $next;
                }
            }
            $new['observations'] = $events;
        } elseif ($row['kind'] === 'audit') {
            $new = $v;
            if (($v['option'] ?? '') === Justificatifs::PREFIX . $id) {
                $new['option'] = 'imagine_justificatif_efface';
                $new['avant'] = null;
                $new['apres'] = null;
            }
            if ((int) ($v['qui_id'] ?? 0) === $id) {
                $new['qui_id'] = 0;
                $new['qui_login'] = 'efface';
            }
        } elseif ($row['kind'] === 'brouillon') {
            $transient = substr($key, strlen('_transient_'));
            delete_transient($transient);
            if (get_transient($transient) !== false) {
                throw new \RuntimeException('Brouillon non effacé.');
            }
            return;
        }
        self::replace($key, $v, $new);
    }

    public static function effacer(string $email, int $page = 1): array
    {
        $result = ['items_removed' => false, 'items_retained' => false, 'messages' => [], 'done' => true];
        $user = self::user($email);
        if (!$user || $page < 1) {
            return $result;
        }
        try {
            $rows = array_slice(self::records($user), 0, self::LIMIT);
            foreach ($rows as $row) {
                self::retirer($row, $user);
                $result['items_removed'] = true;
            }
            $result['done'] = self::records($user) === [];
        } catch (\Throwable) {
            $result['items_retained'] = true;
            $result['messages'][] = __(
                'Effacement Imagine incomplet : donnée conservée ou modifiée, réessayez après correction du stockage.',
                'imagine-site'
            );
        }
        return $result;
    }

    public static function supprimerCompte(int $id): void
    {
        $user = get_userdata($id);
        if (!$user) {
            return;
        }
        do {
            $r = self::effacer($user->user_email);
            if ($r['items_retained']) {
                wp_die(
                    esc_html__('Suppression du compte refusée : nettoyage Imagine incomplet.', 'imagine-site'),
                    '',
                    ['response' => 409]
                );
            }
        } while (!$r['done']);
    }
}
