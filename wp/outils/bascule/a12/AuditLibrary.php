<?php

declare(strict_types=1);

namespace Imagine\ContentInventory;

/** Load only the unchanged inert A02 library, never any WordPress file. */
final class AuditLibrary
{
    public static function load(): void
    {
        if (!defined('IMAGINE_AUDIT_LIBRARY_ONLY')) {
            define('IMAGINE_AUDIT_LIBRARY_ONLY', true);
        }
        if (constant('IMAGINE_AUDIT_LIBRARY_ONLY') !== true) {
            throw new \RuntimeException('A12_AUDIT_LIBRARY_GUARD');
        }
        require_once dirname(__DIR__) . '/audit';
    }
}
