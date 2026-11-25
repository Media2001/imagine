<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Validation pure de la saisie, pas de calcul de droits ou de tarifs. */
final class CommandeRegles
{
    public static function texte(array $data, string $key, int $max = 200): string
    {
        $value = $data[$key] ?? '';
        if (!is_string($value) || strlen($value) > $max || preg_match('/[\x00-\x1f\x7f]/', $value)) {
            throw new \InvalidArgumentException('Champ invalide : ' . $key);
        }
        return trim(strip_tags($value));
    }

    public static function id(array $data, string $key): int
    {
        $value = self::texte($data, $key, 10);
        if (!preg_match('/^[1-9][0-9]{0,9}$/D', $value)) {
            throw new \InvalidArgumentException('Identifiant invalide.');
        }
        return (int) $value;
    }

    public static function client(array $data): array
    {
        $mode = self::texte($data, 'mode');
        if ($mode === 'existant') {
            return ['mode' => $mode, 'id' => self::id($data, 'client')];
        }
        if ($mode === 'direct') {
            return ['mode' => $mode];
        }
        if ($mode !== 'nouveau') {
            throw new \InvalidArgumentException('Client invalide.');
        }
        $nom = self::texte($data, 'nom');
        $sans = ($data['sans_email'] ?? '') === '1';
        $email = $sans ? '' : strtolower(self::texte($data, 'email', 254));
        if ($nom === '' || (!$sans && (!filter_var($email, FILTER_VALIDATE_EMAIL) || str_ends_with($email, '.invalid')))) {
            throw new \InvalidArgumentException('Nom et adresse électronique valides requis, ou sans email.');
        }
        return ['mode' => $mode, 'nom' => $nom, 'email' => $email, 'sans_email' => $sans];
    }

    public static function commande(array $data, bool $direct): array
    {
        $paiement = self::texte($data, 'paiement');
        if (!in_array($paiement, ['bacs', 'imagine_papier'], true)) {
            throw new \InvalidArgumentException('Paiement hors ligne requis.');
        }
        $address = [];
        foreach (['first_name', 'last_name', 'address_1', 'address_2', 'postcode', 'city', 'country'] as $field) {
            $address[$field] = self::texte($data, $field);
            if (!$direct && $address[$field] === '' && $field !== 'address_2') {
                throw new \InvalidArgumentException('Adresse de livraison incomplète.');
            }
        }
        if ($address['country'] !== '' && !preg_match('/^[A-Z]{2}$/D', $address['country'])) {
            throw new \InvalidArgumentException('Pays invalide.');
        }
        return ['produit' => self::id($data, 'produit'), 'paiement' => $paiement, 'adresse' => $address];
    }
}
