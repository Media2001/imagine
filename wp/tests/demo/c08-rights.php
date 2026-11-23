<?php
/** Doublures locales au namespace de l'adaptateur, aucun objet natif n'est muté. */
declare(strict_types=1);
namespace Imagine\Site {
    function wc_memberships_get_user_memberships($id, $args) { return [$GLOBALS['c08_member']]; }
    function get_userdata($id) { return (object) ['roles' => $GLOBALS['c08_roles']]; }
    function get_option($name, $default = false) {
        return $name === 'imagine_acces_plans' ? [987654 => 'abonnement'] : \get_option($name, $default);
    }
    function get_post_meta($id, $key = '', $single = false) {
        return $key === '_subscription_id' ? ($GLOBALS['c08_link'] ? 987655 : 0) : \get_post_meta($id, $key, $single);
    }
    function wc_memberships() {
        return new class {
            public function get_integrations_instance() { return $this; }
            public function get_subscriptions_instance() { return $this; }
            public function get_subscription_from_membership($id) { return $GLOBALS['c08_sub']; }
        };
    }
}
namespace Imagine\Demo\C08Rights {
    if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
        || get_option('imagine_demo_site') !== 'imagine-test-demo') {
        throw new \RuntimeException('Cible fictive C08 requise.');
    }
    $f = get_option('imagine_c08_fixture');
    $owner = $f['users']['actif'];
    $post = get_post($f['article']);
    wp_set_current_user($owner);
    $GLOBALS['c08_member'] = new class ($owner) {
        public string $status = 'active';
        public function __construct(public int $owner) {}
        public function get_plan_id() { return 987654; }
        public function get_user_id() { return $this->owner; }
        public function get_id() { return 987656; }
        public function get_start_date() { return '2026-01-01 00:00:00'; }
        public function get_end_date(...$args) { return '2030-01-01 00:00:00'; }
        public function get_status() { return $this->status; }
    };
    $GLOBALS['c08_sub'] = new class ($owner) {
        public string $status = 'active';
        public function __construct(public int $owner) {}
        public function get_customer_id() { return $this->owner; }
        public function get_date($key, $zone) { return $key === 'start' ? '2026-01-01 00:00:00' : '2030-01-01 00:00:00'; }
        public function get_status() { return $this->status; }
        public function get_meta($key) { return ''; }
    };
    $method = new \ReflectionMethod(\Imagine\Site\Paywall::class, 'rights');
    $now = new \DateTimeImmutable(gmdate('Y-m-d H:i:s'), new \DateTimeZone('UTC'));
    $checks = [];
    foreach ([
        'actif' => ['active', 'active', true, [], 'actif', true],
        'suspendu' => ['paused', 'active', false, [], 'suspendu', false],
        'expire' => ['expired', 'active', false, [], 'expire', false],
        'virement_non_valide' => ['pending', 'active', false, [], 'virement_non_valide', false],
        'onhold_sans_fenetre' => ['active', 'on-hold', true, [], 'suspendu', false],
        'paused_sans_abonnement' => ['paused', 'active', false, [], 'suspendu', false],
        'equipe_administration' => ['expired', 'cancelled', true, ['administrator'], 'expire', true],
        'equipe_redaction' => ['pending', 'active', false, ['editor'], 'virement_non_valide', true],
    ] as $name => [$member, $sub, $link, $roles, $expected, $full]) {
        $GLOBALS['c08_member']->status = $member;
        $GLOBALS['c08_sub']->status = $sub;
        $GLOBALS['c08_link'] = $link;
        $GLOBALS['c08_roles'] = $roles;
        $rights = $method->invoke(null, $owner, $now);
        $checks[$name . ':mappage_exact'] = $rights[array_key_last($rights)]['etat'] === $expected;
        // Les doublures ne déclenchent aucun hook natif : invalidation explicite du banc isolé.
        \Imagine\Site\Paywall::invalidate();
        $decision = \Imagine\Site\Paywall::decision($post);
        $checks[$name . ':decision_moteur'] = $decision['complet'] === $full;
        if ($roles) { $checks[$name . ':motif_equipe'] = $decision['motif'] === 'equipe'; }
    }
    $GLOBALS['c08_roles'] = [];
    $GLOBALS['c08_member']->owner = $owner + 10000;
    \Imagine\Site\Paywall::invalidate();
    $checks['proprietaire_incoherent_ferme'] = !\Imagine\Site\Paywall::decision($post)['complet'];
    $failures = array_keys(array_filter($checks, static fn ($ok) => !$ok));
    echo wp_json_encode(['checks' => $checks, 'total' => count($checks), 'failures' => $failures]);
    if ($failures) { \WP_CLI::halt(1); }
}
