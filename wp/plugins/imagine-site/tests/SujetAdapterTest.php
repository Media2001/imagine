<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Sujet;
use Imagine\Site\SujetConfidentialite;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class SujetAdapterTest extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/SujetWPStubs.php';
    }

    public function testFormulaireLocalConsentementFacultatifEtPasEnumeration(): void
    {
        self::assertTrue(class_exists(Sujet::class), 'Formulaire sujet absent');
        $form = Sujet::formulaire();
        self::assertStringContainsString('name="nom"', $form);
        self::assertStringContainsString('type="email"', $form);
        self::assertStringContainsString('name="sujet"', $form);
        self::assertStringContainsString('type="checkbox"', $form);
        self::assertStringNotContainsString('checked', $form);
        self::assertStringNotContainsString('newsletter', $form);
        $a = Sujet::traiter(['_b08' => 'nonce', 'nom' => 'Nom fictif', 'email' => 'FICTIF@example.org', 'sujet' => '<b>Sujet fictif</b>']);
        $b = Sujet::traiter(['_b08' => 'nonce', 'nom' => 'Inconnu fictif', 'email' => 'inconnu@example.org', 'sujet' => 'Autre sujet', 'consentement' => '1']);
        self::assertSame($a, $b, 'Même message, aucun compte recherché');
        self::assertStringContainsString('enregistrée', $a);
        self::assertCount(2, $GLOBALS['b08_posts'], 'Témoin positif');
        self::assertSame('private', reset($GLOBALS['b08_posts'])->post_status);
        self::assertSame('0', $GLOBALS['b08_meta'][100]['imagine_sujet_consentement']);
        self::assertSame('1', $GLOBALS['b08_meta'][101]['imagine_sujet_consentement']);
        self::assertSame('fictif@example.org', $GLOBALS['b08_meta'][100]['imagine_sujet_email']);
        self::assertSame(['mail' => 0, 'http' => 0], $GLOBALS['b08_calls']);
        foreach ([['_b08' => 'faux'], ['_b08' => 'nonce', 'nom' => []], ['_b08' => 'nonce', 'nom' => 'a', 'email' => 'bad', 'sujet' => 'x']] as $bad) {
            self::assertStringContainsString('refusée', Sujet::traiter($bad));
        }
        self::assertCount(2, $GLOBALS['b08_posts']);
        Sujet::types();
        self::assertFalse($GLOBALS['b08_types'][Sujet::TYPE]['public']);
        self::assertFalse($GLOBALS['b08_types'][Sujet::TYPE]['show_in_rest']);
        self::assertSame('manage_options', $GLOBALS['b08_types'][Sujet::TYPE]['capabilities']['read_post']);
    }

    public function testErreursEcritureJamaisAnnonceesCommeSucces(): void
    {
        self::assertTrue(class_exists(Sujet::class), 'Persistance absente');
        $post = ['_b08' => 'nonce', 'nom' => 'Fictif', 'email' => 'fictif@example.org', 'sujet' => 'Fictif'];
        foreach (['b08_fail_insert', 'b08_fail_meta'] as $fault) {
            $GLOBALS[$fault] = true;
            self::assertStringContainsString('refusée', Sujet::traiter($post));
            self::assertSame([], $GLOBALS['b08_posts']);
            $GLOBALS[$fault] = false;
        }
    }

    public function testPrivacyPaginationAdresseTiersErreursEtEffacement(): void
    {
        self::assertTrue(class_exists(SujetConfidentialite::class), 'Privacy B08 absente');
        for ($i = 0; $i < 101; $i++) {
            self::assertTrue(Sujet::enregistrer('Fictif', 'fictif@example.org', 'Sujet privé ' . $i, false));
        }
        self::assertTrue(Sujet::enregistrer('Tiers', 'tiers@example.org', 'Sujet tiers', true));
        self::assertCount(102, $GLOBALS['b08_posts']);
        $ids = [];
        foreach ([1 => 50, 2 => 50, 3 => 1] as $page => $count) {
            $out = SujetConfidentialite::exporter('FICTIF@example.org', $page);
            self::assertCount($count, $out['data']);
            self::assertSame($page === 3, $out['done']);
            self::assertStringNotContainsString('Sujet tiers', json_encode($out));
            $ids = [...$ids, ...array_column($out['data'], 'item_id')];
        }
        self::assertCount(101, array_unique($ids));
        $GLOBALS['wpdb']->fail = true;
        self::assertInstanceOf(\WP_Error::class, SujetConfidentialite::exporter('fictif@example.org'));
        self::assertFalse(SujetConfidentialite::effacer('fictif@example.org')['done']);
        $GLOBALS['wpdb']->fail = false;
        $GLOBALS['b08_fail_delete'] = true;
        self::assertFalse(SujetConfidentialite::effacer('fictif@example.org')['done']);
        $GLOBALS['b08_fail_delete'] = false;
        foreach ([1, 2, 3] as $page) {
            $result = SujetConfidentialite::effacer('fictif@example.org', $page);
        }
        self::assertTrue($result['done']);
        self::assertSame([], SujetConfidentialite::exporter('fictif@example.org')['data']);
        self::assertCount(1, SujetConfidentialite::exporter('tiers@example.org')['data']);
        self::assertCount(1, $GLOBALS['b08_posts']);
    }
}
