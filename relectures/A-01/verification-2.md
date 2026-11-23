# A-01 — Vérification n°2 (après la qualification 6.9.1 d'Hermès)

Vérificateur : Claude Code (NUC). Date : 23/11/2026.
Objet : contrôler les modifications apportées à A-01 **depuis** `relectures/A-01/verification.md` (figée au commit `618d74b`, 22/11 17:33). Ce n'est pas une relecture complète neuve.

**Ce qui justifie ces modifications.** La consigne active n°1 de `A-FAIRE.md` (23/11, 8 h) → brief `briefs/A-01-qualification-6-9.md`, lui-même issu de la **réponse n°4 de l'arbitrage `docs/arbitrages-2026-11-22.md`** (§ A-01, 17 h : « un premier essai peut être refusé pour cause de version → lot de qualification court »). Le blocage à lever : la commande refusait toute archive 6.9.1 parce que le banc n'était qualifié qu'en 7.0.9.

**Méthode.** `git log/diff 618d74b..HEAD` sur `wp/` et `production/A-01`. Les fichiers A-01 touchés : `core_source.py` (nouveau), `publish.py` (+168), `inside.py`, `archive.py`, `run.py`, `publication_probe.php`, plus les bancs `test_core_selection.py`, `test_qualification_receipts.py`, `test_password_stdin.py`, `qualification_69.py`, `exercise_operator_69.py`, `verify_qualification_69.py`. Lecture des reçus `publication-23nov/52170a14f7a7`, `qualification-23nov/operator-e45e9cc3c582`, `tests-21nov/620035d3d7f6` et de `production/A-01/{notes.md,PRET}`.

---

## 1. Consignes et arbitrages — Appliqué / Non appliqué / Partiel

### Brief point 1 — le cœur suit l'archive, `--expected-core-version` reste un garde-fou
**Appliqué.**
- Lecture de la version dans le manifeste **sans restaurer fichiers/SQL** : `archive.py:11` ajoute `metadata_only`, exploité par `publish.py:126` `archive_core_preflight` (lecture seule, avant tout site/téléchargement/PHP).
- Téléchargement de la version **exacte** depuis wordpress.org, hors archive : `core_source.py:85` `prepare_core` (contrôle MD5 officiel + relecture de `version.php`, `wp-content` du ZIP exclu : `core_source.py:100`). Côté opérateur, la version téléchargée est celle **de l'archive** : `publish.py:526` `prepare_core(receipt['archive_core_preflight']['source'])`.
- Cœur posé **sur cible vide avant injection** puis relu : `publish.py:147` `set_empty_runner_core`, et à l'injection `publish.py:278-279` `assert empty_core['archive_content_absent'] is True` et `version == source == pinned`.
- Égalité stricte garantie au runtime : `publish.py:633-636` `checked_runtime` force `ok=False, core_version_mismatch=True` si la sonde ≠ source.
- Garde-fou `--expected-core-version` : `core_source.py:26` lève `SOURCE_EXPECTED_CORE_VERSION_MISMATCH` si source ≠ attendu. **Prouvé** : reçu opérateur `operator-e45e9cc3c582/result.json`, `cases[0].expected_version_guard` (archive 6.9.1 / attendu 7.0.9 → `exit:1, no_site_created:true, no_core_download_or_bootstrap:true`).

### Brief point 2 — aucune extension installée/mise à jour ; minima WP/PHP = avertissement, pas refus
**Appliqué.**
- Scan des en-têtes d'extensions en texte inerte, requis → avertissements non bloquants : `core_source.py:108` `plugin_warnings` (`blocking:False`).
- Branché à la vérification hors ligne : `inside.py:221` ajoute ces avertissements, et `inside.py:222` pose `import_installed_or_updated_plugins: False`.
- **Prouvé** dans `52170a14f7a7/result.json` : `warnings` contient `PLUGIN_REQUIRES_NEWER_WORDPRESS` (99.0 vs 6.9.1) et `PLUGIN_REQUIRES_NEWER_PHP` (99.0 vs **8.2.32**, version cible réelle, pas « 8.2 »), les deux `blocking:false` ; `import_installed_or_updated_plugins: false` ; les deux publications propres aboutissent malgré ces avertissements.

### Brief point 3 — qualification en 6.9.1 sur site fictif, dernière Woo compatible, aller-retour + cas piégé
**Appliqué.**
- Branche 6.9.1 : `publish.py:492` `qualified_69`, fixture Woo publique préparée (`qualification_69.py`, `publish.py:495-502`).
- **Prouvé** : `publication-23nov/52170a14f7a7/result.json`, `status:PASS`, **4 cas**. Les deux cas propres (classique/HPOS) : runtime réel **WordPress 6.9.1 / Woo 11.0.1 / PHP 8.2.32**, `publication:verified`, témoin `.imagine-staging-verified.json` relu (`runtime_probe_passed:true`). Les deux cas piégés (secret + table personnelle) : `REFUSED_OFFLINE`, aucune injection. Woo **11.0.1** = dernière version publique compatible 6.9.1 (les 8 versions stables supérieures exigent WP 7.0, documenté `notes.md`).
- Entrée opérateur exacte sur archive fictive : `operator-e45e9cc3c582` (propre → exit 0 ; piégé → exit 1), confirmé par l'outil de vérification.

### Brief point 4 — Subscriptions/Memberships en 6.9.1 : utiliser si dispo, sinon ne pas bloquer et écrire la limite
**Appliqué.**
- Subscriptions **non installé** en branche 6.9.1 : `publish.py:563` n'installe que `woocommerce-memberships` ; limite inscrite au reçu `publish.py:502` `subscriptions_691_limit`.
- Sonde tolérante à l'absence de Subscriptions : `publication_probe.php:78` (`tested:false, reason:"Subscriptions absent; 6.9.1 not qualified"`), ancien chemin 7.0.9 **conservé** sous garde (pas de régression).
- Assertions 6.9.1 : `publish.py:667` `assert probe['versions']['subscriptions'] is None`.
- **Memberships 1.30.3 réellement exercé** en 6.9.1 : sonde `memberships:"1.30.3"`, droits/shortcodes via `publication_probe.php:81-102`.
- Limite **dite clairement** : `notes.md:27` et `PRET` (« Subscriptions n'est PAS qualifié en 6.9.1 … premier import réel par Ced, rapport relu avant ouverture »).

### Livrables du brief
**Appliqués.** Mode d'emploi PowerShell en une page en tête de `notes.md:1-27` (commande exacte, ce que Ced fournit, résultat, durée 434.78 s, quoi faire en cas de refus) ; limite point 4 ; `production/A-01/PRET` présent.

### Arbitrage 22/11 — réponses conservées
- **Q3** (version production paramétrable, pas une constante) : **Appliqué**, amélioré — le cœur suit désormais le manifeste, l'attendu n'est plus qu'un garde-fou (`publish.py:505` défaut 6.9.1).
- **Q4** (premier essai refusable → lot de qualification court) : **Appliqué** — ce lot *est* cette qualification ; la limite Subscriptions reste explicite et renvoyée au premier import réel de Ced.
- **Q2** (mises à jour par scripts de bascule seulement, `DISALLOW_FILE_MODS`, egress conservé) : **Appliqué, inchangé** — témoin `update_policy: "deployment_scripts_only; DISALLOW_FILE_MODS retained; update-host egress retained"`.
- **Q1** (témoin racine + rapport) : **Appliqué, inchangé** — `verified_marker_readback.status:"verified"`.

---

## 2. Résultat des tests

Rejoués par moi en local (Windows, Python, lecture seule) :

| Suite | Résultat |
|---|---|
| `test_core_selection.py` | **4/4 OK** |
| `test_password_stdin.py` | **5/5 OK** |
| `test_qualification_receipts.py` | **8/8 OK** |
| `test_arbitrations.py` | **6/6 OK** |
| `test_corrections.py` | **4/4 OK** |
| `test_publication.py` | **8/8 OK** |
| `test_publication_preflight.py` | **7/7 OK** |

Les lignes `{"status":"FAIL",…}` affichées après certaines suites sont des sous-processus bac-à-sable sur un chemin de refus **attendu** (répertoire temporaire) ; les suites rapportent `OK`.

**Vérification indépendante (outil parent, lecture seule, sans `--live-cleanup`) :**
`python wp/tests/a01-court/verify_qualification_69.py --publication …/52170a14f7a7/… --operator …/operator-e45e9cc3c582/… --offline …/620035d3d7f6/…` → **PASS**. Elle a rejoué elle-même **54 tests unitaires hôte (`unit_exit:0`)**, confirmé les 4 cas de publication, les 2 cas opérateur (propre 0 / piégé 1), les 18 contrôles hors ligne, et surtout `payloads_match_current: true` — **le code livré est bien celui qui a produit la preuve** (empreintes). `memberships_691: "1.30.3 actually activated"`, `subscriptions_691: "NOT_TESTED; prior 7.0.9 qualification retained"`.

**Non rejoué par moi** (hors droits d'exécution du relecteur : Docker, licence Novamira, extensions commerciales) : la publication live `--self-test-publication`, l'entrée opérateur réelle, et la passe `--live-cleanup` (GET/inspect Docker). Ces reçus restent **auto-déclarés par la commande**, comme aux tours précédents ; le premier import réel, lancé par Ced, fera foi. Limite assumée par le brief, pas un défaut.

---

## 3. Régressions et modifications non demandées

- **Aucune régression A-01.** Outil partagé et modèles inchangés : `tool_sources_unchanged: true`, `shared_tool_modified: false`, `no_Novamira: true` au reçu. Les 11 scripts natifs et `worker.py` ne sont pas dans le diff.
- **`archive.py` rétro-compatible.** `metadata_only` est à défaut `False` ; la bascule `sql is None` → `'database.sql' not in seen` est équivalente en mode normal (database.sql reste obligatoire). Ajout d'un plafond 1 Mo sur `package.json` = durcissement, pas un changement de comportement sur archive valide.
- **`publication_probe.php` rétro-compatible.** Le chemin Subscriptions 7.0.9 est seulement placé sous garde `if (!empty($fixture['subs']))` ; il n'est pas supprimé.
- **Modifications hors périmètre A-01, à signaler (pas une régression A-01).** Les mêmes commits de synchro / l'arbre de travail embarquent le lot **T-01 « commande de rejeu »** (consigne active n°2) : `wp/tests/rejouer.ps1`, `wp/tests/preparer-image.ps1`, `wp/tests/t01/*` (dont `probe-isolation.php`, `test-isolation.ps1` non suivis dans `git status`). Ils ne touchent pas le code de production A-01 et relèvent de la vérification de T-01, pas de ce lot.

---

## 4. Verdict

**Prêt pour la clôture.**

Les quatre points du brief `A-01-qualification-6-9.md` et les quatre réponses de l'arbitrage du 22/11 sont appliqués et cités ; la qualification 6.9.1 est prouvée de bout en bout sur archive fictive (4 cas PASS, runtime réel WordPress 6.9.1 / Woo 11.0.1) ; les tests rejouables sont au vert ; l'intégrité code ↔ preuve est confirmée par empreintes (`payloads_match_current: true`) ; aucune régression A-01. La seule réserve — Subscriptions non qualifié en 6.9.1 — n'est pas un problème de fond mais la **limite explicitement prévue par le brief (point 4) et l'arbitrage (Q4)**, renvoyée au premier import réel de Ced.

**Rappel doctrine (§3/§6).** Ce verdict ne vaut que pour la clôture d'un lot de code. **Ce n'est pas un GO** : ni l'import de la production d'Imagine, ni l'ouverture d'un staging aux agents. Le premier import réel reste à Ced, par un GO écrit nommant la tâche, et son rapport sera relu avant toute ouverture. Le lot T-01 embarqué dans les mêmes commits est à vérifier dans son propre lot.
