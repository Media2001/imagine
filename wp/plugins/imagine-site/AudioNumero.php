<?php

declare(strict_types=1);

namespace Imagine\Site;

use WP_Post;

/** B11 : même stockage et mêmes en-têtes C11, décision PDF C06 à chaque requête. */
final class AudioNumero
{
    public const META = '_imagine_audio_blob';

    public static function url(int $issue): string
    {
        return add_query_arg('imagine_audio', $issue, home_url('/'));
    }

    public static function path(int $issue): string
    {
        $post = get_post($issue);
        $name = get_post_meta($issue, self::META, true);
        if (!$post || $post->post_type !== 'imagine_numero' || !is_string($name)
            || !preg_match('/\A[a-f0-9]{32}\.wav\z/D', $name)) {
            throw new \RuntimeException('Audio indisponible.');
        }
        $path = PdfNumero::directory() . '/' . $name;
        if (is_link($path) || !is_file($path) || !is_readable($path)) {
            throw new \RuntimeException('Audio indisponible.');
        }
        $head = @file_get_contents($path, false, null, 0, 12);
        if (!is_string($head) || substr($head, 0, 4) !== 'RIFF' || substr($head, 8, 4) !== 'WAVE') {
            throw new \RuntimeException('Audio indisponible.');
        }
        return $path;
    }

    /** Dépôt local explicite dans le répertoire privé C11, jamais un média public. */
    public static function proteger(int $issue, string $source): void
    {
        $post = get_post($issue);
        $directory = PdfNumero::directory();
        if (!$post || $post->post_type !== 'imagine_numero' || is_link($source) || !is_file($source)
            || dirname((string) realpath($source)) !== realpath($directory)) {
            throw new \RuntimeException('Source audio privée requise.');
        }
        $bytes = file_get_contents($source);
        if (!is_string($bytes) || strlen($bytes) < 44 || strlen($bytes) > 20 * 1024 * 1024
            || substr($bytes, 0, 4) !== 'RIFF' || substr($bytes, 8, 4) !== 'WAVE') {
            throw new \RuntimeException('Source audio invalide.');
        }
        $name = get_post_meta($issue, self::META, true);
        if (!is_string($name) || !preg_match('/\A[a-f0-9]{32}\.wav\z/D', $name)) {
            $name = bin2hex(random_bytes(16)) . '.wav';
        }
        $target = $directory . '/' . $name;
        if (is_link($target) || file_put_contents($target, $bytes, LOCK_EX) !== strlen($bytes)
            || !chmod($target, 0600) || file_get_contents($target) !== $bytes) {
            throw new \RuntimeException('Écriture audio refusée.');
        }
        update_post_meta($issue, self::META, $name);
        if (get_post_meta($issue, self::META, true) !== $name) {
            throw new \RuntimeException('Audio non persisté.');
        }
    }

    public static function lecteur(WP_Post $issue): string
    {
        if (!Paywall::decisionPdf($issue)['complet']) {
            return '<p>' . esc_html__('Le sommaire audio est réservé aux ayants droit du numéro.', 'imagine-site') . '</p>';
        }
        try {
            self::path($issue->ID);
        } catch (\Throwable) {
            return '<p>' . esc_html__('Aucun sommaire audio disponible.', 'imagine-site') . '</p>';
        }
        return '<audio data-imagine-audio controls preload="none" src="' . esc_url(self::url($issue->ID)) . '">'
            . esc_html__('Votre navigateur ne permet pas la lecture audio.', 'imagine-site') . '</audio>';
    }

    public static function serve(): void
    {
        if (!isset($_GET['imagine_audio'])) {
            return;
        }
        PdfNumero::privateHeaders();
        $raw = $_GET['imagine_audio'];
        if (!is_string($raw) || !preg_match('/\A[1-9][0-9]*\z/D', $raw)
            || !($issue = get_post((int) $raw)) || $issue->post_type !== 'imagine_numero' || $issue->post_status !== 'publish') {
            wp_die(esc_html__('Audio indisponible.', 'imagine-site'), '', ['response' => 404]);
        }
        if (!in_array($_SERVER['REQUEST_METHOD'] ?? 'GET', ['GET', 'HEAD'], true)) {
            header('Allow: GET, HEAD');
            wp_die(esc_html__('Méthode refusée.', 'imagine-site'), '', ['response' => 405]);
        }
        $handle = false;
        try {
            if (Paywall::decisionPdf($issue)['complet']) {
                $handle = @fopen(self::path($issue->ID), 'rb');
                $head = $handle ? fread($handle, 12) : '';
                if (!$handle || substr($head, 0, 4) !== 'RIFF' || substr($head, 8, 4) !== 'WAVE' || fseek($handle, 0) !== 0) {
                    throw new \RuntimeException('Audio indisponible.');
                }
            }
        } catch (\Throwable) {
            if (is_resource($handle)) {
                fclose($handle);
            }
            $handle = false;
        }
        if (!is_resource($handle)) {
            wp_safe_redirect(get_permalink($issue), 302);
            exit;
        }
        status_header(200);
        header('Content-Type: audio/wav', true);
        header('Content-Disposition: inline; filename="imagine-sommaire-' . $issue->ID . '.wav"', true);
        header('Content-Length: ' . fstat($handle)['size'], true);
        if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'HEAD') {
            fpassthru($handle);
        }
        fclose($handle);
        exit;
    }

    public static function register(): void
    {
        add_action('template_redirect', [self::class, 'serve'], -101);
    }
}
