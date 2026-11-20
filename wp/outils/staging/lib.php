<?php

declare(strict_types=1);

namespace Imagine\Staging;

use RuntimeException;

interface Store
{
    public function database(): string;
    /** Toutes les tables de la base, pas seulement le préfixe WordPress. */
    public function schema(): array;
    public function rows(string $table): array;
    public function begin(): void;
    public function commit(): void;
    public function rollback(): void;
    /** Compare-and-swap : échec si la ligne originale a changé. null supprime. */
    public function replace(string $table, array $before, ?array $after): void;
    public function insert(string $table, array $row): int;
}

final class Engine
{
    private string $target;
    private array $inventory;
    public function __construct(private Store $store, private array $context, private string $prefix)
    {
        $this->target = Guard::context($context);
        if (!preg_match('/^[a-zA-Z0-9_]+_$/D', $prefix) || $store->database() !== $context['database']) {
            throw new RuntimeException('BASE_REFUSEE');
        }
        $catalogue = require __DIR__ . '/schema.php';
        $this->inventory = $store->schema();
        foreach ($this->inventory as $table => $columns) {
            $name = str_starts_with($table, $prefix) ? substr($table, strlen($prefix)) : '';
            if (!isset($catalogue[$name]) || !$columns
                || array_diff($columns, explode(' ', $catalogue[$name]))) {
                throw new RuntimeException('SCHEMA_INCONNU');
            }
        }
        foreach (['options', 'users', 'usermeta', 'posts', 'postmeta', 'comments'] as $required) {
            if (!isset($this->inventory[$prefix . $required])) {
                throw new RuntimeException('SCHEMA_INCOMPLET');
            }
        }
        $urls = $this->options();
        foreach (['home', 'siteurl'] as $key) {
            if (!isset($urls[$key])) {
                throw new RuntimeException('URL_ABSENTE');
            }
            // Une copie encore à l'adresse de production est refusée AVANT toute écriture.
            Guard::context(array_replace($context, ['target_url' => $urls[$key]]));
        }
        foreach ($store->rows($prefix . 'posts') as $post) {
            if (!in_array($post['post_type'] ?? '', ['post', 'page', 'attachment', 'revision', 'nav_menu_item', 'custom_css', 'customize_changeset', 'oembed_cache', 'wp_block', 'wp_template', 'wp_template_part', 'wp_global_styles', 'wp_navigation', 'wp_font_family', 'wp_font_face', 'shop_order', 'shop_order_placehold', 'shop_order_refund', 'shop_subscription', 'shop_coupon', 'product', 'product_variation', 'wc_membership_plan', 'wc_user_membership'], true)) {
                throw new RuntimeException('TYPE_CONTENU_INCONNU');
            }
        }
    }

    private function options(): array
    {
        $options = [];
        foreach ($this->store->rows($this->prefix . 'options') as $row) {
            if (isset($options[$row['option_name']])) {
                throw new RuntimeException('OPTION_DUPLIQUEE');
            }
            $options[$row['option_name']] = $row['option_value'];
        }
        return $options;
    }

    public static function dangerous(string $value): bool
    {
        return (bool) preg_match('/(?:[spr]k_live|whsec|xkeysib|cus|pm|src|seti|pi|ch|tok|ba)_[a-z0-9_-]+|B-[A-Z0-9]{6,}/i', $value);
    }

    private static function decode(string $value): mixed
    {
        if (preg_match('/^(?:O|C|R|r):/', $value)) {
            throw new RuntimeException('SERIALISATION_REFUSEE');
        }
        if (preg_match('/^(?:a|s|i|b|d):|^N;/', $value)) {
            if (preg_match('/(?:^|[;{}])(?:O|C|R|r):[0-9]+/', $value)) {
                throw new RuntimeException('SERIALISATION_REFUSEE');
            }
            set_error_handler(static function (): never {
                throw new RuntimeException('SERIALISATION_INVALIDE');
            });
            try {
                $decoded = unserialize($value, ['allowed_classes' => false, 'max_depth' => 32]);
            } finally {
                restore_error_handler();
            }
            if (is_object($decoded)) {
                throw new RuntimeException('OBJET_REFUSE');
            }
            return $decoded;
        }
        return $value;
    }

    private static function scrub(mixed $value, bool $privacy, int $id, int $depth = 0): mixed
    {
        if ($depth > 32 || is_object($value) || is_resource($value)) {
            throw new RuntimeException('STRUCTURE_REFUSEE');
        }
        if (is_array($value)) {
            $clean = [];
            foreach ($value as $key => $child) {
                if (is_string($key) && (self::sensitiveKey($key) || ($privacy && self::piiKey($key)))) {
                    $clean[$key] = '';
                    continue;
                }
                $clean[$key] = self::scrub($child, $privacy, $id, $depth + 1);
            }
            return $clean;
        }
        if (!is_string($value)) {
            return $value;
        }
        $decoded = self::decode($value);
        if ($decoded !== $value) {
            return serialize(self::scrub($decoded, $privacy, $id, $depth + 1));
        }
        if (str_starts_with($value, '{') || str_starts_with($value, '[')) {
            $json = json_decode($value, false, 32, JSON_THROW_ON_ERROR);
            return json_encode(self::scrubJson($json, $privacy, $id, $depth + 1), JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        }
        if (self::dangerous($value)) {
            return '';
        }
        if ($privacy) {
            $value = preg_replace('/[A-Z0-9.!#$%&\x27*+\/=?^_`{|}~-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i', "abonne-$id@example.org", $value) ?? '';
            $value = preg_replace_callback('/(?<![0-9a-f:.])[0-9a-f:.]*[.:][0-9a-f:.]+(?![0-9a-f:.])/i', static fn (array $m): string => filter_var($m[0], FILTER_VALIDATE_IP) !== false ? '' : $m[0], $value) ?? '';
        }
        return $value;
    }

    /** Les seuls objets acceptés ici viennent de json_decode, jamais de unserialize. */
    private static function scrubJson(mixed $value, bool $privacy, int $id, int $depth): mixed
    {
        if ($depth > 32) {
            throw new RuntimeException('STRUCTURE_REFUSEE');
        }
        if ($value instanceof \stdClass) {
            $clean = new \stdClass();
            foreach (get_object_vars($value) as $key => $child) {
                $clean->{$key} = self::sensitiveKey((string) $key) || ($privacy && self::piiKey((string) $key))
                    ? '' : self::scrubJson($child, $privacy, $id, $depth + 1);
            }
            return $clean;
        }
        if (is_array($value)) {
            return array_map(static fn (mixed $child): mixed => self::scrubJson($child, $privacy, $id, $depth + 1), $value);
        }
        return self::scrub($value, $privacy, $id, $depth + 1);
    }

    private static function sensitiveKey(string $key): bool
    {
        return (bool) preg_match('/secret|api.?key|(?:access|private|public)_?key|password|token|nonce|session|application_password|stripe|paypal|brevo|sendinblue|smtp|webhook|merchant|mandate|transaction_id|billing_agreement|payer_id|client_id|authorization|payment_method_id|source_id|intent_id/i', $key);
    }

    private static function piiKey(string $key): bool
    {
        return (bool) preg_match('/(?:^|_)(first_name|last_name|full_name|billing_name|shipping_name|company|address_?[12]?|city|postcode|state|phone|vat|tax_id|company_number|business_number|siret|iban|bic|nickname|ip_address|user_agent|customer_note|order_key|cart_hash|shipping_packages)(?:$|_)/i', $key);
    }

    private function transform(bool $privacy): void
    {
        foreach ($this->inventory as $table => $_) {
            $kind = substr($table, strlen($this->prefix));
            foreach ($this->store->rows($table) as $row) {
                if ($kind === 'actionscheduler_actions' && in_array($row['status'], ['complete', 'failed'], true)) {
                    $this->store->replace($table, $row, null);
                    continue;
                }
                if (in_array($kind, ['woocommerce_payment_tokens', 'woocommerce_payment_tokenmeta', 'woocommerce_sessions', 'woocommerce_api_keys', 'actionscheduler_logs', 'actionscheduler_claims', 'woocommerce_log', 'wc_download_log', 'wc_rate_limits'], true)
                    || ($privacy && $kind === 'commentmeta')) {
                    $this->store->replace($table, $row, null);
                    continue;
                }
                if ($kind === 'options') {
                    $key = $row['option_name'];
                    if (!$this->allowedOption($key)) {
                        $this->store->replace($table, $row, null);
                        continue;
                    }
                }
                if (isset($row['meta_key']) && self::sensitiveKey($row['meta_key'])) {
                    $this->store->replace($table, $row, null);
                    continue;
                }
                $next = $row;
                $id = (int) ($row['ID'] ?? $row['user_id'] ?? $row['order_id'] ?? $row['id'] ?? $row['comment_ID'] ?? 0);
                foreach ($next as $key => $value) {
                    if ($kind === 'actionscheduler_actions' && in_array($key, ['schedule', 'args', 'extended_args'], true)) {
                        $next[$key] = match ($key) {
                            'args' => '[]', 'extended_args' => null, default => ''
                        };
                        continue; // Charges opaques destinées à être détruites, jamais désérialisées.
                    }
                    $next[$key] = self::scrub($value, $privacy, $id);
                    if ($privacy && ((in_array($kind, ['wc_order_addresses', 'wc_orders', 'wc_customer_lookup', 'wc_order_operational_data'], true) && self::piiKey($key)) || ($key === 'meta_value' && self::piiKey($row['meta_key'] ?? '')))) {
                        $next[$key] = '';
                    }
                }
                if ($kind === 'options') {
                    $next['option_value'] = match ($row['option_name']) {
                        'home', 'siteurl' => $this->target,
                        'blog_public' => '0', 'cron' => serialize([]),
                        'active_plugins' => serialize(array_values(array_intersect((array) self::decode($row['option_value']), ['woocommerce/woocommerce.php', 'woocommerce-subscriptions/woocommerce-subscriptions.php', 'woocommerce-memberships/woocommerce-memberships.php']))),
                        default => $next['option_value'],
                    };
                }
                if ($kind === 'wc_webhooks') {
                    $next['status'] = 'disabled';
                    $next['delivery_url'] = '';
                    $next['secret'] = '';
                }
                if ($kind === 'actionscheduler_actions') {
                    if (!in_array($row['status'], ['pending', 'in-progress', 'complete', 'failed', 'canceled'], true)) {
                        throw new RuntimeException('STATUT_AS_INCONNU');
                    }
                    $next['status'] = in_array($row['status'], ['pending', 'in-progress'], true) ? 'canceled' : $row['status'];
                    $next['args'] = '[]';
                    if (isset($next['extended_args'])) {
                        $next['extended_args'] = null;
                    }
                    if (isset($next['claim_id'])) {
                        $next['claim_id'] = 0;
                    }
                }
                if ($privacy && $kind === 'users' && $row['user_login'] !== 'imagine-test-admin') {
                    $next['user_login'] = 'abonne-' . $id;
                    $next['user_nicename'] = 'abonne-' . $id;
                    $next['user_email'] = "abonne-$id@example.org";
                    $next['display_name'] = 'Abonne ' . $id;
                    $next['user_pass'] = password_hash(bin2hex(random_bytes(32)), PASSWORD_BCRYPT);
                    $next['user_url'] = '';
                    $next['user_activation_key'] = '';
                }
                if ($privacy && $kind === 'wc_customer_lookup') {
                    $next['username'] = 'abonne-' . $id;
                }
                if ($privacy && $kind === 'comments') {
                    foreach (['comment_content', 'comment_author', 'comment_author_url', 'comment_author_IP', 'comment_agent'] as $key) {
                        if (isset($next[$key])) {
                            $next[$key] = '';
                        }
                    }
                    $next['comment_author_email'] = "abonne-$id@example.org";
                }
                if ($privacy && $kind === 'usermeta' && $row['meta_key'] === 'description') {
                    $next['meta_value'] = '';
                }
                if (in_array($kind, ['wc_orders', 'wc_order_operational_data'], true)) {
                    foreach (['transaction_id', 'order_key', 'cart_hash'] as $key) {
                        if (isset($next[$key])) {
                            $next[$key] = '';
                        }
                    }
                }
                if ($privacy && $kind === 'posts' && in_array($row['post_type'], ['shop_order', 'shop_order_placehold', 'shop_subscription', 'shop_order_refund', 'wc_user_membership'], true)) {
                    foreach (['post_title', 'post_content', 'post_excerpt', 'post_password', 'post_name', 'post_content_filtered'] as $key) {
                        if (isset($next[$key])) {
                            $next[$key] = '';
                        }
                    }
                }
                if ($next !== $row) {
                    $this->store->replace($table, $row, $next);
                }
            }
        }
        $options = $this->options();
        foreach (['blog_public' => '0', 'cron' => serialize([]), 'active_plugins' => serialize([])] as $key => $value) {
            if (!isset($options[$key])) {
                $this->store->insert($this->prefix . 'options', ['option_name' => $key, 'option_value' => $value, 'autoload' => 'no']);
            }
        }
    }

    public function neutraliser(): void
    {
        $this->store->begin();
        try {
            $this->transform(false);
            $this->checkUrls();
            $this->store->commit();
        } catch (\Throwable $e) {
            $this->store->rollback();
            throw $e;
        }
        $this->checkUrls(); // Lecture après COMMIT aussi, obligatoire.
    }

    private function allowedOption(string $key): bool
    {
        return $key === $this->prefix . 'user_roles' || in_array($key, ['home', 'siteurl', 'blog_public', 'cron', 'active_plugins', 'template', 'stylesheet', 'blogname', 'blogdescription', 'timezone_string', 'gmt_offset', 'date_format', 'time_format', 'start_of_week', 'permalink_structure', 'WPLANG', 'db_version', 'initial_db_version', 'woocommerce_currency', 'woocommerce_default_country', 'woocommerce_price_num_decimals', 'woocommerce_calc_taxes', 'woocommerce_prices_include_tax'], true);
    }

    public function anonymiser(string $password): void
    {
        if (strlen($password) < 20 || strlen($password) > 72 || str_contains($password, "\0")) {
            throw new RuntimeException('SECRET_ADMIN_REFUSE');
        }
        $this->checkUrls();
        $this->store->begin();
        try {
            $this->transform(true);
            $admin = null;
            foreach ($this->store->rows($this->prefix . 'users') as $row) {
                if ($row['user_login'] === 'imagine-test-admin') {
                    if ($admin !== null) {
                        throw new RuntimeException('ADMIN_DUPLIQUE');
                    }
                    $admin = $row;
                }
            }
            $row = [
                'user_login' => 'imagine-test-admin', 'user_email' => 'admin-test@example.org',
                'user_nicename' => 'imagine-test-admin', 'display_name' => 'Administrateur de test',
                'user_pass' => password_hash($password, PASSWORD_BCRYPT), 'user_url' => '',
                'user_activation_key' => '', 'user_registered' => '2026-01-01 00:00:00', 'user_status' => 0,
            ];
            if ($admin === null) {
                $id = $this->store->insert($this->prefix . 'users', $row);
            } else {
                $id = (int) $admin['ID'];
                $this->store->replace($this->prefix . 'users', $admin, array_replace($admin, $row));
            }
            foreach ($this->store->rows($this->prefix . 'usermeta') as $meta) {
                if ((int) $meta['user_id'] === $id && in_array($meta['meta_key'], [$this->prefix . 'capabilities', $this->prefix . 'user_level'], true)) {
                    $this->store->replace($this->prefix . 'usermeta', $meta, null);
                }
            }
            foreach ([$this->prefix . 'capabilities' => serialize(['administrator' => true]), $this->prefix . 'user_level' => '10'] as $key => $value) {
                $this->store->insert($this->prefix . 'usermeta', ['user_id' => $id, 'meta_key' => $key, 'meta_value' => $value]);
            }
            $this->store->commit();
        } catch (\Throwable $e) {
            $this->store->rollback();
            throw $e;
        }
        $found = array_values(array_filter($this->store->rows($this->prefix . 'users'), static fn (array $u): bool => $u['user_login'] === 'imagine-test-admin'));
        if (count($found) !== 1 || !password_verify($password, $found[0]['user_pass'])) {
            throw new RuntimeException('ADMIN_NON_ECRIT');
        }
        $this->checkAdmin($found[0]);
    }

    private function checkAdmin(array $admin): void
    {
        $roles = self::decode($this->options()[$this->prefix . 'user_roles'] ?? '');
        if (!is_array($roles) || ($roles['administrator']['capabilities']['manage_options'] ?? null) !== true) {
            throw new RuntimeException('ROLE_ADMIN_ABSENT');
        }
        $capabilities = [];
        foreach ($this->store->rows($this->prefix . 'usermeta') as $meta) {
            if ((int) $meta['user_id'] === (int) $admin['ID'] && $meta['meta_key'] === $this->prefix . 'capabilities') {
                $capabilities[] = self::decode($meta['meta_value']);
            }
        }
        if (count($capabilities) !== 1 || ($capabilities[0]['administrator'] ?? null) !== true) {
            throw new RuntimeException('CAPACITE_ADMIN_ABSENTE');
        }
    }

    /** Rapport sans valeurs, identifiants, chemins ou messages SQL. */
    public function verifier(?callable $probe): array
    {
        $issues = [];
        try {
            new self($this->store, $this->context, $this->prefix); // Ré-inventaire, aucune confiance dans l'étape précédente.
            $this->checkUrls();
            $options = $this->options();
            if (($options['blog_public'] ?? null) !== '0' || ($options['cron'] ?? null) !== serialize([])) {
                $issues[] = 'CRON_OU_INDEXATION';
            }
            foreach ($options as $key => $value) {
                if (!$this->allowedOption($key)) {
                    $issues[] = 'OPTION_NON_APPROUVEE';
                }
            }
            $plugins = self::decode($options['active_plugins'] ?? '');
            if (!is_array($plugins) || array_diff($plugins, ['woocommerce/woocommerce.php', 'woocommerce-subscriptions/woocommerce-subscriptions.php', 'woocommerce-memberships/woocommerce-memberships.php'])) {
                $issues[] = 'EXTENSION_NON_APPROUVEE';
            }
            $admins = 0;
            foreach ($this->store->schema() as $table => $_) {
                $kind = substr($table, strlen($this->prefix));
                $rows = $this->store->rows($table);
                if (in_array($kind, ['woocommerce_payment_tokens', 'woocommerce_payment_tokenmeta', 'woocommerce_sessions', 'woocommerce_api_keys', 'actionscheduler_logs', 'actionscheduler_claims', 'woocommerce_log', 'wc_download_log', 'wc_rate_limits', 'commentmeta'], true) && $rows) {
                    $issues[] = 'TABLE_A_VIDER';
                }
                foreach ($rows as $row) {
                    foreach ($row as $key => $value) {
                        if (!is_string($value)) {
                            continue;
                        }
                        if (self::dangerous($value) || self::scrub($value, false, 0) !== $value) {
                            $issues[] = 'SECRET_OU_IDENTIFIANT';
                        }
                        preg_match_all('/[A-Z0-9.!#$%&\x27*+\/=?^_`{|}~-]+@([A-Z0-9.-]+\.[A-Z]{2,})/i', $value, $emails);
                        foreach ($emails[1] as $domain) {
                            if (strtolower($domain) !== 'example.org') {
                                $issues[] = 'EMAIL_EXTERNE';
                            }
                        }
                        preg_match_all('/(?<![0-9a-f:.])[0-9a-f:.]*[.:][0-9a-f:.]+(?![0-9a-f:.])/i', $value, $ips);
                        foreach ($ips[0] as $ip) {
                            if (filter_var($ip, FILTER_VALIDATE_IP) !== false) {
                                $issues[] = 'IP_RESIDUELLE';
                            }
                        }
                        if (in_array($kind, ['wc_order_addresses', 'wc_orders', 'wc_customer_lookup', 'wc_order_operational_data'], true) && self::piiKey($key) && $value !== '') {
                            $issues[] = 'IDENTITE_RESIDUELLE';
                        }
                    }
                    if (isset($row['meta_key']) && (self::sensitiveKey($row['meta_key']) || (self::piiKey($row['meta_key']) && $row['meta_value'] !== ''))) {
                        $issues[] = 'META_RESIDUELLE';
                    }
                    if ($kind === 'users') {
                        $id = (int) $row['ID'];
                        $isAdmin = $row['user_login'] === 'imagine-test-admin';
                        if ($isAdmin) {
                            ++$admins;
                            $this->checkAdmin($row);
                        }
                        if ((!$isAdmin && ($row['user_login'] !== "abonne-$id" || $row['user_email'] !== "abonne-$id@example.org"))
                            || !$row['user_pass'] || (password_get_info($row['user_pass'])['algo'] ?? null) === null
                            || ($row['user_url'] ?? '') !== '' || ($row['user_activation_key'] ?? '') !== '') {
                            $issues[] = 'COMPTE_NON_ANONYME';
                        }
                    }
                    if ($kind === 'comments' && (($row['comment_content'] ?? '') !== '' || ($row['comment_author_IP'] ?? '') !== '')) {
                        $issues[] = 'COMMENTAIRE_RESIDUEL';
                    }
                    if ($kind === 'actionscheduler_actions' && in_array($row['status'], ['pending', 'in-progress'], true)) {
                        $issues[] = 'ACTION_EN_ATTENTE';
                    }
                    if ($kind === 'wc_webhooks' && ($row['status'] !== 'disabled' || $row['delivery_url'] !== '' || $row['secret'] !== '')) {
                        $issues[] = 'WEBHOOK_ACTIF';
                    }
                }
            }
            if ($admins !== 1) {
                $issues[] = 'ADMIN_TEST_ABSENT_OU_DUPLIQUE';
            }
        } catch (\Throwable) {
            $issues[] = 'CONTROLE_DONNEES_ECHOUE';
        }
        if ($issues) {
            $issues[] = 'SONDE_NON_EXECUTEE_DONNEES_REFUSEES';
        } elseif ($probe === null) {
            $issues[] = 'PREUVE_RUNTIME_ABSENTE';
        } else {
            try {
                $proof = $probe();
                foreach (['mail_blocked', 'http_blocked', 'subscriptions_staging', 'environment_staging', 'cron_disabled', 'as_async_disabled', 'as_runner_disabled', 'gateways_disabled'] as $required) {
                    if (($proof[$required] ?? null) !== true) {
                        $issues[] = 'PREUVE_RUNTIME_INCOMPLETE';
                    }
                }
            } catch (\Throwable) {
                $issues[] = 'SONDE_RUNTIME_ECHOUEE';
            }
        }
        if ($probe !== null && !$issues) {
            $after = $this->verifier(null); // Relecture APRÈS le bootstrap de sonde.
            $issues = array_values(array_diff($after['issues'], ['PREUVE_RUNTIME_ABSENTE']));
        }
        return ['ok' => !$issues, 'issues' => array_values(array_unique($issues)), 'scope' => 'offline-data-only'];
    }

    private function checkUrls(): void
    {
        $options = $this->options();
        if (($options['home'] ?? null) !== $this->target || ($options['siteurl'] ?? null) !== $this->target) {
            throw new RuntimeException('URL_NON_ECRITE');
        }
    }
}

final class Guard
{
    public static function context(array $context): string
    {
        if (($context['environment'] ?? null) !== 'staging'
            || ($context['isolated'] ?? null) !== true
            || ($context['restored'] ?? null) !== true
            || !preg_match('/^[a-zA-Z0-9_]+_(staging|test)$/D', $context['database'] ?? '')
            || empty($context['production_hosts']) || !is_array($context['production_hosts'])) {
            throw new RuntimeException('CONTEXTE_REFUSE');
        }
        $url = $context['target_url'] ?? '';
        $parts = parse_url($url);
        if (!is_array($parts) || !in_array($parts['scheme'] ?? '', ['http', 'https'], true)
            || isset($parts['user'], $parts['pass']) || isset($parts['user']) || isset($parts['query'])
            || isset($parts['fragment']) || !empty($parts['path'])
            || !preg_match('/^(localhost|[a-z0-9.-]+\.(test|localhost|invalid))$/D', $parts['host'] ?? '')) {
            throw new RuntimeException('URL_REFUSEE');
        }
        foreach ($context['production_hosts'] as $host) {
            if (!is_string($host) || $host === '' || strtolower($parts['host']) === strtolower($host)) {
                throw new RuntimeException('PRODUCTION_REFUSEE');
            }
        }
        return $url;
    }
}
