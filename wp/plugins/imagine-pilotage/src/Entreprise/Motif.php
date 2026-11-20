<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Entreprise;

/** Motifs stables de refus, issus du brief C-02 (§3.4). */
enum Motif: string
{
    case Vide = 'vide';
    case Longueur = 'longueur';
    case CaracteresInterdits = 'caracteres_interdits';
    case PremierChiffre = 'premier_chiffre';
    case CleIncorrecte = 'cle_incorrecte';

    public function message(): string
    {
        return match ($this) {
            self::Vide => 'Veuillez saisir votre numéro d’entreprise belge.',
            self::Longueur => 'Le numéro d’entreprise doit contenir 10 chiffres (ou 9 dans l’ancien format).',
            self::CaracteresInterdits => 'Utilisez uniquement des chiffres, des espaces, des points ou des tirets, '
                . 'avec BE en préfixe facultatif.',
            self::PremierChiffre => 'Le numéro d’entreprise belge doit commencer par 0 ou 1.',
            self::CleIncorrecte => 'La clé de contrôle du numéro d’entreprise est incorrecte. '
                . 'Vérifiez les chiffres saisis.',
        };
    }
}
