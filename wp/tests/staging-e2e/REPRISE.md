# Reprise A-01 — exécution synthétique et limites

**20 novembre 2026. Référence courante ; remplace les indications historiques incompatibles du README. Acceptance synthétique stabilisée validée (`f36c72f4d187`) ; pas de qualification de l'import réel, aucun `PRET`.**

## Commandes

Depuis la racine du checkout, Python et Docker déjà disponibles :

```sh
python wp/tests/staging-e2e/test_harness.py
python wp/tests/staging-e2e/harness.py fixture-selftest
python wp/tests/staging-e2e/harness.py acceptance
python wp/tests/staging-e2e/harness.py acceptance --licensed-packages
```

Le Docker existant de WSL `Ubuntu` est utilisé si le CLI Windows manque. Le runtime ne télécharge ni ne tire d'image. `prepare` est une phase distincte, publique uniquement, **avant tout site/import** ; elle a déjà été réalisée pour les reçus livrés. Ne pas la relancer pendant une consigne sans téléchargement. Aucune installation hôte.

`fixture-selftest` teste les fixtures/oracles, **pas** les scripts de staging. `acceptance` exige la vraie chaîne, sa fidélité après nettoyage, ses refus de pièges et ses invariants dans les deux stockages. Sorties : `0` = contrôles du mode terminés ; `2` = échec/prérequis indisponible. Une dépendance échouée laisse les étapes suivantes `NOT_TESTED`.

## Paquets payants autorisés — pas de remplacement automatique

`--licensed-packages` accepte uniquement les deux fichiers désignés par Ced :

- `/home/ced/staging-wp/plugins/woocommerce-subscriptions.zip`
- `/home/ced/staging-wp/plugins/woocommerce-memberships.zip`

Copie directe dans le conteneur neuf **après inspection de son isolation**, vérification SHA-256 avant extraction bornée, destruction avec le conteneur. Aucun ZIP/code payant dans le dépôt ou l'image publique. Aucune activation de licence, recherche d'autre paquet ou téléchargement. Une empreinte différente bloque le chemin.

Résultat effectif : **Subscriptions 9.4.1** exige **WordPress 7.0** et **WooCommerce 11.1**, au-delà du runtime préparé **6.9 / 10.4.3**. L'activation est refusée en classique et HPOS. **Memberships 1.30.3** s'active ; ses droits d'accès ne sont pas qualifiés. La présence/version d'un ZIP ne vaut jamais réussite d'acceptance. La branche `licensed-fixture.php`, qui doit créer six abonnements par API sur un runtime compatible, n'a **pas été atteinte**. Preuves : `results/reprise-licensed-inputs.json` et `results/reprise-licensed-acceptance.json`.

## Dépendances publiques effectivement préparées

Versions épinglées, pas présentées comme les dernières : WordPress **6.9**, WooCommerce **10.4.3**, WP-CLI **2.12.0**, Contact Form 7 **6.1.4**, Yoast SEO **26.5**, Meta Box **5.10.7**. URLs, tailles et SHA-256 dans `public-dependencies.json`. Image utilisée :

```text
sha256:b2ffa6ad01ffacc6d31b176232c8d0779c0320daba381e05cbbd80f56d5327a0
```

Le build ne crée/importera aucun site en base. `.dockerignore` exclut le reste du dépôt du contexte. Inventaire Linux : `results/reprise-public-packages.tsv`. Une reconstruction Debian n'est pas annoncée reproductible bit-à-bit.

## Fidélité et pièges : preuve après nettoyage désormais exécutée

Chaque stockage contient 30 comptes et 30 commandes inventés, les trois extensions gratuites actives, un formulaire CF7 réel, des options Yoast réelles, un article, et des champs simples/clonés Meta Box configurés par un MU-plugin synthétique.

`fidelity.php` exige un nouveau bootstrap WordPress, le rendu réel du formulaire, les lectures des champs, l'état actif des extensions et les empreintes exactes des réglages, article et MU-plugin. **Avant et après traitement : PASS classique et HPOS**, reçu `evidence/f36c72f4d187/result.json` (sortie 0 ; 131 PASS, 2 NOT_TESTED). Les montants/statuts/dates/articles/quantités/pays/moyens de paiement restent identiques ; les 60 lignes d'adresses HPOS gardent leurs discriminateurs billing/shipping.

Reprise depuis `6cb3c90a73b0`, sources sujets identiques au départ. Le refus classique vient de `wp_yoast_primary_term.taxonomy` (motif conservateur `nom`, table vide comprise). Le banc prouve d'abord le refus sans décision, puis applique **uniquement dans son contexte fictif** une décision nommée `garder`. Aucun défaut de production ni arbitrage de Ced n'est ajouté. Le refus HPOS 78 est isolé comme `SQLSTATE 23000 / 1062` : `address_type`, clé structurelle unique billing/shipping, était vidé comme une adresse personnelle. La correction garde cette seule colonne de cette seule table, sans dispenser les valeurs du nettoyage des motifs dangereux ni retirer de contrôle au vérificateur.

Après le cas propre : clés connues imbriquées, identifiants Stripe/PayPal, emails compte/commande/**note de commande** refusés avec le tag attendu ; retrait du verrou mail détecté et espion mémoire sensible ; table inconnue non personnelle conservée ; table personnelle refusée sans décision ; décisions synthétiques `garder`, `vider`, `anonymiser` prouvées sur email externe et téléphone inventés, sans perte du champ de présentation. Un email dans un commentaire **sans lien transactionnel** est un avertissement, pas un sixième motif bloquant. Le vieux test qui attendait un avertissement pour une note rattachée à une commande était erroné ; le vérificateur n'a pas été affaibli pour le satisfaire.

Oracles rejoués : `evidence/c1186257ca0c/result.json`, 75 PASS et 2 NOT_TESTED. Contrats data/MU/CLI : `evidence/2ea8c8781c6c/data-result.json`, 9 cas, 337 assertions ; sa régression billing/shipping échoue contre l'ancien `lib.php` conservé. Le contrat PDO emploie le chargement normal de PHP : sous Linux, `-n` supprimait son module PDO partagé. Diagnostics et erreur pré-correction conservés, sans SQL/valeurs bruts.

Les reçus historiques restent immuables. Chaque nouveau reçu indique les sources **exactement copiées** ; les empreintes du reçu stabilisé ont été rapprochées des fichiers courants. Détails et limites : `../../../production/A-01/notes.md`.

## Garde-fous et reçus

Conteneur neuf nommé/étiqueté, réseau `none`, aucun port/montage/volume, capacités retirées, `no-new-privileges`, aucune écoute TCP/IPv6 et MariaDB sur socket Unix. Dumps/réimports uniquement générés dans ce même conteneur. Aucun argument d'archive/SQL externe. Aucun vrai site, secret, volume partagé, service marchand, SMTP, Novamira, déploiement ou Git.

Copie d'une liste explicite de sources avec contrôle de dérive du lot entier. Les diagnostics PDO n'exposent que codes, classe, fichier/ligne de code et noms du schéma ; jamais message SQL brut ni valeurs. Mot de passe éphémère sur stdin. Oracles WordPress et PDO indépendants ; espion PHPMailer mémoire sans transmission, démontré sensible sur un site non bloqué.

Suppression ciblée en `finally`, puis relecture de l'absence du conteneur exact. Une création échouée n'autorise pas la suppression d'un homonyme. Aucun `prune`.

Reçus courants : `results/reprise-*`. Les nouveaux passages vont dans `evidence/<run_id>/` sans écraser les reçus livrés. Les anciens fichiers sans préfixe restent historiques. `REPORT.md` donne les résultats ; la commande opérateur réservée et les limites d'intégration sont dans `../../outils/staging-wp-integration/OPERATEUR-A01.md`.
