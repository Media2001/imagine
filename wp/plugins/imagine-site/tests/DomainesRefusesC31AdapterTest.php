<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\DomainesRefuses;
use Imagine\Site\DomainesRefusesReglages;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class DomainesRefusesC31AdapterTest extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/DomainesRefusesWPStubs.php';
        $GLOBALS['c31_options'][DomainesRefuses::OPTION] = ['jetable-fictif.example.org'];
    }

    public function testRaccordArgumentsEtAbsenceDeFiltreGlobal(): void
    {
        DomainesRefuses::register();
        foreach (['registration_errors', 'woocommerce_registration_errors'] as $hook) {
            self::assertSame([[ [DomainesRefuses::class, 'inscription'], 30, 3 ]], $GLOBALS['c31_hooks'][$hook]);
            [$callback, , $args] = $GLOBALS['c31_hooks'][$hook][0];
            self::assertSame(3, $args);
            $error = $callback(new \WP_Error(), 'mot-de-passe@jetable-fictif.example.org', 'autorise@example.org');
            self::assertFalse($error->has_errors(), 'Le troisième argument est email, jamais le deuxième');
            self::assertTrue($callback(new \WP_Error(), 'login-libre', 'refuse@JETABLE-FICTIF.example.org')->has_errors());
        }
        self::assertSame([[[DomainesRefuses::class, 'compte'], 30, 2]], $GLOBALS['c31_hooks']['woocommerce_save_account_details_errors']);
        self::assertArrayNotHasKey('wp_insert_user', $GLOBALS['c31_hooks']);
        self::assertArrayNotHasKey('user_register', $GLOBALS['c31_hooks']);
    }

    public function testInscriptionGardeAdminMaisPasAjaxPublic(): void
    {
        foreach ([[false, false, false, true], [true, true, false, false], [true, true, true, true], [true, false, false, true]] as [$admin, $cap, $ajax, $refused]) {
            $GLOBALS['c31_admin'] = $admin;
            $GLOBALS['c31_cap'] = $cap;
            $GLOBALS['c31_ajax'] = $ajax;
            $error = new \WP_Error();
            self::assertSame($error, DomainesRefuses::inscription($error, 'fictif', 'refuse@jetable-fictif.example.org'));
            self::assertSame($refused, $error->has_errors());
        }
        $GLOBALS['c31_admin'] = false;
        self::assertFalse(DomainesRefuses::inscription(new \WP_Error(), 'fictif', 'libre@example.org')->has_errors());
        $GLOBALS['c31_options'][DomainesRefuses::OPTION] = [];
        self::assertFalse(DomainesRefuses::inscription(new \WP_Error(), 'fictif', 'refuse@jetable-fictif.example.org')->has_errors());
    }

    public function testCompteInchangeAccepteEtChangementRefuseSansEcriture(): void
    {
        $unchanged = new \WP_Error();
        DomainesRefuses::compte($unchanged, (object) ['ID' => 17, 'user_email' => 'EXISTANT@JETABLE-FICTIF.example.org']);
        self::assertFalse($unchanged->has_errors());
        $changed = new \WP_Error();
        DomainesRefuses::compte($changed, (object) ['ID' => 17, 'user_email' => 'autre@jetable-fictif.example.org']);
        self::assertSame(['imagine_adresse_alternative'], $changed->get_error_codes());
        $allowed = new \WP_Error();
        DomainesRefuses::compte($allowed, (object) ['ID' => 17, 'user_email' => 'autre@example.org']);
        self::assertFalse($allowed->has_errors());
        self::assertSame('existant@jetable-fictif.example.org', $GLOBALS['c31_users'][17]->user_email);
    }

    public function testCommandeRefuseAvantLaSauvegardeNativeDeSession(): void
    {
        DomainesRefuses::register();
        self::assertArrayHasKey('woocommerce_checkout_posted_data', $GLOBALS['c31_hooks']);
        [$callback, $priority, $args] = $GLOBALS['c31_hooks']['woocommerce_checkout_posted_data'][0];
        self::assertSame(1, $priority);
        self::assertSame(1, $args);
        $posted = ['createaccount' => 1, 'billing_email' => 'refuse@jetable-fictif.example.org'];
        try {
            $callback($posted);
            self::fail('Une adresse refusée atteindrait update_session');
        } catch (\Exception $error) {
            self::assertStringContainsString('autre adresse email', $error->getMessage());
        }
        self::assertSame(['createaccount' => 1, 'billing_email' => 'refuse@jetable-fictif.example.org'], $posted);
    }

    public function testCommandeRespecteInviteCompteExistantListeVideEtInscriptionObligatoire(): void
    {
        $posted = ['createaccount' => 0, 'billing_email' => 'refuse@jetable-fictif.example.org'];
        self::assertSame($posted, DomainesRefuses::commande($posted));
        $GLOBALS['c31_logged'] = true;
        $posted['createaccount'] = 1;
        self::assertSame($posted, DomainesRefuses::commande($posted));
        $GLOBALS['c31_logged'] = false;
        $GLOBALS['c31_options'][DomainesRefuses::OPTION] = [];
        self::assertSame($posted, DomainesRefuses::commande($posted));
        $GLOBALS['c31_options'][DomainesRefuses::OPTION] = ['jetable-fictif.example.org'];
        $posted['billing_email'] = 'libre@example.org';
        self::assertSame($posted, DomainesRefuses::commande($posted));
        $GLOBALS['c31_required'] = true;
        $posted = ['createaccount' => 0, 'billing_email' => 'refuse@jetable-fictif.example.org'];
        $this->expectException(\Exception::class);
        $this->expectExceptionMessage('autre adresse email');
        DomainesRefuses::commande($posted);
    }

    public function testStoreApiRefuseAvantSessionEtCommandeMaisIgnoreLesAutresRoutes(): void
    {
        DomainesRefuses::register();
        self::assertArrayHasKey('rest_request_before_callbacks', $GLOBALS['c31_hooks']);
        [$callback, $priority, $args] = $GLOBALS['c31_hooks']['rest_request_before_callbacks'][0];
        self::assertSame(1, $priority);
        self::assertSame(3, $args);
        $request = new \WP_REST_Request('POST', '/wc/store/v1/checkout');
        $request->params = ['create_account' => true, 'billing_address' => ['email' => 'refuse@jetable-fictif.example.org']];
        self::assertInstanceOf(\WP_Error::class, $callback(null, [], $request));
        $existing = new \WP_Error();
        self::assertSame($existing, $callback($existing, [], $request));
        $request->route = '/wc/store/v1/cart';
        self::assertNull($callback(null, [], $request));
        $request->route = '/WC/STORE/v1/CHECKOUT/';
        self::assertInstanceOf(\WP_Error::class, $callback(null, [], $request));
        $request->params['create_account'] = false;
        self::assertNull($callback(null, [], $request));
        $request->params['create_account'] = true;
        $GLOBALS['c31_logged'] = true;
        self::assertNull($callback(null, [], $request));
        $GLOBALS['c31_logged'] = false;
        $GLOBALS['c31_options'][DomainesRefuses::OPTION] = [];
        self::assertNull($callback(null, [], $request));
        $GLOBALS['c31_options'][DomainesRefuses::OPTION] = ['jetable-fictif.example.org'];
        $request->params['billing_address']['email'] = 'libre@example.org';
        self::assertNull($callback(null, [], $request));
    }

    public function testReglageAtomiqueJournalEtRestaurationHorsLigne(): void
    {
        DomainesRefusesReglages::register();
        self::assertSame(['jetable-fictif.example.org'], DomainesRefusesReglages::nettoyer("INVALIDE\\.example.org"));
        self::assertCount(1, $GLOBALS['c31_settings_errors']);
        update_option(DomainesRefuses::OPTION, ['autre-fictif.example.org']);
        $events = array_filter($GLOBALS['c31_options'], static fn ($key) => str_starts_with($key, 'imagine_reglages_journal_'), ARRAY_FILTER_USE_KEY);
        self::assertCount(1, $events);
        self::assertSame(['jetable-fictif.example.org'], reset($events)['avant']);
        self::assertSame(['autre-fictif.example.org'], reset($events)['apres']);
        $GLOBALS['c31_fail_journal'] = true;
        update_option(DomainesRefuses::OPTION, ['perdu-fictif.example.org']);
        self::assertSame(['autre-fictif.example.org'], DomainesRefuses::configuration());
        self::assertCount(2, $GLOBALS['c31_settings_errors']);
    }
}
