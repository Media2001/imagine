<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Acces;

use Imagine\Pilotage\Acces\Moteur;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

final class AbonnementTest extends TestCase
{
    public static function droit(array $modifications = []): array
    {
        return array_replace([
            'type' => 'abonnement', 'etat' => 'actif',
            'debut' => DecisionTest::date('2026-10-01 00:00:00'),
            'fin' => DecisionTest::date('2026-12-01 00:00:00'),
        ], $modifications);
    }

    public static function table(): iterable
    {
        foreach (['abonnement', 'offert', 'groupe'] as $type) {
            foreach (['article', 'pdf'] as $contenu) {
                foreach (['actif', 'grace', 'suspendu', 'expire', 'virement_non_valide'] as $etat) {
                    $motif = match ($etat) {
                        'actif' => $type . '_actif',
                        'grace' => 'delai_grace',
                        default => $etat,
                    };
                    $complet = in_array($etat, ['actif', 'grace'], true);
                    $bloc = match ($etat) {
                        'actif' => 'aucun',
                        'grace', 'suspendu', 'virement_non_valide' => 'regularisation',
                        default => 'abonnement',
                    };
                    yield "$type-$contenu-$etat" => [$type, $contenu, $etat, $complet, $motif, $bloc];
                }
            }
        }
    }

    #[DataProvider('table')]
    public function testTableAbonnements(
        string $type,
        string $contenu,
        string $etat,
        bool $complet,
        string $motif,
        string $bloc,
    ): void {
        $decision = (new Moteur())->decider(
            DecisionTest::contenu(['type' => $contenu]),
            DecisionTest::visiteur([self::droit(['type' => $type, 'etat' => $etat])]),
            DecisionTest::robot(),
            DecisionTest::date(),
        );
        self::assertSame($complet, $decision->complet);
        self::assertSame($motif, $decision->motif->value);
        self::assertSame($bloc, $decision->bloc->value);
    }

    public function testDatesDeDateADateAvecBornesInclusivesExclusivesAUneSeconde(): void
    {
        foreach (['abonnement', 'offert', 'groupe'] as $type) {
            foreach (['actif', 'grace'] as $etat) {
                $droit = self::droit(['type' => $type, 'etat' => $etat]);
                foreach (
                    [
                    ['2026-09-30 23:59:59', false, 'abonnement_pas_commence'],
                    ['2026-10-01 00:00:00', true, $etat === 'grace' ? 'delai_grace' : $type . '_actif'],
                    ['2026-10-01 00:00:01', true, $etat === 'grace' ? 'delai_grace' : $type . '_actif'],
                    ['2026-11-30 23:59:59', true, $etat === 'grace' ? 'delai_grace' : $type . '_actif'],
                    ['2026-12-01 00:00:00', false, 'expire'],
                    ['2026-12-01 00:00:01', false, 'expire'],
                    ] as [$date, $complet, $motif]
                ) {
                    $decision = (new Moteur())->decider(
                        DecisionTest::contenu(['sortie' => DecisionTest::date('2026-01-01 00:00:00')]),
                        DecisionTest::visiteur([$droit]),
                        DecisionTest::robot(),
                        DecisionTest::date($date),
                    );
                    self::assertSame($complet, $decision->complet, "$type-$etat-$date");
                    self::assertSame($motif, $decision->motif->value);
                }
            }
        }
    }

    public function testPdfAnterieurAttendArbitrageSansRetirerLesArticles(): void
    {
        foreach (['actif', 'grace'] as $etat) {
            foreach (['article', 'pdf'] as $type) {
                $decision = (new Moteur())->decider(
                    DecisionTest::contenu(['type' => $type, 'sortie' => DecisionTest::date('2026-09-01')]),
                    DecisionTest::visiteur([self::droit(['etat' => $etat])]),
                    DecisionTest::robot(),
                    DecisionTest::date(),
                );
                self::assertSame($type === 'article', $decision->complet);
                if ($type === 'pdf') {
                    self::assertSame('pdf_anterieur_a_arbitrer', $decision->motif->value);
                    self::assertSame('abonnement', $decision->bloc->value);
                }
            }
        }
    }
}
