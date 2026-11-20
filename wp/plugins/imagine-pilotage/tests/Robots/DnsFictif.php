<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Robots;

use Imagine\Pilotage\Robots\Dns;
use Throwable;

final class DnsFictif implements Dns
{
    public array $noms = ['crawl-fictif.googlebot.com'];
    public array $adresses = ['192.0.2.1'];
    public array $appels = [];
    public ?Throwable $panne = null;
    public int $latence = 0;

    public function __construct(public HorlogeFictive $horloge = new HorlogeFictive())
    {
    }

    public function inverse(string $ip, int $delaiMs): array
    {
        $this->appels[] = ['inverse', $ip, $delaiMs];
        $this->horloge->temps += $this->latence;
        if ($this->panne !== null) {
            throw $this->panne;
        }
        return $this->noms;
    }

    public function directe(string $nom, int $delaiMs): array
    {
        $this->appels[] = ['directe', $nom, $delaiMs];
        $this->horloge->temps += $this->latence;
        if ($this->panne !== null) {
            throw $this->panne;
        }
        return $this->adresses;
    }
}
