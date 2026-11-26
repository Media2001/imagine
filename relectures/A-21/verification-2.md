# Vérification A-21 — contrôle des modifications postérieures au second tour

Vérificateur : Claude. Objet : contrôler que les modifications apportées à A-21 par Hermès **après** la vérification du second tour (`relectures/A-21/verification.md`, figée au commit `dcaf471a`, synchro 17 h 38) sont justifiées par une consigne ou un arbitrage, relancer la suite, repérer toute régression. Pas de relecture complète.

Méthode : `git log` / `git diff dcaf471a..HEAD` sur `wp/outils/bascule/a21`, `wp/tests/a21`, le gardien partagé `wp/outils/bascule/stream_guard.py` et `production/A-21` ; lecture du code modifié ; rejeu de la suite autorisée ; lecture du paquet livré. Sources de cadrage : `A-FAIRE.md` (consigne 0, lignes 17-21), `docs/arbitrages-2026-11-26.md` (passage de 19 h, sections « A-20 et A-21 » et « A-22 »), `production/A-21/notes.md` et `FINALISATION.md`.

Ce qui a changé depuis 17 h 38 : **trois fichiers de code seulement** — `stream_guard.py` (gardien partagé), `run.py` et `verify.py` (liste de dépendances scellées + compte de contrôles) — puis le paquet `preuves/final` régénéré et le marqueur `PRET` refait (17 h 06 → 19 h 21). La logique métier propre à A-21 (`Analysis.php`, `Inventory.php`, `Command.php`, `inventorier-portes`, `confine.py`, `unit.php`, `inside.py`, `README.md`) **n'a pas bougé**.

## 1. Consignes et arbitrages concernés

### A — Refaire les paquets sur le gardien final après la correction A-22 de 17 h 53 : **Appliqué**

Arbitrage de 19 h, « A-20 et A-21 » (`docs/arbitrages-2026-11-26.md:349`) : « le gardien commun a changé après ces vérifications (corrections d'A-22 de 17 h 53), Hermès a retiré lui-même leurs `PRET` et refait leurs paquets sur le gardien final. »

- Gardien partagé renforcé : `wp/outils/bascule/stream_guard.py`, nouvelle fonction `final_binding` (lignes 119-128) et appel de `stream_reports.validate` dans `complete()` (`stream_guard.py:139`).
- Ancien `PRET` retiré puis refait après le gel parent : `production/A-21/PRET` passe de `17 h 06` à `2026-11-26T19:21:25 … preuves files/rapports/2026-11-26-19h21-verification`.
- Paquet unique régénéré : `production/A-21/preuves/final` (et son miroir `utf8/`) entièrement réécrit. Note de reprise : `production/A-21/notes.md:3-9`.

### B — Cinquième canal, le fichier de rapport : **Appliqué**

Arbitrage de 19 h, « A-22 » (`docs/arbitrages-2026-11-26.md:357`) : « Règle étendue : le canari par canal compte désormais un cinquième canal, le fichier de rapport. Un outil qui charge le WordPress du site prouve qu'un rapport altéré en fin de processus n'est pas publié. Vaut pour A-23, A-24, A-25 et la suite. » Même règle dans `A-FAIRE.md:31`.

- Le succès n'est publié que si la ligne de succès (`SUCCESS[tool] + 'A22_FINAL ' + empreintes`) correspond **octet pour octet** aux `sha256` des fichiers réellement publiés : `stream_guard.py:119-128` (`final_binding`), appelée au point de publication `stream_guard.py:174`. Un rapport altéré en fin de processus casse l'égalité → refus.
- Le vérificateur du lot exige désormais **25** contrôles de canaux (au lieu de 21), dont deux `:channels:shutdown_file` et deux `:channels:shutdown_json` : `wp/tests/a21/verify.py:84`.
- Preuves livrées, toutes `PASS` : `production/A-21/preuves/final/a22-channels.json` (25 contrôles, dont `classic:A21:channels:shutdown_file`, `…:shutdown_json` et leurs équivalents `hpos`) ; `result.json` natif (`supervised_bootstrap:shutdown_artifact_canary`, `hostile_artifacts_absent:shutdown_artifact_canary`, `shutdown_missing_json`).

### C — Dépendances scellées complétées par le pont et le contrat A-22 : **Appliqué**

Prolonge R2 du second tour (sceller les dépendances courantes). Ajout de `wp/outils/bascule/stream_reports.py` et `wp/outils/bascule/stream_contract.php` à la liste scellée : `wp/tests/a21/run.py:20` et `wp/tests/a21/verify.py:12`. Le PHP confiné reçoit `auto_prepend_file=stream_contract.php` (`stream_guard.py:169`). Contrôle `exact_current_dependencies` : `PASS` (`candidate-verification.json`).

### D — « Rien d'autre n'a bougé dans leur dossier depuis 17 h 38 » : **Appliqué (vérifié)**

Consigne 0 (`A-FAIRE.md:20`). Vérifié par `git diff` : hors gardien partagé et liste de dépendances, aucun fichier source d'A-21 n'a changé. Les décisions à défaut du lot sont conservées — comptes d'inactivité disjoints, lecture directe de `woocommerce_helper_data`, trois cas IP/IPv6 : `notes.md:19` et contrôle `literal_ip_ipv6_pure_cases` = `PASS` (`candidate-verification.json`).

### E — Revalidation : portes parent après gel, puis rejeu sans Docker : **Appliqué**

Consigne 0 (`A-FAIRE.md:21`) : « tes portes rejouées après le gel des sources, puis le rejeu par le vérificateur de ce qui tourne sans Docker. Écris la date et l'heure du gel. » Gel et portes parent : **2026-11-26 T 19:21:25 +01:00** (`production/A-21/FINALISATION.md:1-3`, `PRET`), preuves présentes dans `files/rapports/2026-11-26-19h21-verification/` (vérificateur A-21 rejoué en UTF-8 et cp1252 : `A-21-utf8.json`, `A-21-cp1252.json`). Rejeu sans Docker : voir §2.

## 2. Résultat des tests

Environnement : NUC Windows 11, PowerShell. Docker/PHP natif non exécutables dans cette session (acquis depuis plusieurs lots).

- **Suite autorisée rejouée**, commande exacte :

  ```
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
  ```

  Dernière ligne :

  ```
  REJEU : 1126 tests, 35550 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
  ```

  A-21 y figure : `T01 TOOL : a21 ; 18 controls ; 0 failures ; exit=0`. Décompte identique à celui du gel parent de 19 h 21 (16 outils, 311 contrôles — `FINALISATION.md:3`).

- **Vérificateur de paquet** `wp/tests/a21/verify.py` : commande **refusée** (approbation requise, session non interactive). Je m'appuie donc sur la lecture du paquet livré : `candidate-verification.json` → `exit_code` 0, 49 contrôles tous `PASS` (dont `exact_current_sources`, `exact_current_dependencies`, `common_guard_native_channels_and_mutation`, `literal_ip_ipv6_pure_cases`, `unknown_never_zero`) ; `a22-channels.json` → 25/25 `PASS` ; `result.json` natif classique+HPOS → tous `PASS`, `exit_code` 0, `no_real_site: true`.

## 3. Régressions ou modifications non demandées

Aucune régression. La logique métier d'A-21 est inchangée et ses décisions à défaut sont conservées.

Deux points de périmètre, tous deux portés par le gardien **partagé** (donc relevant d'A-22, pas d'A-21 seul) :

1. `stream_guard.py` ajoute `A12` à la table `legacy_path` et `auto_prepend_file=stream_contract.php` à la commande PHP. Ces ajouts servent le gardien commun ; ils sont couverts par les preuves et sans effet sur le comportement propre d'A-21.
2. Le gardien reste partagé avec A-20 et A-22 : toute évolution future du gardien rouvrira la question pour A-21 — déjà signalé au premier tour. C'est précisément pourquoi la consigne 0 fait clore les trois lots ensemble.

Aucun accès au réel, aucune archive Imagine, aucun compte, aucune opération Git, Novamira ni déploiement dans ces modifications.

## 4. Verdict

**Prêt pour la clôture.**

Les modifications postérieures au second tour sont toutes justifiées par les arbitrages de 19 h (reprise sur le gardien final, cinquième canal « fichier de rapport ») et la consigne 0 ; elles sont appliquées et vérifiables dans le code et dans les preuves. La suite autorisée est verte (1 126 tests, A-21 à 18 contrôles, exit 0) et le paquet livré est cohérent (vérificateur candidat à 49/49, canaux 25/25, natif tout `PASS`). Aucun problème de fond restant, aucune régression.

Rappels : le vérificateur de paquet n'a pas pu être relancé ici (commande refusée en session non interactive) ; mon contrôle porte sur le rejeu de `rejouer.ps1` et sur la lecture du paquet. La clôture formelle d'A-21 est, par la consigne 0, groupée avec A-20 et A-22 sur le gardien final. Ce verdict clôt la vérification de code ; il n'est pas un GO au sens du §3 de la doctrine (aucune bascule, aucun accès au réel). La décision d'avancer appartient à Ced.
