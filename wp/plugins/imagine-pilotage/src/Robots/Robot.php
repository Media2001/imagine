<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

final readonly class Robot
{
    /** @var list<Plage> */
    public array $reseaux;

    /** @param list<string> $agents @param list<string> $domaines @param list<string> $plages */
    public function __construct(
        public string $identifiant,
        public array $agents,
        public Methode $methode,
        public array $domaines = [],
        public array $plages = [],
        public ?\DateTimeImmutable $expirationPlages = null,
    ) {
        if (preg_match('/\A[a-z][a-z0-9_-]{0,63}\z/D', $identifiant) !== 1 || $agents === []) {
            throw new \InvalidArgumentException('Identifiant ou agents manquants.');
        }
        $vus = [];
        foreach ($agents as $agent) {
            if (!is_string($agent) || preg_match('/\A[a-zA-Z][a-zA-Z0-9_-]*\z/D', $agent) !== 1) {
                throw new \InvalidArgumentException('Jeton agent invalide.');
            }
            if (isset($vus[strtolower($agent)])) {
                throw new \InvalidArgumentException('Jeton agent dupliqué.');
            }
            $vus[strtolower($agent)] = true;
        }
        if ($methode === Methode::Dns && $domaines === []) {
            throw new \InvalidArgumentException('Un domaine est requis pour la méthode DNS.');
        }
        foreach ($domaines as $domaine) {
            if (
                !is_string($domaine) || strlen($domaine) > 253 || preg_match(
                    '/\A[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+\z/D',
                    $domaine,
                ) !== 1
            ) {
                throw new \InvalidArgumentException('Domaine autorisé invalide (ASCII minuscule sans joker).');
            }
        }
        $reseaux = [];
        foreach ($plages as $cidr) {
            if (!is_string($cidr)) {
                throw new \InvalidArgumentException('Plage non textuelle.');
            }
            $reseaux[] = new Plage($cidr);
        }
        $this->reseaux = $reseaux;
    }
}
