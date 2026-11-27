"""Construction unique des tests B09 à partir du contrat B08 corrigé, sources intactes."""
from pathlib import Path
root = Path(__file__).resolve().parents[2]
p = root / 'plugins/imagine-site/tests'
for source, target in [('SujetAdapterTest.php', 'ContactAdapterTest.php'), ('SujetWPStubs.php', 'ContactWPStubs.php')]:
    raw = (p/source).read_text(encoding='utf-8')
    raw = raw.replace('Sujet', 'Contact').replace('sujet', 'contact').replace('b08', 'b09').replace('B08', 'B09')
    raw = raw.replace("['imagine_b09_pages' => ['cooperative' => 1, 'soutenir' => 2, 'contact' => 3, 'enfants' => array_combine(array_keys(\\Imagine\\Site\\CooperativeRegles::PAGES), range(10, 16))]]", "['imagine_b09_pages' => ['contact' => 3]]")
    if target == 'ContactAdapterTest.php':
        raw = raw.replace("$nom = 'Fictif", "self::assertTrue(class_exists(Contact::class), 'Contact absent');\n        $nom = 'Fictif")
    out=p/target
    assert not out.exists()
    out.write_text(raw,encoding='utf-8')
raw=(root/'tests/demo/b08-horslive.php').read_text(encoding='utf-8')
raw=raw.replace('B08','B09').replace('b08','b09').replace('Sujet','Contact').replace('sujet','contact')
a=raw.index('    $mutants = [')
b=raw.index("    if ($mutation !== '')",a)
raw=raw[:a]+'''    $mutants = [
        'slash' => ['Contact.php', "'meta_input' => wp_slash(\\$meta)", "'meta_input' => \\$meta"],
        'consentement' => ['Contact.php', 'type="checkbox" name="consentement"', 'type="checkbox" checked name="consentement"'],
        'mail' => ['Contact.php', '$meta = [', "wp_mail('fictif@example.org', 'Mutation', 'Fictif');\\n        \\$meta = ["],
        'http' => ['Contact.php', '$meta = [', "wp_remote_get('https://example.org/');\\n        \\$meta = ["],
        'prive' => ['Contact.php', "'post_status' => 'private'", "'post_status' => 'publish'"],
        'rest' => ['Contact.php', "'show_in_rest' => false", "'show_in_rest' => true"],
        'export' => ['ContactConfidentialite.php', "return ['data' => \\$data,", "return ['data' => [],"],
        'effacement' => ['ContactConfidentialite.php', 'wp_delete_post($id, true)', 'true'],
        'lecture' => ['Contact.php', "\\$wpdb->last_error !== '' ? null", "\\$wpdb->last_error !== '' ? []"],
        'nonce' => ['Contact.php', "&& wp_verify_nonce(wp_unslash(\\$post['_b09']), 'imagine_contact')", '&& true'],
    ];
'''+raw[b:]
raw=raw.replace("'Cooperative|Soutenir|Contact'", "'Contact'")
(root/'tests/demo/b09-horslive.php').write_text(raw,encoding='utf-8')
