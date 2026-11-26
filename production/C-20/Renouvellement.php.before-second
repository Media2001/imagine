<?php

declare(strict_types=1);
namespace Imagine\Site;

require_once __DIR__ . '/RenouvellementRegles.php';

/** Deuxième passe partielle : aucun changement d'état/dates ni contournement natif. */
final class Renouvellement
{
    /** Réservé au futur succès natif vérifié ; non émis dans cette livraison bloquée. */
    public const HOOK_CONFIRMATION = 'imagine_renouvellement_confirme';

    public static function register(): void
    {
        add_action('imagine_compte_renouvellement', [self::class, 'afficher']);
        add_filter('wcs_view_subscription_actions', [self::class, 'actions'], PHP_INT_MAX, 3);
    }

    private static function vue(\WC_Subscription $sub): array
    {
        return RenouvellementRegles::presentation([
            'status' => $sub->get_status(), 'manual' => $sub->get_requires_manual_renewal(),
            'method' => EcheancesNatives::methode($sub), 'period' => $sub->get_billing_period(),
            'interval' => $sub->get_billing_interval(), 'end' => $sub->get_date('end', 'gmt'),
        ], new \DateTimeImmutable('now', new \DateTimeZone('UTC')));
    }

    public static function actions(array $actions, $sub, int $user): array
    {
        // Cette retenue est propre au site de démonstration autorisé, pas une politique réelle.
        if (wp_get_environment_type() === 'local' && get_option('imagine_demo_site') === 'imagine-test-demo'
            && $sub instanceof \WC_Subscription && home_url() === 'http://192.168.129.32:8085') {
            unset($actions['cancel'], $actions['reactivate']);
        }
        return $actions;
    }

    public static function afficher(array $b02): void
    {
        $sub = wcs_get_subscription((int) ($b02['id'] ?? 0));
        if (!$sub || !get_current_user_id() || (int) $sub->get_customer_id() !== get_current_user_id()) {
            return;
        }
        $view = self::vue($sub);
        echo '<aside data-imagine-renouvellement="' . esc_attr($view['mode']) . '"><h4>'
            . esc_html__('Renouvellement', 'imagine-site') . '</h4><p>'
            . esc_html(__($view['message'], 'imagine-site')) . '</p>';
        if (EcheancesNatives::fictif($sub, 'A-CARTE')) {
            echo '<p>' . esc_html__('Profil fictif A-CARTE : souscription manuelle, moyen de paiement vide ; aucune carte ni passerelle raccordée.', 'imagine-site') . '</p>';
        }
        if (isset($view['fin'])) {
            echo '<dl><dt>' . esc_html__('Date de fin native', 'imagine-site') . '</dt><dd>'
                . esc_html(wp_date('j F Y H:i', strtotime($view['fin'] . ' UTC'), wp_timezone()))
                . '</dd><dt>' . esc_html__('Numéros du bloc — même projection que Mon compte', 'imagine-site') . '</dt><dd>'
                . esc_html(($b02['premier'] ?? __('Non raccordé', 'imagine-site')) . ' — ' . ($b02['dernier'] ?? __('Non raccordé', 'imagine-site')))
                . '</dd><dt>' . esc_html__('Numéros encore dus', 'imagine-site') . '</dt><dd>'
                . esc_html($b02['restants'] === null ? __('Compteur non raccordé — historique d’activation C01 manquant', 'imagine-site') : (string) $b02['restants']) . '</dd></dl>';
        }
        echo '</aside>';
    }
}
