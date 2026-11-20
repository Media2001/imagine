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
    private array $unknownTables = [];
    private array $unknownColumns = [];
    private array $unknownTypes = [];
    private array $decisions;
    private array $policy;
    public function __construct(private Store $store, private array $context, private string $prefix, array $decisions = [])
    {
        $this->target = Guard::context($context);
        if (!preg_match('/^[a-zA-Z0-9_]+_$/D', $prefix) || $store->database() !== $context['database']) {
            throw new RuntimeException('BASE_REFUSEE');
        }
        $catalogue = require __DIR__ . '/schema.php';
        $this->policy = require __DIR__ . '/policy.php';
        $this->decisions = $decisions ?: ($context['table_decisions'] ?? []);
        if (!is_array($this->decisions)) {
            throw new RuntimeException('DECISIONS_INVALIDES');
        }
        $this->inventory = $store->schema();
        foreach ($this->inventory as $table => $columns) {
            $name = str_starts_with($table, $prefix) ? substr($table, strlen($prefix)) : '';
            if (!isset($catalogue[$name])) {
                $this->unknownTables[$table] = $columns;
            } elseif ($extra = array_values(array_diff($columns, explode(' ', $catalogue[$name])))) {
                $this->unknownColumns[$table] = $extra;
            }
        }
        foreach ($this->decisions as $table => $decision) {
            if (!isset($this->unknownTables[$table]) || !is_array($decision)
                || !in_array($decision['action'] ?? '', ['garder', 'vider', 'anonymiser'], true)
                || (($decision['action'] ?? '') === 'anonymiser'
                    && (empty($decision['columns']) || !is_array($decision['columns'])
                        || array_diff($decision['columns'], $this->unknownTables[$table])))) {
                throw new RuntimeException('DECISION_INVALIDE');
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
                $this->unknownTypes[] = (string) ($post['post_type'] ?? '');
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
        return (bool) preg_match('/[spr]k_(?:live|test)_|whsec_|xkeysib[-_]|(?:cus|pm|src|seti|pi|ch|tok|ba)_[a-z0-9_-]+|(?<![a-z0-9])[BI]-[A-Z0-9]{6,}/i', $value);
    }

    private static function paymentIdentityKey(string $key): bool
    {
        return (bool) preg_match('/(?:stripe|paypal).*(?:customer|source|payment_method|token|payer|agreement|intent|mandate|subscription)(?:_id)?$|(?:^|_)(?:payer_id|billing_agreement_id|payment_method_id)$/i', $key);
    }

    /** Inspecte aussi les chaînes décodées JSON/PHP, sans classe ni donnée au rapport. */
    private static function inspect(mixed $value, int $depth = 0): array
    {
        $flags = ['danger' => false, 'external_email' => false, 'opaque' => false];
        if ($depth > 32) {
            $flags['opaque'] = true;
            return $flags;
        }
        if (is_array($value) || $value instanceof \stdClass) {
            foreach ((array) $value as $key => $child) {
                if (is_string($key) && self::paymentIdentityKey($key) && $child !== '' && $child !== null && $child !== []) {
                    $flags['danger'] = true;
                }
                foreach (self::inspect($child, $depth + 1) as $flag => $found) {
                    $flags[$flag] = $flags[$flag] || $found;
                }
            }
        } elseif (is_string($value)) {
            $flags['danger'] = self::dangerous($value);
            preg_match_all('/[A-Z0-9.!#$%&\x27*+\/=?^_`{|}~-]+@([A-Z0-9.-]+\.[A-Z]{2,})/i', $value, $matches);
            foreach ($matches[1] as $domain) {
                $flags['external_email'] = $flags['external_email'] || strtolower($domain) !== 'example.org';
            }
            try {
                $decoded = self::decode($value);
                if ($decoded === $value && (str_starts_with($value, '{') || str_starts_with($value, '['))) {
                    $decoded = json_decode($value, false, 32, JSON_THROW_ON_ERROR);
                }
                if ($decoded !== $value) {
                    foreach (self::inspect($decoded, $depth + 1) as $flag => $found) {
                        $flags[$flag] = $flags[$flag] || $found;
                    }
                }
            } catch (\Throwable) {
                $flags['opaque'] = true;
            }
        }
        return $flags;
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
        // Les formats opaques restent intacts, sans jamais instancier d'objet PHP.
        // Les motifs de service connus restent supprimés même dans ces formats.
        try {
            $decoded = self::decode($value);
        } catch (\Throwable) {
            return self::dangerous($value) ? '' : $value;
        }
        if ($decoded !== $value) {
            $clean = self::scrub($decoded, $privacy, $id, $depth + 1);
            return $clean === $decoded ? $value : serialize($clean);
        }
        if (str_starts_with($value, '{') || str_starts_with($value, '[')) {
            try {
                $json = json_decode($value, false, 32, JSON_THROW_ON_ERROR);
                $clean = self::scrubJson($json, $privacy, $id, $depth + 1);
                return $clean == $json ? $value : json_encode($clean, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
            } catch (\Throwable) {
                return self::dangerous($value) ? '' : $value;
            }
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
        // Ne pas confondre un tableau de réglages Stripe/SMTP et ses champs secrets.
        return (bool) preg_match('/(?:^|_)(?:secret(?:_key)?|api_?key|(?:test_|live_)?(?:secret|publishable|public|private|access)_?key|password|pass|smtp_pass|token|access_token|refresh_token|nonce|session_tokens|application_passwords|consumer_key|consumer_secret|webhook_secret|client_secret|client_id|authorization|merchant_id|payer_id|transaction_id|billing_agreement_id|payment_method_id|source_id|intent_id|mandate_id)$/i', $key)
            || (bool) preg_match('/(?:stripe|paypal|brevo|sendinblue).*(?:customer|source|payment_method|token|key|secret|payer|agreement|intent|mandate)(?:_id)?$/i', $key);
    }

    private static function personalColumn(string $key): bool
    {
        return self::piiKey($key) || (bool) preg_match('/email|e_mail|phone|telephone|mobile|(?:^|_)(?:name|nom|prenom|surname|givenname|firstname|lastname|address|adresse|ip)(?:$|_)|ip_address/i', $key);
    }

    private function readOnly(string $table): bool
    {
        return method_exists($this->store, 'details') && (($this->store->details()['tables'][$table]['type'] ?? '') === 'VIEW');
    }

    private function disabledPlugins(): array
    {
        return array_merge(...array_values($this->policy));
    }

    private function setOption(string $key, string $value): void
    {
        foreach ($this->store->rows($this->prefix . 'options') as $row) {
            if ($row['option_name'] === $key) {
                $next = array_replace($row, ['option_value' => $value]);
                if ($next !== $row) {
                    $this->store->replace($this->prefix . 'options', $row, $next);
                }
                return;
            }
        }
        $this->store->insert($this->prefix . 'options', ['option_name' => $key, 'option_value' => $value, 'autoload' => 'no']);
    }

    private static function piiKey(string $key): bool
    {
        return (bool) preg_match('/(?:^|_)(first_name|last_name|full_name|billing_name|shipping_name|company|address_?[12]?|city|postcode|state|phone|vat|tax_id|company_number|business_number|siret|iban|bic|nickname|ip_address|user_agent|customer_note|order_key|cart_hash|shipping_packages)(?:$|_)/i', $key);
    }

    private function transform(bool $privacy): void
    {
        $disabled = self::decode($this->options()['imagine_staging_disabled_plugins'] ?? serialize([]));
        $disabled = is_array($disabled) ? $disabled : [];
        foreach ($this->inventory as $table => $_) {
            if ($this->readOnly($table)) {
                continue; // Une vue est inventoriée et inspectée, pas réécrite.
            }
            $kind = substr($table, strlen($this->prefix));
            foreach ($this->store->rows($table) as $row) {
                if (isset($this->unknownTables[$table]) && ($this->decisions[$table]['action'] ?? '') === 'vider') {
                    $this->store->replace($table, $row, null);
                    continue;
                }
                if ($kind === 'actionscheduler_actions' && in_array($row['status'], ['complete', 'failed'], true)) {
                    $this->store->replace($table, $row, null);
                    continue;
                }
                if (in_array($kind, ['woocommerce_payment_tokens', 'woocommerce_payment_tokenmeta', 'woocommerce_sessions', 'woocommerce_api_keys', 'actionscheduler_logs', 'actionscheduler_claims', 'woocommerce_log', 'wc_download_log', 'wc_rate_limits'], true)
                    || ($privacy && $kind === 'commentmeta')) {
                    $this->store->replace($table, $row, null);
                    continue;
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
                    // Les réglages d'extensions et tables inconnues ne sont pas une
                    // liste blanche : seules les zones personnelles connues changent.
                    $personal = $privacy && !isset($this->unknownTables[$table])
                        && !in_array($kind, ['options', 'terms', 'termmeta', 'term_taxonomy', 'term_relationships', 'links'], true);
                    $next[$key] = self::scrub($value, $personal, $id);
                    if (self::sensitiveKey((string) $key) && $key !== 'option_name' && $key !== 'meta_key') {
                        $next[$key] = '';
                    }
                    if ($privacy && ((in_array($kind, ['wc_order_addresses', 'wc_orders', 'wc_customer_lookup', 'wc_order_operational_data'], true) && self::piiKey($key)) || ($key === 'meta_value' && self::piiKey($row['meta_key'] ?? '')))) {
                        $next[$key] = '';
                    }
                }
                if ($kind === 'options') {
                    if (in_array($row['option_name'], ['active_plugins', 'active_sitewide_plugins'], true)) {
                        $active = self::decode($row['option_value']);
                        if (is_array($active)) {
                            $names = $row['option_name'] === 'active_plugins' ? $active : array_keys($active);
                            $disabled = array_values(array_unique(array_merge($disabled, array_intersect($names, $this->disabledPlugins()))));
                        }
                    }
                    $next['option_value'] = match ($row['option_name']) {
                        'home', 'siteurl' => $this->target,
                        'blog_public' => '0', 'cron' => serialize([]),
                        'active_plugins' => serialize(array_values(array_diff((array) self::decode($row['option_value']), $this->disabledPlugins()))),
                        'active_sitewide_plugins' => serialize(array_diff_key((array) self::decode($row['option_value']), array_flip($this->disabledPlugins()))),
                        default => $next['option_value'],
                    };
                    if (self::sensitiveKey($row['option_name'])) {
                        $next['option_value'] = '';
                    }
                    if (preg_match('/^woocommerce_.*(?:stripe|paypal|ppcp).*_settings$/i', $row['option_name'])) {
                        $gateway = self::decode($next['option_value']);
                        if (is_array($gateway)) {
                            $gateway['testmode'] = 'yes';
                            if (array_key_exists('sandbox', $gateway)) {
                                $gateway['sandbox'] = 'yes';
                            }
                            if (array_key_exists('test_mode', $gateway)) {
                                $gateway['test_mode'] = 'yes';
                            }
                            $next['option_value'] = serialize($gateway);
                        }
                    }
                }
                if ($privacy && isset($this->unknownTables[$table]) && ($this->decisions[$table]['action'] ?? '') === 'anonymiser') {
                    foreach ($this->decisions[$table]['columns'] as $column) {
                        $next[$column] = preg_match('/email|e_mail/i', $column) ? "abonne-$id@example.org" : '';
                    }
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
        $this->setOption('imagine_staging_disabled_plugins', serialize($disabled));
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

    /** Cinq blocages de données/runtime + décision personnelle, sans aucune valeur. */
    public function verifier(?callable $probe): array
    {
        $issues = [];
        $warnings = [];
        $unknown = [];
        $fresh = new self($this->store, $this->context, $this->prefix, $this->decisions);
        $this->inventory = $fresh->inventory;
        $this->unknownTables = $fresh->unknownTables;
        $this->unknownColumns = $fresh->unknownColumns;
        $this->unknownTypes = $fresh->unknownTypes;
        $this->checkUrls(); // Barrière de cible, jamais transformée en avertissement.
        $options = $this->options();
        $plugins = self::decode($options['active_plugins'] ?? serialize([]));
        $subscriptionsExpected = is_array($plugins)
            && in_array('woocommerce-subscriptions/woocommerce-subscriptions.php', $plugins, true);
        if (($options['blog_public'] ?? null) !== '0' || ($options['cron'] ?? null) !== serialize([])) {
            $warnings[] = 'CRON_OU_INDEXATION';
        }
        if (is_array($plugins) && array_intersect($plugins, $this->disabledPlugins())) {
            $warnings[] = 'EXTENSION_A_DESACTIVER';
        }
        $transactionPosts = [];
        foreach ($this->store->rows($this->prefix . 'posts') as $post) {
            if (in_array($post['post_type'] ?? '', ['shop_order', 'shop_subscription', 'shop_order_refund', 'wc_user_membership'], true)) {
                $transactionPosts[] = (int) $post['ID'];
            }
        }
        foreach ($this->inventory as $table => $columns) {
            $kind = str_starts_with($table, $this->prefix) ? substr($table, strlen($this->prefix)) : '';
            $rows = $this->store->rows($table);
            if (isset($this->unknownTables[$table])) {
                $personal = array_values(array_filter($columns, self::personalColumn(...)));
                $decision = $this->decisions[$table] ?? null;
                $unknown[] = ['name' => $table, 'columns' => array_values($columns), 'rows' => count($rows),
                    'personal_columns' => $personal, 'decision' => $decision];
                if ($personal && $decision === null) {
                    $issues[] = 'TABLE_PERSONNELLE_A_TRANCHER';
                }
                $warnings[] = 'TABLE_INCONNUE_CONSERVEE';
            }
            if (in_array($kind, ['woocommerce_payment_tokens', 'woocommerce_payment_tokenmeta', 'woocommerce_sessions', 'woocommerce_api_keys', 'actionscheduler_logs', 'actionscheduler_claims', 'woocommerce_log', 'wc_download_log', 'wc_rate_limits', 'commentmeta'], true) && $rows) {
                $warnings[] = 'TABLE_A_VIDER';
            }
            foreach ($rows as $row) {
                $emailScope = in_array($kind, ['users', 'usermeta', 'wc_orders', 'wc_order_addresses', 'wc_orders_meta', 'wc_customer_lookup', 'woocommerce_downloadable_product_permissions'], true)
                    || ($kind === 'posts' && in_array((int) ($row['ID'] ?? 0), $transactionPosts, true))
                    || ($kind === 'postmeta' && in_array((int) ($row['post_id'] ?? 0), $transactionPosts, true));
                foreach ($row as $key => $value) {
                    if (!is_string($value)) {
                        continue;
                    }
                    $flags = self::inspect($value);
                    if ($flags['danger'] || (self::paymentIdentityKey((string) $key) && $value !== '')) {
                        $issues[] = 'SECRET_OU_IDENTIFIANT';
                    }
                    // Une clé opaque connue résiduelle est signalée, pas inventée comme
                    // un sixième motif de service. La neutralisation sait la vider.
                    if (self::sensitiveKey((string) $key) && $value !== '') {
                        $warnings[] = 'CHAMP_SECRET_CONNU_RESIDUEL';
                    }
                    if (self::scrub($value, false, 0) !== $value) {
                        $warnings[] = 'REGLAGE_SECRET_RESIDUEL';
                    }
                    if ($flags['external_email']) {
                        if ($emailScope) {
                            $issues[] = 'EMAIL_EXTERNE';
                        } else {
                            $warnings[] = 'EMAIL_HORS_PERIMETRE_COMPTES_COMMANDES';
                        }
                    }
                    if (in_array($kind, ['wc_order_addresses', 'wc_orders', 'wc_customer_lookup', 'wc_order_operational_data'], true) && self::piiKey((string) $key) && $value !== '') {
                        $warnings[] = 'IDENTITE_RESIDUELLE';
                    }
                    if ($flags['opaque']) {
                        $warnings[] = 'FORMAT_OPAQUE_CONSERVE';
                    }
                }
                if (isset($row['meta_key']) && self::paymentIdentityKey($row['meta_key']) && ($row['meta_value'] ?? '') !== '') {
                    $issues[] = 'SECRET_OU_IDENTIFIANT';
                }
                if (isset($row['meta_key']) && (self::sensitiveKey($row['meta_key']) || (self::piiKey($row['meta_key']) && $row['meta_value'] !== ''))) {
                    $warnings[] = 'META_RESIDUELLE';
                }
                if ($kind === 'actionscheduler_actions' && in_array($row['status'], ['pending', 'in-progress'], true)) {
                    $warnings[] = 'ACTION_EN_ATTENTE';
                }
                if ($kind === 'wc_webhooks' && ($row['status'] !== 'disabled' || $row['delivery_url'] !== '' || $row['secret'] !== '')) {
                    $warnings[] = 'WEBHOOK_ACTIF';
                }
            }
        }
        if ($this->unknownColumns) {
            $warnings[] = 'COLONNES_INCONNUES_CONSERVEES';
        }
        if ($this->unknownTypes) {
            $warnings[] = 'TYPES_CONTENU_INCONNUS_CONSERVES';
        }
        $schemaDetails = method_exists($this->store, 'details') ? $this->store->details() : [];
        foreach ($schemaDetails['warnings'] ?? [] as $warning) {
            $warnings[] = $warning;
        }
        if ($issues) {
            $warnings[] = 'SONDE_NON_EXECUTEE_DONNEES_REFUSEES';
        } elseif ($probe === null) {
            $issues[] = 'PREUVE_RUNTIME_ABSENTE';
        } else {
            try {
                $proof = $probe();
                if (($proof['mail_blocked'] ?? null) !== true) {
                    $issues[] = 'EMAIL_NON_COUPE';
                }
                $subscriptionsPresent = $subscriptionsExpected || ($proof['subscriptions_present'] ?? true) !== false;
                if ($subscriptionsPresent && ($proof['subscriptions_staging'] ?? null) !== true) {
                    $issues[] = 'SUBSCRIPTIONS_NON_STAGING';
                }
                foreach (['http_blocked', 'environment_staging', 'cron_disabled', 'as_async_disabled', 'as_runner_disabled', 'gateways_disabled'] as $check) {
                    if (($proof[$check] ?? null) !== true) {
                        $warnings[] = 'RUNTIME_' . strtoupper($check);
                    }
                }
            } catch (\Throwable) {
                $issues[] = 'SONDE_RUNTIME_ECHOUEE';
            }
        }
        if ($probe !== null && !$issues) {
            $after = $this->verifier(null); // Données relues après bootstrap ; pas de seconde sonde.
            $issues = array_values(array_diff($after['issues'], ['PREUVE_RUNTIME_ABSENTE']));
            $warnings = array_merge($warnings, $after['warnings']);
            $unknown = $after['unknown_tables'];
        }
        $disabled = self::decode($this->options()['imagine_staging_disabled_plugins'] ?? serialize([]));
        return ['ok' => !$issues, 'issues' => array_values(array_unique($issues)),
            'warnings' => array_values(array_unique($warnings)), 'unknown_tables' => $unknown,
            'unknown_columns' => $this->unknownColumns,
            'unknown_post_types' => array_values(array_unique($this->unknownTypes)),
            'disabled_plugins' => is_array($disabled) ? array_values($disabled) : [],
            'active_plugins' => is_array($plugins) ? array_values($plugins) : [],
            'schema_details' => $schemaDetails, 'scope' => 'offline-data-only'];
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
