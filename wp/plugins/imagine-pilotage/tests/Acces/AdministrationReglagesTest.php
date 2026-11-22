<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Acces;

use Imagine\Pilotage\Acces\AdministrationReglages;
use Imagine\Pilotage\Acces\Moteur;
use Imagine\Pilotage\Acces\Reglages;
use Imagine\Pilotage\Robots\Decision as DecisionRobot;
use Imagine\Pilotage\Robots\Motif as MotifRobot;
use PHPUnit\Framework\TestCase;

final class AdministrationReglagesTest extends TestCase
{
    protected function setUp(): void
    {
        WordPressFictif::reinitialiser();
    }

    public function testAdaptateurExposeTroisChampsViaSettingsApiSansEffetAuChargement(): void
    {
        $admin = new AdministrationReglages();
        self::assertSame([], WordPressFictif::$appels);
        $admin->brancher();
        self::assertSame(['admin_menu', 'admin_init'], array_keys(WordPressFictif::$appels['hooks']));
        (WordPressFictif::$appels['hooks']['admin_menu'])();
        (WordPressFictif::$appels['hooks']['admin_init'])();
        $menu = WordPressFictif::$appels['menu'];
        self::assertSame('manage_options', $menu['capacite']);
        self::assertSame('imagine-acces', $menu['slug']);
        $setting = WordPressFictif::$appels['setting'];
        self::assertSame('imagine_acces_reglages', $setting['groupe']);
        self::assertSame('imagine_acces_reglages', $setting['option']);
        self::assertSame('array', $setting['args']['type']);
        self::assertFalse($setting['args']['show_in_rest']);
        self::assertSame((new Reglages())->options(), $setting['args']['default']);
        self::assertCount(3, WordPressFictif::$appels['champs']);
        foreach (WordPressFictif::$appels['champs'] as $id => $champ) {
            self::assertSame($id, $champ['args']['label_for']);
            self::assertSame($menu['slug'], $champ['page']);
            self::assertSame(WordPressFictif::$appels['section']['id'], $champ['section']);
        }
    }

    public function testEnregistrementRelectureEtMoteurPrennentChaquePositionSansModifierLeCode(): void
    {
        $admin = new AdministrationReglages();
        $admin->enregistrer();
        $nettoyer = WordPressFictif::$appels['setting']['args']['sanitize_callback'];
        foreach (['ferme_tous', 'equipe'] as $futur) {
            foreach (['extrait', 'complet'] as $robot) {
                foreach (['ferme', 'ouvert'] as $anterieur) {
                    $soumis = ['contenu_futur' => $futur, 'pdf_robot' => $robot,
                        'pdf_anterieur_abonnement' => $anterieur];
                    WordPressFictif::$option = $nettoyer($soumis + ['inconnu' => 'ouvert']);
                    self::assertSame($soumis, WordPressFictif::$option);
                    self::assertSame($soumis, $nettoyer(WordPressFictif::$option));
                    $reglages = (new AdministrationReglages())->lire();
                    self::assertSame($soumis, $reglages->options());
                    $future = (new Moteur())->decider(
                        DecisionTest::contenu(['sortie' => DecisionTest::date('2026-11-22')]),
                        DecisionTest::visiteur([['type' => 'equipe', 'role' => 'redaction']]),
                        DecisionTest::robot(),
                        DecisionTest::date(),
                        null,
                        $reglages,
                    );
                    self::assertSame($futur === 'equipe', $future->complet);
                    $pdfRobot = (new Moteur())->decider(
                        DecisionTest::contenu(['type' => 'pdf']),
                        DecisionTest::visiteur([], false),
                        new DecisionRobot(MotifRobot::VerifieDns, 'google'),
                        DecisionTest::date(),
                        null,
                        $reglages,
                    );
                    self::assertSame($robot === 'complet', $pdfRobot->complet);
                    $ancien = (new Moteur())->decider(
                        DecisionTest::contenu(['type' => 'pdf']),
                        DecisionTest::visiteur([AbonnementTest::droit(['debut' => DecisionTest::date('2026-11-01')])]),
                        DecisionTest::robot(),
                        DecisionTest::date(),
                        null,
                        $reglages,
                    );
                    self::assertSame($anterieur === 'ouvert', $ancien->complet);
                }
            }
        }
        self::assertSame(['imagine_acces_reglages'], array_unique(WordPressFictif::$appels['lectures']));
    }

    public function testStockageAbsentInvalideEtPanneRestentPrudents(): void
    {
        $admin = new AdministrationReglages();
        foreach ([null, 'complet', ['pdf_robot' => '<script>complet</script>'], new \stdClass()] as $option) {
            WordPressFictif::$option = $option;
            self::assertSame((new Reglages())->options(), $admin->lire()->options());
            self::assertSame((new Reglages())->options(), $admin->nettoyer($option));
        }
        WordPressFictif::$panne = true;
        self::assertSame((new Reglages())->options(), $admin->lire()->options());
    }

    public function testPageAdminDeuxChoixParChampEtDelegationNonceAuCoeur(): void
    {
        $admin = new AdministrationReglages();
        $admin->enregistrer();
        foreach ([false, true] as $ouvert) {
            WordPressFictif::$option = (new Reglages($ouvert, $ouvert, $ouvert))->options();
            ob_start();
            $admin->page();
            $html = ob_get_clean();
            $dom = new \DOMDocument();
            self::assertTrue($dom->loadHTML('<meta charset="utf-8">' . $html));
            $xpath = new \DOMXPath($dom);
            self::assertSame(1, $xpath->query('//form[@method="post"][@action="options.php"]')->length);
            self::assertSame(3, $xpath->query('//select')->length);
            foreach (WordPressFictif::$option as $cle => $valeur) {
                $nom = 'imagine_acces_reglages[' . $cle . ']';
                self::assertSame(2, $xpath->query('//select[@name="' . $nom . '"]/option')->length);
                $selection = $xpath->query('//select[@name="' . $nom . '"]/option[@selected]');
                self::assertSame(1, $selection->length);
                self::assertSame($valeur, $selection->item(0)->getAttribute('value'));
            }
            self::assertSame('imagine_acces_reglages', WordPressFictif::$appels['fields_group']);
            self::assertSame('imagine_acces_reglages', WordPressFictif::$appels['errors_option']);
            self::assertTrue(WordPressFictif::$appels['submit_button']);
        }
        foreach (WordPressFictif::$appels['traductions'] as [$texte, $domaine]) {
            self::assertSame('imagine-pilotage', $domaine);
            self::assertNotSame('', $texte);
        }
        WordPressFictif::$autorise = false;
        ob_start();
        $admin->page();
        self::assertSame('', ob_get_clean());
        self::assertSame('manage_options', WordPressFictif::$appels['capacite']);
    }
}
