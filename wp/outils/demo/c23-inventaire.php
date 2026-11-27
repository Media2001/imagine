<?php
/** C23 : inventaire natif en lecture seule, jamais installé sur le site. */
declare(strict_types=1);
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local'
    || get_option('imagine_demo_site') !== 'imagine-test-demo'
    || home_url() !== 'http://192.168.129.32:8085'
    || apply_filters('pre_wp_mail', null, []) !== false
    || !is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.org'))
    || WC()->payment_gateways()->get_available_payment_gateways() !== []) {
    throw new RuntimeException('C23 cible ou coupe-circuits refusés.');
}
$manifest = get_option('imagine_demo_manifest');
$c08 = get_option('imagine_c08_fixture');
$c12 = get_option('imagine_c12_fixture');
$c09 = get_option('imagine_c09_fixture');
$article = (int) $manifest['demo-2026-t4-reserve-1'];
$issue = (int) $manifest['demo-2026-t4'];
$terms = wp_get_post_terms($article, 'imagine_thematique');
if (!$terms || is_wp_error($terms)) { throw new RuntimeException('C23 thématique absente.'); }
$local = static function (string $url): string {
    if (!str_starts_with($url, home_url() . '/')) { throw new RuntimeException('C23 URL non locale.'); }
    return substr($url, strlen(home_url()));
};
$out = ['scope' => 'imagine-test-demo', 'base' => home_url(), 'article' => $article,
    'article_path' => $local(get_permalink($article)), 'article_title' => get_post($article)->post_title,
    'issue' => $issue, 'issue_path' => $local(get_permalink($issue)), 'issue_slug' => get_post($issue)->post_name,
    'pdf' => (int) $manifest['demo-2026-t4-pdf'], 'attachment_path' => '/?attachment_id=' . $manifest['demo-2026-t4-pdf'],
    'auto' => $c08['automatique'], 'auto_path' => $local(get_permalink($c08['automatique'])),
    'c08' => $c08['article'], 'c12' => $c12['trois'], 'posts_archive' => '/' . substr(get_post($article)->post_date, 0, 4) . '/',
    'term_path' => $local(get_term_link($terms[0])), 'posts' => [], 'issues' => [], 'partners' => [],
    'users' => [], 'guards' => ['mail' => true, 'network' => true, 'payments' => true],
    'discovery' => get_option('imagine_decouverte_compte_' . $c09['users']['V-DEC-FIN']),
    'discovery_policy' => Imagine\Site\Decouverte::reglages(), 'discovery_relecture' => get_option('imagine_decouverte_relecture', 'fermee'),
    'account_path' => $local(wc_get_page_permalink('myaccount')),
    'sitemap_enabled' => wp_sitemaps_get_server()->sitemaps_enabled(),
    'admin_pages' => ['imagine-reglages', Imagine\Site\ListeEnvoiAdmin::PAGE, Imagine\Site\EcheancesAdmin::PAGE,
        Imagine\Site\CommandeAdmin::PAGE, Imagine\Site\Justificatifs::PAGE, Imagine\Site\ExtractionsAdmin::PAGE,
        Imagine\Site\TableauBordAdmin::PAGE], 'profile_catalogue' => [], 'additional_publics' => []];
foreach (get_posts(['post_type' => 'post', 'post_status' => 'publish', 'numberposts' => -1]) as $post) {
    $out['posts'][] = ['id' => $post->ID, 'slug' => $post->post_name, 'title' => $post->post_title,
        'path' => $local(get_permalink($post->ID)), 'issue' => (int) get_post_meta($post->ID, 'imagine_numero_id', true),
        'reserved' => get_post_meta($post->ID, 'imagine_reserve', true) === '1',
        'body' => $post->post_content, 'excerpt' => $post->post_excerpt];
}
foreach (get_posts(['post_type' => 'imagine_numero', 'post_status' => 'publish', 'numberposts' => -1]) as $post) {
    $out['issues'][] = ['id' => $post->ID, 'slug' => $post->post_name, 'title' => $post->post_title,
        'pdf' => (int) get_post_meta($post->ID, 'imagine_pdf_id', true),
        'pdf_marker' => 'Numero ' . get_post_meta($post->ID, 'imagine_numero', true) . ' - PDF factice',
        'private_present' => (bool) get_post_meta($post->ID, '_imagine_pdf_blob', true)];
}
foreach (get_posts(['post_type' => 'imagine_partenaire', 'post_status' => 'publish', 'numberposts' => -1]) as $post) {
    $out['partners'][] = ['id' => $post->ID, 'path' => $local(get_permalink($post->ID)), 'title' => $post->post_title];
}
foreach (['V-INSCRIT', 'V-DEC-FIN', 'P-NUMERO', 'A-CARTE'] as $key) {
    $id = (int) $c09['users'][$key];
    if (get_user_meta($id, '_imagine_c09_fixture', true) !== $key || get_userdata($id)->user_login !== strtolower($key)) {
        throw new RuntimeException('C23 profil fictif absent.');
    }
    $out['users'][$key] = $id;
}
$out['buyer_issues'] = array_values(array_map(static fn ($right) => $right['numero'], Imagine\Site\AchatsNumeros::droits($out['users']['P-NUMERO'])));
foreach($c09['users'] as $code=>$id){
    wp_set_current_user((int)$id); Imagine\Site\Paywall::invalidate();
    $articleDecision=Imagine\Site\Paywall::decision(get_post($article));
    $pdfDecision=Imagine\Site\Paywall::decisionPdf(get_post($issue));
    $out['profile_catalogue'][]=['code'=>$code,'id'=>(int)$id,'article_T4'=>$articleDecision,'pdf_T4'=>$pdfDecision,
        'selected'=>in_array($code,['V-INSCRIT','V-DEC-FIN','P-NUMERO','A-CARTE'],true)];
    if(!$articleDecision['complet'] && !$pdfDecision['complet'] && !in_array($code,['V-DEC','V-INSCRIT','V-DEC-FIN','P-NUMERO'],true)){
        $out['additional_publics']['profil-'.strtolower($code)]=$code;
        $out['users'][$code]=(int)$id;
        $out['profile_catalogue'][array_key_last($out['profile_catalogue'])]['selected']=true;
    }
}
$out['cooperator_pages'] = [];
foreach (Imagine\Site\Cooperateurs::ids() as $id) {
    $p = get_post($id);
    if (!$p || $p->post_type !== 'page' || $p->post_status !== 'publish') {
        throw new RuntimeException('C23 B06 page publiée absente.');
    }
    $out['cooperator_pages'][] = ['id' => $p->ID, 'path' => $local(get_permalink($id)),
        'title' => $p->post_title, 'body' => $p->post_content];
}
if (count($out['cooperator_pages']) !== 5) { throw new RuntimeException('C23 B06 inventaire incomplet.'); }
$mapping = ['connecte-sans-abonnement' => 'V-INSCRIT', 'decouverte-epuisee' => 'V-DEC-FIN',
    'acheteur-autre-numero' => 'P-NUMERO', 'abonne-actif' => 'A-CARTE'] + $out['additional_publics'];
$out['cooperator_publics'] = [];
$out['cooperator_roles'] = get_option('imagine_cooperateurs_roles_lecture', ['administrator']);
$out['cooperator_actors'] = [];
foreach ($mapping as $public => $code) {
    wp_set_current_user($out['users'][$code]);
    $out['cooperator_actors'][$public] = ['code' => $code, 'roles' => array_values(wp_get_current_user()->roles),
        'status' => (get_user_meta($out['users'][$code], 'imagine_cooperateur', true)['cooperateur'] ?? false) === true];
    if (Imagine\Site\Cooperateurs::autorise()) { $out['cooperator_publics'][] = $public; }
}
if (!in_array('profil-p-coop', $out['cooperator_publics'], true)) { throw new RuntimeException('C23 B06 coopérateur témoin absent.'); }
echo wp_json_encode($out);
