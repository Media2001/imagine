<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\CommandeRegles;
use PHPUnit\Framework\TestCase;

final class CommandeReglesTest extends TestCase
{
    public function testAdresseNouveauOuiParDefautEtNonExpliciteSeulement(): void
    {
        self::assertTrue(CommandeRegles::adresseNouveau('oui'));
        self::assertFalse(CommandeRegles::adresseNouveau('non'));
        foreach ([null, '', 'invalide', [], false] as $value) {
            self::assertTrue(CommandeRegles::adresseNouveau($value));
        }
    }

    public function testSansEmailIgnoreAdresseSaisieEtNeCreePasAdresseEnPhpPur(): void
    {
        $client = CommandeRegles::client(['mode' => 'nouveau', 'nom' => 'Personnage Fictif', 'sans_email' => '1', 'email' => 'ignore@example.org']);
        self::assertSame('', $client['email']);
        self::assertTrue($client['sans_email']);
        self::assertSame('Personnage Fictif', $client['nom']);
    }

    public function testEmailNormaliseSansModifierIdentiteExistante(): void
    {
        $client = CommandeRegles::client(['mode' => 'nouveau', 'nom' => 'Fictif', 'email' => ' CONNU@EXAMPLE.ORG ']);
        self::assertSame('connu@example.org', $client['email']);
        self::assertFalse($client['sans_email']);
        self::assertSame(12, CommandeRegles::client(['mode' => 'existant', 'client' => '12'])['id']);
        self::assertSame('direct', CommandeRegles::client(['mode' => 'direct'])['mode']);
    }

    public function testClientRefuseTableauEtEmailInvalide(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        CommandeRegles::client(['mode' => 'nouveau', 'nom' => 'Fictif', 'email' => ['bad']]);
    }

    public function testAdresseObligatoireSaufVenteDirecteEtPaiementHorsLigne(): void
    {
        $data = ['produit' => '192', 'paiement' => 'bacs', 'first_name' => 'Personnage', 'last_name' => 'Fictif', 'address_1' => '1 rue Imaginaire', 'postcode' => '1000', 'city' => 'Ville Fictive', 'country' => 'BE'];
        $order = CommandeRegles::commande($data, false);
        self::assertSame(192, $order['produit']);
        self::assertSame('bacs', $order['paiement']);
        self::assertSame('Ville Fictive', $order['adresse']['city']);
        self::assertSame('imagine_papier', CommandeRegles::commande(['produit' => '271', 'paiement' => 'imagine_papier'], true)['paiement']);
    }

    public function testRefusePasserelleEnLigne(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        CommandeRegles::commande(['produit' => '192', 'paiement' => 'stripe'], true);
    }

    public function testRefuseAdresseIncomplete(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        CommandeRegles::commande(['produit' => '192', 'paiement' => 'bacs'], false);
    }
}
