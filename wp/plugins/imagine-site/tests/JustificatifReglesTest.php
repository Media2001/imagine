<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\JustificatifRegles;
use PHPUnit\Framework\TestCase;

final class JustificatifReglesTest extends TestCase
{
    public function testTypesAreDetectedFromBytesAndSizeIsBounded(): void
    {
        self::assertSame('application/pdf', JustificatifRegles::mime("%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n"));
        foreach (["<?php echo 1;", '<svg/>', "%PDF-1.4\n<?php echo 1;", str_repeat('a', 5242881), ''] as $bad) {
            try {
                JustificatifRegles::mime($bad);
                self::fail('Contenu dangereux accepté');
            } catch (\InvalidArgumentException) {
                self::assertTrue(true);
            }
        }
    }

    public function testEndDateEqualToTodayIsAccepted(): void
    {
        $now = gmdate('Y-m-d\TH:i:s\Z');
        $today = substr($now, 0, 10);
        $state = JustificatifRegles::decider(
            ['decision' => 'en_attente', 'categorie' => 'à préciser'], 'valide', $today, 'e-abo', $now
        );
        self::assertSame($today, $state['fin']);
        self::assertSame('valide', $state['decision']);
    }

    public function testCompletePngAndJpegAreAcceptedFromContent(): void
    {
        foreach (['png' => 'image/png', 'jpg' => 'image/jpeg'] as $extension => $mime) {
            $bytes = file_get_contents(__DIR__ . '/fixtures/c17-fictif.' . $extension);
            self::assertSame($mime, JustificatifRegles::mime($bytes));
            self::assertSame([2, 2], array_slice(getimagesizefromstring($bytes), 0, 2));
        }
    }

    public function testCompletePdfAtExactlyFiveMibIsAccepted(): void
    {
        $pdf = file_get_contents(__DIR__ . '/fixtures/c17-fictif.pdf');
        $pdf = str_replace('%%EOF', '%' . str_repeat(' ', JustificatifRegles::MAX - strlen($pdf) - 2) . "\n%%EOF", $pdf);
        self::assertSame(JustificatifRegles::MAX, strlen($pdf));
        self::assertSame('application/pdf', JustificatifRegles::mime($pdf));
    }

    public function testCategoriesAreStrictAndUnknownValuesAreRejected(): void
    {
        self::assertSame(['à préciser'], JustificatifRegles::categories(['à préciser']));
        self::assertSame(['Étudiant', 'Autre'], JustificatifRegles::categories("Étudiant\nAutre"));
        $this->expectException(\InvalidArgumentException::class);
        JustificatifRegles::depot('inventée', ['à préciser']);
    }

    public function testRefusalKeepsNoEndDateOrBlob(): void
    {
        $r = JustificatifRegles::decider(
            ['decision' => 'en_attente', 'categorie' => 'à préciser', 'blob' => 'secret'],
            'refuse',
            'non utilisé',
            'e-abo',
            '2026-11-26T00:00:00Z'
        );
        self::assertSame('', $r['fin']);
        self::assertArrayNotHasKey('blob', $r);
    }

    public function testInvalidDateAndReplayAreRejected(): void
    {
        foreach (['2027-02-29', '2026-11-25', '2027-01-01xxx', ''] as $fin) {
            try {
                JustificatifRegles::decider(['decision' => 'en_attente', 'categorie' => 'à préciser'], 'valide', $fin, 'e-abo', '2026-11-26T00:00:00Z');
                self::fail('Date invalide acceptée');
            } catch (\InvalidArgumentException) {
                self::assertTrue(true);
            }
        }
        $this->expectException(\InvalidArgumentException::class);
        JustificatifRegles::decider(['decision' => 'valide'], 'refuse', '', 'e-abo', '2026-11-26T00:00:00Z');
    }

    public function testDecisionRemovesAllDocumentReferences(): void
    {
        self::assertTrue(class_exists(JustificatifRegles::class), 'Règles C17 absentes');
        $result = JustificatifRegles::decider(['decision' => 'en_attente', 'categorie' => 'à préciser',
            'blob' => str_repeat('a', 32)], 'valide', '2027-01-31', 'e-abo', '2026-11-26T00:00:00Z');
        self::assertSame(['categorie' => 'à préciser', 'decision' => 'valide',
            'date_decision' => '2026-11-26T00:00:00Z', 'fin' => '2027-01-31', 'operateur' => 'e-abo'], $result);
    }
}
