<?php

declare(strict_types=1);
namespace Imagine\Site;

/** Présentation prudente C20 ; aucune nouvelle règle de droit, de numéro ou de dette. */
final class RenouvellementRegles
{
    public static function presentation(array $native, \DateTimeImmutable $now): array
    {
        $end = MonCompteRegles::date((string) ($native['end'] ?? ''));
        if (($native['status'] ?? '') === 'pending-cancel' && $end && $end > $now) {
            return ['mode'=>'arret_a_terme', 'arreter'=>false, 'reprendre'=>false, 'fin'=>$native['end'],
                'message'=>'L’abonnement s’arrêtera à la date indiquée. La reprise n’est pas disponible dans les profils actuels de cette démonstration ; contactez Imagine.'];
        }
        if (in_array($native['method'] ?? '', ['bacs', 'cheque', 'imagine_papier'], true)) {
            return ['mode'=>'manuel', 'arreter'=>false, 'reprendre'=>false,
                'message'=>'Le renouvellement est manuel : aucune reconduction automatique à désactiver.'];
        }
        if (($native['period'] ?? '') === 'month' && (int) ($native['interval'] ?? 0) === 3) {
            return ['mode'=>'quatre_fois', 'arreter'=>false, 'reprendre'=>false,
                'message'=>'Pour ne pas renouveler votre engagement en quatre fois, faites la demande auprès d’Imagine ; les échéances du bloc en cours restent dues.'];
        }
        if (($native['manual'] ?? null) !== true) {
            return ['mode'=>'indisponible', 'arreter'=>false, 'reprendre'=>false,
                'message'=>'La gestion du renouvellement n’est pas disponible sur cette démonstration ; contactez Imagine.'];
        }
        return ['mode'=>'manuel', 'arreter'=>false, 'reprendre'=>false,
            'message'=>'Le renouvellement est manuel : aucune reconduction automatique à désactiver.'];
    }
}
