<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Lecture native à la demande ; ni cache persistant ni transport. */
final class ContactBrevo
{
    public const PAGE = 'imagine-contact-brevo';
    public const TARIFS = 'imagine_brevo_tarifs';

    public static function register(): void
    {
        add_action('admin_menu', static function (): void {
            if (TableauBordAdmin::autorise()) {
                add_submenu_page('imagine', __('Ce qui partirait vers Brevo', 'imagine-site'),
                    __('Ce qui partirait vers Brevo', 'imagine-site'),
                    current_user_can('manage_options') ? 'manage_options' : TableauBordAdmin::CAP,
                    self::PAGE, [self::class, 'page']);
            }
        }, 121);
        add_action('admin_init', static function (): void {
            if (($_GET['page'] ?? null) === self::PAGE) {
                self::verifier();
            }
        });
        add_filter('woocommerce_prevent_admin_access', static function (bool $prevent): bool {
            global $pagenow;
            return $pagenow === 'admin.php' && ($_GET['page'] ?? null) === self::PAGE
                && TableauBordAdmin::autorise() ? false : $prevent;
        });
    }

    /** Liste fermée produit/variation natif => clé interne ; vide/invalide = tout inconnu. */
    public static function tarifs(mixed $value): array
    {
        if (!is_array($value)) {
            return [];
        }
        foreach ($value as $id => $code) {
            if (!preg_match('/^[1-9][0-9]*$/D', (string)$id)
                || !is_string($code) || !preg_match('/^[a-z][a-z0-9_-]{0,63}$/D', $code)) {
                return [];
            }
        }
        return $value;
    }

    /** WCS non mis en cache persistant, contrairement à get_users_subscriptions. */
    public static function contexte(): array
    {
        if (!function_exists('wcs_get_subscriptions') || !function_exists('wc_memberships_get_user_membership')) {
            throw new \RuntimeException('Source native indisponible.');
        }
        $tarifs = self::tarifs(get_option(self::TARIFS, []));
        $data = ['abonnements' => [], 'beneficiaires' => [], 'tarifs' => $tarifs];
        $seen = [];
        for ($page = 1; ; $page++) {
            $rows = wcs_get_subscriptions(['subscriptions_per_page' => 100, 'paged' => $page,
                'subscription_status' => 'any', 'orderby' => 'ID', 'order' => 'ASC']);
            if (!is_array($rows)) {
                throw new \RuntimeException('Abonnements illisibles.');
            }
            foreach ($rows as $sub) {
                if (!$sub instanceof \WC_Subscription || isset($seen[$sub->get_id()])) {
                    throw new \RuntimeException('Abonnement incohérent.');
                }
                $seen[$sub->get_id()] = true;
                $codes = [];
                foreach ($sub->get_items() as $item) {
                    $product = $item->get_variation_id() ?: $item->get_product_id();
                    $codes[] = $tarifs[$product] ?? '';
                }
                $data['abonnements'][(int)$sub->get_customer_id()][] = ['etat' => $sub->get_status(), 'tarifs' => $codes];
                // Réutilisation du contrat de lecture C13 : aucune déduction par email ou par droits C06.
                $relation = EnvoiRelations::beneficiaires($sub);
                if (in_array($relation['origine'], ['offert', 'groupe'], true)) {
                    foreach ($relation['beneficiaires'] as $person) {
                        $id = (int)$person['id'];
                        if ($id !== (int)$sub->get_customer_id()) {
                            $data['beneficiaires'][$id] = true;
                        }
                    }
                }
            }
            if (count($rows) < 100) {
                break;
            }
        }
        return $data;
    }

    public static function fiche(int $id, ?array $contexte = null): array
    {
        $user = $id > 0 ? get_userdata($id) : false;
        $contexte ??= self::contexte();
        $coop = get_user_meta($id, Cooperateurs::META, true);
        return ContactBrevoRegles::fiche([
            'existe' => (bool)$user, 'email_recevable' => $user && Newsletters::admissible($id),
            'email' => $user ? $user->user_email : '', 'catalogue' => array_column(Newsletters::catalogue(), 'id'),
            'preferences' => Newsletters::preferences($id), 'abonnements' => $contexte['abonnements'][$id] ?? [],
            'beneficiaire' => isset($contexte['beneficiaires'][$id]),
            'cooperateur' => is_array($coop) && ($coop['cooperateur'] ?? false) === true,
            'tarifs_autorises' => array_values($contexte['tarifs']),
            'personnalisation' => Personnalisation::attributsConnecteur($id),
        ]);
    }
}
