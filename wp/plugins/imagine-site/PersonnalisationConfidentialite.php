<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Callbacks natifs supplémentaires ; C21 reste intégralement inchangé. */
final class PersonnalisationConfidentialite
{
    public static function register(): void
    {
        add_filter('wp_privacy_personal_data_exporters', static function (array $items): array {
            $items['imagine-personnalisation'] = ['exporter_friendly_name' => __('Personnalisation Imagine', 'imagine-site'),
                'callback' => [self::class, 'exporter']];
            return $items;
        }, 120);
        add_filter('wp_privacy_personal_data_erasers', static function (array $items): array {
            $items['imagine-personnalisation'] = ['eraser_friendly_name' => __('Personnalisation Imagine', 'imagine-site'),
                'callback' => [self::class, 'effacer']];
            return $items;
        }, 120);
        add_action('delete_user', static function (int $id): void {
            PersonnalisationReglages::reserverReponses(Personnalisation::reponses($id));
        }, 6);
    }

    public static function exporter(string $email, int $page = 1): array
    {
        $empty = ['data' => [], 'done' => true];
        $user = is_email($email) ? get_user_by('email', $email) : false;
        if (!$user || $page !== 1) { return $empty; }
        $fields = [];
        foreach ([Personnalisation::META => __('Étiquettes et dates', 'imagine-site'),
            Personnalisation::CONSENTEMENT => __('Consentement distinct et date', 'imagine-site')] as $key => $label) {
            if (metadata_exists('user', $user->ID, $key)) {
                $fields[] = ['name' => $label, 'value' => wp_json_encode(get_user_meta($user->ID, $key, true), JSON_UNESCAPED_UNICODE)];
            }
        }
        if (!$fields) { return $empty; }
        return ['data' => [['group_id' => 'imagine-personnalisation', 'group_label' => __('Personnalisation Imagine', 'imagine-site'),
            'item_id' => 'imagine-personnalisation-' . $user->ID, 'data' => $fields]], 'done' => true];
    }

    public static function effacer(string $email, int $page = 1): array
    {
        $result = ['items_removed' => false, 'items_retained' => false, 'messages' => [], 'done' => true];
        $user = is_email($email) ? get_user_by('email', $email) : false;
        if (!$user || $page !== 1) { return $result; }
        global $wpdb;
        $lock = 'imagine_personnalisation_' . $user->ID;
        if ((int)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 3)', $lock)) !== 1) {
            return array_replace($result, ['items_retained' => true, 'messages' => [__('Personnalisation occupée : réessayez.', 'imagine-site')]]);
        }
        try {
            wp_cache_delete($user->ID, 'user_meta');
            PersonnalisationReglages::reserverReponses(Personnalisation::reponses($user->ID));
            foreach ([Personnalisation::META, Personnalisation::CONSENTEMENT] as $key) {
                if (metadata_exists('user', $user->ID, $key)) {
                    delete_user_meta($user->ID, $key);
                    wp_cache_delete($user->ID, 'user_meta');
                    if (metadata_exists('user', $user->ID, $key)) { $result['items_retained'] = true; }
                    else { $result['items_removed'] = true; }
                }
            }
        } catch (\InvalidArgumentException) {
            $result['items_retained'] = true;
        } finally { $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock)); }
        if ($result['items_retained']) { $result['messages'][] = __('Personnalisation non entièrement effacée : réessayez.', 'imagine-site'); }
        return $result;
    }
}
