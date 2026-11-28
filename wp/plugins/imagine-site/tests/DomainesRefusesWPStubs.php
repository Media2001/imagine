<?php

declare(strict_types=1);

// Monde jetable, suivant ContactWPStubs, jamais chargé dans WordPress.
class WP_Error
{
    private array $errors = [];

    public function __construct(string $code = '', string $message = '', mixed $data = null)
    {
        if ($code !== '') {
            $this->add($code, $message);
        }
    }

    public function add(string $code, string $message): void
    {
        $this->errors[$code][] = $message;
    }

    public function get_error_codes(): array
    {
        return array_keys($this->errors);
    }

    public function has_errors(): bool
    {
        return $this->errors !== [];
    }

    public function get_error_message(): string
    {
        return $this->errors ? reset($this->errors)[0] : '';
    }
}

class WP_REST_Request
{
    public array $params = [];

    public function __construct(public string $method, public string $route)
    {
    }

    public function get_route(): string
    {
        return $this->route;
    }

    public function get_method(): string
    {
        return $this->method;
    }

    public function get_param(string $name): mixed
    {
        return $this->params[$name] ?? null;
    }
}

$GLOBALS['c31_options'] = [];
$GLOBALS['c31_hooks'] = [];
$GLOBALS['c31_users'] = [17 => (object) ['ID' => 17, 'user_email' => 'existant@jetable-fictif.example.org']];
$GLOBALS['c31_admin'] = false;
$GLOBALS['c31_cap'] = false;
$GLOBALS['c31_ajax'] = false;
$GLOBALS['c31_logged'] = false;
$GLOBALS['c31_required'] = false;
$GLOBALS['c31_fail_journal'] = false;
$GLOBALS['c31_settings_errors'] = [];

function __(string $text, string $domain): string
{
    return $text;
}
function get_option(string $key, mixed $default = false): mixed
{
    return $GLOBALS['c31_options'][$key] ?? $default;
}
function add_filter(string $hook, mixed $callback, int $priority = 10, int $args = 1): void
{
    $GLOBALS['c31_hooks'][$hook][] = [$callback, $priority, $args];
}
function add_action(string $hook, mixed $callback, int $priority = 10, int $args = 1): void
{
    add_filter($hook, $callback, $priority, $args);
}
function is_admin(): bool
{
    return $GLOBALS['c31_admin'];
}
function current_user_can(string $capability): bool
{
    return $GLOBALS['c31_cap'];
}
function wp_doing_ajax(): bool
{
    return $GLOBALS['c31_ajax'];
}
function is_user_logged_in(): bool
{
    return $GLOBALS['c31_logged'];
}
function get_userdata(int $id): object|false
{
    return $GLOBALS['c31_users'][$id] ?? false;
}
function WC(): object
{
    return new class {
        public function checkout(): object
        {
            return new class {
                public function is_registration_required(): bool
                {
                    return $GLOBALS['c31_required'];
                }
            };
        }
    };
}
function wp_get_current_user(): object
{
    return (object) ['ID' => 1, 'user_login' => 'operateur-fictif'];
}
function wp_generate_uuid4(): string
{
    static $id = 0;
    return 'fictif-' . ++$id;
}
function wp_cache_delete(string $key, string $group): void
{
}
function add_option(string $key, mixed $value, string $unused = '', bool $autoload = false): bool
{
    if ($GLOBALS['c31_fail_journal'] && str_starts_with($key, 'imagine_reglages_journal_')) {
        return false;
    }
    $GLOBALS['c31_options'][$key] = $value;
    foreach ($GLOBALS['c31_hooks']['added_option'] ?? [] as [$callback]) {
        $callback($key, $value);
    }
    return true;
}
function update_option(string $key, mixed $value, bool $autoload = false): bool
{
    $old = get_option($key, null);
    if ($old === $value) {
        return false;
    }
    // update_option ne déséchappe pas ses arguments (contrairement à update_metadata).
    $value = Imagine\Site\DomainesRefusesReglages::nettoyer($value);
    $GLOBALS['c31_options'][$key] = $value;
    foreach ($GLOBALS['c31_hooks']['updated_option'] ?? [] as [$callback]) {
        $callback($key, $old, $value);
    }
    return true;
}
function delete_option(string $key): bool
{
    unset($GLOBALS['c31_options'][$key]);
    return true;
}
function add_settings_error(mixed ...$args): void
{
    $GLOBALS['c31_settings_errors'][] = $args;
}
function wp_die(mixed ...$args): never
{
    throw new RuntimeException('wp_die');
}
