<?php

declare(strict_types=1);

namespace Imagine\Theme;

/** Vitesse fixe ; seul le HTML déjà autorisé par imagine_article_body() entre ici. */
const IMAGINE_READING_WORDS_PER_MINUTE = 200;

function imagine_reading_minutes(string $html): int
{
    // Le bloc de droits reste affiché, mais n'allonge pas la durée de l'extrait.
    $html = (string) preg_replace('~<aside\b[^>]*\bdata-imagine-bloc="[^"]*"[^>]*>.*?</aside>~is', '', $html);
    $html = (string) preg_replace('~</(?:p|div|li|h[1-6]|figcaption|blockquote|section)>|<br\b[^>]*>~i', ' ', $html);
    $text = html_entity_decode(wp_strip_all_tags($html), ENT_QUOTES | ENT_HTML5, 'UTF-8');
    $words = preg_match_all("/[\p{L}\p{N}]+(?:[’'-][\p{L}\p{N}]+)*/u", $text);
    return max(1, (int) ceil(($words ?: 0) / IMAGINE_READING_WORDS_PER_MINUTE));
}
