<?php

declare(strict_types=1);

namespace Imagine\ContentInventory;

use Imagine\Audit\Audit;

/** SELECT-only structural snapshot. WordPress and third-party PHP are never executed. */
final class Inventory
{
    private \PDO $db;
    private string $prefix;
    private string $site;
    private array $tables = [];

    public function __construct(string $site)
    {
        $this->site = $site;
        $source = self::read($site . '/wp-config.php', 1048576);
        $config = Audit::config($source);
        foreach (token_get_all($source) as $token) {
            if (is_array($token) && $token[0] === T_CONSTANT_ENCAPSED_STRING && in_array(substr($token[1], 1, -1), ['WP_CONTENT_DIR', 'WPMU_PLUGIN_DIR', 'WP_PLUGIN_DIR', 'UPLOADS', 'MULTISITE'], true)) {
                throw new \RuntimeException('A12_CUSTOM_LAYOUT_UNSUPPORTED');
            }
        }
        $this->prefix = $config['table_prefix'];
        $host = $config['DB_HOST'];
        if (preg_match('~\Alocalhost:(/[^;\x00-\x1f]+)\z~D', $host, $match)) {
            $dsn = 'mysql:unix_socket=' . $match[1];
        } elseif (preg_match('/\A([A-Za-z0-9_.-]+)(?::([0-9]{1,5}))?\z/D', $host, $match)) {
            $dsn = 'mysql:host=' . $match[1] . ';port=' . ($match[2] ?? '3306');
        } else {
            throw new \RuntimeException('A12_DB_HOST_UNSUPPORTED');
        }
        if (!preg_match('/\A[A-Za-z0-9_-]+\z/D', $config['DB_NAME'])) {
            throw new \RuntimeException('A12_DB_NAME_UNSUPPORTED');
        }
        $this->db = new \PDO($dsn . ';dbname=' . $config['DB_NAME'] . ';charset=utf8mb4', $config['DB_USER'], $config['DB_PASSWORD'], [
            \PDO::ATTR_ERRMODE => \PDO::ERRMODE_EXCEPTION,
            \PDO::ATTR_EMULATE_PREPARES => false,
            \PDO::MYSQL_ATTR_MULTI_STATEMENTS => false,
            \PDO::ATTR_TIMEOUT => 10,
        ]);
        unset($config);
        $this->db->exec('SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ');
        $this->db->exec('SET SESSION TRANSACTION READ ONLY');
        $this->db->beginTransaction();
        foreach ($this->select('SELECT TABLE_NAME,ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_TYPE=\'BASE TABLE\' ORDER BY TABLE_NAME') as $row) {
            if ($row['ENGINE'] !== 'InnoDB') {
                throw new \RuntimeException('A12_TRANSACTIONAL_TABLES_REQUIRED');
            }
            $this->tables[] = $row['TABLE_NAME'];
        }
        if (in_array($this->prefix . 'blogs', $this->tables, true) || $this->option('ms_files_rewriting') !== '') {
            throw new \RuntimeException('A12_MULTISITE_UNSUPPORTED');
        }
    }

    public function __destruct()
    {
        if (isset($this->db) && $this->db->inTransaction()) {
            $this->db->rollBack();
        }
    }

    private function select(string $sql, array $params = []): array
    {
        if (!str_starts_with($sql, 'SELECT ')) {
            throw new \RuntimeException('A12_SELECT_ONLY');
        }
        $statement = $this->db->prepare($sql);
        $statement->execute($params);
        return $statement->fetchAll(\PDO::FETCH_ASSOC);
    }

    private function table(string $suffix): string
    {
        $name = $this->prefix . $suffix;
        if (!in_array($name, $this->tables, true)) {
            throw new \RuntimeException('A12_TABLE_MISSING');
        }
        return '`' . $name . '`';
    }

    private function option(string $name): string
    {
        $rows = $this->select('SELECT option_value FROM ' . $this->table('options') . ' WHERE option_name=?', [$name]);
        return $rows[0]['option_value'] ?? '';
    }

    private static function read(string $file, int $limit = 16777216): string
    {
        if (is_link($file) || realpath($file) !== $file || !is_file($file) || !is_readable($file) || filesize($file) > $limit) {
            throw new \RuntimeException('A12_SOURCE_UNREADABLE_OR_UNSAFE');
        }
        $text = file_get_contents($file);
        if ($text === false) {
            throw new \RuntimeException('A12_SOURCE_UNREADABLE_OR_UNSAFE');
        }
        return $text;
    }

    private static function tree(string $root): array
    {
        if (is_link($root)) {
            throw new \RuntimeException('A12_SYMLINK_UNSUPPORTED');
        }
        if (!is_dir($root)) {
            return [];
        }
        $files = [];
        $visited = 0;
        $walk = static function (string $dir, int $depth) use (&$walk, &$files, &$visited): void {
            if ($depth > 24) {
                throw new \RuntimeException('A12_SOURCE_LIMIT');
            }
            foreach (new \FilesystemIterator($dir) as $file) {
                if (++$visited > 100000) {
                    throw new \RuntimeException('A12_SOURCE_LIMIT');
                }
                if ($file->isLink()) {
                    throw new \RuntimeException('A12_SYMLINK_UNSUPPORTED');
                }
                if ($file->isDir()) {
                    if (!preg_match('/\A(?:vendor|tests?|fixtures|node_modules|\.git)\z/i', $file->getFilename())) {
                        $walk($file->getPathname(), $depth + 1);
                    }
                } elseif ($file->isFile() && str_ends_with($file->getFilename(), '.php')) {
                    $files[] = $file->getPathname();
                }
            }
        };
        $walk($root, 0);
        sort($files);
        return $files;
    }

    private function declarations(): array
    {
        $sources = [];
        foreach (['post.php', 'taxonomy.php'] as $file) {
            $sources[$this->site . '/wp-includes/' . $file] = 'core';
        }
        foreach (Audit::decode($this->option('active_plugins')) as $plugin) {
            if (!is_string($plugin) || Audit::identifier($plugin) === '[masque]' || !str_ends_with($plugin, '.php')) {
                throw new \RuntimeException('A12_PLUGIN_IDENTIFIER_UNSAFE');
            }
            $main = $this->site . '/wp-content/plugins/' . $plugin;
            $files = str_contains($plugin, '/') ? self::tree(dirname($main)) : [$main];
            foreach ($files as $file) {
                $sources[$file] = 'plugin';
            }
        }
        foreach (glob($this->site . '/wp-content/mu-plugins/*.php') ?: [] as $file) {
            $sources[$file] = 'mu_plugin';
        }
        foreach (array_unique([$this->option('stylesheet'), $this->option('template')]) as $theme) {
            if ($theme === '' || Audit::identifier($theme) === '[masque]' || str_contains($theme, '/')) {
                throw new \RuntimeException('A12_THEME_IDENTIFIER_UNSAFE');
            }
            foreach (self::tree($this->site . '/wp-content/themes/' . $theme) as $file) {
                $sources[$file] = 'theme';
            }
        }
        ksort($sources);
        $result = ['post_types' => [], 'taxonomies' => [], 'unresolved_calls' => 0, 'source_files' => count($sources)];
        foreach ($sources as $file => $owner) {
            $text = self::read($file);
            // Fast lexical prefilter only; no source code is included or evaluated.
            if (!str_contains($text, 'register_post_type') && !str_contains($text, 'register_taxonomy')) {
                continue;
            }
            $found = Declarations::parse($text);
            $result['unresolved_calls'] += $found['unresolved_calls'];
            foreach (['post_types', 'taxonomies'] as $kind) {
                foreach ($found[$kind] as $name) {
                    $result[$kind][$name][] = ['owner' => $owner, 'file' => Audit::identifier(substr($file, strlen($this->site) + 1))];
                }
            }
        }
        return $result;
    }

    private static function publication(?string $value): ?string
    {
        return $value === null || $value === '0000-00-00 00:00:00' ? null : str_replace(' ', 'T', $value) . 'Z';
    }

    private function shape(string $name, string $join, string $where, array $params, array $declarations): array
    {
        $posts = $this->table('posts');
        $states = [];
        foreach ($this->select("SELECT p.post_status,COUNT(DISTINCT p.ID) AS n FROM $posts p $join WHERE $where GROUP BY p.post_status ORDER BY BINARY p.post_status", $params) as $row) {
            $states[Audit::identifier($row['post_status'])] = (int) $row['n'];
        }
        $dates = $this->select("SELECT MIN(NULLIF(p.post_date_gmt,'0000-00-00 00:00:00')) AS first_date,MAX(NULLIF(p.post_date_gmt,'0000-00-00 00:00:00')) AS last_date FROM $posts p $join WHERE $where AND p.post_status='publish'", $params)[0];
        return ['name' => Audit::identifier($name), 'registration' => $declarations ? 'literal_source_candidate_not_runtime_verified' : 'stored_only_registration_unknown',
            'declarations' => $declarations, 'content_count' => array_sum($states), 'states' => $states,
            'first_published_utc' => self::publication($dates['first_date']), 'last_published_utc' => self::publication($dates['last_date'])];
    }

    private function attachments(): array
    {
        $posts = $this->table('posts');
        $meta = $this->table('postmeta');
        $upload = $this->option('upload_path');
        $base = $upload === '' ? $this->site . '/wp-content/uploads' : (str_starts_with($upload, '/') ? $upload : $this->site . '/' . $upload);
        if (!str_starts_with($base . '/', $this->site . '/') || preg_match('~(?:^|/)\.\.?(/|$)|[\x00-\x1f\\\\:]~', $base)) {
            throw new \RuntimeException('A12_UPLOAD_PATH_UNSUPPORTED');
        }
        $rows = $this->select("SELECT a.ID,a.post_mime_type,a.post_parent,parent.ID AS parent_exists,m.meta_value AS attached_path FROM $posts a LEFT JOIN $posts parent ON parent.ID=a.post_parent LEFT JOIN $meta m ON m.post_id=a.ID AND m.meta_key='_wp_attached_file' WHERE a.post_type='attachment' ORDER BY a.ID");
        $seen = [];
        $groups = [];
        $orphan = 0;
        $missing = 0;
        $pdf = 0;
        foreach ($rows as $row) {
            if (isset($seen[$row['ID']])) {
                throw new \RuntimeException('A12_DUPLICATE_ATTACHED_FILE');
            }
            $seen[$row['ID']] = true;
            $mime = preg_match('~\A[a-z0-9.+_-]+/[a-z0-9.+_-]+\z~D', $row['post_mime_type']) ? $row['post_mime_type'] : '[inconnu]';
            $groups[$mime] ??= ['mime' => $mime, 'count' => 0, 'bytes' => 0, 'orphan_count' => 0];
            $groups[$mime]['count']++;
            $pdf += (int) ($mime === 'application/pdf');
            $isOrphan = (int) ((int) $row['post_parent'] === 0 || $row['parent_exists'] === null);
            $orphan += $isOrphan;
            $groups[$mime]['orphan_count'] += $isOrphan;
            $relative = $row['attached_path'];
            if ($relative === null || $relative === '') {
                $missing++;
                continue;
            }
            $path = str_starts_with($relative, '/') ? $relative : $base . '/' . $relative;
            if (!str_starts_with($path, $base . '/') || preg_match('~(?:^|/)\.\.?(/|$)|[\x00-\x1f\\\\:]~', $path)) {
                throw new \RuntimeException('A12_ATTACHMENT_PATH_UNSAFE');
            }
            if (is_link($path) || (realpath($path) !== false && realpath($path) !== $path)) {
                throw new \RuntimeException('A12_ATTACHMENT_PATH_UNSAFE');
            }
            if (!is_file($path)) {
                $missing++;
                continue;
            }
            $groups[$mime]['bytes'] += filesize($path);
        }
        ksort($groups);
        return ['by_mime' => array_values($groups), 'pdf_count' => $pdf, 'orphan_count' => $orphan, 'missing_files' => $missing,
            'size_basis' => 'stat_original_local_attached_file_only_no_derivatives; missing_files_excluded',
            'orphan_basis' => 'parent_zero_or_missing_not_proof_of_unused_media'];
    }

    private function productLinks(): array
    {
        $posts = $this->table('posts');
        $meta = $this->table('postmeta');
        $result = [];
        $keys = $this->select("SELECT DISTINCT meta_key FROM $meta ORDER BY BINARY meta_key");
        foreach ($keys as $row) {
            $key = $row['meta_key'];
            if (!preg_match('/(?:^|_)(?:product|produit|article|numero|issue)(?:_ids?)?(?:_|$)/i', $key)) {
                continue;
            }
            $editorial = static fn(string $alias): string => "$alias.post_type NOT IN ('product','product_variation','attachment','revision','shop_order','shop_order_refund','shop_order_placehold','shop_subscription','shop_coupon','wc_user_membership')";
            $numeric = "m.meta_value REGEXP '^[1-9][0-9]{0,18}$'";
            $pair = "((q.post_type IN ('product','product_variation') AND " . $editorial('p') . ") OR (p.post_type IN ('product','product_variation') AND " . $editorial('q') . '))';
            $match = $this->select("SELECT COUNT(DISTINCT CASE WHEN p.post_type IN ('product','product_variation') THEN q.ID ELSE p.ID END) AS contents,COUNT(DISTINCT p.ID,q.ID) AS pairs FROM $meta m JOIN $posts p ON p.ID=m.post_id JOIN $posts q ON $numeric AND BINARY m.meta_value=BINARY CAST(q.ID AS CHAR) WHERE m.meta_key=? AND $pair", [$key])[0];
            $nonScalar = $this->select("SELECT COUNT(*) AS n FROM $meta m JOIN $posts p ON p.ID=m.post_id WHERE m.meta_key=? AND NOT ($numeric) AND (" . $editorial('p') . " OR p.post_type IN ('product','product_variation'))", [$key])[0]['n'];
            $result[] = ['key' => Audit::identifier($key), 'linked_contents' => (int) $match['contents'], 'distinct_pairs' => (int) $match['pairs'], 'non_scalar_rows' => (int) $nonScalar];
        }
        return $result;
    }

    public function collect(): array
    {
        $declarations = $this->declarations();
        $post = $this->table('posts');
        $meta = $this->table('postmeta');
        $tt = $this->table('term_taxonomy');
        $tr = $this->table('term_relationships');
        $terms = $this->table('terms');
        $types = array_unique(array_merge(array_keys($declarations['post_types']), array_column($this->select("SELECT DISTINCT post_type FROM $post"), 'post_type')));
        sort($types);
        $typeRows = [];
        foreach ($types as $name) {
            $row = $this->shape($name, '', 'p.post_type=?', [$name], $declarations['post_types'][$name] ?? []);
            $keys = [];
            foreach ($this->select("SELECT m.meta_key,COUNT(DISTINCT m.post_id) AS n FROM $meta m JOIN $post p ON p.ID=m.post_id WHERE p.post_type=? GROUP BY BINARY m.meta_key,m.meta_key ORDER BY BINARY m.meta_key", [$name]) as $field) {
                $keys[] = ['key' => Audit::identifier($field['meta_key']), 'content_count' => (int) $field['n']];
            }
            $row['metadata_keys'] = $keys;
            $typeRows[] = $row;
        }
        $taxonomies = array_unique(array_merge(array_keys($declarations['taxonomies']), array_column($this->select("SELECT DISTINCT taxonomy FROM $tt"), 'taxonomy')));
        sort($taxonomies);
        $taxRows = [];
        foreach ($taxonomies as $name) {
            $row = $this->shape($name, "JOIN $tr r ON r.object_id=p.ID JOIN $tt tt ON tt.term_taxonomy_id=r.term_taxonomy_id", 'tt.taxonomy=?', [$name], $declarations['taxonomies'][$name] ?? []);
            $row['term_count'] = (int) $this->select("SELECT COUNT(*) AS n FROM $tt WHERE taxonomy=?", [$name])[0]['n'];
            $row['top_terms'] = [];
            foreach ($this->select("SELECT t.name,COUNT(DISTINCT p.ID) AS n FROM $tt tt JOIN $terms t ON t.term_id=tt.term_id LEFT JOIN $tr r ON r.term_taxonomy_id=tt.term_taxonomy_id LEFT JOIN $post p ON p.ID=r.object_id WHERE tt.taxonomy=? GROUP BY tt.term_taxonomy_id,t.name ORDER BY n DESC,BINARY t.name,tt.term_taxonomy_id LIMIT 20", [$name]) as $term) {
                $termName = strlen($term['name']) <= 200 && !preg_match('/[\x00-\x1f@]|(?:sk_|pk_|rk_|whsec_|xkeysib-|[a-f0-9]{40})/i', $term['name']) ? $term['name'] : '[masque]';
                $row['top_terms'][] = ['name' => $termName, 'content_count' => (int) $term['n']];
            }
            $taxRows[] = $row;
        }
        return ['schema' => 'imagine-a12-content-v1', 'read_only' => true, 'storage' => $this->option('woocommerce_custom_orders_table_enabled') === 'yes' ? 'hpos' : 'classic',
            'registry' => ['runtime_verified' => false, 'coverage' => 'stored_objects_plus_literal_active_source_candidates_not_runtime_registry', 'unresolved_calls' => $declarations['unresolved_calls'], 'source_files' => $declarations['source_files']],
            'post_types' => $typeRows, 'taxonomies' => $taxRows, 'attachments' => $this->attachments(), 'product_links' => $this->productLinks(),
            'conventions' => [
                'Etats: tous contenus stockes, corbeille et brouillons inclus; taxonomies: contenus distincts par taxonomie, pas somme des termes.',
                'Premiere et derniere publication: post_date_gmt des seuls contenus actuellement publish; null si aucun.',
                'Termes: vingt premiers par nombre de contenus distincts relies, tous etats; egalite par nom binaire puis identifiant interne non exporte.',
                'Champs: toutes les cles postmeta, internes incluses, sans limite top-N; comptes de contenus distincts, jamais les valeurs.',
                'Tailles: originaux locaux par MIME enregistre, sans miniatures; aucun telechargement ni appel de filtre tiers.',
                'Liaisons: cles product/produit/article/numero/issue; seules references scalaires canoniques entre contenu et produit/variation, deux directions; structures serialisees non interpretees.',
            ],
            'limitations' => [
                'REGISTRE INCOMPLET: aucun bootstrap. Un appel litteral peut etre conditionnel ou inutilise; un appel dynamique ou une source exclue peut manquer. Jamais une preuve du registre runtime.',
                'Sources: coeur post.php/taxonomy.php, repertoires des extensions actives, MU PHP de premier niveau, themes enfant/parent; vendor/tests/fixtures exclus. Le fichier est une preuve de declaration candidate, pas une attribution runtime certaine.',
                'Site simple, tables InnoDB, configuration litterale et disposition standard. Requetes SELECT dans transaction READ ONLY; aucune action, tache, notification ni HTTP.',
                'Les seuls textes libres permis sont les noms des termes; valeurs suspectes masquees. Aucun titre, contenu, auteur, contact, identifiant de client, valeur de champ ou chemin de media exporte.',
                'Les comptes editoriaux restent dans posts/postmeta dans les deux magasins; aucune lecture des coordonnees de commande HPOS ni interpretation des droits.',
            ]];
    }
}
