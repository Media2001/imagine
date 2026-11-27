<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\Agenda;
use Imagine\Site\AgendaConfidentialite;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class AgendaAdapterTest extends TestCase
{
    private string $theme;

    protected function setUp(): void
    {
        require __DIR__ . '/AgendaWPStubs.php';
        $GLOBALS['agenda_posts'] = [1 => new \WP_Post()];
        $GLOBALS['agenda_meta'] = [1 => ['imagine_type' => 'partenaire', 'imagine_date' => '2030-01-01', 'imagine_heure' => '12:00', 'imagine_lieu' => 'Lieu fictif', 'imagine_url_partenaire' => 'https://partner.example.org/']];
        $GLOBALS['agenda_current'] = 1;
        $GLOBALS['agenda_now'] = (new \DateTimeImmutable('2030-01-01 11:59:59 UTC'))->getTimestamp();
        $GLOBALS['agenda_hooks'] = $GLOBALS['agenda_boxes'] = $GLOBALS['agenda_translations'] = [];
        $GLOBALS['agenda_loop'] = 0;
        $GLOBALS['wpdb'] = new \AgendaWPDB();
        if (!defined('ABSPATH')) { define('ABSPATH', '/offline/'); }
        $this->theme = dirname(__DIR__, 3) . '/themes/imagine';
        if (!is_file($this->theme . '/functions.php')) { $this->theme = '/repo/wp/themes/imagine'; }
        require $this->theme . '/functions.php';
    }

    public function testAntislashSaisieAffichageAdministrationEtExport(): void
    {
        $GLOBALS['agenda_meta'][1]['imagine_type'] = 'rencontre';
        Agenda::boites();
        AgendaConfidentialite::register();
        $exporters = apply_filters('wp_privacy_personal_data_exporters', []);
        $noms = ['Fictif \\ Atelier', 'Fictif \\\\ double', "Fictif O'Exemple \\ & Atelier", 'Fictif sans antislash'];
        foreach ($noms as $index => $nom) {
            $email = 'antislash-' . $index . '@example.org';
            $_SERVER['REQUEST_METHOD'] = 'POST';
            // WordPress échappe les superglobales avant le handler.
            $_POST = wp_slash(['evenement' => '1', 'nom' => $nom, 'email' => $email,
                'consentement' => '1', 'imagine_agenda_nonce' => 'agenda-test-nonce']);
            for ($attempt = 0; $attempt < 2; $attempt++) {
                try {
                    Agenda::recevoir();
                    self::fail('La réception doit rediriger.');
                } catch (\AgendaRedirect $redirect) {
                    self::assertSame(303, $redirect->status);
                    self::assertSame(get_permalink(1) . '?inscription=enregistree', $redirect->location);
                } catch (\AgendaRefusal $refusal) {
                    self::fail('Saisie antislash refusée : HTTP ' . $refusal->getCode());
                }
            }
            $ids = Agenda::inscriptions($email, 1);
            self::assertCount(1, $ids);
            self::assertSame($nom, get_post_meta($ids[0], 'imagine_agenda_nom', true));
            ob_start();
            $GLOBALS['agenda_boxes']['imagine-agenda-personne'](get_post($ids[0]));
            $html = ob_get_clean();
            self::assertStringContainsString('id="imagine-agenda-admin"', $html);
            self::assertStringContainsString('<dd>' . esc_html($nom) . '</dd>', $html);
            $export = $exporters['imagine-agenda']['callback']($email, 1);
            self::assertTrue($export['done']);
            self::assertCount(1, $export['data']);
            $fields = array_column($export['data'][0]['data'], 'value', 'name');
            self::assertSame($nom, $fields['Nom']);
        }
    }

    public function testBouchonEcritureMetaDesechappeCommeWordPress(): void
    {
        $raw = 'Fictif \\ Atelier';
        update_post_meta(1, 'temoin', $raw);
        self::assertSame(stripslashes($raw), get_post_meta(1, 'temoin', true));
        update_post_meta(1, 'temoin', wp_slash($raw));
        self::assertSame($raw, get_post_meta(1, 'temoin', true));
        $id = wp_insert_post(['post_type' => Agenda::INSCRIPTION, 'post_status' => 'private',
            'post_parent' => 1, 'meta_input' => ['temoin' => $raw]]);
        self::assertSame(stripslashes($raw), get_post_meta($id, 'temoin', true));
    }

    public function testExportErreurArreteEtRepriseNeSauteAucunePage(): void
    {
        $GLOBALS['agenda_meta'][1]['imagine_type'] = 'rencontre';
        self::assertTrue(Agenda::inscrire(1, 'Fictif export', 'export@example.org', false));
        $GLOBALS['wpdb']->fail = true;
        $failed = AgendaConfidentialite::exporter('export@example.org', 1);
        self::assertInstanceOf(\WP_Error::class, $failed, 'Une erreur arrête la pagination native.');
        $GLOBALS['wpdb']->fail = false;
        $retry = AgendaConfidentialite::exporter('export@example.org', 1);
        self::assertTrue($retry['done']);
        self::assertCount(1, $retry['data']);
        self::assertSame('imagine-agenda-2', $retry['data'][0]['item_id']);
        for ($i = 0; $i < 120; $i++) {
            wp_insert_post(['post_type' => Agenda::INSCRIPTION, 'post_status' => 'private', 'post_parent' => 1,
                'meta_input' => ['imagine_agenda_email' => 'export@example.org', 'imagine_agenda_nom' => 'Fictif pagination']]);
        }
        $items = [];
        for ($page = 1; $page <= 3; $page++) {
            $part = AgendaConfidentialite::exporter('export@example.org', $page);
            self::assertSame($page === 3, $part['done']);
            self::assertCount($page === 3 ? 21 : 50, $part['data']);
            $items = array_merge($items, array_column($part['data'], 'item_id'));
        }
        self::assertSame(array_map(static fn ($id) => 'imagine-agenda-' . $id, range(2, 122)), $items);
        self::assertCount(121, array_unique($items));
    }

    public function testProjectionFicheSchemaExecuteLeContenuUneSeuleFois(): void
    {
        $GLOBALS['agenda_posts'][1]->post_content = '<div id="agenda-temoin">[agenda_test]</div>';
        $calls = 0;
        add_filter('the_content', static function (string $html) use (&$calls): string {
            $calls++;
            return str_replace('[agenda_test]', '<strong>Texte rendu &amp; visible ' . $calls . '</strong>', $html);
        }, 11);
        ob_start();
        require $this->theme . '/single-imagine_evenement.php';
        $html = ob_get_clean();
        self::assertSame(1, $calls, 'Un shortcode à effet ne doit pas être exécuté deux fois.');
        self::assertStringNotContainsString('[agenda_test]', $html);
        preg_match('~<script type="application/ld\\+json">(.*?)</script>~s', $html, $match);
        $schema = json_decode($match[1], true, flags: JSON_THROW_ON_ERROR);
        $dom = new \DOMDocument(); $dom->loadHTML('<?xml encoding="UTF-8">' . $html, LIBXML_NOERROR | LIBXML_NOWARNING);
        self::assertSame($dom->getElementById('agenda-temoin')->textContent, $schema['description']);
        self::assertSame('Texte rendu & visible 1', $schema['description']);
    }

    public function testPartenairePasseConserveSonLienSansInscription(): void
    {
        $GLOBALS['agenda_meta'][1]['imagine_date'] = '2020-01-01';
        ob_start();
        require $this->theme . '/single-imagine_evenement.php';
        $html = ob_get_clean();
        self::assertStringContainsString('id="evenement-1"', $html);
        self::assertStringContainsString('Partenariat', $html);
        self::assertStringContainsString('href="https://partner.example.org/" rel="sponsored noopener noreferrer"', $html);
        self::assertStringNotContainsString('inscriptions closes', $html);
        self::assertStringNotContainsString('imagine-agenda-inscription', $html);
        self::assertFalse(Agenda::ouvert(1));
        self::assertFalse(Agenda::inscrire(1, 'Fictif', 'partenaire@example.org', false));
        self::assertCount(1, $GLOBALS['agenda_posts']);
    }

    public function testLibellesLitterauxEtDomainesDesGabarits(): void
    {
        self::assertTrue(is_callable([Agenda::class, 'libellesTypes']), 'Présentation extractible des types manquante.');
        self::assertSame(Agenda::TYPES, Agenda::libellesTypes());
        foreach ([dirname(__DIR__) . '/Agenda.php', dirname(__DIR__) . '/AgendaConfidentialite.php'] as $path) {
            $tokens = token_get_all(file_get_contents($path));
            foreach ($tokens as $i => $token) {
                if (!is_array($token) || $token[0] !== T_STRING || !in_array($token[1], ['__', 'esc_html__', 'esc_html_e'], true)) { continue; }
                $j = $i + 1;
                while ($tokens[$j] !== '(') { $j++; }
                do { $j++; } while (is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE);
                self::assertIsArray($tokens[$j]);
                self::assertSame(T_CONSTANT_ENCAPSED_STRING, $tokens[$j][0], $path . ': traduction extractible');
            }
        }
        foreach (['single', 'archive'] as $name) {
            $source = file_get_contents($this->theme . '/' . $name . '-imagine_evenement.php');
            self::assertStringNotContainsString("'imagine-site'", $source);
            self::assertStringNotContainsString("=== 'partenaire' ?", $source);
        }
    }

    public function testAdministrationSignaleLaSaisieInvalideSansMasquerLeDefaut(): void
    {
        Agenda::boites();
        $box = $GLOBALS['agenda_boxes']['imagine-agenda-champs'];
        foreach ([['imagine_type', 'inconnu'], ['imagine_date', '2030-02-30'], ['imagine_heure', '25:00']] as [$key, $bad]) {
            $old = $GLOBALS['agenda_meta'][1][$key]; $GLOBALS['agenda_meta'][1][$key] = $bad;
            self::assertNull(Agenda::evenement(1));
            self::assertFalse(Agenda::ouvert(1));
            self::assertSame([], Agenda::schema(1));
            ob_start(); $box(get_post(1)); $html = ob_get_clean();
            self::assertStringContainsString('imagine-agenda-incomplet', $html);
            self::assertStringContainsString('Type, date ou heure invalide', $html);
            $GLOBALS['agenda_meta'][1][$key] = $old;
        }
        // Un brouillon correctement saisi ne doit pas recevoir une fausse alerte.
        $GLOBALS['agenda_posts'][1]->post_status = 'draft';
        ob_start(); $box(get_post(1)); $html = ob_get_clean();
        self::assertStringNotContainsString('imagine-agenda-incomplet', $html);
    }

    public function testBorneOuvertEtDoublonTraversentLeVraiAdaptateur(): void
    {
        $GLOBALS['agenda_meta'][1]['imagine_type'] = 'rencontre';
        $start = Agenda::evenement(1)['debut'];
        foreach ([$start - 1 => true, $start => false, $start + 1 => false] as $instant => $expected) {
            $GLOBALS['agenda_now'] = $instant;
            self::assertSame($expected, Agenda::ouvert(1));
        }
        $GLOBALS['agenda_now'] = $start - 1;
        self::assertTrue(Agenda::inscrire(1, 'Fictif doublon', ' FICTIF@EXAMPLE.ORG ', false));
        $ids = Agenda::inscriptions('fictif@example.org', 1);
        self::assertCount(1, $ids);
        self::assertTrue(Agenda::inscrire(1, 'Autre nom', 'fictif@example.org', true));
        self::assertSame($ids, Agenda::inscriptions('fictif@example.org', 1));
        self::assertSame('0', get_post_meta($ids[0], 'imagine_agenda_consentement', true));
        self::assertCount(4, $GLOBALS['wpdb']->locks);
        $GLOBALS['wpdb']->fail = true;
        self::assertFalse(Agenda::inscrire(1, 'Panne fictive', 'panne@example.org', false));
        self::assertCount(2, $GLOBALS['agenda_posts']);
        $GLOBALS['wpdb']->fail = false;
        $GLOBALS['agenda_now'] = $start;
        self::assertFalse(Agenda::inscrire(1, 'Trop tard', 'tard@example.org', false));
        self::assertCount(2, $GLOBALS['agenda_posts']);
    }

    public function testLiensDuCorpsPartenaireEtContreExemples(): void
    {
        $content = '<a href="https://outside.example.org/" rel="nofollow">Externe</a>'
            . '<a href=" https:////outside.example.org/">Ambigu</a>'
            . '<a href="https://demo.example.org/fiche">Interne absolu</a>'
            . '<a href="/fiche">Interne relatif</a><a href="#lieu">Ancre</a>';
        $dom = new \DOMDocument();
        $dom->loadHTML(apply_filters('the_content', $content));
        $links = iterator_to_array($dom->getElementsByTagName('a'));
        self::assertCount(5, $links);
        self::assertSame('nofollow sponsored', $links[0]->getAttribute('rel'));
        self::assertSame('sponsored', $links[1]->getAttribute('rel'));
        foreach (array_slice($links, 2) as $link) { self::assertSame('', $link->getAttribute('rel')); }
        $GLOBALS['agenda_meta'][1]['imagine_type'] = 'rencontre';
        self::assertSame($content, apply_filters('the_content', $content));
        $GLOBALS['agenda_posts'][1]->post_type = 'imagine_partenaire';
        self::assertStringContainsString('nofollow sponsored', apply_filters('the_content', $content), 'B05 reste couvert.');
    }
}
