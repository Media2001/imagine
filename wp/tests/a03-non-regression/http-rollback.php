<?php

declare(strict_types=1);

// Fixture-only HTTP rollback adapter. Native web bootstraps need a writer (for
// transient refreshes); reusing the subject's SELECT account causes SQL errors.
// Execute those writes for real, but never commit them. Not deployed by A03.
if (PHP_SAPI === 'cli-server') {
    require_once ABSPATH . 'wp-includes/plugin.php';
    require_once ABSPATH . 'wp-includes/class-wpdb.php';
    $GLOBALS['wpdb'] = new class ('root', '', DB_NAME, DB_HOST) extends wpdb {
        private bool $probe = false;
        public function begin(): void
        {
            if (parent::query('START TRANSACTION') === false) {
                throw new RuntimeException('A03_FIXTURE_WEB_BEGIN');
            }
            $this->probe = true;
        }

        public function finish(): void
        {
            $this->probe = false;
            parent::query('ROLLBACK');
        }

        public function query($query)
        {
            if ($this->probe && preg_match('/\A\s*(?:START|BEGIN|COMMIT|ROLLBACK|SAVEPOINT|RELEASE)\b/i', $query)) {
                return 0;
            }
            if (
                $this->probe
                && preg_match('/\A\s*(?:CREATE|ALTER|DROP|TRUNCATE|RENAME|GRANT|REVOKE|LOCK|UNLOCK)\b/i', $query)
            ) {
                throw new RuntimeException('A03_FIXTURE_WEB_DDL');
            }
            return parent::query($query);
        }
    };
    $GLOBALS['wpdb']->begin();
    register_shutdown_function(static function (): void {
        $GLOBALS['wpdb']->finish();
    });
}
