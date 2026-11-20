<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Robots;

use DateTimeImmutable;
use Imagine\Pilotage\Robots\CacheMemoire;
use Imagine\Pilotage\Robots\Configuration;
use Imagine\Pilotage\Robots\Methode;
use Imagine\Pilotage\Robots\Plage;
use Imagine\Pilotage\Robots\Robot;
use Imagine\Pilotage\Robots\Verificateur;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

final class PlagesTest extends TestCase
{
    #[DataProvider('casCidr')]
    public function testCidrBinaire(string $cidr, string $ip, bool $attendu): void
    {
        self::assertTrue(class_exists(Plage::class), 'Le contrôle CIDR C-03 doit exister.');
        self::assertSame($attendu, (new Plage($cidr))->contient($ip));
    }

    public static function casCidr(): array
    {
        return [
            ['192.0.2.128/25', '192.0.2.128', true],
            ['192.0.2.128/25', '192.0.2.255', true],
            ['192.0.2.128/25', '192.0.2.127', false],
            ['192.0.2.128/25', '192.0.3.0', false],
            ['192.0.2.1/32', '192.0.2.1', true],
            ['192.0.2.1/32', '192.0.2.2', false],
            ['0.0.0.0/0', '198.51.100.2', true],
            ['2001:db8::/127', '2001:0db8:0:0:0:0:0:1', true],
            ['2001:db8::/127', '2001:db8::2', false],
            ['2001:db8::1/128', '2001:db8::1', true],
            ['2001:db8::1/128', '2001:db8::', false],
            ['2001:db8::/32', '2001:db9::', false],
            ['::/0', '2001:db8::1', true],
            ['192.0.2.0/24', '::ffff:192.0.2.1', false],
            ['2001:db8::/32', '192.0.2.1', false],
            ['192.0.2.0/24', 'invalide', false],
        ];
    }

    #[DataProvider('cidrInvalides')]
    public function testCidrMalformeRefuse(string $cidr): void
    {
        self::assertTrue(class_exists(Plage::class));
        $this->expectException(\InvalidArgumentException::class);
        new Plage($cidr);
    }

    public static function cidrInvalides(): array
    {
        return array_map(static fn ($cidr) => [$cidr], [
            '192.0.2.1', '192.0.2.0/33', '2001:db8::/129', '192.0.2.0/-1',
            '192.0.2.0/24/1', '192.0.2.0/2e1', '192.0.2.0/024', 'example.org/24',
            'fe80::1%eth0/64', ' 192.0.2.0/24',
        ]);
    }

    #[DataProvider('adressesSimulees')]
    public function testPlagesSansDns(string $ip, bool $attendu): void
    {
        $dns = new DnsFictif();
        $robot = new Robot(
            'fictif',
            ['FictifBot'],
            Methode::Plages,
            plages: ['192.0.2.0/24', '2001:db8::/32'],
            expirationPlages: new DateTimeImmutable('2026-11-21Z'),
        );
        $moteur = new Verificateur(new Configuration([$robot]), $dns, new CacheMemoire(), $dns->horloge);
        $decision = $moteur->verifier('FictifBot/1.0', $ip, new DateTimeImmutable('2026-11-20Z'));
        self::assertSame($attendu, $decision->estVerifie());
        self::assertSame($attendu ? 'verifie_plage' : 'plage_absente', $decision->motif->value);
        self::assertSame($attendu ? 'fictif' : null, $decision->robot);
        self::assertSame([], $dns->appels);
    }

    public static function adressesSimulees(): array
    {
        return [['192.0.2.1', true], ['2001:db8::123', true], ['198.51.100.1', false]];
    }

    public function testPlagesAbsentesEtExpireesRestentFermees(): void
    {
        $dns = new DnsFictif();
        foreach ([null, new DateTimeImmutable('2026-11-20Z')] as $expiration) {
            $robot = new Robot(
                'fictif',
                ['FictifBot'],
                Methode::Plages,
                plages: ['192.0.2.0/24'],
                expirationPlages: $expiration,
            );
            $moteur = new Verificateur(new Configuration([$robot]), $dns, new CacheMemoire(), $dns->horloge);
            $decision = $moteur->verifier('FictifBot/1', '192.0.2.1', new DateTimeImmutable('2026-11-20Z'));
            self::assertFalse($decision->estVerifie());
        }
        self::assertSame([], $dns->appels);
    }

    public function testPositifEnCacheNeDepassePasLaValiditeDesPlages(): void
    {
        $dns = new DnsFictif();
        $maintenant = new DateTimeImmutable('2026-11-20Z');
        $robot = new Robot(
            'fictif',
            ['FictifBot'],
            Methode::Plages,
            plages: ['192.0.2.0/24'],
            expirationPlages: $maintenant->modify('+30 seconds'),
        );
        $moteur = new Verificateur(new Configuration([$robot]), $dns, new CacheMemoire(), $dns->horloge);
        self::assertTrue($moteur->verifier('FictifBot/1', '192.0.2.1', $maintenant)->estVerifie());
        $decision = $moteur->verifier('FictifBot/1', '192.0.2.1', $maintenant->modify('+29 seconds'));
        self::assertTrue($decision->estVerifie());
        self::assertSame('plages_expirees', $moteur->verifier(
            'FictifBot/1',
            '192.0.2.1',
            $maintenant->modify('+30 seconds'),
        )->motif->value);
        self::assertSame([], $dns->appels);
    }
}
