<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

/** Le futur adaptateur impose un délai dur, retourne PTR/A/AAAA ou lève une exception. */
interface Dns
{
    /** @return list<string> */
    public function inverse(string $ip, int $delaiMs): array;

    /** @return list<string> */
    public function directe(string $nom, int $delaiMs): array;
}
