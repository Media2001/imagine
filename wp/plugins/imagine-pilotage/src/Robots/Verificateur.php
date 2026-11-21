<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

use DateTimeImmutable;

/** C-03 / §3.9 et §4.4 : une identité seulement, jamais un droit au contenu. */
final readonly class Verificateur
{
    public function __construct(
        private Configuration $configuration,
        private Dns $dns,
        private Cache $cache,
        private HorlogeMonotone $horloge,
    ) {
    }

    public function verifier(string $agent, string $ip, DateTimeImmutable $maintenant): Decision
    {
        $candidats = array_values(array_filter(
            $this->configuration->robots,
            static function (Robot $robot) use ($agent): bool {
                foreach ($robot->agents as $jeton) {
                    $motif = '~(?<![a-z0-9_-])' . preg_quote($jeton, '~') . '(?=[/\s;)]|$)~i';
                    if (preg_match($motif, $agent) === 1) {
                        return true;
                    }
                }
                return false;
            },
        ));
        if ($candidats === []) {
            return new Decision(Motif::AgentInconnu);
        }
        if (count($candidats) !== 1) {
            return new Decision(Motif::AgentAmbigu);
        }
        if (filter_var($ip, FILTER_VALIDATE_IP) === false) {
            return new Decision(Motif::IpInvalide);
        }
        $robot = $candidats[0];
        $ip = inet_ntop(inet_pton($ip));
        $cle = hash('sha256', serialize(['c03-v2', $this->configuration, $robot->identifiant, $ip]));
        try {
            $entree = $this->cache->lire($cle);
        } catch (\Throwable) {
            return new Decision(Motif::CacheIndisponible);
        }
        if ($entree !== null && $entree->creation <= $maintenant && $maintenant < $entree->expiration) {
            return $entree->decision;
        }
        try {
            $decision = $robot->methode === Methode::Dns
                ? $this->verifierDns($robot, $ip)
                : $this->verifierPlages($robot, $ip, $maintenant);
        } catch (DelaiDnsDepasse) {
            $decision = new Decision(Motif::DelaiDepasse);
        } catch (\Throwable) {
            $decision = new Decision(Motif::DnsImpossible);
        }
        if (
            !$decision->estVerifie()
            && !in_array($decision->motif, [Motif::DomaineRefuse, Motif::AdresseDifferente, Motif::PlageAbsente], true)
        ) {
            // Une panne ou un doute est refusé sans empoisonner la requête suivante.
            return $decision;
        }
        $ttl = $decision->estVerifie() ? $this->configuration->ttlPositif : $this->configuration->ttlNegatif;
        $expiration = $maintenant->setTimezone(new \DateTimeZone('UTC'))->modify('+' . $ttl . ' seconds');
        if ($decision->estVerifie() && $robot->methode === Methode::Plages) {
            $expiration = min($expiration, $robot->expirationPlages);
        }
        try {
            $this->cache->ecrire($cle, new EntreeCache($decision, $maintenant, $expiration));
        } catch (\Throwable) {
            return new Decision(Motif::CacheIndisponible);
        }
        return $decision;
    }

    private function verifierPlages(Robot $robot, string $ip, DateTimeImmutable $maintenant): Decision
    {
        if ($robot->expirationPlages === null || $maintenant >= $robot->expirationPlages) {
            return new Decision(Motif::PlagesExpirees);
        }
        foreach ($robot->reseaux as $plage) {
            if ($plage->contient($ip)) {
                return new Decision(Motif::VerifiePlage, $robot->identifiant);
            }
        }
        return new Decision(Motif::PlageAbsente);
    }

    private function verifierDns(Robot $robot, string $ip): Decision
    {
        $domaineAdmis = false;
        $debut = $this->horloge->millisecondes();
        $noms = $this->dns->inverse($ip, $this->reste($debut));
        $this->reste($debut);
        foreach ($noms as $nom) {
            $nom = strtolower(str_ends_with($nom, '.') ? substr($nom, 0, -1) : $nom);
            if (!$this->domaineAdmis($nom, $robot)) {
                continue;
            }
            $domaineAdmis = true;
            $adresses = $this->dns->directe($nom, $this->reste($debut));
            $this->reste($debut);
            foreach ($adresses as $adresse) {
                if (filter_var($adresse, FILTER_VALIDATE_IP) !== false && inet_pton($adresse) === inet_pton($ip)) {
                    return new Decision(Motif::VerifieDns, $robot->identifiant);
                }
            }
        }
        return new Decision($domaineAdmis ? Motif::AdresseDifferente : Motif::DomaineRefuse);
    }

    private function reste(int $debut): int
    {
        $ecoule = $this->horloge->millisecondes() - $debut;
        if ($ecoule < 0 || $ecoule >= $this->configuration->delaiDnsMs) {
            throw new DelaiDnsDepasse();
        }
        return $this->configuration->delaiDnsMs - $ecoule;
    }

    private function domaineAdmis(string $nom, Robot $robot): bool
    {
        if (
            strlen($nom) > 253 || preg_match(
                '/\A[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+\z/D',
                $nom,
            ) !== 1
        ) {
            return false;
        }
        foreach ($robot->domaines as $domaine) {
            if (str_ends_with($nom, '.' . strtolower($domaine))) {
                return true;
            }
        }
        return false;
    }
}
