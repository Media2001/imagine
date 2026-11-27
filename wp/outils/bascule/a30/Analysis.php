<?php

declare(strict_types=1);

namespace Imagine\OfflineDryRun;

/** Pure projection: no WordPress, filesystem, SQL, dates, mail or network. */
final class Analysis
{
    public static function analyse(
        array $rows,
        array $validProducts,
        array $matches,
        bool $neutralised,
        string $storage
    ): array {
        $result = [];
        foreach ($rows as $row) {
            $product = $row['product'] !== null && ($validProducts[$row['product']] ?? false)
                ? $row['product'] : null;
            if ($row['rejected']) {
                $issue = 'refuse_a13';
            } elseif ($row['email'] === '') {
                $issue = 'sans_email';
            } elseif ($product === null) {
                $issue = 'type_a_decider';
            } elseif ($neutralised) {
                // Not a sixth issue: account attribution is unavailable on this copy.
                $issue = null;
            } else {
                $count = $matches[$row['line']] ?? 0;
                if ($count > 1) {
                    throw new \RuntimeException('A30_EXISTING_EMAIL_AMBIGUOUS');
                }
                $issue = $count === 1 ? 'compte_existant' : 'compte_a_creer';
            }
            $result[] = ['line' => $row['line'], 'issue' => $issue,
                'product' => $product, 'payment' => $row['payment']];
        }
        return ['schema' => 'imagine-a30-private-v1', 'storage' => $storage,
            'neutralised' => $neutralised, 'rows' => $result];
    }
}
