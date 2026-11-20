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
