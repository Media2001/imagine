<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\IntegrationsCorps;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class IntegrationsCorpsB12Test extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/IntegrationsCorpsB12Stubs.php';
    }

    public function testOnlySameSiteOriginAndPathAreDelegated(): void
    {
        foreach (['https://demo.example.invalid/magazine/article/', 'https://DEMO.example.invalid:443/magazine/wp/a', '//demo.example.invalid/magazine/a'] as $url) {
            self::assertFalse(IntegrationsCorps::externe($url), $url);
            self::assertFalse(IntegrationsCorps::lien([], [], $url));
        }
        foreach (['https://demo.example.invalid.evil.invalid/magazine/a', 'https://demo.example.invalid:444/magazine/a', 'http://demo.example.invalid/magazine/a', 'https://demo.example.invalid/magazine-other/a', 'https://demo.example.invalid/other/a', 'https://demo.example.invalid@evil.invalid/magazine/a', 'https://user@demo.example.invalid/magazine/a', 'https://vimeo.com/123', 'javascript:alert(1)'] as $url) {
            self::assertTrue(IntegrationsCorps::externe($url), $url);
        }
    }

    public function testResolutionAndHandlerReturnOnlyEscapedOrdinaryLink(): void
    {
        $url = 'https://tiers.example.invalid/video?a=1&b="<test>';
        $html = IntegrationsCorps::lien([], [], $url);
        self::assertSame($html, IntegrationsCorps::resolution('<iframe>cached</iframe>', $url));
        self::assertStringContainsString('<a href=', $html);
        self::assertStringContainsString('&amp;', $html);
        self::assertDoesNotMatchRegularExpression('/<(iframe|script|img|test)\b/i', $html);
        self::assertSame('native', IntegrationsCorps::resolution('native', home_url('/a')));
    }

    public function testNativeExternalBlockShortCircuitsBeforeStoredHtml(): void
    {
        $block = ['blockName' => 'core/embed', 'attrs' => ['url' => 'https://tiers.example.invalid/a']];
        $html = IntegrationsCorps::bloc('<iframe>stale</iframe>', $block);
        self::assertStringContainsString('<a href=', $html);
        self::assertStringNotContainsString('<iframe', $html);
        $block['attrs']['url'] = home_url('/a');
        self::assertSame('native', IntegrationsCorps::bloc('native', $block));
        self::assertNull(IntegrationsCorps::bloc(null, ['blockName' => 'core/paragraph']));
    }

    public function testProxyLocksBeforeCacheWithoutBypassingPermissionsOrOtherRoutes(): void
    {
        $request = new \WP_REST_Request('/oembed/1.0/proxy', 'https://tiers.example.invalid/a');
        $result = IntegrationsCorps::apercu(null, $request, '/oembed/1.0/proxy');
        self::assertSame(200, $result->status);
        self::assertSame(['version', 'type', 'html'], array_keys($result->data));
        self::assertSame('link', $result->data['type']);
        self::assertSame('native', IntegrationsCorps::apercu('native', new \WP_REST_Request('/oembed/1.0/proxy', home_url('/a')), ''));
        self::assertSame('native', IntegrationsCorps::apercu('native', new \WP_REST_Request('/oembed/1.0/embed', 'https://tiers.example.invalid/a'), ''));
        $error = new \WP_Error();
        self::assertSame($error, IntegrationsCorps::apercu($error, $request, ''));
        $GLOBALS['b12_editor'] = false;
        self::assertNull(IntegrationsCorps::apercu(null, $request, ''));
    }

    public function testNativeHookRegistrationPrecedesCaches(): void
    {
        IntegrationsCorps::register();
        self::assertSame('imagine_corps_externe', $GLOBALS['b12_handler'][0]);
        self::assertSame(PHP_INT_MIN, $GLOBALS['b12_handler'][3]);
        self::assertSame(['pre_oembed_result', 'pre_render_block', 'rest_dispatch_request'], array_keys($GLOBALS['b12_hooks']));
        foreach ($GLOBALS['b12_hooks'] as $definition) {
            self::assertSame(PHP_INT_MAX, $definition[1]);
        }
    }
}
