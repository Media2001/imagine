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

    public function testAccesAttendPaiementOuMandatEtExpireALAnniversaire(): void
    {
        $moteur = new Moteur($this->calendrier());
        $commande = $moteur->ouvrir($this->date('2026-10-08 12:00'));
        self::assertFalse($moteur->accesNumerique($commande, $this->date('2026-10-09')));
        foreach (\Imagine\Pilotage\Numeros\Activation::cases() as $motif) {
            $active = $commande->activer($this->date('2026-10-10 14:30'), $motif);
            self::assertFalse($moteur->accesNumerique($active, $this->date('2026-10-10 14:29:59')));
            self::assertTrue($moteur->accesNumerique($active, $this->date('2026-10-10 14:30')));
            self::assertTrue($moteur->accesNumerique($active, $this->date('2027-10-10 14:29:59')));
            self::assertFalse($moteur->accesNumerique($active, $this->date('2027-10-10 14:30')));
            self::assertSame('Europe/Brussels', $active->ouverture?->getTimezone()->getName());
        }
        self::assertNull($commande->ouverture);
    }

    public function testRenouvellementEtDetteSansInventerUnNumero(): void
    {
        $moteur = new Moteur($this->calendrier());
        $annee = $moteur->ouvrir($this->date('2026-10-08'));
        $suite = $moteur->renouveler($annee, $this->date('2027-10-08'));
        self::assertSame(['175', '176', '177', '178'], $this->ids($moteur->numeros($suite)));
        self::assertSame('HS-2028', $moteur->horsSerie($suite)?->id);

        $partiel = new Moteur(new Calendrier(array_filter(
            $this->calendrier()->numeros,
            static fn (Numero $numero): bool => $numero->sortie < new DateTimeImmutable('2027-04-01')
        )));
        self::assertSame(['171'], $this->ids($partiel->numeros($annee)));
        self::assertNull($partiel->dernier($annee));
        self::assertSame(3, $partiel->nonResolus($annee));
        self::assertNull($partiel->horsSerie($annee));
        $suiteInconnue = $partiel->renouveler($annee, $this->date('2027-10-08'));
        self::assertSame([], $partiel->numeros($suiteInconnue));
        self::assertSame(4, $partiel->nonResolus($suiteInconnue));
        self::assertSame(['175', '176', '177', '178'], $this->ids($moteur->numeros($suiteInconnue)));
        self::assertSame(0, $moteur->nonResolus($annee));
        self::assertNull((new Moteur(new Calendrier([])))->premier($annee));
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
