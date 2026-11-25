<?php

declare(strict_types=1);

namespace Imagine\Nettoyage;

/** No WordPress/plugin bootstrap: inspection cannot execute a migration/hook. */
final class Database
{
    public static function identifier(string $name): string
    {
        if (!preg_match('/\A[A-Za-z0-9_]+\z/D', $name)) {
            throw new \RuntimeException('A05_SQL_IDENTIFIER');
        }
        return '`' . $name . '`';
    }

    public static function value(\PDO $db, string $table, string $name): string|false
    {
        $q = $db->prepare('SELECT option_value FROM ' . $table . ' WHERE option_name=?');
        $q->execute([$name]);
        return $q->fetchColumn();
    }

    public static function decode(string|false $raw): array
    {
        if ($raw === false) {
            return [];
        }
        $value = unserialize($raw, ['allowed_classes' => false]);
        if (!is_array($value)) {
            throw new \RuntimeException('A05_SERIALIZED_OPTION');
        }
        return $value;
    }

    public static function run(array $input): array
    {
        define('IMAGINE_AUDIT_LIBRARY_ONLY', true);
        require_once dirname(__DIR__) . '/audit';
        require_once dirname(__DIR__) . '/a03/Policy.php';
        $config = \Imagine\Audit\Audit::config(file_get_contents($input['site'] . '/wp-config.php'));
        if (preg_match('/define\s*\(\s*[\'"]MULTISITE[\'"]\s*,\s*true/i', file_get_contents($input['site'] . '/wp-config.php'))) {
            throw new \RuntimeException('A05_MULTISITE_UNSUPPORTED');
        }
        $db = new \PDO(\Imagine\NonRegression\Policy::dsn($config), $config['DB_USER'], $config['DB_PASSWORD'], [
            \PDO::ATTR_ERRMODE => \PDO::ERRMODE_EXCEPTION,
        ]);
        $prefix = $config['table_prefix'];
        $options = self::identifier($prefix . 'options');
        if ($input['mode'] === 'inspect') {
            $db->exec('START TRANSACTION READ ONLY');
            $tables = [];
            $q = $db->query('SELECT TABLE_NAME, COALESCE(DATA_LENGTH,0)+COALESCE(INDEX_LENGTH,0) AS bytes FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() ORDER BY TABLE_NAME');
            foreach ($q as $row) {
                $name = (string) $row['TABLE_NAME'];
                $tables[] = ['name' => $name, 'rows' => (int) $db->query('SELECT COUNT(*) FROM ' . self::identifier($name))->fetchColumn(), 'bytes' => (int) $row['bytes']];
            }
            $rows = $db->query('SELECT option_name AS name, OCTET_LENGTH(option_value) AS bytes FROM ' . $options . ' ORDER BY option_name')->fetchAll(\PDO::FETCH_ASSOC);
            $cron = [];
            foreach (self::decode(self::value($db, $options, 'cron')) as $stamp => $hooks) {
                if ($stamp === 'version') {
                    continue;
                }
                foreach ($hooks as $hook => $events) {
                    $cron[$hook] ??= ['name' => $hook, 'rows' => 0, 'bytes' => 0];
                    $cron[$hook]['rows'] += count($events);
                    $cron[$hook]['bytes'] += strlen(serialize($events));
                }
            }
            $result = ['prefix' => $prefix, 'tables' => $tables, 'options' => $rows, 'cron' => array_values($cron), 'active' => array_values(self::decode(self::value($db, $options, 'active_plugins'))), 'theme' => self::value($db, $options, 'stylesheet')];
            $db->rollBack();
            return $result;
        }
        $op = $input['operation'];
        $name = $op['name'];
        if ($op['kind'] === 'table') {
            $db->exec('DROP TABLE IF EXISTS ' . self::identifier($name));
            $q = $db->prepare('SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=?');
            $q->execute([$name]);
            if ((int) $q->fetchColumn() !== 0) {
                throw new \RuntimeException('A05_TABLE_READBACK');
            }
        } elseif ($op['kind'] === 'option') {
            $q = $db->prepare('DELETE FROM ' . $options . ' WHERE option_name=?');
            $q->execute([$name]);
            if (self::value($db, $options, $name) !== false) {
                throw new \RuntimeException('A05_OPTION_READBACK');
            }
        } elseif ($op['kind'] === 'cron') {
            $db->beginTransaction();
            $raw = self::value($db, $options, 'cron');
            $cron = self::decode($raw);
            foreach ($cron as $stamp => &$hooks) {
                if ($stamp !== 'version') {
                    unset($hooks[$name]);
                }
            }
            unset($hooks);
            foreach ($cron as $stamp => $hooks) {
                if ($stamp !== 'version' && $hooks === []) {
                    unset($cron[$stamp]);
                }
            }
            $next = serialize($cron);
            if ($next !== $raw) {
                $q = $db->prepare('UPDATE ' . $options . ' SET option_value=? WHERE option_name=\'cron\' AND BINARY option_value=BINARY ?');
                $q->execute([$next, $raw]);
                if ($q->rowCount() !== 1 || self::value($db, $options, 'cron') !== $next) {
                    throw new \RuntimeException('A05_CRON_CAS');
                }
            }
            $db->commit();
        } else {
            throw new \RuntimeException('A05_OPERATION');
        }
        return ['complete' => true];
    }
}

try {
    $input = json_decode(stream_get_contents(STDIN), true, 64, JSON_THROW_ON_ERROR);
    echo json_encode(Database::run($input), JSON_THROW_ON_ERROR) . "\n";
} catch (\Throwable $error) {
    $code = preg_match('/\AA05_[A-Z_]+\z/D', $error->getMessage()) ? $error->getMessage() : 'A05_DATABASE_FAILED';
    fwrite(STDERR, $code . "\n");
    exit(1);
}
