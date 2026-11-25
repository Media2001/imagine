# A-10 — livré pour relecture

Paquet courant : `preuves/5e795d00f9d6`, produit après les derniers changements des sources. `python wp/tests/a10/verifier.py --replay` : **code 0, 10 assertions unitaires + 187 natives + 7 runner = 204 PASS**, zéro échec. Commande et sortie réelle : `rejeu-corrections.json`. Assertions nommées, pas un décompte PHPUnit. Les paquets précédents restent historiques ; ancien état : `notes-avant-corrections.md` et `manifest-avant-corrections.json`.

## Sept instructions de correction

1. Union des fiches et des noms distincts de lignes coupon portées par les abonnements retenus ou les commandes de la fenêtre. Sans fiche : `record_status = fiche introuvable`, comptes conservés et tous les réglages inconnus à `null`. Noms historiques regroupés sans casse et projetés en minuscules ; une fiche existante garde son nom enregistré.
2. Suppression et renommage effectués par les véritables API Woo sur des coupons encore portés par un abonnement actif, dans chaque magasin ; cas supplémentaire sans fiche sur commande seule. Doublons non multipliés, aucun identifiant personnel projeté.
3. Dates de l'oracle converties explicitement en UTC sur des clones, sans mutation des objets métier. Bruxelles hiver/été, expirations legacy, offsets +5.75, −3.5 et zéro ; refus `A10_TIMEZONE_INVALID` sur 15 et 0.1.
4. Horloge MariaDB des connexions SELECT du banc fixée au 25 novembre 2026 à 12:00:00 UTC, sans paramètre ni contournement dans le sujet. Six commandes : égalité et ±1 seconde à chaque borne ; trois expirations : égalité et ±1 seconde à l'instant observé. 29 février conservé.
5. Refus réels `A10_DUPLICATE_COUPON_META` et `A10_META_INVALID`, aucune sortie après refus et empreintes identiques ; formats structurés invalides aussi en unité.
6. Montant enregistré vide conservé à `null` (inconnu), testé et documenté ; seuils vides toujours zéro sans restriction. Projection volontaire du stockage vide, pas prétention d'égalité au défaut normalisé d'un getter Woo.
7. Rejeu natif frais par le vérificateur parent, classique et HPOS : anciens contrôles conservés, suite étendue de 110 à 204 assertions.

Les variantes sont préparées après la preuve principale et disposent chacune de photographies intégrales propres avant/après le sujet. Leurs mutations intentionnelles de préparation ne sont pas des écritures de l'inventaire. RED orphelin : `986b88d210ed` ; RED oracle Bruxelles : `514fff446e2a`, échecs attendus dans les deux magasins avant correction.

## Livré et prouvé

- Commande ciblée `wp/outils/bascule/inventorier-codes`, module autonome `a10/`, tests et vérificateur `wp/tests/a10/`. Aucun branchement aux transformations de bascule.
- Vingt-sept noms de codes fictifs par magasin : vingt-quatre fiches et trois noms historiques sans fiche, couvrant les sept types Woo/Subscriptions, restrictions, limites, saisons, bornes, expirés/jamais utilisés à part. Emails uniquement comptés.
- Magasins classique et HPOS : oracle des getters **réels** Woo, vrai renouvellement Subscriptions conservant le coupon récurrent, quatre états porteurs décomptés séparément. Compte exact : un porteur dans chacun des états active/on-hold/pending/pending-cancel ; cinq commandes récentes distinctes pour le récurrent malgré les lignes dupliquées et la casse différente. Anciennes, futures, corbeille et abonnements terminés exclus conformément au contrat déclaré.
- Empreintes logiques **des 55 tables** identiques avant/après dans chacun des deux magasins, cron et Action Scheduler compris ; fichiers du site identiques ; piège de bootstrap intact. Identifiants client, noms et emails absents des deux sorties. Compte SELECT pour l'auditeur ; tentative UPDATE root également bloquée par sa transaction READ ONLY.
- Garde audit obligatoire, empreinte du rapport A-02, refus des sorties dans le site, dans le dépôt (disposition canonique réellement éprouvée), via lien vers la racine web, existantes, sans audit, avec audit invalide/mauvais magasin, configuration dynamique ou argument inconnu. Mode 0700/0600 prouvé dans le conteneur.
- Banc A-02 réutilisé sans modification : image figée, WordPress 7.0.9 / WooCommerce 11.1.1 / Subscriptions 9.4.1. Sources natives tracées par SHA-256, sans embarquer les extensions commerciales.
- Réseau absent, aucun port/montage/privilège ; ownership A-10 distinct. Chaque conteneur créé a été supprimé par son nom/label exact puis son absence relue. Le verrou voie 1 reste au parent, inchangé.

## Préservation, RED et préparation

`a02-baseline.json` couvre l'inventaire et les bytes A-02. Seul ajout autorisé : les **deux lignes exactes** de `readme-ajout.txt` en fin de `wp/tests/a02-audit/README.md` ; leur retrait reconstruit le SHA-256 original. Aucun autre outil accepté modifié, aucun Git, staging, demo, archive ou site réel accédé.

Les premiers RED historiques (module puis commande absents) sont conservés ; les deux RED propres à cette correction figurent ci-dessus. GREEN final après le dernier changement de source : `5e795d00f9d6`.

La préparation initiale `wp/tests/preparer-image.ps1` avait réellement terminé code **0** : reçu et journal bruts dans `preparation/`, toujours vérifiés avec le SHA-256 courant du script. Cette correction étend le paquet A10 existant sans nouvelle dépendance : **aucune reconstruction de l'image partagée**, ni nouvelle préparation présentée comme fraîche. Le journal initial conserve l'avertissement préexistant « T01 sans tests : themes/imagine » ; aucun fichier de cette voie 2 modifié. Aucune prétention de rejeu global T01 : l'acceptance est la fixture native autonome.

## Défauts techniques et limites

Douze mois **calendaires UTC**, bornes incluses ; commandes de tous statuts sauf corbeille/auto-draft, donc pas des ventes nettes. `pending-cancel` est conservé à part pour ne pas perdre ces porteurs. La limite Subscriptions inclut le paiement initial éligible ; pas un solde de renouvellements par client. Récurrence = réglage standard, pas promesse de remise future. Pas de reclassement ni de suppression.

Le garde audit est structurel avec liaison SHA-256, pas une identité cryptographique de site : l'opérateur doit choisir sa photographie récente. Site simple, config littérale, tables InnoDB, stockage standard ; extensions tierces/filtres/marques d'autres versions et historique réel non qualifiés. L'audit réel reste interdit sans GO et ses rapports restent hors dépôt. Aucune question métier tranchée, aucun GO implicite.

Relecture : `python wp/tests/a10/verifier.py` ; nouveau passage natif indépendant : ajouter `--replay`. `manifest.json` scelle les sources, références et preuves courantes ; les essais historiques ne sont pas requalifiés.
