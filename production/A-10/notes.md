# A-10 — livré pour relecture

Paquet courant : `preuves/eaeb5368fbca`. Vérificateur parent réellement exécuté avec `--replay` : code 0, **6 assertions unitaires + 97 natives + 7 de runner = 110**, aucune échouée. Ce sont des assertions nommées, pas des tests PHPUnit. Les paquets précédents restent historiques.

## Livré et prouvé

- Commande ciblée `wp/outils/bascule/inventorier-codes`, module autonome `a10/`, tests et vérificateur `wp/tests/a10/`. Aucun branchement aux transformations de bascule.
- Dix coupons fictifs couvrant les sept types Woo/Subscriptions, leurs restrictions produits/catégories/email (emails uniquement comptés), limites, dates et usages. Expirés/jamais utilisés à part, avec recoupement autorisé.
- Magasins classique et HPOS : oracle des getters **réels** Woo, vrai renouvellement Subscriptions conservant le coupon récurrent, quatre états porteurs décomptés séparément. Compte exact : un porteur dans chacun des états active/on-hold/pending/pending-cancel ; cinq commandes récentes distinctes pour le récurrent malgré les lignes dupliquées et la casse différente. Anciennes, futures, corbeille et abonnements terminés exclus conformément au contrat déclaré.
- Empreintes logiques **des 55 tables** identiques avant/après dans chacun des deux magasins, cron et Action Scheduler compris ; fichiers du site identiques ; piège de bootstrap intact. Identifiants client, noms et emails absents des deux sorties. Compte SELECT pour l'auditeur ; tentative UPDATE root également bloquée par sa transaction READ ONLY.
- Garde audit obligatoire, empreinte du rapport A-02, refus des sorties dans le site, dans le dépôt (disposition canonique réellement éprouvée), via lien vers la racine web, existantes, sans audit, avec audit invalide/mauvais magasin, configuration dynamique ou argument inconnu. Mode 0700/0600 prouvé dans le conteneur.
- Banc A-02 réutilisé sans modification : image figée, WordPress 7.0.9 / WooCommerce 11.1.1 / Subscriptions 9.4.1. Sources natives tracées par SHA-256, sans embarquer les extensions commerciales.
- Réseau absent, aucun port/montage/privilège ; ownership A-10 distinct. Chaque conteneur créé a été supprimé par son nom/label exact puis son absence relue. Le verrou voie 1 reste au parent, inchangé.

## Préservation, RED et préparation

`a02-baseline.json` couvre l'inventaire et les bytes A-02. Seul ajout autorisé : les **deux lignes exactes** de `readme-ajout.txt` en fin de `wp/tests/a02-audit/README.md` ; leur retrait reconstruit le SHA-256 original. Aucun autre outil accepté modifié, aucun Git, staging, demo, archive ou site réel accédé.

RED unité : `0d1b57191584` (module absent). RED natif : `e73f6d49a5e2` (fixture/renouvellement réels prêts, commande absente dans les deux magasins). Les essais intermédiaires ont notamment révélé la méta native nullable de limite d'articles, puis le défaut natif zéro des seuils vides ; les corrections ont été rejouées. GREEN final après le dernier changement de source : `eaeb5368fbca`.

`wp/tests/preparer-image.ps1` a réellement tourné, code **0** : reçu et journal bruts dans `preparation/`. Le journal garde l'avertissement préexistant « T01 sans tests : themes/imagine » et les marqueurs de transport PowerShell ; la vérification d'image termine bien avec succès. Aucun fichier de cette voie 2 n'a été modifié. Aucune prétention de rejeu global T-01 : l'acceptance A-10 est la fixture native autonome ci-dessus.

## Défauts techniques et limites

Douze mois **calendaires UTC**, bornes incluses ; commandes de tous statuts sauf corbeille/auto-draft, donc pas des ventes nettes. `pending-cancel` est conservé à part pour ne pas perdre ces porteurs. La limite Subscriptions inclut le paiement initial éligible ; pas un solde de renouvellements par client. Récurrence = réglage standard, pas promesse de remise future. Pas de reclassement ni de suppression.

Le garde audit est structurel avec liaison SHA-256, pas une identité cryptographique de site : l'opérateur doit choisir sa photographie récente. Site simple, config littérale, tables InnoDB, stockage standard ; extensions tierces/filtres/marques d'autres versions et historique réel non qualifiés. L'audit réel reste interdit sans GO et ses rapports restent hors dépôt. Aucune question métier tranchée, aucun GO implicite.

Relecture : `python wp/tests/a10/verifier.py` ; nouveau passage natif indépendant : ajouter `--replay`. `manifest.json` scelle les sources, références et preuves courantes ; les essais historiques ne sont pas requalifiés.
