<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

enum Motif: string
{
    case EntreeInvalide = 'entree_invalide';
    case ContenuOuvert = 'contenu_ouvert';
    case RobotVerifie = 'robot_verifie';
    case Anonyme = 'anonyme';
    case SansDroit = 'sans_droit';
}
