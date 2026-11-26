<?php
/** Offline B05: real WordPress HTML processor; only storage/UI boundary doubles. */
declare(strict_types=1);
define('ABSPATH', '/usr/src/wordpress/');
define('WPINC', 'wp-includes');
require ABSPATH . WPINC . '/plugin.php';
require ABSPATH . WPINC . '/class-wp-post.php';
require ABSPATH . WPINC . '/http.php';
require ABSPATH . WPINC . '/compat.php';
require ABSPATH . WPINC . '/utf8.php';
require ABSPATH . WPINC . '/kses.php';
foreach (['class-wp-html-attribute-token.php', 'class-wp-html-span.php', 'class-wp-html-text-replacement.php', 'class-wp-html-decoder.php', 'class-wp-html-tag-processor.php'] as $file) {
    if (is_file(ABSPATH . WPINC . '/html-api/' . $file)) { require_once ABSPATH . WPINC . '/html-api/' . $file; }
}
function get_post_type(): string { return $GLOBALS['type'] ?? 'imagine_partenaire'; }
function home_url(string $path = ''): string { return 'http://demo.example.org' . $path; }
function get_option(string $name, mixed $default = false): mixed { return $GLOBALS['options'][$name] ?? $default; }
function get_post(int $id): ?WP_Post { return isset($GLOBALS['posts'][$id]) ? new WP_Post((object)$GLOBALS['posts'][$id]) : null; }
function __(string $s, string $domain = ''): string { return $s; }
function esc_html__(string $s, string $domain = ''): string { return htmlspecialchars($s, ENT_QUOTES); }
function esc_html(string $s): string { return htmlspecialchars($s, ENT_QUOTES); }
function esc_attr(string $s): string { return htmlspecialchars($s, ENT_QUOTES); }
function add_settings_error(...$args): void { $GLOBALS['settings_errors'][] = $args; }
function get_plugin_page_hookname(...$args): string { return 'imagine_page_imagine-reglages'; }
function get_posts(array $args): array { return []; }
class WP_Query {
    private int $index = 0;
    public function __construct(private array $rows = []) {}
    public function have_posts(): bool { return $this->index < count($this->rows); }
    public function the_post(): void { $GLOBALS['current'] = $this->rows[$this->index++]; $GLOBALS['type'] = $GLOBALS['current']['post_type']; }
}
function get_the_ID(): int { return $GLOBALS['current']['ID']; }
function get_permalink(): string { return home_url('/?p=' . get_the_ID()); }
function get_the_title(): string { return 'Titre fictif ' . get_the_ID(); }
function get_the_excerpt(): string { return 'Extrait fictif'; }
function esc_url(string $url): string { return htmlspecialchars($url, ENT_QUOTES); }
function wp_reset_postdata(): void {}
function is_search(): bool { return false; }
require '/repo/wp/themes/imagine/functions.php';
require '/repo/wp/plugins/imagine-site/Partenaires.php';
$checks = [];
$case = $argv[1] ?? 'all';
if (in_array($case, ['links','all'], true)) {
    $fixtures = [
        'external' => ['https://example.org/out', true],
        'protocol_relative' => ['//example.org/out', true],
        'leading_space' => [' https://example.org/out', true],
        'extra_slashes' => ['https:////example.org/out', true],
        'ambiguous_http' => ['https:example.org/out', true],
        'backslash_authority' => ['https:\\example.org/out', true],
        'internal' => ['http://demo.example.org/a', false],
        'internal_case' => ['HTTP://DEMO.EXAMPLE.ORG/a', false],
        'relative' => ['/partenaires/', false],
        'anchor' => ['#suite', false],
    ];
    foreach ($fixtures as $name => [$href, $commercial]) {
        $html = '<a href="' . htmlspecialchars($href, ENT_QUOTES) . '" rel="noopener nofollow">Fictif</a>';
        $actual = Imagine\Theme\imagine_partner_content($html);
        $tags = new WP_HTML_Tag_Processor($actual);
        $tags->next_tag('A');
        $rel = preg_split('/\s+/', trim((string)$tags->get_attribute('rel')));
        $checks[$name] = in_array('sponsored', $rel, true) === $commercial;
        $checks[$name . '_preserve_rel'] = in_array('noopener', $rel, true) && in_array('nofollow', $rel, true);
        $checks[$name . '_unique'] = count($rel) === count(array_unique($rel));
        $checks[$name . '_idempotent'] = Imagine\Theme\imagine_partner_content($actual) === $actual;
    }
    $GLOBALS['type'] = 'post';
    $checks['editorial_unchanged'] = Imagine\Theme\imagine_partner_content($html) === $html;
}
if (in_array($case, ['selection','all'], true)) {
    $class = Imagine\Site\Partenaires::class;
    $GLOBALS['posts'] = [1=>['ID'=>1,'post_type'=>'imagine_partenaire','post_status'=>'publish'],2=>['ID'=>2,'post_type'=>'imagine_partenaire','post_status'=>'draft'],3=>['ID'=>3,'post_type'=>'post','post_status'=>'publish']];
    foreach ([1=>true,0=>false,2=>false,3=>false,99=>false,'bogus'=>false] as $id=>$valid) {
        $GLOBALS['options'][$class::OPTION]=$id;
        $checks['selection_' . $id] = ($class::selection()?->ID === 1) === $valid;
    }
    $GLOBALS['options'][$class::OPTION]=1;
    foreach (['valid'=>['1',1],'zero'=>['0',0],'draft'=>['2',1],'not_partner'=>['3',1],'invalid'=>['bad',1],'null'=>[null,1]] as $key=>[$value,$expected]) {
        $checks['clean_' . $key]=$class::nettoyer($value)===$expected;
    }
}
if (in_array($case, ['injection','all'], true)) {
    Imagine\Site\Partenaires::register();
    $hook = get_plugin_page_hookname();
    $GLOBALS['admin_markup']='<form><input value="imagine_reglages"></form>';
    add_action($hook, static function (): void { echo $GLOBALS['admin_markup']; });
    do_action('admin_menu');
    foreach (['normal'=>'<form><input value="imagine_reglages"></form>','missing_end'=>'<form><input value="imagine_reglages">','missing_group'=>'<form></form>'] as $key=>$markup) {
        $GLOBALS['admin_markup']=$markup;
        ob_start(); do_action($hook); $output=ob_get_clean();
        $checks[$key . '_visible_result']=str_contains($output, $key==='normal' ? 'id="imagine-partenaire-du-mois"' : 'imagine-partenaire-injection-erreur');
        $checks[$key . '_preserves_form']=str_contains($output, $markup) || $key==='normal';
    }
}
if (in_array($case, ['copy','all'], true)) {
    $source=file_get_contents('/repo/wp/themes/imagine/archive-imagine_partenaire.php');
    $checks['archive_copy_internal_navigation']=str_contains($source, 'Les fiches ci-dessous sont des liens internes') && !str_contains($source, 'Les liens vers les partenaires sont déclarés');
}
if (in_array($case, ['list','all'], true)) {
    foreach (['post', 'imagine_partenaire'] as $type) {
        ob_start();
        Imagine\Theme\imagine_list(new WP_Query([['ID' => 1, 'post_type' => $type]]));
        $html = ob_get_clean();
        $tags = new WP_HTML_Tag_Processor($html);
        $present = $tags->next_tag('A');
        $checks['list_' . $type . '_present'] = $present && str_contains($html, 'Titre fictif 1');
        $checks['list_' . $type . '_ordinary_navigation'] = $present && !str_contains((string)$tags->get_attribute('rel'), 'sponsored');
    }
}
$failures=array_keys(array_filter($checks,static fn($v)=>$v!==true));
echo json_encode(['checks'=>$checks,'total'=>count($checks),'failures'=>$failures],JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT),"\n";
exit($failures ? 1 : 0);
