<?php

declare(strict_types=1);

use Imagine\Site\Cooperateurs as C;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new RuntimeException('Démo seule.');
}
$checks = [];
$checks['deux_reglages_exposes'] = method_exists(C::class, 'reglages') && method_exists(C::class, 'champsReglages');
if ($checks['deux_reglages_exposes']) {
    global $wpdb;
    $original = get_current_user_id();
    $wpdb->query('START TRANSACTION');
    try {
        $admin = get_user_by('login', 'admin');
        wp_set_current_user($admin->ID);
        C::reglages();
        $keys = ['imagine_cooperateurs_roles_attribut', 'imagine_cooperateurs_roles_lecture'];
        $registered = get_registered_settings();
        foreach ($keys as $key) {
            delete_option($key);
            $checks[$key.'_settings_api'] = isset($registered[$key]) && $registered[$key]['group'] === 'imagine_reglages' && $registered[$key]['show_in_rest'] === false;
            $checks[$key.'_defaut_admin'] = C::roles($key) === ['administrator'];
        }
        $id = wp_insert_user(['user_login'=>'b06-reglages-fictif','user_email'=>'b06-reglages@example.org','user_pass'=>wp_generate_password(40),'role'=>'editor']);
        if (is_wp_error($id)) { throw new RuntimeException('Fixture absente.'); }
        $editor = get_userdata($id);
        $editor->add_cap('manage_options');
        $editor->add_cap('edit_users');
        $roles = ['administrator', 'editor', 'shop_manager'];
        $fixture = get_option('imagine_c08_fixture');
        $articleWitness = 'Les lucioles violettes de C08 gardent le secret du village fictif.';
        $articleAccess = [];
        foreach ($roles as $role) {
            wp_set_current_user(0); $editor->set_role($role); wp_set_current_user($id);
            $GLOBALS['post'] = get_post($fixture['article']);
            $articleAccess[$role] = str_contains(apply_filters('the_content', $GLOBALS['post']->post_content), $articleWitness);
        }
        $space = wp_insert_post(['post_type'=>'page','post_status'=>'publish','post_title'=>'B06 réglages espace fictif']);
        update_option(C::PAGE, $space, false);
        foreach (range(0, 7) as $write) {
            $writers = array_values(array_filter($roles, static fn ($r, $i) => (bool) ($write & (1 << $i)), ARRAY_FILTER_USE_BOTH));
            foreach (range(0, 7) as $read) {
                $readers = array_values(array_filter($roles, static fn ($r, $i) => (bool) ($read & (1 << $i)), ARRAY_FILTER_USE_BOTH));
                wp_set_current_user($admin->ID);
                update_option($keys[0], $writers, false);
                update_option($keys[1], $readers, false);
                $checks["config_{$write}_{$read}_persistee"] = C::roles($keys[0]) === $writers && C::roles($keys[1]) === $readers;
                foreach ($roles as $role) {
                    wp_set_current_user(0);
                    $editor->set_role($role);
                    wp_set_current_user($id);
                    $checks["config_{$write}_{$read}_{$role}"] = C::administration() === in_array($role, $writers, true) && C::autorise() === in_array($role, $readers, true);
                    $checks["config_{$write}_{$read}_{$role}_capacite_native"] = current_user_can('read_post', $space) === in_array($role, $readers, true);
                    $GLOBALS['post'] = get_post($fixture['article']);
                    $checks["config_{$write}_{$read}_{$role}_article_inchange"] = str_contains(apply_filters('the_content', $GLOBALS['post']->post_content), $articleWitness) === $articleAccess[$role];
                }
                // Le véritable adaptateur d'article ne reçoit aucun de ces réglages.
                $fixture = get_option('imagine_c08_fixture');
                wp_set_current_user((int) get_user_by('login', 'p-coop')->ID);
                $GLOBALS['post'] = get_post($fixture['article']);
                $body = apply_filters('the_content', $GLOBALS['post']->post_content);
                $checks["config_{$write}_{$read}_article_ferme"] = str_contains($body, 'Extrait public C08') && !str_contains($body, 'Les lucioles violettes de C08 gardent le secret du village fictif.');
            }
        }
        wp_set_current_user($admin->ID);
        foreach ($keys as $key) {
            update_option($key, ['administrator'], false);
            foreach (['administrator', ['inconnu'], ['manage_options'], ['editor','editor'], [true], ['subscriber'], ['editor'=>'editor']] as $bad) {
                update_option($key, $bad, false);
                $checks[$key.'_invalid_'.count($checks)] = C::roles($key) === ['administrator'];
            }
            wp_set_current_user(0); $editor->set_role('editor'); $editor->add_cap('manage_options'); wp_set_current_user($id);
            update_option($key, ['editor'], false);
            $checks[$key.'_capacite_ne_permet_pas_configuration'] = C::roles($key) === ['administrator'];
            wp_set_current_user($admin->ID);
        }
        $html = C::champsReglages();
        $checks['champs_separes_non_vides'] = str_contains($html, 'imagine-cooperateurs-reglages') && str_contains($html, $keys[0]) && str_contains($html, $keys[1]);
    } finally {
        $wpdb->query('ROLLBACK'); wp_cache_flush(); wp_set_current_user($original);
    }
}
$failures = array_keys(array_filter($checks, static fn ($v) => $v !== true));
echo wp_json_encode(['checks'=>$checks,'total'=>count($checks),'failures'=>$failures]);
if ($failures) { WP_CLI::halt(1); }
