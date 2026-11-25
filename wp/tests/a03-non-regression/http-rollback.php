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
        private int $optionsSequence = 0;

        public function begin(): void
        {
            $this->optionsSequence = (int) $this->get_var(
                "SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()"
                . " AND TABLE_NAME='wp_options'"
            );
            if (parent::query('START TRANSACTION') === false) {
                throw new RuntimeException('A03_FIXTURE_WEB_BEGIN');
            }
            $this->probe = true;
        }

        public function finish(): void
        {
            $this->probe = false;
            parent::query('ROLLBACK');
            // InnoDB does not roll back allocated option IDs. Restore the exact
            // synthetic sequence as well; schema/rows are checked independently.
            if ($this->optionsSequence < 1 || parent::query(
                'ALTER TABLE wp_options AUTO_INCREMENT=' . $this->optionsSequence
            ) === false) {
                throw new RuntimeException('A03_FIXTURE_WEB_SEQUENCE');
            }
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
