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
        mixed $decouverte = null,
    ): Decision {
        try {
            return $this->evaluer($contenu, $visiteur, $robot, $instant, $decouverte);
        } catch (\Throwable) {
            return new Decision(false, Motif::EntreeInvalide, Bloc::Abonnement);
        }
    }

    private function evaluer(
        mixed $contenu,
        mixed $visiteur,
        mixed $robot,
        mixed $instant,
        mixed $decouverte,
    ): Decision {
        // Liste synchronisée manuellement avec config/robots.php : tout nouveau robot
        // approuvé doit être ajouté aux deux endroits, sinon accès fermé en extrait.
        if (
            !is_array($contenu) || !is_array($visiteur) || !$robot instanceof DecisionRobot
            || !$this->dateValide($instant)
            || ($robot->estVerifie() && !in_array($robot->robot, ['google', 'bing'], true))
            || ($decouverte !== null && (
                (!$decouverte instanceof DureeDecouverte && !$decouverte instanceof NombreArticlesDecouverte)
                || !$decouverte->estValide()
            ))
            || !$this->cles($contenu, ['reserve', 'numero', 'type', 'sortie', 'decouverte'])
            || !is_bool($contenu['reserve']) || !is_bool($contenu['decouverte'])
            || !$this->identifiantValide($contenu['numero'])
            || !in_array($contenu['type'], ['article', 'pdf'], true)
            || !$this->dateValide($contenu['sortie']) || $contenu['sortie'] > $instant
            || !$this->cles($visiteur, ['identifie', 'droits'])
            || !is_bool($visiteur['identifie']) || !is_array($visiteur['droits'])
            || !array_is_list($visiteur['droits'])
            || (!$visiteur['identifie'] && $visiteur['droits'] !== [])
        ) {
            return new Decision(false, Motif::EntreeInvalide, Bloc::Abonnement);
        }
        $nombreDecouvertes = 0;
        foreach ($visiteur['droits'] as $droit) {
            if (
                !$this->droitValide($droit)
                || ($droit['type'] === 'decouverte' && ($decouverte === null || ++$nombreDecouvertes > 1))
            ) {
                return new Decision(false, Motif::EntreeInvalide, Bloc::Abonnement);
            }
        }
        if (!$contenu['reserve']) {
            return new Decision(true, Motif::ContenuOuvert, Bloc::Aucun);
        }
        if ($robot->estVerifie()) {
            return new Decision(true, Motif::RobotVerifie, Bloc::Aucun);
        }
        $decision = $visiteur['identifie']
            ? new Decision(false, Motif::SansDroit, Bloc::Abonnement)
            : new Decision(false, Motif::Anonyme, Bloc::Connexion);
        foreach ($visiteur['droits'] as $droit) {
            $candidate = match ($droit['type']) {
                'equipe' => new Decision(true, Motif::Equipe, Bloc::Aucun),
                'cooperateur' => new Decision(false, Motif::CooperateurSansAbonnement, Bloc::Abonnement),
                'achat' => $this->achat($droit, $contenu, $instant),
                'decouverte' => $this->decouverte($decouverte, $droit, $contenu, $instant),
                default => $this->abonnement($droit, $contenu, $instant),
            };
            if ($this->priorite($candidate) > $this->priorite($decision)) {
                $decision = $candidate;
            }
        }
        return $decision;
    }

    private function abonnement(array $droit, array $contenu, \DateTimeImmutable $instant): Decision
    {
        if (in_array($droit['etat'], ['suspendu', 'expire', 'virement_non_valide'], true)) {
            return new Decision(
                false,
                Motif::from($droit['etat']),
                $droit['etat'] === 'expire' ? Bloc::Abonnement : Bloc::Regularisation,
            );
        }
        if ($instant < $droit['debut']) {
            return new Decision(false, Motif::AbonnementPasCommence, Bloc::Abonnement);
        }
        if ($instant >= $droit['fin']) {
            return new Decision(false, Motif::Expire, Bloc::Abonnement);
        }
        if ($contenu['type'] === 'pdf' && $contenu['sortie'] < $droit['debut']) {
            return new Decision(false, Motif::PdfAnterieurAArbitrer, Bloc::Abonnement);
        }
        return $droit['etat'] === 'grace'
            ? new Decision(true, Motif::DelaiGrace, Bloc::Regularisation)
            : new Decision(true, Motif::from($droit['type'] . '_actif'), Bloc::Aucun);
    }

    private function decouverte(
        Decouverte $reglage,
        array $droit,
        array $contenu,
        \DateTimeImmutable $instant,
    ): Decision {
        $motif = $reglage->evaluer($contenu, $droit, $instant);
        return new Decision(
            in_array($motif, [Motif::DecouverteDuree, Motif::DecouverteArticles], true),
            $motif,
            match ($motif) {
                Motif::DecouverteDuree, Motif::DecouverteArticles => Bloc::Aucun,
                Motif::DecouverteEpuisee => Bloc::DecouverteEpuisee,
                Motif::CompteNonVerifie => Bloc::Connexion,
                default => Bloc::Abonnement,
            },
        );
    }

    private function achat(array $droit, array $contenu, \DateTimeImmutable $instant): Decision
    {
        if ($droit['numero'] !== $contenu['numero']) {
            return new Decision(false, Motif::AutreNumero, Bloc::Abonnement);
        }
        return $instant < $droit['acquis_le']
            ? new Decision(false, Motif::AchatPasCommence, Bloc::Abonnement)
            : new Decision(true, Motif::NumeroAchete, Bloc::Aucun);
    }

    private function droitValide(mixed $droit): bool
    {
        if (!is_array($droit) || !isset($droit['type'])) {
            return false;
        }
        if ($droit['type'] === 'decouverte') {
            return $this->cles($droit, ['type', 'debut', 'compte_verifie', 'consommes'])
                && $this->dateValide($droit['debut']) && is_bool($droit['compte_verifie'])
                && is_int($droit['consommes']) && $droit['consommes'] >= 0;
        }
        if ($droit['type'] === 'equipe') {
            return $this->cles($droit, ['type', 'role'])
                && in_array($droit['role'], ['redaction', 'administration'], true);
        }
        if ($droit['type'] === 'cooperateur') {
            return $this->cles($droit, ['type']);
        }
        if ($droit['type'] === 'achat') {
            return $this->cles($droit, ['type', 'numero', 'acquis_le'])
                && $this->identifiantValide($droit['numero'])
                && $this->dateValide($droit['acquis_le']);
        }
        return $this->cles($droit, ['type', 'etat', 'debut', 'fin'])
            && in_array($droit['type'], ['abonnement', 'offert', 'groupe'], true)
            && in_array($droit['etat'], ['actif', 'grace', 'suspendu', 'expire', 'virement_non_valide'], true)
            && $this->dateValide($droit['debut']) && $this->dateValide($droit['fin'])
            && $droit['debut'] < $droit['fin'];
    }

    private function priorite(Decision $decision): int
    {
        return match ($decision->motif) {
            Motif::Equipe => 120,
            Motif::NumeroAchete => 110,
            Motif::AbonnementActif => 100,
            Motif::OffertActif => 99,
            Motif::GroupeActif => 98,
            Motif::DelaiGrace => 80,
            Motif::DecouverteDuree, Motif::DecouverteArticles => 90,
            Motif::DecouverteEpuisee => 23,
            Motif::DecouvertePasCommencee => 22,
            Motif::DecouverteHorsPerimetre => 21,
            Motif::CompteNonVerifie => 20,
            Motif::Suspendu => 30,
            Motif::VirementNonValide => 29,
            Motif::Expire => 28,
            Motif::AbonnementPasCommence => 27,
            Motif::PdfAnterieurAArbitrer => 26,
            Motif::AchatPasCommence => 25,
            Motif::AutreNumero => 24,
            Motif::CooperateurSansAbonnement => 1,
            default => 0,
        };
    }

    private function dateValide(mixed $date): bool
    {
        return $date instanceof \DateTimeImmutable && $date->format('u') === '000000';
    }

    private function identifiantValide(mixed $identifiant): bool
    {
        return is_string($identifiant) && $identifiant !== ''
            && preg_match('/[\x00-\x20\x7f]/', $identifiant) === 0;
    }

    private function cles(array $valeur, array $cles): bool
    {
        return count($valeur) === count($cles) && array_diff($cles, array_keys($valeur)) === [];
    }
}
