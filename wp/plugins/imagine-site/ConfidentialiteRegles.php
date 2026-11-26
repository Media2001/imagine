<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Projections explicites : aucune copie générique de métadonnées personnelles. */
final class ConfidentialiteRegles
{
    public static function postal(array $event, int $user): ?array
    {
        $d = $event['donnees'] ?? [];
        $own = (int) ($d['user'] ?? 0) === $user;
        $people = array_values(array_filter($d['beneficiaires'] ?? [], static fn ($p): bool => (int) ($p['id'] ?? 0) === $user));
        if (!$own && !$people) {
            return null;
        }
        $out = array_intersect_key($d, array_flip(['id', 'creation', 'debut', 'fin', 'etat', 'paiement', 'grace_debut', 'grace_fin', 'origine', 'renouvellements']));
        if ($own && ($d['origine'] ?? 'abonnement') === 'abonnement') {
            $out += array_intersect_key($d, array_flip(['destinataire', 'rue', 'complement', 'code_postal', 'ville', 'pays']));
        }
        if ($people) {
            $out['beneficiaires'] = array_map(static fn ($p): array => array_intersect_key($p, array_flip(['id', 'nom', 'rue', 'complement', 'code_postal', 'ville', 'pays'])), $people);
        }
        return ['observe_utc' => $event['observe_utc'] ?? '', 'donnees' => $out];
    }
}
