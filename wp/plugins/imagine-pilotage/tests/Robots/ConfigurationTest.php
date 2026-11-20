<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Robots;

use DateTimeImmutable;
use Imagine\Pilotage\Robots\CacheMemoire;
use Imagine\Pilotage\Robots\Configuration;
use Imagine\Pilotage\Robots\Decision;
use Imagine\Pilotage\Robots\Methode;
use Imagine\Pilotage\Robots\Motif;
use Imagine\Pilotage\Robots\Robot;
use Imagine\Pilotage\Robots\Verificateur;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

final class ConfigurationTest extends TestCase
{
    #[DataProvider('reglagesInvalides')]
    public function testReglagesInvalidesRefuses(int $delai, int $positif, int $negatif): void
    {
        $this->expectException(\InvalidArgumentException::class);
        new Configuration([], $delai, $positif, $negatif);
    }

    public static function reglagesInvalides(): array
    {
        return [[0, 3600, 60], [-1, 3600, 60], [200, 0, 60], [200, 10, 0], [200, 10, 10], [200, 10, 11]];
    }

    #[DataProvider('robotsInvalides')]
    public function testRobotMalConfigureRefuse(string $id, array $agents, array $domaines, array $plages): void
    {
        $this->expectException(\InvalidArgumentException::class);
        new Robot($id, $agents, Methode::Dns, $domaines, $plages);
    }

    public static function robotsInvalides(): array
    {
        return [
            ['', ['Bot'], ['example.org'], []],
            ['id', [], ['example.org'], []],
            ['id', ['Bot/1'], ['example.org'], []],
            ['id', ['Bot', 'bot'], ['example.org'], []],
            ['id', ['Bot'], [], []],
            ['id', ['Bot'], ['*.example.org'], []],
            ['id', ['Bot'], ['com'], []],
            ['id', ['Bot'], ['example.org.'], []],
            ['id', ['Bot'], ['example.org'], ['192.0.2.0/33']],
        ];
    }

    public function testIdentifiantsDupliquesRefuses(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        new Configuration([
            new Robot('id', ['BotA'], Methode::Dns, ['example.org']),
            new Robot('id', ['BotB'], Methode::Dns, ['example.net']),
        ]);
    }

    public function testJetonsPartagesRefuses(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        new Configuration([
            new Robot('a', ['Bot'], Methode::Dns, ['example.org']),
            new Robot('b', ['bot'], Methode::Dns, ['example.net']),
        ]);
    }

    public function testDecisionIncoherenteRefusee(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        new Decision(Motif::VerifieDns);
    }

    public function testRefusNePortePasIdentiteVerifiee(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        new Decision(Motif::AgentInconnu, 'google');
    }

    public function testDatesNormaliseesBruxelles(): void
    {
        $date = new DateTimeImmutable('2026-11-20T12:00:00Z');
        $entree = new \Imagine\Pilotage\Robots\EntreeCache(
            new Decision(Motif::AgentInconnu),
            $date,
            $date->modify('+60 seconds'),
        );
        self::assertSame('Europe/Brussels', $entree->creation->getTimezone()->getName());
        self::assertSame('Europe/Brussels', $entree->expiration->getTimezone()->getName());
        self::assertSame($date->getTimestamp(), $entree->creation->getTimestamp());
        $robot = new Robot('fictif', ['FictifBot'], Methode::Plages, expirationPlages: $date);
        self::assertSame('Europe/Brussels', $robot->expirationPlages->getTimezone()->getName());
        self::assertSame($date->getTimestamp(), $robot->expirationPlages->getTimestamp());
    }

    public function testConfigurationInitialeGoogleBingSeulementEtAucunDnsAuChargement(): void
    {
        $chemin = dirname(__DIR__, 2) . '/config/robots.php';
        self::assertFileExists($chemin, 'Configuration initiale Google/Bing requise.');
        $configuration = require $chemin;
        self::assertInstanceOf(Configuration::class, $configuration);
        self::assertSame(['google', 'bing'], array_column($configuration->robots, 'identifiant'));
        $dns = new DnsFictif();
        $moteur = new Verificateur($configuration, $dns, new CacheMemoire(), $dns->horloge);
        $date = new DateTimeImmutable('2026-11-20Z');
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $date)->estVerifie());
        $dns->noms = ['msnbot-fictif.search.msn.com.'];
        self::assertSame('bing', $moteur->verifier('bingbot/2.0', '192.0.2.1', $date)->robot);
        self::assertFalse($moteur->verifier('Applebot/1.0', '192.0.2.1', $date)->estVerifie());
        self::assertCount(4, $dns->appels);
    }
}
