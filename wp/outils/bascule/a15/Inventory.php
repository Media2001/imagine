<?php

declare(strict_types=1);

namespace Imagine\EmailInventory;

/** Project the actually loaded WC_Emails registry, never render or trigger an email. */
final class Inventory
{
    public static function safeLabel(string $value): string
    {
        return strlen($value) <= 200 && !preg_match('/[@\x00-\x1f<>]|https?:\/\//i', $value)
            ? $value : '[intitule masque]';
    }

    public static function shape(object $email, string $owner, ?array $stored = null): array
    {
        if (($email->block_email_editor_enabled ?? false) === true) {
            throw new \RuntimeException('A15_BLOCK_EDITOR_UNSUPPORTED');
        }
        $settings = $stored ?? $email->settings;
        $fields = $email->get_form_fields();
        $changed = static function (string $key, string $default, bool $emptyFallback = false) use ($settings): bool {
            if (!array_key_exists($key, $settings)) {
                return false;
            }
            if (!is_scalar($settings[$key]) && $settings[$key] !== null) {
                throw new \RuntimeException('A15_SETTINGS_SHAPE');
            }
            $value = (string) $settings[$key];
            return !($emptyFallback && $value === '') && $value !== $default;
        };
        $subject = false;
        $content = false;
        foreach ($fields as $key => $field) {
            if (!preg_match('/\A(subject|heading)(?:_[a-zA-Z0-9_]+)?\z/D', (string) $key, $kind)) {
                continue;
            }
            $method = 'get_default_' . $key;
            $default = $field['placeholder'] ?? $field['default'] ?? '';
            if (in_array($key, ['subject', 'heading'], true) && method_exists($email, $method)) {
                $default = $email->$method();
            }
            $modified = $changed($key, (string) $default, true);
            if ($kind[1] === 'subject') {
                $subject = $subject || $modified;
            } else {
                $content = $content || $modified;
            }
        }
        foreach (['body', 'additional_content', 'preheader'] as $key) {
            if (isset($fields[$key]) || array_key_exists($key, $settings)) {
                $method = 'get_default_' . $key;
                $default = method_exists($email, $method) ? $email->$method() : ($fields[$key]['default'] ?? '');
                $content = $content || $changed($key, (string) $default);
            }
        }
        $list = static function (mixed $value): array {
            if (!is_scalar($value) && $value !== null) {
                throw new \RuntimeException('A15_SETTINGS_SHAPE');
            }
            $parts = preg_split('/[,;\r\n]+/', (string) $value);
            $parts = array_values(array_unique(array_filter(array_map(
                static fn(string $item): string => strtolower(preg_replace('/\s+/', '', $item)),
                $parts
            ), static fn(string $item): bool => $item !== '')));
            sort($parts, SORT_STRING);
            return $parts;
        };
        $recipient = false;
        foreach (['recipient', 'cc', 'bcc'] as $key) {
            if (!array_key_exists($key, $settings)) {
                continue;
            }
            $configured = $list($settings[$key]);
            $default = $list($fields[$key]['default'] ?? '');
            $recipient = $recipient || ($configured !== [] && $configured !== $default);
        }
        if (!preg_match('/\A[a-zA-Z0-9_-]{1,120}\z/D', (string) $email->id)) {
            throw new \RuntimeException('A15_EMAIL_ID_UNSAFE');
        }
        return [
            'id' => $email->id,
            'title' => self::safeLabel((string) $email->get_title()),
            'extension' => $owner,
            'enabled' => (bool) $email->is_enabled(),
            'recipient_nature' => $email->is_customer_email() ? 'client' : 'administration',
            'recipient_customised' => $recipient,
            'subject_customised' => $subject,
            'content_customised' => $content,
        ];
    }

    private static function owner(string $file, string $site): string
    {
        $parts = ['plugin' => '/wp-content/plugins/', 'mu_plugin' => '/wp-content/mu-plugins/',
            'theme' => '/wp-content/themes/'];
        foreach ($parts as $kind => $part) {
            if (str_starts_with($file, $site . $part)) {
                $slug = explode('/', substr($file, strlen($site . $part)))[0];
                if (!preg_match('/\A[a-zA-Z0-9_.-]+\z/D', $slug)) {
                    throw new \RuntimeException('A15_OWNER_UNSAFE');
                }
                return $kind . ':' . $slug;
            }
        }
        return str_starts_with($file, $site . '/wp-includes/') ? 'wordpress' : 'unattributed';
    }

    private static function overrides(object $email, string $site): array
    {
        $result = [];
        $templates = [];
        foreach (['template_html', 'template_plain'] as $property) {
            $template = (string) ($email->$property ?? '');
            if ($template !== '') {
                $templates[$template] = $email->template_base;
            }
        }
        if (($email->template_html ?? '') !== '' && $email->get_email_type() !== 'plain') {
            foreach (['emails/email-header.php', 'emails/email-footer.php', 'emails/email-styles.php'] as $template) {
                $templates[$template] = WC()->plugin_path() . '/templates/';
            }
        }
        foreach ($templates as $template => $defaultPath) {
            if (!preg_match('/\A[a-zA-Z0-9_\/-]+\.php\z/D', $template) || str_contains($template, '..')) {
                throw new \RuntimeException('A15_TEMPLATE_UNSAFE');
            }
            $located = wc_locate_template($template, 'woocommerce/', $defaultPath);
            $file = realpath($located);
            if (!$file || !is_file($file)) {
                throw new \RuntimeException('A15_TEMPLATE_MISSING');
            }
            if (str_starts_with($file, $site . '/wp-content/themes/')) {
                $relative = substr($file, strlen($site) + 1);
                if (!preg_match('/\A[a-zA-Z0-9_.\/-]+\z/D', $relative)) {
                    throw new \RuntimeException('A15_TEMPLATE_UNSAFE');
                }
                $result[] = $relative;
            }
        }
        sort($result, SORT_STRING);
        return array_values(array_unique($result));
    }

    private static function transports(string $site): array
    {
        require_once ABSPATH . 'wp-admin/includes/plugin.php';
        $hookOwners = [];
        foreach (['phpmailer_init', 'pre_wp_mail', 'wp_mail'] as $hook) {
            foreach (($GLOBALS['wp_filter'][$hook]->callbacks ?? []) as $callbacks) {
                foreach ($callbacks as $item) {
                    $fn = $item['function'];
                    try {
                        if (is_array($fn)) {
                            $ref = new \ReflectionMethod($fn[0], $fn[1]);
                        } elseif (is_object($fn) && !$fn instanceof \Closure) {
                            $ref = new \ReflectionMethod($fn, '__invoke');
                        } else {
                            $ref = new \ReflectionFunction($fn);
                        }
                        // Core email MIME formatting is not an SMTP/provider implementation.
                        if (
                            $ref instanceof \ReflectionMethod && $ref->getDeclaringClass()->getName() === 'WC_Email'
                            && $ref->getName() === 'handle_multipart'
                        ) {
                            continue;
                        }
                        $file = $ref->getFileName();
                        if ($file) {
                            $hookOwners[self::owner($file, $site)] = true;
                        }
                    } catch (\ReflectionException) {
                        // An unreflectable hook is not assigned to an invented provider.
                    }
                }
            }
        }
        $rows = [];
        foreach (['plugin' => get_plugins(), 'mu_plugin' => get_mu_plugins()] as $kind => $plugins) {
            foreach ($plugins as $file => $data) {
                $slug = explode('/', $file)[0];
                $observed = isset($hookOwners[$kind . ':' . $slug]);
                $named = preg_match(
                    '/smtp|brevo|sendinblue|sendgrid|mailgun|mailjet|postmark|amazon.?ses|sendmail/i',
                    $file . ' ' . $data['Name']
                );
                if (!$named && !$observed) {
                    continue;
                }
                $rows[] = [
                    'name' => self::safeLabel((string) $data['Name']),
                    'version' => \Imagine\Audit\Audit::version($data['Version']),
                    'active' => $kind === 'mu_plugin' || is_plugin_active($file),
                    'runtime_mail_hook' => $observed,
                ];
            }
        }
        usort($rows, static fn(array $a, array $b): int => [$a['name'], $a['version']] <=> [$b['name'], $b['version']]);
        return $rows;
    }

    public static function collect(string $site): array
    {
        \Imagine\PublicAddresses\Runtime::boot($site);
        global $wpdb;
        $engines = $wpdb->get_col(
            "SELECT ENGINE FROM information_schema.TABLES "
            . "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_TYPE='BASE TABLE'"
        );
        if (array_filter($engines, static fn($engine): bool => $engine !== 'InnoDB')) {
            throw new \RuntimeException('A15_TRANSACTIONAL_TABLES_REQUIRED');
        }
        if (!did_action('wp_loaded') || !function_exists('WC')) {
            throw new \RuntimeException('A15_NATIVE_REGISTRY_UNAVAILABLE');
        }
        $emails = [];
        $summary = [];
        $files = [];
        foreach (WC()->mailer()->get_emails() as $email) {
            if (!$email instanceof \WC_Email) {
                throw new \RuntimeException('A15_REGISTRY_SHAPE');
            }
            $ref = new \ReflectionClass($email);
            $owner = self::owner((string) $ref->getFileName(), $site);
            $stored = get_option($email->get_option_key(), []);
            if (!is_array($stored)) {
                throw new \RuntimeException('A15_SETTINGS_SHAPE');
            }
            $row = self::shape($email, $owner, $stored);
            if ($email instanceof \WC_Memberships_User_Membership_Email) {
                foreach (wc_memberships_get_membership_plans() as $plan) {
                    if ($plan->get_email_content($email->id) !== $email->get_default_body()) {
                        $row['content_customised'] = true;
                    }
                }
            }
            $row['template_overrides'] = self::overrides($email, $site);
            $row['template_overridden'] = $row['template_overrides'] !== [];
            if (isset($emails[$row['id']])) {
                throw new \RuntimeException('A15_DUPLICATE_ID');
            }
            $emails[$row['id']] = $row;
            $summary[$owner] = ($summary[$owner] ?? 0) + (int) $row['enabled'];
            foreach ($row['template_overrides'] as $file) {
                $files[$file] = true;
            }
        }
        ksort($emails, SORT_STRING);
        ksort($summary, SORT_STRING);
        return [
            'schema' => 'imagine-a15-v1', 'read_only' => true,
            'storage' => get_option('woocommerce_custom_orders_table_enabled') === 'yes' ? 'hpos' : 'classic',
            'registry' => ['native_loaded' => true, 'email_count' => count($emails)],
            'emails' => array_values($emails), 'transport_plugins' => self::transports($site),
            'summary' => ['active_by_extension' => $summary, 'overridden_template_files' => count($files)],
        ];
    }
}
