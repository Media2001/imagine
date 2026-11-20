<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Entreprise;

use Imagine\Pilotage\Entreprise\NumeroEntreprise;
use Imagine\Pilotage\Entreprise\RechercheDenomination;
use Imagine\Pilotage\Entreprise\RechercheDenominationIndisponible;
use Imagine\Pilotage\Entreprise\ResultatRecherche;
use InvalidArgumentException;
use PHPUnit\Framework\TestCase;

final class RechercheDenominationTest extends TestCase
{
    public function testImplementationVideSignaleIndisponibiliteSansDenomination(): void
    {
        $recherche = new RechercheDenominationIndisponible();
        self::assertInstanceOf(RechercheDenomination::class, $recherche);
        $base = '01234567';
        $numero = NumeroEntreprise::depuisSaisie($base . sprintf('%02d', 97 - ((int) $base % 97)));
        $resultat = $recherche->rechercher($numero);
        self::assertFalse($resultat->estDisponible());
        self::assertNull($resultat->denomination);
        self::assertSame('La recherche de dénomination n’est pas disponible.', $resultat->message());
        self::assertSame('TRADUIT:' . $resultat->message(), $resultat->message(static fn ($t) => 'TRADUIT:' . $t));
        self::assertTrue($numero->estValide());
    }

    public function testInterfaceInjectableAvecDoubleStrictementFictif(): void
    {
        $faux = new class implements RechercheDenomination {
            public function rechercher(NumeroEntreprise $numero): ResultatRecherche
            {
                return new ResultatRecherche('Organisation fictive C-02');
            }
        };
        $base = '12345678';
        $numero = NumeroEntreprise::depuisSaisie($base . sprintf('%02d', 97 - ((int) $base % 97)));
        $r = $faux->rechercher($numero);
        self::assertTrue($r->estDisponible());
        self::assertSame('Organisation fictive C-02', $r->denomination);
        self::assertSame('Une dénomination a été trouvée.', $r->message());
        self::assertSame('TRADUIT:' . $r->message(), $r->message(static fn ($t) => 'TRADUIT:' . $t));
        self::assertTrue((new \ReflectionClass($r))->isReadOnly());
    }

    public function testUneDenominationVideNeSimulePasUnSucces(): void
    {
        $this->expectException(InvalidArgumentException::class);
        new ResultatRecherche('   ');
    }
}
