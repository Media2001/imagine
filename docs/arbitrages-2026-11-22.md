# Arbitrages — 22 novembre 2026

## Principe, posé par Ced le 22/11

**Une règle métier que le client n'a pas encore tranchée ne bloque pas un lot.** Elle devient un **réglage**, modifiable dans l'administration sans toucher au code, avec une valeur par défaut prudente. Le jour où Imagine répond, on change le réglage.

Conséquences pour tout lot, présent et à venir :

- la règle ouverte est isolée en un seul endroit, derrière un réglage nommé ;
- la valeur par défaut est la plus prudente : en cas de doute sur un droit d'accès, c'est fermé ;
- chaque valeur possible du réglage est testée ;
- le lot se clôt sans attendre la réponse ; la question reste inscrite dans `docs/decisions.md`.

Ce principe ne couvre pas ce qui touche au réel (compte, licence, import de la production, mise en ligne) : là, l'accord de Ced reste nécessaire.

## C-06 — Décision d'accès

Trois réglages, avec leur valeur par défaut. Chacun a ses tests dans les deux positions.

| Réglage | Valeur par défaut | Autre valeur |
|---|---|---|
| Contenu dont la date de sortie est à venir | **Fermé pour tous**, équipe et robots compris. La prévisualisation par la rédaction passe par le mécanisme de WordPress, hors de cette décision | Ouvert à l'équipe |
| PDF d'un numéro pour un robot d'indexation vérifié | **Extrait** (pas de PDF complet) | Complet |
| PDF d'un numéro paru avant le début de l'abonnement, pour un abonné en cours | **Fermé** | Ouvert |

Le motif provisoire `PdfAnterieurAArbitrer` est remplacé par un motif définitif qui nomme le réglage. Les autres réserves du brief (longueur de l'extrait, forme de l'accès découverte, affichage en délai de grâce) sont déjà des réglages ou relèvent du branchement.

## C-05 — Paiement en quatre fois

**Option A retenue : quatre échéances par bloc de quatre numéros**, une par numéro. Une fenêtre de date à date peut donc contenir cinq dates de paiement quand la commande tombe entre la date commune et la clôture : c'est accepté.

Cette décision corrige la formulation de l'arbitrage du 21/11 (« par année d'engagement de date à date »), qui était une erreur de rédaction de Claude : le cahier des charges compte le papier en numéros (§3.5) et prévoit une échéance par numéro (§3.4). Les dates communes et la marge avant clôture sont conservées sans exception.

Les trois autres questions de la proposition deviennent des réglages :

| Réglage | Valeur par défaut |
|---|---|
| Marge avant clôture, en jours civils | Aucune valeur par défaut : le réglage est obligatoire, et le moteur refuse de planifier tant qu'il n'est pas renseigné |
| Après un rejet en cours d'année | Les échéances restantes restent dues (§3.4 : les quatre échéances sont dues) ; l'accès suit le réglage du délai de grâce |
| Changement de tarif en cours d'année | Montants figés pour les quatre échéances du bloc en cours |

## C-07 — Liste d'envoi

Le format attendu par le routeur (ordre et colonnes) devient un réglage d'export. Colonnes provisoires d'ici la réponse d'Imagine.
