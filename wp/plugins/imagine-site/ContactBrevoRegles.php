<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Projection pure. Les attributs personnels sont déjà filtrés par C24 en amont. */
final class ContactBrevoRegles
{
    public static function fiche(array $source): array
    {
        if (!$source['existe']) {
            return ['fiche' => null, 'raison' => 'compte_absent'];
        }
        if (!$source['email_recevable']) {
            return ['fiche' => null, 'raison' => 'email_non_recevable'];
        }
        $newsletters = [];
        $retrait = false;
        foreach ($source['preferences'] as $pref) {
            if (($pref['origine'] ?? null) === 'lecteur' && ($pref['choix'] ?? null) === false) {
                $retrait = true;
            }
        }
        foreach ($source['catalogue'] as $id) {
            $pref = $source['preferences'][$id] ?? [];
            if (($pref['origine'] ?? null) === 'lecteur' && ($pref['choix'] ?? null) === true) {
                $newsletters[] = $id;
            }
        }
        if (!$newsletters) {
            return $retrait ? ['fiche' => ['statut' => 'a_retirer'], 'raison' => 'desinscrit_de_tout']
                : ['fiche' => null, 'raison' => 'aucun_choix_lecteur'];
        }
        $actifs = array_filter($source['abonnements'], static fn (array $s): bool => $s['etat'] === 'active');
        $tarifs = [];
        $complet = (bool) $actifs;
        foreach ($actifs as $sub) {
            $complet = $complet && (bool) $sub['tarifs'];
            foreach ($sub['tarifs'] as $tarif) {
                $complet = $complet && in_array($tarif, $source['tarifs_autorises'], true);
                $tarifs[] = $tarif;
            }
        }
        $tarifs = array_values(array_unique($tarifs));
        $beneficiaire = $source['beneficiaire'];
        return ['fiche' => ['email' => $source['email'],
            'statut' => $beneficiaire ? 'inconnu' : ($actifs ? 'abonne' : 'non_abonne'),
            'cooperateur' => $source['cooperateur'] ? 'oui' : 'non',
            'tarif' => !$beneficiaire && $complet && count($tarifs) === 1 ? $tarifs[0] : 'inconnu',
            'newsletters' => $newsletters, 'personnalisation' => $source['personnalisation']], 'raison' => 'eligible'];
    }
}
