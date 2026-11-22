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
    public static function setUpBeforeClass(): void
    {
        ExportCsvTest::setUpBeforeClass();
    }

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
            'A-CARTE' => ['actif', true, 'BE', 'carte@example.org', 'carte-fictive', ['carte-fictive']],
            'A-SEPA4' => ['actif', true, 'BE', 'sepa@example.org', 'sepa-fictive', ['sepa-fictive']],
            'A-GRACE' => ['grace', false, 'BE', 'grace@example.org', 'grace-fictive', ['grace-fictive']],
            'A-SUSP' => ['suspendu', true, 'BE', 'suspendue@example.org', 'suspendue-fictive', []],
            'A-VIR' => ['actif', false, 'BE', 'virement@example.org', 'virement-fictif', []],
            'A-PAPIER attente' => ['actif', false, 'BE', 'papier.attente@example.org', 'papier-attente', []],
            'A-PAPIER valide' => ['actif', true, 'BE', 'papier@example.org', 'papier-fictif', ['papier-fictif']],
            'A-EXPIRE' => ['expire', true, 'BE', 'expiree@example.org', 'expiree-fictive', []],
            'A-NONRENOUV' => ['actif', true, 'BE', 'nonrenouv@example.org', 'nonrenouv-fictive', ['nonrenouv-fictive']],
            'A-ETRANGER' => ['actif', true, 'FR', 'etrangere@example.org', 'etrangere-fictive', ['etrangere-fictive']],
            'A-SANSMAIL' => ['actif', true, 'BE', null, 'horsligne-fictive', ['horsligne-fictive']],
        ];
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('profils')]
    public function testProfilsACloture(
        string $etat,
        bool $paiement,
        string $pays,
        ?string $emailCompte,
        string $idDestinataire,
        array $idsAttendus
    ): void {
        // L'email reste une donnée du compte fictif, jamais une entrée du moteur postal.
        $compte = ['email' => $emailCompte, 'destinataire_id' => $idDestinataire];
        $destinataire = new Destinataire(
            $compte['destinataire_id'],
            'Profil Fictif',
            '1 rue Imaginaire',
            '',
            '00100',
            'Ville Fictive',
            $pays
        );
        $liste = $this->calculer([$this->abonnement([
            $this->situation(etat: $etat, paiement: $paiement, destinataires: [$destinataire]),
        ])]);
        self::assertSame($idsAttendus, array_column($liste->lignes, 'destinataire_id'));
        self::assertSame([], $liste->anomalies);
        if ($idsAttendus !== []) {
            self::assertSame($pays, $liste->lignes[0]['pays']);
            self::assertSame('00100', $liste->lignes[0]['code_postal']);
            self::assertArrayNotHasKey('email', $liste->lignes[0]);
            self::assertStringContainsString(
                ',' . $pays . ',',
                \Imagine\Pilotage\Envoi\ExportCsv::liste($liste)
            );
        }
    }

    public static function originesSansDestinataire(): array
    {
        return [
            'individuel' => ['abonnement', [['motif' => 'destinataire_manquant', 'abonnement_id' => 'sans-personne']]],
            'offert' => ['offert', [['motif' => 'destinataire_manquant', 'abonnement_id' => 'sans-personne']]],
            'groupe libre' => ['groupe', []],
        ];
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('originesSansDestinataire')]
    public function testSansDestinataireNeDisparaitPasEnSilence(string $origine, array $anomalies): void
    {
        $liste = $this->calculer([
            $this->abonnement([$this->situation(destinataires: [])], 'sans-personne', $origine),
        ]);
        self::assertSame([], $liste->lignes);
        self::assertSame($anomalies, $liste->anomalies);
        if ($origine !== 'groupe') {
            $this->expectException(\LogicException::class);
        }
        self::assertSame(
            implode(',', \Imagine\Pilotage\Envoi\ExportCsv::COLONNES) . "\n",
            \Imagine\Pilotage\Envoi\ExportCsv::liste($liste)
        );
    }

    public function testAbsenceDestinataireNonEligibleSansAnomalie(): void
    {
        $liste = $this->calculer([
            $this->abonnement([$this->situation(paiement: false, destinataires: [])]),
        ]);
        self::assertSame([], $liste->lignes);
        self::assertSame([], $liste->anomalies);
    }

    public function testGraceSansPaiementIncluseParReglageUnique(): void
    {
        $numero = $this->numero();
        foreach ([false, true] as $paiement) {
            $abo = $this->abonnement([$this->situation(etat: 'grace', paiement: $paiement)]);
            self::assertCount(1, $this->calculer([$abo])->lignes);
            self::assertSame([], ListeEnvoi::etablir(
                $numero,
                new Calendrier([$numero]),
                [$abo],
                $numero->cloture,
                inclureGrace: false
            )->lignes);
        }
    }

    public function testGraceAvecFinAtteinteAbsenteQuelQueSoitLePaiement(): void
    {
        foreach ([false, true] as $paiement) {
            $situation = new Situation(
                $this->date('2026-11-01'),
                $this->date('2026-11-01'),
                'grace',
                $paiement,
                ['171'],
                [$this->personne()],
                $this->numero()->cloture
            );
            self::assertSame([], $this->calculer([$this->abonnement([$situation])])->lignes);
        }
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

    public static function champsPostaux(): array
    {
        $cas = [];
        foreach (['nom', 'rue', 'codePostal', 'ville', 'pays'] as $champ) {
            foreach (['ordinaire' => ' ', 'insecable' => "\u{00A0}", 'fine' => "\u{202F}"] as $type => $espace) {
                $cas[$champ . ' vide ' . $type] = [$champ, $espace, false];
                $cas[$champ . ' entoure ' . $type] = [$champ, $espace . 'Fictif' . $espace, true];
            }
        }
        return $cas;
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('champsPostaux')]
    public function testPresencePostaleUnicode(string $champ, string $valeur, bool $present): void
    {
        $champs = [
            'id' => 'fictif', 'nom' => 'Camille Fictive', 'rue' => '1 rue Imaginaire',
            'complement' => '', 'codePostal' => '1000', 'ville' => 'Ville Fictive', 'pays' => 'BE',
        ];
        $champs[$champ] = $valeur;
        $liste = $this->calculer([
            $this->abonnement([$this->situation(destinataires: [new Destinataire(...$champs)])]),
        ]);
        self::assertCount(1, $liste->lignes);
        self::assertSame(
            $present ? [] : [$champ === 'pays' ? 'pays_manquant' : 'adresse_incomplete'],
            array_column($liste->anomalies, 'motif')
        );
        if (!$present) {
            $this->expectException(\LogicException::class);
        }
        self::assertNotEmpty(\Imagine\Pilotage\Envoi\ExportCsv::liste($liste));
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

    public function testDoublonNomAdresseCasseAccentueeEtEspacesUnicode(): void
    {
        $a = new Destinataire(
            'a',
            "\u{00A0}ÉLODIE  FICTIVE\u{202F}",
            '1 RUE IMAGINAIRE',
            '',
            '1000',
            'CITÉ FICTIVE',
            'BE'
        );
        $b = new Destinataire('b', 'élodie fictive', '1 rue imaginaire', '', '1000', 'cité fictive', 'be');
        $liste = $this->calculer([
            $this->abonnement([$this->situation(destinataires: [$a])], 'a'),
            $this->abonnement([$this->situation(destinataires: [$b])], 'b'),
        ]);
        self::assertCount(2, $liste->lignes);
        self::assertSame(['a', 'b'], array_column($liste->lignes, 'destinataire_id'));
        self::assertSame(
            ['doublon_destinataire_adresse', 'doublon_destinataire_adresse'],
            array_column($liste->anomalies, 'motif')
        );
        self::assertSame([0, 1], array_column($liste->anomalies, 'ligne'));
        self::assertSame($liste->lignes, array_column($liste->anomalies, 'exemplaire'));
        $this->expectException(\LogicException::class);
        \Imagine\Pilotage\Envoi\ExportCsv::liste($liste);
    }

    public function testDoublonIdentiteStableMemeAdresseMalgreNomDifferent(): void
    {
        $a = new Destinataire('commun', 'Élodie Fictive', '1 rue Imaginaire', '', '1000', 'Ville Fictive', 'BE');
        $b = new Destinataire('commun', 'Nom Fictif Modifie', '1 rue Imaginaire', '', '1000', 'Ville Fictive', 'BE');
        $liste = $this->calculer([
            $this->abonnement([$this->situation(destinataires: [$a])], 'a'),
            $this->abonnement([$this->situation(destinataires: [$b])], 'b'),
        ]);
        self::assertCount(2, $liste->lignes);
        self::assertSame([0, 1], array_column($liste->anomalies, 'ligne'));
        self::assertSame(
            ['doublon_destinataire_adresse', 'doublon_destinataire_adresse'],
            array_column($liste->anomalies, 'motif')
        );
    }

    public function testMemeIdentiteStableMaisAdresseDifferenteSansDoublon(): void
    {
        $liste = $this->calculer([
            $this->abonnement([$this->situation(destinataires: [$this->personne('commun')])], 'a'),
            $this->abonnement([$this->situation(destinataires: [$this->personne('commun', '2 rue Autre')])], 'b'),
        ]);
        self::assertCount(2, $liste->lignes);
        self::assertSame([], $liste->anomalies);
    }

    public function testDestinatairesDistinctsMemeAdresseNeSontPasFusionnes(): void
    {
        $a = $this->personne('a');
        $b = new Destinataire('b', 'Autre Fictive', $a->rue, '', '1000', 'Ville Fictive', 'BE');
        $liste = $this->calculer([
            $this->abonnement([$this->situation(destinataires: [$a])], 'a'),
            $this->abonnement([$this->situation(destinataires: [$b])], 'b'),
        ]);
        self::assertCount(2, $liste->lignes);
        self::assertSame([], $liste->anomalies);
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

    public function testExportRefuseAnomaliesNonRevues(): void
    {
        $this->expectException(\LogicException::class);
        $a = $this->abonnement([$this->situation()], 'a');
        $b = $this->abonnement([$this->situation()], 'b');
        \Imagine\Pilotage\Envoi\ExportCsv::liste($this->calculer([$a, $b]));
    }

    public function testExportAnomaliesRevuesEtPaysEtranger(): void
    {
        $d = new Destinataire('etranger', 'Fictive Etrangere', '2 rue Imaginaire', '', '00100', 'Ville Fictive', 'FR');
        $a = $this->abonnement([$this->situation(destinataires: [$d])], 'a');
        $b = $this->abonnement([$this->situation(destinataires: [$d])], 'b');
        $csv = \Imagine\Pilotage\Envoi\ExportCsv::liste($this->calculer([$a, $b]), anomaliesRevues: true);
        self::assertStringContainsString('00100', $csv);
        self::assertStringContainsString(',FR,', $csv);
        self::assertSame(3, substr_count($csv, "\n"));
    }

    public function testIntegrationC01PremierDernierEtHorsSerie(): void
    {
        $calendrier = new Calendrier(require dirname(__DIR__) . '/Numeros/fixtures/calendrier.php');
        $moteur = new \Imagine\Pilotage\Numeros\Moteur($calendrier);
        $initiale = $moteur->ouvrir($this->date('2026-10-08'));
        $renouvellement = $moteur->renouveler($initiale, $this->date('2027-10-08'));
        $cas = [
            [$initiale, ['171', '172', '173', '174', 'HS-2027'], [
                '170' => 0, '171' => 1, '172' => 1, '173' => 1, '174' => 1, '175' => 0,
                'HS-2026' => 0, 'HS-2027' => 1, 'HS-2028' => 0,
            ]],
            [$renouvellement, ['175', '176', '177', '178', 'HS-2028'], [
                '174' => 0, '175' => 1, '176' => 1, '177' => 1, '178' => 1, 'HS-2027' => 0, 'HS-2028' => 1,
            ]],
        ];
        $parId = [];
        foreach ($calendrier->numeros as $numero) {
            $parId[$numero->id] = $numero;
        }
        foreach ($cas as [$annee, $dusAttendus, $exemplairesAttendus]) {
            $dus = array_map(static fn (Numero $n): string => $n->id, $moteur->numeros($annee));
            $horsSerie = $moteur->horsSerie($annee);
            self::assertNotNull($horsSerie);
            $dus[] = $horsSerie->id;
            self::assertSame($dusAttendus, $dus);
            $situation = new Situation($annee->debut, $annee->debut, 'actif', true, $dus, [$this->personne()]);
            $abo = new Abonnement('abonnement-fictif', 'abonnement', $annee->debut, [$situation]);
            foreach ($exemplairesAttendus as $id => $attendu) {
                $numero = $parId[$id];
                $liste = ListeEnvoi::etablir($numero, $calendrier, [$abo], $numero->cloture);
                self::assertCount($attendu, $liste->lignes, (string) $id);
                self::assertSame([], $liste->anomalies, (string) $id);
            }
        }
    }

    public function testHistoriqueInvalideRefuse(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->abonnement(['pas une situation']);
    }

    public function testDestinataireRepeteDansUnGroupeRefuse(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->situation(destinataires: [$this->personne(), $this->personne()]);
    }

    public function testAbonnementIndividuelAvecPlusieursDestinatairesRefuse(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->abonnement([$this->situation(destinataires: [$this->personne('a'), $this->personne('b')])]);
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
