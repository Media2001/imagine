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
                $fields[] = ['name' => __($label, 'imagine-site'), 'value' => (string)get_post_meta($id, 'imagine_contact_' . $key, true)];
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
        // La collection rétrécit : toujours sa première tranche, pas l'offset export.
        foreach (array_slice($ids, 0, 50) as $id) {
            if (!wp_delete_post($id, true) || get_post($id)) {
                $result['items_retained'] = true;
            } else {
                $result['items_removed'] = true;
            }
        }
        $remaining = Contact::ids($email);
        $result['done'] = $remaining === [] && !$result['items_retained'];
        if (!$result['done']) {
            $result['messages'][] = __('Effacement des messages de contact incomplet : réessayez.', 'imagine-site');
        }
        return $result;
    }
}
