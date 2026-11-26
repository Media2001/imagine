<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\ConfidentialiteRegles;
use PHPUnit\Framework\TestCase;

final class ConfidentialiteReglesTest extends TestCase
{
    public function testEffacementNeModifiePasUneObservationEtrangereDuGel(): void
    {
        $foreign = ['donnees' => ['id' => '70', 'user' => '2', 'beneficiaires_resolus' => true]];
        self::assertSame($foreign, ConfidentialiteRegles::retirerPostal($foreign, 3));
        self::assertNull(ConfidentialiteRegles::retirerPostal($foreign, 2));
        $shared = ['donnees' => ['user' => '2', 'beneficiaires' => [['id' => '3'], ['id' => '4']],
            'relation_native' => [['user_id' => 3], ['user_id' => 4]], 'beneficiaires_resolus' => true]];
        $out = ConfidentialiteRegles::retirerPostal($shared, 3);
        self::assertSame([['id' => '4']], $out['donnees']['beneficiaires']);
        self::assertSame([['user_id' => 4]], $out['donnees']['relation_native']);
        self::assertTrue($out['donnees']['beneficiaires_resolus']);
        self::assertNull(ConfidentialiteRegles::postal($out, 3));
        $owner = ConfidentialiteRegles::retirerPostal($shared, 2);
        self::assertSame('0', $owner['donnees']['user']);
        self::assertSame($shared['donnees']['beneficiaires'], $owner['donnees']['beneficiaires']);
        self::assertSame($shared['donnees']['relation_native'], $owner['donnees']['relation_native']);
        self::assertTrue($owner['donnees']['beneficiaires_resolus']);
    }

    public function testRelationInactiveEstExporteeEtRetireeSansAdresseDUnTiers(): void
    {
        $event = ['donnees' => ['id' => '70', 'user' => '2', 'destinataire' => 'AUTRE',
            'beneficiaires' => [], 'relation_native' => [['user_id' => 3, 'membership_id' => 80, 'etat' => 'paused'],
                ['user_id' => 4, 'membership_id' => 81, 'etat' => 'active']]]];
        $out = ConfidentialiteRegles::postal($event, 3);
        self::assertNotNull($out);
        self::assertStringContainsString('paused', json_encode($out));
        self::assertStringNotContainsString('AUTRE', json_encode($out));
        self::assertSame(
            [['user_id' => 4, 'membership_id' => 81, 'etat' => 'active']],
            ConfidentialiteRegles::retirerPostal($event, 3)['donnees']['relation_native']
        );
    }

    public function testCadeauEffaceAussiAdresseDuBeneficiaire(): void
    {
        $event = ['donnees' => ['user' => '2', 'origine' => 'offert', 'destinataire' => 'CIBLE',
            'rue' => 'RUE CIBLE', 'beneficiaires' => [['id' => '3', 'nom' => 'CIBLE']],
            'relation_native' => ['recipient_user' => 3]]];
        $out = ConfidentialiteRegles::retirerPostal($event, 3);
        self::assertStringNotContainsString('CIBLE', json_encode($out));
        self::assertSame('2', $out['donnees']['user']);
    }

    public function testEffacementOffrantPreserveAttributionEtAdresseExactesDuBeneficiaire(): void
    {
        $event = ['donnees' => ['id' => '70', 'user' => '2', 'origine' => 'offert',
            'destinataire' => 'CIBLE', 'rue' => 'RUE CIBLE', 'beneficiaires_resolus' => true,
            'beneficiaires' => [['id' => '3', 'nom' => 'CIBLE', 'rue' => 'RUE CIBLE']],
            'relation_native' => ['recipient_user' => 3]]];
        $before = ConfidentialiteRegles::postal($event, 3);
        $out = ConfidentialiteRegles::retirerPostal($event, 2);
        self::assertSame('0', $out['donnees']['user']);
        self::assertSame($before, ConfidentialiteRegles::postal($out, 3));
        self::assertSame($event['donnees']['relation_native'], $out['donnees']['relation_native']);
        self::assertSame('RUE CIBLE', $out['donnees']['rue']);
        self::assertNull(ConfidentialiteRegles::postal($out, 2));
    }

    public function testRetraitNeResoutJamaisUnGroupeInconnu(): void
    {
        $event = ['donnees' => ['user' => '2', 'origine' => 'groupe', 'beneficiaires_resolus' => false,
            'beneficiaires' => [['id' => '3'], ['id' => '4']], 'relation_native' => [['user_id' => 3], ['user_id' => 4]]]];
        $out = ConfidentialiteRegles::retirerPostal($event, 3);
        self::assertFalse($out['donnees']['beneficiaires_resolus']);
        self::assertSame([['id' => '4']], $out['donnees']['beneficiaires']);
    }

    public function testTraductionsConfidentialiteOntToutesUnPremierArgumentLitteral(): void
    {
        $source = file_get_contents(dirname(__DIR__) . '/Confidentialite.php');
        $tokens = array_values(array_filter(token_get_all($source), static fn ($t): bool =>
            !is_array($t) || !in_array($t[0], [T_WHITESPACE, T_COMMENT, T_DOC_COMMENT], true)));
        $count = 0;
        foreach ($tokens as $i => $t) {
            if (is_array($t) && $t[0] === T_STRING && in_array($t[1], ['__', 'esc_html__'], true)) {
                self::assertSame('(', $tokens[$i + 1]);
                self::assertSame(T_CONSTANT_ENCAPSED_STRING, $tokens[$i + 2][0]);
                $count++;
            }
        }
        self::assertGreaterThan(15, $count);
        self::assertStringContainsString('SansEmail::META', $source);
        self::assertStringContainsString('Newsletters::META', $source);
    }

    public function testExportPostalNeDivulguePasLesAutresBeneficiaires(): void
    {
        $event = ['observe_utc' => '2026-11-26', 'donnees' => [
            'id' => '70', 'user' => '2', 'destinataire' => 'Payeur', 'rue' => 'Rue du payeur',
            'beneficiaires' => [['id' => '3', 'nom' => 'Cible'], ['id' => '4', 'nom' => 'Autre']],
            'relation_native' => [['user_id' => 3], ['user_id' => 4]], 'note' => 'INTERNE',
        ]];
        $out = ConfidentialiteRegles::postal($event, 3);
        self::assertStringContainsString('Cible', json_encode($out));
        foreach (['Payeur', 'Autre', 'INTERNE', 'relation_native'] as $forbidden) {
            self::assertStringNotContainsString($forbidden, json_encode($out));
        }
        self::assertNull(ConfidentialiteRegles::postal($event, 9));
    }
}
