# Échéancier — C-05, prototype non branché

- `Planificateur` et `Versement` : PHP pur. C-01 fournit calendrier, numéros et communes ; C-05 ne les recalcule pas.
- `planifier(Annee $annee, ?int $margeJours = null)` : quatre positions par bloc de quatre numéros, jonctions strictement croissantes. Marge absente : `MARGE_OBLIGATOIRE`. Calendrier incomplet ou dates égales/inversées : refus avant retour du plan. Pas de lecture d’horloge.
- Premier versement à la commande ; reconductions aux communes C-01. Option A : cinq dates dans une fenêtre anniversaire sont possibles, jamais cinq positions dans un bloc.
- `RaccordManuel` : preuve seulement, marqueur fictif C05 + drapeau manuel explicite + passerelle vide. Aucun hook ni encaisseur de production.

## Réglages d’administration

`ReglagesAdministration` utilise l’option `imagine_c05_reglages`, la Settings API, `manage_woocommerce`, le nonce WordPress et des sorties échappées. Pas de REST. Saisie invalide : ancienne option conservée. Option corrompue : lecture refusée.

| Clé | Défaut | Autre valeur |
|---|---|---|
| `marge_jours` | null : aucune durée par défaut, planification bloquée | Entier civil strictement positif |
| `confirmation_premier_sepa` | `avec_marge` | `sans_marge` |
| `apres_rejet` | `restent_dues` | `annuler_restantes` |
| `tarif` | `fige_bloc` | `courant_impayes` |

La nouvelle clé absente des anciennes options reçoit `avec_marge`, sans migration destructive ni nouvelle durée. Deux positions dans une liste de sélection, sans changement de code. Les réglages rejet/tarif ne changent pas.

`Reglages::premierSepaPayeLe(DateTimeImmutable $commande, ?DateTimeImmutable $confirmation)` concerne **uniquement le premier paiement SEPA** :

- `avec_marge` : maximum de la confirmation effective et de commande + `marge_jours`, en jours civils Europe/Brussels ; durée non renseignée : refus explicite ;
- `sans_marge` : confirmation effective, sans délai additionnel ;
- aucune confirmation : null, jamais payé par simple écoulement du temps ; confirmation antérieure à la commande : refus ;
- l’appelant ne considère le premier numéro payé que si la date retournée est non nulle et atteinte ; pour l’état historique avant clôture, elle doit être strictement antérieure à la clôture C-01 ;
- ne modifie aucun numéro, échéance, montant, dette, commande Woo, mandat, droit numérique ou liste d’envoi. Les renouvellements et les autres modes de paiement n’appellent pas cette méthode.

Exemple fictif : commande le 09/04/2027 à 12 h, confirmation à 13 h, marge 7. Avec marge : payé au plus tôt le 16/04 à 12 h ; sans marge : le 09/04 à 13 h. Avec marge, ce numéro n’est pas payé avant sa clôture du 10/04. Aucun report automatique de numéro ni prélèvement ajouté.

## Branchement et tests

Seam parent inchangé, après autoload : `(new Imagine\Pilotage\Echeancier\ReglagesAdministration())->enregistrer();`. Le banc l’appelle explicitement ; aucune modification du bootstrap partagé. L’appelant futur lit les réglages, fournit une confirmation effective et utilise la date projetée pour le premier SEPA. `montantsRestants` reste une projection en centimes sans écriture financière.

Depuis la racine du dépôt, **PHP uniquement dans des conteneurs jetables** : instructions `wp/tests/echeancier-runner/README-sepa.md`. Suite canonique dans le conteneur : `composer test` (inclut Echeancier), `composer lint`, `composer validate --strict --no-check-publish`. Tests dédiés : `ConfirmationPremierSepaTest` ; vraie Settings API et Subscriptions classique/HPOS dans le banc séparé. Aucun test de recette `docs/recette/` automatisé.

Remise courante : `production/C-05/sepa-22nov-1700.md`, `replays/sepa-22nov-1700/`. Anciennes preuves conservées, sans prétendre qu’elles correspondent aux nouveaux octets. PRET n’est ni clôture indépendante ni GO réel/financier.
