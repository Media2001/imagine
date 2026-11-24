<?php

/** Banc isolé : vrais fichiers et vrai contrôleur ; seules les API WP sont doublées. */
declare(strict_types=1);

namespace {
    final class WP_Post
    {
        public function __construct(
            public int $ID = 1,
            public string $post_type = 'imagine_numero',
            public string $post_status = 'publish',
            public string $post_mime_type = ''
        ) {
        }
    }
    function get_post($id): ?WP_Post { return $GLOBALS['posts'][(int) $id] ?? null; }
    function get_post_meta($id, $key, $single = true): mixed { return $GLOBALS['meta'][$id][$key] ?? ''; }
    function update_post_meta($id, $key, $value): void { $GLOBALS['meta'][$id][$key] = $value; }
    function delete_post_meta($id, $key): void { unset($GLOBALS['meta'][$id][$key]); }
    function get_current_blog_id(): int { return 1; }
    function home_url($path): string { return 'http://example.org' . $path; }
    function site_url($path): string { return home_url($path); }
    function add_query_arg($key, $value, $url): string { return $url . '?' . $key . '=' . $value; }
    function wp_slash($value): mixed { return $value; }
    function wp_update_post($data, $error = false): int {
        foreach ($data as $key => $value) {
            if ($key !== 'ID' && property_exists($GLOBALS['posts'][$data['ID']], $key)) {
                $GLOBALS['posts'][$data['ID']]->$key = $value;
            }
        }
        return $data['ID'];
    }
    function is_wp_error($value): bool { return false; }
    function __($text, $domain): string { return $text; }
    function esc_html__($text, $domain): string { return $text; }
    function esc_html($text): string { return htmlspecialchars($text); }
    function esc_attr($text): string { return htmlspecialchars($text); }
    function esc_url($text): string { return htmlspecialchars($text); }
    function get_permalink($post): string { return 'http://example.org/numeros/1/'; }
    function wp_login_url($redirect): string { return 'http://example.org/login'; }
    function nocache_headers(): void {}
    function status_header($code): void { $GLOBALS['status'] = $code; }
    function wp_safe_redirect($url, $status): void {
        $GLOBALS['status'] = $status;
        $GLOBALS['redirect'] = $url;
    }
    function wp_die($text, $title, $args): never {
        $GLOBALS['status'] = $args['response'];
        echo $text;
        exit;
    }
    function is_attachment(): bool { return $GLOBALS['attachment_request'] ?? false; }
    function get_queried_object_id(): int { return 2; }
}
namespace Imagine\Site {
    final class Paywall
    {
        public static function decisionPdf(\WP_Post $post): array
        {
            if ($GLOBALS['decision_error'] ?? false) {
                throw new \RuntimeException('Panne synthétique.');
            }
            return $GLOBALS['decision'];
        }
    }
    function header(string $header, bool $replace = true): void {
        [$key, $value] = array_pad(explode(':', $header, 2), 2, '');
        $GLOBALS['headers'][strtolower($key)] = trim($value);
    }
    function header_remove(string $key): void { unset($GLOBALS['headers'][strtolower($key)]); }
}
namespace {
    $scenario = json_decode($argv[1], true, 512, JSON_THROW_ON_ERROR);
    $temp = rtrim(getenv('TMPDIR') ?: sys_get_temp_dir(), '/\\') . '/imagine-c11-' . bin2hex(random_bytes(8));
    mkdir($temp, 0700);
    mkdir($temp . '/public');
    mkdir($temp . '/private');
    define('ABSPATH', $temp . '/public/');
    $_SERVER['DOCUMENT_ROOT'] = ABSPATH;
    define('IMAGINE_PDF_PRIVATE_DIR', $temp . '/' . ($scenario['directory'] ?? 'private'));
    $GLOBALS['posts'] = [1 => new WP_Post(), 2 => new WP_Post(2, 'attachment', 'inherit', 'application/pdf')];
    $GLOBALS['meta'] = [1 => ['imagine_pdf_id' => 2]];
    $GLOBALS['decision'] = ['complet' => $scenario['complete'] ?? false, 'bloc' => $scenario['bloc'] ?? 'connexion'];
    $GLOBALS['headers'] = ['etag' => 'old', 'last-modified' => 'old'];
    $GLOBALS['status'] = 200;
    $GLOBALS['decision_error'] = $scenario['decision_error'] ?? false;
    require dirname(__DIR__) . '/PdfNumero.php';
    ob_start();
    register_shutdown_function(static function () use ($temp): void {
        $body = ob_get_clean();
        $result = ['status' => $GLOBALS['status'], 'headers' => $GLOBALS['headers'],
            'redirect' => $GLOBALS['redirect'] ?? null, 'body' => base64_encode($body),
            'value' => $GLOBALS['value'] ?? null, 'error' => $GLOBALS['error'] ?? null];
        $remove = static function (string $path) use (&$remove): void {
            if (is_dir($path) && !is_link($path)) {
                foreach (new DirectoryIterator($path) as $item) {
                    if (!$item->isDot()) { $remove($item->getPathname()); }
                }
                rmdir($path);
            } else { unlink($path); }
        };
        $remove($temp);
        echo json_encode($result, JSON_THROW_ON_ERROR);
    });
    try {
        $pdf = '%PDF-1.4 C11 FICTIF';
        $source = $temp . '/public/source.pdf';
        file_put_contents($source, $pdf);
        switch ($scenario['action']) {
            case 'boundary':
                $method = new ReflectionMethod(\Imagine\Site\PdfNumero::class, 'withinDirectory');
                $GLOBALS['value'] = $method->invoke(null, $scenario['path'], $scenario['root'], $scenario['windows']);
                break;
            case 'directory':
                if (in_array($scenario['directory'] ?? '', ['public/child', 'public-private'], true)) { mkdir($temp . '/' . $scenario['directory']); }
                $GLOBALS['value'] = \Imagine\Site\PdfNumero::directory();
                break;
            case 'protect-copies':
                $copy = $temp . '/public/stale.pdf';
                if ($scenario['blocked']) {
                    mkdir($copy);
                } else {
                    file_put_contents($copy, $pdf);
                }
                \Imagine\Site\PdfNumero::protect(1, 2, $source, [$copy]);
                clearstatcache();
                $GLOBALS['value'] = !file_exists($copy) && !file_exists($source);
                break;
            case 'protect':
                \Imagine\Site\PdfNumero::protect(1, 2, $source);
                clearstatcache();
                $GLOBALS['value'] = !file_exists($source) && file_get_contents(\Imagine\Site\PdfNumero::path(1)) === $pdf;
                break;
            case 'path':
            case 'block':
            case 'serve':
                \Imagine\Site\PdfNumero::protect(1, 2, $source);
                $path = \Imagine\Site\PdfNumero::path(1);
                switch ($scenario['fault'] ?? '') {
                    case 'missing': unlink($path); break;
                    case 'corrupt': file_put_contents($path, 'PAS UN PDF'); break;
                    case 'traversal': $GLOBALS['meta'][1]['_imagine_pdf_blob'] = '../source.pdf'; break;
                    case 'wrong-type': $GLOBALS['posts'][1]->post_type = 'post'; break;
                }
                if ($scenario['action'] === 'path') {
                    $GLOBALS['value'] = \Imagine\Site\PdfNumero::path(1);
                } elseif ($scenario['action'] === 'block') {
                    echo \Imagine\Site\PdfNumero::block(get_post(1));
                } else {
                    $_GET = array_key_exists('raw', $scenario) ? ['imagine_pdf' => $scenario['raw']] : [];
                    $_SERVER['REQUEST_METHOD'] = $scenario['method'] ?? 'GET';
                    $GLOBALS['attachment_request'] = $scenario['attachment'] ?? false;
                    if ($scenario['draft'] ?? false) { $GLOBALS['posts'][1]->post_status = 'draft'; }
                    \Imagine\Site\PdfNumero::serve();
                }
                break;
            default: throw new RuntimeException('Scénario inconnu.');
        }
    } catch (Throwable $error) {
        $GLOBALS['error'] = $error->getMessage();
    }
}
