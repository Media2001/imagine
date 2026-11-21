<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

enum Bloc: string
{
    case Aucun = 'aucun';
    case Abonnement = 'abonnement';
    case Connexion = 'connexion';
    case Regularisation = 'regularisation';
}
