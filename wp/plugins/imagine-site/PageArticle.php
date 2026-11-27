<?php

declare(strict_types=1);

namespace Imagine\Site;

use WP_Post;

/** Métadonnées publiques seulement : ne lit jamais post_content. */
final class PageArticle
{
    public const SIGNATURE = 'imagine_signature';

    public static function register(): void
    {
        add_action('add_meta_boxes_post', static function (): void {
            add_meta_box('imagine-b16', __('Signature publique', 'imagine-site'), [self::class, 'champ'], 'post', 'normal');
        });
        add_action('save_post_post', [self::class, 'sauver']);
    }

    public static function champ(WP_Post $post): void
    {
        wp_nonce_field('imagine_b16', 'imagine_b16_nonce');
        echo '<label for="imagine_signature">' . esc_html__('Nom signé, sans lien ni adresse', 'imagine-site') . '</label>';
        echo '<input id="imagine_signature" name="imagine_signature" type="text" value="'
            . esc_attr((string) get_post_meta($post->ID, self::SIGNATURE, true)) . '">';
    }

    public static function sauver(int $id): void
    {
        if (
            wp_is_post_revision($id) || wp_is_post_autosave($id) || !current_user_can('edit_post', $id)
            || !isset($_POST['imagine_b16_nonce']) || !is_string($_POST['imagine_b16_nonce'])
            || !wp_verify_nonce(wp_unslash($_POST['imagine_b16_nonce']), 'imagine_b16')
            || !isset($_POST[self::SIGNATURE]) || !is_string($_POST[self::SIGNATURE])
        ) {
            return;
        }
        $value = sanitize_text_field(wp_unslash($_POST[self::SIGNATURE]));
        update_post_meta($id, self::SIGNATURE, wp_slash($value));
    }

    public static function resume(WP_Post $post): string
    {
        // La requête C08 peut fournir un clone expurgé avec une phrase de repli.
        // Relire seulement la colonne publique, jamais le corps ni un extrait généré.
        return trim((string) get_post_field('post_excerpt', $post->ID, 'raw'));
    }

    public static function appel(array $decision): bool
    {
        return ($decision['complet'] ?? false) === true && in_array(
            $decision['motif'] ?? '',
            ['numero_achete', 'decouverte_duree', 'decouverte_articles'],
            true
        );
    }

    public static function entete(WP_Post $post): void
    {
        echo '<h1>' . esc_html(get_the_title($post)) . '</h1>';
        $resume = self::resume($post);
        if ($resume !== '') {
            echo '<p data-b16="resume">' . esc_html($resume) . '</p>';
        }
        $tags = get_the_terms($post, 'post_tag');
        if ($tags && !is_wp_error($tags)) {
            echo '<p data-b16="mots-cles">' . esc_html__('Mots-clés :', 'imagine-site') . ' '
                . esc_html(implode(', ', wp_list_pluck($tags, 'name'))) . '</p>';
        }
        $terms = get_the_term_list($post->ID, 'imagine_thematique', '', ', ');
        if ($terms && !is_wp_error($terms)) {
            echo '<p data-b16="thematique">' . esc_html__('Thématiques :', 'imagine-site') . ' ' . wp_kses_post($terms) . '</p>';
        }
        $signature = get_post_meta($post->ID, self::SIGNATURE, true);
        if (is_string($signature) && trim($signature) !== '') {
            echo '<p data-b16="signature">' . esc_html__('Par', 'imagine-site') . ' ' . esc_html($signature) . '</p>';
        }
        $issue = get_post((int) get_post_meta($post->ID, 'imagine_numero_id', true));
        if ($issue && $issue->post_type === 'imagine_numero' && $issue->post_status === 'publish') {
            echo '<p data-b16="numero">' . esc_html__('Numéro d’origine :', 'imagine-site') . ' <a href="'
                . esc_url(get_permalink($issue)) . '">' . esc_html(get_the_title($issue)) . '</a></p>';
        }
    }

    public static function fin(WP_Post $post): void
    {
        // Appel après le corps : C08 a déjà mémorisé cette décision de lecture.
        if (!self::appel(Paywall::decision($post))) {
            return;
        }
        $url = Navigation::abonnementUrl();
        if ($url !== '') {
            echo '<footer data-b16="abonnement" data-imagine-distraction><p><a href="' . esc_url($url) . '">'
                . esc_html__('Abonnez-vous pour poursuivre vos lectures.', 'imagine-site') . '</a></p></footer>';
        }
    }
}
