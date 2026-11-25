<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use DateTimeImmutable;
use Imagine\Site\AchatNumero;
use PHPUnit\Framework\TestCase;

require_once dirname(__DIR__) . '/AchatNumero.php';

final class AchatNumeroTest extends TestCase
{
    public function testSnapshotRemainsTheOnlyAcquiredIssue(): void
    {
        $line = ['client' => 42, 'etat' => 'processing', 'payee' => true,
            'acquis' => new DateTimeImmutable('2020-01-01T00:00:00Z'),
            'remboursement' => false, 'instantane' => 12, 'publie' => true, 'quantite' => 1];
        foreach ([13, 0, null] as $mapping) {
            self::assertSame('12', AchatNumero::droit(42, $line + ['numero' => $mapping])['numero']);
        }
        foreach (['publie' => false, 'instantane' => 0, 'quantite' => 0] as $key => $value) {
            self::assertNull(AchatNumero::droit(42, array_replace($line, [$key => $value])));
        }
        self::assertNull(AchatNumero::droit(42, array_diff_key($line, ['publie' => true])));
        self::assertNull(AchatNumero::droit(42, array_diff_key($line, ['instantane' => true])));
    }

    public function testRefundScopeDefaultsClosedAndSupportsPerLine(): void
    {
        foreach (['commande', 'ligne', 'invalide', null, []] as $scope) {
            self::assertFalse(AchatNumero::remboursement($scope, false, false, false));
            self::assertTrue(AchatNumero::remboursement($scope, true, true, false));
            self::assertTrue(AchatNumero::remboursement($scope, true, false, true));
            self::assertSame($scope !== 'ligne', AchatNumero::remboursement($scope, true, false, false));
        }
    }
}
