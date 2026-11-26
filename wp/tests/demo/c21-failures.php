<?php

declare(strict_types=1);

namespace Imagine\Demo\C21;

use Imagine\Site\{Decouverte, EnvoiNatif, Justificatifs};

if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible C21 refusée.');
}
require_once ABSPATH . 'wp-admin/includes/user.php';
$login = 'imagine-c21-defaut-fictif';
if (get_user_by('login', $login)) {
    throw new \RuntimeException('Collision de fixture : aucun remplacement.');
}
$id = wp_insert_user(['user_login' => $login, 'user_pass' => wp_generate_password(48),
    'user_email' => 'c21-defaut-fictif@example.org', 'role' => 'customer']);
if (is_wp_error($id)) {
    throw new \RuntimeException('Création fictive refusée.');
}
$checks = [];
$path = null;
$backup = null;
$key = EnvoiNatif::RELEVE . 'C21-DEFAUT-FICTIF';
try {
    $doc = Justificatifs::recevoir((int) $id, 'à préciser', "%PDF-1.4\nC21 FICTIF\n%%EOF\n", Justificatifs::version([]));
    $path = Justificatifs::chemin($doc);
    $backup = $path . '.c21-backup';
    if (!rename($path, $backup) || !mkdir($path, 0700)) {
        throw new \RuntimeException('Injection de panne impossible.');
    }
    $erasers = apply_filters('wp_privacy_personal_data_erasers', []);
    $r = call_user_func($erasers['imagine-site']['callback'], 'c21-defaut-fictif@example.org', 1);
    $checks['echec_physique_signale_sans_faux_succes'] = $r['items_retained'] && count($r['messages']) === 1;
    $checks['reference_conservee_si_fichier_non_supprimable'] = Justificatifs::etat((int) $id) === $doc && is_dir($path);
    $response = null;
    $handler = static function () use (&$response): callable {
        return static function ($message, $title, $args) use (&$response): never {
            $response = ['message' => $message, 'title' => $title, 'args' => $args];
            throw new \RuntimeException('C21 wp_die capturé');
        };
    };
    add_filter('wp_die_handler', $handler, PHP_INT_MAX);
    try {
        wp_delete_user((int) $id); // Vraie suppression native : le hook C21 doit interrompre le chemin.
        $checks['suppression_compte_refusee_409_reelle'] = false;
    } catch (\RuntimeException $e) {
        $checks['suppression_compte_refusee_409_reelle'] = $e->getMessage() === 'C21 wp_die capturé'
            && ($response['args']['response'] ?? null) === 409
            && str_contains($response['message'] ?? '', 'nettoyage Imagine incomplet');
    } finally {
        remove_filter('wp_die_handler', $handler, PHP_INT_MAX);
    }
    $checks['refus_409_conserve_compte_et_document'] = (bool) get_userdata((int) $id)
        && Justificatifs::etat((int) $id) === $doc && is_dir($path) && is_file($backup);
    if (!rmdir($path) || !rename($backup, $path)) {
        throw new \RuntimeException('Restauration documentaire impossible.');
    }
    $checks['document_restaure_octets_exacts'] = hash_file('sha256', $path) === hash('sha256', "%PDF-1.4\nC21 FICTIF\n%%EOF\n");
    add_option(Decouverte::key((int) $id), ['debut' => '2026-11-01 00:00:00', 'reglages' => Decouverte::defauts(), 'articles' => []], '', false);
    add_option($key, ['observe_utc' => '2026-11-26', 'donnees' => ['id' => '999997', 'user' => (string) $id]], '', false);
    update_user_meta((int) $id, 'imagine_email_confirme', '1');
    $checks['suppression_compte_native_reussit'] = wp_delete_user((int) $id);
    $checks['hook_suppression_retire_decouverte_et_historique'] = get_option(Decouverte::key((int) $id), null) === null
        && get_option($key, null) === null;
    clearstatcache(true, $path);
    $checks['hook_C17_et_C21_retire_reference_et_document'] = get_option(Justificatifs::PREFIX . $id, null) === null
        && !file_exists($path) && !file_exists($backup);
} finally {
    if ($path && is_dir($path)) {
        rmdir($path);
    }
    if ($backup && is_file($backup)) {
        rename($backup, $path);
    }
    if (get_userdata((int) $id)) {
        wp_delete_user((int) $id);
    }
    delete_option($key);
    $checks['fixture_finalement_absente'] = !get_user_by('login', $login);
}
echo wp_json_encode(['checks' => $checks, 'total' => count($checks),
    'failures' => array_keys(array_filter($checks, static fn ($v): bool => !$v))]);
