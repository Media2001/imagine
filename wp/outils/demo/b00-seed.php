<?php
/** Jeu B-00 fictif et provisoire : aucune source de production. */

declare(strict_types=1);

namespace Imagine\Demo\Seed;

if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'local') {
    throw new \RuntimeException('Exécution réservée au site fictif local par WP-CLI.');
}
if (get_option('blogname') !== 'imagine-test-demo' && get_option('imagine_demo_site') !== 'imagine-test-demo') {
    throw new \RuntimeException('La cible B-00 ne correspond pas.');
}
$data = json_decode((string) file_get_contents(__DIR__ . '/b00-fixture.json'), true, 512, JSON_THROW_ON_ERROR);
$secret = json_decode((string) file_get_contents('/var/www/.imagine-demo/seed-secret.json'), true, 512, JSON_THROW_ON_ERROR);
$manifest = [];

// Purge uniquement les identités et signatures d'installation, jamais un contenu
// simplement intitulé comme un exemple ou ajouté par un autre lot.
$purged = [];
foreach ([1 => ['post', 'hello-world', 'Hello world!'], 2 => ['page', 'sample-page', 'Sample Page']] as $id => [$type, $slug, $title]) {
    $post = get_post($id);
    if ($post && $post->post_type === $type && $post->post_name === $slug
        && $post->post_title === $title && !get_post_meta($id, 'imagine_demo_key', true)) {
        wp_delete_post($id, true);
        $purged[] = $id;
    }
}
$comment = get_comment(1);
if ($comment && $comment->comment_author === 'A WordPress Commenter'
    && $comment->comment_author_email === 'wapuu@wordpress.example'
    && $comment->comment_author_url === 'https://wordpress.org/') {
    wp_delete_comment(1, true);
}
// Migration ciblée du second verrou obsolète : aucun ID, corps ou droit changé.
$passwordsRemoved = [];
if (class_exists('Imagine\\Site\\Paywall')) {
    global $wpdb;
    $passwordsRemoved = $wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_type='post' AND post_password<>''");
    foreach ($passwordsRemoved as $id) {
        $wpdb->update($wpdb->posts, ['post_password' => ''], ['ID' => (int) $id], ['%s'], ['%d']);
        clean_post_cache((int) $id);
    }
}
update_option('WPLANG', 'fr_FR');

function upsert(string $key, array $post): int
{
    $existing = get_posts(['post_type' => $post['post_type'], 'post_status' => ['publish', 'private', 'draft', 'inherit', 'pending', 'future', 'trash'], 'numberposts' => 2,
        'meta_key' => 'imagine_demo_key', 'meta_value' => $key]);
    if (count($existing) > 1) {
        throw new \RuntimeException('Doublon fictif détecté : ' . $key);
    }
    $post['ID'] = $existing[0]->ID ?? 0;
    $post['post_date'] = '2026-01-01 12:00:00';
    $post['post_date_gmt'] = '2026-01-01 11:00:00';
    $post['comment_status'] = 'closed';
    $post['ping_status'] = 'closed';
    $post['meta_input']['imagine_demo_key'] = $key;
    $id = wp_insert_post(wp_slash($post), true);
    if (is_wp_error($id)) {
        throw new \RuntimeException('Échec de création du contenu fictif.');
    }
    return (int) $id;
}

function media(string $key, string $filename, string $mime, string $title): int
{
    if ($mime === 'application/pdf') {
        // C11 : jamais de copie PDF dans uploads ni dans les assets publics du seed.
        if (!class_exists('Imagine\\Site\\PdfNumero')) {
            throw new \RuntimeException('Adaptateur PDF privé obligatoire.');
        }
        $issueKey = substr($key, 0, -4);
        $issues = get_posts(['post_type' => 'imagine_numero', 'numberposts' => 2,
            'meta_key' => 'imagine_demo_key', 'meta_value' => $issueKey]);
        if (count($issues) !== 1) {
            throw new \RuntimeException('Numéro PDF ambigu.');
        }
        $issue = $issues[0]->ID;
        $id = upsert($key, ['post_type' => 'attachment', 'post_status' => 'private',
            'post_title' => $title, 'post_name' => $key, 'post_mime_type' => $mime,
            'guid' => \Imagine\Site\PdfNumero::url($issue)]);
        update_post_meta($issue, 'imagine_pdf_id', $id);
        \Imagine\Site\PdfNumero::protect($issue, $id, '/var/www/imagine-private-pdf/source/' . $filename);
        return $id;
    }
    $uploads = wp_upload_dir();
    $directory = $uploads['basedir'] . '/imagine-demo';
    wp_mkdir_p($directory);
    $target = $directory . '/' . $filename;
    $bytes = (string) file_get_contents(__DIR__ . '/assets/' . $filename);
    if (!is_file($target) || hash_file('sha256', $target) !== hash('sha256', $bytes)) {
        file_put_contents($target, $bytes);
    }
    $id = upsert($key, ['post_type' => 'attachment', 'post_status' => 'inherit', 'post_title' => $title,
        'post_name' => $key, 'post_mime_type' => $mime,
        'guid' => $uploads['baseurl'] . '/imagine-demo/' . $filename]);
    update_attached_file($id, $target);
    if ($mime === 'image/png') {
        update_post_meta($id, '_wp_attachment_image_alt', $title . ' — image de remplacement générée');
        require_once ABSPATH . 'wp-admin/includes/image.php';
        if (!wp_get_attachment_metadata($id)) {
            wp_update_attachment_metadata($id, wp_generate_attachment_metadata($id, $target));
        }
    }
    return $id;
}

update_option('imagine_demo_site', 'imagine-test-demo');
update_option('blogname', 'Imagine — démonstration entièrement fictive');
update_option('blogdescription', 'Aucun abonné, article ou paiement réel. Modèle provisoire B-00.');
update_option('blog_public', '0');
update_option('admin_email', 'admin-demo@example.org');
update_option('timezone_string', 'Europe/Brussels');
update_option('default_comment_status', 'closed');
update_option('default_ping_status', 'closed');
update_option('users_can_register', '0');
update_option('woocommerce_store_address', '1 rue Imaginaire');
update_option('woocommerce_store_city', 'Ville Fictive');
update_option('woocommerce_default_country', 'BE');
update_option('woocommerce_currency', 'EUR');
update_option('woocommerce_allow_tracking', 'no');
update_option('woocommerce_task_list_hidden', 'yes');
foreach (['bacs', 'cheque', 'cod', 'paypal', 'stripe'] as $gateway) {
    update_option('woocommerce_' . $gateway . '_settings', ['enabled' => 'no', 'testmode' => 'yes']);
}
update_option('imagine_demo_calendrier', $data['calendar']);
$admin = get_user_by('login', $secret['admin_user']);
if (!$admin) {
    throw new \RuntimeException('Administrateur normal de l’outil absent.');
}
wp_update_user(['ID' => $admin->ID, 'user_email' => 'admin-demo@example.org', 'display_name' => 'Administrateur Fictif Imagine']);
$editor = get_user_by('login', 'imagine-demo-redaction');
$user = ['user_login' => 'imagine-demo-redaction', 'user_email' => 'redaction-demo@example.org',
    'display_name' => 'Rédaction Fictive Imagine', 'role' => 'editor', 'user_pass' => $secret['editor_password']];
if ($editor) {
    $user['ID'] = $editor->ID;
}
$editorId = wp_insert_user($user);
if (is_wp_error($editorId)) {
    throw new \RuntimeException('Échec du compte de test fictif.');
}
$manifest['user:redaction'] = (int) $editorId;
$terms = [];
foreach ($data['themes'] as $i => $theme) {
    $slug = 'demo-thematique-' . ($i + 1);
    $term = get_term_by('slug', $slug, 'imagine_thematique');
    $termId = $term ? (int) $term->term_id : wp_insert_term($theme, 'imagine_thematique', ['slug' => $slug]);
    if (is_wp_error($termId)) {
        throw new \RuntimeException('Échec de la thématique fictive.');
    }
    $terms[] = is_array($termId) ? (int) $termId['term_id'] : $termId;
    $manifest['term:' . $slug] = end($terms);
}
$intro = 'Cette histoire est entièrement inventée pour la démonstration Imagine. Dans le village Imaginaire, des personnages fictifs discutent de projets qui n’existent pas. Aucun nom, événement ni reportage ne provient du magazine réel.';
$paragraph = 'À la maison des possibles, les habitants inventés construisent ensemble une carte de leur territoire imaginaire. Les discussions traversent la place des Nuages et le jardin des Horizons. Ce texte de remplissage en français permet de distinguer un court extrait du corps complet de l’article, de tester la lecture, les liens et les futures présentations. Il ne rapporte aucun fait réel et ne propose aucun service commercial.';
$home = '<p><strong>DÉMONSTRATION ENTIÈREMENT FICTIVE — aucune donnée réelle, aucun paiement ni email sortant.</strong></p><p>Modèle provisoire B-00. Ce n’est ni la maquette ni le site final Imagine.</p><h2>Nos cinq numéros fictifs</h2><ul>';
foreach ($data['issues'] as $issue) {
    $slug = $issue['slug'];
    $title = $issue['type'] === 'hors-serie' ? 'Hors-série fictif — été 2026' : 'Numéro fictif ' . $issue['label'] . ' — 2026';
    $id = upsert($slug, ['post_type' => 'imagine_numero', 'post_status' => 'publish', 'post_title' => $title,
        'post_name' => $slug, 'post_content' => $intro, 'post_excerpt' => $intro, 'meta_input' => [
            'imagine_code' => $issue['code'], 'imagine_type' => $issue['type'],
            'imagine_sortie' => $issue['sortie'], 'imagine_cloture' => $issue['cloture']]]);
    $manifest[$slug] = $id;
    $cover = media($slug . '-couverture', $slug . '.png', 'image/png', $title);
    $pdf = media($slug . '-pdf', $slug . '.pdf', 'application/pdf', 'PDF factice — ' . $title);
    $manifest[$slug . '-couverture'] = $cover;
    $manifest[$slug . '-pdf'] = $pdf;
    set_post_thumbnail($id, $cover);
    update_post_meta($id, 'imagine_pdf_id', $pdf);
    $contents = '<p>' . $intro . '</p><p>Sortie fictive : ' . esc_html($issue['sortie']) . ' ; clôture de la liste : ' . esc_html($issue['cloture']) . '.</p>'
        . wp_get_attachment_image($cover, 'medium') . '<h2>Sommaire fictif</h2><ul>';
    for ($i = 1; $i <= 4; $i++) {
        $reserved = $i < 4;
        $articleSlug = $slug . ($reserved ? '-reserve-' . $i : '-ouvert');
        $articleTitle = ($reserved ? 'Article fictif réservé ' . $i : 'Reportage fictif en accès libre') . ' — ' . $issue['code'];
        $excerpt = 'Extrait de démonstration : un récit inventé sur les solidarités du village Imaginaire. La suite, beaucoup plus longue, sert uniquement aux tests de lecture.';
        $body = '<p>' . $intro . '</p>';
        for ($p = 1; $p <= 5; $p++) {
            $body .= '<p>' . $paragraph . ' (Scène fictive ' . $p . '.)</p>';
        }
        $body .= '<p>' . ($reserved ? 'CONTENU_FICTIF_RESERVE_' : 'CONTENU_FICTIF_OUVERT_') . $issue['code'] . '_' . $i . '</p>';
        $article = upsert($articleSlug, ['post_type' => 'post', 'post_status' => 'publish',
            'post_name' => $articleSlug, 'post_title' => $articleTitle, 'post_content' => $body, 'post_excerpt' => $excerpt,
            'post_author' => (int) $editorId, 'post_password' => $reserved && !class_exists('Imagine\\Site\\Paywall') ? $secret['article_password'] : '',
            'meta_input' => ['imagine_numero_id' => $id, 'imagine_reserve' => $reserved ? '1' : '0']]);
        wp_set_object_terms($article, [$terms[($i - 1) % count($terms)]], 'imagine_thematique', false);
        $manifest[$articleSlug] = $article;
        $contents .= '<li><a href="' . esc_url(get_permalink($article)) . '">' . esc_html($articleTitle) . '</a></li>';
    }
    $contents .= '</ul><p><a href="' . esc_url(wp_get_attachment_url($pdf)) . '">Ouvrir le PDF factice de démonstration</a></p>';
    upsert($slug, ['post_type' => 'imagine_numero', 'post_status' => 'publish', 'post_name' => $slug,
        'post_title' => $title, 'post_content' => $contents, 'post_excerpt' => $intro]);
    $home .= '<li><a href="' . esc_url(get_permalink($id)) . '">' . esc_html($title) . '</a></li>';
}
$home .= '</ul><h2>Trois thématiques fictives</h2><ul>';
foreach ($terms as $termId) {
    $home .= '<li><a href="' . esc_url(get_term_link($termId, 'imagine_thematique')) . '">' . esc_html(get_term($termId)->name) . '</a></li>';
}
$home .= '</ul>';
foreach (['events' => 'imagine_evenement', 'partners' => 'imagine_partenaire'] as $group => $type) {
    $home .= '<h2>' . ($group === 'events' ? 'Événements inventés' : 'Partenaires inventés') . '</h2><ul>';
    foreach ($data[$group] as $index => $name) {
        $slug = 'demo-' . $group . '-' . ($index + 1);
        $id = upsert($slug, ['post_type' => $type, 'post_status' => 'publish', 'post_name' => $slug,
            'post_title' => $name, 'post_excerpt' => $intro, 'post_content' => '<p>' . $intro . '</p><p>' . $paragraph . '</p>',
            'meta_input' => ['imagine_date' => $group === 'events' ? '2026-12-' . (10 + $index) : '']]);
        $manifest[$slug] = $id;
        $home .= '<li><a href="' . esc_url(get_permalink($id)) . '">' . esc_html($name) . '</a></li>';
    }
    $home .= '</ul>';
}
$calendarId = upsert('demo-calendrier', ['post_type' => 'page', 'post_status' => 'publish', 'post_name' => 'calendrier-fictif',
    'post_title' => 'Calendrier de parution fictif — 2026 à 2028', 'post_content' => '<p>Quatre trimestriels et un hors-série d’été par an. Dates de fixture, non validées pour une exploitation réelle.</p>[imagine_demo_calendrier]']);
$manifest['demo-calendrier'] = $calendarId;
$home .= '<p><a href="' . esc_url(get_permalink($calendarId)) . '">Calendrier fictif sur trois ans</a> · <a href="' . esc_url(admin_url()) . '">Administration de la démonstration</a></p>';
$homeId = upsert('demo-accueil', ['post_type' => 'page', 'post_status' => 'publish', 'post_name' => 'accueil-fictif',
    'post_title' => 'Imagine — site de démonstration fictif', 'post_content' => $home]);
$manifest['demo-accueil'] = $homeId;
update_option('show_on_front', 'page');
update_option('page_on_front', $homeId);
ksort($manifest);
update_option('imagine_demo_manifest', $manifest);
flush_rewrite_rules();
echo wp_json_encode(['manifest' => $manifest, 'installation_posts_purged' => $purged, 'article_password_ids_retired' => array_map('intval', $passwordsRemoved), 'locale' => get_locale(), 'url' => home_url('/'), 'calendar_count' => count($data['calendar'])], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . "\n";
