# C-25 — Demande de rétractation seule

> **État courant — 27 novembre 2026, corrections de la fusion de 00 h 02 :** les quatre instructions sont appliquées. Dossier actuel : `CORRECTIONS-002-V2.md`, sceau `livraison-corrections002-V2.json`. Canonique : **10 tests / 172 assertions** ; global : **1151 / 36062**, **20 outils / 521 contrôles** ; live : **57 contrôles**, rollback réel des deux réglages par `options.php`, motif à antislash jusqu’à l’export natif C21, readbacks métier verts ; **15/15 mutations** détectées. Le README est complété, y compris `delete_user`/`wp_die` en panne SQL persistante. C10/C21 clos et markup C10 inchangés. Validation visuelle/juridique et arbitrages métier restent dus. Les sections ci-dessous décrivent **l’historique de la livraison précédente**, dont les reçus ne sont pas écrasés.


## Standard d’abord — dix lignes, documentation officielle consultée le 26 novembre 2026

1. WooCommerce conserve les événements et remarques dans les notes de commande natives.
2. Une note **privée** est interne ; elle ne produit pas la notification d’une note destinée au client.
3. Une note client est envoyée par email : cette variante est exclue de C-25.
4. Les remboursements WooCommerce sont des opérations distinctes, automatiques ou manuelles.
5. Même un remboursement « manuel » inscrit un remboursement : il n’est pas un simple dépôt de demande.
6. Changer l’état d’une commande n’est donc pas notre mécanisme de rétractation.
7. Subscriptions expose les abonnements et leurs commandes dans Mon compte.
8. Ses actions client documentées incluent annulation, suspension, reprise, renouvellement et changement de paiement.
9. Les pages consultées ne décrivent pas notre combinaison « deux étapes, demande seule, aucun effet » ; aucune preuve d’absence universelle de fonction Woo n’est revendiquée.
10. Le stockage standard suffit : **note Woo privée**, métadonnée privée et journal C-10 ; aucun nouveau CPT, aucun moteur de remboursement ou d’annulation.

Sources officielles lues :
- WooCommerce, *Single order page — Order notes* : https://woocommerce.com/document/managing-orders/view-edit-or-add-an-order/
- WooCommerce, *Refunding Orders in WooCommerce* : https://woocommerce.com/document/woocommerce-refunds/
- WooCommerce Subscriptions, *Subscriber’s View* : https://woocommerce.com/document/subscriptions/customers-view/

La démonstration interrogée utilise WooCommerce **11.2.2** et MariaDB **11.8.8**. Les trois tables de la transaction (`comments`, `commentmeta`, `options`) sont InnoDB. Cela ne qualifie pas un autre site. Les dates et obligations légales citées dans le brief n’ont pas été validées juridiquement ici.

## Choix et périmètre

- Règle pure : jours configurables 1–365 ; défaut 14 ; origine paiement ou date manuelle UTC. La borne finale est incluse ; futur et date absente restent fermés.
- Étape 1 sans brouillon ni écriture ; étape 2 avec nonce lié à la cible et au motif, et bouton de confirmation explicite. Motif facultatif, échappé au rendu.
- Titulaire contrôlé avant lecture/écriture et de nouveau sous verrou. Pour une souscription, contrôle du titulaire de la souscription **et** de sa commande initiale ; aucun rapprochement offert/groupé.
- Verrou MySQL par commande, relecture sous verrou, transaction note+métadonnée+événement C-10. La clé unique du journal empêche aussi le doublon. Un échec d’écriture du journal annule la note ; cela est injecté et vérifié sur le vrai adaptateur.
- Aucun appel à `payment_complete`, création de remboursement, modification de statut, renouvellement, adhésion ou accès. La demande ne sauvegarde pas la commande. Le champ manuel d’administration sauvegarde uniquement sa métadonnée native.
- Confidentialité additive : export de la note et du motif, pages de 50 ; une lecture SQL en panne renvoie `WP_Error`, jamais une page vide. Effacement par lots sans décalage d’offset après suppression ; erreurs déclarées incomplètes ; tiers préservés. Le journal conserve date/référence anti-doublon après retrait du motif, de l’auteur et de l’identifiant de note. C’est une trace métier **pseudonymisée**, pas une anonymisation irréversible, et aucune politique de conservation native n’est changée.
- C-06, C-10, C-21 et C-23 ne sont pas modifiés ; seul un bloc additif du bootstrap partagé charge les nouvelles classes. La matrice de sorties relève de C-26.

## Commandes rejouables

Depuis la racine `C:/Users/Ced/imagine` ; chaque nom de reçu est neuf, jamais écrasé :

```text
python wp/outils/demo/c25.py local canonique-<nom-neuf>
python wp/outils/demo/c25-mutations.py mutations-<nom-neuf>
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
python wp/outils/demo/c25-recette.py recette-<nom-neuf>
python wp/outils/demo/c25-finaliser.py verifier
```

La recette native est **mutante puis restauratrice** et réservée au seul site fictif gardé. Elle demande les profils de démonstration existants et l’état initial sans demande C-25. Elle n’est pas une commande d’audit sur le réel. Les tests canoniques et mutations ne chargent ni WordPress ni réseau : ils utilisent des bouchons seulement pour les API WordPress/Woo et exécutent les vraies classes. Ils entrent aussi dans la découverte T-01 sans modifier le runner clos.

## Preuves livrées

- TDD réel : reçus `tdd-01-red`/`green` (règle manquante), `tdd-02-red`/`green` (adaptateur manquant), `tdd-03-red` (deux étapes manquantes), `tdd-04-red` puis `tdd-04-green-reprise` (confidentialité/réglages ; reprise après une erreur SQL précédente). Les rouges restent rouges.
- Livraison : `canonique-livraison-V2.json` et son JUnit : **8 tests, 146 assertions**. `mutations-livraison-V2.json` : **11 mutations de sources jetables** détectées (délai, propriétaire, confirmation, rejeu, export, tiers, effacement, nonce, email, HTTP, statut financier).
- `image-livraison-V2.json` : préparation officielle postérieure aux nouveaux tests. `regression-livraison-V2.json` : suite globale réelle, compteurs dans son reçu et JUnit, aucun échec/erreur/ignoré.
- `recette-livraison-V2.json` : parcours HTTP, abandon sans note, nonce de l’étape 1 refusé à l’étape 2, deux POST concurrents/deux accusés/une seule note, GET ultérieur, refus signé hors délai, autre titulaire, administration, deux réglages C-10 ; puis parcours abonnement, panne réelle du journal et de lecture SQL, reprise d’export, effacement et conservation des tiers.
- Les décisions d’accès sont relues sur de vrais numéros avec témoin ouvert avant comparaison. Commandes, abonnements, adhésions, rôles et actions métier restent identiques après la demande ; aucune finance n’est déclenchée. Les lectures de compte créent un cache WCS et une note incrémente le compteur natif de commentaires : ces deux écarts mesurés sont traités comme cache/trace **pendant** la demande, puis restaurés et comparés intégralement au nettoyage.
- Les compteurs d’appels C-25 restent vides. L’administration WordPress tente aussi des vérifications de maintenance **hors C-25**, bloquées par le coupe-circuit B-00 : elles sont distinguées dans `observer_counts`, pas niées. Aucun mail ni appel extérieur réel n’a été laissé passer.
- Préimages durables privées dans le scratch Hermes, avant sessions et mutations ; seuls leurs chemins opaques et SHA-256 figurent dans les reçus. Restauration relue des lignes brutes utilisateurs, métadonnées, commandes classiques/HPOS, notes, options métier et empreintes des actions. Sessions restaurées. Observateur MU et script de recette distant supprimés. Aucun nouveau profil ni fixture conservé.

## Écarts rencontrés, corrigés et non cachés

1. Premier essai HTTP : mauvaise hypothèse `/mon-compte/`, 404. Le parcours résout maintenant `wc_get_page_permalink('myaccount')` (`/my-account/`). Restauration initiale déjà verte.
2. Le premier essai de date manuelle sauvegardait en HPOS, mais l’inverse ne traitait que `postmeta` : les dates natives de modification avaient aussi bougé. Les reçus rouges sont conservés. La récupération a retrouvé les dates **par égalité avec les SHA-256 métier d’avant mutation**, sans choisir une nouvelle date, puis a confirmé l’égalité complète (`recovery-metier-V2.json`). La recette photographie désormais toutes les tables HPOS avant mutation et restaure les lignes exactes.
3. Les premiers contrôles « zéro HTTP » additionnaient la maintenance WordPress et C-25. L’observateur distingue leur pile d’appel ; les mutations hors ligne prouvent qu’un email ou HTTP ajouté à C-25 fait échouer le test. Les caches WCS ont été identifiés, pas requalifiés en droits métier.
4. Les scripts d’investigation ponctuels sont archivés dans `historique/`, hors des commandes normales : **ne pas les rejouer**. Les reçus intermédiaires n’ont pas été rebaptisés en preuves vertes.

`A-VOIR.md` contient les trois questions fermées demandées à Imagine et les adresses. `PRET` ne sera posé qu’après le scellement des sources courantes, des reçus finaux et des contrôles de restauration. La validation visuelle et le droit applicable restent hors de ce verdict technique.
