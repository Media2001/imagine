<?php

declare(strict_types=1);
namespace Imagine\Site;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Numeros\{Calendrier, Numero, TypeNumero};

require_once __DIR__ . '/EnvoiRegles.php';
require_once __DIR__ . '/EnvoiRelations.php';

/** Raccord WordPress : aucune règle de sélection de C01/C07 recopiée. */
final class EnvoiNatif
{
    public static function calendrier(): Calendrier
    {
        $rows = get_option(self::CALENDRIER, null);
        if (!is_array($rows)) { throw new \RuntimeException('Initialisation postale requise.'); }
        return EnvoiRegles::calendrier($rows);
    }

    public const RELEVE = 'imagine_envoi_releve_';
    public const CALENDRIER = 'imagine_envoi_calendrier_reference';
    public const GEL = 'imagine_envoi_gel_';

    public static function initialiser(): void
    {
        $rows = get_option('imagine_demo_calendrier', []);
        EnvoiRegles::calendrier($rows);
        if (get_option(self::CALENDRIER, null) === null) { add_option(self::CALENDRIER, $rows, '', false); }
        $stored = get_option(self::CALENDRIER, null);
        if (!is_array($stored)) { throw new \RuntimeException('Référence postale non persistée.'); }
        EnvoiRegles::reviserCalendrier($stored, $rows, new DateTimeImmutable('now', new DateTimeZone('UTC')));
        if ($stored !== $rows) {
            update_option(self::CALENDRIER, $rows, false);
            if (get_option(self::CALENDRIER) !== $rows) { throw new \RuntimeException('Référence postale non relue.'); }
        }
    }

    /** Un relevé est une observation présente, jamais un paiement ni un passé inventés. */
    public static function relever(\WC_Subscription $sub): array
    {
        $created = $sub->get_date_created();
        if (!$created) {
            throw new \RuntimeException('Création native absente.');
        }
        $data = [
            'id' => (string) $sub->get_id(), 'user' => (string) $sub->get_customer_id(),
            'creation' => $created->getTimestamp(), 'debut' => $sub->get_date('start', 'gmt'),
            'fin' => $sub->get_date('end', 'gmt'), 'etat' => $sub->get_status(),
            'paiement' => $sub->get_date_paid()?->getTimestamp(),
            'grace_debut' => $sub->get_meta('_imagine_acces_grace_debut'),
            'grace_fin' => $sub->get_meta('_imagine_acces_grace_fin'),
            'destinataire' => trim($sub->get_shipping_first_name() . ' ' . $sub->get_shipping_last_name()),
            'rue' => $sub->get_shipping_address_1(), 'complement' => $sub->get_shipping_address_2(),
            'code_postal' => $sub->get_shipping_postcode(), 'ville' => $sub->get_shipping_city(),
            'pays' => $sub->get_shipping_country(), 'renouvellements' => EnvoiRelations::renouvellements($sub),
        ] + EnvoiRelations::beneficiaires($sub);
        return self::enregistrer($data);
    }

    private static function enregistrer(array $data): array
    {
        $events = self::releves($data['id']);
        $last = $events === [] ? null : $events[array_key_last($events)];
        if (($last['donnees'] ?? null) !== $data) {
            $last = ['observe_utc' => (new DateTimeImmutable('now', new DateTimeZone('UTC')))->format('Y-m-d H:i:s.u'), 'donnees' => $data];
            $key = self::RELEVE . $data['id'] . '_' . str_replace('-', '', wp_generate_uuid4());
            if (!add_option($key, $last, '', false) || get_option($key) !== $last) {
                throw new \RuntimeException('Relevé postal indisponible : export refusé.');
            }
        }
        return $last;
    }

    public static function releves(?string $id = null): array
    {
        global $wpdb;
        $prefix = self::RELEVE . ($id === null ? '' : $id . '_');
        $rows = $wpdb->get_col($wpdb->prepare(
            "SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_id",
            $wpdb->esc_like($prefix) . '%'
        ));
        if ($wpdb->last_error) { throw new \RuntimeException('Lecture des relevés indisponible.'); }
        $events = array_map('maybe_unserialize', $rows);
        usort($events, static fn (array $a, array $b): int => strcmp($a['observe_utc'], $b['observe_utc']));
        return $events;
    }

    public static function register(): void
    {
        add_action('woocommerce_after_subscription_object_save', static function ($sub): void {
            if ($sub instanceof \WC_Subscription) { self::relever($sub); }
        });
        add_action('woocommerce_after_order_object_save', static function ($order): void {
            if ($order instanceof \WC_Subscription) {
                self::relever($order);
            } elseif (function_exists('wcs_get_subscriptions_for_renewal_order')) {
                foreach (wcs_get_subscriptions_for_renewal_order($order) as $sub) { self::relever($sub); }
            }
        });
        add_filter('pre_update_option_imagine_demo_calendrier', static function ($value, $old) {
            try {
                EnvoiRegles::reviserCalendrier(get_option(self::CALENDRIER, $old), $value,
                    new DateTimeImmutable('now', new DateTimeZone('UTC')));
                return $value;
            } catch (\Throwable) {
                add_settings_error('imagine_demo_calendrier', 'imagine_envoi_cloture',
                    __('Calendrier refusé : les clôtures et rangs passés sont immuables.', 'imagine-site'));
                return $old;
            }
        }, 10, 2);
        add_action('update_option_imagine_demo_calendrier', static function (): void { self::initialiser(); });
    }

    /** Liste C07 exacte ; C01 fournit les numéros théoriquement dus, sans activation fictive. */
    public static function apercu(string $code): array
    {
        $calendar = self::calendrier();
        $selected = array_values(array_filter($calendar->numeros, static fn (Numero $n): bool => $n->id === $code));
        if ($selected === []) {
            throw new \OutOfBoundsException('Numéro absent du calendrier.');
        }
        if (!function_exists('wcs_get_subscriptions')) {
            throw new \RuntimeException('Subscriptions indisponible.');
        }
        $number = $selected[0];
        $now = new DateTimeImmutable('now', new DateTimeZone('UTC'));
        $key = self::GEL . $code;
        $frozen = get_option($key, null);
        if ($frozen !== null) { return self::relireGel($code, $frozen, $now); }
        $alive = [];
        foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']) as $sub) {
            self::relever($sub);
            $alive[(string) $sub->get_id()] = true;
        }
        $events = self::releves();
        $latest = [];
        foreach ($events as $event) { $latest[$event['donnees']['id']] = $event['donnees']; }
        foreach ($latest as $id => $data) {
            if (!isset($alive[$id]) && $data['etat'] !== 'cancelled') {
                $data['etat'] = 'cancelled';
                $events[] = self::enregistrer($data);
            }
        }
        $view = self::calculer($code, $events, $now);
        if (!$view['provisoire']) {
            $snapshot = ['version' => 1, 'numero' => $code, 'calendrier' => get_option(self::CALENDRIER),
                'observations' => $events, 'cloture' => $number->cloture->format(DATE_ATOM), 'blocs' => $view['blocs']];
            add_option($key, $snapshot, '', false); // Le premier gel gagne en concurrence.
            $frozen = get_option($key, null);
            if ($frozen === null) { throw new \RuntimeException('Gel indisponible : export fermé.'); }
            return self::relireGel($code, $frozen, $now);
        }
        return $view;
    }

    private static function relireGel(string $code, mixed $frozen, DateTimeImmutable $now): array
    {
        if (!is_array($frozen) || ($frozen['version'] ?? null) !== 1 || ($frozen['numero'] ?? null) !== $code) {
            throw new \RuntimeException('Gel postal invalide.');
        }
        $view = EnvoiRegles::calculer($code, $frozen['observations'], $now, $frozen['calendrier']);
        if ($view['provisoire'] || $view['liste']->cloture->format(DATE_ATOM) !== $frozen['cloture']
            || $view['blocs'] !== $frozen['blocs']) {
            throw new \RuntimeException('Référence historique incohérente.');
        }
        return $view;
    }

    /** Compatibilité des recettes ; horloge, calendrier et logique dans le banc pur. */
    public static function calculer(string $code, array $events, DateTimeImmutable $now): array
    {
        return EnvoiRegles::calculer($code, $events, $now, get_option(self::CALENDRIER));
    }
}
