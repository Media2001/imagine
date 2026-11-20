<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Robots;

use DateTimeImmutable;
use Imagine\Pilotage\Robots\CacheMemoire;
use Imagine\Pilotage\Robots\Configuration;
use Imagine\Pilotage\Robots\Dns;
use Imagine\Pilotage\Robots\HorlogeMonotone;
use Imagine\Pilotage\Robots\Methode;
use Imagine\Pilotage\Robots\Motif;
use Imagine\Pilotage\Robots\Robot;
use Imagine\Pilotage\Robots\Verificateur;
use PHPUnit\Framework\TestCase;

final class VerificateurTest extends TestCase
{
    public function testDnsInverseEtDirecteConcordent(): void
    {
        $dns = new DnsFictif();
        $decision = $this->moteur($dns)->verifier('Googlebot/2.1', '192.0.2.1', $this->date());
        self::assertTrue($decision->estVerifie());
        self::assertSame('google', $decision->robot);
        self::assertSame(Motif::VerifieDns, $decision->motif);
        self::assertSame(['inverse', 'directe'], array_column($dns->appels, 0));
    }

    public function testAdresseQuelconqueNeSuffitPas(): void
    {
        $dns = new DnsFictif();
        $dns->noms = [];
        $decision = $this->moteur($dns)->verifier('Googlebot/2.1', '192.0.2.9', $this->date());
        self::assertFalse($decision->estVerifie());
        self::assertSame(Motif::DomaineRefuse, $decision->motif);
        self::assertCount(1, $dns->appels);
    }

    public function testInverseFalsifieRefuse(): void
    {
        $dns = new DnsFictif();
        $dns->adresses = ['192.0.2.2'];
        self::assertSame(Motif::AdresseDifferente, $this->moteur($dns)->verifier(
            'Googlebot/2.1',
            '192.0.2.1',
            $this->date(),
        )->motif);
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('domainesInterdits')]
    public function testDomaineTrompeurSansResolutionDirecte(string $nom): void
    {
        $dns = new DnsFictif();
        $dns->noms = [$nom];
        self::assertSame(Motif::DomaineRefuse, $this->moteur($dns)->verifier(
            'Googlebot/2.1',
            '192.0.2.1',
            $this->date(),
        )->motif);
        self::assertCount(1, $dns->appels);
    }

    public static function domainesInterdits(): array
    {
        return array_map(static fn ($nom) => [$nom], [
            'googlebot.com.exemple.net', 'evilgooglebot.com', 'googlebot.com',
            'crawl.google.com', 'crawl.googleusercontent.com', 'https://x.googlebot.com',
            'x..googlebot.com', 'x.googlebot.com..', "x.googlebot.com\n", 'x_googlebot.com',
        ]);
    }

    public function testIpv6CanoniqueEtPointFinalDns(): void
    {
        $dns = new DnsFictif();
        $dns->noms = ['CRAWL-FICTIF.GOOGLEBOT.COM.'];
        $dns->adresses = ['2001:db8:0:0::1'];
        $decision = $this->moteur($dns)->verifier('Googlebot/2.1', '2001:db8::1', $this->date());
        self::assertTrue($decision->estVerifie());
        self::assertSame('crawl-fictif.googlebot.com', $dns->appels[1][1]);
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('agentsInterdits')]
    public function testJetonAgentExactSansDns(string $agent): void
    {
        $dns = new DnsFictif();
        self::assertSame(Motif::AgentInconnu, $this->moteur($dns)->verifier(
            $agent,
            '192.0.2.1',
            $this->date(),
        )->motif);
        self::assertSame([], $dns->appels);
    }

    public static function agentsInterdits(): array
    {
        return [['NotGooglebot/1'], ['Googlebot-Image/1'], ['GooglebotFake/1'], ['GoogleOther']];
    }

    public function testIpInvalideSansDns(): void
    {
        $dns = new DnsFictif();
        self::assertSame(Motif::IpInvalide, $this->moteur($dns)->verifier(
            'Googlebot/2.1',
            '192.0.2.1, 198.51.100.1',
            $this->date(),
        )->motif);
        self::assertSame([], $dns->appels);
    }

    public function testPanneDnsFermee(): void
    {
        $dns = new DnsFictif();
        $dns->panne = new \RuntimeException('Échec fictif du résolveur');
        self::assertSame('dns_impossible', $this->moteur($dns)->verifier(
            'Googlebot/2.1', '192.0.2.1', $this->date(),
        )->motif->value);
    }

    public function testReponseInverseTropLenteRefuseeSansDirecte(): void
    {
        $dns = new DnsFictif();
        $dns->latence = 200;
        self::assertSame('delai_depasse', $this->moteur($dns)->verifier(
            'Googlebot/2.1', '192.0.2.1', $this->date(),
        )->motif->value);
        self::assertCount(1, $dns->appels);
    }

    public function testBudgetTotalNonRenouvelePourDirecte(): void
    {
        $dns = new DnsFictif();
        $dns->latence = 101;
        self::assertSame('delai_depasse', $this->moteur($dns)->verifier(
            'Googlebot/2.1', '192.0.2.1', $this->date(),
        )->motif->value);
        self::assertSame([200, 99], array_column($dns->appels, 2));
    }

    public function testBudgetDnsConfigurable(): void
    {
        $dns = new DnsFictif();
        $dns->latence = 50;
        $configuration = new Configuration([
            new Robot('google', ['Googlebot'], Methode::Dns, ['googlebot.com']),
        ], delaiDnsMs: 500);
        $moteur = new Verificateur($configuration, $dns, new CacheMemoire(), $dns->horloge);
        self::assertTrue($moteur->verifier('Googlebot/2.1', '192.0.2.1', $this->date())->estVerifie());
        self::assertSame([500, 450], array_column($dns->appels, 2));
    }

    public function testAgentAmbiguSansDns(): void
    {
        $dns = new DnsFictif();
        $configuration = new Configuration([
            new Robot('google', ['Googlebot'], Methode::Dns, ['googlebot.com']),
            new Robot('bing', ['bingbot'], Methode::Dns, ['search.msn.com']),
        ]);
        $moteur = new Verificateur($configuration, $dns, new CacheMemoire(), $dns->horloge);
        self::assertSame('agent_ambigu', $moteur->verifier(
            'Googlebot/2.1 bingbot/2.0', '192.0.2.1', $this->date(),
        )->motif->value);
        self::assertSame([], $dns->appels);
    }

    private function moteur(DnsFictif $dns): Verificateur
    {
        return new Verificateur(new Configuration([
            new Robot('google', ['Googlebot'], Methode::Dns, ['googlebot.com']),
        ]), $dns, new CacheMemoire(), $dns->horloge);
    }

    private function date(): DateTimeImmutable
    {
        return new DateTimeImmutable('2026-11-20T12:00:00+01:00');
    }

    public function testAgentInconnuSansDns(): void
    {
        self::assertTrue(class_exists(Verificateur::class), 'Le moteur C-03 doit exister.');
        $dns = new class implements Dns {
            public function inverse(string $ip, int $delaiMs): array
            {
                throw new \LogicException('Aucun DNS pour un agent inconnu.');
            }

            public function directe(string $nom, int $delaiMs): array
            {
                throw new \LogicException('Aucun DNS pour un agent inconnu.');
            }
        };
        $horloge = new class implements HorlogeMonotone {
            public function millisecondes(): int
            {
                return 0;
            }
        };
        $configuration = new Configuration([
            new Robot('google', ['Googlebot'], Methode::Dns, ['googlebot.com']),
        ]);
        $moteur = new Verificateur($configuration, $dns, new CacheMemoire(), $horloge);
        $decision = $moteur->verifier('RobotAbsent/1.0', '192.0.2.1', new DateTimeImmutable('2026-11-20Z'));
        self::assertFalse($decision->estVerifie());
        self::assertNull($decision->robot);
        self::assertSame(Motif::AgentInconnu, $decision->motif);
    }
}
