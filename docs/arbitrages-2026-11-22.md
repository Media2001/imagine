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

## A-01 — Import et publication (ajout du 22/11, 17 h)

Réponses de Claude aux quatre questions de la fusion `corrections/A-01.md`. Ce sont des choix techniques, pris selon la règle « qui valide quoi ».

| Question de la fusion | Réponse |
|---|---|
| 1. Statut « vérifié » porté par un fichier témoin à la racine du site et par le rapport, le tableau de bord restant `running` | **Oui.** Les lots suivants lisent le témoin, pas le tableau de bord. |
| 2. Mises à jour depuis l'administration, ou par scripts seulement | **Par scripts de bascule seulement** (doctrine : tout changement durable est un script rejouable). `DISALLOW_FILE_MODS` reste actif. La sortie vers `*.wordpress.org` et `*.woocommerce.com` est conservée, parce que ces scripts en ont besoin pour télécharger. |
| 3. Cœur épinglé à la version de la production (6.9.1), toute archive d'une autre version étant refusée avec rapport | **Oui**, tant que le chantier de mise à niveau n'a pas tourné. La version attendue est un paramètre de la commande, pas une constante. |
| 4. Un premier essai sur l'archive réelle peut être refusé pour une raison de format, de grammaire SQL, de moteur de table ou de version | **Oui, c'est attendu** : ce premier essai sert de test. Un refus déclenche un lot de qualification court (une demi-journée), sur le motif exact du refus, sans jamais ouvrir l'archive : seul le rapport de la commande, qui ne contient aucune valeur, sert de base. |

Sur l'effet de bord signalé par la relecture : chaque site de test active puis libère une licence Novamira. C'est couvert par l'accord de Ced du 22/11. Limite-toi au nombre de sites nécessaire à la preuve, et indique ce nombre dans ton rapport.

## C-05 — ajout du 22/11, 17 h

La marge de confirmation pour un premier paiement par SEPA (délai avant de considérer le premier numéro comme payé) devient un **réglage**. Valeur par défaut : la marge s'applique.
