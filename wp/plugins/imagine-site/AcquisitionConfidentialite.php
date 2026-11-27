<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Raccord C21 aux outils natifs. L'effacement est la seule exception à l'immutabilité. */
final class AcquisitionConfidentialite
{
    public static function register(): void
    {
        add_filter('wp_privacy_personal_data_exporters', static function (array $items): array {
            $items['imagine-acquisition'] = ['exporter_friendly_name' => __('Source d’acquisition déclarée', 'imagine-site'),
                'callback' => [self::class, 'exporter']];
            return $items;
        }, 160);
        add_filter('wp_privacy_personal_data_erasers', static function (array $items): array {
            $items['imagine-acquisition'] = ['eraser_friendly_name' => __('Source d’acquisition déclarée', 'imagine-site'),
                'callback' => [self::class, 'effacer']];
            return $items;
        }, 160);
        add_action('delete_user', static function (int $id): void {
            $user = get_userdata($id);
            if (!$user) {
                return;
            }
            do {
                $result = self::effacer($user->user_email);
                if ($result['items_retained']) {
                    wp_die(esc_html__('Suppression refusée : source d’acquisition non effacée.', 'imagine-site'));
                }
            } while (!$result['done']);
        }, 8);
    }

    /** Une lecture SQL invalide ne devient jamais une liste vide ou un chiffre zéro. */
    public static function lignes(?int $owner = null, bool $seen = false): array|\WP_Error
    {
        global $wpdb;
        $prefix = $seen ? Acquisition::VUE : Acquisition::REPONSE;
        $rows = $wpdb->get_results($wpdb->prepare(
            "SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_name",
            $wpdb->esc_like($prefix) . '%'
        ), ARRAY_A);
        if ($wpdb->last_error || !is_array($rows)) {
            return new \WP_Error('imagine_acquisition_lecture', __('Lecture des déclarations impossible.', 'imagine-site'));
        }
        $out = [];
        foreach ($rows as $row) {
            $data = maybe_unserialize($row['option_value']);
            if (
                !is_array($data) || !isset($data['commande'], $data['date']) || !is_int($data['commande'])
                || $data['commande'] < 1 || $row['option_name'] !== $prefix . $data['commande']
                || !is_string($data['date']) || !preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/D', $data['date'])
            ) {
                return new \WP_Error('imagine_acquisition_format', __('Déclaration illisible : lecture incomplète.', 'imagine-site'));
            }
            if (($data['etat'] ?? '') === 'effacee') {
                continue;
            }
            if (
                !isset($data['compte']) || !is_int($data['compte']) || $data['compte'] < 1
                || (!$seen && (!isset($data['choix'], $data['libelle'])
                    || AcquisitionRegles::liste([$data['choix'] => $data['libelle']]) === null))
            ) {
                return new \WP_Error('imagine_acquisition_format', __('Déclaration illisible : lecture incomplète.', 'imagine-site'));
            }
            if ($owner === null || $data['compte'] === $owner) {
                $out[] = $data;
            }
        }
        return $out;
    }

    private static function compte(string $email): object|false
    {
        global $wpdb;
        if (!is_email($email)) {
            return false;
        }
        $wpdb->last_error = '';
        $user = get_user_by('email', $email);
        return $wpdb->last_error ? new \WP_Error('imagine_acquisition_compte', __('Lecture du compte impossible.', 'imagine-site')) : $user;
    }

    public static function exporter(string $email, int $page = 1): array|\WP_Error
    {
        $user = self::compte($email);
        if (is_wp_error($user)) {
            return $user;
        }
        if (!$user) {
            return ['data' => [], 'done' => true];
        }
        $answers = self::lignes((int) $user->ID);
        $seen = self::lignes((int) $user->ID, true);
        if (is_wp_error($answers) || is_wp_error($seen)) {
            return new \WP_Error('imagine_acquisition_export', __('Export incomplet : déclarations illisibles.', 'imagine-site'));
        }
        $data = [];
        foreach ([['reponse', $answers], ['proposition', $seen]] as [$kind, $rows]) {
            foreach ($rows as $row) {
                $fields = [['name' => __('Commande', 'imagine-site'), 'value' => (string) $row['commande']],
                    ['name' => __('Date UTC', 'imagine-site'), 'value' => $row['date']]];
                if ($kind === 'reponse') {
                    $fields[] = ['name' => __('Réponse déclarée', 'imagine-site'), 'value' => $row['libelle']];
                }
                $data[] = ['group_id' => 'imagine-acquisition', 'group_label' => __('Source d’acquisition déclarée', 'imagine-site'),
                    'item_id' => 'imagine-acquisition-' . $kind . '-' . $row['commande'], 'data' => $fields];
            }
        }
        $source = get_user_meta($user->ID, Acquisition::SOURCE, true);
        if ($source !== '') {
            $data[] = ['group_id' => 'imagine-acquisition', 'group_label' => __('Source d’acquisition déclarée', 'imagine-site'),
                'item_id' => 'imagine-acquisition-compte', 'data' => [['name' => __('Source du compte', 'imagine-site'),
                    'value' => is_array($source) ? wp_json_encode($source, JSON_UNESCAPED_UNICODE) : (string) $source]]];
        }
        return ['data' => array_slice($data, (max(1, $page) - 1) * 50, 50), 'done' => max(1, $page) * 50 >= count($data)];
    }

    public static function effacer(string $email, int $page = 1): array
    {
        $result = ['items_removed' => false, 'items_retained' => false, 'messages' => [], 'done' => false];
        $user = self::compte($email);
        if (is_wp_error($user)) {
            return array_replace($result, ['items_retained' => true, 'messages' => [__('Lecture du compte impossible.', 'imagine-site')]]);
        }
        if (!$user) {
            return array_replace($result, ['done' => true]);
        }
        global $wpdb;
        $owner = (int) $user->ID;
        $lock = 'imagine_c27_' . substr(hash('sha256', DB_NAME . ':' . $wpdb->prefix . ':' . $owner), 0, 40);
        $locked = (int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 3)', $lock)) === 1;
        $keys = [];
        try {
            if (!$locked) {
                throw new \RuntimeException('Verrou indisponible');
            }
            foreach ([Acquisition::REPONSE => false, Acquisition::VUE => true] as $prefix => $seen) {
                $rows = self::lignes($owner, $seen);
                if (is_wp_error($rows)) {
                    throw new \RuntimeException('Lecture impossible');
                }
                foreach (array_slice($rows, 0, 50) as $row) {
                    $keys[$prefix . $row['commande']] = $row;
                }
            }
            if ($wpdb->query('START TRANSACTION') === false) {
                throw new \RuntimeException('Transaction impossible');
            }
            foreach ($keys as $key => $row) {
                // La commande ne pourra pas être interrogée à nouveau ; plus de réponse ni de compte.
                $tombstone = ['commande' => $row['commande'], 'date' => $row['date'], 'etat' => 'effacee'];
                update_option($key, $tombstone, false);
                if (get_option($key) !== $tombstone) {
                    throw new \RuntimeException('Déclaration non effacée');
                }
                $result['items_removed'] = true;
            }
            if (get_user_meta($owner, Acquisition::SOURCE, true) !== '') {
                delete_user_meta($owner, Acquisition::SOURCE);
                $result['items_removed'] = true;
            }
            if (get_user_meta($owner, Acquisition::SOURCE, true) !== '' || $wpdb->query('COMMIT') === false) {
                throw new \RuntimeException('Source non effacée');
            }
            $remaining = self::lignes($owner);
            $remainingSeen = self::lignes($owner, true);
            $result['done'] = $remaining === [] && $remainingSeen === [];
            if (is_wp_error($remaining) || is_wp_error($remainingSeen)) {
                throw new \RuntimeException('Relecture impossible');
            }
        } catch (\Throwable) {
            $wpdb->query('ROLLBACK');
            foreach (array_keys($keys) as $key) {
                wp_cache_delete($key, 'options');
            }
            wp_cache_delete($owner, 'user_meta');
            $result['items_retained'] = true;
            $result['done'] = false;
            $result['messages'][] = __('Effacement incomplet : réessayez.', 'imagine-site');
        } finally {
            if ($locked) {
                $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
            }
        }
        return $result;
    }
}
