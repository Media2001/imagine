<?php

declare(strict_types=1);
namespace Imagine\Site\Tests;

use Imagine\Site\Paywall;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunInSeparateProcess;
use PHPUnit\Framework\TestCase;

final class C20PaywallAdapterTest extends TestCase
{
    public static function bornes(): array
    {
        return [
            'sans_fin_native_ferme' => ['', '2027-01-01 00:00:00', '2026-12-25 18:01:49', false, 'virement_non_valide'],
            'juste_avant_fin_ouvert' => ['2026-12-25 18:01:50', '2027-01-01 00:00:00', '2026-12-25 18:01:49', true, 'abonnement_actif'],
            'fin_exacte_ferme' => ['2026-12-25 18:01:50', '2027-01-01 00:00:00', '2026-12-25 18:01:50', false, 'expire'],
            'apres_fin_ferme' => ['2026-12-25 18:01:50', '2027-01-01 00:00:00', '2026-12-25 18:01:51', false, 'expire'],
            'membership_plus_court_avant_ouvert' => ['2026-12-25 18:01:50', '2026-12-01 00:00:00', '2026-11-30 23:59:59', true, 'abonnement_actif'],
            'membership_plus_court_exact_ferme' => ['2026-12-25 18:01:50', '2026-12-01 00:00:00', '2026-12-01 00:00:00', false, 'expire'],
            'membership_plus_court_apres_ferme' => ['2026-12-25 18:01:50', '2026-12-01 00:00:00', '2026-12-01 00:00:01', false, 'expire'],
        ];
    }

    #[DataProvider('bornes')]
    #[RunInSeparateProcess]
    #[PreserveGlobalState(false)]
    public function testDecisionPaywallSurBornesNatives(string $subEnd, string $memberEnd, string $instant, bool $open, string $motif): void
    {
        require __DIR__ . '/fixtures/c20-native-doubles.php';
        require_once dirname(__DIR__) . '/tests-c13/bootstrap.php';
        $GLOBALS['c20_subscription'] = new \WC_Subscription();
        $GLOBALS['c20_subscription']->end = $subEnd;
        $GLOBALS['c20_membership'] = new \C20MembershipDouble();
        $GLOBALS['c20_membership']->end = $memberEnd;
        // Set the existing per-request clock, without introducing a production hook.
        $clock = new \ReflectionProperty(Paywall::class, 'requestInstant');
        $clock->setValue(null, new \DateTimeImmutable($instant, new \DateTimeZone('UTC')));
        $decision = Paywall::decisionPdf(new \WP_Post());
        self::assertNotSame('adaptateur_indisponible', $decision['motif'], 'The real adapter must run, not fail closed on a missing stub.');
        self::assertSame($open, $decision['complet']);
        self::assertSame($motif, $decision['motif']);
    }
}
