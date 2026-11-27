# Relecture indépendante Codex — A-31

Date : 27 novembre 2026. Périmètre : brief A-31, cahier des charges §4.3, décisions applicables, `production/A-31/`, outil et tests A-31 dans `wp/`, dépendances nécessaires à leur compréhension. Doctrine et consignes de `relecteurs/AGENTS.md` appliquées. Le rapport Claude n'a pas été lu. Aucune correction de production effectuée.

## 1. Conformité

Les livrables demandés sont présents : outil de comptage, documentation du standard en huit points, deux lignes dans le mode d'emploi partagé, tests, paquet unique de preuves, vérificateur sans argument, déclaration `rejeu.json` et `PRET`.

Le périmètre correspond au §4.3 : mesurer l'historique conservé et ses liens cassés, sans réparation. Le magasin faisant autorité est choisi entre classique et HPOS ; les copies de synchronisation ne sont pas additionnées. Les états et natures exportés sont fermés. Les remboursements sont séparés des commandes. L'année la plus ancienne n'est pas remplacée par une année plus récente lorsque son groupe est rare.

Les interprétations sont explicites dans le README : année UTC de création, exclusion des commandes à la corbeille, comptage des orphelins par commande, natures simultanées classées « illisible ». La définition d'un abonnement vivant reprend bien `active` d'A-19 (`wp/outils/bascule/a19/Analysis.php:63`).

Réserve : le regroupement des petits effectifs ne protège pas effectivement la rubrique des renouvellements orphelins ; voir **R1**, section 4.

## 2. Exactitude métier

Cas déroulés à la main à partir de la promesse de conservation du §4.3 et des scénarios du brief, puis comparés au code et aux résultats natifs livrés :

1. **Renouvellement orphelin et seuil cinq.** Cinq commandes portent chacune une référence numérique de renouvellement vers un abonnement absent. `Inventory::relations()` conserve leur nature `renewal` et marque chaque commande orpheline une seule fois. `Analysis::analyse()` produit cinq renouvellements orphelins. Le banc à cinq répétitions contient aussi cinq renouvellements valides : résultat attendu et livré, dix commandes `renewal`, dont cinq orphelines. Le calcul est correct. À une répétition, le résultat public révèle toutefois encore l'orphelin unique malgré la suppression de son libellé interne : R1.

2. **Abonnements sans parent et compte supprimé.** Cinq abonnements `active` sans parent, cinq `cancelled` sans parent et cinq commandes portant un identifiant de compte positif absent doivent donner cinq `living_without_parent` et cinq `orders_missing_account`. Les abonnements annulés et les commandes invitées ne doivent rien ajouter. C'est le résultat du code et des rapports `classic-five`/`hpos-five`.

3. **Ancienneté et remboursement.** Une commande de 2019 et cinq de 2020 donnent `oldest_year = fusionne`, sans annoncer 2020 comme première année. Un remboursement de 2021 ne modifie pas l'ancienneté des commandes. Ces comportements sont expressément vérifiés par les tests PHP livrés. Une date illisible rend également l'ancienneté illisible ; le rejeu nominal conserve les mêmes rapports.

La lecture de l'import gelé confirme la conservation des relations WCS numériques, des parents structurels, des comptes référencés et des dates sur le banc fourni. La métadonnée d'extension sensible disparaît effectivement lors de la neutralisation. Le choix prudent `natures = inconnu après neutralisation` évite alors de transformer une relation détruite en commande sans abonnement. Les années, états, liens numériques, remboursements et ancienneté restent exploitables dans les limites documentées et sous K=5. L'import n'a pas été modifié.

## 3. Tests

Commandes exécutées depuis la racine, sans génération de nouveau paquet ni resceau :

```text
C:/Python314/python.exe -B production/A-31/verify.py
C:/Python314/python.exe -B -m unittest discover -s wp/tests/a31 -p "test_*.py" -v
```

- **Vérificateur sans argument : PASS**, sortie `A31_PACKAGE_PASS`, code 0. Exécuté avant et après les suites ; le paquet et ses sources liées restent acceptés.
- **Suite Python UTF-8 : 37 tests, 30 réussis, 7 erreurs d'environnement.** Variables : `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`.
- **Suite Python cp1252 : 37 tests, 30 réussis, 7 erreurs d'environnement.** Variables : `PYTHONIOENCODING=cp1252`, `PYTHONUTF8=0`, `PYTHONDONTWRITEBYTECODE=1`.

Les sept erreurs sont des `PermissionError` dans les répertoires temporaires Windows utilisés par les tests de livraison, de superviseur absent, de mutations et de fichiers de rapport. Elles empêchent d'exécuter leurs assertions ; ce ne sont pas sept défauts métier démontrés. Aucun déplacement de ces écritures vers le dépôt n'a été effectué pour contourner la restriction. Le rejeu local complet n'est donc **pas déclaré vert**.

Le paquet scellé contient, lui, deux suites de 37 tests réussis, les quatre cellules classique/HPOS × UTF-8/cp1252, les contrôles PHP purs et de frontière, les empreintes avant/après et le contrôle PSR-12. Le vérificateur exécuté en contrôle la cohérence avec les sources courantes. La matrice PHP/Docker n'a pas été relancée pendant cette relecture : les preuves natives ont été relues et vérifiées, sans accès à un site ou à une base.

La couverture dépasse le nominal : valeurs opaques, nature contradictoire, seuils 1/4/5, année absente, rejeu, import effectif sur fixture, refus des canaux et altération cohérente JSON/Markdown après exécution. En revanche, l'oracle `wp/tests/a31/expected.py:8` attend précisément le résultat exposant l'orphelin rare. Il valide l'arithmétique sans détecter R1. La correction de R1 doit inclure un test de non-divulgation des effectifs 1 à 4, en plus du cas visible à 5. La frontière du changement d'année avec décalage horaire n'est pas exercée par le banc natif, dont les commandes sont créées en juin.

## 4. Sécurité et données

### R1 — Important — Le compartiment des orphelins annule le regroupement K=5

**Localisation :** `wp/outils/bascule/a31/Analysis.php:59`.

**Problème :** `orphan_renewals` est alimenté par une seule métrique possible, `renewals_missing_subscription`, puis traité isolément par `pool()`. Lorsque son effectif est inférieur à cinq, enlever `metric` ne cache rien : la clé parente identifie toujours exactement la catégorie et `autres` en donne l'effectif. Le groupe rare reste donc identifiable, contrairement au brief et à la règle annoncée de suppression des libellés rares.

**Preuve livrée :** `production/A-31/preuves/final/utf8/native/classic-history/commandes.json:30` contient `"orphan_renewals": {"groups": [], "autres": 1}`. Les résultats HPOS et cp1252 reproduisent ce comportement. On sait ainsi qu'il existe exactement un renouvellement orphelin, sans donnée auxiliaire ni calcul de différence. Dans A-20, le compartiment « autres pays » retire au contraire l'identité du pays rare ; ici, le compartiment conserve l'identité de l'unique métrique.

**Correction proposée :** intégrer les renouvellements orphelins au regroupement commun des anomalies structurelles rares, en supprimant leur sous-total public distinct sous cinq. Vérifier que les autres champs ne permettent pas de reconstituer ce sous-total. Adapter ensemble le schéma fermé, les deux rendus et les oracles ; tester 0, 1, 4 et 5 orphelins, seuls et mêlés aux autres anomalies, dans les deux magasins. Il s'agit d'une correction technique de la protection demandée, sans nouvelle règle métier à arbitrer par Ced.

Hors R1, aucun secret ou donnée réelle identifié dans les éléments examinés. L'outil utilise le gardien commun et le confinement existant ; les rapports sont validés après la fin du processus, avec liaison par empreintes. Les requêtes A-31 sont des lectures à valeurs fixes ; le préfixe passe par le chargeur de configuration commun. Les droits des fichiers et les sorties fermées sont couverts par les preuves natives. L'outil n'expose pas de route web ; nonces d'interface et paywall ne sont pas des surfaces nouvelles de ce lot.

## 5. Doctrine

Le standard est privilégié : objets WooCommerce, choix natif du magasin, lecteurs WCS et distinction entre références enregistrées et abonnements effectivement résolus. Le recours au lecteur non caché est expliqué par l'obligation de lecture seule. La logique d'agrégation est isolée dans `Analysis.php`, avec `strict_types` et espace de noms `Imagine`.

Les preuves de style sont acceptées par le vérificateur ; les exceptions de fixture sont documentées. Aucun changement de l'import gelé ou du gardien n'est demandé dans cette relecture. Aucune question visuelle, métier ou touchant au réel n'est ouverte par le constat retenu.

## 6. Études (lots sans code)

Sans objet : lot de code. Le README cite les documentations officielles et distingue les sources publiques des empreintes du code installé. Ces pages externes n'ont pas été consultées pendant la relecture, conformément au périmètre local imposé ; les reçus d'inspection native ont été examinés.

## Verdict

**À corriger.**

- **Bloquant :** aucun point classé à ce niveau.
- **Important : R1**, regroupement K=5 inefficace pour les renouvellements orphelins.
- **Mineur :** aucun point distinct retenu.

Le vérificateur du paquet passe. Les suites locales restent partiellement empêchées par les permissions des dossiers temporaires, limite distincte de R1. Ce verdict n'est pas un GO.
