<?php

declare(strict_types=1);

namespace Imagine\Site\Tests;

use Imagine\Site\NewslettersRegles;
use PHPUnit\Framework\TestCase;

final class NewslettersReglesTest extends TestCase
{
    public function testChoixDateEtRechargement(): void
    {
        $catalogue = [['id' => 'main', 'titre' => 'Fictif', 'presentation' => 'Fictif.', 'principale' => true]];
        $on = NewslettersRegles::choisir($catalogue, [], ['main'], '2026-11-26T10:00:00Z', 'lecteur');
        self::assertSame(['main' => ['choix' => true, 'date_utc' => '2026-11-26T10:00:00Z', 'origine' => 'lecteur']], $on);
        self::assertSame($on, NewslettersRegles::choisir($catalogue, $on, ['main'], '2026-11-26T10:01:00Z', 'lecteur'));
        $off = NewslettersRegles::choisir($catalogue, $on, [], '2026-11-26T10:02:00Z', 'lecteur');
        self::assertFalse($off['main']['choix']);
        self::assertSame('2026-11-26T10:02:00Z', $off['main']['date_utc']);
    }

    public function testIdentifiantInconnuRefuse(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        NewslettersRegles::choisir([], [], ['inconnu'], '2026-11-26T10:00:00Z', 'lecteur');
    }

    public function testCatalogueDupliqueRefuse(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $row = ['id' => 'main', 'titre' => 'Fictif', 'presentation' => 'Fictif.', 'principale' => true];
        NewslettersRegles::catalogue([$row, $row]);
    }

    public function testCatalogueEtQuatriemeSansCode(): void
    {
        $rows = [['id' => 'principale', 'titre' => 'Lettre fictive', 'presentation' => 'Présentation fictive.', 'principale' => true]];
        self::assertSame($rows, NewslettersRegles::catalogue($rows));
        $rows[] = ['id' => 'quatrieme', 'titre' => 'Autre', 'presentation' => 'Autre lettre.', 'principale' => false];
        self::assertCount(2, NewslettersRegles::catalogue($rows));
    }
}
