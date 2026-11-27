<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\MediasRegles;
use PHPUnit\Framework\TestCase;

final class MediasB11Test extends TestCase
{
    public function testVideoUsesExactClosedHost(): void
    {
        $this->assertSame('https://video-fictive.example.invalid/essai?a=1&b=2', MediasRegles::video('https://video-fictive.example.invalid/essai?a=1&b=2', ['video-fictive.example.invalid']));
        foreach (['https://evil.invalid/a', 'https://sub.video-fictive.example.invalid/a', 'http://video-fictive.example.invalid/a', 'https://video-fictive.example.invalid@evil.invalid/a', 'https://video-fictive.example.invalid:443/a', 'https://video-fictive.example.invalid/\\a', "https://video-fictive.example.invalid/\na", 'javascript:alert(1)'] as $url) {
            $this->assertNull(MediasRegles::video($url, ['video-fictive.example.invalid']), $url);
        }
        $this->assertNull(MediasRegles::video('https://video-fictive.example.invalid/a', []));
    }

    public function testPodcastRemainsAnExplicitHttpsLink(): void
    {
        $this->assertSame('https://podcast-fictif.example.invalid/a?x=1&y=2', MediasRegles::lien('https://podcast-fictif.example.invalid/a?x=1&y=2'));
        foreach (['', 'data:text/html,test', '//podcast-fictif.example.invalid/a', 'http://podcast-fictif.example.invalid/a', "https://podcast-fictif.example.invalid/\nb", 'https://user:pass@podcast-fictif.example.invalid/a', 'https://podcast-fictif.example.invalid:8443/a'] as $url) {
            $this->assertNull(MediasRegles::lien($url));
        }
    }

    public function testNonScalarAndOversizedInputsAreRefused(): void
    {
        foreach ([null, false, 123, [], ['url' => 'https://video-fictive.example.invalid/a'], 'https://video-fictive.example.invalid/' . str_repeat('a', 2000)] as $url) {
            $this->assertNull(MediasRegles::video($url, ['video-fictive.example.invalid']));
            $this->assertNull(MediasRegles::lien($url));
        }
    }

    public function testHostnameIsCaseInsensitiveButNeverASuffixMatch(): void
    {
        $url = 'https://VIDEO-FICTIVE.EXAMPLE.INVALID/a';
        $this->assertSame($url, MediasRegles::video($url, ['video-fictive.example.invalid']));
        foreach (['video-fictive.example.invalid.evil.invalid', 'evil-video-fictive.example.invalid', 'video-fictive.example.invalid.'] as $host) {
            $this->assertNull(MediasRegles::video('https://' . $host . '/a', ['video-fictive.example.invalid']));
        }
    }
}
