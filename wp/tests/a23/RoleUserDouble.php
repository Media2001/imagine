<?php

declare(strict_types=1);

namespace Imagine\ReaderAccountsRoleTest;

// Aliased to the native WP_User boundary only in the separate role-probe process.
final class RoleUserDouble
{
    public array $roles;
    public array $allcaps;

    public function __construct(int $id)
    {
        $this->roles = $GLOBALS['a23RoleUsers'][$id]['roles'];
        $this->allcaps = $GLOBALS['a23RoleUsers'][$id]['allcaps'];
    }
}
