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
