<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Manual editorial designation; one native option, no rotation or new content model. */
final class Partenaires
{
    public const OPTION = 'imagine_partenaire_du_mois';

    public static function selection(): ?\WP_Post
    {
        $value = get_option(self::OPTION, 0);
        if (!(is_int($value) || is_string($value)) || !preg_match('/^[1-9][0-9]*$/D', (string) $value)) {
            return null;
        }
        $post = get_post((int) $value);
        return $post && $post->post_type === 'imagine_partenaire' && $post->post_status === 'publish'
            ? $post : null;
    }

    public static function nettoyer(mixed $value): int
    {
        $old = self::selection()?->ID ?? 0;
        if ($value === null) {
            return $old; // A predecessor's C10 form must not erase a designation.
        }
        if ($value === 0 || $value === '0') {
            return 0;
        }
        if ((is_int($value) || is_string($value)) && preg_match('/^[1-9][0-9]*$/D', (string) $value)) {
            $post = get_post((int) $value);
            if ($post && $post->post_type === 'imagine_partenaire' && $post->post_status === 'publish') {
                return $post->ID;
            }
        }
        add_settings_error(self::OPTION, 'imagine_partenaire_invalide', __('Partenaire invalide : sélection conservée.', 'imagine-site'));
        return $old;
    }

    public static function register(): void
    {
        add_action('pre_get_posts', [self::class, 'exclureRechercheFlux']);
        add_filter('register_post_type_args', static function (array $args, string $type): array {
            if ($type === 'imagine_partenaire') {
                $args['exclude_from_search'] = true;
            }
            return $args;
        }, 10, 2);
        add_action('admin_init', static function (): void {
            register_setting('imagine_reglages', self::OPTION, [
                'type' => 'integer', 'sanitize_callback' => [self::class, 'nettoyer'], 'show_in_rest' => false,
            ]);
        }, 40);
        // C10 has no internal rendering hook: extend only its native form by menu hook,
        // like the existing C12/C17 adapters; retain capability, nonce and options.php.
        add_action('admin_menu', static function (): void {
            global $wp_filter;
            $hook = get_plugin_page_hookname('imagine-reglages', 'imagine');
            foreach (($wp_filter[$hook]->callbacks ?? []) as $priority => $callbacks) {
                foreach ($callbacks as $callback) {
                    $fn = $callback['function'];
                    remove_action($hook, $fn, $priority);
                    add_action($hook, static function () use ($fn): void {
                        ob_start();
                        $fn();
                        $html = ob_get_clean();
                        $end = strpos($html, '</form>');
                        if ($end !== false && preg_match('/value=[\'\"]imagine_reglages[\'\"]/', $html)) {
                            ob_start();
                            self::champ();
                            $html = substr_replace($html, ob_get_clean(), $end, 0);
                        } else {
                            // Never silently lose the manual designation if C10 markup drifts.
                            $html = '<div class="notice notice-error imagine-partenaire-injection-erreur"><p>'
                                . esc_html__('Le champ Partenaire du mois est indisponible : le formulaire de réglages a changé. Contactez l’administration du site.', 'imagine-site')
                                . '</p></div>' . $html;
                        }
                        echo $html;
                    }, $priority);
                }
            }
        }, 130);
    }

    /** Also close explicitly forced partner types, without changing editorial queries. */
    public static function exclureRechercheFlux(\WP_Query $query): void
    {
        if (is_admin() || (!$query->is_search() && !$query->is_feed())) {
            return;
        }
        $types = $query->get('post_type');
        if (!$types || $types === 'any' || (is_array($types) && in_array('any', $types, true))) {
            $types = $query->is_feed() && !$types ? ['post']
                : array_values(get_post_types(['exclude_from_search' => false]));
        }
        $types = array_values(array_diff((array) $types, ['imagine_partenaire']));
        $query->set('post_type', $types ?: ['post']);
        if (!$types) {
            $query->set('post__in', [0]);
        }
    }

    public static function champ(): void
    {
        echo '<h2>' . esc_html__('Partenaires', 'imagine-site') . '</h2><p><label for="imagine-partenaire-du-mois">'
            . esc_html__('Partenaire du mois', 'imagine-site') . '</label></p><select id="imagine-partenaire-du-mois" name="'
            . esc_attr(self::OPTION) . '"><option value="0">' . esc_html__('Aucun — bloc masqué', 'imagine-site') . '</option>';
        $selected = self::selection()?->ID ?? 0;
        foreach (
            get_posts(['post_type' => 'imagine_partenaire', 'post_status' => 'publish',
            'numberposts' => -1, 'orderby' => ['title' => 'ASC', 'ID' => 'ASC']]) as $post
        ) {
            echo '<option value="' . esc_attr((string) $post->ID) . '"' . selected($selected, $post->ID, false) . '>'
                . esc_html($post->post_title) . '</option>';
        }
        echo '</select><p>' . esc_html__('Un seul choix manuel, sans rotation. Sans partenaire publié désigné, aucun bloc sur l’accueil.', 'imagine-site') . '</p>';
    }
}
