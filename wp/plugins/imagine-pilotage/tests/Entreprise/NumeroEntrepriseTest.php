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

    #[\PHPUnit\Framework\Attributes\DataProvider('invalides')]
    public function testRefuseAvecMotifFrancais(string $saisie, string $motif, string $message): void
    {
        $resultat = NumeroEntreprise::depuisSaisie($saisie);
        self::assertFalse($resultat->estValide());
        self::assertSame($motif, $resultat->motif->value);
        self::assertSame($message, $resultat->message());
        self::assertNull($resultat->normalise);
        self::assertNull($resultat->affichage());
    }

    public static function invalides(): iterable
    {
        $vide = 'Veuillez saisir votre numéro d’entreprise belge.';
        $longueur = 'Le numéro d’entreprise doit contenir 10 chiffres (ou 9 dans l’ancien format).';
        $caracteres = 'Utilisez uniquement des chiffres, des espaces, des points ou des tirets, '
            . 'avec BE en préfixe facultatif.';
        $debut = 'Le numéro d’entreprise belge doit commencer par 0 ou 1.';
        $cle = 'La clé de contrôle du numéro d’entreprise est incorrecte. Vérifiez les chiffres saisis.';
        yield 'vide' => ['', 'vide', $vide];
        yield 'espaces seuls' => [" \u{00A0}\u{202F}", 'vide', $vide];
        yield 'prefixe seul' => ['BE', 'vide', $vide];
        yield 'separateurs seuls' => [' .-- ', 'vide', $vide];
        yield 'huit chiffres' => ['01234567', 'longueur', $longueur];
        yield 'onze chiffres' => [self::fictif('01234567') . '0', 'longueur', $longueur];
        yield 'lettres' => ['0123A56749', 'caracteres_interdits', $caracteres];
        yield 'autre pays' => ['FR' . self::fictif('01234567'), 'caracteres_interdits', $caracteres];
        yield 'prefixe repete' => ['BEBE' . self::fictif('01234567'), 'caracteres_interdits', $caracteres];
        yield 'prefixe coupe' => ['B E' . self::fictif('01234567'), 'caracteres_interdits', $caracteres];
        yield 'premier chiffre deux' => [self::fictif('22345678'), 'premier_chiffre', $debut];
        yield 'cle fausse' => ['0123456700', 'cle_incorrecte', $cle];
        yield 'ancien format cle fausse' => ['123456700', 'cle_incorrecte', $cle];
        yield 'lettres avant longueur' => ['A', 'caracteres_interdits', $caracteres];
        yield 'signe plus' => ['+' . self::fictif('01234567'), 'caracteres_interdits', $caracteres];
        yield 'barre oblique' => ['0123/456/749', 'caracteres_interdits', $caracteres];
        yield 'chiffres unicode' => ['０１２３４５６７４９', 'caracteres_interdits', $caracteres];
        yield 'tabulation' => ["\t" . self::fictif('01234567'), 'caracteres_interdits', $caracteres];
        yield 'saut de ligne' => [self::fictif('01234567') . "\n", 'caracteres_interdits', $caracteres];
        yield 'octet nul' => [self::fictif('01234567') . "\0", 'caracteres_interdits', $caracteres];
        yield 'utf8 mal forme' => ["\xFF", 'caracteres_interdits', $caracteres];
    }

    public function testMessagesPassentParLeTraducteurInjecte(): void
    {
        $traduire = static fn (string $texte): string => 'TRADUIT:' . $texte;
        foreach (['', self::fictif('01234567'), '0123456700'] as $saisie) {
            $r = NumeroEntreprise::depuisSaisie($saisie);
            self::assertSame('TRADUIT:' . $r->message(), $r->message($traduire));
        }
    }

    public function testCouvreTousLesRestesEtToutesLesCles(): void
    {
        foreach ([0, 10000000] as $debut) {
            for ($offset = 0; $offset < 97; $offset++) {
                $base = sprintf('%08d', $debut + $offset);
                // Oracle par divisions successives, distinct du modulo de production.
                $reste = 0;
                foreach (str_split($base) as $chiffre) {
                    $reste = $reste * 10 + (int) $chiffre;
                    while ($reste >= 97) {
                        $reste -= 97;
                    }
                }
                for ($cle = 0; $cle <= 99; $cle++) {
                    $saisie = $base . sprintf('%02d', $cle);
                    $valide = NumeroEntreprise::depuisSaisie($saisie)->estValide();
                    self::assertSame($cle === 97 - $reste, $valide, $saisie);
                }
            }
        }
    }

    public function testResultatImmuableEtNonForgeable(): void
    {
        $classe = new \ReflectionClass(NumeroEntreprise::class);
        self::assertTrue($classe->isReadOnly());
        self::assertTrue($classe->getConstructor()->isPrivate());
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
