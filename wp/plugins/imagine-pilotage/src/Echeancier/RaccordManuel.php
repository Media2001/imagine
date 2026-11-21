<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Echeancier;

use DateTimeZone;
use LogicException;
use WC_Subscription;

/** Adaptateur de preuve manuel seulement, aucun hook enregistré au chargement. */
final class RaccordManuel
{
    public function positionner(WC_Subscription $abonnement, Versement $prochain): void
    {
        $this->verifier($abonnement);
        if ($prochain->initial || !$abonnement->can_date_be_updated('next_payment')) {
            throw new LogicException('La prochaine position doit être un renouvellement modifiable.');
        }
        $abonnement->update_dates([
            'next_payment' => $prochain->date->setTimezone(new DateTimeZone('UTC'))->format('Y-m-d H:i:s'),
        ], 'gmt');
        $abonnement->save();
    }

    /** Fin de projection du prototype, pas annulation de la dette ou du contrat. */
    public function arreterProjection(WC_Subscription $abonnement): void
    {
        $this->verifier($abonnement);
        $abonnement->update_dates(['next_payment' => 0], 'gmt');
        $abonnement->save();
    }

    private function verifier(WC_Subscription $abonnement): void
    {
        if (!$abonnement->is_manual() || $abonnement->get_meta('imagine_c05_fixture') !== 'yes') {
            throw new LogicException('Prototype réservé aux abonnements manuels fictifs C05.');
        }
    }
}
