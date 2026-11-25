<?php
/** C15 owned C09 state witnesses and narrowly scoped native restoration. */
declare(strict_types=1);
namespace Imagine\Demo\C15Corrections;

function guard(): array
{
    if (wp_get_environment_type() !== 'local' || get_option('imagine_demo_site') !== 'imagine-test-demo'
        || home_url() !== 'http://192.168.129.32:8085'
        || apply_filters('pre_wp_mail', null, []) !== false
        || !is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
        || WC()->payment_gateways()->get_available_payment_gateways() !== []) {
        throw new \RuntimeException('C15 fixture guard');
    }
    return get_option('imagine_c09_fixture');
}

function snapshot(): array
{
    $f = guard();
    $out = [];
    foreach (['A-PAPIER', 'A-VIR'] as $key) {
        $s = wcs_get_subscription($f['subscriptions'][$key]);
        $o = wc_get_order($f['orders'][$key]);
        if ($s->get_meta('_imagine_c09_fixture') !== $key || $o->get_meta('_imagine_c09_fixture') !== $key
            || !$s->get_requires_manual_renewal() || $s->get_payment_method() !== '' || $o->get_payment_method() !== '') {
            throw new \RuntimeException('Wrong fixture owner/manual flag');
        }
        $dates = [];
        foreach (array_keys($s->get_data()) as $name) {
            if (str_starts_with($name, 'schedule_')) {
                $type = substr($name, 9);
                $dates[$type] = $s->get_date($type, 'gmt');
            }
        }
        $meta = [];
        foreach ($s->get_meta_data() as $m) {
            $data = $m->get_data();
            $meta[$data['key']] = $data['value'];
        }
        $m = wc_memberships_get_user_membership($f['memberships'][$key]);
        $out[$key] = ['sub' => ['status' => $s->get_status(), 'dates' => $dates,
            'suspension_count' => $s->get_suspension_count(), 'meta' => $meta,
            'paid' => $s->get_date_paid()?->getTimestamp(), 'completed' => $s->get_date_completed()?->getTimestamp()],
            'order' => ['status' => $o->get_status(), 'paid' => $o->get_date_paid()?->getTimestamp(),
                'completed' => $o->get_date_completed()?->getTimestamp()],
            'membership' => ['status' => $m->get_status(), 'start' => $m->get_start_date(), 'end' => $m->get_end_date('mysql', false)],
            'roles' => array_values(get_userdata($f['users'][$key])->roles)];
    }
    return $out;
}

function restore(array $before, array $renewals = []): bool
{
    $f = guard();
    foreach ($renewals as $id) {
        $o = wc_get_order($id);
        if (!$o) {
            continue;
        }
        if ($o->get_meta('imagine_c15_witness') !== 'A-PAPIER' || (int) $o->get_customer_id() !== (int) $f['users']['A-PAPIER']) {
            throw new \RuntimeException('Refuse foreign renewal deletion');
        }
        $o->delete(true);
    }
    foreach ($before as $key => $row) {
        if (!in_array($key, ['A-PAPIER', 'A-VIR'], true)) {
            throw new \RuntimeException('Wrong restore scope');
        }
        $o = wc_get_order($f['orders'][$key]);
        $o->set_status($row['order']['status']);
        $o->set_date_paid($row['order']['paid']);
        $o->set_date_completed($row['order']['completed']);
        $o->save();
        $s = wcs_get_subscription($f['subscriptions'][$key]);
        if ($s->get_status() !== $row['sub']['status']) {
            $s->update_status($row['sub']['status']);
        }
        // Reacquire after native transition hooks; restore every observed schedule.
        $s = wcs_get_subscription($s->get_id());
        $s->update_dates($row['sub']['dates'], 'gmt');
        $s->set_suspension_count($row['sub']['suspension_count']);
        $s->set_date_paid($row['sub']['paid']);
        $s->set_date_completed($row['sub']['completed']);
        foreach ($s->get_meta_data() as $m) {
            $data = $m->get_data();
            if (!array_key_exists($data['key'], $row['sub']['meta'])) {
                $s->delete_meta_data($data['key']);
            }
        }
        foreach ($row['sub']['meta'] as $name => $value) {
            $s->update_meta_data($name, $value);
        }
        $s->save();
        $m = wc_memberships_get_user_membership($f['memberships'][$key]);
        $m->update_status($row['membership']['status']);
        $m->set_start_date($row['membership']['start']);
        $m->set_end_date($row['membership']['end'] ?: '');
        $u = get_userdata($f['users'][$key]);
        $u->set_role('');
        foreach ($row['roles'] as $role) {
            $u->add_role($role);
        }
    }
    return true;
}

function unpaid(): int
{
    $f = guard();
    $s = wcs_get_subscription($f['subscriptions']['A-PAPIER']);
    $o = wcs_create_renewal_order($s);
    if (is_wp_error($o)) {
        throw new \RuntimeException('Native renewal unavailable');
    }
    $o->update_meta_data('imagine_c15_witness', 'A-PAPIER');
    $o->update_meta_data('imagine_demo_fictif', '1');
    $o->set_payment_method('');
    $o->set_transaction_id('');
    $o->save();
    // Real WCS unpaid-renewal transition (no gateway/payment_complete).
    $s = wcs_get_subscription($s->get_id());
    $s->payment_failed();
    return $o->get_id();
}
