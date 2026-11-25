<?php

declare(strict_types=1);

namespace Imagine\Site;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Numeros\{Calendrier, Numero, TypeNumero, Moteur};
use Imagine\Pilotage\Envoi\{Abonnement, Destinataire, Situation, ListeEnvoi};

/** Règles C13 pures : aucune fonction WordPress, horloge et observations injectées. */
final class EnvoiRegles
{
    public static function date(string $value): DateTimeImmutable
    {
        $date = DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $value, new DateTimeZone('UTC'));
        if (!$date || $date->format('Y-m-d H:i:s') !== $value) {
            throw new \RuntimeException('Date native postale invalide.');
        }
        return $date;
    }

    public static function calendrier(array $rows): Calendrier
    {
        $numbers = [];
        foreach ($rows as $row) {
            $dates = [];
            foreach (['sortie', 'cloture'] as $key) {
                $value = $row[$key] ?? '';
                $date = is_string($value) ? DateTimeImmutable::createFromFormat('!Y-m-d', $value,
                    new DateTimeZone('Europe/Brussels')) : false;
                if (!$date || $date->format('Y-m-d') !== $value) {
                    throw new \RuntimeException('Calendrier postal invalide.');
                }
                $dates[$key] = $date;
            }
            $numbers[] = new Numero($row['code'], TypeNumero::from($row['type']), $dates['sortie'], $dates['cloture']);
        }
        return new Calendrier($numbers);
    }

    public static function calculer(string $code, array $events, DateTimeImmutable $now, array $rows): array
    {
        $calendar = self::calendrier($rows);
        $selected = array_values(array_filter($calendar->numeros, static fn (Numero $n): bool => $n->id === $code));
        if ($selected === []) {
            throw new \OutOfBoundsException('Numéro absent du calendrier.');
        }
        $number = $selected[0];
        usort($events, static fn (array $a, array $b): int => strcmp($a['observe_utc'], $b['observe_utc']));
        $groups = [];
        foreach ($events as $event) {
            $groups[$event['donnees']['id']][] = $event;
        }
        $subscriptions = $exclusions = $blocks = [];
        $blocked = false;
        foreach ($groups as $id => $history) {
            $situations = [];
            $last = $history[array_key_last($history)]['donnees'];
            $creation = new DateTimeImmutable('@' . $history[0]['donnees']['creation']);
            $reason = $creation >= $number->cloture ? 'cree_apres_cloture' : 'historique_indisponible';
            foreach ($history as $event) {
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
                $engine = new Moteur($calendar);
                $year = $engine->ouvrir($start);
                $years = [[$year, $data['paiement']]];
                $renewals = $data['renouvellements'] ?? [];
                usort($renewals, static fn (array $a, array $b): int => strcmp($a['debut'], $b['debut']));
                $seen = [];
                foreach ($renewals as $renewal) {
                    if (isset($seen[$renewal['id']])) {
                        throw new \LogicException('Renouvellement natif en double.');
                    }
                    $seen[$renewal['id']] = true;
                    $renewed = self::date($renewal['debut']);
                    if ($renewal['paiement'] === null || $renewal['paiement'] >= $number->cloture->getTimestamp()
                        || $renewed >= $number->cloture) {
                        continue;
                    }
                    $year = $engine->renouveler($year, $renewed);
                    $years[] = [$year, $renewal['paiement']];
                }
                $due = [];
                $paid = false;
                $blocks[(string) $id] = [];
                foreach ($years as [$block, $payment]) {
                    $ids = array_map(static fn (Numero $n): string => $n->id, $engine->numeros($block));
                    if ($hs = $engine->horsSerie($block)) {
                        $ids[] = $hs->id;
                    }
                    $blocks[(string) $id][] = ['debut' => $block->debut->format(DATE_ATOM), 'numeros' => $ids,
                        'non_resolus' => $engine->nonResolus($block)];
                    if (in_array($code, $ids, true)) {
                        $paid = $payment !== null && $payment < $number->cloture->getTimestamp();
                    }
                    $due = array_values(array_unique([...$due, ...$ids]));
                }
                $origin = $data['origine'] ?? 'abonnement';
                $resolved = $origin === 'abonnement' || ($data['beneficiaires_resolus'] ?? false);
                $people = $origin === 'abonnement'
                    ? [new Destinataire($data['user'], $data['destinataire'], $data['rue'], $data['complement'],
                        $data['code_postal'], $data['ville'], $data['pays'])]
                    : array_map(static fn (array $p): Destinataire => new Destinataire($p['id'], $p['nom'],
                        $p['rue'], $p['complement'], $p['code_postal'], $p['ville'], $p['pays']),
                        $data['beneficiaires'] ?? []);
                $resolved = $resolved && ($origin !== 'offert' || count($people) === 1)
                    && ($origin !== 'groupe' || count($people) <= ($data['places'] ?? 0));
                if (!$resolved) {
                    $state = 'suspendu';
                    $people = [];
                }
                // Un seul état retenu par observation ; les bénéficiaires libres ne sont pas des personnes.
                $situations[] = new Situation(max($start, $recorded), $recorded, $state, $paid, $due, $people, $end);
                $last = $data;
                $reason = match (true) {
                    !$resolved => 'beneficiaires_non_resolus',
                    $state === 'expire', $end !== null && $end <= $number->cloture => 'expire',
                    $state === 'suspendu' => 'suspendu', $state === 'attente' => 'virement_non_valide',
                    !$paid && $state !== 'grace' => 'paiement_non_valide',
                    !in_array($code, $due, true) => 'numero_non_du', default => 'non_eligible',
                };
            }
            $subscriptions[] = new Abonnement((string) $id, $last['origine'] ?? 'abonnement', $creation, $situations);
            $exclusions[(string) $id] = ['abonnement_id' => (string) $id,
                'destinataire' => $last['destinataire'], 'motif' => $reason];
            $blocked = $blocked || in_array($reason, ['historique_indisponible', 'beneficiaires_non_resolus'], true);
        }
        $list = ListeEnvoi::etablir($number, $calendar, $subscriptions, $number->cloture);
        $belgium = 0;
        foreach ($list->lignes as $row) {
            unset($exclusions[$row['abonnement_id']]);
            $belgium += $row['pays'] === 'BE' ? 1 : 0;
        }
        return ['liste' => $list, 'exclus' => array_values($exclusions), 'belgique' => $belgium,
            'etranger' => count($list->lignes) - $belgium, 'historique_incomplet' => $blocked,
            'provisoire' => $now < $number->cloture, 'blocs' => $blocks];
    }
}
