<?php
/** C26 fixture applicative ; évaluée seulement sur la démonstration gardée. */
declare(strict_types=1);

use Imagine\Site\Agenda;
use Imagine\Site\Sujet;
use Imagine\Site\Personnalisation;
use Imagine\Site\Retractation;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || home_url() !== 'http://192.168.129.32:8085'
    || apply_filters('pre_wp_mail', null, []) !== false
    || !is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
    || WC()->payment_gateways()->get_available_payment_gateways() !== []) {
    throw new RuntimeException('C26 cible refusée');
}
$input = $GLOBALS['c26_input'];
$operation = $GLOBALS['c26_operation'];
$owner = (int)$input['owner'];
$user = get_userdata($owner);
if (!$user || !str_ends_with($user->user_email, '@example.org')
    || !get_user_meta($owner, '_imagine_c09_fixture', true)) {
    throw new RuntimeException('C26 propriétaire fictif refusé');
}
if ($operation === 'seed') {
    wp_set_current_user($owner);
    $events = [];
    $event = 0;
    foreach (get_posts(['post_type' => 'imagine_evenement', 'post_status' => 'publish', 'numberposts' => -1]) as $p) {
        $events[] = ['id' => $p->ID, 'path' => wp_parse_url(get_permalink($p), PHP_URL_PATH), 'title' => $p->post_title];
        if (!$event && Agenda::ouvert($p->ID)) {
            $event = $p->ID;
        }
    }
    if (!$event || Agenda::inscriptions($user->user_email) !== [] || Sujet::ids($user->user_email) !== []) {
        throw new RuntimeException('C26 prérequis inscription/sujet refusé');
    }
    if (!Agenda::inscrire($event, 'C26_AGENDA_FICTIF', $user->user_email, false)
        || !Sujet::enregistrer('Personnage fictif C26', $user->user_email, 'C26_SUJET_FICTIF', false)) {
        throw new RuntimeException('C26 fixture privée non écrite');
    }
    $questions = Personnalisation::catalogue();
    if (!$questions || !$questions[0]['choix']) {
        throw new RuntimeException('C26 catalogue absent');
    }
    $question = $questions[0];
    Personnalisation::enregistrer($owner, [$question['id'] => [$question['choix'][0]['id']]], null, Personnalisation::version($owner));
    $answers = Personnalisation::reponses($owner);
    // Sentinelle de fixture dédiée : pas une date susceptible d'apparaître ailleurs.
    $answers[$question['id']]['date_utc'] = 'C26_PERSONNALISATION_FICTIF';
    update_user_meta($owner, Personnalisation::META, $answers);
    if (Personnalisation::reponses($owner) !== $answers) {
        throw new RuntimeException('C26 réponse fixture non persistée');
    }
    $order = wc_create_order(['customer_id' => $owner, 'created_via' => 'c26-fixture', 'status' => 'pending']);
    if (is_wp_error($order)) {
        throw new RuntimeException('C26 commande fixture absente');
    }
    $order->set_date_paid(time());
    $order->update_meta_data(Retractation::MANUELLE, gmdate('Y-m-d'));
    $order->save();
    $record = Retractation::demander((int)$order->get_id(), $owner, 'confirmer', 'C26_RETRACTATION_FICTIF');
    if (is_wp_error($record)) {
        throw new RuntimeException('C26 demande fixture absente');
    }
    // Sentinelle temporaire persistée : traverse le vrai accusé et le vrai export.
    $record['date'] = 'C26_ACCUSE_FICTIF';
    update_comment_meta((int)$record['note'], Retractation::META, wp_slash($record));
    $journal = get_option(Retractation::JOURNAL . $order->get_id());
    $journal['apres']['date'] = $record['date'];
    update_option(Retractation::JOURNAL . $order->get_id(), $journal, false);
    if (Retractation::lire((int)$order->get_id()) !== $record) {
        throw new RuntimeException('C26 accusé fixture non persisté');
    }
    $pages = get_option('imagine_b08_pages');
    $list = [];
    foreach ([$pages['cooperative'], $pages['soutenir'], $pages['sujet'], ...array_values($pages['enfants'])] as $id) {
        $p = get_post((int)$id);
        if (!$p || $p->post_status !== 'publish') {
            throw new RuntimeException('C26 page B08 absente');
        }
        $list[] = ['id' => $p->ID, 'path' => wp_parse_url(get_permalink($p), PHP_URL_PATH), 'title' => $p->post_title];
    }
    echo wp_json_encode(['scope' => 'imagine-test-demo', 'pages' => $list, 'events' => $events,
        'owner' => $owner, 'registration' => Agenda::inscriptions($user->user_email)[0],
        'subject' => Sujet::ids($user->user_email)[0], 'order' => $order->get_id(), 'note' => $record['note'],
        'markers' => ['agenda' => 'C26_AGENDA_FICTIF', 'personnalisation' => 'C26_PERSONNALISATION_FICTIF',
            'retractation' => 'C26_RETRACTATION_FICTIF', 'sujet' => 'C26_SUJET_FICTIF', 'accuse' => 'C26_ACCUSE_FICTIF']]);
} elseif ($operation === 'privacy') {
    $registry = apply_filters('wp_privacy_personal_data_exporters', []);
    $keys = ['agenda' => 'imagine-agenda', 'personnalisation' => 'imagine-personnalisation',
        'retractation' => 'imagine-retractation', 'sujet' => 'imagine-sujets'];
    $out = [];
    foreach ($input['audiences'] as $public => $email) {
        if (!str_ends_with($email, '@example.org')) {
            throw new RuntimeException('C26 email fictif requis');
        }
        foreach ($keys as $family => $key) {
            if (!isset($registry[$key]['callback']) || !is_callable($registry[$key]['callback'])) {
                throw new RuntimeException('C26 callback natif absent');
            }
            // Mutation de raccord : le vrai callback reçoit le titulaire adverse.
            // Aucun tableau de résultat, corps ou indicateur n'est falsifié en mémoire.
            $target = ($input['mutation'] ?? '') === $family && $public !== 'inverse-proprietaire'
                ? $user->user_email : $email;
            $value = call_user_func($registry[$key]['callback'], $target, 1);
            $out[] = ['public' => $public, 'family' => $family,
                'payload' => is_wp_error($value) ? ['error' => $value->get_error_code()] : $value];
        }
    }
    echo wp_json_encode($out);
} elseif ($operation === 'cleanup') {
    foreach ([Agenda::inscriptions($user->user_email), Sujet::ids($user->user_email)] as $ids) {
        if (!is_array($ids)) {
            throw new RuntimeException('C26 nettoyage incomplet');
        }
        foreach ($ids as $id) {
            if (!in_array($id, $input['old_private_ids'], true)) {
                wp_delete_post($id, true);
            }
        }
    }
    // Les commandes nouvelles sont repérées par created_via et propriétaire, jamais par plages d'IDs.
    foreach (wc_get_orders(['customer_id' => $owner, 'limit' => -1, 'type' => 'shop_order']) as $order) {
        if ($order->get_created_via() !== 'c26-fixture') {
            continue;
        }
        $id = (int)$order->get_id();
        $record = Retractation::lire($id);
        if ($record && !empty($record['note'])) {
            wp_delete_comment((int)$record['note'], true);
        }
        delete_option(Retractation::JOURNAL . $id);
        $order->delete(true);
        if (wc_get_order($id)) {
            throw new RuntimeException('C26 commande non supprimée');
        }
    }
    echo wp_json_encode(true);
} else {
    throw new RuntimeException('C26 opération refusée');
}
