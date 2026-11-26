<?php

declare(strict_types=1);

namespace Imagine\Site;

/** B06 : attribut administratif ; aucun raccord à Memberships ni au droit des articles. */
final class Cooperateurs
{
    public const META = 'imagine_cooperateur';
    public const PAGE = 'imagine_cooperateurs_page';
    public const ACCROCHE = 'imagine_cooperateur_modifie';

    public static function register(): void
    {
        add_action('show_user_profile', [self::class, 'fiche']);
        add_action('edit_user_profile', [self::class, 'fiche']);
        foreach (['personal_options_update', 'edit_user_profile_update'] as $hook) {
            add_action($hook, static function (int $id): void {
                if (!isset($_POST['imagine_cooperateur_present'])) {
                    return;
                }
                try {
                    self::enregistrer($id);
                } catch (\Throwable) {
                    wp_die(esc_html__('Statut coopérateur non modifié : rechargez la fiche.', 'imagine-site'), '', ['response' => 403]);
                }
            });
        }
        add_action('woocommerce_account_dashboard', [self::class, 'compte'], 25);
        add_filter('the_posts', [self::class, 'protegerObjets'], -1000);
        add_filter('the_content', [self::class, 'contenu'], -1000);
        add_filter('get_the_excerpt', [self::class, 'extrait'], -1000, 2);
        add_action('pre_get_posts', [self::class, 'requete'], -1000);
        add_filter('rest_pre_dispatch', [self::class, 'rest'], -1000, 3);
        add_filter('map_meta_cap', [self::class, 'capacites'], 20, 4);
        add_filter('wp_sitemaps_posts_query_args', [self::class, 'sitemap'], 10, 2);
        add_action('template_redirect', static function (): void {
            if (in_array(get_queried_object_id(), self::ids(), true)) {
                if (!defined('DONOTCACHEPAGE')) {
                    define('DONOTCACHEPAGE', true);
                }
                nocache_headers();
            }
        }, -1000);
        add_filter('wp_privacy_personal_data_exporters', static function (array $items): array {
            $items['imagine-cooperateurs'] = ['exporter_friendly_name' => __('Statut coopérateur', 'imagine-site'),
                'callback' => [self::class, 'exporter']];
            return $items;
        });
        add_filter('wp_privacy_personal_data_erasers', static function (array $items): array {
            $items['imagine-cooperateurs'] = ['eraser_friendly_name' => __('Statut coopérateur', 'imagine-site'),
                'callback' => [self::class, 'effacer']];
            return $items;
        });
        add_action('delete_user', static function (int $id): void {
            $user = get_userdata($id);
            if ($user) {
                do {
                    $r = self::effacer($user->user_email);
                    if ($r['items_retained']) {
                        throw new \RuntimeException('Effacement coopérateur incomplet.');
                    }
                } while (!$r['done']);
            }
        }, 4);
    }

    public static function administration(): bool
    {
        return CooperateursRegles::administration(wp_get_current_user()->roles);
    }

    public static function autorise(): bool
    {
        return CooperateursRegles::lecture(
            get_user_meta(get_current_user_id(), self::META, true),
            wp_get_current_user()->roles,
            is_user_logged_in()
        );
    }

    public static function fiche(\WP_User $user): void
    {
        if (!self::administration() || !current_user_can('edit_user', $user->ID)) {
            return;
        }
        $state = get_user_meta($user->ID, self::META, true);
        echo '<h2>' . esc_html__('Espace coopérateurs', 'imagine-site') . '</h2><table class="form-table"><tr><th>'
            . esc_html__('Coopérateur', 'imagine-site') . '</th><td>';
        wp_nonce_field('imagine_cooperateur_' . $user->ID, 'imagine_cooperateur_nonce');
        echo '<input type="hidden" name="imagine_cooperateur_present" value="1"><label><input type="checkbox" name="imagine_cooperateur_oui" value="1"'
            . checked(is_array($state) && ($state['cooperateur'] ?? false) === true, true, false) . '> '
            . esc_html__('Ouvrir l’espace coopérateurs, jamais les articles', 'imagine-site') . '</label>';
        if (is_array($state) && ($state['cooperateur'] ?? null) === true) {
            echo '<p>' . esc_html__('Source : administration', 'imagine-site') . ' — <time>' . esc_html($state['date_utc'] ?? '') . '</time></p>';
        }
        echo '</td></tr></table>';
    }

    public static function enregistrer(int $id): void
    {
        $nonce = $_POST['imagine_cooperateur_nonce'] ?? null;
        if (
            ($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST' || !self::administration()
            || !get_userdata($id) || !current_user_can('edit_user', $id)
            || !is_string($nonce) || !wp_verify_nonce($nonce, 'imagine_cooperateur_' . $id)
            || ($_POST['imagine_cooperateur_present'] ?? '') !== '1'
            || (isset($_POST['imagine_cooperateur_oui']) && $_POST['imagine_cooperateur_oui'] !== '1')
        ) {
            throw new \RuntimeException('Modification refusée.');
        }
        global $wpdb;
        $lock = 'imagine_cooperateur_' . $id;
        if ((int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s,3)', $lock)) !== 1) {
            throw new \RuntimeException('Statut occupé.');
        }
        try {
            wp_cache_delete($id, 'user_meta');
            $old = get_user_meta($id, self::META, true);
            $existed = metadata_exists('user', $id, self::META);
            $oui = isset($_POST['imagine_cooperateur_oui']);
            if (
                (!$existed && !$oui) || (is_array($old) && ($old['cooperateur'] ?? null) === $oui
                && ($old['source'] ?? '') === 'administration')
            ) {
                return;
            }
            $new = ['cooperateur' => $oui, 'source' => 'administration', 'date_utc' => gmdate('Y-m-d\TH:i:s\Z')];
            if (!update_user_meta($id, self::META, $new) || get_user_meta($id, self::META, true) !== $new) {
                throw new \RuntimeException('Statut non enregistré.');
            }
            $u = wp_get_current_user();
            $row = ['quand_utc' => $new['date_utc'], 'qui_id' => $u->ID, 'qui_login' => $u->user_login,
                'option' => self::META . '_' . $id, 'avant' => $existed ? $old : null, 'apres' => $new];
            $key = \Imagine\Pilotage\Administration\Reglages::JOURNAL . str_replace('-', '', wp_generate_uuid4());
            if (!add_option($key, $row, '', false) || get_option($key) !== $row) {
                $existed ? update_user_meta($id, self::META, $old) : delete_user_meta($id, self::META);
                wp_cache_delete($id, 'user_meta');
                if (get_user_meta($id, self::META, true) !== $old) {
                    throw new \RuntimeException('Restauration du statut impossible.');
                }
                throw new \RuntimeException('Journal indisponible.');
            }
            // Point nommé pour un futur raccord ; aucun écouteur/transport enregistré ici.
            do_action(self::ACCROCHE, $id, $new, $old);
        } finally {
            $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
        }
    }

    /** Journal C10/C17 commun, événements B06 ciblés uniquement. */
    public static function audits(int $id): array
    {
        global $wpdb;
        $prefix = \Imagine\Pilotage\Administration\Reglages::JOURNAL;
        $rows = $wpdb->get_results($wpdb->prepare("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_id", $wpdb->esc_like($prefix) . '%'));
        if ($wpdb->last_error !== '' || !is_array($rows)) {
            throw new \RuntimeException('Journal coopérateur indisponible.');
        }
        $out = [];
        foreach ($rows as $row) {
            $value = maybe_unserialize($row->option_value);
            if (is_array($value) && ($value['option'] ?? '') === self::META . '_' . $id) {
                $out[$row->option_name] = $value;
            }
        }
        return $out;
    }

    /** Racine, marqueurs persistants et descendants : aucune règle d'article. */
    public static function ids(): array
    {
        global $wpdb;
        $root = (int) get_option(self::PAGE);
        $ids = $root ? [$root] : [];
        $marked = $wpdb->get_col($wpdb->prepare("SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key=%s AND meta_value='1'", 'imagine_espace_cooperateurs'));
        $ids = array_merge($ids, array_map('intval', $marked));
        $pages = $wpdb->get_results("SELECT ID,post_parent,post_name FROM {$wpdb->posts} WHERE post_type='page'");
        do {
            $before = count($ids);
            foreach ($pages as $page) {
                if ($page->post_name === 'espace-cooperateurs' || in_array((int) $page->post_parent, $ids, true)) {
                    $ids[] = (int) $page->ID;
                }
            }
            $ids = array_values(array_unique($ids));
        } while (count($ids) !== $before);
        return $ids;
    }

    private static function reserve(int $id): bool
    {
        return in_array($id, self::ids(), true);
    }

    private static function refus(): string
    {
        return '<p data-imagine-cooperateurs-refus>' . esc_html__('Cet espace est réservé aux coopérateurs.', 'imagine-site') . '</p>';
    }

    public static function protegerObjets(array $posts): array
    {
        if (self::autorise()) {
            return $posts;
        }
        foreach ($posts as &$post) {
            if ($post instanceof \WP_Post && self::reserve($post->ID)) {
                $post = clone $post; // Ne jamais empoisonner le cache partagé des objets.
                $post->post_content = self::refus();
                $post->post_excerpt = '';
                $post->post_content_filtered = '';
            }
        }
        return $posts;
    }

    public static function contenu(string $html): string
    {
        $id = (int) get_the_ID();
        if (!self::reserve($id)) {
            return $html;
        }
        if (!self::autorise()) {
            return self::refus();
        }
        if ($id === (int) get_option(self::PAGE)) {
            $html .= '<nav aria-label="' . esc_attr__('Espace coopérateurs', 'imagine-site') . '"><ul>';
            foreach (get_pages(['parent' => $id, 'sort_column' => 'menu_order,post_title']) as $page) {
                $html .= '<li><a href="' . esc_url(get_permalink($page->ID)) . '">' . esc_html($page->post_title) . '</a></li>';
            }
            $html .= '</ul></nav>';
        }
        return $html;
    }

    public static function extrait(string $html, mixed $post = null): string
    {
        $p = get_post($post);
        return $p && self::reserve($p->ID) && !self::autorise() ? '' : $html;
    }

    private static function exclure(array $args): array
    {
        $ids = self::ids();
        $args['post__not_in'] = array_values(array_unique(array_merge((array) ($args['post__not_in'] ?? []), $ids)));
        if (!empty($args['post__in'])) {
            $args['post__in'] = array_values(array_diff($args['post__in'], $ids)) ?: [0];
        }
        return $args;
    }

    public static function requete(\WP_Query $q): void
    {
        if (!self::autorise() && !$q->is_singular()) {
            foreach (self::exclure($q->query_vars) as $name => $value) {
                if (in_array($name, ['post__in', 'post__not_in'], true)) {
                    $q->set($name, $value);
                }
            }
        }
    }

    public static function capacites(array $caps, string $cap, int $userId, array $args): array
    {
        if (in_array($cap, ['read_post', 'edit_post', 'delete_post'], true) && isset($args[0])) {
            $id = (int) $args[0];
            $id = (int) (wp_is_post_revision($id) ?: $id);
            $u = get_userdata($userId);
            if (
                self::reserve($id) && !CooperateursRegles::lecture(
                    get_user_meta($userId, self::META, true),
                    $u ? $u->roles : [],
                    $userId > 0
                )
            ) {
                return ['do_not_allow'];
            }
        }
        return $caps;
    }

    public static function sitemap(array $args, string $type): array
    {
        return $type === 'page' ? self::exclure($args) : $args;
    }

    public static function rest(mixed $result, \WP_REST_Server $server, \WP_REST_Request $request): mixed
    {
        if (self::autorise()) {
            return $result;
        }
        $route = $request->get_route();
        $id = 0;
        if (preg_match('~^/wp/v2/pages/([0-9]+)(?:/|$)~', $route, $match)) {
            $id = (int) $match[1];
        } elseif ($route === '/oembed/1.0/embed' && is_string($request->get_param('url'))) {
            $id = (int) url_to_postid($request->get_param('url'));
        }
        if ($id && self::reserve($id)) {
            return new \WP_Error('imagine_cooperateurs_reserve', __('Cet espace est réservé aux coopérateurs.', 'imagine-site'), ['status' => 403]);
        }
        return $result;
    }

    public static function exporter(string $email, int $page = 1): array|\WP_Error
    {
        $user = get_user_by('email', $email);
        $rows = [];
        if ($user) {
            if (metadata_exists('user', $user->ID, self::META)) {
                $rows['statut'] = [self::META => get_user_meta($user->ID, self::META, true)];
            }
            try {
                $audits = self::audits($user->ID);
            } catch (\RuntimeException) {
                return new \WP_Error('imagine_cooperateurs_export_incomplet', __('Export du statut coopérateur incomplet : réessayez.', 'imagine-site'));
            }
            foreach ($audits as $key => $event) {
                // Ne jamais exporter le nom/login ni d'autres dossiers de l'opérateur.
                $rows[$key] = array_intersect_key($event, array_flip(['quand_utc', 'avant', 'apres']));
            }
        }
        $items = [];
        foreach (array_slice($rows, (max(1, $page) - 1) * 50, 50, true) as $key => $fields) {
            $data = [];
            foreach ($fields as $name => $value) {
                $data[] = ['name' => $name, 'value' => wp_json_encode($value, JSON_UNESCAPED_UNICODE)];
            }
            $items[] = ['group_id' => 'imagine-cooperateurs', 'group_label' => __('Statut coopérateur', 'imagine-site'),
                'item_id' => 'imagine-cooperateur-' . hash('sha256', $key), 'data' => $data];
        }
        return ['data' => $items, 'done' => max(1, $page) * 50 >= count($rows)];
    }

    public static function effacer(string $email, int $page = 1): array
    {
        $result = ['items_removed' => false, 'items_retained' => false, 'messages' => [], 'done' => true];
        $u = get_user_by('email', $email);
        if (!$u) {
            return $result;
        }
        global $wpdb;
        $lock = 'imagine_cooperateur_' . $u->ID;
        $locked = (int) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s,3)', $lock)) === 1;
        try {
            if (!$locked) {
                throw new \RuntimeException('Statut occupé.');
            }
            if (metadata_exists('user', $u->ID, self::META)) {
                delete_user_meta($u->ID, self::META);
                wp_cache_delete($u->ID, 'user_meta');
                if (metadata_exists('user', $u->ID, self::META)) {
                    throw new \RuntimeException('Attribut non effacé.');
                }
                $result['items_removed'] = true;
            }
            foreach (array_slice(self::audits($u->ID), 0, 50, true) as $key => $old) {
                $new = $old;
                $new['option'] = 'imagine_cooperateur_efface';
                $new['avant'] = $new['apres'] = null;
                $sql = $wpdb->prepare(
                    "UPDATE {$wpdb->options} SET option_value=%s WHERE option_name=%s AND BINARY option_value=BINARY %s",
                    maybe_serialize($new),
                    $key,
                    maybe_serialize($old)
                );
                if ($wpdb->query($sql) !== 1) {
                    throw new \RuntimeException('Audit modifié.');
                }
                wp_cache_delete($key, 'options');
                if (get_option($key) !== $new) {
                    throw new \RuntimeException('Audit non relu.');
                }
                $result['items_removed'] = true;
            }
            $result['done'] = self::audits($u->ID) === [];
        } catch (\Throwable) {
            $result['items_retained'] = true;
            $result['done'] = false;
            $result['messages'][] = __('Effacement du statut coopérateur incomplet : réessayez.', 'imagine-site');
        } finally {
            if ($locked) {
                $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
            }
        }
        return $result;
    }

    public static function compte(): void
    {
        if (!is_user_logged_in()) {
            return;
        }
        $s = get_user_meta(get_current_user_id(), self::META, true);
        $oui = CooperateursRegles::lecture($s, [], true);
        echo '<section id="mon-statut-cooperateur"><h2>' . esc_html__('Mon statut de coopérateur', 'imagine-site') . '</h2><p>'
            . esc_html($oui ? __('Coopérateur : oui', 'imagine-site') : __('Coopérateur : non', 'imagine-site'));
        if (is_array($s) && ($s['cooperateur'] ?? null) === true) {
            echo ' — ' . esc_html__('Source : administration', 'imagine-site') . ' — <time>' . esc_html($s['date_utc'] ?? '') . '</time>';
        }
        echo '</p>';
        if (self::autorise() && ($id = (int) get_option(self::PAGE))) {
            echo '<p><a href="' . esc_url(get_permalink($id)) . '">' . esc_html__('Espace coopérateurs', 'imagine-site') . '</a></p>';
        }
        echo '</section>';
    }
}
