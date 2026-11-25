<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Même marqueur que les comptes sans email de la liste d'envoi C13. */
final class SansEmail
{
    public const META = 'imagine_sans_email';

    /** Garde individuelle, complément du coupe-circuit global de la démo. */
    public static function filtrer(mixed $return, array $atts): mixed
    {
        $addresses = (array) ($atts['to'] ?? []);
        foreach ((array) ($atts['headers'] ?? []) as $header) {
            foreach (preg_split('/\r?\n/', (string) $header) as $line) {
                if (preg_match('/^\s*(?:cc|bcc)\s*:/i', $line)) {
                    $addresses[] = $line;
                }
            }
        }
        foreach ($addresses as $address) {
            preg_match_all('/[a-z0-9.!#$%&\x27*+\/=?^_`{|}~-]+@[a-z0-9.-]+/i', (string) $address, $matches);
            foreach ($matches[0] as $email) {
                $email = strtolower(rtrim($email, '.'));
                $user = get_user_by('email', $email);
                if (str_ends_with($email, '.invalid') || ($user && get_user_meta($user->ID, self::META, true) === '1')) {
                    return false; // Refuser tout le message, ne jamais dérouter un destinataire.
                }
            }
        }
        return $return;
    }

    public static function register(): void
    {
        add_filter('pre_wp_mail', [self::class, 'filtrer'], PHP_INT_MAX, 2);
    }
}
