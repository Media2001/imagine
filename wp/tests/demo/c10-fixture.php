<?php
/** Témoin de lecture C10 seulement ; jamais de compte ni de modification d'un contenu B00/C08/C09. */
declare(strict_types=1);
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new RuntimeException('Cible fictive C10 requise.');
}
$fixture = get_option('imagine_c10_fixture');
if (!$fixture) {
    $find = static function (string $kind, array $data): int {
        $posts = get_posts(['post_type' => $data['post_type'], 'post_status' => 'any',
            'posts_per_page' => 2, 'meta_key' => '_imagine_c10_fixture', 'meta_value' => $kind]);
        if (count($posts) > 1) {
            throw new RuntimeException('Témoin C10 dupliqué : arrêt sans modifier.');
        }
        if ($posts) {
            return $posts[0]->ID;
        }
        $id = wp_insert_post($data + ['meta_input' => ['_imagine_c10_fixture' => $kind]], true);
        if (is_wp_error($id)) {
            throw new RuntimeException($id->get_error_message());
        }
        return $id;
    };
    // Brouillon : ne remplace jamais la carte kiosque B00. Date ancienne de l'article : hors nouveautés.
    $issue = $find('numero-futur', ['post_type' => 'imagine_numero', 'post_status' => 'draft',
        'post_title' => 'Témoin C10 — numéro fictif à venir',
        'meta_input' => ['_imagine_c10_fixture' => 'numero-futur', 'imagine_sortie' => '2099-01-01']]);
    $article = $find('article-futur', ['post_type' => 'post', 'post_status' => 'publish',
        'post_title' => 'Témoin C10 — lecture de l’équipe avant parution',
        'post_name' => 'temoin-c10-acces-equipe', 'post_date' => '2000-01-01 12:00:00',
        'post_date_gmt' => '2000-01-01 11:00:00', 'post_password' => '',
        'post_excerpt' => 'Article entièrement fictif pour vérifier le réglage des contenus pas encore parus.',
        'post_content' => '<p>Contenu fictif C10.</p><p>Les lanternes turquoise de C10 éclairent le jardin imaginaire.</p>',
        'meta_input' => ['_imagine_c10_fixture' => 'article-futur',
            'imagine_reserve' => true, 'imagine_numero_id' => $issue]]);
    add_option('imagine_c10_fixture', ['article' => $article, 'issue' => $issue], '', false);
    $fixture = get_option('imagine_c10_fixture');
}
if (!is_array($fixture)
    || get_post_meta($fixture['article'], '_imagine_c10_fixture', true) !== 'article-futur'
    || get_post_meta($fixture['issue'], '_imagine_c10_fixture', true) !== 'numero-futur'
    || get_post_meta($fixture['issue'], 'imagine_sortie', true) !== '2099-01-01'
    || get_post_meta($fixture['article'], 'imagine_numero_id', true) != $fixture['issue']
    || get_post_type($fixture['article']) !== 'post'
    || get_post_status($fixture['article']) !== 'publish'
    || get_post_status($fixture['issue']) !== 'draft') {
    throw new RuntimeException('Témoin C10 divergent : arrêt sans réparation implicite.');
}
echo wp_json_encode($fixture);
