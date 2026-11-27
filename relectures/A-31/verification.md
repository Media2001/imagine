# Vérification (2e et dernier tour) — Lot A-31 (historique des commandes, comptées)

Vérificateur : Claude. Date : 2026-11-27. Base relue : état au commit `34ea9f21` (dépôt des corrections, 09:03). État vérifié : HEAD (`fd773579`). Diff limité à `wp/outils/bascule/a31`, `wp/tests/a31` et `production/A-31` ; le reste du diff `wp/` concerne A-32, A-33, les démos et les plugins (autres lots, hors périmètre).

Ce n'est pas une relecture complète. Je contrôle seulement l'application des 6 instructions de `corrections/A-31.md`, les tests, et les écarts non demandés.

## 1. Application des instructions de `corrections/A-31.md`

Rappel : le défaut proposé (§5) était **publier les comptes exacts des liens cassés**. Hermès a appliqué ce défaut, comme la fusion l'autorise sans réponse de Ced.

| # | Instruction | État | Preuve |
|---|---|---|---|
| 1 | Sortir les 4 métriques de liens cassés du K=5 ; chacune devient un scalaire exact (y.c. 1 à 4) | **Appliquée** | `Analysis.php:50-51` (`$links` scalaire), `:63,66,69,75` (incréments), `:81` (`$result = $links`). Les clés `orphan_renewals`/`structural_links` ont disparu des `$buckets` (`:41`). `report.py:9-10` (`LINKS`), `:48` valide 4 entiers. |
| 2 | Réserver pool()/K=5 aux ventilations ; statuer sur `refunds` (défaut = total exact) | **Appliquée** | `years`/`statuses` restent sous `pool()` (`Analysis.php:82-85`) ; `natures` conserve le K=5 du 1er tour (non contesté) ; `refunds` expose `total` exact + groupes annuels sous K=5 (`Analysis.php:87`, `report.py:50-54`). Conforme au défaut de la question 2. |
| 3 | Adapter schéma fermé + JSON/MD + `expected.py` ; tester 0/1/4/5 seule et mêlée, 2 magasins, 2 encodages ; témoin RED anti-refonte | **Appliquée** | `report.py:48-54` (schéma) ; `expected.py` (oracles scalaires) ; matrice 0→5 `alone`/`mixed` × classic/HPOS (`inside.py:87-126`, `unit.php:90-123`), UTF-8+cp1252 (`matrix.py`). Témoin RED : `run.py:100-115` (`red_scalar_rare_pool_caught`), vérifié par `verify.py:118-132`. |
| 4 | Fixture « abonnement à la corbeille » : compte à l'existence, pas vivant, renouvellement non orphelin | **Appliquée** | `seed.php:106-113` (sub actif → `delete(false)` → `trash`, relation renewal) ; contrôle `trash_subscription_exists_not_living_not_orphan` (`inside.py`, `verify.py:153`). |
| 5 | Fixture frontière changement d'année en UTC (31/12 23:xx / 01/01 00:xx) | **Appliquée** | `seed.php:89,93,100` (TZ Europe/Brussels ; parent `2018-01-01T00:30+01:00` = 2017 UTC ; renewal `2018-12-31T23:30-01:00` = 2019 UTC). Contrôle `utc_boundary_both_directions_oldest`. Conséquence attendue : `oldest` nominal passe 2018→2017 (`expected.py`). |
| 6 | Ne pas toucher l'import gelé ni le gardien ; aléa T01 = infra | **Appliquée** | `git diff 34ea9f21 HEAD -- wp/outils/staging` : vide. `-- wp/outils/bascule/a22 wp/tests/a22` : vide. Import A-28 et gardien A-22 intacts. |

Aucune instruction non appliquée ni partielle.

## 2. Résultat des tests

**Contrainte de session** : le rejeu canonique Docker (`wp/tests/rejouer.ps1`) n'a pas pu être relancé ici — le validateur de commandes de cette session non-interactive refuse l'exécution d'un `.ps1` et le lancement d'un PowerShell imbriqué ; `php`/`docker` ne sont pas joignables hors conteneur. J'ai donc (a) rejoué localement les suites Python pures du contrat, et (b) vérifié les preuves committées régénérées par Hermès après correction.

**(a) Suites Python pures, rejouées ici — vertes :**
- `test_fusion.py` : 5 tests OK (contrat scalaire 0→5 seul/mêlé, classic+HPOS ; `refunds.total` exact + années K=5 ; natures/années de refund restaurées en K=5 ; scalaires numériques fermés ; TMPDIR omis).
- `test_report.py` : 11 tests OK. `test_mutations.py` : 3 tests OK.

**(b) Preuves committées — rejeu « a31-retouche-20261127-2003 » (`production/A-31/preuves/final`) :**
- `windows-matrix.json` : Python 42 tests, `all_pass=true`, en UTF-8 **et** cp1252, exit 0 ; `run.py` natif exit 0 (deux encodages) ; style exit 0 ; `sources_stable=true`.
- `utf8/native/result.json` : **552 contrôles, exit 0, 0 non-PASS**, dont 384 contrôles scalaires, corbeille (classic+HPOS) et frontière UTC (classic+HPOS).
- `utf8/native/runner.json` : `red_mutation_k5_caught` = PASS **et** `red_scalar_rare_pool_caught` = PASS.
- `utf8/native/red-scalar-unit.json` : exit 1, la cible `scalar_orphan_renewals_1_alone_orphan_renewals` tombe en FAIL → le témoin RED est bien discriminant (une re-fusion des scalaires casse le test).

Les résultats Python que j'ai rejoués concordent avec cette preuve. Réserve honnête : je n'ai pas pu relancer moi-même la matrice Docker native dans cette session ; je m'appuie sur les preuves scellées d'Hermès pour la partie WordPress/magasins.

## 3. Régressions et modifications non demandées

Aucune régression. Deux écarts, tous deux bénins et scopés à A-31 :

1. **Retrait de `TMPDIR` forcé** dans le harnais de test (`gates.py` `env.pop('TMPDIR')`, helper `matrix.py:python_environment`, assertion `verify.py` `tmpdir is None`). Non listé dans les 6 instructions, mais il règle précisément les « 7 `PermissionError` » signalées par Codex en §2 de la fusion (classées limite d'environnement, pas défaut A-31). L'effet est positif et désormais *testé* : le rejeu Python local est vert de façon fiable (42 tests, les deux consoles), ce que ma passe confirme. Modification limitée aux fichiers de test A-31.
2. **Suppression de `production/A-31/refresh-parent.json`** : ancien marqueur de provenance de la passe pré-correction (08:10), remplacé par les preuves de la nouvelle passe. Non référencé ailleurs (`grep` vide). Sans effet.

Choix de conception à noter (conforme, pas un écart) : `natures` reste sous K=5 comme au 1er tour — l'instruction 2 réserve le K=5 aux ventilations dimensionnelles et `natures` n'a jamais été contestée.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les 6 instructions sont appliquées et correctement testées ; le défaut prudent de la fusion (comptes de liens cassés exacts, `refunds.total` exact, K=5 réservé à années / années×états / natures / années de remboursement) est en place ; aucune régression ; import gelé et gardien intacts. Aucun problème de fond technique ne subsiste.

Reste, et c'est précisément l'objet de la validation de Ced, les **deux questions fermées de `corrections/A-31.md` §5** (politique d'exposition du schéma : comptes rares de liens cassés et total des remboursements **publiés exactement** vs **plafonnés à « moins de 5 »**). Le défaut proposé — publication exacte — est déjà appliqué ; si Ced tranche dans l'autre sens, l'instruction 1 bascule vers l'option inverse décrite en fin de §4 de la fusion.

**Rappel doctrine** : ce verdict n'est pas un GO. Il atteste que la correction est faite et le lot prêt à être tranché par Ced ; il n'autorise ni la clôture ni la mise en production. A-22 (gardien des sorties) conditionne toujours la sortie.
