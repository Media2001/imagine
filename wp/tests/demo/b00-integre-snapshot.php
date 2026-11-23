<?php
/** Empreintes de conservation inter-lots, jamais les secrets ou hachages de connexion. */
declare(strict_types=1);
namespace Imagine\Tests\Demo\IntegreSnapshot;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('Cible fictive B00 requise.');
}
global $wpdb;
$hash = static fn ($value): string => hash('sha256', wp_json_encode($value));
$out = ['scope' => 'imagine-test-demo'];
foreach (['imagine_c08_fixture', 'imagine_c09_fixture', 'imagine_acces_plans'] as $key) {
    $out['options'][$key] = get_option($key);
}
$settings = $wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name IN ('imagine_acces_reglages','imagine_c05_reglages','imagine_envoi_colonnes_export') OR option_name LIKE 'imagine\\_reglages\\_journal\\_%' ORDER BY option_name", ARRAY_A);
$out['c10_settings_and_journal_sha256'] = $hash($settings);
$out['c10_active'] = is_plugin_active('imagine-pilotage/imagine-reglages.php');
foreach (['imagine-pilotage', 'imagine-connecteur'] as $dir) {
    foreach (new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator(WP_PLUGIN_DIR . '/' . $dir, \FilesystemIterator::SKIP_DOTS)) as $file) {
        if ($file->isFile() && $file->getExtension() === 'php') {
            $out['protected_code'][$dir . substr($file->getPathname(), strlen(WP_PLUGIN_DIR . '/' . $dir))] = hash_file('sha256', $file->getPathname());
        }
    }
}
ksort($out['protected_code']);
foreach (['c08', 'c09'] as $lot) {
    $f = get_option('imagine_' . $lot . '_fixture', []);
    $out[$lot]['counts'] = [];
    foreach (['users', 'orders', 'subscriptions', 'memberships'] as $group) {
        $rows = [];
        foreach ($f[$group] ?? [] as $key => $id) {
            if ($group === 'users') {
                $user = get_userdata($id);
                $meta = get_user_meta($id);
                // Les connexions HTTP créent des jetons de session, pas de nouveaux droits.
                unset($meta['session_tokens'], $meta['last_update'], $meta['_woocommerce_persistent_cart_' . get_current_blog_id()]);
                ksort($meta);
                $rows[$key] = ['user' => $user->data, 'roles' => $user->roles, 'meta' => $meta];
            } elseif ($group === 'memberships') {
                $rows[$key] = [get_post($id), get_post_meta($id)];
            } else {
                $object = $group === 'subscriptions' ? wcs_get_subscription($id) : wc_get_order($id);
                $rows[$key] = $object->get_data();
                $rows[$key]['items'] = [];
                foreach ($object->get_items(['line_item', 'shipping', 'fee']) as $itemId => $item) {
                    $rows[$key]['items'][$itemId] = $item->get_data();
                }
            }
        }
        $out[$lot]['counts'][$group] = count($rows);
        $out[$lot][$group . '_sha256'] = $hash($rows);
    }
    // Les mots de passe d'article migrent séparément ; les contenus et IDs restent exacts.
    $articles = [];
    foreach (['article', 'automatique'] as $key) {
        if (isset($f[$key])) {
            $post = get_post($f[$key]);
            $articles[$key] = [$post->ID, $post->post_name, $post->post_content, $post->post_excerpt, get_post_meta($post->ID)];
        }
    }
    $out[$lot]['articles_sha256'] = $hash($articles);
}
$out['decisions'] = [];
$post = get_post(get_option('imagine_c08_fixture')['article']);
foreach (get_option('imagine_c09_fixture')['users'] as $key => $id) {
    wp_set_current_user($id);
    $out['decisions'][$key] = \Imagine\Site\Paywall::decision($post);
}
wp_set_current_user(0);
echo wp_json_encode($out, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
