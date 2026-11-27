<?php

declare(strict_types=1);

$base = ['existe' => true, 'email_recevable' => true, 'email' => 'fictif@example.org',
    'catalogue' => ['principale', 'coop'], 'preferences' => ['principale' => ['choix' => true, 'origine' => 'lecteur']],
    'abonnements' => [['etat' => 'active', 'tarifs' => ['normal-1']]], 'beneficiaire' => false,
    'cooperateur' => false, 'tarifs_autorises' => ['normal-1', 'normal-4'], 'personnalisation' => ['fictif' => ['choix' => ['a']]]];
$active = ['email' => 'fictif@example.org', 'statut' => 'abonne', 'cooperateur' => 'non',
    'tarif' => 'normal-1', 'newsletters' => ['principale'], 'personnalisation' => ['fictif' => ['choix' => ['a']]]];
$cases = ['actif' => [$base, ['fiche' => $active, 'raison' => 'eligible']]];
foreach (['pending', 'on-hold', 'expired', 'cancelled', 'pending-cancel'] as $status) {
    $cases[$status] = [array_replace($base, ['abonnements' => [['etat' => $status, 'tarifs' => ['normal-1']]]]),
        ['fiche' => array_replace($active, ['statut' => 'non_abonne', 'tarif' => 'inconnu']), 'raison' => 'eligible']];
}
foreach ([
    'absent' => [['existe' => false], null, 'compte_absent'],
    'sans_email' => [['email_recevable' => false], null, 'email_non_recevable'],
    'sans_choix' => [['preferences' => []], null, 'aucun_choix_lecteur'],
    'defaut_creation' => [['preferences' => ['principale' => ['choix' => true, 'origine' => 'defaut_creation']]], null, 'aucun_choix_lecteur'],
    'retrait' => [['preferences' => ['principale' => ['choix' => false, 'origine' => 'lecteur']]], ['statut' => 'a_retirer'], 'desinscrit_de_tout'],
    'liste_supprimee' => [['catalogue' => []], null, 'aucun_choix_lecteur'],
    'refus_hors_catalogue' => [['catalogue' => [], 'preferences' => ['principale' => ['choix' => false, 'origine' => 'lecteur']]], ['statut' => 'a_retirer'], 'desinscrit_de_tout'],
    'suppression_choix_positif_sans_retrait' => [['catalogue' => [], 'preferences' => ['principale' => ['choix' => true, 'origine' => 'lecteur']]], null, 'aucun_choix_lecteur'],
    'beneficiaire' => [['beneficiaire' => true], array_replace($active, ['statut' => 'inconnu', 'tarif' => 'inconnu']), 'eligible'],
    'coop' => [['cooperateur' => true], array_replace($active, ['cooperateur' => 'oui']), 'eligible'],
    'hors_liste' => [['abonnements' => [['etat' => 'active', 'tarifs' => ['invente']]]], array_replace($active, ['tarif' => 'inconnu']), 'eligible'],
    'ferme' => [['tarifs_autorises' => []], array_replace($active, ['tarif' => 'inconnu']), 'eligible'],
    'conflit' => [['abonnements' => [['etat' => 'active', 'tarifs' => ['normal-1']], ['etat' => 'active', 'tarifs' => ['normal-4']]]], array_replace($active, ['tarif' => 'inconnu']), 'eligible'],
    'incomplet' => [['abonnements' => [['etat' => 'active', 'tarifs' => ['normal-1', '']]]], array_replace($active, ['tarif' => 'inconnu']), 'eligible'],
    'projection_vide' => [['personnalisation' => []], array_replace($active, ['personnalisation' => []]), 'eligible'],
    'autre_liste' => [['preferences' => ['principale' => ['choix' => false, 'origine' => 'lecteur'], 'coop' => ['choix' => true, 'origine' => 'lecteur']]], array_replace($active, ['newsletters' => ['coop']]), 'eligible'],
] as $name => [$delta, $fiche, $reason]) {
    $cases[$name] = [array_replace($base, $delta), ['fiche' => $fiche, 'raison' => $reason]];
}
return $cases;
