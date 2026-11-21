<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Acces;

use Imagine\Pilotage\Acces\Moteur;
use PHPUnit\Framework\TestCase;

final class DroitsTest extends TestCase
{
    public static function achat(string $numero = '170'): array
    {
        return ['type' => 'achat', 'numero' => $numero, 'acquis_le' => DecisionTest::date('2026-10-02')];
    }

    public function testAchatNumeroEstPerpetuelMaisExactArticlesEtPdf(): void
    {
        foreach (['article', 'pdf'] as $type) {
            foreach (['170', '169', '171', '0170', 'HS-2026'] as $numero) {
                foreach (['2026-10-01 23:59:59', '2026-10-02 00:00:00', '2026-10-02 00:00:01', '2099-12-31'] as $date) {
                    $permis = $numero === '170' && $date !== '2026-10-01 23:59:59';
                    $decision = (new Moteur())->decider(
                        DecisionTest::contenu(['type' => $type, 'numero' => $numero]),
                        DecisionTest::visiteur([self::achat()]),
                        DecisionTest::robot(),
                        DecisionTest::date($date),
                    );
                    self::assertSame($permis, $decision->complet, "$type-$numero-$date");
                    self::assertSame(
                        $permis ? 'numero_achete' : ($numero !== '170' ? 'autre_numero' : 'achat_pas_commence'),
                        $decision->motif->value,
                    );
                    self::assertSame($permis ? 'aucun' : 'abonnement', $decision->bloc->value);
                }
            }
        }
    }

    public function testEquipeEtCooperateurSansConfusionDeRole(): void
    {
        foreach (['redaction', 'administration', null] as $role) {
            $droit = $role === null ? ['type' => 'cooperateur'] : ['type' => 'equipe', 'role' => $role];
            $decision = (new Moteur())->decider(
                DecisionTest::contenu(['type' => 'pdf']),
                DecisionTest::visiteur([$droit]),
                DecisionTest::robot(),
                DecisionTest::date(),
            );
            self::assertSame($role !== null, $decision->complet);
            self::assertSame($role === null ? 'cooperateur_sans_abonnement' : 'equipe', $decision->motif->value);
            self::assertSame($role === null ? 'abonnement' : 'aucun', $decision->bloc->value);
        }
    }

    public function testCombinaisonsTousSousEnsemblesEtOrdreInverseFavorisentLeDroitValide(): void
    {
        $droits = [
            ['droit' => ['type' => 'cooperateur'], 'motif' => 'cooperateur_sans_abonnement', 'plein' => false],
            ['droit' => self::achat('169'), 'motif' => 'autre_numero', 'plein' => false],
            ['droit' => AbonnementTest::droit(['etat' => 'expire']), 'motif' => 'expire', 'plein' => false],
            ['droit' => AbonnementTest::droit(['etat' => 'virement_non_valide']), 'motif' => 'virement_non_valide',
                'plein' => false],
            ['droit' => AbonnementTest::droit(['etat' => 'suspendu']), 'motif' => 'suspendu', 'plein' => false],
            ['droit' => AbonnementTest::droit(['etat' => 'grace']), 'motif' => 'delai_grace', 'plein' => true],
            ['droit' => AbonnementTest::droit(['type' => 'groupe']), 'motif' => 'groupe_actif', 'plein' => true],
            ['droit' => AbonnementTest::droit(['type' => 'offert']), 'motif' => 'offert_actif', 'plein' => true],
            ['droit' => AbonnementTest::droit(), 'motif' => 'abonnement_actif', 'plein' => true],
            ['droit' => self::achat(), 'motif' => 'numero_achete', 'plein' => true],
            ['droit' => ['type' => 'equipe', 'role' => 'redaction'], 'motif' => 'equipe', 'plein' => true],
        ];
        for ($masque = 0; $masque < (1 << count($droits)); $masque++) {
            $selection = [];
            $motif = 'sans_droit';
            $plein = false;
            foreach ($droits as $index => $ligne) {
                if (($masque & (1 << $index)) !== 0) {
                    $selection[] = $ligne['droit'];
                    $motif = $ligne['motif'];
                    $plein = $ligne['plein'];
                }
            }
            foreach ([$selection, array_reverse($selection)] as $ordre) {
                $decision = (new Moteur())->decider(
                    DecisionTest::contenu(),
                    DecisionTest::visiteur($ordre),
                    DecisionTest::robot(),
                    DecisionTest::date(),
                );
                self::assertSame($plein, $decision->complet, "Sous-ensemble $masque");
                self::assertSame($motif, $decision->motif->value, "Sous-ensemble $masque");
            }
        }
    }

    public function testAchatIndependantOuvrePdfAncienMemeAvecGraceOuSuspension(): void
    {
        foreach (['grace', 'suspendu', 'expire', 'actif'] as $etat) {
            $decision = (new Moteur())->decider(
                DecisionTest::contenu(['type' => 'pdf']),
                DecisionTest::visiteur([
                    AbonnementTest::droit(['etat' => $etat, 'debut' => DecisionTest::date('2026-11-01')]),
                    self::achat(),
                ]),
                DecisionTest::robot(),
                DecisionTest::date(),
            );
            self::assertTrue($decision->complet);
            self::assertSame('numero_achete', $decision->motif->value);
            self::assertSame('aucun', $decision->bloc->value);
        }
    }
}
