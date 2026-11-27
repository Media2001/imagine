<?php

declare(strict_types=1);

use Imagine\Site\Acquisition;
use Imagine\Site\AcquisitionConfidentialite;

// Exclusivement chargé par le lanceur gardé sur imagine-test-demo, avec son ID possédé.
$owner = 28;
$id = $c27_order;
$mode = $c27_mode;
global $wpdb;
delete_user_meta($owner, Acquisition::SOURCE);
$previous = ['commande' => 999999, 'compte' => $owner, 'date' => '2026-11-27T12:00:00Z',
    'choix' => 'mars', 'libelle' => 'Origine antérieure fictive \\ lune'];
$setup = true;
if ($mode === 'I1') {
    update_user_meta($owner, Acquisition::SOURCE, wp_slash($previous));
} elseif ($mode === 'M1') {
    add_option(Acquisition::VUE . $id, ['commande' => $id, 'compte' => $owner, 'date' => gmdate('Y-m-d\TH:i:s\Z')], '', false);
} else {
    $setup = Acquisition::repondre($id, $owner, 'lune') === true;
}
$reads = 0;
$faults = 0;
$armed = false;
$filter = static function (string $sql) use ($wpdb, $mode, &$reads, &$faults, &$armed): string {
    if (str_contains($sql, 'GET_LOCK(')) {
        $armed = true;
        if ($mode === 'I2') {
            // Le compte est déjà résolu ; la première lecture SOURCE sous verrou est fraîche.
            wp_cache_delete(28, 'user_meta');
        }
    }
    if (str_contains($sql, 'RELEASE_LOCK(')) {
        $armed = false;
    }
    if ($armed && preg_match('/^\s*SELECT\s+(?:meta_value|user_id, meta_key, meta_value)\s+FROM\b/i', $sql)
        && str_contains($sql, $wpdb->usermeta)) {
        ++$reads;
        if (($mode === 'I1' || $mode === 'I2') && $reads === 1 || $mode === 'finalfail' && $reads === 3) {
            ++$faults;
            // Vraie erreur SQL, pas un résultat PHP fabriqué ; seule cette lecture échoue.
            return 'SELECT imagine_c27_colonne_fictive_absente FROM ' . $wpdb->usermeta . ' LIMIT 1';
        }
    }
    return $sql;
};
$deleteFilter = static fn (): bool => false;
$oldSuppress = $wpdb->suppress_errors(true);
wp_cache_delete($owner, 'user_meta');
if ($mode === 'deletefail') {
    // Cache périmé vide comme dans la requête concurrente de la fusion.
    wp_cache_set($owner, [], 'user_meta');
    add_filter('delete_user_metadata', $deleteFilter);
}
add_filter('query', $filter);
try {
    $result = $mode === 'I1' ? Acquisition::repondre($id, $owner, 'lune')
        : AcquisitionConfidentialite::effacer(get_userdata($owner)->user_email);
} finally {
    remove_filter('query', $filter);
    remove_filter('delete_user_metadata', $deleteFilter);
    $wpdb->suppress_errors($oldSuppress);
}
wp_cache_delete($owner, 'user_meta');
$source = get_user_meta($owner, Acquisition::SOURCE, true);
$sourceRows = $wpdb->get_results($wpdb->prepare(
    "SELECT meta_value FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key=%s",
    $owner,
    Acquisition::SOURCE
), ARRAY_A);
$answer = get_option(Acquisition::REPONSE . $id, null);
$seen = get_option(Acquisition::VUE . $id, null);
$refused = is_wp_error($result);
if ($mode === 'I1') {
    $pass = $setup && $faults === 1 && $refused && $source === $previous && $answer === null;
} elseif ($mode === 'M1') {
    $pass = $setup && $result['done'] === true && $result['items_retained'] === false
        && $answer === null && $seen === ['commande' => $id, 'etat' => 'effacee'] && $sourceRows === [];
} else {
    $pass = $setup && $result['done'] === false && $result['items_retained'] === true
        && ($mode === 'finalfail' ? $faults === 1 && $reads === 3 : $sourceRows !== [] && is_array($answer))
        && ($mode !== 'I2' || $faults === 1);
}
echo wp_json_encode(['pass' => $pass, 'setup' => $setup, 'mode' => $mode, 'sql_reads' => $reads,
    'sql_faults' => $faults, 'refused' => $refused, 'result' => $refused ? $result->get_error_code() : $result,
    'source_present' => $sourceRows !== [], 'source_previous_preserved' => $source === $previous,
    'answer_present' => $answer !== null, 'seen' => $seen]);
