<?php

declare(strict_types=1);

require_once dirname(__DIR__) . '/tests-c13/bootstrap.php';

use Imagine\Site\EnvoiRegles;
use PHPUnit\Framework\TestCase;

final class EnvoiReglesTest extends TestCase
{
    private function calendrier(): array
    {
        $rows = [];
        foreach ([2026, 2027, 2028] as $year) {
            foreach ([1, 4, 7, 10] as $i => $month) {
                $rows[] = ['code' => "$year-T" . ($i + 1), 'type' => 'regulier',
                    'sortie' => sprintf('%d-%02d-15', $year, $month),
                    'cloture' => sprintf('%d-%02d-05', $year, $month)];
            }
        }
        return $rows;
    }

    private function donnees(): array
    {
        return ['id' => '10', 'user' => '20', 'creation' => strtotime('2026-01-01 UTC'),
            'debut' => '2026-01-01 00:00:00', 'fin' => '', 'etat' => 'active',
            'paiement' => strtotime('2026-01-01 UTC'), 'grace_debut' => '', 'grace_fin' => '',
            'destinataire' => 'Personnage Fictif', 'rue' => '1 rue Imaginaire', 'complement' => '',
            'code_postal' => '1000', 'ville' => 'Ville Fictive', 'pays' => 'BE'];
    }

    private function vue(array $data, string $code = '2026-T1', ?array $events = null): array
    {
        return EnvoiRegles::calculer($code, $events ?? [['observe_utc' => '2026-01-02 00:00:00', 'donnees' => $data]],
            new DateTimeImmutable('2028-01-01 UTC'), $this->calendrier());
    }

    public function testCadeauEtGroupeConserventIdentitesEtPlacesLibres(): void
    {
        $data = $this->donnees();
        $person = ['id' => 'benef-1', 'nom' => 'Beneficiaire Fictif', 'rue' => '7 rue Fictive',
            'complement' => '', 'code_postal' => '75000', 'ville' => 'Ville Fictive', 'pays' => 'FR'];
        $data['origine'] = 'offert';
        $data['beneficiaires'] = [$person];
        $data['beneficiaires_resolus'] = true;
        $gift = $this->vue($data);
        self::assertSame('benef-1', $gift['liste']->lignes[0]['destinataire_id']);
        self::assertSame('offert', $gift['liste']->lignes[0]['origine']);
        $data['origine'] = 'groupe';
        $data['places'] = 3;
        $other = $person;
        $other['id'] = 'benef-2';
        $other['nom'] = 'Autre Fictif';
        $data['beneficiaires'][] = $other;
        self::assertCount(2, $this->vue($data)['liste']->lignes);
        $data['beneficiaires_resolus'] = false;
        self::assertSame([], $this->vue($data)['liste']->lignes);
        self::assertTrue($this->vue($data)['historique_incomplet']);
        self::assertSame('beneficiaires_non_resolus', $this->vue($data)['exclus'][0]['motif']);
    }

    public function testRenouvellementEnregistreSansDeplacerLeDebut(): void
    {
        $data = $this->donnees();
        $event = static fn (array $d): array => [['observe_utc' => '2027-01-02 00:00:00', 'donnees' => $d]];
        self::assertSame([], $this->vue($data, '2027-T1', $event($data))['liste']->lignes);
        $data['renouvellements'] = [['id' => '90', 'debut' => '2027-01-01 00:00:00',
            'paiement' => strtotime('2027-01-01 UTC')]];
        $view = $this->vue($data, '2027-T1', $event($data));
        self::assertCount(1, $view['liste']->lignes);
        self::assertSame(['2027-T1', '2027-T2', '2027-T3', '2027-T4'], $view['blocs']['10'][1]['numeros']);
        self::assertSame('2026-01-01 00:00:00', $data['debut']);
        $data['renouvellements'][0]['paiement'] = null;
        self::assertSame([], $this->vue($data, '2027-T1', $event($data))['liste']->lignes);
    }

    public function testClotureEgaleRejeuEtHistoriqueBeneficiaires(): void
    {
        $data = $this->donnees();
        $base = ['observe_utc' => '2026-01-02 00:00:00', 'donnees' => $data];
        $data['rue'] = 'Adresse apres cloture';
        $late = ['observe_utc' => '2026-01-04 23:00:00', 'donnees' => $data]; // minuit Bruxelles
        $before = $this->vue($data, '2026-T1', [$base]);
        $after = $this->vue($data, '2026-T1', [$late, $base, $base]);
        self::assertSame($before['liste']->lignes, $after['liste']->lignes);
        $unknown = $this->vue($data, '2026-T1', [$late]);
        self::assertTrue($unknown['historique_incomplet']);
        self::assertSame([], $unknown['liste']->lignes);
    }

    public function testCalendrierPasseImmuableEtFuturModifiable(): void
    {
        $rows = $this->calendrier();
        $next = $rows;
        $next[4]['cloture'] = '2027-01-06';
        self::assertSame($next, EnvoiRegles::reviserCalendrier($rows, $next, new DateTimeImmutable('2026-11-01 UTC')));
        $next[0]['cloture'] = '2026-01-07';
        $this->expectException(LogicException::class);
        EnvoiRegles::reviserCalendrier($rows, $next, new DateTimeImmutable('2026-11-01 UTC'));
    }

    public function testCalendrierIncompletFermeExport(): void
    {
        $rows = array_slice($this->calendrier(), 0, 2);
        $view = EnvoiRegles::calculer('2026-T1', [['observe_utc' => '2026-01-02 00:00:00', 'donnees' => $this->donnees()]],
            new DateTimeImmutable('2026-01-03 UTC'), $rows);
        self::assertTrue($view['historique_incomplet']);
        self::assertSame('calendrier_incomplet', $view['exclus'][0]['motif']);
        self::assertSame([], $view['liste']->lignes);
    }

    public function testFinNativeNulleEtInitialCreationFerme(): void
    {
        $data = $this->donnees();
        $data['fin'] = 0;
        self::assertCount(1, $this->vue($data)['liste']->lignes);
        $data['creation'] = strtotime('2026-01-04 23:00:00 UTC');
        self::assertSame([], $this->vue($data)['liste']->lignes);
    }

    public function testReferenceGeleeResisteCalendrierCourantEtBeneficiaireModifie(): void
    {
        $data = $this->donnees();
        $data['origine'] = 'offert';
        $data['beneficiaires_resolus'] = true;
        $data['beneficiaires'] = [['id' => '30', 'nom' => 'Beneficiaire Fictif', 'rue' => 'Avant cloture',
            'complement' => '', 'code_postal' => '1000', 'ville' => 'Ville Fictive', 'pays' => 'BE']];
        $base = ['observe_utc' => '2026-01-02 00:00:00', 'donnees' => $data];
        $snapshot = EnvoiRegles::figer('2026-T1', [$base], new DateTimeImmutable('2026-02-01 UTC'), $this->calendrier());
        $data['beneficiaires'][0]['rue'] = 'Apres cloture';
        $late = ['observe_utc' => '2026-01-06 00:00:00', 'donnees' => $data];
        self::assertSame($this->vue($data, '2026-T1', [$base, $late])['liste']->lignes,
            EnvoiRegles::relire($snapshot, new DateTimeImmutable('2028-01-01 UTC'))['liste']->lignes);
        self::assertSame('Avant cloture', EnvoiRegles::relire($snapshot, new DateTimeImmutable('2028-01-01 UTC'))['liste']->lignes[0]['rue']);
        $snapshot['blocs'] = [];
        $this->expectException(RuntimeException::class);
        EnvoiRegles::relire($snapshot, new DateTimeImmutable('2028-01-01 UTC'));
    }

    public function testRejeuContradictoireRefuse(): void
    {
        $data = $this->donnees();
        $first = ['observe_utc' => '2026-01-02 00:00:00', 'donnees' => $data];
        $data['rue'] = 'Contradiction au meme instant';
        $this->expectException(LogicException::class);
        $this->vue($data, '2026-T1', [$first, ['observe_utc' => $first['observe_utc'], 'donnees' => $data]]);
    }

    public function testPaiementFuturEtRenouvellementALaClotureRestentFermes(): void
    {
        $data = $this->donnees();
        $data['paiement'] = strtotime('2026-01-03 UTC');
        self::assertSame([], $this->vue($data)['liste']->lignes);
        $data['paiement'] = strtotime('2026-01-01 UTC');
        $data['renouvellements'] = [['id' => '90', 'debut' => '2027-01-01 00:00:00',
            'paiement' => strtotime('2027-01-04 23:00:00 UTC')]];
        self::assertSame([], $this->vue($data, '2027-T1', [['observe_utc' => '2027-01-04 23:00:00', 'donnees' => $data]])['liste']->lignes);
    }

    public function testIndividuelEtNonPayeRestentDistincts(): void
    {
        $data = $this->donnees();
        self::assertCount(1, $this->vue($data)['liste']->lignes);
        $data['paiement'] = null;
        self::assertSame([], $this->vue($data)['liste']->lignes);
        self::assertSame('paiement_non_valide', $this->vue($data)['exclus'][0]['motif']);
    }
}
