<?php

declare(strict_types=1);

namespace Imagine\Site;

final class AgendaRegles
{
    public static function inscription(string $type, int $debut, int $maintenant): bool
    {
        return in_array($type, ['sortie', 'rencontre'], true) && $debut > $maintenant;
    }

    public static function email(string $email): string
    {
        return strtolower(trim($email));
    }

    public static function cle(int $evenement, string $email): string
    {
        return 'imagine_agenda_' . hash('sha256', $evenement . ':' . self::email($email));
    }
}
