<?php
/** Temporary concurrency rendezvous, loaded only on guarded fictitious demo. */
declare(strict_types=1);
add_action('woocommerce_pre_payment_complete', static function ($id): void {
    if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo'
        || home_url() !== 'http://192.168.129.32:8085'
        || ($_POST['action'] ?? '') !== 'imagine_virement_recu') {
        return;
    }
    $f = get_option('imagine_c09_fixture');
    $o = wc_get_order($id);
    if ((int) $id === (int) $f['orders']['A-VIR'] && $o->get_meta('_imagine_c09_fixture') === 'A-VIR'
        && $o->get_payment_method() === '' && $o->get_meta('imagine_demo_fictif') === '1') {
        usleep(1500000);
    }
}, 0);

add_action('woocommerce_payment_complete', static function ($id): void {
    $f = get_option('imagine_c09_fixture');
    if (wp_get_environment_type() === 'local' && get_option('imagine_demo_site') === 'imagine-test-demo'
        && home_url() === 'http://192.168.129.32:8085'
        && ($_POST['action'] ?? '') === 'imagine_virement_recu'
        && ($_POST['imagine_c15_refus'] ?? '') === 'apres'
        && (int) $id === (int) ($f['orders']['A-VIR'] ?? 0)) {
        // WC_Order catches this after the paid transition and returns false.
        throw new RuntimeException('C15 — refus natif injecté après transition fictive.');
    }
}, PHP_INT_MAX);

function imagine_c15_witness_lock_header(): void
{
    global $wpdb;
    $f = get_option('imagine_c09_fixture');
    $id = (int) ($f['orders']['A-VIR'] ?? 0);
    $name = 'imagine_c15_' . substr(hash('sha256', DB_NAME . ':' . $wpdb->prefix . ':' . $id), 0, 48);
    $used = $wpdb->get_var($wpdb->prepare('SELECT IS_USED_LOCK(%s)', $name));
    // Same live connection, before exit: tests finally, not auto-release on disconnect.
    header('X-Imagine-C15-Lock: ' . ($used === null || (string) $used !== (string) $wpdb->get_var('SELECT CONNECTION_ID()') ? 'free' : 'held'));
}
add_filter('wp_die_handler', static function ($handler) {
    return static function ($message, $title = '', $args = []) use ($handler): void {
        imagine_c15_witness_lock_header();
        $handler($message, $title, $args);
    };
});
add_filter('wp_redirect', static function ($location) {
    imagine_c15_witness_lock_header();
    return $location;
});
