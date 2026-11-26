<?php

declare(strict_types=1);

// Loaded only inside isolated PHPUnit children, never in WordPress.
final class WC_Subscription
{
    public function __construct(private int $id, private string $status = 'on-hold')
    {
    }

    public function get_id(): int { return $this->id; }
    public function get_customer_id(): int { return $this->id; }
    public function get_status(): string { return $this->status; }
    public function has_status(string $status): bool { return $this->status === $status; }
    public function get_date(string $key, string $zone = 'gmt'): string { return ''; }
    public function get_time(string $key): int { return 0; }
    public function get_meta(string $key): string { return ''; }
    public function get_payment_method(): string { return 'bacs'; }
    public function get_items(): array { return []; }
    public function get_shipping_first_name(): string { return 'Fictif'; }
    public function get_shipping_last_name(): string { return 'Test'; }
    public function get_shipping_address_1(): string { return ''; }
    public function get_shipping_address_2(): string { return ''; }
    public function get_shipping_postcode(): string { return '1000'; }
    public function get_shipping_city(): string { return 'Ville fictive'; }
    public function get_shipping_country(): string { return 'BE'; }
}

function wcs_get_subscriptions(array $args): array
{
    $GLOBALS['c18_queries'][] = $args;
    if (count($GLOBALS['c18_queries']) > 4) {
        throw new LogicException('Pagination sans arrêt.');
    }
    return $GLOBALS['c18_pages'][$args['paged']] ?? [];
}

function get_userdata(int $id): object
{
    return (object) ['ID' => $id, 'first_name' => 'Fictif', 'last_name' => 'Test', 'user_email' => 'fictif@example.org'];
}

function get_user_meta(int $id, string $key, bool $single): string
{
    return '';
}

function __(string $text, string $domain): string
{
    return $domain === 'imagine-site' && ($GLOBALS['c18_translate'] ?? false) && $text === 'Actif' ? 'Active' : $text;
}
