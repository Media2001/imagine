<?php

declare(strict_types=1);

namespace Imagine\ContentInventory;

use Imagine\Audit\Audit;

/** Observe real API calls before bootstrap, then enumerate the final native objects. */
final class Registry
{
    private array $events = ['post_types' => [], 'taxonomies' => []];

    public function __construct(private string $site)
    {
    }

    public static function origin(string $site, ?string $file): array
    {
        $unknown = ['owner' => 'unknown', 'file' => null];
        if ($file === null || !str_starts_with($file, $site . '/') || !is_readable($file)) {
            return $unknown;
        }
        $relative = substr($file, strlen($site) + 1);
        if (Audit::identifier($relative) === '[masque]') {
            return $unknown;
        }
        $owner = match (true) {
            str_starts_with($relative, 'wp-includes/'), str_starts_with($relative, 'wp-admin/') => 'core',
            str_starts_with($relative, 'wp-content/themes/') => 'theme',
            str_starts_with($relative, 'wp-content/mu-plugins/') => 'mu_plugin',
            str_starts_with($relative, 'wp-content/plugins/') => 'plugin',
            default => 'unknown',
        };
        return ['owner' => $owner, 'file' => $relative];
    }

    private function record(string $kind, string $name, ?object $object, string $function): void
    {
        $file = null;
        foreach (debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS) as $frame) {
            if (($frame['function'] ?? '') === $function && !isset($frame['class'])) {
                $file = $frame['file'] ?? null;
                break;
            }
        }
        $this->events[$kind][$name] = ['object' => $object, 'origin' => self::origin($this->site, $file)];
    }

    public function listen(): void
    {
        $post = function (string $name, object $object): void {
            $this->record('post_types', $name, $object, 'register_post_type');
        };
        $taxonomy = function (string $name): void {
            $this->record('taxonomies', $name, $GLOBALS['wp_taxonomies'][$name] ?? null, 'register_taxonomy');
        };
        // Native WP_Hook::build_preinitialized_hooks normalizes these at plugin.php.
        // Do not load ANY site PHP before the A11 runtime's source safety checks.
        $GLOBALS['wp_filter']['registered_post_type'][PHP_INT_MAX][] = ['function' => $post, 'accepted_args' => 2];
        $GLOBALS['wp_filter']['registered_taxonomy'][PHP_INT_MAX][] = ['function' => $taxonomy, 'accepted_args' => 1];
    }

    public function snapshot(): array
    {
        $result = ['post_types' => [], 'taxonomies' => []];
        $native = ['post_types' => get_post_types([], 'objects'), 'taxonomies' => get_taxonomies([], 'objects')];
        foreach ($native as $kind => $objects) {
            foreach ($objects as $name => $object) {
                $event = $this->events[$kind][$name] ?? null;
                $result[$kind][$name] = [$event && $event['object'] === $object
                    ? $event['origin'] : ['owner' => 'unknown', 'file' => null]];
            }
            ksort($result[$kind]);
        }
        return $result;
    }
}
