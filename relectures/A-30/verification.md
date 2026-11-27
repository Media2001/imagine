# Vérification A-30 — second et dernier tour

Vérificateur : Claude. Objet : contrôler que les corrections de `corrections/A-30.md` ont été appliquées par Hermès, relancer les tests, repérer toute régression ou modification non demandée, et rendre un verdict.

Base de comparaison : commit de la fusion `83297a58` (27/11 06:43). Changements examinés via `git diff 83297a58 HEAD` sur `wp/tests/a30`, `wp/outils/bascule/a30` et `production/A-30`. Ce n'est pas une relecture complète : je contrôle le delta et les preuves.

Séquence constatée : livraison **worker** d'Hermès à 06h39 (`production/A-30/corrections-06h39.md`) qui applique C01/M1/M2 dans les tests/outils **sans resceller** (verifiers laissés rouges, `PACKAGE_DRIFT`, par construction) ; puis étape **parent/T03** vers 08h14 qui rejoue les matrices natives, obtient les paquets verts, resèle et pose un nouveau `PRET`. C'est conforme à la doctrine (le worker ne scelle pas ; le parent scelle après T03).

## 1. Instructions de corrections/A-30.md

### Instruction 1 (important — A30-C01) : supprimer la dépendance implicite à `TMPDIR`, centralisée. **Appliquée.**
- Nouveau point unique `wp/tests/a30/temp_support.py:22` : `assert_outside_repo(os.environ.get('TMPDIR') or tempfile.gettempdir())`. `TMPDIR` devient une surcharge **optionnelle** ; absent/vide → répertoire temporaire standard de Python.
- Garde hors dépôt conservée : `assert_outside_repo` (`temp_support.py:14-18`) refuse tout chemin sous la racine du dépôt (`A30_TEST_TEMP_IN_REPOSITORY`), avant et après création.
- Les quatre classes passent par ce point unique : `test_core.py:32`, `test_cli.py:18`, `test_boundary.py:19`, `test_verify.py:19` appellent désormais `temporary_directory(...)`. Plus aucun `os.environ['TMPDIR']` dans la suite (grep à zéro).

### Instruction 2 (important — A30-C01, preuve) : rejeu sans `TMPDIR`, `TEMP`/`TMP` définies, deux encodages, 25 tests verts, prouvé par `matrix.py` sur session propre, paquet reconstruit. **Appliquée.**
- `matrix.py:27` (`clean_environment`) **retire** `TMPDIR`/`TEMP`/`TMP` hérités et pose `TEMP`/`TMP` sur un scratch privé hors dépôt (`--temp-root`, `assert_outside_repo`). Le fils est lancé `cwd=ROOT` dans un nouveau processus.
- La matrice sonde l'environnement réellement exécuté et refuse un environnement non conforme : `matrix.py:44` (`environment_valid`) vérifie `TMPDIR_present is False`, `TMPDIR is None`, `TEMP=TMP=tempfile.gettempdir()` hors dépôt, `platform`, encodages, mode UTF-8 et nombre de tests découverts > 0 (`A30_CLEAN_WINDOWS_ENV_REQUIRED`).
- `test_result` (`matrix.py:60`) lit le résumé réel d'unittest (exécutés = découverts, aucun échec/erreur/ignoré) : plus de « `OK` in text » laxiste.
- `verify.py` durci : `python_evidence_valid` (`verify.py:35`) recalcule le résumé et les empreintes et exige l'environnement propre ; le schéma scellé est contrôlé (`verify.py:71`, `schema == 'a30-clean-windows-v1'`). Plus de simple seuil « ≥ 17 + hash ».
- Preuve ajoutée au banc : trois nouveaux modules de test (`test_temp_support.py`, `test_matrix.py`, `test_historical_windows.py`) qui exercent le retrait de `TMPDIR`, le refus du dépôt, le comptage réel et le contrôle sémantique du lecteur.
- Paquet scellé reconstruit : `production/A-30/preuves/final/windows-matrix.json` enregistre, pour **utf-8 et cp1252**, `tests_run = suite_discovered = 38`, `all_pass = True`, `TMPDIR_present = False`.

### Instruction 3 (mineur — M1) : capture datée hors dépôt des pages WooCommerce, ou « doute » explicite. **Appliquée.**
- `wp/outils/bascule/a30/README.md:13` : captures du 27/11/2026 05:49:56 UTC, HTTP 200, octets/en-têtes/SHA-256 conservés **hors dépôt** ; **doute explicite** maintenu sur l'ancienne affirmation des deux URL « importing-subscriptions » en 404 (non recapturée, ne fonde pas le choix). Empreintes détaillées dans `production/A-30/corrections-06h39.md:58-67`.

### Instruction 4 (mineur — M2) : documenter le marqueur `imagine_staging_disabled_plugins` comme signal canonique de neutralisation. **Appliquée.**
- `wp/outils/bascule/a30/README.md:49` : paragraphe « Contrat canonique avec le moteur de staging gelé » — la présence (et non la valeur) de l'option est le signal lu par `Inventory.php`, et tout changement du moteur impose la mise à jour/requalification d'A-30.
- Réserve : la fusion proposait « dans `Inventory.php` **ou** le README ». Le README est donc conforme ; `Inventory.php` n'a volontairement pas été touché (aucun changement des six PHP A-30).

### Instruction 5 (clôture — hors A-30) : repartir d'un arbre propre avant le second tour. **Non exécutée — à dessein, reste réserve de clôture.**
- Correctement traitée comme réserve de clôture, pas comme modification A-30 : aucune opération Git, aucun reset, aucun autre lot touché (doctrine §3 : un worker ne fait pas de Git).
- L'arbre de travail porte toujours des modifications non committées d'autres lots (B-09, C-27, A-31/demo, Acquisition…). La dérive de compte global (1157/36234 contre 1153/36075) vient de ces lots concurrents, pas d'A-30. **À traiter par le parent à la clôture.**

## 2. Résultat des tests (relancés localement)

Session Windows **propre** (confirmé : `TMPDIR` absent, `tempfile.gettempdir()` = `C:\Users\Ced\AppData\Local\Temp`). C'est exactement le contexte qui produisait 22/25 `KeyError` avant correction.

- `python -B -m unittest discover -s wp/tests/a30 -p "test_*.py"` (UTF-8) : **Ran 38 tests — OK**.
- Même suite en `-X utf8=0` (cp1252) : **Ran 38 tests — OK**.
- `python -B production/A-30/verify.py` : `{"exit_code": 0, "package": "PASS", "native_packet": "PASS"}`.
- Paquet scellé `windows-matrix.json` : deux encodages à `tests_run = suite_discovered = 38`, `all_pass = True`, `TMPDIR_present = False` — cohérent avec mon rejeu.

Le défaut A30-C01 est **reproductiblement corrigé** : plus aucun `KeyError: 'TMPDIR'`, la suite est rejouable sur une session Windows propre dans les deux encodages. L'exigence écrite du brief (« Suite Python rejouable sous Windows (cp1252) ») est honorée.

## 3. Régressions ou modifications non demandées

- **Périmètre A-30 propre.** Le delta A-30 ne touche que `production/A-30/`, `wp/tests/a30/` et `wp/outils/bascule/a30/README.md`. Les six PHP d'A-30 sont inchangés, l'axe produit `0` conservé, les 48 dépendances identiques (Hermès le documente, le diff le confirme : aucun PHP A-30 modifié).
- **Nouveau `PRET` à 08h14.** Créé par l'étape parent après requalification native (« 11 paquets verts, preuve T03 »). Légitime et cohérent (`verify.py` PASS). À noter : la livraison worker 06h39 laissait les verifiers rouges par construction ; c'est le rescellage parent qui les a rendus verts. Rien d'anormal, mais la bascule rouge→vert tient à l'étape parent, pas à la seule livraison worker.
- **Aucune régression constatée** dans A-30 : la suite passe au vert là où elle échouait, le lecteur scellé est plus strict qu'avant, et aucune preuve verte n'a été recopiée d'un ancien sceau.
- **Hors A-30** : les changements concurrents d'autres lots dans l'arbre (cf. instruction 5) ne sont pas des modifications A-30 ; ils relèvent de la clôture.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions sont traitées : les deux importantes (A30-C01) sont appliquées et vérifiées par rejeu réel sur session Windows propre (38 tests OK, UTF-8 et cp1252, `TMPDIR` absent), les deux mineures (M1/M2) sont documentées, la cinquième est correctement laissée en réserve de clôture au parent. Aucune régression A-30, aucune modification hors périmètre dans le delta A-30, aucune question ouverte pour Ced (A30-C01 purement technique, M1/M2 documentaires, axe produit `0` décision technique déjà arbitrée).

Réserves à porter à la clôture (non bloquantes, hors A-30) :
- Repartir d'un arbre propre avant de figer les comptes globaux (instruction 5) : la dérive 1157/36234 vs 1153/36075 vient de lots concurrents.
- La qualification native verte dépend de l'étape parent/T03 ; toute nouvelle évolution de source invaliderait le sceau et imposerait un nouveau paquet.

**Rappel doctrine : ce verdict n'est pas un GO.** « Prêt pour la validation de Ced » ne vaut que pour la clôture d'un lot de code ; il n'autorise aucun import, ni accès à un site, une base ou un compte réel.
