<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Projections explicites : aucune copie générique de métadonnées personnelles. */
final class ConfidentialiteRegles
{
    public static function retirerPostal(array $event, int $id): ?array
    {
        if (self::postal($event, $id) === null) { return $event; }
        if ((int) ($event['donnees']['user'] ?? 0) === $id) { return null; }
        $d = &$event['donnees'];
        $d['beneficiaires'] = array_values(array_filter($d['beneficiaires'] ?? [], static fn ($p): bool => (int) ($p['id'] ?? 0) !== $id));
        $relations = $d['relation_native'] ?? [];
        if (isset($relations['recipient_user']) && (int) $relations['recipient_user'] === $id) { $relations = []; }
        else { $relations = array_values(array_filter($relations, static fn ($p): bool => !is_array($p) || (int) ($p['user_id'] ?? 0) !== $id)); }
        $d['relation_native'] = $relations;
        $d['beneficiaires_resolus'] = false;
        return $event;
    }

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
