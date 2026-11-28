<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Refus avant insertion, uniquement aux frontières publiques natives. */
final class DomainesRefuses
{
    public const OPTION = 'imagine_domaines_refuses';

    public static function register(): void
    {
        add_filter('registration_errors', [self::class, 'inscription'], 30, 3);
        add_filter('woocommerce_registration_errors', [self::class, 'inscription'], 30, 3);
        add_action('woocommerce_save_account_details_errors', [self::class, 'compte'], 30, 2);
        // get_posted_data est évalué avant update_session (qui écrit billing_email).
        add_filter('woocommerce_checkout_posted_data', [self::class, 'commande'], 1, 1);
    }

    public static function configuration(): array
    {
        return DomainesRefusesRegles::liste(get_option(self::OPTION, [])) ?? [];
    }

    private static function valider(\WP_Error $errors, string $email): \WP_Error
    {
        if (DomainesRefusesRegles::refuse($email, self::configuration())) {
            $errors->add('imagine_adresse_alternative', __('Cette adresse ne peut pas être utilisée pour créer ou modifier votre compte. Merci d’utiliser une autre adresse email.', 'imagine-site'));
        }
        return $errors;
    }

    public static function inscription(\WP_Error $errors, string $username, string $email): \WP_Error
    {
        // Les écrans de création de l'administration n'utilisent normalement
        // pas ces filtres. L'exception n'ouvre jamais un AJAX public.
        if (is_admin() && current_user_can('create_users') && !wp_doing_ajax()) {
            return $errors;
        }
        return self::valider($errors, $email);
    }

    public static function commande(array $data): array
    {
        if (
            !is_user_logged_in()
            && (!empty($data['createaccount']) || WC()->checkout()->is_registration_required())
            && isset($data['billing_email'])
            && is_string($data['billing_email'])
        ) {
            $errors = self::valider(new \WP_Error(), $data['billing_email']);
            if ($errors->has_errors()) {
                // process_checkout attrape cette exception et affiche le message neutre.
                // Ni session client ni commande ne reçoivent l'adresse refusée.
                throw new \Exception($errors->get_error_message());
            }
        }
        return $data;
    }

    public static function compte(\WP_Error $errors, object $user): void
    {
        $current = isset($user->ID) ? get_userdata((int) $user->ID) : false;
        if (
            $current && isset($user->user_email) && is_string($user->user_email)
            && strcasecmp($user->user_email, $current->user_email) !== 0
        ) {
            self::valider($errors, $user->user_email);
        }
    }
}
