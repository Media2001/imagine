<?php

declare(strict_types=1);

namespace Imagine\A28Tests;

use Imagine\Staging\Store;

final class MemoryStore implements Store
{
    public array $tables;
    private array $saved = [];
    public bool $view = false;

    public function __construct()
    {
        $this->tables = [
            'x_options' => [
                ['option_id' => 1, 'option_name' => 'home', 'option_value' => 'https://fiction.test'],
                ['option_id' => 2, 'option_name' => 'siteurl', 'option_value' => 'https://fiction.test'],
                ['option_id' => 3, 'option_name' => 'cron', 'option_value' => 'a:0:{}'],
                ['option_id' => 4, 'option_name' => 'blog_public', 'option_value' => '0'],
                ['option_id' => 5, 'option_name' => 'active_plugins', 'option_value' => 'a:0:{}'],
            ],
            'x_users' => [], 'x_usermeta' => [], 'x_posts' => [], 'x_postmeta' => [], 'x_comments' => [],
        ];
    }

    public function database(): string
    {
        return 'a28_test';
    }

    public function schema(): array
    {
        $columns = [];
        foreach ($this->tables as $table => $rows) {
            $columns[$table] = $rows ? array_keys(reset($rows)) : [];
        }
        return $columns;
    }

    public function details(): array
    {
        return ['tables' => ['x_fluentform_submissions' => ['type' => $this->view ? 'VIEW' : 'BASE TABLE']]];
    }

    public function rows(string $table): array
    {
        return array_values($this->tables[$table]);
    }

    public function begin(): void
    {
        $this->saved = $this->tables;
    }

    public function commit(): void
    {
        $this->saved = [];
    }

    public function rollback(): void
    {
        $this->tables = $this->saved;
    }

    public function replace(string $table, array $before, ?array $after): void
    {
        foreach ($this->tables[$table] as $key => $row) {
            if ($row === $before) {
                if ($after === null) {
                    unset($this->tables[$table][$key]);
                } else {
                    $this->tables[$table][$key] = $after;
                }
                return;
            }
        }
        throw new \RuntimeException('A28_CAS');
    }

    public function insert(string $table, array $row): int
    {
        $row['option_id'] = count($this->tables[$table]) + 1;
        $this->tables[$table][] = $row;
        return $row['option_id'];
    }
}
