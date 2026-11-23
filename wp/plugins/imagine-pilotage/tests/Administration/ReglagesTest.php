<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Tests\Administration;

use Imagine\Pilotage\Administration\Reglages;
use Imagine\Pilotage\Acces\AdministrationReglages as Acces;
use Imagine\Pilotage\Echeancier\ReglagesAdministration as Paiement;
use Imagine\Pilotage\Envoi\AdministrationFormatExport as Envoi;
use PHPUnit\Framework\Attributes\PreserveGlobalState;
use PHPUnit\Framework\Attributes\RunTestsInSeparateProcesses;
use PHPUnit\Framework\TestCase;

#[RunTestsInSeparateProcesses]
#[PreserveGlobalState(false)]
final class ReglagesTest extends TestCase
{
    private Reglages $screen;

    protected function setUp(): void
    {
        require_once __DIR__ . '/WordPressFictif.php';
        $GLOBALS['wpdb'] = new class {
            public string $options = 'options';

            public function esc_like(string $text): string
            {
                return $text;
            }

            public function prepare(string $sql, string $value): string
            {
                return $sql;
            }

            public function get_col(string $sql): array
            {
                return [];
            }
        };
        $this->screen = new Reglages();
        $this->screen->brancher();
    }

    public function testClesExactesEtChoixStrictsConserventValeursPrecedentes(): void
    {
        foreach ([Acces::OPTION => 'nettoyerAcces', Paiement::OPTION => 'nettoyerPaiement'] as $option => $method) {
            $valid = $this->screen->defauts()[$option];
            WordPressFictif::$options[$option] = $valid;
            self::assertSame($valid, $this->screen->$method($valid));
            $extra = $valid + ['inconnue' => 'x'];
            $missing = $valid;
            unset($missing[array_key_first($missing)]);
            $invalid = $valid;
            $invalid[array_key_first($invalid)] = ['type-invalide'];
            foreach (['texte', [], $extra, $missing, $invalid] as $value) {
                $count = count(WordPressFictif::$errors);
                self::assertSame($valid, $this->screen->$method($value));
                self::assertCount($count + 1, WordPressFictif::$errors);
                self::assertSame([], $this->events());
            }
        }
    }

    public function testPremierPaiementInvalideConserveDefautDeclare(): void
    {
        $valid = $this->screen->defauts()[Paiement::OPTION];
        $invalid = $valid;
        $invalid['marge_jours'] = ['invalide'];
        self::assertSame($valid, $this->screen->nettoyerPaiement($invalid));
        self::assertSame($valid, (new Paiement())->defauts());
    }

    public function testJournalUniqueApresPersistancePasSurNoopOuRefus(): void
    {
        $old = $this->screen->defauts()[Acces::OPTION];
        $new = array_replace($old, ['contenu_futur' => 'equipe']);
        WordPressFictif::$options[Acces::OPTION] = $old;
        $this->screen->nettoyerAcces($new);
        self::assertSame([], $this->events());
        update_option(Acces::OPTION, $new);
        self::assertCount(1, $this->events());
        self::assertSame([$new], WordPressFictif::$persistedAtJournal);
        $event = array_values($this->events())[0];
        self::assertSame($old, $event['avant']);
        self::assertSame($new, $event['apres']);
        self::assertSame(7, $event['qui_id']);
        self::assertSame('admin-fictif', $event['qui_login']);
        self::assertMatchesRegularExpression('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/', $event['quand_utc']);
        update_option(Acces::OPTION, $new);
        update_option(Acces::OPTION, $this->screen->nettoyerAcces($new + ['extra' => 1]));
        self::assertCount(1, $this->events());
    }

    public function testPremiereCreationJournaliseeUneFois(): void
    {
        $new = array_replace($this->screen->defauts()[Acces::OPTION], ['pdf_robot' => 'complet']);
        add_option(Acces::OPTION, $new);
        self::assertCount(1, $this->events());
        self::assertSame([$new], WordPressFictif::$persistedAtJournal);
    }

    public function testJournalKoRefuseModificationEtPrevient(): void
    {
        $old = $this->screen->defauts()[Acces::OPTION];
        WordPressFictif::$options[Acces::OPTION] = $old;
        WordPressFictif::$journalKo = true;
        update_option(Acces::OPTION, array_replace($old, ['contenu_futur' => 'equipe']));
        self::assertSame($old, get_option(Acces::OPTION));
        self::assertSame([], $this->events());
        self::assertStringContainsString('journal', WordPressFictif::$errors[0][2]);
    }

    public function testJournalKoRefusePremiereCreationSansInventerOption(): void
    {
        WordPressFictif::$journalKo = true;
        add_option(Acces::OPTION, array_replace($this->screen->defauts()[Acces::OPTION], ['pdf_robot' => 'complet']));
        self::assertArrayNotHasKey(Acces::OPTION, WordPressFictif::$options);
        self::assertCount(1, WordPressFictif::$errors);
    }

    public function testApercuCsvRelitFormatPersiste(): void
    {
        WordPressFictif::$options[Envoi::OPTION] = ['ville', 'pays'];
        self::assertSame("ville,pays\n\"Ville Fictive\",BE\n", $this->screen->apercuCsv());
        WordPressFictif::$options[Envoi::OPTION] = ['pays'];
        self::assertSame("pays\nBE\n", $this->screen->apercuCsv());
    }

    public function testPageDelegueNonceEtLitPaiementNormalise(): void
    {
        WordPressFictif::$options[Paiement::OPTION] = [];
        ob_start();
        $this->screen->page();
        $html = ob_get_clean();
        self::assertSame(Reglages::GROUPE, WordPressFictif::$calls['nonce_group']);
        self::assertStringContainsString('action="options.php"', $html);
        self::assertStringContainsString('value="avec_marge" selected="selected"', $html);
        self::assertStringContainsString('ne modifient pas encore le paiement', $html);
        self::assertStringContainsString('lus par le paywall', $html);
        self::assertSame(8, substr_count($html, 'À confirmer par Imagine'));
    }

    public function testRefusPageSansManageOptions(): void
    {
        WordPressFictif::$autorise = false;
        $this->expectException(\RuntimeException::class);
        $this->expectExceptionCode(403);
        $this->screen->page();
    }

    public function testOptionsMemeGroupePrive(): void
    {
        $this->screen->enregistrer();
        self::assertCount(3, WordPressFictif::$settings);
        foreach (WordPressFictif::$settings as $args) {
            self::assertSame(Reglages::GROUPE, $args['group']);
            self::assertFalse($args['show_in_rest']);
        }
    }

    private function events(): array
    {
        return array_filter(
            WordPressFictif::$options,
            static fn (string $name): bool => str_starts_with($name, Reglages::JOURNAL),
            ARRAY_FILTER_USE_KEY
        );
    }
}
