<?php

declare(strict_types=1);

use Imagine\Site\Medias;
use Imagine\Site\AudioNumero;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[$name] = $ok;
    if (!$ok) {
        throw new RuntimeException('B11 : ' . $name);
    }
};
$check('adaptateurs_charges', class_exists(Medias::class) && class_exists(AudioNumero::class));
$issue = (int) $GLOBALS['b11_issue'];
$article = (int) $GLOBALS['b11_article'];
$u = get_option('imagine_c09_fixture')['users'];
$video = 'https://video-fictive.example.invalid/B11_VIDEO_FICTIVE?a=1&b=2';
$podcast = 'https://podcast-fictif.example.invalid/B11_PODCAST_FICTIF';
update_option(Medias::OPTION, ['hosts' => ['video-fictive.example.invalid'], 'integration' => '0'], false);
$check('saisie_valide', Medias::enregistrer($article, $video, $podcast));
$check('readback_metadonnees', get_post_meta($article, Medias::VIDEO, true) === $video && get_post_meta($article, Medias::PODCAST, true) === $podcast);
$check('mauvais_hote_refuse', !Medias::enregistrer($article, 'https://evil.invalid/video', $podcast));
$check('refus_preserve', get_post_meta($article, Medias::VIDEO, true) === $video);
$check('antislash_refuse_sans_perte', !Medias::enregistrer($article, $video . '\\bad', $podcast) && get_post_meta($article, Medias::VIDEO, true) === $video);
wp_set_current_user((int) $u['A-CARTE']);
$positive = Medias::rendre(get_post($article));
$check('temoin_ayant_droit', str_contains(html_entity_decode($positive), $video) && str_contains($positive, $podcast));
wp_set_current_user(0);
$check('anonyme_ni_lien_ni_adresse', Medias::rendre(get_post($article)) === '');
wp_set_current_user((int) $u['V-INSCRIT']);
$check('connecte_sans_droit_ferme', Medias::rendre(get_post($article)) === '');
foreach (['0', '1'] as $setting) {
    update_option(Medias::OPTION, ['hosts' => ['video-fictive.example.invalid'], 'integration' => $setting], false);
    wp_set_current_user((int) $u['A-CARTE']);
    $html = Medias::rendre(get_post($article));
    $check('integration_' . $setting, substr_count($html, 'data-imagine-video-emplacement') === (int) $setting && !preg_match('/<(iframe|script|img)\b/i', $html));
}
$check('reglage_inconnu_ferme', Medias::nettoyer(['hosts' => ['video-fictive.example.invalid'], 'integration' => 'yes'])['integration'] === '0');
$check('liste_hotes_invalide_conserve', Medias::nettoyer(['hosts' => ['https://evil.invalid'], 'integration' => '0']) === Medias::configuration());
wp_set_current_user((int) $u['P-NUMERO']);
$check('audio_acheteur_numero', str_contains(AudioNumero::lecteur(get_post($issue)), 'imagine_audio=' . $issue));
wp_set_current_user((int) $u['A-CARTE']);
$activeIssue = (int) get_option('imagine_b11_fixture')['issue_active'];
$check('audio_abonne_actif_numero_couvert', str_contains(AudioNumero::lecteur(get_post($activeIssue)), 'imagine_audio=' . $activeIssue));
$check('audio_anterieur_ferme_par_C06', !str_contains(AudioNumero::lecteur(get_post($issue)), 'imagine_audio='));
$path = AudioNumero::path($issue);
$check('audio_hors_webroot', !str_starts_with(realpath($path), realpath(ABSPATH) . '/') && dirname($path) === Imagine\Site\PdfNumero::directory());
$bytes = file_get_contents($path);
$check('silence_wave_3_secondes', strlen($bytes) === 48044 && substr($bytes, 0, 4) === 'RIFF' && substr($bytes, 8, 4) === 'WAVE' && substr($bytes, 44) === str_repeat("\0", 48000));
wp_set_current_user(0);
$check('audio_anonyme_sans_adresse', !str_contains(AudioNumero::lecteur(get_post($issue)), 'imagine_audio'));
echo wp_json_encode(['checks' => $checks, 'total' => count($checks)]);
