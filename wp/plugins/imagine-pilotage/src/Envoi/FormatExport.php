<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Envoi;

/** Sélection ordonnée des champs existants ; les neuf colonnes provisoires restent le défaut. */
final readonly class FormatExport
{
    /** @param list<string> $colonnes */
    public function __construct(public array $colonnes = ExportCsv::COLONNES)
    {
        if ($colonnes === [] || !array_is_list($colonnes)) {
            throw new \InvalidArgumentException('Choisir au moins une colonne dans une liste ordonnée.');
        }
        $vues = [];
        foreach ($colonnes as $colonne) {
            if (!is_string($colonne) || !in_array($colonne, ExportCsv::COLONNES, true) || isset($vues[$colonne])) {
                throw new \InvalidArgumentException('Colonne inconnue ou répétée dans le format d’export.');
            }
            $vues[$colonne] = true;
        }
    }
}
