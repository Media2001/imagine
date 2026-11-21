<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use DateTimeImmutable;
use DateTimeZone;
use InvalidArgumentException;

final readonly class Event
{
    public DateTimeImmutable $occurredAt;

    public array $content;

    public function __construct(
        public EventType $type,
        public string $sourceId,
        DateTimeImmutable $occurredAt,
        array $content,
        public ?string $subscriptionId = null
    ) {
        if (trim($sourceId) === '' || ($subscriptionId !== null && trim($subscriptionId) === '')) {
            throw new InvalidArgumentException('Identifiant d’origine ou d’abonnement vide.');
        }
        $content = self::snapshot($content);
        $this->occurredAt = $occurredAt->setTimezone(new DateTimeZone('Europe/Brussels'));
        self::whitelist($content, [
            'identity', 'address', 'lines', 'total_minor', 'currency', 'payment_method',
            'enterprise_number', 'payment_reference',
        ]);
        $nested = [
            'identity' => ['name', 'email'],
            'address' => ['street', 'postal_code', 'city', 'country'],
        ];
        foreach ($nested as $key => $keys) {
            if (isset($content[$key]) && is_array($content[$key])) {
                self::whitelist($content[$key], $keys);
            }
        }
        if (isset($content['lines']) && is_array($content['lines'])) {
            foreach ($content['lines'] as $line) {
                if (is_array($line)) {
                    self::whitelist($line, ['product', 'amount_minor']);
                }
            }
        }
        // Unknown keys and nested values never become part of an event.
        self::scalarsOnly($content);
        $this->content = $content;
    }

    private static function snapshot(array $values, int $depth = 0): array
    {
        if ($depth > 2) {
            throw new InvalidArgumentException('Valeur imbriquée non autorisée.');
        }
        $copy = [];
        foreach ($values as $key => $value) {
            if (!is_array($value) && !is_scalar($value) && $value !== null) {
                throw new InvalidArgumentException('Valeur non autorisée.');
            }
            $copy[$key] = is_array($value) ? self::snapshot($value, $depth + 1) : $value;
        }
        return $copy;
    }

    public function key(): string
    {
        return hash('sha256', json_encode([$this->type->value, $this->sourceId], JSON_THROW_ON_ERROR));
    }

    private static function whitelist(array $values, array $keys): void
    {
        if (array_diff(array_keys($values), $keys) !== []) {
            throw new InvalidArgumentException('Champ non autorisé dans les données de facturation.');
        }
    }

    private static function scalarsOnly(array $content): void
    {
        foreach ($content as $key => $value) {
            if (in_array($key, ['identity', 'address', 'lines'], true) && is_array($value)) {
                foreach ($value as $child) {
                    if ($key === 'lines' && is_array($child)) {
                        foreach ($child as $cell) {
                            if (!is_scalar($cell) && $cell !== null) {
                                throw new InvalidArgumentException('Valeur imbriquée non autorisée.');
                            }
                        }
                    } elseif (!is_scalar($child) && $child !== null) {
                        throw new InvalidArgumentException('Valeur imbriquée non autorisée.');
                    }
                }
            } elseif (!is_scalar($value) && $value !== null) {
                throw new InvalidArgumentException('Valeur non autorisée.');
            }
        }
    }
}
