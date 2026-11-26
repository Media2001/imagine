<?php
/** Recette B07 sur le vrai WPDB, callbacks RGPD natifs et reprise paginée. */
declare(strict_types=1);
use Imagine\Site\Agenda;
use Imagine\Site\AgendaConfidentialite;
$checks = []; $error = null; $owned = [];
$email = 'b07-correction-pagination@example.org';
if (Agenda::inscriptions($email) !== []) { throw new RuntimeException('Fixture préexistante'); }
$fixture = (int)get_option('imagine_b07_fixture')['rencontre'];
try {
    $checks['inscription_vrai_adaptateur'] = Agenda::inscrire($fixture, 'Fictif pagination B07', $email, false);
    $ids = Agenda::inscriptions($email); $owned = $ids ?? [];
    $checks['premier_temoin_persistant'] = count($owned) === 1;
    $ex = apply_filters('wp_privacy_personal_data_exporters', [])['imagine-agenda']['callback'];
    global $wpdb;
    $break = static function (string $sql) use ($wpdb): string {
        return str_contains($sql, "m.meta_key='imagine_agenda_email'") ? 'SELECT imagine_b07_column_absente FROM ' . $wpdb->posts . ' LIMIT 1' : $sql;
    };
    $prior = $wpdb->suppress_errors(true);
    add_filter('query', $break);
    try {
        $failed = call_user_func($ex, $email, 1);
        $checks['page1_panne_WP_Error'] = is_wp_error($failed) && $failed->get_error_code() === 'imagine_agenda_export_lecture';
        $er = AgendaConfidentialite::effacer($email);
        $checks['effacement_panne_incomplet'] = !$er['done'] && $er['items_retained'] && !$er['items_removed'];
    } finally { remove_filter('query', $break); $wpdb->suppress_errors($prior); }
    $retry = call_user_func($ex, $email, 1);
    $checks['reprise_page1_inscription_non_omise'] = !is_wp_error($retry) && $retry['done'] && array_column($retry['data'], 'item_id') === ['imagine-agenda-' . $owned[0]];
    for ($i = 0; $i < 120; $i++) {
        $id = wp_insert_post(['post_type' => Agenda::INSCRIPTION, 'post_status' => 'private', 'post_title' => 'Pagination fictive B07', 'post_parent' => $fixture,
            'meta_input' => ['imagine_agenda_email' => $email, 'imagine_agenda_nom' => 'Personnage fictif ' . $i, 'imagine_agenda_consentement' => '0', 'imagine_agenda_date' => gmdate(DATE_ATOM)]], true);
        if (is_wp_error($id) || !$id) { throw new RuntimeException('Insertion fixture impossible'); }
        $owned[] = $id;
    }
    $expected = array_map(static fn ($id) => 'imagine-agenda-' . $id, $owned);
    $checks['121_inscriptions_reelles'] = Agenda::inscriptions($email) === $owned && count($owned) === 121;
    $all = [];
    for ($page = 1; $page <= 3; $page++) {
        if ($page === 2) {
            $prior = $wpdb->suppress_errors(true); add_filter('query', $break);
            try { $failed = call_user_func($ex, $email, $page); $checks['page2_panne_WP_Error'] = is_wp_error($failed); }
            finally { remove_filter('query', $break); $wpdb->suppress_errors($prior); }
        }
        $part = call_user_func($ex, $email, $page);
        $checks['page' . $page . '_taille_et_fin'] = !is_wp_error($part) && count($part['data']) === ($page === 3 ? 21 : 50) && $part['done'] === ($page === 3);
        $checks['page' . $page . '_C21_preserve'] = Imagine\Site\Confidentialite::filtrerPage($part, 1, $email, $page, 0, false, 'imagine-agenda') === $part;
        $all = array_merge($all, array_column($part['data'], 'item_id'));
    }
    $checks['pagination_complete_sans_omission_ni_doublon'] = $all === $expected && count(array_unique($all)) === 121;
    $er = apply_filters('wp_privacy_personal_data_erasers', [])['imagine-agenda']['callback'];
    for ($page = 1; $page <= 3; $page++) { $result = call_user_func($er, $email, $page); }
    $checks['effacement_121_apres_pagination'] = $result['done'] && !$result['items_retained'] && Agenda::inscriptions($email) === [];
} catch (Throwable $e) { $error = get_class($e) . ': ' . $e->getMessage(); }
finally {
    foreach ($owned as $id) { if (get_post($id)) { wp_delete_post($id, true); } }
    $checks['inscriptions_essai_retirees'] = Agenda::inscriptions($email) === [];
}
$failures = array_keys(array_filter($checks, static fn ($v) => !$v));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures, 'error' => $error]);
exit($failures || $error ? 1 : 0);
