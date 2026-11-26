<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\CooperateursRegles as R;
use PHPUnit\Framework\TestCase;

/** Découverte par le phpunit.xml existant : ni WordPress, ni base, ni HTTP. */
final class CooperateursReglesTest extends TestCase
{
    public function testDefautEtCapaciteNeValantPasRole(): void
    {
        self::assertTrue(R::administration(['administrator']));
        foreach ([[], ['subscriber'], ['editor'], ['shop_manager'], ['manage_options']] as $roles) {
            self::assertFalse(R::administration($roles));
        }
    }

    public function testChaqueConfigurationIndependanteDesDeuxDroits(): void
    {
        $names = ['administrator', 'editor', 'shop_manager'];
        for ($write = 0; $write < 8; $write++) {
            $writers = array_values(array_filter($names, static fn ($r, $i) => (bool) ($write & (1 << $i)), ARRAY_FILTER_USE_BOTH));
            for ($read = 0; $read < 8; $read++) {
                $readers = array_values(array_filter($names, static fn ($r, $i) => (bool) ($read & (1 << $i)), ARRAY_FILTER_USE_BOTH));
                foreach (array_merge($names, ['subscriber', 'manage_options']) as $role) {
                    self::assertSame(in_array($role, $writers, true), R::administration([$role], $writers));
                    self::assertSame(in_array($role, $readers, true), R::lecture([], [$role], true, $readers));
                    self::assertFalse(R::lecture([], [$role], false, $readers));
                }
            }
        }
    }

    public function testAttributEtCasLimitesSansWordPress(): void
    {
        $state = ['cooperateur' => true, 'source' => 'administration', 'date_utc' => '2026-11-26T15:00:00Z'];
        self::assertTrue(R::lecture($state, [], true, []));
        self::assertFalse(R::lecture($state, [], false, []));
        foreach ([null, '', [], ['cooperateur' => true], array_replace($state, ['cooperateur' => false]),
            array_replace($state, ['cooperateur' => '1']), array_replace($state, ['source' => 'coophub']),
            array_replace($state, ['date_utc' => 'hier']), array_replace($state, ['date_utc' => 123]),
            array_replace($state, ['date_utc' => '2026-11-26 15:00:00']), array_replace($state, ['date_utc' => '2026-11-26T15:00:00Z\n'])] as $bad) {
            self::assertFalse(R::lecture($bad, [], true, []));
        }
        self::assertTrue(R::administration(['subscriber', 'editor'], ['editor']));
        self::assertFalse(R::administration(['manage_options'], ['editor']));
    }
}
