<?php

declare(strict_types=1);

namespace Imagine\Theme;

/** Présentation pure de la décision C06/C08, jamais un calcul de droits. */
function imagine_access_status(array $decision): array
{
    $code = 'reserve';
    if (($decision['complet'] ?? false) === true) {
        $code = match ($decision['motif'] ?? '') {
            'contenu_ouvert' => 'libre',
            'decouverte_duree', 'decouverte_articles' => 'decouverte',
            default => 'ouvert',
        };
    }
    $label = match ($code) {
        'libre' => __('Libre', 'imagine'),
        'decouverte' => __('Découverte', 'imagine'),
        'ouvert' => __('Ouvert pour vous', 'imagine'),
        default => __('Réservé', 'imagine'),
    };
    return ['code' => $code, 'label' => $label];
}
