# A-01 — Vérification (2e et dernier tour)

Vérificateur : Claude Code (NUC). Date : 22/11/2026.
Objet : contrôler que les corrections de `corrections/A-01.md` ont bien été appliquées par Hermès, rejouer les tests, repérer régressions et écarts. Pas une relecture complète neuve.

Méthode : `git diff` depuis `c5183bc` (fusion `corrections/A-01.md` figée) jusqu'à l'état de travail actuel, sur `wp/` et `production/A-01/`. Lecture ligne à ligne de `publish.py`, `inside.py`, `worker.py`, des notes et des reçus. Les 4 questions ouvertes de la fusion ont reçu une réponse de Ced dans `docs/arbitrages-2026-11-22.md` (section A-01, « 17 h ») : prises en compte.

---

## 1. Suivi des instructions de `corrections/A-01.md`

### Instruction 1 — R4 (priorité) : arrêt garanti avant tout nettoyage
**Appliquée.** `wp/outils/staging-court/publish.py:562-603`. Le bloc `finally` est réécrit : chaque nettoyage passe par `cleanup_attempt(phase, action)` (l.565) qui capture l'exception et la range dans `result['cleanup_errors']` **sans la laisser remonter**. L'arrêt de sûreté est tenté **en premier**, avant suppression des helpers et du runner : `if created and (self_test or receipt['status'] != 'PASS'): cleanup_attempt('failure_stop', stop_site)` (l.574-577). La présence de la moindre erreur de nettoyage force `status='FAIL'` (l.603). Le contre-exemple de R4 (témoin en échec → `FAIL`, puis suppression runner en échec) est donc couvert : l'arrêt n'est plus court-circuité.
Test d'orchestration ajouté : `test_corrections.py::CleanupOrchestration::test_marker_write_then_runner_removal_failure_still_stops_site` → **vert chez moi**. Reçu : `production/A-01/corrections-22nov/faults-15bcd5cf2841/marker-and-removal.json`.

### Instruction 2 — R3 : reçu d'échec structuré (étape + code liste sûre)
**Appliquée.** `wp/outils/staging-court/inside.py:248-263` : `execute_offline_request` renvoie toujours un reçu, y compris en exception, avec `failure:{stage,code}` tirés d'un dictionnaire **fermé** `FAILURE_STAGES` (l.229-245). Un code inconnu retombe sur `IMPORT_REFUSED` ; jamais de stderr/SQL brut. Côté parent, `publish.py:478-486` relit `offline.json` **avant** destruction du runner et pose `receipt['offline_failure']` ; reçu illisible → `OFFLINE_RECEIPT_UNAVAILABLE` (l.481).
Test : `test_corrections.py::OfflineDiagnostics::test_truncated_archive_and_unsupported_sql_have_distinct_safe_receipts` → **vert**. Deux diagnostics distincts prouvés : `archive_restore/ARCHIVE_TRUNCATED` et `sql_preflight/SQL_DDL_UNSUPPORTED` (reçus `faults-*/archive-truncated.json`, `sql-unsupported.json`).

### Instruction 3 — R1 : version du cœur contrôlée, pas de montée implicite
**Appliquée.** `wp/outils/staging-court/inside.py:71-100` : `validate_core_version(package, version_file, expected)` exige l'égalité textuelle stricte `source == pinned == expected` **avant** tout import SQL/bootstrap (appel l.124, en amont du plan et de l'import DB). Discordance → `SOURCE_CORE_VERSION_MISMATCH` ou `PINNED_CORE_EXPECTED_VERSION_MISMATCH`, avec les versions au reçu. En complément, `publish.py:109` `runtime_core_preflight` lit la version du cœur épinglé **en données seules, avant création de site**. Version attendue paramétrable `--expected-core-version` (défaut opérateur 6.9.1), conforme à la réponse Ced n°3 (oui, cœur épinglé à la version production).
Tests : `test_corrections.py::SourceCoreVersion` et `test_arbitrations.py::ExpectedCore` → **verts**. Cas « source ≠ cœur » exercé. Refus réel du défaut 6.9.1 contre le runtime 7.0.9 : `production/A-01/publication-22nov/a6ca179f2442/result.json` (`status:FAIL`, aucun site créé, erreur levée à `publish.py:413`).

### Instruction 4 — R2 : moteurs non-InnoDB signalés, non bloquants
**Appliquée.** `wp/outils/staging-wp-integration/worker/worker.py:79-83,137-138,187` : `sql_plan` accepte un ensemble **fermé** et opt-in `{INNODB, MYISAM, ARIA, MEMORY}` (défaut inchangé `INNODB` pour les autres appelants), renvoie `table_engines`, sans suffixe SQL arbitraire ni moteur externe. `inside.py:155` l'appelle avec les quatre moteurs ; relecture indépendante des moteurs via `information_schema` après import (l.176-181), refus `TABLE_ENGINE_READBACK_REFUSED` si conversion ; les non-InnoDB passent en `warnings:[{code:NON_INNODB_TABLE,…}]` (l.218).
Test : `test_corrections.py::TableEngines::test_myisam_is_preserved_and_reported_without_general_sql_fallback` → **vert**. MyISAM réellement importé, conservé et signalé dans les cas E2E classique/HPOS (reçu `publication-22nov/79cef0705045/result.json`). Réserve honnête : Aria/Memory sont en grammaire seulement, non qualifiés E2E (documenté dans `notes.md`).

### Instruction 5 — R5 : profil « vérifié » rendu cohérent
**Appliquée, selon l'arbitrage Ced n°2** (« par scripts de bascule seulement »). L'arbitrage prime l'alternative « refermer l'egress » de la fusion. `publish.py:240` et `inside.py:190` conservent `DISALLOW_FILE_MODS=true`/`DISALLOW_FILE_EDIT=true` ; auto-updates désactivées ; egress `*.wordpress.org`/`*.woocommerce.com` **conservé parce que les scripts en ont besoin pour télécharger** (`update_policy`, `publish.py:394`). L'incohérence « egress ouvert mais inutilisable » est levée : le nouveau banc `script_capacity_probe.php` + `publish.py:342` prouve après publication que le téléchargement HTTP 200 marche sous verrou, avec déploiement/rejeu idempotent/rollback par script, et que l'updater admin/WP-CLI reste refusé.
Tests : `test_arbitrations.py::ScriptsOnlyCapacity` et `::ReceiptGates` (dont refus d'un reçu de capacité falsifié) → **verts**. Capacité prouvée dans `publication-22nov/79cef0705045/result.json`.

### Instruction 6 — mineur : documenter mutation `CREATE_WORDS` et périmètre de format
**Appliquée.** `production/A-01/notes.md` : mutation `CREATE_WORDS` en mémoire locale seulement (section R6) et périmètre de format qualifié / refus attendus (`.wpress` non compressé, site simple, grammaire fermée, versions épinglées). Également résumé dans `wp/outils/staging-court/README.md`.

### Instruction 7 — mineur : second motif bloquant de bout en bout
**Appliquée.** `publish.py:385` : le self-test exerce désormais **quatre** cas, dont `('classic','personal')` ; `--case personal` pour le rejeu ciblé. Deux motifs bloquants traversent tout le chemin (archive → 3 scripts natifs → sas → relecture arrêt/HTTP) : `SECRET_OU_IDENTIFIANT` et `TABLE_PERSONNELLE_A_TRANCHER` (`publish.py:506`). Prouvés en `REFUSED_OFFLINE` dans `publication-22nov/79cef0705045/result.json`.

**Bilan : 7 instructions sur 7 appliquées** (5 importantes, 2 mineures). Les 4 questions ouvertes de la fusion sont tranchées par Ced dans `docs/arbitrages-2026-11-22.md`.

---

## 2. Résultat des tests

Rejoués par moi, en local (Windows, Python, sans Docker ni accès site) :

| Suite | Résultat |
|---|---|
| `wp/tests/a01-court/test_publication.py` | **8/8 OK** |
| `wp/tests/a01-court/test_corrections.py` (R4, R3, R1, R2) | **4/4 OK** |
| `wp/tests/a01-court/test_arbitrations.py` (version attendue, capacité scripts, portes de reçu) | **6/6 OK** |
| `wp/tests/a01-court/test_publication_preflight.py` | **7/7 OK** |
| `python -m unittest discover -s wp/tests/staging-e2e -p test_harness.py` | **17/17 OK** |

**42 tests verts rejoués.** Les lignes `{"status":"FAIL",…}` affichées après deux suites sont des sous-processus bac-à-sable sur un chemin de refus **attendu** (répertoire temporaire), pas des échecs : les deux suites rapportent `OK`.

Intégrité code ↔ preuve (lecture seule, sans `--live-cleanup`) sur le reçu cité au `PRET` :
`python wp/tests/a01-court/verify_publication.py --report production/A-01/publication-22nov/79cef0705045/result.json` → **PASS**, 4 cas, `source_payloads_match_current_files: true`. Les empreintes des sources de la commande correspondent aux fichiers actuels : le code livré est bien celui qui a produit la preuve. `shared_tool_source_hashes_match_live:false` est normal — c'est simplement la valeur du drapeau `--live-cleanup` non passé (`verify_publication.py:134`), pas un défaut d'intégrité.

**Non rejoué par moi** (hors droits d'exécution du relecteur : Docker, licence Novamira, extensions commerciales) : la publication live `--self-test-publication` (4 cas), les pilotes de pannes `exercise_corrections.py`, la régression hors ligne (18 contrôles, 337 assertions). Ces reçus restent **auto-déclarés par la commande** ; le premier import réel, lancé par Ced, fera foi. C'est la même limite assumée qu'au premier tour et par le brief — pas un défaut.

---

## 3. Régressions et modifications non demandées

- **Aucune régression A-01 constatée.** Les scripts natifs `wp/outils/staging/*` sont **inchangés** (aucun dans le diff). La seule retouche de l'outil partagé est `worker.py`, exigée par R2, et **rétro-compatible** (paramètre `table_engines` à défaut `INNODB`, les autres appelants ne changent pas de comportement).
- **Refus par défaut 6.9.1 assumé, pas une régression.** L'état livré est un *PRET de code* : avec `--expected-core-version 6.9.1` (défaut opérateur), la commande **refuse avant toute lecture d'archive** parce que le runtime commercial épinglé est 7.0.9, et que Subscriptions 9.4.1 / WooCommerce 11.1.1 exigent WP 7.0. Ce blocage opérationnel est **honnête et correctement déclaré** (`PRET`, `notes.md`, `README.md`) ; la réponse Ced n°4 l'accepte et renvoie à un lot de qualification court dédié. Aucun minimum de paquet contourné, aucune montée de version implicite.
- **Changements hors périmètre A-01, à signaler (pas une régression A-01).** Les mêmes commits de synchro embarquent des modifications du lot **C-05** (marge de confirmation d'un premier paiement SEPA devenue un réglage, arbitrage du 22/11 17 h) : `wp/plugins/imagine-pilotage/src/Echeancier/{Reglages.php,ReglagesAdministration.php,README.md}`, `wp/tests/echeancier-runner/*`. Elles ne concernent pas A-01 et relèvent de la vérification de C-05.
- **Fichiers non encore commités** (état de travail) : `wp/tests/a01-court/verify_correction_artifacts.py` (modifié) et deux artefacts `production/A-01/corrections-22nov/artifact-arbitrages-{before-pret,final}.json` (non suivis). Cohérents avec la remise ; la synchronisation Git ne les a pas encore pris.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les 7 instructions de la fusion sont appliquées et citées, les 4 questions sont tranchées par Ced, les tests rejouables sont au vert, l'intégrité code ↔ preuve est confirmée par empreintes, et aucune régression A-01 n'est constatée. Il ne reste **aucun problème de fond ni question ouverte** côté code : le « blocage 6.9.1 » n'est pas un défaut mais le périmètre honnêtement déclaré du lot (publication qualifiée en 7.0.9 ; 6.9.1 renvoyé à un lot de qualification court, accepté par Ced).

**Rappel doctrine (§3/§6).** Ce verdict ne vaut que pour la clôture d'un lot de code. **Ce n'est pas un GO** : ni l'import de la production d'Imagine, ni la publication 6.9.1, ni l'ouverture d'un staging aux agents. Le premier import réel reste à Ced, par un GO écrit nommant la tâche, et son rapport sera relu avant toute ouverture. Les changements hors A-01 (C-05 SEPA) sont à vérifier dans leur propre lot.
