# A-01 — Vérification n°6 (après la quatrième passe « refus muet » d'Hermès)

Vérificateur : Claude Code (NUC). Date : 26/11/2026.
Objet : contrôler les modifications apportées à A-01 **depuis** `relectures/A-01/verification-5.md` (committée au `1ae7771`, synchro 25/11 17:33). Ce n'est pas une relecture complète neuve.

**Ce qui justifie ces modifications.**
- Brief `briefs/A-01-archive-reelle-4.md` (voie 1, trois heures, « passe avant tout le reste »), déclenché par l'échec du premier import réel : le 26/11 à 0 h 16, l'import s'est arrêté à l'étape « base » après ~50 min sur un **refus muet** (`stage: database`, `code: COMMAND_REFUSED`, stderr jeté). Rapport source : `production/A-01/publication-23nov/3151645bb471/result.json`. Cinq tâches, **toutes techniques** : (1) plus aucun refus muet, reçus structurés assainis ; (2) compatibilité d'une vraie base de production (collations/mode SQL/instructions longues/JSON/colonnes générées/moteurs non-InnoDB/objets exécutables) ; (3) mode `--diagnose-database` en quelques minutes ; (4) reprise ; (5) nettoyage de `imagine-test-a01-ced-02`.
- `A-FAIRE.md` **PRIORITÉ ABSOLUE (26/11, 1 h 20)** : la quatrième passe passe avant tout le reste, Ced attend pour relancer.
- Arbitrage `docs/arbitrages-2026-11-26.md`, section « Files » : « La quatrième passe d'A-01 reste en tête (session de Ced, 1 h 20). » Aucun arbitrage ne tranche de règle métier ici : toutes les décisions sont techniques.

**Méthode.** `git diff 1ae7771..HEAD` sur `wp/outils/staging-court`, `wp/outils/staging`, `wp/tests/a01-court` et `production/A-01`. Code A-01 touché : nouveaux `diagnostics.py`, `sql_compat.py`, `database_only.py` ; retouches `inside.py` (+71/-91 global), `publish.py` (+63), `run.py` (+13), `sql_stream.py` (+38) ; outil natif partagé `command.php` (+30), `lib.php` (~5), `pdo-store.php` (+12). Tests nouveaux : `test_archive_reelle_4.py`, `test_diagnostics.php`, `exercise_fourth.py`, `fourth_fixture.php`, `fourth_verify.py`, `verify_fourth.py`. Notes et reçus lus : `archive-reelle-4-notes.md`, `archive-reelle-4-final.json`, `archive-reelle-4/4d311daa09cc/result.json`, `archive-reelle/5754d4a5d8b8/result.json`, `PRET`.

---

## 1. Consignes et arbitrages — Appliqué / Non appliqué / Partiel

### Tâche 1 — plus aucun refus muet, nulle part dans la commande
**Appliqué.**
- Module de diagnostic fermé commun : `wp/outils/staging-court/diagnostics.py`. `execute` (l.51-71) remplace les `subprocess.run` nus ; tout échec externe lève `CommandFailure` avec `{stage, code, …}` et **jamais** le stderr brut. Délai → `COMMAND_TIMEOUT` nommé avec `timeout_seconds` (l.54-55) ; échec de lancement → `COMMAND_START_REFUSED` + `os_errno` (l.56-57).
- MariaDB : `database_error` (l.21-34) rend `errno`, `sqlstate`, `line`, puis `statement`+`table` **lus dans la grammaire** du fichier normalisé, jamais dans le texte du message (`statement_coordinate`, l.12-18). Aucun extrait d'instruction ni valeur. Test ciblé : `test_archive_reelle_4.py:15-23` (erreur 1062 « Duplicate entry '…' » → coordonnées seules, « FICTION »/« Duplicate » absents du reçu).
- PHP : `php_error` (l.37-48) rend `class`, `file` relatif à `wp-content` (borné, anti-`..`), `line` ; message/pile/arguments **jetés**.
- Suppression des deux refus muets historiques : `inside.py` `command` passe par `execute` (l.31-37) ; l'import de base a son propre contrat `import_database` (l.224-234) avec `sql_path` pour localiser l'erreur. L'ancien `COMMAND_REFUSED` générique et le `stderr=DEVNULL` ont disparu. Démarrage MariaDB : `DATABASE_START_REFUSED`/`_TIMEOUT` deviennent des `CommandFailure` datés (`inside.py:48-53`).
- Côté appelants externes : `run.py` `docker` (l.29-30) et `publish.py` `call`/`wsl_python` (l.35-37) passent par `execute` ; les transferts de publication séparent leurs étapes et codes (`pipe_sanitized_database`, `publish.py:254-270` ; transfert cœur vide l.313-318). Fils d'étape posés tout au long de la publication (`receipt['stage']`, p.ex. `publish.py:608,633,646,690,729-744,782`) → un échec nomme l'étape atteinte (`publish.py:794-796`).
- Phases natives et sonde : `command.php::diagnostic` (l.14-34) produit `stage`/`code`/`php{class,file,line}` + `database{sqlstate,errno}` pour `PDOException`, à partir de codes **connus** (liste blanche l.21) sinon `STAGING_REFUSE` ; le `catch` muet d'avant est remplacé (l.101-108). Coordonnée d'opération suivie dans `pdo-store.php` (`failureCoordinate`, l.15-18, maj aux l.42,45,82,90,109,135) ; `lib.php` propage le reçu de sonde (l.733-735, 753). Message/argument/ligne jamais sérialisés.

### Tâche 2 — une base réelle n'est pas une base de test (compatibilité)
**Appliqué**, avec le périmètre explicitement borné.
- Collations MySQL 8 : `sql_compat.py:5-10` (`0900_ai_ci`/`0900_as_ci` → `unicode_520_ci` ; `0900_as_cs`/`0900_bin` → `bin`, utf8mb4 seul). Correspondance **syntaxique seule**, jamais sur une valeur de ligne (`compatible_tokens`, l.15-26) ; toute autre variante `_0900_` → `SQL_COLLATION_UNSUPPORTED` (l.23-24). Test `test_archive_reelle_4.py:56-62` (le littéral chaîne homonyme n'est pas touché).
- Mode SQL : `mode_statement` (l.36-47) conserve un `SET SQL_MODE` fermé et supporté (liste `MODES` l.12) ; `ANSI_QUOTES`/`NO_BACKSLASH_ESCAPES` refusés (lexer différent). À défaut, repli non strict explicite `NO_AUTO_VALUE_ON_ZERO` à l'import (`inside.py:228`, `database_start` l.46-47). Le mode source inconnu n'est **jamais inventé** (confirmé `archive-reelle-4-notes.md` l.15).
- Instructions longues / JSON / colonnes générées / index préfixé / ROW_FORMAT : `MAX_STATEMENT` porté à 64 Mio (`sql_stream.py:19`), `max-allowed-packet=256M` (`inside.py:228`), grammaire fermée élargie en mémoire (`CREATE_WORDS.update`, suffixe `ROW_FORMAT` adapté, `sql_stream.py:236-240`). Test `test_archive_reelle_4.py:65-76`.
- Moteurs non-InnoDB : lecture indépendante des moteurs après import, l'import doit **préserver** et non convertir (`inside.py:157-161`, `TABLE_ENGINE_READBACK_REFUSED`) ; avertissement `NON_INNODB_TABLE` par table (`inside.py:212-214`).
- Objets exécutables (`DEFINER`/vues/triggers/procédures/événements/`DELIMITER`) : **refus explicite avant import** `SQL_EXECUTABLE_OBJECT_REFUSED` (`sql_stream.py` `statement`, ~l.185), jamais exécution ni suppression silencieuse. Commentaires conditionnels : seul un SET fermé entier est déballé (`sql_compat.unwrap_setting`, l.29-33). Tests `:82-90`.
- Durée : import borné 3 600 s, enveloppe restauration 5 400 s (`inside.py:231` ; `publish.py:710`, `database_only.py:134`). Framer rendu possessif contre le retour arrière (`sql_stream.py:21-22`), régression de temps borné `:78-80`.
- **Limite dite clairement** (conforme à la consigne « dis ce que tu as pu reproduire ») : MySQL 8 n'a **pas** été exécuté ; son cas est dérivé des CREATE du vrai export (`archive-reelle-4-notes.md` l.16). Ce n'est pas une qualification MySQL 8 générale ni de toutes les extensions historiques.

### Tâche 3 — répéter la base sans restaurer les fichiers (`--diagnose-database`)
**Appliqué.** `database_only.py` : `diagnose_database_path` (l.79) lit **seulement** `database.sql` dans l'archive (`locate_database` saute tout payload non-SQL, prouvé par le lecteur tracé `test_archive_reelle_4.py:94-112`), l'importe dans un runner neuf `network=none`/`cap-drop ALL`/`no-new-privileges` (l.105-107), applique la politique des tables, puis **diffère explicitement** les phases natives faute des fichiers (`inside_database` l.70-73, `FILES_REQUIRED_NATIVE_PHASES`). Aucun site créé, runner détruit et absence relue (l.147-149), `data_verified=false`. Garde d'usage : `--diagnose-database` exige `--operator-ced --archive`, refuse site/mot de passe/self-test (`publish.py:542-548`). Mesuré : partie base ~9,3 s sur l'archive fictive (`archive-reelle-4-notes.md` l.9).

### Tâche 4 — reprise
**Appliqué (branche conservatrice, conforme au brief).** Le brief demandait une reprise « si simple, sinon ne la fais pas ». Hermès dit ce qui est conservé/refait et **n'ajoute pas** de reprise : après échec avant injection, le site reste sur sa baseline vide, runner et copie de travail détruits ; un rejeu refait tout sous un **nouveau nom** ; pas de reprise sur copie non anonymisée conservée (`archive-reelle-4-notes.md` l.19, `README.md` l.35-40). Le diagnostic base seul évite de restaurer les fichiers pour apprendre une erreur SQL. Choix prudent documenté : acceptable.

### Tâche 5 — nettoyage de `imagine-test-a01-ced-02`
**Partiel, conforme au brief.** Le brief autorisait la suppression **seulement** après avoir vérifié par lecture l'absence de fichier/base issus de l'archive, « au moindre doute, laisse-le et dis-le ». Hermès ne le supprime pas : il ne peut pas établir l'absence d'injection sans lire la copie, ce que la doctrine lui interdit (`archive-reelle-4-notes.md` l.20, `README.md` l.41-42). C'est la branche prudente prévue par le brief. Reste à Ced de le vérifier/supprimer par l'API normale.

### Doctrine — assainissement des diagnostics / contrat natif
**Appliqué.** Aucune donnée réelle, aucun message/valeur/adresse dans les reçus (tests `test_archive_reelle_4.py:20-23,44,46-52`). L'outil natif partagé est touché (tâche 1 « les trois phases et du pont ») mais la nouvelle sortie se limite à ajouter une clé `failure` assainie ; les codes non reconnus retombent sur `STAGING_REFUSE`, le comportement historique.

---

## 2. Résultat des tests

Commande demandée, écrite exactement :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

**Non refusée** (le wrapper PowerShell direct l'a d'abord bloquée comme « processus imbriqué » ; relancée sans encombre par le Bash tool). Conteneur jetable T01, `network=none`, `rootfs=ro`, montage `wp` en lecture seule, `ports=none`, `cap-drop=ALL`, `no-new-privileges`, puis nettoyage avec absence vérifiée.

Dernière ligne (reportée telle quelle) :

```
REJEU : 1069 tests, 34310 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Les quatre bibliothèques sur mesure (`imagine-connecteur`, `imagine-non-regression`, `imagine-pilotage`, `imagine-site`) passent toutes, 0 échec.

**Écart de décompte expliqué, non régressif.** La note d'Hermès annonçait « 1 062 tests / 34 271 assertions » au dépôt du `PRET` (`archive-reelle-4-notes.md` l.11) ; je relève 1 069 / 34 310. Les 7 tests et 39 assertions de plus viennent **de la voie 2**, pas d'A-01 : depuis le commit du `PRET` (`5952ea1`), `wp/plugins/imagine-site` a reçu C-16/C-19 (`git diff 5952ea1..HEAD` : `TableauBordReglesTest.php` +28, `CommandeReglesTest.php` +9). `imagine-site` est balayé par `rejouer.ps1` mais est entièrement hors A-01. Aucun test A-01 n'est en échec.

**Limite inchangée, non régressive.** `rejouer.ps1` ne balaie que les quatre extensions sur mesure ; les tests propres à A-01 de cette passe (`wp/tests/a01-court/test_diagnostics.php` et les suites Python `test_archive_reelle_4.py`, `exercise_fourth.py`) **ne sont pas dans ce balayage** (0 occurrence dans la sortie), ni le natif `wp/outils/staging/*`. Ils restent **auto-déclarés par les conteneurs Docker d'Hermès** (reçus `archive-reelle-4/…`, `archive-reelle/5754d4a5d8b8` : 108 réussis/1 ignoré NTFS), hors de mes droits d'exécution. Inchangé par rapport aux tours précédents.

---

## 3. Régressions et modifications non demandées

- **Aucune régression décelée du code A-01.** Les cinq tâches sont tracées au brief ; la suite PHP partagée est au vert (0 échec). Les deux refus muets visés (`COMMAND_REFUSED` à l'import, `stderr=DEVNULL`) ont disparu.
- **Outil natif partagé modifié — mais demandé.** `command.php`, `lib.php`, `pdo-store.php` sont touchés, ce que la tâche 1 impose explicitement (« les trois phases et le pont »). La sortie n'ajoute qu'une clé `failure` assainie et un suivi de coordonnée ; les codes inconnus retombent sur `STAGING_REFUSE`. Risque inter-lots contenu, suite globale verte. À garder à l'œil si le moteur natif évolue.
- **Élargissement de grammaire en mémoire** (déjà signalé en n°5, mineur) : `sql_stream.py:236-240` mute `CREATE_WORDS` du parseur partagé importé (ajout `GENERATED/ALWAYS/AS/STORED/VIRTUAL/…`) et retire le suffixe `ROW_FORMAT` avant la validation ; en mémoire seulement, copie en conteneur, signalé. À documenter si le parseur partagé évolue. Non bloquant.
- **Code mort mineur, sans effet.** `publish.py:44` `wsl_python` garde un `if p.returncode: raise WSL_TRANSPORT_REFUSED` après un `execute(check=True)` qui aurait déjà levé : inatteignable, inoffensif.
- **Hors A-01, non committé / étranger.** `git status` montre du volume voie 2 (C-16 `imagine-site`, `wp/tests/a14/*`, `production/C-16/*`) et un fichier parasite à nom anormal (`prefix}u0024s`) : tous étrangers à cette vérification, à traiter dans leurs lots respectifs.

---

## 4. Verdict

**Prêt pour la clôture.**

Sur le fond, la quatrième passe d'A-01 est **conforme** : les cinq tâches du brief `A-01-archive-reelle-4.md` sont appliquées et citées — (1) refus muets éliminés, reçus assainis donnant étape + errno/SQLSTATE/ligne/instruction/table pour MariaDB et classe/fichier/ligne pour PHP, sans message ni valeur ; (2) compatibilité d'une vraie base (collations MySQL 8 par correspondance syntaxique, mode SQL de la source ou repli non strict, 64 Mio/256 Mio, JSON/colonnes générées/ROW_FORMAT/index préfixé, moteurs non-InnoDB préservés, objets exécutables refusés explicitement) avec son périmètre borné dit clairement ; (3) mode `--diagnose-database` base seule, runner jeté, aucun site ni fichier, en quelques minutes ; (4) reprise prudente décrite et volontairement non ajoutée ; (5) `imagine-test-a01-ced-02` laissé intact au moindre doute, comme le brief l'autorise.

La raison même du brief — un refus muet coûtant un aller-retour d'une heure à Ced — est **levée** : chaque échec externe, SQL, PHP et de délai porte désormais un reçu structuré et assaini. La suite PHP partagée passe au vert (1 069 tests, 0 échec) ; l'écart de décompte avec la note est entièrement imputable à la voie 2 (`imagine-site`), pas à A-01. Toutes les décisions étaient techniques ; **aucune question ouverte pour Ced** dans ce lot. Je ne relève ni régression, ni problème de fond restant.

**Réserves habituelles, non bloquantes.** La preuve propre à A-01 (diagnostic base seul, import de la vraie chaîne fictive, erreurs runtime synthétiques) reste **auto-déclarée par les conteneurs Docker d'Hermès** : inhérent au lot, assumé par le brief. Ce verdict vaut pour la **clôture d'un lot de code**, **pas un GO** (doctrine §3/§6) : ni import de l'archive d'Imagine, ni ouverture d'un staging aux agents. Ced seul relance l'import/diagnostic réel ; son rapport fera foi.
