<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Adaptateur de lecture : les lignes C15/C18 sont consommées, pas réinterprétées. */
final class TableauBordNatives
{
    public static function lire(): array
    {
        // C18 assure pagination, cohérence du titulaire, état B02 et méthode C15.
        $rows = ExtractionsNatives::lire('etat', ['etat' => '']);
        $data = ['abonnements' => [], 'mouvements' => [],
            'echeances' => EcheancesNatives::lire('echeances', 180),
            'echecs' => EcheancesNatives::lire('echecs', 30)];
        foreach ($rows as $row) {
            $data['abonnements'][] = array_intersect_key($row, array_flip(['etat', 'mode_paiement']));
            $sub = wcs_get_subscription((int) $row['abonnement_id']);
            if (!$sub) {
                throw new \RuntimeException('Abonnement disparu pendant la lecture.');
            }
            $data['mouvements'][] = ['creation' => $sub->get_date_created()?->getTimestamp() ?? 0,
                'fin' => (int) $sub->get_time('end'), 'etat' => $sub->get_status()];
        }
        $data['maintenant'] = time();
        $out = [];
        foreach (TableauBordRegles::catalogue() as $id => $definition) {
            $out[$id] = TableauBordRegles::calculer($id, $data);
        }
        return $out;
    }
}
