<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Entreprise;

use Imagine\Pilotage\Entreprise\NumeroEntreprise;
use PHPUnit\Framework\TestCase;

/** §3.4 et brief C-02 : cohérence locale seulement, aucun registre interrogé. */
final class NumeroEntrepriseTest extends TestCase
{
    private static function fictif(string $base): string
    {
        return $base . sprintf('%02d', 97 - ((int) $base % 97));
    }

    #[\PHPUnit\Framework\Attributes\DataProvider('formes')]
    public function testNormaliseLesFormesDeSaisie(string $saisie, string $attendu): void
    {
        $resultat = NumeroEntreprise::depuisSaisie($saisie);
        self::assertTrue($resultat->estValide());
        self::assertSame($attendu, $resultat->normalise);
        self::assertSame($attendu, NumeroEntreprise::depuisSaisie($resultat->affichage())->normalise);
    }

    public static function formes(): iterable
    {
        $n = self::fictif('01234567');
        $p = substr($n, 0, 4) . '.' . substr($n, 4, 3) . '.' . substr($n, 7);
        yield 'prefixe' => ['BE' . $n, $n];
        yield 'points' => [$p, $n];
        yield 'espaces' => ['  BE ' . substr($n, 0, 4) . ' ' . substr($n, 4, 3) . ' ' . substr($n, 7) . ' ', $n];
        yield 'tirets' => [str_replace('.', '-', $p), $n];
        yield 'minuscules' => ['be ' . $p, $n];
        yield 'espaces insécables' => ["\u{00A0}BE\u{202F}" . $p . "\u{00A0}", $n];
        yield 'neuf chiffres' => [substr($n, 1), $n];
        yield 'ancien format préfixé' => ['BE ' . substr($p, 1), $n];
        yield 'separateurs mixtes' => ['BE ' . str_replace('.', ' - ', $p), $n];
        yield 'premier chiffre un' => [self::fictif('12345678'), self::fictif('12345678')];
    }

    public function testAccepteDixChiffresEtExposeAffichage(): void
    {
        $numero = self::fictif('01234567');
        $resultat = NumeroEntreprise::depuisSaisie($numero);

        self::assertTrue($resultat->estValide());
        self::assertSame($numero, $resultat->normalise);
        $affichage = substr($numero, 0, 4) . '.' . substr($numero, 4, 3) . '.' . substr($numero, 7);
        self::assertSame($affichage, $resultat->affichage());
        self::assertNull($resultat->motif);
        self::assertSame('Le numéro d’entreprise est cohérent.', $resultat->message());
    }
}
