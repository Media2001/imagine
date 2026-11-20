<?php

declare(strict_types=1);

namespace Imagine\Connecteur;

use Closure;
use InvalidArgumentException;

final readonly class Validator
{
    /** @param list<Rule> $rules */
    public function __construct(private array $rules)
    {
        $names = [];
        foreach ($rules as $rule) {
            if (!$rule instanceof Rule || isset($names[$rule->name()])) {
                throw new InvalidArgumentException('Règles non valides ou noms dupliqués.');
            }
            $names[$rule->name()] = true;
        }
    }

    public function with(Rule $rule): self
    {
        return new self([...$this->rules, $rule]);
    }

    /** @return list<Violation> */
    public function validate(Event $event): array
    {
        $violations = [];
        foreach ($this->rules as $rule) {
            $message = $rule->check($event);
            if ($message !== null) {
                $violations[] = new Violation($rule->name(), $message);
            }
        }
        return $violations;
    }

    /** No accounting vocabulary is assumed: payment identifiers come from the adapter. */
    public static function billing(array $knownPayments, ?callable $enterpriseValidator = null): self
    {
        $enterprise = $enterpriseValidator === null ? null : Closure::fromCallable($enterpriseValidator);
        return new self([
            new NamedRule('identity', static function (Event $event): ?string {
                return self::text($event->content['identity']['name'] ?? null)
                    ? null : 'L’identité de facturation est obligatoire.';
            }),
            new NamedRule('address', static function (Event $event): ?string {
                foreach (['street', 'postal_code', 'city', 'country'] as $field) {
                    if (!self::text($event->content['address'][$field] ?? null)) {
                        return 'L’adresse de facturation est incomplète.';
                    }
                }
                return null;
            }),
            new NamedRule('amounts', static fn (Event $event): ?string => self::amounts($event)),
            new NamedRule('payment_method', static function (Event $event) use ($knownPayments): ?string {
                return in_array($event->content['payment_method'] ?? null, $knownPayments, true)
                    ? null : 'Le mode de paiement n’est pas reconnu.';
            }),
            new NamedRule('enterprise_number', static function (Event $event) use ($enterprise): ?string {
                $number = $event->content['enterprise_number'] ?? null;
                if ($number === null || $number === '') {
                    return null;
                }
                if (!is_string($number) || $enterprise === null) {
                    return 'Contrôle du numéro d’entreprise indisponible ou valeur non valide.';
                }
                return $enterprise($number) ? null : 'Le numéro d’entreprise n’est pas valide.';
            }),
        ]);
    }

    private static function text(mixed $value): bool
    {
        return is_string($value) && trim($value) !== '';
    }

    private static function amounts(Event $event): ?string
    {
        $content = $event->content;
        $lines = $content['lines'] ?? null;
        $total = $content['total_minor'] ?? null;
        $currency = $content['currency'] ?? null;
        if (
            !is_array($lines) || !array_is_list($lines) || $lines === [] || !is_int($total)
            || !is_string($currency) || preg_match('/^[A-Z]{3}$/D', $currency) !== 1
        ) {
            return 'Lignes, devise ou montant total non valides.';
        }
        $sum = 0;
        foreach ($lines as $line) {
            $amount = is_array($line) ? ($line['amount_minor'] ?? null) : null;
            if (!is_int($amount) || !self::text($line['product'] ?? null)) {
                return 'Chaque ligne exige un produit et un montant entier en unité mineure.';
            }
            if (
                ($amount > 0 && $sum > PHP_INT_MAX - $amount)
                || ($amount < 0 && $sum < PHP_INT_MIN - $amount)
            ) {
                return 'La somme des montants dépasse les limites de calcul.';
            }
            $sum += $amount;
        }
        return $sum === $total ? null : 'La somme des lignes ne correspond pas au total.';
    }
}
