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
        require dirname(__DIR__, 3) . '/themes/imagine/functions.php';
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
