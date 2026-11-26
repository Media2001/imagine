<?php

declare(strict_types=1);

// The native class name is the boundary being doubled, not application code.
// phpcs:ignore Squiz.Classes.ValidClassName.NotCamelCaps -- WordPress API compatibility.
final class WP_User
{
    public array $roles;
    public array $allcaps;

    public function __construct(int $id)
    {
        $this->roles = $GLOBALS['a23RoleUsers'][$id]['roles'];
        $this->allcaps = $GLOBALS['a23RoleUsers'][$id]['allcaps'];
    }
}
