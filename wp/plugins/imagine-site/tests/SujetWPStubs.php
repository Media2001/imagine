<?php

declare(strict_types=1);

// Monde WordPress jetable uniquement, chargé en processus séparé.
class WP_Error
{
    public function __construct(public string $code = '', public string $message = '') {}
}
class SujetWPDB
{
    public string $posts = 'wp_posts';
    public string $postmeta = 'wp_postmeta';
    public string $last_error = '';
    public bool $fail = false;
    public function prepare(string $sql, mixed ...$args): array { return [$sql, $args]; }
    public function get_col(array $query): array
    {
        $this->last_error = $this->fail ? 'Panne fictive' : '';
        if ($this->fail) { return []; }
        [$sql, $args] = $query;
        $ids = [];
        foreach ($GLOBALS['b08_posts'] as $id => $p) {
            if ($p->post_type === $args[0] && get_post_meta($id, 'imagine_sujet_email', true) === $args[1]) { $ids[] = $id; }
        }
        sort($ids);
        return $ids;
    }
}
$GLOBALS['wpdb'] = new SujetWPDB();
$GLOBALS['b08_options'] = ['imagine_b08_pages' => ['cooperative' => 1, 'soutenir' => 2, 'sujet' => 3, 'enfants' => array_combine(array_keys(\Imagine\Site\CooperativeRegles::PAGES), range(10, 16))]];
$GLOBALS['b08_posts'] = [];
$GLOBALS['b08_meta'] = [];
$GLOBALS['b08_calls'] = ['mail' => 0, 'http' => 0];
function __(string $s, string $d): string { return $s; }
function esc_html(string $s): string { return htmlspecialchars($s, ENT_QUOTES, 'UTF-8'); }
function esc_attr(string $s): string { return esc_html($s); }
function esc_url(string $s): string { return esc_html($s); }
function get_option(string $k, mixed $d = false): mixed { return $GLOBALS['b08_options'][$k] ?? $d; }
function home_url(string $path = ''): string { return 'https://demo.example.org' . $path; }
function get_permalink(int $id): string { return 'https://demo.example.org/page/' . $id; }
function get_page_by_path(string $path): object { return (object)['ID' => $path === 'espace-cooperateurs' ? 90 : 91]; }
function admin_url(string $path = ''): string { return 'https://demo.example.org/wp-admin/' . $path; }
function wp_nonce_field(string $a, string $n): void { echo '<input name="' . $n . '" value="nonce">'; }
function wp_verify_nonce(string $n, string $a): bool { return $n === 'nonce'; }
function wp_unslash(string $s): string { return stripslashes($s); }
function sanitize_text_field(string $s): string { return trim(strip_tags($s)); }
function sanitize_textarea_field(string $s): string { return trim(strip_tags($s)); }
function is_email(string $s): bool { return filter_var($s, FILTER_VALIDATE_EMAIL) !== false; }
function is_wp_error(mixed $v): bool { return $v instanceof WP_Error; }
function wp_insert_post(array $row, bool $errors = false): int|WP_Error
{
    if ($GLOBALS['b08_fail_insert'] ?? false) { return new WP_Error('write'); }
    $id = count($GLOBALS['b08_posts']) + 100;
    $GLOBALS['b08_posts'][$id] = (object)(['ID' => $id] + $row);
    $GLOBALS['b08_meta'][$id] = ($GLOBALS['b08_fail_meta'] ?? false) ? [] : $row['meta_input'];
    return $id;
}
function get_post(int $id): ?object { return $GLOBALS['b08_posts'][$id] ?? null; }
function get_post_meta(int $id, string $key, bool $one = true): mixed { return $GLOBALS['b08_meta'][$id][$key] ?? ''; }
function wp_delete_post(int $id, bool $force = false): bool
{
    if ($GLOBALS['b08_fail_delete'] ?? false) { return false; }
    unset($GLOBALS['b08_posts'][$id], $GLOBALS['b08_meta'][$id]);
    return true;
}
function wp_mail(mixed ...$args): void { $GLOBALS['b08_calls']['mail']++; }
function wp_remote_get(mixed ...$args): void { $GLOBALS['b08_calls']['http']++; }
function add_action(string $name, mixed $fn, int $priority = 10, int $args = 1): void { $GLOBALS['b08_hooks'][$name][] = $fn; }
function add_filter(string $name, mixed $fn, int $priority = 10, int $args = 1): void { add_action($name, $fn, $priority, $args); }
function register_post_type(string $name, array $args): void { $GLOBALS['b08_types'][$name] = $args; }
function current_user_can(string $cap): bool { return $GLOBALS['b08_admin'] ?? true; }
function add_settings_error(mixed ...$args): void {}
function checked(mixed $a, mixed $b = true, bool $echo = true): string { return $a === $b ? ' checked' : ''; }
function get_privacy_policy_url(): string { return 'https://demo.example.org/privacy/'; }
