<?php

declare(strict_types=1);

namespace Imagine\Demo\C17;

/** PDF synthétique lisible, généré ici : aucune source ni identité réelle. */
function document(string $code): string
{
    $text = 'BT /F1 16 Tf 50 760 Td (DOCUMENT FICTIF C17 - ' . $code . ') Tj 0 -35 Td (AUCUNE PERSONNE REELLE) Tj ET';
    $objects = ['<< /Type /Catalog /Pages 2 0 R >>', '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
        '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
        '<< /Length ' . strlen($text) . ">>\nstream\n" . $text . "\nendstream"];
    $pdf = "%PDF-1.4\n";
    $offsets = [0];
    foreach ($objects as $i => $object) {
        $offsets[] = strlen($pdf);
        $pdf .= ($i + 1) . " 0 obj\n" . $object . "\nendobj\n";
    }
    $xref = strlen($pdf);
    $pdf .= "xref\n0 6\n0000000000 65535 f \n";
    foreach (array_slice($offsets, 1) as $offset) {
        $pdf .= sprintf("%010d 00000 n \n", $offset);
    }
    return $pdf . "trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n" . $xref . "\n%%EOF\n";
}

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
        $bytes = document($code);
        $category = \Imagine\Site\JustificatifsReglages::categories()[0];
        $pending = \Imagine\Site\Justificatifs::recevoir($id, $category, $bytes, \Imagine\Site\Justificatifs::version($old));
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
