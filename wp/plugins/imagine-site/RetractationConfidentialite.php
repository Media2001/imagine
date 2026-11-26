<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Extension additive des outils natifs ; ne modifie pas la politique de conservation C21. */
final class RetractationConfidentialite
{
    public static function register(): void
    {
        add_filter('wp_privacy_personal_data_exporters', static function (array $items): array {
            $items['imagine-retractation'] = ['exporter_friendly_name' => __('Demandes de rétractation', 'imagine-site'), 'callback' => [self::class, 'exporter']];
            return $items;
        }, 140);
        add_filter('wp_privacy_personal_data_erasers', static function (array $items): array {
            $items['imagine-retractation'] = ['eraser_friendly_name' => __('Demandes de rétractation', 'imagine-site'), 'callback' => [self::class, 'effacer']];
            return $items;
        }, 140);
        add_action('delete_user', static function (int $id): void {
            $user = get_userdata($id);
            if (!$user) {
                return;
            }
            do {
                $result = self::effacer($user->user_email);
                if ($result['items_retained']) {
                    wp_die(esc_html__('Suppression refusée : rétractations non entièrement nettoyées.', 'imagine-site'));
                }
            } while (!$result['done']);
        }, 7);
    }

    /** null n'est jamais confondu avec une liste vide après une panne SQL. */
    public static function lignes(?int $owner = null): array|\WP_Error
    {
        global $wpdb;
        $rows = $wpdb->get_results($wpdb->prepare(
            "SELECT m.comment_id,m.meta_value FROM {$wpdb->commentmeta} m INNER JOIN {$wpdb->comments} c ON c.comment_ID=m.comment_id WHERE m.meta_key=%s ORDER BY m.comment_id",
            Retractation::META
        ), ARRAY_A);
        if ($wpdb->last_error || !is_array($rows)) {
            return new \WP_Error('imagine_retractation_lecture', __('Lecture des demandes impossible : réessayez cette page.', 'imagine-site'));
        }
        $out = [];
        foreach ($rows as $row) {
            $data = maybe_unserialize($row['meta_value']);
            if (!is_array($data) || !isset($data['commande'], $data['compte'], $data['date'], $data['raison'], $data['note'])
                || (int)$data['note'] !== (int)$row['comment_id']) {
                return new \WP_Error('imagine_retractation_format', __('Demande illisible : export incomplet.', 'imagine-site'));
            }
            if ($owner === null || (int)$data['compte'] === $owner) {
                $out[] = $data;
            }
        }
        return $out;
    }

    private static function personnelles(string $email): array|\WP_Error
    {
        global $wpdb;
        if (!is_email($email)) {
            return [];
        }
        $wpdb->last_error = '';
        $user = get_user_by('email', $email);
        if ($wpdb->last_error) {
            return new \WP_Error('imagine_retractation_compte', __('Lecture du compte impossible.', 'imagine-site'));
        }
        return $user ? self::lignes((int)$user->ID) : [];
    }

    public static function exporter(string $email, int $page = 1): array|\WP_Error
    {
        $rows = self::personnelles($email);
        if (is_wp_error($rows)) {
            return $rows;
        }
        $data = [];
        foreach (array_slice($rows, (max(1, $page) - 1) * 50, 50) as $row) {
            $data[] = ['group_id' => 'imagine-retractation', 'group_label' => __('Demandes de rétractation', 'imagine-site'),
                'item_id' => 'imagine-retractation-' . $row['note'],
                'data' => [['name' => __('Commande', 'imagine-site'), 'value' => (string)$row['commande']],
                    ['name' => __('Date UTC', 'imagine-site'), 'value' => $row['date']],
                    ['name' => __('Motif facultatif', 'imagine-site'), 'value' => $row['raison']]]];
        }
        return ['data' => $data, 'done' => max(1, $page) * 50 >= count($rows)];
    }

    public static function effacer(string $email, int $page = 1): array
    {
        $result = ['items_removed' => false, 'items_retained' => false, 'messages' => [], 'done' => false];
        $rows = self::personnelles($email);
        if (is_wp_error($rows)) {
            return array_replace($result, ['items_retained' => true, 'messages' => [__('Lecture impossible : effacement incomplet.', 'imagine-site')]]);
        }
        global $wpdb;
        foreach (array_slice($rows, 0, 50) as $row) {
            $lock = 'imagine_retractation_' . $row['commande'];
            $key = Retractation::JOURNAL . $row['commande'];
            if ((int)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 3)', $lock)) !== 1) {
                $result['items_retained'] = true;
                break;
            }
            try {
                if ($wpdb->query('START TRANSACTION') === false) {
                    throw new \RuntimeException('Transaction impossible');
                }
                $event = get_option($key, null);
                if (!is_array($event) || !is_array($event['apres'] ?? null)) {
                    throw new \RuntimeException('Journal illisible');
                }
                if (!wp_delete_comment((int)$row['note'], true) || get_comment((int)$row['note'])) {
                    throw new \RuntimeException('Note non effacée');
                }
                // La date et la référence métier restent : empêchent de redéposer après effacement.
                // Aucun motif, identifiant de compte ni login dans cette trace dépersonnalisée.
                $event['qui_id'] = 0;
                $event['qui_login'] = 'efface';
                $event['apres']['note'] = 0;
                update_option($key, $event, false);
                if (get_option($key) !== $event || $wpdb->query('COMMIT') === false) {
                    throw new \RuntimeException('Journal non nettoyé');
                }
                $result['items_removed'] = true;
            } catch (\Throwable) {
                $wpdb->query('ROLLBACK');
                wp_cache_delete($key, 'options');
                wp_cache_delete('alloptions', 'options');
                clean_comment_cache((int)$row['note']);
                wp_cache_delete((int)$row['note'], 'comment_meta');
                $result['items_retained'] = true;
                break;
            } finally {
                $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
            }
        }
        $remaining = self::personnelles($email);
        $result['done'] = is_array($remaining) && $remaining === [] && !$result['items_retained'];
        if (is_wp_error($remaining) || $result['items_retained']) {
            $result['items_retained'] = true;
            $result['messages'][] = __('Effacement incomplet : réessayez.', 'imagine-site');
        }
        return $result;
    }
}
