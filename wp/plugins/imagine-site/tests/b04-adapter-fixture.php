<?php

/** Banc hors réseau : vrai Paywall, vrai raccord et moteur C06 ; seules API WP/SQL doublées. */
declare(strict_types=1);

if (PHP_SAPI !== 'cli' || !isset($argv[1])) {
    http_response_code(404);
    exit;
}
define('DAY_IN_SECONDS', 86400);
final class WP_Post
{
    public function __construct(public int $ID, public string $post_type = 'post', public string $post_status = 'publish')
    {
    }
}
final class C12Database
{
    public string $options = 'wp_options';
    public string $last_error = '';
    public function prepare(string $query, mixed ...$values): array { return [$query, $values]; }
    public function get_var(array $query): mixed { return $GLOBALS['stored'][$query[1][0]] ?? null; }
    public function query(array $query): int|false
    {
        [$sql, $args] = $query;
        if ($GLOBALS['deny_write'] ?? false) { return false; }
        if (str_starts_with($sql, 'INSERT IGNORE')) {
            if (isset($GLOBALS['stored'][$args[0]])) { return 0; }
            $GLOBALS['stored'][$args[0]] = $args[1];
            return 1;
        }
        if (str_starts_with($sql, 'UPDATE') && ($GLOBALS['stored'][$args[1]] ?? null) === $args[2]) {
            $GLOBALS['stored'][$args[1]] = $args[0];
            return 1;
        }
        return 0;
    }
}
function get_option($key, $default = false): mixed { return $GLOBALS['options'][$key] ?? $default; }
function get_current_user_id(): int { return 7; }
function get_current_blog_id(): int { return 1; }
function get_userdata($id): object { return (object) ['first_name' => 'Fictif', 'last_name' => 'C12', 'user_email' => 'c12@example.org', 'roles' => []]; }
function get_user_meta($id, $key, $single = true): string { return $GLOBALS['verified'] ?? '1'; }
function is_email($email): bool { return filter_var($email, FILTER_VALIDATE_EMAIL) !== false; }
function maybe_serialize($value): string { return serialize($value); }
function maybe_unserialize($value): mixed { return unserialize($value); }
function wp_cache_delete($key, $group): void {}
function get_post($id): ?WP_Post { return $GLOBALS['posts'][$id] ?? null; }
function get_post_meta($id, $key, $single = true): mixed { return $GLOBALS['meta'][$id][$key] ?? ''; }
function metadata_exists($type, $id, $key): bool { return array_key_exists($key, $GLOBALS['meta'][$id] ?? []); }
function wp_timezone(): DateTimeZone { return new DateTimeZone('UTC'); }
final class WC_Order
{
    public function get_type(): string { return 'shop_order'; }
    public function get_customer_id(): int { return 7; }
    public function get_date_paid($context): DateTimeImmutable { return new DateTimeImmutable('2000-01-01 UTC'); }
    public function get_id(): int { return 901; }
    public function get_total(): string { return '0'; }
    public function get_status($context): string { return 'completed'; }
    public function is_paid(): bool { return true; }
    public function get_items($type): array { return [new class {
        public function get_meta($key, ...$args): int { return 39; }
        public function get_id(): int { return 902; }
        public function get_quantity(): int { return 1; }
    }]; }
}
function wc_get_orders($args): mixed {
    return $args['type'] === 'shop_order_refund' ? [] : (object) [
        'orders' => ($GLOBALS['purchased'] ?? false) ? [new WC_Order()] : [], 'max_num_pages' => 1,
    ];
}
function wc_memberships_get_user_memberships($id, $args): array { return []; }
function wcs_get_subscription($id): mixed { return null; }
function wp_get_current_user(): object { return get_userdata(7); }
function __($text, $domain): string { return $text; }
function add_settings_error(...$args): void { $GLOBALS['settings_errors'][] = $args; }
function get_post_type($id): string { return 'imagine_numero'; }

spl_autoload_register(static function (string $class): void {
    $prefix = 'Imagine\\Pilotage\\';
    if (str_starts_with($class, $prefix)) {
        require dirname(__DIR__, 2) . '/imagine-pilotage/src/' . str_replace('\\', '/', substr($class, strlen($prefix))) . '.php';
    }
});
require dirname(__DIR__) . '/AchatNumero.php';
require dirname(__DIR__) . '/AchatsNumeros.php';
require dirname(__DIR__) . '/Paywall.php';
require dirname(__DIR__) . '/Decouverte.php';
require dirname(__DIR__) . '/DecouverteReglages.php';

use Imagine\Site\Decouverte;
use Imagine\Site\Paywall;

$scenario = json_decode($argv[1], true, 512, JSON_THROW_ON_ERROR);
$GLOBALS['wpdb'] = new C12Database();
$GLOBALS['wp_filter'] = [];
$GLOBALS['stored'] = [];
$GLOBALS['options'][Decouverte::OPTION] = ['ouverture' => 'premiere_lecture', 'forme' => 'articles', 'jours' => 7, 'nombre' => 2, 'numeros' => ['39', '25', '18']];
$GLOBALS['options']['imagine_acces_plans'] = [];
$GLOBALS['options']['imagine_decouverte_relecture'] = $scenario['relecture'] ?? 'fermee';
$GLOBALS['posts'] = [39 => new WP_Post(39, 'imagine_numero'), 25 => new WP_Post(25, 'imagine_numero'), 18 => new WP_Post(18, 'imagine_numero')];
foreach (['un' => [101, 39, true], 'non' => [102, 39, false], 'deux' => [103, 25, true], 'trois' => [104, 18, true]] as $label => [$id, $issue, $marked]) {
    $GLOBALS['posts'][$id] = new WP_Post($id);
    $GLOBALS['meta'][$id] = ['imagine_numero_id' => (string) $issue, 'imagine_reserve' => '1'];
    if ($marked) { $GLOBALS['meta'][$id]['imagine_decouverte'] = '1'; }
    $GLOBALS['meta'][$issue]['imagine_sortie'] = '2020-01-01';
    $ids[$label] = $id;
}
// Le vérificateur robot n'est pas remplacé : l'absence d'adresse distante reste non vérifiée.
$_SERVER['HTTP_USER_AGENT'] = 'Imagine-C12-local/1.0';
$_SERVER['REMOTE_ADDR'] = '127.0.0.1';
$article = new ReflectionProperty(Decouverte::class, 'article');
$out = [];
foreach ($scenario['steps'] as $step) {
    if (isset($step['form'])) { $GLOBALS['options'][Decouverte::OPTION]['forme'] = $step['form']; }
    if (isset($step['setting'])) { $GLOBALS['options']['imagine_decouverte_relecture'] = $step['setting']; }
    if (isset($step['scope'])) { $GLOBALS['options'][Decouverte::OPTION]['numeros'] = $step['scope']; }
    if (isset($step['verified'])) { $GLOBALS['verified'] = $step['verified']; }
    if (isset($step['deny_write'])) { $GLOBALS['deny_write'] = $step['deny_write']; }
    if (isset($step['purchased'])) { $GLOBALS['purchased'] = $step['purchased']; }
    if (isset($step['instant'])) {
        (new ReflectionProperty(Paywall::class, 'requestInstant'))->setValue(null, new DateTimeImmutable($step['instant']));
    }
    if ($step['issue'] ?? false) {
        Paywall::invalidate();
        $issue = $GLOBALS['posts'][39];
        $GLOBALS['meta'][39]['imagine_sortie'] = '2099-01-01';
        $out[] = ['pdf' => Paywall::decisionPdf($issue),
            'possede' => method_exists(Paywall::class, 'couvreNumero') ? Paywall::couvreNumero($issue) : false];
        continue;
    }
    $id = $ids[$step['article']];
    if (array_key_exists('marker', $step)) { $GLOBALS['meta'][$id]['imagine_decouverte'] = $step['marker']; }
    if ($step['future'] ?? false) { $GLOBALS['meta'][$GLOBALS['meta'][$id]['imagine_numero_id']]['imagine_sortie'] = '2099-01-01'; }
    $article->setValue(null, ($step['reading'] ?? true) ? $id : 0);
    Paywall::invalidate(); // Doublures hors hooks : invalidation explicite, pas une preuve de hooks WP.
    $decision = ($step['listing'] ?? false) ? (method_exists(Paywall::class, 'decisionListe') ? Paywall::decisionListe($GLOBALS['posts'][$id]) : ['complet' => false, 'motif' => 'missing_listing']) : Paywall::decision($GLOBALS['posts'][$id]);
    $out[] = ['decision' => $decision, 'state' => Decouverte::etat(7)];
}
echo json_encode($out, JSON_THROW_ON_ERROR);
