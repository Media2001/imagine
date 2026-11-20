# Reprise A-01 — exécution synthétique et limites

**20 novembre 2026. Référence courante ; remplace les indications historiques incompatibles du README. Acceptance non validée ; aucun `PRET`.**

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

## Fidélité : référence exécutée, preuve post-nettoyage bloquée

Chaque stockage contient 30 comptes et 30 commandes inventées, les trois extensions gratuites actives, un formulaire CF7 réel, des options Yoast réelles, un article, et des champs simples/clonés Meta Box configurés par un MU-plugin synthétique.

`fidelity.php` exige un nouveau bootstrap WordPress, le rendu réel du formulaire, les lectures des champs, l'état actif des extensions et les empreintes exactes des réglages, article et MU-plugin. La référence **avant** traitement fonctionne en classique et HPOS. La preuve **après** traitement est implémentée, mais **non atteinte** : dans le reçu livré, `neutraliser` échoue avec `SQLSTATE 23000`, erreur **1062**, sur `wp_options.option_name`.

Après le cas propre, le harness prévoit les clés connues imbriquées, identifiants Stripe/PayPal, emails compte/commande, retrait du verrou mail avec espion mémoire, table inconnue non personnelle conservée, table personnelle refusée sans décision, puis décisions synthétiques `garder`, `vider`, `anonymiser`. Les décisions de fixtures ne sont jamais présentées comme des arbitrages de Ced. Un email de note réintroduit doit être un avertissement, pas un sixième motif bloquant. Aucun refus de résidu n'est crédité avant une vraie vérification positive.

Les sources de données évoluent en parallèle. Chaque reçu indique les sources **exactement copiées** ; les tests doivent être rejoués après stabilisation. Un éventuel écart avec le fichier courant est consigné à l'emballage, pas masqué.

## Garde-fous et reçus

Conteneur neuf nommé/étiqueté, réseau `none`, aucun port/montage/volume, capacités retirées, `no-new-privileges`, aucune écoute TCP/IPv6 et MariaDB sur socket Unix. Dumps/réimports uniquement générés dans ce même conteneur. Aucun argument d'archive/SQL externe. Aucun vrai site, secret, volume partagé, service marchand, SMTP, Novamira, déploiement ou Git.

Copie d'une liste explicite de sources avec contrôle de dérive du lot entier. Les diagnostics PDO n'exposent que codes, classe, fichier/ligne de code et noms du schéma ; jamais message SQL brut ni valeurs. Mot de passe éphémère sur stdin. Oracles WordPress et PDO indépendants ; espion PHPMailer mémoire sans transmission, démontré sensible sur un site non bloqué.

Suppression ciblée en `finally`, puis relecture de l'absence du conteneur exact. Une création échouée n'autorise pas la suppression d'un homonyme. Aucun `prune`.

Reçus courants : `results/reprise-*`. Les nouveaux passages vont dans `evidence/<run_id>/` sans écraser les reçus livrés. Les anciens fichiers sans préfixe restent historiques. `REPORT.md` donne les résultats ; la commande opérateur réservée et les limites d'intégration sont dans `../../outils/staging-wp-integration/OPERATEUR-A01.md`.
