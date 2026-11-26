<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Extension additive des outils RGPD natifs, sans modifier C21. */
final class AgendaConfidentialite
{
    public static function register(): void
    {
        add_filter('wp_privacy_personal_data_exporters', static function (array $items): array {
            $items['imagine-agenda'] = ['exporter_friendly_name' => __('Inscriptions aux événements', 'imagine-site'), 'callback' => [self::class, 'exporter']];
            return $items;
        }, 130);
        add_filter('wp_privacy_personal_data_erasers', static function (array $items): array {
            $items['imagine-agenda'] = ['eraser_friendly_name' => __('Inscriptions aux événements', 'imagine-site'), 'callback' => [self::class, 'effacer']];
            return $items;
        }, 130);
    }

    public static function exporter(string $email, int $page = 1): array|\WP_Error
    {
        $ids = is_email($email) ? Agenda::inscriptions($email) : [];
        if ($ids === null) { return new \WP_Error('imagine_agenda_export_lecture', __('Lecture des inscriptions impossible : réessayez cette page.', 'imagine-site')); }
        $data = [];
        foreach (array_slice($ids, (max(1, $page) - 1) * 50, 50) as $id) {
            $p = get_post($id);
            $fields = [['name' => __('Événement', 'imagine-site'), 'value' => get_the_title($p->post_parent)]];
            foreach (['imagine_agenda_nom' => __('Nom', 'imagine-site'), 'imagine_agenda_email' => __('Adresse email', 'imagine-site'), 'imagine_agenda_consentement' => __('Consentement (1 = oui, 0 = non)', 'imagine-site'), 'imagine_agenda_date' => __('Date UTC', 'imagine-site')] as $key => $label) {
                $fields[] = ['name' => $label, 'value' => (string)get_post_meta($id, $key, true)];
            }
            $data[] = ['group_id' => 'imagine-agenda', 'group_label' => __('Inscriptions aux événements', 'imagine-site'), 'item_id' => 'imagine-agenda-' . $id, 'data' => $fields];
        }
        return ['data' => $data, 'done' => max(1, $page) * 50 >= count($ids)];
    }

    public static function effacer(string $email, int $page = 1): array
    {
        $ids = is_email($email) ? Agenda::inscriptions($email) : [];
        $result = ['items_removed' => false, 'items_retained' => false, 'messages' => [], 'done' => true];
        if ($ids === null) {
            return array_replace($result, ['items_retained' => true, 'done' => false, 'messages' => [__('Lecture des inscriptions impossible : réessayez.', 'imagine-site')]]);
        }
        foreach (array_slice($ids, 0, 50) as $id) {
            if (!wp_delete_post($id, true) || get_post($id)) {
                $result['items_retained'] = true;
            } else { $result['items_removed'] = true; }
        }
        $remaining = Agenda::inscriptions($email);
        $result['done'] = $remaining === [];
        if ($remaining === null || $result['items_retained']) {
            $result['done'] = false;
            $result['messages'][] = __('Effacement des inscriptions incomplet : réessayez.', 'imagine-site');
        }
        return $result;
    }
}
