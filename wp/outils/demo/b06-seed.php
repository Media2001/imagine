<?php

declare(strict_types=1);

use Imagine\Site\Cooperateurs as C;
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo') { throw new RuntimeException('Démo seule.'); }
$pages = [
    'espace-cooperateurs' => 'Espace coopérateurs',
    'appels-a-benevolat' => 'Appels à bénévolat',
    'lettre-de-missions' => 'Lettre de missions',
    'cadastre-des-competences' => 'Cadastre des compétences',
    'relais-des-evenements' => 'Relais des événements',
];
$root = 0;
$ids = [];
foreach ($pages as $slug => $title) {
    $path = $root ? 'espace-cooperateurs/' . $slug : $slug;
    $old = get_page_by_path($path);
    if ($old && (get_post_meta($old->ID, 'imagine_espace_cooperateurs', true) !== '1'
        || $old->post_content !== '' || $old->post_title !== $title || $old->post_parent !== $root)) {
        throw new RuntimeException('Page étrangère B06 : refus.');
    }
    if ($old) {
        $id = $old->ID;
    } else {
        $id = wp_insert_post(['post_type'=>'page', 'post_status'=>'publish', 'post_title'=>$title,
            'post_name'=>$slug,'post_content'=>'','post_excerpt'=>'','post_parent'=>$root], true);
        if (is_wp_error($id)) { throw new RuntimeException('Page non créée.'); }
        update_post_meta($id, 'imagine_espace_cooperateurs', '1');
    }
    $read = get_post($id);
    if ($read->post_content !== '' || $read->post_status !== 'publish'
        || get_post_meta($id, 'imagine_espace_cooperateurs', true) !== '1') {
        throw new RuntimeException('Relecture B06 divergente.');
    }
    $ids[] = ['id'=>$id,'path'=>wp_parse_url(get_permalink($id),PHP_URL_PATH),'title'=>$title];
    if (!$root) { $root = $id; update_option(C::PAGE, $root, false); }
}
if ((int)get_option(C::PAGE) !== $root || count($ids) !== 5) { throw new RuntimeException('Espace incomplet.'); }
echo wp_json_encode(['pages'=>$ids,'root'=>$root]);
