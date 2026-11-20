# Opérateur A-01 — commande réservée, pas de GO d'import réel

**20 novembre 2026. La reprise n'est pas `PRET`. Ne pas exécuter cette commande contre une sauvegarde réelle avec le worker prototype actuel.**

Les tests du lot utilisent des sites inventés. Aucun agent ne doit ouvrir la sauvegarde originale, se connecter à l'ancien staging ou appliquer ce patch au service partagé. Seul Ced lancera un éventuel import réel, après levée explicite des blocages ci-dessous.

## Blocages avant utilisation réelle

1. L'acceptance des scripts de données échoue encore dans le snapshot livré, en classique et HPOS : `neutraliser` renvoie 78, `SQLSTATE 23000 / 1062`, sur `wp_options.option_name`. Rejouer la chaîne après les corrections du pair ; la référence gratuite **avant** nettoyage ne prouve pas la fidélité **après**.
2. Les ZIP autorisés sont présents, mais Subscriptions **9.4.1** exige WordPress **7.0** et WooCommerce **11.1**. Le runtime synthétique préparé est **6.9 / 10.4.3** : activation réellement refusée. Memberships **1.30.3** s'active, sans qualification des droits. Obtenir une consigne sur des dépendances compatibles ; ne pas contourner les headers ni télécharger d'alternative pendant le parcours.
3. **L'importeur prototype n'est pas fidèle au brief repris.** Il lit le SQL mais élimine les autres fichiers de l'archive et reconstruit du code approuvé. Il ne conserve donc pas l'ensemble extensions/thème/MU/médias de la copie. Ce chemin n'a pas été exercé ni adopté pour une sauvegarde réelle.
4. Le remplacement/activation Novamira neuf reste non implémenté ; le worker refuse cette étape. Aucune image worker d'import complet, pile FPM/nginx ou API/MCP réelle n'a été qualifiée dans cette reprise.
5. Le transport WordPress post-vérification reste `network_mode: none`. Une éventuelle liste d'hôtes applicative n'y rend pas les mises à jour joignables. La sortie limitée aux hôtes de mise à jour du brief reste à qualifier séparément, sans ouvrir le réseau avant vérification.

Les reçus et leurs limites sont dans `../../tests/staging-e2e/REPORT.md` et `../../tests/staging-e2e/results/reprise-*`. `test-results.json` dans ce dossier décrit l'ancienne recette, pas une nouvelle exécution du service partagé.

## Commande unique — après qualification et adoption explicites

Les variables sont fournies par Ced : instance, chemins vus par l'opérateur **et** le daemon Docker, copie fraîche, URL de production distincte, port réservé, trois images locales approuvées par ID immuable. Elles ne sont pas devinées. Le worker actuel exige un nom de staging `localhost`, `.test`, `.localhost` ou `.invalid` ; ne pas utiliser une IP ou changer ce garde pour contourner un refus.

```sh
cd "$OUTIL_ADOPTE"
python3 -m api.subscription_operator \
  --name "$NOUVELLE_COPIE" \
  --archive "$ARCHIVE_APPROUVEE" \
  --workflow "$DEPOT_SCRIPTS_APPROUVE" \
  --production-url "$URL_PRODUCTION" \
  --port "$PORT_STAGING" \
  --worker-image "$IMAGE_WORKER_SHA256" \
  --db-image "$IMAGE_MARIADB_SHA256" \
  --nginx-image "$IMAGE_NGINX_SHA256" \
  --table-decisions "$DECISIONS_CED_JSON"
```

Omettre `--table-decisions` si aucun arbitrage n'est fourni. Le mot de passe du compte `imagine-test-admin` est demandé dans le terminal privé ; 20 à 72 octets, jamais dans argv, un fichier du dépôt ou un journal. `--password-fd N` permet une entrée privée explicitement maîtrisée. Aucun identifiant MCP importé n'est réutilisé.

Sans `--start`, aucune publication web. L'ajout explicite de `--start` n'autorise le démarrage qu'après la chaîne complète réussie ; il ne contourne aucun blocage. Pour cette reprise, **ne pas l'ajouter**. Aucun pull/build/téléchargement/activation de licence pendant l'import.

## Ce que l'opérateur doit voir

- Code de sortie `0` seulement après la chaîne complète ; `1` si refus/échec, sans repli vers l'ancien importeur.
- Objet JSON avec `slug`, `status`, `verification_state`, `verification_report`.
- Statuts distincts : `quarantined` avant réussite de l'import, `imported` après restauration mais avant validation, `verified` après toute la chaîne. Changer le statut runtime ne vaut pas vérification.
- Rapport filtré : étape, `ok`, booléens requis, tags d'erreurs/avertissements, extensions désactivées, types inconnus, tables inconnues avec **nom, colonnes, nombre de lignes, colonnes personnelles et décision**. Aucune valeur de ligne ni message PDO brut.
- En cas d'échec après création, le CLI restitue le rapport de **sa propre copie exacte**, sans mot de passe ; les rapports privés restent hors dépôt, et aucune URL web/agent n'est rendue utilisable.

Le transport refuse un rapport dépassant 16 Kio ; il ne déclare pas une vérification complète avec une liste de tables tronquée. Un rapport trop gros est un blocage à diagnostiquer, pas un succès partiel.

## Décisions de tables — Ced uniquement

Exemple de **format**, entièrement synthétique, jamais une autorisation sur une table réelle :

```json
{
  "wp_table_synthetique_a": {"action": "garder"},
  "wp_table_synthetique_b": {"action": "vider"},
  "wp_table_synthetique_c": {"action": "anonymiser", "columns": ["email", "phone"]}
}
```

Fichier JSON limité à 4096 caractères sérialisés, uniquement noms de tables/colonnes et actions `garder`, `vider`, `anonymiser`. Aucune donnée personnelle ou valeur secrète. Le worker valide les identifiants, et le moteur natif vérifie les coordonnées effectives du schéma. La décision fait partie de la signature du parcours ; pas de remplacement silencieux entre étapes.

Une table inconnue sans colonne personnelle est conservée et rapportée. Une table à colonne personnelle sans décision bloque `verified`. `garder` n'exempte pas les cinq contrôles bloquants : emails compte/commande/abonnement hors `example.org`, motifs connus de clés, identifiants Stripe/PayPal, blocage mail exécuté, mode staging si Subscriptions est présent.

Après lecture du rapport et arbitrage, une relance utilise un **nouveau nom et une copie fraîche** ; ne pas réimporter en place un site déjà exposé. Pas de suppression globale de ressources pour débloquer.

## Vérifications possibles sans service partagé

```sh
python wp/tests/staging-e2e/test_harness.py
python wp/outils/staging-wp-integration/test_compatibility.py
python wp/outils/staging-wp-integration/worker/test_worker.py
python wp/tests/staging-e2e/harness.py fixture-selftest
python wp/tests/staging-e2e/harness.py acceptance
python wp/tests/staging-e2e/harness.py acceptance --licensed-packages
```

Les deux suites d'intégration utilisent des doubles explicites de transport/stockage. Elles valident les contrats et le filtrage, pas une restauration réelle. Ne pas lancer la découverte de tests de l'outil partagé : elle pourrait viser des sites existants. Aucun `apply.py --apply`, redémarrage, déploiement ou accès à l'instance partagée n'a été réalisé ici.
