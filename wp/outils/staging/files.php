<?php

declare(strict_types=1);

namespace Imagine\Staging;

use FilesystemIterator;
use RecursiveDirectoryIterator;
use RecursiveIteratorIterator;
use RuntimeException;

/** Ne lit jamais le contenu des archives, imports ou journaux : uniquement unlink/rmdir. */
final class Files
{
    private string $root;
    private const PLUGIN = 'wp-content/mu-plugins/000-imagine-staging-safety.php';
    public function __construct(string $root)
    {
        $real = realpath($root);
        if ($real === false || is_link($root) || strlen($real) < 8 || !is_dir($real . '/wp-content')
            || is_link($real . '/.imagine-staging-offline')
            || !is_file($real . '/.imagine-staging-offline')
            || file_get_contents($real . '/.imagine-staging-offline') !== "OFFLINE_COPY\n") {
            throw new RuntimeException('RACINE_HORS_LIGNE_REFUSEE');
        }
        $this->root = str_replace('\\', '/', $real);
    }
    private function entries(): array
    {
        $out = [];
        $iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($this->root, FilesystemIterator::SKIP_DOTS), RecursiveIteratorIterator::CHILD_FIRST);
        foreach ($iterator as $entry) {
            if ($entry->isLink()) {
                throw new RuntimeException('LIEN_SYMBOLIQUE_REFUSE');
            }
            $path = str_replace('\\', '/', $entry->getPathname());
            $relative = substr($path, strlen($this->root) + 1);
            $out[] = [$path, $relative, $entry->isDir()];
        }
        return $out;
    }
    private static function forbidden(string $relative): bool
    {
        $code = (bool) preg_match('~^(?:wp-admin/|wp-includes/|wp-content/(?:plugins|themes|languages)/)~', $relative);
        $archive = (bool) preg_match('~\.(?:sql|sqlite|sqlite3|db|dump|zip|tar|gz|gzip|tgz|bz2|xz|zst|lz4|7z|rar|wpress|wpstg|bak|old|log)(?:\.[^/]*)?$~i', $relative);
        $data = !$code && (bool) preg_match('~(?:^|/)[^/]*(?:backup|back-up|dump|archive|import|export|updraft|ai1wm|wpvivid|duplicator|wflogs|wc-logs|cache)[^/]*(?:/|$)|\.(?:csv|tsv|xls|xlsx|ods|xml|jsonl|vcf|ics)(?:\.[^/]*)?$~i', $relative);
        return $archive || $data
            || in_array($relative, ['wp-content/advanced-cache.php', 'wp-content/object-cache.php'], true);
    }
    public function purge(): void
    {
        $entries = $this->entries(); // Inventaire complet sans lien AVANT toute suppression.
        foreach ($entries as [$path, $relative, $directory]) {
            if (self::forbidden($relative)) {
                $ok = $directory ? rmdir($path) : unlink($path);
                if (!$ok || file_exists($path)) {
                    throw new RuntimeException('PURGE_ECHOUEE');
                }
            }
        }
        $destination = $this->root . '/' . self::PLUGIN;
        if (!is_dir(dirname($destination)) && !mkdir(dirname($destination), 0755, true)) {
            throw new RuntimeException('MU_REPERTOIRE_ECHOUE');
        }
        $source = __DIR__ . '/mu-plugins/000-imagine-staging-safety.php';
        $data = file_get_contents($source);
        if ($data === false || file_put_contents($destination, $data, LOCK_EX) !== strlen($data)) {
            throw new RuntimeException('MU_ECRITURE_ECHOUEE');
        }
        $this->verify();
    }
    public function verify(): void
    {
        foreach ($this->entries() as [$path, $relative]) {
            if (self::forbidden($relative)) {
                throw new RuntimeException('ARCHIVE_IMPORT_OU_DROPIN_PRESENT');
            }
        }
        $installed = $this->root . '/' . self::PLUGIN;
        if (!is_file($installed) || !hash_equals(hash_file('sha256', __DIR__ . '/mu-plugins/000-imagine-staging-safety.php'), hash_file('sha256', $installed))) {
            throw new RuntimeException('MU_ABSENT_OU_MODIFIE');
        }
    }

    /** Noms relatifs seulement : aucune lecture de source ou valeur importée. */
    public function inventory(): array
    {
        $mu = [];
        $dropins = [];
        foreach ($this->entries() as [$_, $relative, $directory]) {
            if (!$directory && str_starts_with($relative, 'wp-content/mu-plugins/') && $relative !== self::PLUGIN) {
                $mu[] = substr($relative, strlen('wp-content/mu-plugins/'));
            }
            if (in_array($relative, ['wp-content/db.php', 'wp-content/sunrise.php', 'wp-content/db-error.php',
                'wp-content/install.php', 'wp-content/maintenance.php', 'wp-content/fatal-error-handler.php',
                'wp-content/php-error.php'], true)) {
                $dropins[] = basename($relative);
            }
        }
        sort($mu);
        sort($dropins);
        return ['mu_plugins' => $mu, 'drop_ins' => $dropins,
            'warnings' => array_merge($mu ? ['MU_PRODUCTION_CONSERVES'] : [], $dropins ? ['DROPINS_NON_CACHE_CONSERVES'] : [])];
    }
}
