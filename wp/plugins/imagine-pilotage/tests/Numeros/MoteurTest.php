<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Numeros;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Numeros\Calendrier;
use Imagine\Pilotage\Numeros\Moteur;
use Imagine\Pilotage\Numeros\Numero;
use PHPUnit\Framework\TestCase;

final class MoteurTest extends TestCase
{
    private function date(string $date): DateTimeImmutable
    {
        return new DateTimeImmutable($date, new DateTimeZone('Europe/Brussels'));
    }

    private function calendrier(): Calendrier
    {
        return new Calendrier(require __DIR__ . '/fixtures/calendrier.php');
    }

    private function ids(array $numeros): array
    {
        return array_map(static fn (Numero $numero): string => $numero->id, $numeros);
    }

    public function testExempleDuCahierDesCharges(): void
    {
        $moteur = new Moteur($this->calendrier());
        $annee = $moteur->ouvrir($this->date('2026-10-08'));
        self::assertSame(['171', '172', '173', '174'], $this->ids($moteur->numeros($annee)));
        self::assertSame('171', $moteur->premier($annee)?->id);
        self::assertSame('174', $moteur->dernier($annee)?->id);
        self::assertSame('HS-2027', $moteur->horsSerie($annee)?->id);
    }
}
