<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

trait PerimetreDecouverte
{
    private function perimetreValide(): bool
    {
        if (!is_bool($this->pdf) || !is_array($this->numeros) || !array_is_list($this->numeros)) {
            return false;
        }
        $vus = [];
        foreach ($this->numeros as $numero) {
            if (
                !is_string($numero) || $numero === '' || preg_match('/[\x00-\x20\x7f]/', $numero) !== 0
                || in_array($numero, $vus, true)
            ) {
                return false;
            }
            $vus[] = $numero;
        }
        return true;
    }

    private function prerequis(array $contenu, array $droit, \DateTimeImmutable $instant): ?Motif
    {
        if (!$droit['compte_verifie']) {
            return Motif::CompteNonVerifie;
        }
        if ($instant < $droit['debut']) {
            return Motif::DecouvertePasCommencee;
        }
        if (
            !$contenu['decouverte'] || !in_array($contenu['numero'], $this->numeros, true)
            || ($contenu['type'] === 'pdf' && !$this->pdf)
        ) {
            return Motif::DecouverteHorsPerimetre;
        }
        return null;
    }
}
