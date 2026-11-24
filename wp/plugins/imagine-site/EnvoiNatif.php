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

    /** Entrées de relevés explicites pour éprouver le gel sans antidater le natif. */
    public static function calculer(string $code, array $events, DateTimeImmutable $now): array
    {
        $calendar = self::calendrier();
        $selected = array_values(array_filter($calendar->numeros, static fn (Numero $n): bool => $n->id === $code));
        if ($selected === []) {
            throw new \OutOfBoundsException('Numéro absent du calendrier.');
        }
        $number = $selected[0];
        $groups = [];
        foreach ($events as $event) {
            $groups[$event['donnees']['id']][] = $event;
        }
        $subscriptions = $exclusions = [];
        $blocked = false;
        foreach ($groups as $id => $events) {
            $situations = [];
            $last = $events[array_key_last($events)]['donnees'];
            $creation = new DateTimeImmutable('@' . $events[0]['donnees']['creation']);
            $reason = $creation >= $number->cloture ? 'cree_apres_cloture' : 'historique_indisponible';
            foreach ($events as $event) {
                $recorded = new DateTimeImmutable($event['observe_utc'], new DateTimeZone('UTC'));
                if ($recorded >= $number->cloture) {
                    continue;
                }
                $data = $event['donnees'];
                $start = self::date($data['debut']);
                $end = $data['fin'] === '' ? null : self::date($data['fin']);
                $state = match ($data['etat']) {
                    'active', 'pending-cancel' => 'actif', 'expired', 'cancelled' => 'expire',
                    'pending' => 'attente', default => 'suspendu',
                };
                if ($data['etat'] === 'on-hold' && $data['grace_debut'] !== '' && $data['grace_fin'] !== '') {
                    $from = self::date($data['grace_debut']);
                    $until = self::date($data['grace_fin']);
                    $reference = min($now, $number->cloture->modify('-1 microsecond'));
                    if ($from <= $reference && $reference < $until) {
                        $state = 'grace';
                        $end = $end === null ? $until : min($end, $until);
                    }
                }
                $engine = new \Imagine\Pilotage\Numeros\Moteur($calendar);
                $year = $engine->ouvrir($start);
                $due = array_map(static fn (Numero $n): string => $n->id, $engine->numeros($year));
                if ($hs = $engine->horsSerie($year)) {
                    $due[] = $hs->id;
                }
                $paid = $data['paiement'] !== null && $data['paiement'] < $number->cloture->getTimestamp();
                $person = new \Imagine\Pilotage\Envoi\Destinataire($data['user'], $data['destinataire'],
                    $data['rue'], $data['complement'], $data['code_postal'], $data['ville'], $data['pays']);
                $situations[] = new \Imagine\Pilotage\Envoi\Situation(max($start, $recorded), $recorded,
                    $state, $paid, $due, [$person], $end);
                $reason = match (true) {
                    $state === 'expire', $end !== null && $end <= $number->cloture => 'expire',
                    $state === 'suspendu' => 'suspendu', $state === 'attente' => 'virement_non_valide',
                    !$paid && $state !== 'grace' => 'paiement_non_valide',
                    !in_array($code, $due, true) => 'numero_non_du', default => 'non_eligible',
                };
            }
            $subscriptions[] = new \Imagine\Pilotage\Envoi\Abonnement((string) $id, 'abonnement', $creation, $situations);
            $exclusions[(string) $id] = ['abonnement_id' => (string) $id,
                'destinataire' => $last['destinataire'], 'motif' => $reason];
            $blocked = $blocked || $reason === 'historique_indisponible';
        }
        $list = \Imagine\Pilotage\Envoi\ListeEnvoi::etablir($number, $calendar, $subscriptions, $number->cloture);
        $belgium = 0;
        foreach ($list->lignes as $row) {
            unset($exclusions[$row['abonnement_id']]);
            $belgium += $row['pays'] === 'BE' ? 1 : 0;
        }
        return ['liste' => $list, 'exclus' => array_values($exclusions), 'belgique' => $belgium,
            'etranger' => count($list->lignes) - $belgium, 'historique_incomplet' => $blocked,
            'provisoire' => $now < $number->cloture];
    }
}
