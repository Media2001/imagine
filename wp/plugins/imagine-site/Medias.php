<?php

declare(strict_types=1);

namespace Imagine\Site;

use WP_Post;

/** Champs distincts du contenu : jamais soumis au moteur oEmbed. */
final class Medias
{
    public const OPTION = 'imagine_medias';
    public const VIDEO = '_imagine_video';
    public const PODCAST = '_imagine_podcast';

    public static function configuration(): array
    {
        $value = get_option(self::OPTION, []);
        return self::valider($value) ?? ['hosts' => [], 'integration' => '0'];
    }

    private static function valider(mixed $value): ?array
    {
        if (!is_array($value) || !isset($value['hosts']) || !is_array($value['hosts']) || count($value['hosts']) > 20) {
            return null;
        }
        foreach ($value['hosts'] as $host) {
            if (!is_string($host) || strlen($host) > 253
                || !preg_match('/\A[a-z0-9]+(?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,}\z/D', $host)
                || str_contains($host, '..')) {
                return null;
            }
        }
        return ['hosts' => array_values(array_unique($value['hosts'])),
            'integration' => ($value['integration'] ?? '') === '1' ? '1' : '0'];
    }

    public static function nettoyer(mixed $value): array
    {
        if (is_array($value) && is_string($value['hosts'] ?? null)) {
            $value['hosts'] = preg_split('/\s+/', trim($value['hosts']), -1, PREG_SPLIT_NO_EMPTY);
        }
        $valid = self::valider($value);
        if ($valid === null) {
            add_settings_error(self::OPTION, 'imagine_medias_refus', __('Hôtes invalides : réglage précédent conservé.', 'imagine-site'));
        }
        return $valid ?? self::configuration();
    }

    public static function enregistrer(int $id, mixed $video, mixed $podcast): bool
    {
        $post = get_post($id);
        if (!$post || !in_array($post->post_type, ['post', 'imagine_numero'], true)
            || !is_string($video) || !is_string($podcast)
            || ($video !== '' && MediasRegles::video($video, self::configuration()['hosts']) === null)
            || ($podcast !== '' && MediasRegles::lien($podcast) === null)) {
            return false;
        }
        foreach ([self::VIDEO => $video, self::PODCAST => $podcast] as $key => $value) {
            update_post_meta($id, $key, wp_slash($value));
        }
        return get_post_meta($id, self::VIDEO, true) === $video && get_post_meta($id, self::PODCAST, true) === $podcast;
    }

    public static function rendre(WP_Post $post): string
    {
        if ($post->post_status !== 'publish' || !in_array($post->post_type, ['post', 'imagine_numero'], true)
            || ($post->post_type === 'post' && !Paywall::decision($post)['complet'])) {
            return '';
        }
        $config = self::configuration();
        $video = MediasRegles::video(get_post_meta($post->ID, self::VIDEO, true), $config['hosts']);
        $podcast = MediasRegles::lien(get_post_meta($post->ID, self::PODCAST, true));
        $html = '';
        if ($video !== null) {
            $html .= '<p><a data-imagine-video href="' . esc_url($video) . '" rel="external noopener noreferrer">'
                . esc_html__('Voir la vidéo', 'imagine-site') . '</a></p>';
            if ($config['integration'] === '1') {
                $html .= '<div data-imagine-video-emplacement aria-label="'
                    . esc_attr__('Emplacement du lecteur après consentement — aucun service chargé.', 'imagine-site') . '"></div>';
            }
        }
        if ($podcast !== null) {
            $html .= '<p><a data-imagine-podcast href="' . esc_url($podcast) . '" rel="external noopener noreferrer">'
                . esc_html__('Écouter le podcast sur son service', 'imagine-site') . '</a></p>';
        }
        return $html;
    }

    public static function champs(WP_Post $post): void
    {
        wp_nonce_field('imagine_medias_' . $post->ID, '_imagine_medias_nonce');
        foreach (['video' => [self::VIDEO, __('Adresse de la vidéo', 'imagine-site')],
            'podcast' => [self::PODCAST, __('Lien vers le podcast', 'imagine-site')]] as $name => [$key, $label]) {
            echo '<p><label for="b11-' . esc_attr($name) . '">' . esc_html($label)
                . '</label><br><input class="widefat" id="b11-' . esc_attr($name) . '" name="b11_' . esc_attr($name)
                . '" type="url" value="' . esc_attr((string) get_post_meta($post->ID, $key, true)) . '"></p>';
        }
        echo '<p>' . esc_html__('Liens uniquement. HTTPS ; vidéo limitée aux hôtes des réglages. Aucun lecteur tiers chargé.', 'imagine-site') . '</p>';
    }

    public static function reglages(): string
    {
        $config = self::configuration();
        return '<section id="imagine-medias-reglages"><h2>' . esc_html__('Vidéos et podcasts', 'imagine-site') . '</h2><p><label>'
            . esc_html__('Hôtes vidéo autorisés (un par ligne ; liste vide : fermé)', 'imagine-site')
            . '<br><textarea name="imagine_medias[hosts]" rows="3" cols="60">'
            . esc_textarea(implode("\n", $config['hosts'])) . '</textarea></label></p><p><label>'
            . esc_html__('Intégrer le lecteur après consentement', 'imagine-site') . ' <select name="imagine_medias[integration]">'
            . '<option value="0"' . selected($config['integration'], '0', false) . '>' . esc_html__('Non', 'imagine-site') . '</option>'
            . '<option value="1"' . selected($config['integration'], '1', false) . '>' . esc_html__('Emplacement seulement (consentement non choisi)', 'imagine-site')
            . '</option></select></label></p></section>';
    }

    public static function register(): void
    {
        add_action('add_meta_boxes', static function (): void {
            foreach (['post', 'imagine_numero'] as $type) {
                add_meta_box('imagine-medias', __('Vidéo et podcast', 'imagine-site'), [self::class, 'champs'], $type);
            }
        });
        add_action('save_post', static function (int $id): void {
            if (wp_is_post_revision($id) || wp_is_post_autosave($id) || !current_user_can('edit_post', $id)
                || !is_string($_POST['_imagine_medias_nonce'] ?? null)
                || !wp_verify_nonce(wp_unslash($_POST['_imagine_medias_nonce']), 'imagine_medias_' . $id)) {
                return;
            }
            if (!self::enregistrer($id, wp_unslash($_POST['b11_video'] ?? null), wp_unslash($_POST['b11_podcast'] ?? null))) {
                add_filter('redirect_post_location', static fn (string $url): string => add_query_arg('imagine_medias_refus', '1', $url));
            }
        });
        add_action('admin_notices', static function (): void {
            if (isset($_GET['imagine_medias_refus'])) {
                echo '<div class="notice notice-error"><p>' . esc_html__('Médias refusés : adresse ou hôte invalide, anciens liens conservés.', 'imagine-site') . '</p></div>';
            }
        });
        add_action('admin_init', static function (): void {
            register_setting('imagine_reglages', self::OPTION, ['type' => 'array', 'show_in_rest' => false,
                'sanitize_callback' => [self::class, 'nettoyer']]);
        }, 60);
        // Même insertion additive que C22/C24/C25/C27 ; C10 demeure inchangé.
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
                        if ($end !== false && str_contains($html, 'imagine_reglages')) {
                            $html = substr_replace($html, self::reglages(), $end, 0);
                        }
                        echo $html;
                    }, $priority);
                }
            }
        }, 160);
    }
}
