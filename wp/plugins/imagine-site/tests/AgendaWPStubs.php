<?php

declare(strict_types=1);

// Bouchons isolés en sous-processus PHPUnit : aucun WordPress ni transport live.
namespace {
    class WP_Error
    {
        public function __construct(public string $code = '', public string $message = '') {}
        public function get_error_code(): string { return $this->code; }
    }
    class WP_Post
    {
        public function __construct(public int $ID = 1, public string $post_type = 'imagine_evenement', public string $post_status = 'publish', public string $post_password = '', public string $post_content = 'Description fictive', public string $post_title = 'Événement fictif', public int $post_parent = 0) {}
    }
    class AgendaWPDB
    {
        public string $posts = 'wp_posts';
        public string $postmeta = 'wp_postmeta';
        public string $last_error = '';
        public bool $fail = false;
        public array $locks = [];
        public function prepare(string $sql, mixed ...$args): array { return [$sql, $args]; }
        public function get_var(array $query): int { $this->locks[] = $query[0]; return 1; }
        public function get_col(array $query): array
        {
            $this->last_error = $this->fail ? 'panne fictive' : '';
            if ($this->fail) { return []; }
            [$sql, $args] = $query;
            $ids = [];
            foreach ($GLOBALS['agenda_posts'] as $id => $p) {
                if ($p->post_type === $args[0] && get_post_meta($id, 'imagine_agenda_email', true) === $args[1]
                    && (!isset($args[2]) || $p->post_parent === $args[2])) { $ids[] = $id; }
            }
            sort($ids);
            return $ids;
        }
    }
    // Seule la surface de l'analyseur HTML utilisée par B05 est simulée.
    class WP_HTML_Tag_Processor
    {
        private \DOMDocument $dom;
        private array $links;
        private int $index = -1;
        public function __construct(string $html)
        {
            $this->dom = new \DOMDocument();
            $this->dom->loadHTML('<?xml encoding="UTF-8"><div id="agenda-root">' . $html . '</div>', LIBXML_NOERROR | LIBXML_NOWARNING);
            $this->links = iterator_to_array($this->dom->getElementsByTagName('a'));
        }
        public function next_tag(string $tag): bool { return isset($this->links[++$this->index]); }
        public function get_attribute(string $name): string { return $this->links[$this->index]->getAttribute($name); }
        public function set_attribute(string $name, string $value): void { $this->links[$this->index]->setAttribute($name, $value); }
        public function get_updated_html(): string
        {
            $root = $this->dom->getElementById('agenda-root'); $html = '';
            foreach ($root->childNodes as $node) { $html .= $this->dom->saveHTML($node); }
            return $html;
        }
    }
    function get_post(?int $id = null): ?WP_Post { return $GLOBALS['agenda_posts'][$id ?? $GLOBALS['agenda_current']] ?? null; }
    function get_post_type(): string { return get_post()?->post_type ?? ''; }
    function get_post_meta(int $id, string $key, bool $single = true): mixed { return $GLOBALS['agenda_meta'][$id][$key] ?? ''; }
    function wp_timezone(): \DateTimeZone { return new \DateTimeZone('UTC'); }
    function wp_strip_all_tags(string $html): string { return strip_tags(preg_replace('~<(script|style)\b[^>]*>.*?</\1>~is', '', $html)); }
    function home_url(string $path = ''): string { return 'https://demo.example.org' . $path; }
    function wp_parse_url(string $url, int $component = -1): mixed { return parse_url($url, $component); }
    function add_filter(string $name, mixed $callback, int $priority = 10, int $args = 1): void { $GLOBALS['agenda_hooks'][$name][$priority][] = $callback; }
    function add_action(string $name, mixed $callback, int $priority = 10, int $args = 1): void { add_filter($name, $callback, $priority, $args); }
    function apply_filters(string $name, mixed $value): mixed
    {
        $hooks = $GLOBALS['agenda_hooks'][$name] ?? []; ksort($hooks);
        foreach ($hooks as $callbacks) { foreach ($callbacks as $callback) { $value = $callback($value); } }
        return $value;
    }
    function __(string $text, string $domain): string { $GLOBALS['agenda_translations'][] = [$text, $domain]; return $text; }
    function esc_html(string $text): string { return htmlspecialchars($text, ENT_QUOTES, 'UTF-8'); }
    function esc_attr(string $text): string { return esc_html($text); }
    function esc_url(string $text): string { return esc_html($text); }
    function esc_html__(string $text, string $domain): string { return esc_html(__($text, $domain)); }
    function esc_html_e(string $text, string $domain): void { echo esc_html__($text, $domain); }
    function get_permalink(?int $id = null): string { return home_url('/evenement/' . ($id ?? $GLOBALS['agenda_current'])); }
    function get_the_title(int $id): string { return get_post($id)?->post_title ?? ''; }
    function is_email(string $email): bool { return filter_var($email, FILTER_VALIDATE_EMAIL) !== false; }
    function is_wp_error(mixed $value): bool { return $value instanceof WP_Error; }
    function sanitize_text_field(string $text): string { return trim(strip_tags($text)); }
    function wp_insert_post(array $data, bool $error = false): int
    {
        $id = max(array_keys($GLOBALS['agenda_posts'])) + 1;
        $GLOBALS['agenda_posts'][$id] = new WP_Post(ID: $id, post_type: $data['post_type'], post_status: $data['post_status'], post_parent: $data['post_parent']);
        $GLOBALS['agenda_meta'][$id] = $data['meta_input'];
        return $id;
    }
    function wp_delete_post(int $id, bool $force = false): bool { unset($GLOBALS['agenda_posts'][$id], $GLOBALS['agenda_meta'][$id]); return true; }
    function get_header(): void {}
    function get_footer(): void {}
    function have_posts(): bool { return $GLOBALS['agenda_loop']++ === 0; }
    function the_post(): void {}
    function get_the_ID(): int { return $GLOBALS['agenda_current']; }
    function the_title(): void { echo esc_html(get_post()->post_title); }
    function get_the_content(): string { return get_post()->post_content; }
    function the_content(): void { echo apply_filters('the_content', get_the_content()); }
    function get_post_type_archive_link(string $type): string { return home_url('/evenements/'); }
    function wp_json_encode(mixed $value, int $flags = 0): string { return json_encode($value, $flags); }
    function add_meta_box(string $id, string $label, callable $callback, string $type): void { $GLOBALS['agenda_boxes'][$id] = $callback; }
    function wp_nonce_field(string $action, string $name): void {}
    function selected(mixed $current, mixed $value, bool $echo = true): string { return $current === $value ? ' selected' : ''; }
    function current_user_can(string $cap): bool { return true; }
}
namespace Imagine\Site {
    function time(): int { return $GLOBALS['agenda_now']; }
}
