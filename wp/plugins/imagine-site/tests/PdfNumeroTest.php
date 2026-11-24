<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

final class PdfNumeroTest extends TestCase
{
    private function request(array $scenario): array
    {
        $process = proc_open([PHP_BINARY, __DIR__ . '/pdf-fixture.php', json_encode($scenario, JSON_THROW_ON_ERROR)],
            [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']], $pipes);
        self::assertIsResource($process);
        fclose($pipes[0]);
        $out = stream_get_contents($pipes[1]);
        $err = stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);
        self::assertSame(0, proc_close($process), $err . $out);
        self::assertSame('', $err);
        return json_decode($out, true, 512, JSON_THROW_ON_ERROR);
    }

    public static function boundaries(): array
    {
        return [
            'unix enfant' => ['/srv/site/uploads/a.pdf', '/srv/site', false, true],
            'unix égal' => ['/srv/site/', '/srv/site', false, true],
            'unix frère' => ['/srv/site-private/a.pdf', '/srv/site', false, false],
            'unix casse distincte' => ['/srv/SITE/a.pdf', '/srv/site', false, false],
            'windows enfant' => ['C:\\Site\\uploads\\a.pdf', 'c:/site/', true, true],
            'windows égal' => ['C:\\SITE', 'c:/site', true, true],
            'windows frère' => ['C:\\site-private\\a.pdf', 'c:/site', true, false],
            'windows autre volume' => ['D:\\Site\\a.pdf', 'c:/site', true, false],
        ];
    }

    #[DataProvider('boundaries')]
    public function testCanonicalDirectoryBoundary(string $path, string $root, bool $windows, bool $expected): void
    {
        $response = $this->request(['action' => 'boundary', 'path' => $path, 'root' => $root, 'windows' => $windows]);
        self::assertNull($response['error']);
        self::assertSame($expected, $response['value']);
    }

    public function testPublicSourceIsActuallyRemoved(): void
    {
        $response = $this->request(['action' => 'protect']);
        self::assertNull($response['error']);
        self::assertTrue($response['value']);
    }

    public static function directories(): array
    {
        return [['public'], ['public/child'], ['missing']];
    }

    #[DataProvider('directories')]
    public function testUnsafeDirectoryFailsClosed(string $directory): void
    {
        $response = $this->request(['action' => 'directory', 'directory' => $directory]);
        self::assertSame('Stockage PDF privé indisponible.', $response['error']);
    }

    public function testNeighbourDirectoryIsNotMistakenForPublicChild(): void
    {
        $response = $this->request(['action' => 'directory', 'directory' => 'public-private']);
        // Absent is closed; the existing sibling is covered by the canonical matrix.
        self::assertNotNull($response['error']);
    }

    public static function pathFaults(): array
    {
        return [['missing'], ['corrupt'], ['traversal'], ['wrong-type']];
    }

    #[DataProvider('pathFaults')]
    public function testPathFailsClosed(string $fault): void
    {
        $response = $this->request(['action' => 'path', 'fault' => $fault]);
        self::assertNotNull($response['error']);
        self::assertStringNotContainsString('%PDF-', base64_decode($response['body']));
    }

    public static function invalidIds(): array
    {
        return [[[]], ['0'], ['01'], ['../1'], ['999']];
    }

    #[DataProvider('invalidIds')]
    public function testServe404(mixed $raw): void
    {
        $response = $this->request(['action' => 'serve', 'raw' => $raw]);
        self::assertSame(404, $response['status']);
        self::assertNull($response['error']);
        self::assertStringNotContainsString('%PDF-', base64_decode($response['body']));
    }

    public function testServe405(): void
    {
        $response = $this->request(['action' => 'serve', 'raw' => '1', 'method' => 'POST']);
        self::assertSame(405, $response['status']);
        self::assertSame('GET, HEAD', $response['headers']['allow']);
    }

    public static function redirects(): array
    {
        return [
            'sans droit' => [['raw' => '1']],
            'panne décision' => [['raw' => '1', 'decision_error' => true]],
            'pdf absent' => [['raw' => '1', 'complete' => true, 'fault' => 'missing']],
            'pièce jointe' => [['attachment' => true]],
        ];
    }

    #[DataProvider('redirects')]
    public function testServeRedirectsWithoutBytes(array $scenario): void
    {
        $response = $this->request(['action' => 'serve'] + $scenario);
        self::assertSame(302, $response['status']);
        self::assertSame('http://example.org/numeros/1/', $response['redirect']);
        self::assertSame('', base64_decode($response['body']));
    }

    public static function methods(): array { return [['GET'], ['HEAD']]; }

    #[DataProvider('methods')]
    public function testAuthorizedGetAndHead(string $method): void
    {
        $response = $this->request(['action' => 'serve', 'raw' => '1', 'complete' => true, 'method' => $method]);
        self::assertNull($response['error']);
        self::assertSame(200, $response['status']);
        self::assertSame('application/pdf', $response['headers']['content-type']);
        self::assertSame($method === 'HEAD' ? '' : '%PDF-1.4 C11 FICTIF', base64_decode($response['body']));
        self::assertStringContainsString('private, no-store', $response['headers']['cache-control']);
        self::assertArrayNotHasKey('etag', $response['headers']);
        self::assertArrayNotHasKey('last-modified', $response['headers']);
    }

    public static function blocks(): array
    {
        return [
            [false, 'connexion', '', 'connexion'],
            [false, 'regularisation', '', 'regularisation'],
            [false, 'abonnement', '', 'abonnement'],
            [true, 'aucun', 'missing', 'abonnement'],
            [true, 'aucun', '', null],
        ];
    }

    #[DataProvider('blocks')]
    public function testBlock(bool $complete, string $bloc, string $fault, ?string $expected): void
    {
        $response = $this->request(['action' => 'block', 'complete' => $complete, 'bloc' => $bloc, 'fault' => $fault]);
        self::assertNull($response['error']);
        $body = base64_decode($response['body']);
        if ($expected === null) {
            self::assertSame('', $body);
        } else {
            self::assertStringContainsString('data-imagine-pdf-bloc="' . $expected . '"', $body);
            self::assertStringNotContainsString('%PDF-', $body);
        }
    }
}
