<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Envoi;

use Imagine\Connecteur\CsvProtection;

final class ExportCsv
{
    public const COLONNES = [
        'abonnement_id', 'destinataire_id', 'destinataire', 'rue', 'complement',
        'code_postal', 'ville', 'pays', 'origine',
    ];

    public static function liste(ListeEnvoi $liste, bool $anomaliesRevues = false): string
    {
        if ($liste->anomalies !== [] && !$anomaliesRevues) {
            throw new \LogicException('Anomalies à traiter avant de transmettre la liste au routeur.');
        }
        return self::lignes($liste->lignes);
    }

    /** @param list<array<string, string>> $lignes */
    public static function lignes(array $lignes, ?FormatExport $format = null): string
    {
        $colonnes = ($format ?? new FormatExport())->colonnes;
        $stream = fopen('php://memory', 'w+b');
        fputcsv($stream, $colonnes, escape: '', eol: "\n");
        foreach ($lignes as $ligne) {
            $valeurs = [];
            foreach ($colonnes as $colonne) {
                $valeurs[] = CsvProtection::cellule($ligne[$colonne]);
            }
            fputcsv($stream, $valeurs, escape: '', eol: "\n");
        }
        rewind($stream);
        $bytes = stream_get_contents($stream);
        fclose($stream);
        return $bytes;
    }
}
