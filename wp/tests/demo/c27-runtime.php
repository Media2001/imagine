<?php

declare(strict_types=1);

use Imagine\Site\Acquisition;

$checks = [];
$checks['adaptateur_present'] = class_exists(Acquisition::class);
if (!$checks['adaptateur_present']) {
    echo wp_json_encode(['checks' => $checks]);
    return;
}
$orders = [];
$prefix = 'imagine_acquisition_';
$beforeConfig = get_option(Acquisition::OPTION, null);
$source = get_user_meta(28, Acquisition::SOURCE, true);
try {
    update_option(Acquisition::OPTION, ['lune' => 'Radio fictive \\ lune', 'mars' => 'Journal martien fictif'], false);
    $order = wc_create_order(['customer_id' => 28, 'status' => 'pending', 'created_via' => 'checkout']);
    $orders[] = $order->get_id();
    $order->set_total(1);
    $order->save();
    $r = Acquisition::repondre($order->get_id(), 28, 'lune');
    $checks['POST_avant_paiement_refuse_sans_trace'] = is_wp_error($r) && get_option(Acquisition::REPONSE . $order->get_id(), null) === null;
    $order->set_status('processing');
    $order->set_date_paid(time());
    $order->save();
    $checks['tiers_refuse'] = is_wp_error(Acquisition::repondre($order->get_id(), 29, 'lune'));
    $checks['hors_liste_refuse'] = is_wp_error(Acquisition::repondre($order->get_id(), 28, 'texte-libre'));
    $first = Acquisition::repondre($order->get_id(), 28, 'lune');
    $record = get_option(Acquisition::REPONSE . $order->get_id());
    $checks['reponse_unique_datee_lue'] = $first === true && is_array($record) && $record['libelle'] === 'Radio fictive \\ lune' && preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/D', $record['date']) === 1;
    $checks['double_refuse_immuable'] = is_wp_error(Acquisition::repondre($order->get_id(), 28, 'mars')) && get_option(Acquisition::REPONSE . $order->get_id()) === $record;
    $checks['source_si_vide_seulement'] = get_user_meta(28, Acquisition::SOURCE, true) === ($source === '' ? $record : $source);
} finally {
    foreach ($orders as $id) {
        foreach ([Acquisition::REPONSE, Acquisition::VUE] as $key) {
            delete_option($key . $id);
        }
        wc_get_order($id)?->delete(true);
    }
    $beforeConfig === null ? delete_option(Acquisition::OPTION) : update_option(Acquisition::OPTION, $beforeConfig, false);
    $source === '' ? delete_user_meta(28, Acquisition::SOURCE) : update_user_meta(28, Acquisition::SOURCE, wp_slash($source));
}
echo wp_json_encode(['checks' => $checks]);
