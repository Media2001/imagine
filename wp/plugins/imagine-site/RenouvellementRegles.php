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
                'message'=>'arret_a_terme'];
        }
        if (in_array($native['method'] ?? '', ['bacs', 'cheque', 'imagine_papier'], true)) {
            return ['mode'=>'manuel', 'arreter'=>false, 'reprendre'=>false,
                'message'=>'manuel'];
        }
        if (($native['period'] ?? '') === 'month' && (int) ($native['interval'] ?? 0) === 3) {
            return ['mode'=>'quatre_fois', 'arreter'=>false, 'reprendre'=>false,
                'message'=>'quatre_fois'];
        }
        if (($native['manual'] ?? null) !== true) {
            return ['mode'=>'indisponible', 'arreter'=>false, 'reprendre'=>false,
                'message'=>'indisponible'];
        }
        return ['mode'=>'manuel', 'arreter'=>false, 'reprendre'=>false,
            'message'=>'manuel'];
    }
}
