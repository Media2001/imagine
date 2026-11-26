<?php

declare(strict_types=1);
namespace Imagine\Site\Tests;

use Imagine\Site\Renouvellement;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunInSeparateProcess;
use PHPUnit\Framework\TestCase;

final class C20RenouvellementI18nTest extends TestCase
{
    #[RunInSeparateProcess]
    #[PreserveGlobalState(false)]
    public function testChaqueCodeTraduitUnLitteralPuisEchappeLeResultat(): void
    {
        require __DIR__ . '/fixtures/c20-native-doubles.php';
        $sub = $GLOBALS['c20_subscription'] = new \WC_Subscription();
        $sub->end = '9999-01-01 00:00:00';
        $messages = [
            'arret_a_terme' => 'L’abonnement s’arrêtera à la date indiquée. La reprise n’est pas disponible dans les profils actuels de cette démonstration ; contactez Imagine.',
            'manuel' => 'Le renouvellement est manuel : aucune reconduction automatique à désactiver.',
            'quatre_fois' => 'Pour ne pas renouveler votre engagement en quatre fois, faites la demande auprès d’Imagine ; les échéances du bloc en cours restent dues.',
            'indisponible' => 'La gestion du renouvellement n’est pas disponible sur cette démonstration ; contactez Imagine.',
        ];
        $source = file_get_contents(dirname(__DIR__) . '/Renouvellement.php');
        foreach ($messages as $code => $literal) {
            $sub->status = $code === 'arret_a_terme' ? 'pending-cancel' : 'active';
            $sub->method = $code === 'manuel' ? 'bacs' : '';
            $sub->period = $code === 'quatre_fois' ? 'month' : 'year';
            $sub->interval = $code === 'quatre_fois' ? 3 : 1;
            $sub->manual = $code !== 'indisponible';
            $GLOBALS['c20_translations'] = [];
            ob_start();
            try {
                Renouvellement::afficher(['id' => 30, 'restants' => null]);
                $html = ob_get_contents();
            } finally {
                ob_end_clean();
            }
            self::assertContains([$literal, 'imagine-site'], $GLOBALS['c20_translations']);
            self::assertStringContainsString("__('" . $literal . "', 'imagine-site')", $source, 'Standard extraction requires a literal in the adapter.');
            self::assertStringContainsString(esc_html('<em>' . $literal . '</em>'), $html);
            self::assertStringNotContainsString('<em>', $html);
            self::assertStringNotContainsString('<button', $html);
        }
        self::assertStringNotContainsString("__(\$view['message']", $source);
    }
}
