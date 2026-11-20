<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Entreprise;

/** Implémentation vide : ni réseau, ni fichier, ni existence déduite du numéro. */
final class RechercheDenominationIndisponible implements RechercheDenomination
{
    public function rechercher(NumeroEntreprise $numero): ResultatRecherche
    {
        return new ResultatRecherche();
    }
}
