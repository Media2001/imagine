<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Numeros;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Numeros\Activation;
use Imagine\Pilotage\Numeros\Calendrier;
use Imagine\Pilotage\Numeros\Moteur;
use Imagine\Pilotage\Numeros\Numero;
use Imagine\Pilotage\Numeros\TypeNumero;
use PHPUnit\Framework\TestCase;

final class CorrectionsTest extends TestCase
{
    private function date(string $date): DateTimeImmutable
    {
        return new DateTimeImmutable($date, new DateTimeZone('Europe/Brussels'));
    }

    public function testCalendrierInverseRefuseALaConstruction(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->expectExceptionMessage('171 et 172');
        new Calendrier([
            new Numero('171', TypeNumero::Regulier, $this->date('2027-01-05'), $this->date('2026-12-20')),
            new Numero('172', TypeNumero::Regulier, $this->date('2027-04-05'), $this->date('2026-12-15')),
        ]);
    }

    public function testModificationInverseeRefuseeSansChangerSequenceDernierEtEcheances(): void
    {
        $calendrier = new Calendrier(require __DIR__ . '/fixtures/calendrier.php');
        try {
            $calendrier->modifier(new Numero(
                '172',
                TypeNumero::Regulier,
                $this->date('2027-04-05'),
                $this->date('2026-12-15')
            ), $this->date('2026-12-01'));
            self::fail('Une clôture inversée doit être refusée.');
        } catch (\InvalidArgumentException $e) {
            self::assertStringContainsString('171 et 172', $e->getMessage());
        }
        $moteur = new Moteur($calendrier);
        $annee = $moteur->ouvrir($this->date('2026-12-16'));
        self::assertSame(['171', '172', '173', '174'], array_map(fn ($n) => $n->id, $moteur->numeros($annee)));
        self::assertSame('174', $moteur->dernier($annee)?->id);
        self::assertSame(['171', '172', '173', '174'], array_map(
            fn ($e) => $e->numero->id,
            $moteur->echeances($annee, 7)
        ));
    }

    public function testAcces29FevrierImmediatSuspensionEtFinExclusive28Fevrier(): void
    {
        $moteur = new Moteur(new Calendrier([]));
        foreach (Activation::cases() as $motif) {
            $debut = $this->date('2028-02-29 14:30:00');
            $annee = $moteur->ouvrir($debut)->activer($debut, $motif);
            self::assertFalse($moteur->accesNumerique($annee, $debut->modify('-1 second')));
            self::assertTrue($moteur->accesNumerique($annee, $debut));
            self::assertTrue($moteur->accesNumerique($annee, $this->date('2028-03-01 14:30')));
            $annee = $annee->suspendre($this->date('2028-03-02'));
            self::assertFalse($moteur->accesNumerique($annee, $this->date('2028-03-02')));
            $annee = $annee->reactiver($this->date('2028-03-03'));
            self::assertTrue($moteur->accesNumerique($annee, $this->date('2029-02-28 14:29:59')));
            self::assertFalse($moteur->accesNumerique($annee, $this->date('2029-02-28 14:30:00')));
            self::assertFalse($moteur->accesNumerique($annee, $this->date('2029-03-01 14:30:00')));
        }
    }
}
