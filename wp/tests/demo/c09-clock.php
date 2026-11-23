<?php
/** Horloge du générateur : frontières UTC, avec vrais objets puis restauration. */
declare(strict_types=1);
namespace Imagine\Demo\C09ClockTests;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') { throw new \RuntimeException('Cible refusée.'); }
$checks = [];
$helper = WP_CONTENT_DIR . '/imagine-demo-build/c09-calendar.php';
$checks['horloge_injectable_disponible'] = is_file($helper);
if ($checks['horloge_injectable_disponible']) {
    require_once $helper;
    $seed = WP_CONTENT_DIR . '/imagine-demo-build/c09-seed.php';
    $cases = ['2026-11-30 23:59:59' => '2026-11-30 23:59:59',
        '2026-12-31 23:59:59' => '2026-12-31 23:59:59',
        '2027-01-01 00:00:00' => '2027-01-01 01:00:00'];
    $proof = [];
    try {
        foreach ($cases as $instant => $due) {
            $GLOBALS['imagine_c09_now'] = new \DateTimeImmutable($instant, new \DateTimeZone('UTC'));
            $checks[$instant . ':calcul_exact'] = \Imagine\Demo\C09\papierDue(\Imagine\Demo\C09\now()) === $due;
            ob_start(); (static function ($path): void { require $path; })($seed); ob_end_clean();
            $f = get_option('imagine_c09_fixture');
            $s = wcs_get_subscription($f['subscriptions']['A-PAPIER']);
            $proof[$instant] = ['next_payment' => $s->get_date('next_payment'), 'manual' => $s->is_manual()];
            $checks[$instant . ':objet_natif_exact'] = $s->get_date('next_payment') === $due && $s->is_manual();
            $checks[$instant . ':ce_mois_inclus_derniere_seconde'] = substr($s->get_date('next_payment'), 0, 7) === substr($instant, 0, 7)
                && $s->get_date('next_payment') >= $instant;
        }
    } finally {
        unset($GLOBALS['imagine_c09_now']);
        ob_start(); (static function ($path): void { require $path; })($seed); ob_end_clean();
    }
    $f = get_option('imagine_c09_fixture');
    $restored = wcs_get_subscription($f['subscriptions']['A-PAPIER']);
    $checks['horloge_reelle_restauree_et_relue'] = substr($restored->get_date('next_payment'), 0, 7) === gmdate('Y-m')
        && abs(strtotime($restored->get_date('start') . ' UTC') - (time() - 335 * DAY_IN_SECONDS)) < 120;
}
$failures = array_keys(array_filter($checks, static fn ($v) => !$v));
echo wp_json_encode(['total' => count($checks), 'checks' => $checks, 'failures' => $failures, 'proof' => $proof ?? []]);
if ($failures) { \WP_CLI::halt(1); }
