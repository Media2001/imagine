<?php

declare(strict_types=1);

namespace Imagine\PublicAddresses;

/** The native connection is fenced BEFORE wp-settings, including privileged users. */
final class ReadOnlyDb extends \wpdb
{
    public int $blocked = 0;
    private bool $fenced = false;

    public function __construct(string $user, string $password, string $database, string $host)
    {
        parent::__construct($user, $password, $database, $host);
        $this->suppress_errors(true);
        if (parent::query('SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ') === false || parent::query('SET SESSION TRANSACTION READ ONLY') === false || parent::query('START TRANSACTION READ ONLY') === false) {
            throw new \RuntimeException('A11_READONLY_TRANSACTION_FAILED');
        }
        $this->fenced = true;
    }

    public function query($query)
    {
        if ($this->fenced && (!preg_match('/\A\s*(SELECT|SHOW|DESCRIBE|DESC)\b/i', $query) || preg_match('/\b(INTO\s+(OUTFILE|DUMPFILE)|GET_LOCK|RELEASE_LOCK|FOR\s+UPDATE|LOCK\s+IN\s+SHARE)\b/i', $query))) {
            $this->blocked++;
            $this->last_error = 'A11_WRITE_FORBIDDEN';
            return false;
        }
        $result = parent::query($query);
        if ($this->fenced && $result === false) {
            throw new \RuntimeException('A11_READ_FAILED');
        }
        return $result;
    }
}
