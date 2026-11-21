<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Envoi;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Envoi\Abonnement;
use Imagine\Pilotage\Envoi\Destinataire;
use Imagine\Pilotage\Envoi\ListeEnvoi;
use Imagine\Pilotage\Envoi\Situation;
use Imagine\Pilotage\Numeros\Calendrier;
use Imagine\Pilotage\Numeros\Numero;
use Imagine\Pilotage\Numeros\TypeNumero;
use PHPUnit\Framework\TestCase;

final class ListeEnvoiTest extends TestCase
{
    private function date(string $value): DateTimeImmutable
    {
        return new DateTimeImmutable($value, new DateTimeZone('Europe/Brussels'));
    }

    private function numero(): Numero
    {
        return new Numero('171', TypeNumero::Regulier, $this->date('2027-01-01'), $this->date('2026-12-20'));
    }

    private function personne(string $id = 'fictif-1', string $rue = '1 rue Imaginaire'): Destinataire
    {
        return new Destinataire($id, 'Camille Fictive', $rue, '', '1000', 'Ville Fictive', 'BE');
    }

    private function situation(
        string $date = '2026-11-01',
        string $etat = 'actif',
        bool $paiement = true,
        ?array $destinataires = null,
        array $dus = ['171'],
        ?string $enregistre = null
    ): Situation {
        return new Situation(
            $this->date($date),
            $this->date($enregistre ?? $date),
            $etat,
            $paiement,
            $dus,
            $destinataires ?? [$this->personne()]
        );
    }

    private function abonnement(array $situations, string $id = 'abo-fictif', string $origine = 'abonnement'): Abonnement
    {
        return new Abonnement($id, $origine, $this->date('2026-10-01'), $situations);
    }

    private function calculer(array $abonnements): ListeEnvoi
    {
        $numero = $this->numero();
        return ListeEnvoi::etablir($numero, new Calendrier([$numero]), $abonnements, $numero->cloture);
    }

    public function testAbonneActifRecoitUnExemplaireSansEmail(): void
    {
        $liste = $this->calculer([$this->abonnement([$this->situation()])]);
        self::assertCount(1, $liste->lignes);
        self::assertSame('Camille Fictive', $liste->lignes[0]['destinataire']);
        self::assertSame('abonnement', $liste->lignes[0]['origine']);
        self::assertSame([], $liste->anomalies);
    }
}
