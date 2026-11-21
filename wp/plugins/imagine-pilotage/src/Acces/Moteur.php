<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

use Imagine\Pilotage\Robots\Decision as DecisionRobot;

final class Moteur
{
    public function decider(
        mixed $contenu = null,
        mixed $visiteur = null,
        mixed $robot = null,
        mixed $instant = null,
    ): Decision {
        if (
            !is_array($contenu) || !is_array($visiteur) || !$robot instanceof DecisionRobot
            || !$instant instanceof \DateTimeImmutable
            || !$this->cles($contenu, ['reserve', 'numero', 'type', 'sortie', 'decouverte'])
            || !is_bool($contenu['reserve']) || !is_bool($contenu['decouverte'])
            || !is_string($contenu['numero']) || trim($contenu['numero']) === ''
            || !in_array($contenu['type'], ['article', 'pdf'], true)
            || !$contenu['sortie'] instanceof \DateTimeImmutable
            || !$this->cles($visiteur, ['identifie', 'droits'])
            || !is_bool($visiteur['identifie']) || !is_array($visiteur['droits'])
            || !array_is_list($visiteur['droits']) || $visiteur['droits'] !== []
        ) {
            return new Decision(false, Motif::EntreeInvalide, Bloc::Abonnement);
        }
        if (!$contenu['reserve']) {
            return new Decision(true, Motif::ContenuOuvert, Bloc::Aucun);
        }
        if ($robot->estVerifie()) {
            return new Decision(true, Motif::RobotVerifie, Bloc::Aucun);
        }
        return $visiteur['identifie']
            ? new Decision(false, Motif::SansDroit, Bloc::Abonnement)
            : new Decision(false, Motif::Anonyme, Bloc::Connexion);
    }

    private function cles(array $valeur, array $cles): bool
    {
        return count($valeur) === count($cles) && array_diff($cles, array_keys($valeur)) === [];
    }
}
