<?php

declare(strict_types=1);

/** Doubles de transport minimaux, confinés au processus PHPUnit séparé. */
class WC_Subscription
{
    public function has_status(array|string $status): bool { return in_array($this->get_status(), (array) $status, true); }
    public function get_status(): string { return $GLOBALS['b02_status'] ?? 'on-hold'; }
    public function get_id(): int { return 10; }
    public function get_customer_id(): int { return 20; }
    public function get_date(string $key, string $zone = ''): string { return $key === 'start' ? ($GLOBALS['b02_start'] ?? '2026-11-01 00:00:00') : ''; }
    public function get_meta(string $key): string { return ''; }
    public function get_payment_method(): string { return ''; }
    public function get_billing_period(): string { return 'month'; }
    public function get_billing_interval(): string { return '3'; }
    public function get_related_orders(string $return, string $type): array { return []; }
    public function get_parent_id(): int { return 0; }
    public function get_items(): array { return []; }
    public function get_total(): string { return '30.00'; }
    public function get_currency(): string { return 'EUR'; }
    public function get_requires_manual_renewal(): bool { return true; }
    public function get_view_order_url(): string { return '/view-subscription/10'; }
    public function get_address(string $kind): array { return []; }
}
function __(string $value, string $domain = ''): string { return $value; }
function get_current_user_id(): int { return 20; }
function wcs_get_users_subscriptions(int $id): array { return [new WC_Subscription()]; }
function get_posts(array $args): array { return []; }
function wc_get_order(int $id): bool { return false; }
function get_option(string $name, mixed $default = null): mixed { return $name === 'imagine_envoi_calendrier_reference' ? ($GLOBALS['b02_calendar'] ?? null) : $default; }
function add_query_arg(mixed ...$args): string { return '/edit-address'; }
function wc_get_endpoint_url(mixed ...$args): string { return '/edit-address'; }
function wc_get_page_permalink(string $page): string { return '/mon-compte'; }
function add_action(string $name, mixed ...$args): void { $GLOBALS['b02_hooks'][] = $name; }
function add_filter(string $name, mixed ...$args): void {}
function esc_attr__(string $value, string $domain = ''): string { return htmlspecialchars($value); }
function esc_html__(string $value, string $domain = ''): string { return htmlspecialchars($value); }
function esc_attr_e(string $value, string $domain = ''): void { echo htmlspecialchars($value); }
function esc_html_e(string $value, string $domain = ''): void { echo htmlspecialchars($value); }
function esc_attr(string $value): string { return htmlspecialchars($value); }
function esc_html(string $value): string { return htmlspecialchars($value); }
function esc_url(string $value): string { return htmlspecialchars($value); }
function wp_kses_post(string $value): string { return $value; }
function wc_price(mixed $value, array $args): string { return (string) $value; }
function WC(): object { return (object) ['countries' => new class { public function get_formatted_address(array $address): string { return 'Adresse fictive'; } }]; }
function wc_get_account_endpoint_url(string $endpoint): string { return '/' . $endpoint; }
