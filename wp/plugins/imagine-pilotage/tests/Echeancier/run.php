<?php

declare(strict_types=1);

use Imagine\Pilotage\Echeancier\Planificateur;
use Imagine\Pilotage\Numeros\Activation;
use Imagine\Pilotage\Numeros\Annee;
use Imagine\Pilotage\Numeros\Calendrier;
use Imagine\Pilotage\Numeros\Moteur;
use Imagine\Pilotage\Numeros\Numero;
use Imagine\Pilotage\Numeros\TypeNumero;

spl_autoload_register(static function (string $name): void {
    $prefix = 'Imagine\\Pilotage\\';
    if (str_starts_with($name, $prefix)) {
        $path = __DIR__ . '/../../src/' . str_replace('\\', '/', substr($name, strlen($prefix))) . '.php';
        if (is_file($path)) {
            require_once $path;
        }
    }
});

function c05Date(string $date): DateTimeImmutable
{
    return new DateTimeImmutable($date, new DateTimeZone('Europe/Brussels'));
}

function c05Calendrier(): Calendrier
{
    $numeros = [];
    foreach (range(2026, 2031) as $year) {
        foreach ([1, 4, 7, 10] as $month) {
            $id = sprintf('REG-%d-%02d', $year, $month);
            $numeros[] = new Numero(
                $id,
                TypeNumero::Regulier,
                c05Date(sprintf('%d-%02d-20', $year, $month)),
                c05Date(sprintf('%d-%02d-10', $year, $month))
            );
        }
        $numeros[] = new Numero(
            'HS-' . $year,
            TypeNumero::HorsSerie,
            c05Date($year . '-08-20'),
            c05Date($year . '-08-10')
        );
    }
    return new Calendrier($numeros);
}

function c05Annee(string $date): Annee
{
    return (new Annee(c05Date($date)))->activer(c05Date($date), Activation::Paiement);
}

function c05Assert(bool $condition, string $message): void
{
    global $assertions;
    $assertions++;
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$tests = [];
$assertions = 0;
$tests['initial_quatre_numeros_c01_sans_cinquieme'] = static function (): void {
    $source = new Moteur(c05Calendrier());
    $annee = c05Annee('2027-02-20 12:00:00');
    $plan = (new Planificateur($source))->planifier($annee, $annee->finNumerique(), 7);
    c05Assert(count($plan) === 4, 'Quatre positions initial compris');
    c05Assert(array_map(static fn ($v) => $v->numero->id, $plan) === [
        'REG-2027-04', 'REG-2027-07', 'REG-2027-10', 'REG-2028-01',
    ], 'Identifiants repris de C01');
    c05Assert(array_map(static fn ($v) => $v->date->format('Y-m-d H:i:s'), $plan) === [
        '2027-02-20 12:00:00', '2027-07-03 00:00:00', '2027-10-03 00:00:00', '2028-01-03 00:00:00',
    ], 'Initial remplace date commune du premier numero, pas les trois suivants');
    c05Assert(array_map(static fn ($v) => $v->rang, $plan) === [1, 2, 3, 4], 'Rangs');
    c05Assert($plan[0]->initial && !$plan[1]->initial, 'Initial marque une seule fois');
};

function c05Refuse(callable $action, string $fragment): void
{
    try {
        $action();
    } catch (DomainException | InvalidArgumentException $error) {
        c05Assert(str_contains($error->getMessage(), $fragment), 'Refus précis : ' . $error->getMessage());
        return;
    }
    c05Assert(false, 'Un plan incompatible doit être refusé : ' . $fragment);
}

if (defined('IMAGINE_C05_FIXTURE')) {
    return;
}

$tests['reconduction_commune_et_numeros_suivants'] = static function (): void {
    $source = new Moteur(c05Calendrier());
    $initiale = c05Annee('2027-02-20 12:00:00');
    $debut = $initiale->finNumerique();
    $suite = $source->renouveler($initiale, $debut)->activer($debut, Activation::Paiement);
    $plan = (new Planificateur($source))->planifier($suite, $suite->finNumerique(), 7);
    c05Assert(count($plan) === 4, 'Quatre communes à la reconduction');
    c05Assert(array_map(static fn ($v) => $v->numero->id, $plan) === [
        'REG-2028-04', 'REG-2028-07', 'REG-2028-10', 'REG-2029-01',
    ], 'Quatre suivants C01');
    foreach ($plan as $index => $v) {
        c05Assert(!$v->initial, 'Pas de deuxième initial');
        c05Assert($v->date == $source->echeances($suite, 7)[$index]->lancement, 'Date C01 exacte');
    }
};
$tests['veille_cloture_refus_cinquieme_dans_annee_de_date_a_date'] = static function (): void {
    $source = new Moteur(c05Calendrier());
    $initiale = c05Annee('2027-04-09 12:00:00');
    $suite = $source->renouveler($initiale, $initiale->finNumerique());
    c05Refuse(
        static fn () => (new Planificateur($source))->planifier($suite, c05Date('2029-04-09 12:00:00'), 7),
        'HORS_ENGAGEMENT REG-2028-04'
    );
};

$tests['calendrier_incomplet_refuse_sans_inventer'] = static function (): void {
    $source = new Moteur(new Calendrier(array_slice(c05Calendrier()->numeros, 0, 2)));
    $annee = c05Annee('2026-01-01');
    c05Refuse(
        static fn () => (new Planificateur($source))->planifier($annee, $annee->finNumerique(), 7),
        'CALENDRIER_INCOMPLET'
    );
};
$tests['clotures_identiques_refusees_sans_deplacer'] = static function (): void {
    $n = c05Calendrier()->numeros;
    $n[2] = new Numero($n[2]->id, $n[2]->type, $n[2]->sortie, $n[1]->cloture);
    $source = new Moteur(new Calendrier($n));
    $annee = c05Annee('2026-01-01');
    c05Refuse(
        static fn () => (new Planificateur($source))->planifier($annee, $annee->finNumerique(), 7),
        'DATES_NON_CROISSANTES'
    );
};
$tests['borne_contractuelle_invalide_refusee'] = static function (): void {
    $annee = c05Annee('2027-02-20');
    c05Refuse(
        static fn () => (new Planificateur(new Moteur(c05Calendrier())))->planifier($annee, $annee->debut, 7),
        'FIN_ENGAGEMENT'
    );
};

$tests['marge_obligatoire_et_parametrable'] = static function (): void {
    $annee = c05Annee('2027-02-20 12:00:00');
    $planner = new Planificateur(new Moteur(c05Calendrier()));
    foreach ([0, -1] as $marge) {
        c05Refuse(static fn () => $planner->planifier($annee, $annee->finNumerique(), $marge), 'marge');
    }
    foreach ([1, 3, 7] as $marge) {
        $plan = $planner->planifier($annee, $annee->finNumerique(), $marge);
        c05Assert($plan[1]->date->format('Y-m-d') === sprintf('2027-07-%02d', 10 - $marge), 'Marge injectée');
        c05Assert($plan[0]->date == $annee->debut, 'Initial indépendant de la marge');
    }
};
$tests['jour_cloture_et_lendemain_passent_au_numero_suivant'] = static function (): void {
    $source = new Moteur(c05Calendrier());
    foreach (['2027-04-10 00:00:00', '2027-04-10 12:00:00', '2027-04-11 12:00:00'] as $date) {
        $a = c05Annee($date);
        $plan = (new Planificateur($source))->planifier($a, $a->finNumerique(), 7);
        c05Assert($plan[0]->numero->id === 'REG-2027-07', 'Clôture incluse C01');
        $b = $source->renouveler($a, $a->finNumerique());
        $suite = (new Planificateur($source))->planifier($b, c05Date($date)->modify('+2 years'), 7);
        c05Assert($suite[0]->numero->id === 'REG-2028-07', 'Suivant sans doublon');
    }
};
$tests['fuseau_dst_et_29_fevrier_sont_ceux_de_c01'] = static function (): void {
    $source = new Moteur(c05Calendrier());
    $a = c05Annee('2028-02-29 10:30:00');
    c05Assert($a->finNumerique()->format('Y-m-d H:i:s') === '2029-02-28 10:30:00', 'Anniversaire C01');
    $plan = (new Planificateur($source))->planifier($a, $a->finNumerique(), 7);
    c05Assert($plan[1]->date->format('P') === '+02:00', 'Été C01');
    c05Assert($plan[3]->date->format('P') === '+01:00', 'Hiver C01');
    $utc = $a->debut->setTimezone(new DateTimeZone('UTC'));
    $other = c05Annee($utc->format(DATE_ATOM));
    c05Assert((new Planificateur($source))->planifier($other, $other->finNumerique(), 7)[0]->date == $plan[0]->date, 'Instant absolu');
};
$tests['contre_exemple_a00_cinq_dates_naives_quatre_positions'] = static function (): void {
    $source = new Moteur(c05Calendrier());
    $a = c05Annee('2027-02-20 12:00:00');
    $naives = [$a->debut];
    foreach ($source->calendrier->numeros as $n) {
        if ($n->type === TypeNumero::Regulier && $n->cloture > $a->debut && $n->cloture < $a->finNumerique()) {
            $naives[] = $n->cloture;
        }
    }
    c05Assert(count($naives) === 5, 'Cinq dates si on ajoute toutes les clôtures');
    c05Assert(count((new Planificateur($source))->planifier($a, $a->finNumerique(), 7)) === 4, 'Le premier numéro est payé à la commande');
};
$tests['reconduction_inconnue_si_precedente_incomplete'] = static function (): void {
    $source = new Moteur(new Calendrier(array_slice(c05Calendrier()->numeros, 0, 2)));
    $a = c05Annee('2026-01-01');
    $b = $source->renouveler($a, $a->finNumerique());
    c05Refuse(static fn () => (new Planificateur($source))->planifier($b, c05Date('2028-01-01'), 7), 'CALENDRIER_INCOMPLET');
};

// One test for every day, not only three hand-picked successful dates.
for ($jour = c05Date('2027-01-01 12:00:00'); $jour < c05Date('2028-01-01'); $jour = $jour->modify('+1 day')) {
    $date = $jour->format('Y-m-d H:i:s');
    $tests['annee_complete_' . $jour->format('Y-m-d')] = static function () use ($date): void {
        $source = new Moteur(c05Calendrier());
        $a = c05Annee($date);
        $planner = new Planificateur($source);
        $p = $planner->planifier($a, $a->finNumerique(), 7);
        c05Assert(count($p) === 4, 'Quatre initial compris');
        c05Assert(array_map(static fn ($v) => $v->numero->id, $p) === array_map(static fn ($n) => $n->id, $source->numeros($a)), 'C01 seul sélectionne');
        $b = $source->renouveler($a, $a->finNumerique())->activer($a->finNumerique(), Activation::Paiement);
        $premiereCommune = $source->echeances($b, 7)[0]->lancement;
        if ($premiereCommune < $b->debut) {
            c05Refuse(static fn () => $planner->planifier($b, $b->finNumerique(), 7), 'HORS_ENGAGEMENT');
        } else {
            $suite = $planner->planifier($b, $b->finNumerique(), 7);
            c05Assert(count($suite) === 4, 'Reconduction quatre');
            $dates = array_map(static fn ($v) => $v->date, [...$p, ...$suite]);
            c05Assert(count(array_filter($dates, static fn ($d) => $d >= $a->debut && $d < $a->finNumerique())) === 4, 'Pas de cinquième avant anniversaire');
        }
    };
}

$results = [];
foreach ($tests as $name => $test) {
    try {
        $test();
        $results[] = ['test' => $name, 'pass' => true];
    } catch (Throwable $e) {
        $results[] = ['test' => $name, 'pass' => false, 'error' => $e::class . ': ' . $e->getMessage()];
    }
}
$failed = count(array_filter($results, static fn (array $r): bool => !$r['pass']));
echo 'C05_JSON=' . json_encode([
    'tests' => count($results), 'assertions' => $assertions, 'failed' => $failed, 'results' => $results,
], JSON_UNESCAPED_UNICODE) . "\n";
exit($failed === 0 ? 0 : 1);
