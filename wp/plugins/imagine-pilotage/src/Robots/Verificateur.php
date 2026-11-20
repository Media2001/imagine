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
        private CacheMemoire $cache,
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
        if (filter_var($ip, FILTER_VALIDATE_IP) === false) {
            return new Decision(Motif::IpInvalide);
        }
        return $this->verifierDns($candidats[0], $ip);
    }

    private function verifierDns(Robot $robot, string $ip): Decision
    {
        $domaineAdmis = false;
        foreach ($this->dns->inverse($ip, 200) as $nom) {
            $nom = strtolower(str_ends_with($nom, '.') ? substr($nom, 0, -1) : $nom);
            if (!$this->domaineAdmis($nom, $robot)) {
                continue;
            }
            $domaineAdmis = true;
            foreach ($this->dns->directe($nom, 200) as $adresse) {
                if (filter_var($adresse, FILTER_VALIDATE_IP) !== false && inet_pton($adresse) === inet_pton($ip)) {
                    return new Decision(Motif::VerifieDns, $robot->identifiant);
                }
            }
        }
        return new Decision($domaineAdmis ? Motif::AdresseDifferente : Motif::DomaineRefuse);
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
