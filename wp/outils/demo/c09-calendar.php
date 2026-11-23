<?php
/** Horloge technique des fixtures C09, jamais une règle financière. */
declare(strict_types=1);
namespace Imagine\Demo\C09;
function now(): \DateTimeImmutable
{
    $instant = $GLOBALS['imagine_c09_now'] ?? new \DateTimeImmutable('now', new \DateTimeZone('UTC'));
    if (!$instant instanceof \DateTimeImmutable) { throw new \InvalidArgumentException('Horloge C09 invalide.'); }
    return $instant->setTimezone(new \DateTimeZone('UTC'));
}
function papierDue(\DateTimeImmutable $instant): string
{
    $utc = $instant->setTimezone(new \DateTimeZone('UTC'));
    // Échéance à lancer, inclusive : à la dernière seconde elle est due maintenant,
    // et non strictement future, sans basculer au mois suivant.
    return min($utc->modify('+1 hour'), $utc->modify('last day of this month')->setTime(23, 59, 59))->format('Y-m-d H:i:s');
}
