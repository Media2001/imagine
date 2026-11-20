<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Numeros;

enum Activation: string
{
    case Paiement = 'paiement';
    case Mandat = 'mandat';
}
