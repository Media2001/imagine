<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\PageArticle;
use PHPUnit\Framework\TestCase;

final class PageArticleB16Test extends TestCase
{
    public function testAppelSuitSeulementLeMotifC08(): void
    {
        foreach (['numero_achete', 'decouverte_duree', 'decouverte_articles'] as $motif) {
            self::assertTrue(PageArticle::appel(['complet' => true, 'motif' => $motif]));
            self::assertFalse(PageArticle::appel(['complet' => false, 'motif' => $motif]));
        }
        foreach (['abonnement_actif', 'offert_actif', 'groupe_actif', 'delai_grace', 'equipe', 'contenu_ouvert', 'robot_verifie', 'inconnu'] as $motif) {
            self::assertFalse(PageArticle::appel(['complet' => true, 'motif' => $motif]));
        }
        self::assertFalse(PageArticle::appel(['complet' => 1, 'motif' => 'numero_achete']));
        self::assertFalse(PageArticle::appel([]));
    }

    public static function profils(): array
    {
        return [
            ['complimentary', 'active', 'offert', '2026-12-25 18:01:49', true, 'offert_actif'],
            ['pending', 'pending-cancel', 'abonnement', '2026-12-25 18:01:49', true, 'abonnement_actif'],
            ['pending', 'pending-cancel', 'abonnement', '2026-12-25 18:01:50', false, 'expire'],
            ['pending', 'pending-cancel', 'abonnement', '2026-12-25 18:01:51', false, 'expire'],
        ];
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('profils')]
    #[\PHPUnit\Framework\Attributes\RunInSeparateProcess]
    #[\PHPUnit\Framework\Attributes\PreserveGlobalState(false)]
    public function testVraiPaywallSurProfilsDivergents(string $memberStatus, string $subStatus, string $plan, string $instant, bool $open, string $motif): void
    {
        $source = file_get_contents(__DIR__ . '/fixtures/c20-native-doubles.php');
        $source = str_replace("return 'pending';", 'return ' . var_export($memberStatus, true) . ';', $source);
        $source = str_replace("10 => 'abonnement'", '10 => ' . var_export($plan, true), $source);
        eval(substr($source, strpos($source, 'class WP_Post')));
        require_once dirname(__DIR__) . '/tests-c13/bootstrap.php';
        $GLOBALS['c20_subscription'] = new \WC_Subscription();
        $GLOBALS['c20_subscription']->status = $subStatus;
        $GLOBALS['c20_membership'] = new \C20MembershipDouble();
        $clock = new \ReflectionProperty(\Imagine\Site\Paywall::class, 'requestInstant');
        $clock->setValue(null, new \DateTimeImmutable($instant, new \DateTimeZone('UTC')));
        $decision = \Imagine\Site\Paywall::decisionPdf(new \WP_Post());
        self::assertSame($open, $decision['complet']);
        self::assertSame($motif, $decision['motif']);
        self::assertFalse(PageArticle::appel($decision));
    }
}
