<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Projections explicites : aucune copie générique de métadonnées personnelles. */
final class ConfidentialiteRegles
{
    public static function retirerPostal(array $event, int $id): ?array
    {
        if (self::postal($event, $id) === null) {
            return $event;
        }
        $d = &$event['donnees'];
        if ((int) ($d['user'] ?? 0) === $id) {
            $others = array_filter($d['beneficiaires'] ?? [], static fn ($p): bool => (int) ($p['id'] ?? 0) !== $id);
            $links = $d['relation_native'] ?? [];
            $otherLinks = isset($links['recipient_user'])
                ? ((int) $links['recipient_user'] !== $id ? [$links] : [])
                : array_filter($links, static fn ($p): bool => is_array($p) && (int) ($p['user_id'] ?? 0) !== $id);
            if (!$others && !$otherLinks) {
                return null;
            }
            // L'identité du payeur n'est pas l'attribution postale des tiers.
            $d['user'] = '0';
            if (($d['origine'] ?? '') !== 'offert') {
                foreach (['destinataire', 'rue', 'complement', 'code_postal', 'ville', 'pays'] as $field) {
                    $d[$field] = '';
                }
            }
        }
        if (($d['origine'] ?? '') === 'offert'
            && (int) ($d['relation_native']['recipient_user'] ?? 0) === $id) {
            foreach (['destinataire', 'rue', 'complement', 'code_postal', 'ville', 'pays'] as $field) {
                $d[$field] = '';
            }
        }
        $d['beneficiaires'] = array_values(array_filter(
            $d['beneficiaires'] ?? [],
            static fn ($p): bool => (int) ($p['id'] ?? 0) !== $id
        ));
        $relations = $d['relation_native'] ?? [];
        if (isset($relations['recipient_user']) && (int) $relations['recipient_user'] === $id) {
            $relations = [];
        } else {
            $relations = array_values(array_filter(
                $relations,
                static fn ($p): bool => !is_array($p) || (int) ($p['user_id'] ?? 0) !== $id
            ));
        }
        $d['relation_native'] = $relations;
        // Un retrait certain ne transforme jamais les attributions restantes en inconnues.
        // Une origine initialement non résolue reste non résolue : aucun droit nouveau.
        return $event;
    }

    public static function postal(array $event, int $user): ?array
    {
        $d = $event['donnees'] ?? [];
        $own = (int) ($d['user'] ?? 0) === $user;
        $people = array_values(array_filter(
            $d['beneficiaires'] ?? [],
            static fn ($p): bool => (int) ($p['id'] ?? 0) === $user
        ));
        $relations = $d['relation_native'] ?? [];
        $links = isset($relations['recipient_user'])
            ? ((int) $relations['recipient_user'] === $user ? [['user_id' => $user]] : [])
            : array_values(array_filter(
                $relations,
                static fn ($p): bool => is_array($p) && (int) ($p['user_id'] ?? 0) === $user
            ));
        if (!$own && !$people && !$links) {
            return null;
        }
        $out = array_intersect_key($d, array_flip([
            'id', 'creation', 'debut', 'fin', 'etat', 'paiement', 'grace_debut', 'grace_fin',
            'origine', 'renouvellements',
        ]));
        if ($own && ($d['origine'] ?? 'abonnement') === 'abonnement') {
            $out += array_intersect_key($d, array_flip([
                'destinataire', 'rue', 'complement', 'code_postal', 'ville', 'pays',
            ]));
        }
        if ($people) {
            $out['beneficiaires'] = array_map(static fn ($p): array => array_intersect_key($p, array_flip([
                'id', 'nom', 'rue', 'complement', 'code_postal', 'ville', 'pays',
            ])), $people);
        }
        if ($links) {
            $out['attribution'] = array_map(static fn ($p): array => array_intersect_key($p, array_flip([
                'user_id', 'membership_id', 'etat', 'debut', 'fin',
            ])), $links);
        }
        return ['observe_utc' => $event['observe_utc'] ?? '', 'donnees' => $out];
    }
}
