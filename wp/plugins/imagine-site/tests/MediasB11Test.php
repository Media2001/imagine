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
}
