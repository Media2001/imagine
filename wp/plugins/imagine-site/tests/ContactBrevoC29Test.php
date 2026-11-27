<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use PHPUnit\Framework\TestCase;

final class ContactBrevoC29Test extends TestCase
{
    public function testUnCompteConsentiActifProduitUneFichePure(): void
    {
        self::assertTrue(class_exists(\Imagine\Site\ContactBrevoRegles::class), 'C29 calcul pur absent');
        $input = ['existe' => true, 'email_recevable' => true, 'email' => 'fictif@example.org',
            'catalogue' => ['principale'], 'preferences' => ['principale' => ['choix' => true, 'origine' => 'lecteur']],
            'abonnements' => [['etat' => 'active', 'tarifs' => ['normal-1']]], 'beneficiaire' => false,
            'cooperateur' => false, 'tarifs_autorises' => ['normal-1'], 'personnalisation' => ['fictif' => ['choix' => ['a']]]];
        $copy = $input;
        self::assertSame(['fiche' => ['email' => 'fictif@example.org', 'statut' => 'abonne', 'cooperateur' => 'non',
            'tarif' => 'normal-1', 'newsletters' => ['principale'], 'personnalisation' => $input['personnalisation']],
            'raison' => 'eligible'], \Imagine\Site\ContactBrevoRegles::fiche($input));
        self::assertSame($copy, $input);
    }
}
