<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Contact;
use Imagine\Site\ContactConfidentialite;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class ContactAdapterTest extends TestCase
{
    protected function setUp(): void
    {
        require __DIR__ . '/ContactWPStubs.php';
    }

    public function testFormulaireLocalConsentementFacultatifEtPasEnumeration(): void
    {
        self::assertTrue(class_exists(Contact::class), 'Formulaire contact absent');
        $form = Contact::formulaire();
        self::assertStringContainsString('name="nom"', $form);
        self::assertStringContainsString('type="email"', $form);
        self::assertStringContainsString('name="contact"', $form);
        self::assertStringContainsString('type="checkbox"', $form);
        self::assertStringNotContainsString('checked', $form);
        self::assertStringNotContainsString('newsletter', $form);
        $a = Contact::traiter(['_b09' => 'nonce', 'nom' => 'Nom fictif', 'email' => 'FICTIF@example.org', 'contact' => '<b>Contact fictif</b>']);
        $b = Contact::traiter(['_b09' => 'nonce', 'nom' => 'Inconnu fictif', 'email' => 'inconnu@example.org', 'contact' => 'Autre contact', 'consentement' => '1']);
        self::assertSame($a, $b, 'Même message, aucun compte recherché');
        self::assertStringContainsString('enregistrée', $a);
        self::assertCount(2, $GLOBALS['b09_posts'], 'Témoin positif');
        self::assertSame('private', reset($GLOBALS['b09_posts'])->post_status);
        self::assertSame('0', $GLOBALS['b09_meta'][100]['imagine_contact_consentement']);
        self::assertSame('1', $GLOBALS['b09_meta'][101]['imagine_contact_consentement']);
        self::assertSame('fictif@example.org', $GLOBALS['b09_meta'][100]['imagine_contact_email']);
        self::assertSame(['mail' => 0, 'http' => 0], $GLOBALS['b09_calls']);
        foreach ([['_b09' => 'faux', 'nom' => 'Fictif', 'email' => 'fictif@example.org', 'contact' => 'Rejeu signé faux'], ['_b09' => 'nonce', 'nom' => []], ['_b09' => 'nonce', 'nom' => 'a', 'email' => 'bad', 'contact' => 'x']] as $bad) {
            self::assertStringContainsString('refusée', Contact::traiter($bad));
        }
        self::assertCount(2, $GLOBALS['b09_posts']);
        Contact::types();
        self::assertFalse($GLOBALS['b09_types'][Contact::TYPE]['public']);
        self::assertFalse($GLOBALS['b09_types'][Contact::TYPE]['show_in_rest']);
        self::assertSame('manage_options', $GLOBALS['b09_types'][Contact::TYPE]['capabilities']['read_post']);
    }

    public function testAntislashDuPostAuDetailAdminEtExport(): void
    {
        self::assertTrue(class_exists(Contact::class), 'Contact absent');
        $nom = 'Fictif \\ rédaction';
        $texte = "Contact C:\\dossier\\fichier et l'apostrophe\nDeuxième ligne \\";
        $_POST = wp_slash(['_b09' => 'nonce', 'nom' => $nom, 'email' => 'slash@example.org', 'contact' => $texte]);
        self::assertStringContainsString('enregistrée', Contact::traiter($_POST));
        self::assertCount(1, $GLOBALS['b09_posts']);
        self::assertSame($texte, get_post_meta(100, 'imagine_contact_texte', true));
        self::assertSame($nom, get_post_meta(100, 'imagine_contact_nom', true));
        Contact::register();
        foreach ($GLOBALS['b09_hooks']['add_meta_boxes'] as $callback) {
            $callback();
        }
        ob_start();
        ($GLOBALS['b09_boxes']['imagine-contact-prive'])(get_post(100));
        $detail = ob_get_clean();
        self::assertStringContainsString(nl2br(esc_html($texte)), $detail);
        self::assertStringContainsString(esc_html($nom), $detail);
        $export = ContactConfidentialite::exporter('slash@example.org');
        self::assertCount(1, $export['data'], 'Export positif avant lecture du texte');
        self::assertSame($texte, array_column($export['data'][0]['data'], 'value', 'name')['Message']);
        self::assertSame($nom, array_column($export['data'][0]['data'], 'value', 'name')['Nom']);
        self::assertSame(['mail' => 0, 'http' => 0], $GLOBALS['b09_calls']);
    }

    public function testErreursEcritureJamaisAnnonceesCommeSucces(): void
    {
        self::assertTrue(class_exists(Contact::class), 'Persistance absente');
        $post = ['_b09' => 'nonce', 'nom' => 'Fictif', 'email' => 'fictif@example.org', 'contact' => 'Fictif'];
        foreach (['b09_fail_insert', 'b09_fail_meta'] as $fault) {
            $GLOBALS[$fault] = true;
            self::assertStringContainsString('refusée', Contact::traiter($post));
            self::assertSame([], $GLOBALS['b09_posts']);
            $GLOBALS[$fault] = false;
        }
    }

    public function testDetailReserveAAdministrationEtCapacitesNatives(): void
    {
        self::assertTrue(Contact::enregistrer('Fictif', 'fictif@example.org', 'B09_TEMOIN_ADMIN', true));
        Contact::register();
        foreach ($GLOBALS['b09_hooks']['add_meta_boxes'] as $callback) {
            $callback();
        }
        $render = $GLOBALS['b09_boxes']['imagine-contact-prive'];
        ob_start();
        $render(get_post(100));
        self::assertStringContainsString('B09_TEMOIN_ADMIN', ob_get_clean());
        $GLOBALS['b09_admin'] = false;
        ob_start();
        $render(get_post(100));
        self::assertSame('', ob_get_clean());
        Contact::types();
        $args = $GLOBALS['b09_types'][Contact::TYPE];
        foreach (['public', 'publicly_queryable', 'show_in_rest', 'can_export'] as $key) {
            self::assertFalse($args[$key]);
        }
        self::assertTrue($args['exclude_from_search']);
        foreach ($args['capabilities'] as $key => $cap) {
            self::assertSame($key === 'create_posts' ? 'do_not_allow' : 'manage_options', $cap);
        }
    }

    public function testRaccordSeulementContactPrincipalEtMenuFooterNatif(): void
    {
        \Imagine\Site\AutresPages::register();
        foreach ($GLOBALS['b09_hooks']['after_setup_theme'] as $callback) {
            $callback();
        }
        self::assertSame(['imagine-footer' => 'Navigation de pied de page'], $GLOBALS['b09_menus']);
        $render = $GLOBALS['b09_hooks']['the_content'][0];
        self::assertStringContainsString('<form id="imagine-contact"', $render('Éditorial natif'));
        self::assertStringStartsWith('Éditorial natif', $render('Éditorial natif'));
        foreach (['b09_singular', 'b09_loop', 'b09_main'] as $flag) {
            $GLOBALS[$flag] = false;
            self::assertSame('Sans raccord', $render('Sans raccord'));
            $GLOBALS[$flag] = true;
        }
        $GLOBALS['b09_page'] = 4;
        self::assertSame('FAQ native inchangée', $render('FAQ native inchangée'));
    }

    public function testSuppressionPartielleRefuseSuccesEtReprendSansPostNiEmail(): void
    {
        self::assertTrue(Contact::enregistrer('Fictif', 'partiel@example.org', 'Texte personnel fictif', false));
        self::assertTrue(Contact::enregistrer('Tiers', 'tiers@example.org', 'Texte tiers', true));
        $GLOBALS['b09_partial_delete'] = true;
        $first = ContactConfidentialite::effacer('partiel@example.org');
        self::assertNull(get_post(100), 'Le post a réellement disparu');
        self::assertSame('Texte personnel fictif', get_post_meta(100, 'imagine_contact_texte', true));
        self::assertSame('', get_post_meta(100, 'imagine_contact_email', true), 'La reprise ne peut pas rechercher cette adresse');
        self::assertFalse($first['done'], 'Une méta personnelle orpheline interdit done');
        self::assertTrue($first['items_retained']);
        self::assertFalse($first['items_removed']);
        $GLOBALS['b09_partial_delete'] = false;
        $GLOBALS['b09_fail_meta_delete'] = true;
        self::assertFalse(ContactConfidentialite::effacer('partiel@example.org')['done']);
        $GLOBALS['b09_fail_meta_delete'] = false;
        $last = ContactConfidentialite::effacer('partiel@example.org');
        self::assertTrue($last['done']);
        self::assertTrue($last['items_removed']);
        self::assertSame([], $GLOBALS['b09_meta'][100] ?? []);
        self::assertSame('Texte tiers', get_post_meta(101, 'imagine_contact_texte', true));
        self::assertCount(1, ContactConfidentialite::exporter('tiers@example.org')['data']);
        self::assertSame(['imagine_b09_pages' => ['contact' => 3]], $GLOBALS['b09_options']);
    }

    public function testPrivacyPaginationAdresseTiersErreursEtEffacement(): void
    {
        self::assertTrue(class_exists(ContactConfidentialite::class), 'Privacy B09 absente');
        for ($i = 0; $i < 101; $i++) {
            self::assertTrue(Contact::enregistrer('Fictif', 'fictif@example.org', 'Contact privé ' . $i, false));
        }
        self::assertTrue(Contact::enregistrer('Tiers', 'tiers@example.org', 'Contact tiers', true));
        self::assertCount(102, $GLOBALS['b09_posts']);
        $ids = [];
        foreach ([1 => 50, 2 => 50, 3 => 1] as $page => $count) {
            $out = ContactConfidentialite::exporter('FICTIF@example.org', $page);
            self::assertCount($count, $out['data']);
            self::assertSame($page === 3, $out['done']);
            self::assertStringNotContainsString('Contact tiers', json_encode($out));
            $ids = [...$ids, ...array_column($out['data'], 'item_id')];
        }
        self::assertCount(101, array_unique($ids));
        $GLOBALS['wpdb']->fail = true;
        self::assertInstanceOf(\WP_Error::class, ContactConfidentialite::exporter('fictif@example.org'));
        self::assertFalse(ContactConfidentialite::effacer('fictif@example.org')['done']);
        $GLOBALS['wpdb']->fail = false;
        $GLOBALS['b09_fail_delete'] = true;
        self::assertFalse(ContactConfidentialite::effacer('fictif@example.org')['done']);
        $GLOBALS['b09_fail_delete'] = false;
        foreach ([1, 2, 3] as $page) {
            $result = ContactConfidentialite::effacer('fictif@example.org', $page);
        }
        self::assertTrue($result['done']);
        self::assertSame([], ContactConfidentialite::exporter('fictif@example.org')['data']);
        self::assertCount(1, ContactConfidentialite::exporter('tiers@example.org')['data']);
        self::assertCount(1, $GLOBALS['b09_posts']);
    }
}
