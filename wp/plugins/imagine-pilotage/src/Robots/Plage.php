<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

use InvalidArgumentException;

/** Comparaison binaire CIDR, sans dépendance réseau ni conversion IPv6 vers IPv4. */
final readonly class Plage
{
    private string $reseau;
    private int $prefixe;

    public function __construct(public string $cidr)
    {
        $parties = explode('/', $cidr);
        if (
            count($parties) !== 2 || filter_var($parties[0], FILTER_VALIDATE_IP) === false
            || preg_match('/\A(?:0|[1-9][0-9]{0,2})\z/D', $parties[1]) !== 1
        ) {
            throw new InvalidArgumentException('Plage CIDR invalide.');
        }
        $this->reseau = inet_pton($parties[0]);
        $this->prefixe = (int) $parties[1];
        if ($this->prefixe > strlen($this->reseau) * 8) {
            throw new InvalidArgumentException('Préfixe CIDR trop grand.');
        }
    }

    public function contient(string $ip): bool
    {
        if (filter_var($ip, FILTER_VALIDATE_IP) === false) {
            return false;
        }
        $adresse = inet_pton($ip);
        if (strlen($adresse) !== strlen($this->reseau)) {
            return false;
        }
        $octets = intdiv($this->prefixe, 8);
        if (substr($adresse, 0, $octets) !== substr($this->reseau, 0, $octets)) {
            return false;
        }
        $reste = $this->prefixe % 8;
        if ($reste === 0) {
            return true;
        }
        $masque = (0xff << (8 - $reste)) & 0xff;
        return (ord($adresse[$octets]) & $masque) === (ord($this->reseau[$octets]) & $masque);
    }
}
