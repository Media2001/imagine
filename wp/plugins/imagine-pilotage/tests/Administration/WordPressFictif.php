<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Administration {
    /** Contrat Settings API ; les nonces réels restent couverts par la recette HTTP. */
    final class WordPressFictif
    {
        public static array $options = [];
        public static array $hooks = [];
        public static array $errors = [];
        public static array $settings = [];
        public static array $calls = [];
        public static bool $autorise = true;
        public static bool $journalKo = false;
        public static array $persistedAtJournal = [];
    }
}

namespace {
    use Imagine\Pilotage\Tests\Administration\WordPressFictif as Banc;

    function add_action(string $hook, callable $callback, int $priority = 10, int $args = 1): void
    {
        Banc::$hooks[$hook][] = [$callback, $args];
    }

    function add_filter(string $hook, callable $callback, int $priority = 10, int $args = 1): void
    {
        add_action($hook, $callback, $priority, $args);
    }

    function do_action(string $hook, mixed ...$args): void
    {
        foreach (Banc::$hooks[$hook] ?? [] as [$callback, $count]) {
            $callback(...array_slice($args, 0, $count));
        }
    }

    function get_option(string $name, mixed $default = false): mixed
    {
        return Banc::$options[$name] ?? Banc::$settings[$name]['default'] ?? $default;
    }

    function update_option(string $name, mixed $value): bool
    {
        $old = get_option($name);
        if ($old === $value) {
            return false;
        }
        if (!array_key_exists($name, Banc::$options)) {
            return add_option($name, $value);
        }
        Banc::$options[$name] = $value;
        do_action('updated_option', $name, $old, $value);
        return true;
    }

    function add_option(string $name, mixed $value, string $deprecated = '', mixed $autoload = null): bool
    {
        if (str_starts_with($name, 'imagine_reglages_journal_')) {
            Banc::$persistedAtJournal[] = get_option($value['option']);
            if (Banc::$journalKo) {
                return false;
            }
        }
        if (array_key_exists($name, Banc::$options)) {
            return false;
        }
        Banc::$options[$name] = $value;
        do_action('added_option', $name, $value);
        return true;
    }

    function delete_option(string $name): bool
    {
        unset(Banc::$options[$name]);
        return true;
    }

    function register_setting(string $group, string $name, array $args): void
    {
        Banc::$settings[$name] = ['group' => $group] + $args;
    }

    function add_settings_error(string $name, string $code, string $message): void
    {
        Banc::$errors[] = [$name, $code, $message];
    }

    function __(string $text, string $domain): string
    {
        return $text;
    }

    function current_user_can(string $cap): bool
    {
        Banc::$calls['cap'] = $cap;
        return Banc::$autorise;
    }

    function wp_die(string $message, string $title = '', array $args = []): never
    {
        throw new RuntimeException($message, $args['response'] ?? 0);
    }

    function wp_get_current_user(): object
    {
        return (object) ['ID' => 7, 'user_login' => 'admin-fictif'];
    }

    function wp_generate_uuid4(): string
    {
        static $id = 0;
        return 'event-' . ++$id;
    }

    function esc_html(string $text): string
    {
        return htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
    }

    function esc_attr(string $text): string
    {
        return esc_html($text);
    }

    function esc_textarea(string $text): string
    {
        return esc_html($text);
    }

    function selected(mixed $value, mixed $choice, bool $echo = true): string
    {
        return $value === $choice ? ' selected="selected"' : '';
    }

    function settings_errors(): void
    {
    }

    function settings_fields(string $group): void
    {
        Banc::$calls['nonce_group'] = $group;
    }

    function submit_button(string $text): void
    {
    }

    function wp_get_environment_type(): string
    {
        return 'test';
    }

    function maybe_unserialize(mixed $value): mixed
    {
        return $value;
    }
}
