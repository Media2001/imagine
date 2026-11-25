<?php

declare(strict_types=1);

namespace Imagine\Demo\C17;

/** Reset strictement limité aux deux comptes synthétiques ; aucun objet commercial. */
function profils(bool $reset = false): array
{
    if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
        || get_option('imagine_demo_site') !== 'imagine-test-demo' || home_url() !== 'http://192.168.129.32:8085'
        || !has_filter('pre_wp_mail') || !has_filter('pre_http_request')) {
        throw new \RuntimeException('C17 refuse cette cible.');
    }
    $manifest = get_option('imagine_c09_fixture');
    $out = [];
    foreach (['P-SOL-ATT', 'P-SOL-OK'] as $code) {
        $id = (int) ($manifest['users'][$code] ?? 0);
        if (!$id || get_user_meta($id, '_imagine_c09_fixture', true) !== $code) {
            throw new \RuntimeException('Profil C09 C17 non possédé.');
        }
        $old = \Imagine\Site\Justificatifs::etat($id);
        if ($old && !$reset) {
            $out[$code] = $old;
            continue;
        }
        $bytes = "%PDF-1.4\n% DOCUMENT FICTIF C17 " . $code . " - AUCUNE PERSONNE REELLE\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF\n";
        $pending = \Imagine\Site\Justificatifs::recevoir($id, 'à préciser', $bytes, \Imagine\Site\Justificatifs::version($old));
        if ($code === 'P-SOL-OK') {
            \Imagine\Site\Justificatifs::verrou($id, static function () use ($id, $pending): void {
                $state = \Imagine\Site\JustificatifRegles::decider($pending, 'valide', gmdate('Y-m-d', time() + 45 * DAY_IN_SECONDS),
                    'fixture-c09-fictive', gmdate('Y-m-d\TH:i:s\Z'));
                \Imagine\Site\Justificatifs::supprimerFichier($pending);
                update_option(\Imagine\Site\Justificatifs::PREFIX . $id, $state, false);
                if (\Imagine\Site\Justificatifs::etat($id) !== $state) {
                    throw new \RuntimeException('Reset C17 non persisté.');
                }
            });
        }
        $out[$code] = \Imagine\Site\Justificatifs::etat($id);
    }
    return $out;
}
