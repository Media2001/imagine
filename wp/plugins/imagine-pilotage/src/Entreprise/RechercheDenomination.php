<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Entreprise;

/**
 * Point d'injection prévu par §3.4 ; décision 8 ouverte, aucune recherche réelle.
 * L'appelant contrôle estValide() avant toute future recherche.
 */
interface RechercheDenomination
{
    public function rechercher(NumeroEntreprise $numero): ResultatRecherche;
}
