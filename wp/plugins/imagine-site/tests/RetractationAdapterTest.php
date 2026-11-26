<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Retractation;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class RetractationAdapterTest extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/RetractationWPStubs.php';
    }

    public function testDeuxEtapesAbandonConfirmationEtOrigineManuelle(): void
    {
        self::assertTrue(is_callable([Retractation::class, 'panneau']), 'Parcours deux étapes absent');
        $initial = Retractation::panneau(10, []);
        self::assertStringContainsString('Me rétracter', $initial);
        self::assertStringContainsString('facultatif', $initial);
        self::assertStringNotContainsString('Accusé de réception', $initial);
        self::assertSame([], $GLOBALS['retract_notes']);
        $review = Retractation::panneau(20, ['etape' => 'preparer', '_c25' => 'nonce', 'raison' => '<b>Motif fictif</b>']);
        self::assertStringContainsString('Confirmer ma demande', $review);
        self::assertStringContainsString('Commande n°10', $review);
        self::assertStringContainsString('2030-01-01', $review);
        self::assertSame([], $GLOBALS['retract_notes'], 'Abandon sans persistance');
        self::assertSame([], $GLOBALS['retract_options']);
        self::assertStringContainsString('refusée', Retractation::panneau(10, ['etape' => 'confirmer', '_c25' => 'faux', 'confirmation' => 'confirmer']));
        self::assertSame([], $GLOBALS['retract_notes']);
        $receipt = Retractation::panneau(10, ['etape' => 'confirmer', '_c25' => 'nonce', 'confirmation' => 'confirmer', 'raison' => '']);
        self::assertStringContainsString('Accusé de réception', $receipt);
        self::assertStringContainsString('2030-01-02T00:00:00Z', $receipt);
        self::assertStringContainsString('Accusé de réception', Retractation::panneau(20, []));
        self::assertCount(1, $GLOBALS['retract_notes']);
    }

    public function testRefusHorsDelaiTitulaireConfirmationEtVerrou(): void
    {
        foreach ([[11, 7, 'confirmer'], [10, 8, 'confirmer'], [10, 0, 'confirmer'], [10, 7, ''], [999, 7, 'confirmer']] as [$target, $user, $confirm]) {
            self::assertInstanceOf(\WP_Error::class, Retractation::demander($target, $user, $confirm, ''));
        }
        $GLOBALS['retract_now'] = strtotime('2030-02-01 UTC');
        self::assertStringNotContainsString('name="etape"', Retractation::panneau(10, []));
        self::assertInstanceOf(\WP_Error::class, Retractation::demander(10, 7, 'confirmer', ''));
        $GLOBALS['retract_options'][Retractation::OPTION] = ['jours' => 30, 'origine' => 'manuelle'];
        $GLOBALS['retract_orders'][10]->meta[Retractation::MANUELLE] = '2030-01-15';
        self::assertTrue(Retractation::ouverte($GLOBALS['retract_orders'][10]));
        $GLOBALS['retract_now'] = strtotime('2030-02-15 UTC');
        self::assertFalse(Retractation::ouverte($GLOBALS['retract_orders'][10]));
        self::assertInstanceOf(\WP_Error::class, Retractation::demander(10, 7, 'confirmer', ''));
        $GLOBALS['retract_now'] = strtotime('2030-01-20 UTC');
        $GLOBALS['wpdb']->locked = true;
        self::assertInstanceOf(\WP_Error::class, Retractation::demander(20, 7, 'confirmer', ''));
        self::assertSame([], $GLOBALS['retract_notes']);
    }

    public function testEchecsNoteEtJournalNannoncentPasDeSucces(): void
    {
        foreach (['retract_fail_note', 'retract_fail_journal'] as $fault) {
            $GLOBALS[$fault] = true;
            self::assertInstanceOf(\WP_Error::class, Retractation::demander(10, 7, 'confirmer', 'Motif'));
            self::assertSame([], $GLOBALS['retract_notes']);
            self::assertSame([], $GLOBALS['retract_options']);
            $GLOBALS[$fault] = false;
        }
        self::assertIsArray(Retractation::demander(10, 7, 'confirmer', 'Reprise'));
    }

    public function testDemandeSeulePersistanteEtRejeuSansAucunEffet(): void
    {
        self::assertTrue(class_exists(Retractation::class), 'Adaptateur C25 absent');
        $before = $GLOBALS['retract_orders'][10]->business;
        $first = Retractation::demander(10, 7, 'confirmer', 'Motif fictif facultatif');
        self::assertIsArray($first);
        self::assertSame(10, $first['commande']);
        self::assertSame(7, $first['compte']);
        self::assertSame('Motif fictif facultatif', $first['raison']);
        self::assertSame('2030-01-02T00:00:00Z', $first['date']);
        self::assertSame($first, Retractation::demander(10, 7, 'confirmer', 'Autre motif'));
        self::assertSame($before, $GLOBALS['retract_orders'][10]->business);
        self::assertCount(1, $GLOBALS['retract_notes']);
        self::assertCount(1, $GLOBALS['retract_options']);
        self::assertSame(0, $GLOBALS['retract_mail']);
        self::assertSame(0, $GLOBALS['retract_http']);
        self::assertSame(0, $GLOBALS['retract_financial']);
        self::assertSame('imagine_reglages_journal_retractation_10', array_key_first($GLOBALS['retract_options']));
    }
}
