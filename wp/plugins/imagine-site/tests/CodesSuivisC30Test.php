<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\CodesSuivisRegles;
use PHPUnit\Framework\TestCase;

final class CodesSuivisC30Test extends TestCase
{
    public function testListeFermeeEtChampsExacts(): void
    {
        $list = ['fictif-affiche' => 'FICTIF \\ Affiche'];
        self::assertSame($list, CodesSuivisRegles::liste($list));
        self::assertSame([], CodesSuivisRegles::liste([]));
        self::assertNull(CodesSuivisRegles::liste(['../injection' => 'test']));
        self::assertNull(CodesSuivisRegles::liste(['fictif' => '<script>']));
        self::assertNull(CodesSuivisRegles::retenir('inconnu', $list));
        self::assertNull(CodesSuivisRegles::retenir(['fictif-affiche'], $list));
        self::assertSame(['code' => 'fictif-affiche', 'libelle' => 'FICTIF \\ Affiche'], CodesSuivisRegles::retenir('fictif-affiche', $list));
    }

    public function testMutationInconnuRefuseParLeMemeControle(): void
    {
        $source = file_get_contents(dirname(__DIR__) . '/CodesSuivisRegles.php');
        $source = str_replace('final class CodesSuivisRegles', 'final class CodesSuivisReglesMutantC30', $source);
        $source = str_replace("isset(\$liste[\$code])", 'true', $source);
        $source = str_replace("\$liste[\$code]", "(\$liste[\$code] ?? 'FICTIF inventé')", $source);
        eval(substr($source, strpos($source, 'namespace')));
        $control = static fn ($result): bool => $result === null;
        self::assertTrue($control(CodesSuivisRegles::retenir('inconnu', [])));
        self::assertFalse($control(\Imagine\Site\CodesSuivisReglesMutantC30::retenir('inconnu', [])));
    }
}
