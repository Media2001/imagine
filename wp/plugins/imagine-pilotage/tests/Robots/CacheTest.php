<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Robots;

use DateTimeImmutable;
use Imagine\Pilotage\Robots\CacheMemoire;
use Imagine\Pilotage\Robots\Configuration;
use Imagine\Pilotage\Robots\Methode;
use Imagine\Pilotage\Robots\Robot;
use Imagine\Pilotage\Robots\Verificateur;
use PHPUnit\Framework\TestCase;

final class CacheTest extends TestCase
{
    private function date(string $modification = '+0 seconds'): DateTimeImmutable
    {
        return (new DateTimeImmutable('2026-11-20T12:00:00+01:00'))->modify($modification);
    }

    private function configuration(): Configuration
    {
        return new Configuration([
            new Robot('google', ['Googlebot'], Methode::Dns, ['googlebot.com']),
            new Robot('bing', ['bingbot'], Methode::Dns, ['search.msn.com']),
        ]);
    }

    public function testPositifExpireExactementEtNeProlongePasSaVie(): void
    {
        $dns = new DnsFictif();
        $moteur = new Verificateur($this->configuration(), $dns, new CacheMemoire(), $dns->horloge);
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date())->estVerifie());
        $dns->noms = [];
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+3599 seconds'))->estVerifie());
        self::assertCount(2, $dns->appels);
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+3600 seconds'))->estVerifie());
        self::assertCount(3, $dns->appels);
    }

    public function testNegatifExpirePlusVite(): void
    {
        $dns = new DnsFictif();
        $dns->noms = [];
        $moteur = new Verificateur($this->configuration(), $dns, new CacheMemoire(), $dns->horloge);
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date())->estVerifie());
        $dns->noms = ['crawl-fictif.googlebot.com'];
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+59 seconds'))->estVerifie());
        self::assertCount(1, $dns->appels);
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+60 seconds'))->estVerifie());
        self::assertCount(3, $dns->appels);
    }

    public function testTimeoutNegatifMisEnCache(): void
    {
        $dns = new DnsFictif();
        $dns->latence = 250;
        $moteur = new Verificateur($this->configuration(), $dns, new CacheMemoire(), $dns->horloge);
        self::assertSame('delai_depasse', $moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date())->motif->value);
        $dns->latence = 0;
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+59 seconds'))->estVerifie());
        self::assertCount(1, $dns->appels);
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+60 seconds'))->estVerifie());
    }

    public function testCacheNeTransferePasGoogleVersBingNiNavigateurNiAutreIp(): void
    {
        $dns = new DnsFictif();
        $moteur = new Verificateur($this->configuration(), $dns, new CacheMemoire(), $dns->horloge);
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date())->estVerifie());
        self::assertFalse($moteur->verifier('Mozilla/5.0', '192.0.2.1', $this->date())->estVerifie());
        self::assertCount(2, $dns->appels);
        self::assertFalse($moteur->verifier('bingbot/2.0', '192.0.2.1', $this->date())->estVerifie());
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.2', $this->date())->estVerifie());
        self::assertCount(5, $dns->appels);
    }

    public function testCacheIpv6Canonique(): void
    {
        $dns = new DnsFictif();
        $dns->adresses = ['2001:db8::1'];
        $moteur = new Verificateur($this->configuration(), $dns, new CacheMemoire(), $dns->horloge);
        self::assertTrue($moteur->verifier('Googlebot/2.1', '2001:db8::1', $this->date())->estVerifie());
        self::assertTrue($moteur->verifier('Googlebot/2.1', '2001:0db8:0:0:0:0:0:1', $this->date())->estVerifie());
        self::assertCount(2, $dns->appels);
    }

    public function testChangementConfigurationInvalideCacheEtDureesParametrables(): void
    {
        $dns = new DnsFictif();
        $cache = new CacheMemoire();
        $config = new Configuration($this->configuration()->robots, ttlPositif: 10, ttlNegatif: 2);
        $moteur = new Verificateur($config, $dns, $cache, $dns->horloge);
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date())->estVerifie());
        $dns->noms = [];
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+9 seconds'))->estVerifie());
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+10 seconds'))->estVerifie());
        $dns->noms = ['crawl-fictif.googlebot.com'];
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+11 seconds'))->estVerifie());
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+12 seconds'))->estVerifie());
        $autre = new Configuration([new Robot('google', ['Googlebot'], Methode::Dns, ['example.org'])]);
        $moteur = new Verificateur($autre, $dns, $cache, $dns->horloge);
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('+13 seconds'))->estVerifie());
    }

    public function testReculDateNeReutilisePasUneDecisionFuture(): void
    {
        $dns = new DnsFictif();
        $moteur = new Verificateur($this->configuration(), $dns, new CacheMemoire(), $dns->horloge);
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date())->estVerifie());
        $dns->noms = [];
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date('-1 second'))->estVerifie());
        self::assertCount(3, $dns->appels);
    }
}
