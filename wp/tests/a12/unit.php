<?php

declare(strict_types=1);

namespace Imagine\ContentInventory\Tests;

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};

$file = '/subject/a12/Declarations.php';
$check('declaration_parser_implemented', is_file($file));
if (is_file($file)) {
    require $file;
    $source = <<<'PHP'
<?php
// register_post_type('comment_fake', []);
$x = "register_taxonomy('string_fake', 'post')";
function register_post_type($a, $b) {}
$obj->register_post_type('method_fake', []);
Foo::register_taxonomy('static_fake', 'post');
register_post_type('a12_article', []);
\register_taxonomy('a12_rubrique', ['a12_article']);
register_post_type($dynamic, []);
register_post_type('prefix_' . $suffix, []);
register_post_type('a12_empty', []);
PHP;
    $r = \Imagine\ContentInventory\Declarations::parse($source);
    $check('literal_post_types_not_comments_strings_or_methods', $r['post_types'] === ['a12_article', 'a12_empty']);
    $check('literal_fully_qualified_taxonomy', $r['taxonomies'] === ['a12_rubrique']);
    $check('dynamic_and_concatenated_arguments_explicit', $r['unresolved_calls'] === 2);
    $r = \Imagine\ContentInventory\Declarations::parse('<?php register_post_type("name@example.org", []);');
    $check('invalid_identifier_never_exported', $r['post_types'] === [] && $r['unresolved_calls'] === 1);
}
$result = [
    'suite' => 'A12-pure-unit', 'checks' => $checks,
    'exit_code' => (int) in_array('FAIL', array_column($checks, 'status'), true),
];
file_put_contents('/report/unit.json', json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n");
echo json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n";
exit($result['exit_code']);
