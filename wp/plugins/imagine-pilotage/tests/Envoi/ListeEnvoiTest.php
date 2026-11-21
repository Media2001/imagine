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

    private function abonnement(
        array $situations,
        string $id = 'abo-fictif',
        string $origine = 'abonnement'
    ): Abonnement {
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

    public static function profils(): array
    {
        return [
            'A-CARTE' => ['actif', true, true],
            'A-SEPA4' => ['actif', true, true],
            'A-GRACE' => ['grace', true, true],
            'A-SUSP' => ['suspendu', true, false],
            'A-VIR' => ['actif', false, false],
            'A-PAPIER attente' => ['actif', false, false],
            'A-PAPIER valide' => ['actif', true, true],
            'A-EXPIRE' => ['expire', true, false],
            'A-NONRENOUV' => ['actif', true, true],
            'A-ETRANGER' => ['actif', true, true],
            'A-SANSMAIL' => ['actif', true, true],
        ];
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('profils')]
    public function testProfilsACloture(string $etat, bool $paiement, bool $attendu): void
    {
        $liste = $this->calculer([$this->abonnement([$this->situation(etat: $etat, paiement: $paiement)])]);
        self::assertCount($attendu ? 1 : 0, $liste->lignes);
    }

    public function testPaiementUneSecondeAvantEtApresEtExactementACloture(): void
    {
        foreach (['2026-12-19 23:59:59' => 1, '2026-12-20 00:00:00' => 0, '2026-12-20 00:00:01' => 0] as $at => $n) {
            $abo = $this->abonnement([
                $this->situation(paiement: false),
                $this->situation($at),
            ]);
            self::assertCount($n, $this->calculer([$abo])->lignes, $at);
        }
    }

    public function testAdresseHistoriqueEtRejeuMalgreChangementPosterieur(): void
    {
        $avant = $this->situation('2026-12-19 23:59:59', destinataires: [$this->personne(rue: '2 rue Avant')]);
        $apres = $this->situation('2026-12-20 00:00:01', destinataires: [$this->personne(rue: '3 rue Apres')]);
        $base = $this->calculer([$this->abonnement([$this->situation(), $avant])]);
        $rejeu = $this->calculer([$this->abonnement([$apres, $avant, $this->situation()])]);
        self::assertSame('2 rue Avant', $base->lignes[0]['rue']);
        self::assertSame($base->lignes, $rejeu->lignes);
    }

    public function testReactivationEtCreationApresClotureNeRattrapentPas(): void
    {
        $abo = $this->abonnement([
            $this->situation(etat: 'suspendu'),
            $this->situation('2026-12-20 00:00:01'),
        ]);
        $nouveau = new Abonnement('nouveau', 'abonnement', $this->date('2026-12-20 00:00:01'), [
            $this->situation('2026-12-20 00:00:01'),
        ]);
        self::assertSame([], $this->calculer([$abo, $nouveau])->lignes);
    }

    public function testCorrectionRetrodateeEnregistreeApresClotureIgnoree(): void
    {
        $abo = $this->abonnement([
            $this->situation(paiement: false),
            $this->situation('2026-12-19', enregistre: '2026-12-21'),
        ]);
        self::assertSame([], $this->calculer([$abo])->lignes);
    }

    public function testNumeroDuSeulementSansRecalculC01(): void
    {
        foreach ([['171'], ['170'], ['172'], []] as $dus) {
            self::assertCount(in_array('171', $dus, true) ? 1 : 0, $this->calculer([
                $this->abonnement([$this->situation(dus: $dus)]),
            ])->lignes);
        }
    }

    public function testAnomaliesSepareesEtDoublonsConserves(): void
    {
        $incomplet = new Destinataire('incomplet', 'Fictive SansRue', '', '', '1000', 'Ville Fictive', '');
        $abo1 = $this->abonnement([$this->situation()], 'a');
        $abo2 = $this->abonnement([$this->situation()], 'b');
        $abo3 = $this->abonnement([$this->situation(destinataires: [$incomplet])], 'c');
        $liste = $this->calculer([$abo1, $abo2, $abo3]);
        self::assertCount(3, $liste->lignes);
        self::assertCount(4, $liste->anomalies);
        self::assertSame(
            ['adresse_incomplete', 'doublon_destinataire_adresse', 'doublon_destinataire_adresse', 'pays_manquant'],
            array_column($liste->anomalies, 'motif')
        );
    }

    public function testOrdreDeterministeEtImmutabilite(): void
    {
        $a = $this->abonnement([$this->situation()], 'a');
        $b = $this->abonnement([$this->situation()], 'b');
        $un = $this->calculer([$a, $b]);
        $deux = $this->calculer([$b, $a]);
        self::assertSame($un->lignes, $deux->lignes);
        self::assertSame($un->anomalies, $deux->anomalies);
        $this->expectException(\Error::class);
        $un->lignes[0]['rue'] = 'mutation';
    }

    public function testFinEffectiveAtteinteMemeSansEvenementExpire(): void
    {
        $s = new Situation(
            $this->date('2026-11-01'),
            $this->date('2026-11-01'),
            'actif',
            true,
            ['171'],
            [$this->personne()],
            $this->date('2026-12-19')
        );
        self::assertSame([], $this->calculer([$this->abonnement([$s])])->lignes);
    }

    public function testNumeroEtClotureDoiventCorrespondreAuCalendrier(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        ListeEnvoi::etablir($this->numero(), new Calendrier([]), [], $this->numero()->cloture);
    }

    public function testClotureDivergenteRefusee(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        ListeEnvoi::etablir(
            $this->numero(),
            new Calendrier([$this->numero()]),
            [],
            $this->date('2026-12-21')
        );
    }

    public function testHistoriqueAmbiguRefuse(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->abonnement([$this->situation(), $this->situation(etat: 'suspendu')]);
    }

    public function testOrigineInconnueRefusee(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->abonnement([$this->situation()], origine: 'inconnue');
    }

    public function testAbonnementDupliqueRefuse(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $a = $this->abonnement([$this->situation()]);
        $this->calculer([$a, $a]);
    }

    public function testEtatInconnuRefuse(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->situation(etat: 'inconnu');
    }

    public function testOffertGroupeEtCommandeUnitaire(): void
    {
        $offert = $this->abonnement([$this->situation()], 'cadeau', 'offert');
        $groupe = $this->abonnement([
            $this->situation(destinataires: [$this->personne('ancien')]),
            $this->situation('2026-12-19', destinataires: [$this->personne('benef-1'), $this->personne('benef-2')]),
            $this->situation('2026-12-21', destinataires: [$this->personne('remplacant')]),
        ], 'groupe', 'groupe');
        $unitaire = $this->abonnement([$this->situation()], 'unitaire', 'numero_unite');
        $liste = $this->calculer([$offert, $groupe, $unitaire]);
        self::assertCount(3, $liste->lignes);
        self::assertSame(['fictif-1', 'benef-1', 'benef-2'], array_column($liste->lignes, 'destinataire_id'));
        self::assertSame(['offert', 'groupe', 'groupe'], array_column($liste->lignes, 'origine'));
        self::assertSame([], $this->calculer([
            $this->abonnement([$this->situation(destinataires: [])], 'libre', 'groupe'),
        ])->lignes);
    }
}
