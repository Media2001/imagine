<?php

declare(strict_types=1);

namespace Imagine\Site;

use WP_Post;

/** Stockage hors document root, jamais de livraison statique ou d'URL de fichier. */
final class PdfNumero
{
    public static function directory(): string
    {
        $public = realpath(ABSPATH);
        $root = realpath(dirname(rtrim(ABSPATH, '/\\')) . '/imagine-private-pdf');
        if (!$public || !$root || is_link(dirname(rtrim(ABSPATH, '/\\')) . '/imagine-private-pdf')
            || $root === $public || str_starts_with($root . '/', $public . '/')) {
            throw new \RuntimeException('Stockage PDF privé indisponible.');
        }
        $path = $root . '/site-' . get_current_blog_id();
        if (is_link($path) || (!is_dir($path) && !mkdir($path, 0700))) {
            throw new \RuntimeException('Répertoire PDF privé indisponible.');
        }
        return $path;
    }

    public static function url(int $issue): string
    {
        return add_query_arg('imagine_pdf', $issue, home_url('/'));
    }

    public static function path(int $issue): string
    {
        $post = get_post($issue);
        $name = get_post_meta($issue, '_imagine_pdf_blob', true);
        if (!$post || $post->post_type !== 'imagine_numero' || !is_string($name)
            || !preg_match('/\A[a-f0-9]{32}\.pdf\z/D', $name)) {
            throw new \RuntimeException('Référence PDF invalide.');
        }
        $path = self::directory() . '/' . $name;
        if (is_link($path) || !is_file($path) || !is_readable($path)) {
            throw new \RuntimeException('PDF indisponible.');
        }
        return $path;
    }

    /** Import explicite local : le numéro et le média gardent leurs identifiants natifs. */
    public static function protect(int $issue, int $attachment, string $source): void
    {
        $post = get_post($issue);
        $media = get_post($attachment);
        if (!$post || $post->post_type !== 'imagine_numero' || !$media || $media->post_type !== 'attachment'
            || $media->post_mime_type !== 'application/pdf'
            || (int) get_post_meta($issue, 'imagine_pdf_id', true) !== $attachment) {
            throw new \RuntimeException('Association PDF invalide.');
        }
        $bytes = file_get_contents($source);
        if (!is_string($bytes) || !str_starts_with($bytes, '%PDF-')) {
            throw new \RuntimeException('Source PDF invalide.');
        }
        $name = get_post_meta($issue, '_imagine_pdf_blob', true);
        if (!is_string($name) || !preg_match('/\A[a-f0-9]{32}\.pdf\z/D', $name)) {
            $name = bin2hex(random_bytes(16)) . '.pdf';
        }
        $target = self::directory() . '/' . $name;
        if (is_link($target)) {
            throw new \RuntimeException('Cible PDF invalide.');
        }
        if (!is_file($target) || file_get_contents($target) !== $bytes) {
            if (file_put_contents($target, $bytes, LOCK_EX) !== strlen($bytes) || !chmod($target, 0600)
                || file_get_contents($target) !== $bytes) {
                throw new \RuntimeException('Écriture PDF refusée.');
            }
        }
        update_post_meta($issue, '_imagine_pdf_blob', $name);
        update_post_meta($attachment, '_imagine_pdf_numero', $issue);
        // Aucun chemin physique ou ancien URL dans les sorties médias natives.
        delete_post_meta($attachment, '_wp_attached_file');
        delete_post_meta($attachment, '_wp_attachment_metadata');
        $result = wp_update_post(wp_slash(['ID' => $attachment, 'post_status' => 'private',
            'guid' => self::url($issue), 'post_content' => '', 'post_excerpt' => '']), true);
        if (is_wp_error($result) || get_post_meta($issue, '_imagine_pdf_blob', true) !== $name
            || get_post($attachment)->post_status !== 'private') {
            throw new \RuntimeException('Protection PDF non persistée.');
        }
        // L'appelant supprime aussi toutes ses copies de travail publiques exactes.
        $public = realpath(ABSPATH);
        $realSource = realpath($source);
        if ($public && $realSource && str_starts_with($realSource, $public . '/') && !unlink($source)) {
            throw new \RuntimeException('Ancien PDF public non retiré.');
        }
    }

    private static function issueForMedia(int $attachment): int
    {
        $issue = (int) get_post_meta($attachment, '_imagine_pdf_numero', true);
        if ($issue && (int) get_post_meta($issue, 'imagine_pdf_id', true) === $attachment) {
            return $issue;
        }
        return 0;
    }

    public static function block(WP_Post $issue): string
    {
        $decision = Paywall::decisionPdf($issue);
        if ($decision['complet']) {
            try {
                self::path($issue->ID);
                return '';
            } catch (\Throwable) {
                $decision = ['bloc' => 'abonnement'];
            }
        }
        $bloc = $decision['bloc'];
        $text = match ($bloc) {
            'connexion' => __('Connectez-vous pour consulter vos droits au PDF de ce numéro.', 'imagine-site'),
            'regularisation' => __('Votre abonnement doit être régularisé pour accéder au PDF.', 'imagine-site'),
            default => __('Le PDF de ce numéro est réservé aux ayants droit.', 'imagine-site'),
        };
        return '<aside data-imagine-pdf-bloc="' . esc_attr($bloc) . '"><p>' . esc_html($text)
            . '</p><a href="' . esc_url(wp_login_url(get_permalink($issue))) . '">'
            . esc_html__('Connexion', 'imagine-site') . '</a></aside>';
    }

    private static function privateHeaders(): void
    {
        nocache_headers();
        header('Cache-Control: private, no-store, no-cache, must-revalidate, max-age=0', true);
        header('Vary: Cookie, Authorization, User-Agent', true);
        header_remove('ETag');
        header_remove('Last-Modified');
        header('X-Content-Type-Options: nosniff', true);
        header('X-Robots-Tag: noindex, noarchive', true);
    }

    public static function serve(): void
    {
        if (!isset($_GET['imagine_pdf'])) {
            if (is_attachment() && ($issue = self::issueForMedia(get_queried_object_id()))) {
                self::privateHeaders();
                wp_safe_redirect(get_permalink($issue), 302);
                exit;
            }
            return;
        }
        self::privateHeaders();
        $raw = $_GET['imagine_pdf'];
        if (!is_string($raw) || !preg_match('/\A[1-9][0-9]*\z/D', $raw)) {
            wp_die(esc_html__('PDF indisponible.', 'imagine-site'), '', ['response' => 404]);
        }
        $issue = get_post((int) $raw);
        if (!$issue || $issue->post_type !== 'imagine_numero' || $issue->post_status !== 'publish') {
            wp_die(esc_html__('PDF indisponible.', 'imagine-site'), '', ['response' => 404]);
        }
        if (!in_array($_SERVER['REQUEST_METHOD'] ?? 'GET', ['GET', 'HEAD'], true)) {
            header('Allow: GET, HEAD');
            wp_die(esc_html__('Méthode refusée.', 'imagine-site'), '', ['response' => 405]);
        }
        $handle = false;
        try {
            if (Paywall::decisionPdf($issue)['complet']) {
                $handle = fopen(self::path($issue->ID), 'rb');
                if (!$handle || fread($handle, 5) !== '%PDF-' || fseek($handle, 0) !== 0) {
                    throw new \RuntimeException('PDF invalide.');
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
        header('Content-Type: application/pdf', true);
        header('Content-Disposition: attachment; filename="imagine-numero-' . $issue->ID . '.pdf"', true);
        header('Content-Length: ' . fstat($handle)['size'], true);
        // Aucune URL physique ni X-Sendfile/X-Accel : chaque GET réévalue les droits.
        if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'HEAD') {
            fpassthru($handle);
        }
        fclose($handle);
        exit;
    }

    public static function register(): void
    {
        add_action('template_redirect', [self::class, 'serve'], -100);
        add_filter('wp_get_attachment_url', static function ($url, int $id) {
            $issue = self::issueForMedia($id);
            return $issue ? self::url($issue) : $url;
        }, PHP_INT_MAX, 2);
        add_filter('rest_prepare_attachment', static function ($response, WP_Post $post) {
            return self::issueForMedia($post->ID)
                ? new \WP_Error('imagine_pdf_prive', __('Média privé.', 'imagine-site'), ['status' => 404]) : $response;
        }, PHP_INT_MAX, 2);
    }
}
