<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

enum Motif: string
{
    case AgentInconnu = 'agent_inconnu';
    case VerifieDns = 'verifie_dns';
    case DomaineRefuse = 'domaine_refuse';
    case AdresseDifferente = 'adresse_differente';
    case IpInvalide = 'ip_invalide';
}
