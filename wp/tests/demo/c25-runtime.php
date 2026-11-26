<?php

declare(strict_types=1);

use Imagine\Site\Retractation as R;
use Imagine\Site\RetractationConfidentialite as P;
use Imagine\Site\RetractationReglages as S;

$checks = [];
$check = static function (string $name, bool $value) use (&$checks): void { $checks[$name] = $value; };
$check('default_14_paiement', R::configuration() === ['jours' => 14, 'origine' => 'paiement']);
$receipt = R::lire(126);
$check('http_accuse_persistant', is_array($receipt) && $receipt['commande'] === 126 && $receipt['compte'] === 28);
$check('une_note_par_commande', count(P::lignes(28)) === 1);
$check('note_native_privee', get_comment_meta($receipt['note'], 'is_customer_note', true) !== '1');
$check('journal_C10_present', is_array(get_option(R::JOURNAL . 126)));
$check('rejeu_montre_premiere', R::demander(126, 28, 'confirmer', 'Autre motif') === $receipt);
$check('tiers_refuse', is_wp_error(R::demander(126, 9, 'confirmer', '')));
$check('ancien_refuse_POST', is_wp_error(R::demander(88, 9, 'confirmer', '')));
$check('sub_sans_parent_fermee', R::commande(77, 3) === null);

// Chaque valeur de réglage ; aucune modification du paiement ni du statut de l'ordre.
$order = wc_get_order(88);
$order->update_meta_data(R::MANUELLE, gmdate('Y-m-d'));
$order->save_meta_data();
update_option(R::OPTION, ['jours' => 1, 'origine' => 'manuelle'], false);
$check('manuel_un_jour_ouvert', R::ouverte(wc_get_order(88)));
wp_set_current_user(9);
$panel = R::panneau(89, []);
$check('abonnement_lie_commande', str_contains($panel, 'Commande n°88') && str_contains($panel, 'Me rétracter'));
$check('sub_cible_tiers_refuse', R::commande(89, 28) === null);
$check('abandon_etape1_sans_note', R::lire(88) === null);

// Échec réel d'INSERT du journal : la note Woo et ses métadonnées sont annulées.
global $wpdb;
$oldSuppress = $wpdb->suppress_errors(true);
$fault = static function (string $query): string {
    return str_contains($query, 'INSERT INTO') && str_contains($query, R::JOURNAL . '88') ? 'INSERT INTO imagine_c25_table_inexistante VALUES (1)' : $query;
};
add_filter('query', $fault);
$failed = R::demander(89, 9, 'confirmer', 'Échec fictif du journal');
remove_filter('query', $fault);
$check('journal_panne_pas_succes', is_wp_error($failed));
$check('journal_panne_note_annulee', P::lignes(9) === [] && R::lire(88) === null);
$wpdb->suppress_errors($oldSuppress);
$manual = R::demander(89, 9, 'confirmer', 'Motif abonnement fictif');
$check('sub_demande_sur_commande_initiale', is_array($manual) && $manual['commande'] === 88);
$check('sub_et_commande_meme_accuse', R::demander(88, 9, 'confirmer', '') === $manual);

// Export natif additif avec échec SQL puis reprise de la même page.
$email = get_userdata(9)->user_email;
$export = P::exporter($email);
$check('export_positif_motif', count($export['data']) === 1 && str_contains(wp_json_encode($export), 'Motif abonnement fictif'));
$check('export_tiers_absent', !str_contains(wp_json_encode($export), 'Motif HTTP fictif'));
$oldSuppress = $wpdb->suppress_errors(true);
$fault = static fn (string $query): string => str_contains($query, 'SELECT m.comment_id,m.meta_value') ? 'SELECT * FROM imagine_c25_table_inexistante' : $query;
add_filter('query', $fault);
$check('export_SQL_erreur_pas_page_vide', is_wp_error(P::exporter($email, 1)));
$check('erase_SQL_incomplet', !P::effacer($email)['done']);
remove_filter('query', $fault);
$wpdb->suppress_errors($oldSuppress);
$check('export_reprise_page_preservee', P::exporter($email, 1) === $export);
$erased = P::effacer($email, 1);
$check('effacement_note_et_motif', $erased['done'] && $erased['items_removed'] && P::lignes(9) === []);
$event = get_option(R::JOURNAL . 88);
$check('journal_depersonnalise', $event['qui_id'] === 0 && $event['qui_login'] === 'efface' && $event['apres']['note'] === 0);
$check('effacement_tiers_preserve', count(P::lignes(28)) === 1);
$check('export_et_eraser_inscrits', isset(apply_filters('wp_privacy_personal_data_exporters', [])['imagine-retractation'], apply_filters('wp_privacy_personal_data_erasers', [])['imagine-retractation']));

// Un départ manuel ancien se ferme, y compris l'envoi direct.
$order = wc_get_order(88);
$order->update_meta_data(R::MANUELLE, '2020-01-01');
$order->save_meta_data();
$check('manuel_ancien_ferme', !R::ouverte(wc_get_order(88)));
// La commande 94 n'a pas encore de demande : prouve le refus, pas le rejeu de 88.
$order94 = wc_get_order(94);
$order94->update_meta_data(R::MANUELLE, '2020-01-01');
$order94->save_meta_data();
$check('manuel_ancien_POST_refuse', is_wp_error(R::demander(94, 11, 'confirmer', '')));
$check('manuel_date_absente_fermee', !R::ouverte(wc_get_order(100)));
update_option(R::OPTION, ['jours' => 30, 'origine' => 'paiement'], false);
$check('reglage_30_valide', S::nettoyer(['jours' => '30', 'origine' => 'paiement']) === ['jours' => 30, 'origine' => 'paiement']);
$check('raison_vide_acceptee', $receipt['raison'] === 'Motif HTTP fictif');
$check('aucune_sortie_ni_mutation_financiere', get_option('imagine_c25_observations') === []);
$out = ['total' => count($checks), 'checks' => $checks, 'failures' => array_keys(array_filter($checks, static fn ($v) => !$v))];
echo wp_json_encode($out);
