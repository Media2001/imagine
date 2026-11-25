<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Statut documentaire uniquement : aucun prix, abonnement ou droit d'accès. */
final class JustificatifRegles
{
    public const MAX = 5242880;

    public static function categories(mixed $value): array
    {
        $rows = is_string($value) ? preg_split('/\r?\n/', trim($value)) : $value;
        if (!is_array($rows) || count($rows) < 1 || count($rows) > 30) {
            throw new \InvalidArgumentException('Liste de catégories invalide.');
        }
        $out = [];
        foreach ($rows as $row) {
            if (!is_string($row) || trim($row) === '' || strlen($row) > 100
                || preg_match('/[<>\x00-\x1f]/', $row)) {
                throw new \InvalidArgumentException('Catégorie invalide.');
            }
            $out[] = trim($row);
        }
        return array_values(array_unique($out));
    }

    public static function depot(string $categorie, array $categories): array
    {
        if (!in_array($categorie, self::categories($categories), true)) {
            throw new \InvalidArgumentException('Catégorie inconnue.');
        }
        return ['categorie' => $categorie, 'decision' => 'en_attente'];
    }

    public static function mime(string $bytes): string
    {
        if ($bytes === '' || strlen($bytes) > self::MAX || preg_match('/<\?(?:php|=)|<script\b/i', $bytes)) {
            throw new \InvalidArgumentException('Fichier vide, trop volumineux ou exécutable.');
        }
        $mime = (new \finfo(FILEINFO_MIME_TYPE))->buffer($bytes);
        if ($mime === 'application/pdf' && str_starts_with($bytes, '%PDF-')
            && str_contains(substr($bytes, -2048), '%%EOF')
            && !preg_match('~/JavaScript\b|/JS\b|/Launch\b|/EmbeddedFile\b|/OpenAction\b|/AA\b~i', $bytes)) {
            return $mime;
        }
        if (in_array($mime, ['image/jpeg', 'image/png'], true)) {
            $image = @getimagesizefromstring($bytes);
            if ($image && ($image['mime'] ?? '') === $mime && $image[0] <= 12000 && $image[1] <= 12000) {
                return $mime;
            }
        }
        throw new \InvalidArgumentException('PDF, JPEG ou PNG non actif requis.');
    }

    public static function decider(array $pending, string $decision, string $fin, string $operateur, string $quand): array
    {
        if (($pending['decision'] ?? '') !== 'en_attente' || !in_array($decision, ['valide', 'refuse'], true)
            || $operateur === '') {
            throw new \InvalidArgumentException('Décision documentaire invalide.');
        }
        if ($decision === 'valide') {
            $date = \DateTimeImmutable::createFromFormat('!Y-m-d', $fin, new \DateTimeZone('UTC'));
            if (!$date || $date->format('Y-m-d') !== $fin || $fin < substr($quand, 0, 10)) {
                throw new \InvalidArgumentException('Date de fin invalide ou passée.');
            }
        }
        return ['categorie' => $pending['categorie'], 'decision' => $decision, 'date_decision' => $quand,
            'fin' => $decision === 'valide' ? $fin : '', 'operateur' => $operateur];
    }
}
