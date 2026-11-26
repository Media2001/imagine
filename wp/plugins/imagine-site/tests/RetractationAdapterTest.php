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

    public function testConfidentialiteExportReprisePaginationEtEffacementSansTiers(): void
    {
        self::assertTrue(class_exists(\Imagine\Site\RetractationConfidentialite::class), 'Confidentialité C25 absente');
        $privacy = \Imagine\Site\RetractationConfidentialite::class;
        self::assertIsArray(Retractation::demander(10, 7, 'confirmer', 'Motif secret fictif'));
        self::assertIsArray(Retractation::demander(11, 8, 'confirmer', 'Motif tiers fictif'));
        $all = $privacy::lignes();
        self::assertCount(2, $all, 'Témoin positif avant les absences');
        $export = $privacy::exporter('fictif@example.org');
        self::assertCount(1, $export['data']);
        self::assertStringContainsString('Motif secret fictif', json_encode($export));
        self::assertStringNotContainsString('Motif tiers fictif', json_encode($export));
        $GLOBALS['wpdb']->fail = true;
        self::assertInstanceOf(\WP_Error::class, $privacy::exporter('fictif@example.org', 1));
        self::assertFalse($privacy::effacer('fictif@example.org')['done']);
        $GLOBALS['wpdb']->fail = false;
        self::assertCount(1, $privacy::exporter('fictif@example.org', 1)['data']);
        for ($i = 100; $i < 221; $i++) {
            $row = ['commande' => $i, 'compte' => 7, 'date' => '2030-01-01T00:00:00Z', 'raison' => 'Pagination fictive', 'note' => $i];
            $GLOBALS['retract_notes'][$i] = ['comment_ID' => $i];
            $GLOBALS['retract_meta'][$i] = $row;
            $GLOBALS['retract_options'][Retractation::JOURNAL . $i] = ['qui_id' => 7, 'qui_login' => 'fictif', 'apres' => ['commande' => $i, 'note' => $i, 'date' => $row['date']]];
        }
        $ids = [];
        for ($page = 1; $page <= 3; $page++) {
            $part = $privacy::exporter('fictif@example.org', $page);
            self::assertSame($page === 3, $part['done']);
            self::assertCount($page === 3 ? 22 : 50, $part['data']);
            $ids = [...$ids, ...array_column($part['data'], 'item_id')];
        }
        self::assertCount(122, array_unique($ids));
        $GLOBALS['retract_fail_delete'] = true;
        self::assertFalse($privacy::effacer('fictif@example.org')['done']);
        $GLOBALS['retract_fail_delete'] = false;
        for ($page = 1; $page <= 3; $page++) {
            $result = $privacy::effacer('fictif@example.org', $page);
        }
        self::assertTrue($result['done']);
        self::assertSame([], $privacy::exporter('fictif@example.org')['data']);
        self::assertCount(1, $privacy::exporter('tiers@example.org')['data']);
        self::assertStringNotContainsString('Motif secret fictif', json_encode($GLOBALS['retract_meta']));
        self::assertSame(0, $GLOBALS['retract_options'][Retractation::JOURNAL . 10]['qui_id']);
        self::assertSame(0, $GLOBALS['retract_options'][Retractation::JOURNAL . 10]['apres']['note']);
        self::assertIsArray(Retractation::demander(10, 7, 'confirmer', 'Rejeu après effacement'));
        self::assertCount(1, $GLOBALS['retract_notes'], 'La trace dépersonnalisée empêche le rejeu');
    }

    public function testReglagesC10EtDateManuelleConservatrice(): void
    {
        self::assertTrue(class_exists(\Imagine\Site\RetractationReglages::class), 'Réglages C25 absents');
        $settings = \Imagine\Site\RetractationReglages::class;
        self::assertSame(['jours' => 14, 'origine' => 'paiement'], Retractation::configuration());
        foreach (['paiement', 'manuelle'] as $origin) {
            self::assertSame(['jours' => 30, 'origine' => $origin], $settings::nettoyer(['jours' => '30', 'origine' => $origin]));
        }
        foreach ([[], ['jours' => '0', 'origine' => 'paiement'], ['jours' => '14', 'origine' => 'inconnue']] as $bad) {
            self::assertSame(Retractation::configuration(), $settings::nettoyer($bad));
        }
        $html = $settings::champs();
        self::assertStringContainsString('name="imagine_retractation_reglages[jours]"', $html);
        self::assertStringContainsString('name="imagine_retractation_reglages[origine]"', $html);
        self::assertNull(Retractation::dateManuelle('2030-02-30'));
        self::assertNull(Retractation::dateManuelle('texte'));
        self::assertSame(strtotime('2030-01-03 UTC'), Retractation::dateManuelle('2030-01-03'));
    }

    public function testRaccordsEntreeAdministrationEtDateManuelle(): void
    {
        Retractation::register();
        \Imagine\Site\RetractationConfidentialite::register();
        \Imagine\Site\RetractationReglages::register();
        foreach (['woocommerce_account_dashboard', 'woocommerce_view_order', 'woocommerce_subscription_details_after_subscription_table', 'admin_menu', 'wp_privacy_personal_data_exporters', 'wp_privacy_personal_data_erasers', 'woocommerce_process_shop_order_meta'] as $hook) {
            self::assertNotEmpty($GLOBALS['retract_hooks'][$hook]);
        }
        ob_start(); Retractation::entree(10); $open = ob_get_clean();
        self::assertStringContainsString('Me rétracter', $open);
        $GLOBALS['retract_now'] = strtotime('2030-02-01 UTC');
        ob_start(); Retractation::entree(10); $closed = ob_get_clean();
        self::assertStringNotContainsString('Me rétracter', $closed);
        $GLOBALS['retract_now'] = strtotime('2030-01-02 UTC');
        self::assertIsArray(Retractation::demander(10, 7, 'confirmer', '<script>x</script>motif fictif'));
        ob_start(); Retractation::administration(); $admin = ob_get_clean();
        self::assertStringContainsString('#10', $admin);
        self::assertStringContainsString('motif fictif', $admin);
        self::assertStringNotContainsString('<script>', $admin);
        $GLOBALS['wpdb']->fail = true;
        ob_start(); Retractation::administration(); $failed = ob_get_clean();
        self::assertStringContainsString('Lecture impossible', $failed);
        $GLOBALS['wpdb']->fail = false;
        $_POST = ['imagine_c25_date' => '2030-02-30', '_imagine_c25_date' => 'nonce'];
        \Imagine\Site\RetractationReglages::sauverDate(10);
        self::assertSame([], $GLOBALS['retract_orders'][10]->meta);
        $_POST['imagine_c25_date'] = '2030-01-03';
        $_POST['_imagine_c25_date'] = 'faux';
        \Imagine\Site\RetractationReglages::sauverDate(10);
        self::assertSame([], $GLOBALS['retract_orders'][10]->meta);
        $_POST['_imagine_c25_date'] = 'nonce';
        \Imagine\Site\RetractationReglages::sauverDate(10);
        self::assertSame('2030-01-03', $GLOBALS['retract_orders'][10]->meta[Retractation::MANUELLE]);
        self::assertSame(0, $GLOBALS['retract_financial']);
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
