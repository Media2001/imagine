<?php

declare(strict_types=1);

namespace Imagine\RetentionInventory;

final class Inventory
{
    private const FOLDERS = ['exports', 'logs', 'backups', 'wc-logs', 'woocommerce_uploads',
        'ai1wm-backups', 'wpallimport', 'gravity_forms', 'wpcf7_uploads', 'formidable', 'wpforms'];
    private const EXTENSIONS = ['csv', 'xls', 'xlsx', 'log', 'txt', 'zip', 'gz', 'pdf', 'json', 'sql',
        'xml', 'jpg', 'jpeg', 'png', 'webp', 'gif', 'php', 'html', 'css', 'js', 'bak', 'wpress'];

    public static function technical(string $key): string
    {
        return preg_match('/\A[a-zA-Z_][a-zA-Z0-9_-]{0,99}\z/D', $key) ? $key : 'autre';
    }

    public static function groups(array $rows): array
    {
        $groups = [];
        foreach ($rows as $row) {
            $flags = Forms::scan((string) $row['value']);
            if (!in_array(true, $flags, true)) {
                continue;
            }
            $key = self::technical($row['key']);
            $index = $row['scope'] . ':' . $key;
            $groups[$index] ??= ['scope' => $row['scope'], 'key' => $key, 'iban' => 0, 'card' => 0, 'national' => 0];
            foreach ($flags as $type => $hit) {
                $groups[$index][$type] += (int) $hit;
            }
        }
        ksort($groups);
        return array_values($groups);
    }

    private static function rows(string $query): \Generator
    {
        global $wpdb;
        $cursor = 0;
        do {
            $rows = $wpdb->get_results($wpdb->prepare($query, $cursor), ARRAY_A);
            if (!is_array($rows) || $wpdb->last_error !== '') {
                throw new \RuntimeException('A18_QUERY_FAILED');
            }
            foreach ($rows as $row) {
                $cursor = (int) $row['row_id'];
                yield ['scope' => $row['scope'], 'key' => $row['field_key'], 'value' => $row['field_value']];
            }
        } while (count($rows) === 500);
    }

    private static function database(bool $hpos): array
    {
        global $wpdb;
        $p = $wpdb->prefix;
        $queries = [
            "SELECT umeta_id row_id,'account' scope,meta_key field_key,meta_value field_value "
                . "FROM `{$p}usermeta` WHERE umeta_id>%d ORDER BY umeta_id LIMIT 500",
            "SELECT option_id row_id,'option' scope,option_name field_key,option_value field_value "
                . "FROM `{$p}options` WHERE option_id>%d ORDER BY option_id LIMIT 500",
        ];
        $queries[] = $hpos
            ? "SELECT m.id row_id,IF(o.type='shop_subscription','subscription','order') scope,"
                . "m.meta_key field_key,m.meta_value field_value FROM `{$p}wc_orders_meta` m "
                . "JOIN `{$p}wc_orders` o ON o.id=m.order_id WHERE m.id>%d "
                . "AND o.type IN ('shop_order','shop_subscription') ORDER BY m.id LIMIT 500"
            : "SELECT m.meta_id row_id,IF(o.post_type='shop_subscription','subscription','order') scope,"
                . "m.meta_key field_key,m.meta_value field_value FROM `{$p}postmeta` m "
                . "JOIN `{$p}posts` o ON o.ID=m.post_id WHERE m.meta_id>%d "
                . "AND o.post_type IN ('shop_order','shop_subscription') ORDER BY m.meta_id LIMIT 500";
        $aggregated = [];
        foreach ($queries as $query) {
            // Aggregate every value independently, bounded pagination without retaining values.
            foreach (self::rows($query) as $row) {
                foreach (self::groups([$row]) as $group) {
                    $index = $group['scope'] . ':' . $group['key'];
                    $aggregated[$index] ??= array_merge($group, ['iban' => 0, 'card' => 0, 'national' => 0]);
                    foreach (['iban', 'card', 'national'] as $type) {
                        $aggregated[$index][$type] += $group[$type];
                    }
                }
            }
        }
        ksort($aggregated);
        return ['status' => 'observe', 'groups' => array_values($aggregated)];
    }

    public static function media(string $root): array
    {
        $groups = [];
        if (!is_dir($root)) {
            return [];
        }
        foreach (new \DirectoryIterator($root) as $top) {
            if ($top->isDot() || !$top->isDir() || preg_match('/\A[0-9]{4}\z/D', $top->getFilename())) {
                continue;
            }
            $folder = in_array($top->getFilename(), self::FOLDERS, true) ? $top->getFilename() : 'autre';
            $groups[$folder] ??= ['folder' => $folder, 'directories' => 0, 'files' => [], 'bytes' => 0,
                'server_rule_file_present' => false, 'reading_denied' => null];
            $groups[$folder]['directories']++;
            $iterator = new \RecursiveDirectoryIterator($top->getPathname(), \FilesystemIterator::SKIP_DOTS);
            foreach (new \RecursiveIteratorIterator($iterator) as $file) {
                if (!$file->isFile()) {
                    continue;
                }
                $rule = in_array($file->getFilename(), ['.htaccess', 'web.config'], true);
                $ext = $rule ? 'regles' : strtolower($file->getExtension());
                $ext = $rule || in_array($ext, self::EXTENSIONS, true) ? $ext : 'autre';
                $groups[$folder]['files'][$ext] = ($groups[$folder]['files'][$ext] ?? 0) + 1;
                $groups[$folder]['bytes'] += $file->getSize();
                $groups[$folder]['server_rule_file_present'] = $groups[$folder]['server_rule_file_present'] || $rule;
            }
            ksort($groups[$folder]['files']);
        }
        ksort($groups);
        foreach ($groups as &$group) {
            if (!$group['files']) {
                $group['files'] = (object) [];
            }
        }
        unset($group);
        return array_values($groups);
    }

    public static function collect(string $site): array
    {
        \Imagine\PublicAddresses\Runtime::boot($site);
        global $wpdb;
        $hpos = get_option('woocommerce_custom_orders_table_enabled') === 'yes';
        $neutralised = get_option('imagine_staging_disabled_plugins', null) !== null;
        $database = $neutralised
            ? ['status' => 'inconnu après neutralisation', 'groups' => null] : self::database($hpos);
        $tokens = $wpdb->get_results(
            "SELECT gateway_id,type,COUNT(*) count FROM `{$wpdb->prefix}woocommerce_payment_tokens` "
                . 'GROUP BY gateway_id,type ORDER BY gateway_id,type',
            ARRAY_A
        );
        if (!is_array($tokens) || $wpdb->last_error !== '') {
            throw new \RuntimeException('A18_QUERY_FAILED');
        }
        $tokenGroups = [];
        foreach ($tokens as $token) {
            $gateway = self::technical($token['gateway_id']);
            $type = self::technical($token['type']);
            $index = $gateway . ':' . $type;
            $tokenGroups[$index] ??= ['gateway' => $gateway, 'type' => $type, 'count' => 0];
            $tokenGroups[$index]['count'] += (int) $token['count'];
        }
        ksort($tokenGroups);
        $uploads = wp_upload_dir(null, false, true)['basedir'];
        if (!is_string($uploads) || !str_starts_with($uploads . '/', $site . '/') || str_contains($uploads, '..')) {
            throw new \RuntimeException('A18_UPLOAD_ROOT_UNSAFE');
        }
        return ['schema' => 'imagine-a18-retention-v1', 'read_only' => true, 'storage' => $hpos ? 'hpos' : 'classic',
            'database' => $database, 'payment_tokens' => array_values($tokenGroups), 'media' => self::media($uploads),
            'count_basis' => 'Une valeur stockee compte au plus une fois par forme ; une cle est separee par portee.',
            'server_rules' => 'Presence observee par nom technique ferme ; lecture effectivement interdite inconnue '
                . 'sans ouvrir les fichiers ni lire la configuration serveur.',
            'token_basis' => 'References par passerelle et type ; jamais des numeros de carte ou IBAN.'];
    }
}
