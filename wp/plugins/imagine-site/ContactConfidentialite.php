<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Déclaration additive aux outils natifs utilisés par C21 ; recherche par adresse. */
final class ContactConfidentialite
{
    public static function register(): void
    {
        add_filter('wp_privacy_personal_data_exporters', static function (array $items): array {
            $items['imagine-contacts'] = ['exporter_friendly_name' => __('Messages de contact', 'imagine-site'), 'callback' => [self::class, 'exporter']];
            return $items;
        }, 150);
        add_filter('wp_privacy_personal_data_erasers', static function (array $items): array {
            $items['imagine-contacts'] = ['eraser_friendly_name' => __('Messages de contact', 'imagine-site'), 'callback' => [self::class, 'effacer']];
            return $items;
        }, 150);
    }

    public static function exporter(string $email, int $page = 1): array|\WP_Error
    {
        $ids = is_email(SujetRegles::email($email)) ? Contact::ids($email) : [];
        if ($ids === null) {
            return new \WP_Error('imagine_contact_lecture', __('Lecture des messages de contact impossible : réessayez cette page.', 'imagine-site'));
        }
        $data = [];
        foreach (array_slice($ids, (max(1, $page) - 1) * 50, 50) as $id) {
            $fields = [];
            foreach (Contact::CHAMPS as $key => $label) {
                $fields[] = ['name' => __($label, 'imagine-site'), 'value' => (string) get_post_meta($id, 'imagine_contact_' . $key, true)];
            }
            $data[] = ['group_id' => 'imagine-contacts', 'group_label' => __('Messages de contact', 'imagine-site'), 'item_id' => 'imagine-contact-' . $id, 'data' => $fields];
        }
        return ['data' => $data, 'done' => max(1, $page) * 50 >= count($ids)];
    }

    public static function effacer(string $email, int $page = 1): array
    {
        $ids = is_email(SujetRegles::email($email)) ? Contact::ids($email) : [];
        $result = ['items_removed' => false, 'items_retained' => false, 'messages' => [], 'done' => true];
        if ($ids === null) {
            return array_replace($result, ['items_retained' => true, 'done' => false, 'messages' => [__('Lecture des messages de contact impossible : réessayez.', 'imagine-site')]]);
        }
        // Témoin durable AVANT suppression : l'adresse peut disparaître avant le texte.
        $option = 'imagine_contact_effacement_' . hash('sha256', SujetRegles::email($email));
        $pending = get_option($option, []);
        $batch = array_slice(array_values(array_unique([...$pending, ...$ids])), 0, 50);
        $pending = array_values(array_unique([...$pending, ...$batch]));
        if ($pending !== []) {
            update_option($option, $pending, false);
            if (get_option($option, []) !== $pending) {
                return array_replace($result, ['items_retained' => true, 'done' => false,
                    'messages' => [__('Témoin de nettoyage contact indisponible : réessayez.', 'imagine-site')]]);
            }
        }
        foreach ($batch as $id) {
            $post = get_post($id);
            if ($post && $post->post_type !== Contact::TYPE) {
                $result['items_retained'] = true;
                continue;
            }
            if ($post) {
                wp_delete_post($id, true);
            } else {
                // Reprise d'un effacement partiel : uniquement les clés de ce contact connu.
                foreach (self::metas($id) ?? [] as $key) {
                    delete_post_meta($id, $key);
                }
            }
            if (get_post($id) || self::metas($id) !== []) {
                $result['items_retained'] = true;
            } else {
                $result['items_removed'] = true;
                $pending = array_values(array_diff($pending, [$id]));
            }
        }
        if ($pending === []) {
            delete_option($option);
        } else {
            update_option($option, $pending, false);
        }
        $remaining = Contact::ids($email);
        $result['done'] = $remaining === [] && !$result['items_retained'] && get_option($option, []) === [];
        $result['items_retained'] = !$result['done'];
        if (!$result['done']) {
            $result['messages'][] = __('Effacement des messages de contact incomplet : réessayez.', 'imagine-site');
        }
        return $result;
    }

    /** Lecture SQL directe : ni jointure sur le post disparu, ni cache de méta. */
    private static function metas(int $id): ?array
    {
        global $wpdb;
        $keys = $wpdb->get_col($wpdb->prepare("SELECT meta_key FROM {$wpdb->postmeta} WHERE post_id=%d AND LEFT(meta_key,16)=%s", $id, 'imagine_contact_'));
        return $wpdb->last_error !== '' ? null : $keys;
    }
}
