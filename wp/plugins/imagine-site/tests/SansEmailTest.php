<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\SansEmail;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class SansEmailTest extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/fixtures/c16-sans-email-stubs.php';
    }

    public static function messagesRefuses(): iterable
    {
        yield 'TO .invalid sans compte' => [['to' => 'Fictif <A@SANS-EMAIL.IMAGINE.INVALID>']];
        yield 'TO tableau .invalid et normal' => [['to' => ['normal@example.org', 'fictif@demo.invalid']]];
        yield 'TO marque melange chaine' => [['to' => 'normal@example.org, Fictif <SANS@EXAMPLE.ORG>']];
        yield 'TO marque melange tableau' => [['to' => ['sans@example.org', 'normal@example.org']]];
        yield 'CC marque entetes tableau' => [['to' => 'normal@example.org', 'headers' => ['Cc: Fictif <sans@example.org>']]];
        yield 'BCC marque entetes multiligne' => [['to' => 'normal@example.org', 'headers' => "Content-Type: text/plain\r\nbCc: sans@example.org"]];
        yield 'BCC .invalid sans compte' => [['to' => 'normal@example.org', 'headers' => ['Bcc: fictif@demo.invalid']]];
    }

    #[DataProvider('messagesRefuses')]
    public function testToutLeMessageEstRefuseSansTransport(array $atts): void
    {
        $before = $atts;
        self::assertFalse(SansEmail::filtrer(null, $atts));
        self::assertSame($before, $atts); // Pas de redirection ni suppression partielle de destinataire.
    }

    public function testDestinatairesNormauxConserventLaDecisionPrecedente(): void
    {
        $atts = ['to' => 'normal@example.org', 'headers' => ['Cc: autre@example.org', 'Bcc: inconnu@example.org']];
        self::assertNull(SansEmail::filtrer(null, $atts));
        self::assertFalse(SansEmail::filtrer(false, $atts));
        $sentinel = new \stdClass();
        self::assertSame($sentinel, SansEmail::filtrer($sentinel, $atts));
    }
}
