<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Robots;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Robots\Cache;
use Imagine\Pilotage\Robots\Configuration;
use Imagine\Pilotage\Robots\EntreeCache;
use Imagine\Pilotage\Robots\Methode;
use Imagine\Pilotage\Robots\Robot;
use Imagine\Pilotage\Robots\Verificateur;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

final class CacheDefensifTest extends TestCase
{
    public function testTupleV2DistinctEtIdentiteDuCandidat(): void
    {
        $config = new Configuration([
            new Robot('robot', ['FictifA'], Methode::Dns, ['example.org']),
            new Robot('robot19', ['FictifB'], Methode::Dns, ['example.org']),
        ]);
        $cache = $this->cache();
        $dns = new DnsFictif();
        $dns->noms = ['robot-fictif.example.org'];
        $moteur = new Verificateur($config, $dns, $cache, $dns->horloge);
        $date = new DateTimeImmutable('2026-11-21T10:00:00Z');
        $positif = $moteur->verifier('FictifA/1', '192.0.2.1', $date);
        self::assertTrue($positif->estVerifie());
        self::assertSame('robot', $positif->robot);
        $refus = $moteur->verifier('FictifB/1', '2.0.2.1', $date);
        self::assertFalse($refus->estVerifie());
        self::assertNull($refus->robot);
        self::assertSame('adresse_differente', $refus->motif->value);
        self::assertCount(4, $dns->appels);
        self::assertCount(2, $cache->entrees);
        foreach ([['robot', '192.0.2.1'], ['robot19', '2.0.2.1']] as [$robot, $ip]) {
            $cle = hash('sha256', serialize(['c03-v2', $config, $robot, $ip]));
            self::assertArrayHasKey($cle, $cache->entrees);
        }
        self::assertSame('robot', $moteur->verifier('FictifA/1', '192.0.2.1', $date)->robot);
        self::assertCount(4, $dns->appels);
    }

    #[DataProvider('transitions')]
    public function testExpirationAbsolueAuxTransitions(string $utc): void
    {
        $debut = (new DateTimeImmutable($utc))->setTimezone(new DateTimeZone('Europe/Brussels'));
        $cache = $this->cache();
        $dns = new DnsFictif();
        $config = new Configuration([new Robot('google', ['Googlebot'], Methode::Dns, ['googlebot.com'])]);
        $moteur = new Verificateur($config, $dns, $cache, $dns->horloge);
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $debut)->estVerifie());
        $entree = array_values($cache->entrees)[0];
        self::assertSame(3600, $entree->expiration->getTimestamp() - $entree->creation->getTimestamp());
        $dns->noms = [];
        $avant = $debut->setTimestamp($debut->getTimestamp() + 3599);
        $expiration = $debut->setTimestamp($debut->getTimestamp() + 3600);
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $avant)->estVerifie());
        self::assertCount(2, $dns->appels);
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.1', $expiration)->estVerifie());
        self::assertCount(3, $dns->appels);
        $entree = array_values($cache->entrees)[0];
        self::assertSame(60, $entree->expiration->getTimestamp() - $entree->creation->getTimestamp());
        $dns->noms = ['crawl-fictif.googlebot.com'];
        $avant = $debut->setTimestamp($debut->getTimestamp() + 3659);
        $expiration = $debut->setTimestamp($debut->getTimestamp() + 3660);
        self::assertFalse($moteur->verifier('Googlebot/2.1', '192.0.2.1', $avant)->estVerifie());
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $expiration)->estVerifie());
        self::assertCount(5, $dns->appels);
    }

    public static function transitions(): array
    {
        return [['2026-03-29T00:30:00Z'], ['2026-10-25T00:30:00Z']];
    }

    private function cache(): Cache
    {
        return new class implements Cache {
            public array $entrees = [];

            public function lire(string $cle): ?EntreeCache
            {
                return $this->entrees[$cle] ?? null;
            }

            public function ecrire(string $cle, EntreeCache $entree): void
            {
                $this->entrees[$cle] = $entree;
            }
        };
    }
}
