<?php

declare(strict_types=1);
namespace Imagine\Site;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Numeros\{Calendrier, Numero, TypeNumero};

/** Raccord WordPress : aucune règle de sélection de C01/C07 recopiée. */
final class EnvoiNatif
{
    public static function calendrier(): Calendrier
    {
        $numeros = [];
        $zone = new DateTimeZone('Europe/Brussels');
        foreach (get_option('imagine_demo_calendrier', []) as $row) {
            foreach (['sortie', 'cloture'] as $key) {
                if (!NumeroPublication::valid($row[$key] ?? null)) {
                    throw new \RuntimeException('Calendrier postal invalide.');
                }
            }
            $numeros[] = new Numero($row['code'], TypeNumero::from($row['type']),
                new DateTimeImmutable($row['sortie'], $zone), new DateTimeImmutable($row['cloture'], $zone));
        }
        return new Calendrier($numeros);
    }

    public const RELEVE = 'imagine_envoi_releve_';

    private static function date(string $value): DateTimeImmutable
    {
        $date = DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $value, new DateTimeZone('UTC'));
        if (!$date || $date->format('Y-m-d H:i:s') !== $value) {
            throw new \RuntimeException('Date native postale invalide.');
        }
        return $date;
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
            'pays' => $sub->get_shipping_country(),
        ];
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
        $events = array_map('maybe_unserialize', $rows);
        usort($events, static fn (array $a, array $b): int => strcmp($a['observe_utc'], $b['observe_utc']));
        return $events;
    }

    public static function register(): void
    {
        add_action('woocommerce_after_order_object_save', static function ($order): void {
            if ($order instanceof \WC_Subscription) {
                self::relever($order);
            }
        });
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
        foreach (wcs_get_subscriptions(['subscriptions_per_page' => -1, 'subscription_status' => 'any']) as $sub) {
            self::relever($sub);
        }
        return self::calculer($code, self::releves(), $now);
    }

    /** Compatibilité des recettes ; horloge, calendrier et logique dans le banc pur. */
    public static function calculer(string $code, array $events, DateTimeImmutable $now): array
    {
        return EnvoiRegles::calculer($code, $events, $now, get_option(self::CALENDRIER));
    }
}
