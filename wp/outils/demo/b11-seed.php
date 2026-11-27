<?php

declare(strict_types=1);

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || home_url() !== 'http://192.168.129.32:8085'
    || apply_filters('pre_wp_mail', null, []) !== false
    || !is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
    || WC()->payment_gateways()->get_available_payment_gateways() !== []) {
    throw new RuntimeException('B11 cible fictive refusée');
}
$fixture = get_option('imagine_b11_fixture', null);
$issue = get_page_by_path('demo-2026-t1', OBJECT, 'imagine_numero');
if (!$issue || $issue->ID !== 11 || !in_array('11', array_column(Imagine\Site\AchatsNumeros::droits((int) get_option('imagine_c09_fixture')['users']['P-NUMERO']), 'numero'), true)) {
    throw new RuntimeException('B11 numéro acheté fictif requis');
}
if ($fixture === null) {
    if (get_page_by_path('b11-article-medias-fictifs', OBJECT, 'post')) {
        throw new RuntimeException('B11 collision de page');
    }
    $id = wp_insert_post(wp_slash(['post_type' => 'post', 'post_status' => 'publish',
        'post_name' => 'b11-article-medias-fictifs', 'post_title' => 'B11 — Article médias entièrement fictif',
        'post_excerpt' => 'Extrait public fictif ; vidéo et podcast réservés avec le texte.',
        'post_content' => '<p>CONTENU_FICTIF_RESERVE_B11_VIDEO_PODCAST — scénario entièrement fictif.</p>',
        'meta_input' => ['imagine_numero_id' => $issue->ID, 'imagine_reserve' => '1', '_imagine_b11_fictif' => '1']]), true);
    if (is_wp_error($id)) {
        throw new RuntimeException('B11 article non créé');
    }
    update_option(Imagine\Site\Medias::OPTION, ['hosts' => ['video-fictive.example.invalid'], 'integration' => '0'], false);
    foreach ([$id, $issue->ID] as $postId) {
        if (!Imagine\Site\Medias::enregistrer($postId, 'https://video-fictive.example.invalid/B11_VIDEO_FICTIVE?a=1&b=2', 'https://podcast-fictif.example.invalid/B11_PODCAST_FICTIF')) {
            throw new RuntimeException('B11 médias non persistés');
        }
    }
    $source = Imagine\Site\PdfNumero::directory() . '/b11-source-silence.wav';
    if (file_exists($source) || is_link($source)) {
        throw new RuntimeException('B11 source déjà présente');
    }
    // PCM mono 16 bits, 8 kHz, trois secondes ; ni téléchargement ni média tiers.
    $data = str_repeat("\0", 48000);
    $bytes = 'RIFF' . pack('V', 36 + strlen($data)) . 'WAVEfmt ' . pack('VvvVVvv', 16, 1, 1, 8000, 16000, 2, 16) . 'data' . pack('V', strlen($data)) . $data;
    try {
        if (file_put_contents($source, $bytes, LOCK_EX) !== strlen($bytes) || !chmod($source, 0600)) {
            throw new RuntimeException('B11 silence non créé');
        }
        Imagine\Site\AudioNumero::proteger($issue->ID, $source);
    } finally {
        if (is_file($source)) {
            unlink($source);
        }
    }
    $fixture = ['fictif' => true, 'issue' => $issue->ID, 'article' => $id, 'silence_sha256' => hash('sha256', $bytes), 'seconds' => 3];
    update_option('imagine_b11_fixture', $fixture, false);
}
if (!isset($fixture['issue_active'])) {
    $current = get_post(39);
    wp_set_current_user((int) get_option('imagine_c09_fixture')['users']['A-CARTE']);
    if (!$current || !Imagine\Site\Paywall::decisionPdf($current)['complet']) {
        throw new RuntimeException('B11 numéro courant couvert requis');
    }
    $source = Imagine\Site\AudioNumero::path($issue->ID);
    Imagine\Site\AudioNumero::proteger($current->ID, $source);
    $fixture['issue_active'] = $current->ID;
    update_option('imagine_b11_fixture', $fixture, false);
}
$article = get_post($fixture['article']);
if (!$article || get_post_meta($article->ID, '_imagine_b11_fictif', true) !== '1'
    || get_option('imagine_b11_fixture') !== $fixture
    || hash_file('sha256', Imagine\Site\AudioNumero::path($issue->ID)) !== $fixture['silence_sha256']) {
    throw new RuntimeException('B11 fixture non relue');
}
echo wp_json_encode($fixture + ['issue_url' => get_permalink($issue), 'article_url' => get_permalink($article)]);
