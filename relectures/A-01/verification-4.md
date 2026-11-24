# A-01 — Vérification n°4 (après la correction « archive réelle 2 » d'Hermès)

Vérificateur : Claude Code (NUC). Date : 24/11/2026.
Objet : contrôler les modifications apportées à A-01 **depuis** `relectures/A-01/verification-3.md` (committée au `c6be375`, synchro 23/11 16:33). Ce n'est pas une relecture complète neuve.

**Ce qui justifie ces modifications.** Le brief `briefs/A-01-archive-reelle-2.md` (voie 1, « passe avant tout », demi-journée), déclenché par le diagnostic réel lancé par Ced le 24/11 : la commande n'avait jamais vu la forme d'une vraie archive All-in-One WP Migration. Cinq volets : A format réel + préfixe `.`, B plafonds réalistes, C secrets là où ils sont, D exclusion des fichiers à données personnelles, E diagnostic lisible. **Aucun arbitrage `docs/arbitrages-*.md` nouveau sur A-01** : les trois fichiers d'arbitrages (21, 22, 23/11) ne portent pas sur ce brief ; la doctrine « rejouable / non-régression / standard d'abord » reste la référence. Section courante de `production/A-01/notes.md` : « archive-reelle-2 » (24/11).

**Méthode.** `git diff c6be375..HEAD` sur `wp/` et `production/A-01`. Code A-01 touché : `archive.py` (+219/-), `archive_policy.py` (nouveau), `core_source.py` (+33), `diagnosis.py` (+55), `inside.py` (~99), `publish.py` (+81), `run.py` (+2/-1), `sql_diagnostic.py` (nouveau), `sql_stream.py` (nouveau). Tests : `test_archive_reelle_2.py` (nouveau), `prepare_ai1wm.py`, `exercise_ai1wm.py`, `verify_ai1wm_final.py`, `ai1wm_*`, `test_native_file_policy.php` (nouveau). Reçus lus : `archive-reelle-2-final.json`, `archive-reelle-2-livraison.json`, `archive-reelle-2-rapport.md`, `archive-reelle-2/{2b2c796bf78b,8f6e3d24930d,da5698b02266}`, `archive-reelle-2-public/public-source.json`, `PRET`, `notes.md`.

---

## 1. Consignes et arbitrages — Appliqué / Non appliqué / Partiel

### Volet A — lire le format réel, normaliser le préfixe `.`, tester sur de vraies archives
**Appliqué.**
- Préfixe `.` / `./` de la racine AI1WM normalisé **en tête seulement** : `archive.py:95-101` (`archive_path` : `.`/`./` → `''`, `./x` → `x`). Un segment `.` ou `..` **à l'intérieur** reste refusé et compté : `archive.py:113-116` (`ARCHIVE_PATH_DOT`, `ARCHIVE_PATH_PARENT`). Le refus `ARCHIVE_DATABASE_MISSING` en chaîne disparaît quand la racine est lue (`database.sql` reconnu, `archive.py:167-168,188`).
- En-têtes v1 (chemin 4096) et v2 (chemin 4088 + CRC32) : `archive.py:15-27` (`header_fields`) ; EOF nul ou v2 : `archive.py:30-35` (`eof_block`) ; CRC d'entrée vérifié quand présent : `archive.py:224-232`.
- Sources publiques citées (AI1WM 7.109, paquet épinglé par SHA-256, fichiers `class-ai1wm-*`) : `production/A-01/notes.md` (section « Sources publiques effectivement lues ») et `archive-reelle-2-public/public-source.json`. Archives de test produites par la vraie extension (grosse : 32 455 entrées, 1,51 Go, SQL 169 Mo) : reçu `archive-reelle-2/2b2c796bf78b/qualification-89a75913.json`.

### Volet B — plafonds réalistes, lecture en flux, garde d'espace disque
**Appliqué.**
- Défauts **50 Gio / 2 000 000 entrées / 8 Gio base** : `archive_policy.py:5-7` (`DEFAULT_MAX_BYTES`, `DEFAULT_MAX_ENTRIES`, `DEFAULT_MAX_SQL_BYTES`).
- Réglables en ligne de commande : `publish.py:511-513` (`--max-bytes`, `--max-entries`, `--max-sql-bytes`, `type=int`), passés au diagnostic (`diagnosis.py:209,277`) et à l'import (`publish.py:524`).
- Lecture en flux par blocs de 1 Mio, sans chargement global : `archive.py:217-230` (`CHUNK`) ; SQL borné par instruction, jamais tokenisé en mémoire : `sql_stream.py`.
- Garde d'espace disque **avant toute création** : `archive.py:44-49` (`DISK_SPACE_INSUFFICIENT`, marge 256 Mio) et `publish.py:62-65` (`before_any_creation:True`, contrôle du vrai `DockerRootDir`).
- Diagnostic affiche taille totale, nombre d'entrées, taille de base : `diagnosis.py:307` / `format_summary`.

### Volet C — secrets : chercher là où il y en a
**Appliqué.**
- Fichiers : seuls les **candidats de configuration propres au site** (`.php/.json/.env/.ini` hors `plugins/`, `themes/`, exports exclus, `package.json`/`database.sql`) : `archive_policy.py:37-44` (`secret_candidate`). Médias et code public non recherchés.
- Résultat en **avertissement, jamais refus** : `diagnosis.py:232,238` (`SECRET_OU_IDENTIFIANT`, `blocking=False`).
- Base inchangée : secrets SQL signalés en avertissement `SOURCE_SECRET_NEUTRALISABLE` (`diagnosis.py:202`, `sql_stream.py:182`) ; neutralisation native inchangée.

### Volet D — fichiers à données personnelles : ne pas les restaurer
**Appliqué.**
- Liste d'exclusion par défaut (wpallexport, wpallimport, memberships_csv_*, wc-logs, wpdesk-logs, ur-logs, matomo, wpdm-cache, journaux, sauvegardes, archives hors années datées) : `archive_policy.py:9,20-34` (`EXCLUDE_UPLOADS`, `excluded`).
- `woocommerce_uploads` / `simple-file-list` : PDF et images gardés, autres types fermés : `archive_policy.py:10-11,32-33` (`KEEP_UPLOADS`, `MEDIA`).
- Octets des exclus **ni lus ni extraits** : `archive.py:206-211` (`skip_payload` saute par `seek`) et `archive.py:359`.
- Dossier d'uploads inconnu → **refus avec son nom**, fermé par défaut : `archive_policy.py:14-17` (`unknown_upload`) + `archive.py:204-205` et `restore` `archive.py:358` (`UPLOADS_DIRECTORY_REVIEW_REQUIRED`) ; nom de dossier préservé pour décision : `archive.py:65-68` (`location`).
- Rapport zone/nombre/octets exclus : `archive.py:206-209,153` (`excluded_zones`) ; traitement natif respectant médias conservés : `wp/tests/a01-court/test_native_file_policy.php`, `publish.py:690`.

### Volet E — un diagnostic lisible
**Appliqué.**
- Résumé d'un écran (statut + une ligne par règle avec cinq premières zones, inventaire extensions/thèmes, dossiers d'uploads nombre/taille, exclus) : `diagnosis.py:306-319` (`format_summary`) ; résumé mesuré à 15 lignes au reçu courant.
- Inventaire extensions/thèmes/uploads construit au parcours : `archive.py:147,153,195-203`.
- Détail complet seulement sur `--detail` : `publish.py:509,527-528,534` (`--detail` réservé au diagnostic, sinon résumé).

### Doctrine — rejouable / historique préservé / outil partagé intact
**Appliqué.** Ancien PRET déplacé intact (`PRET-archive-reelle-23nov-historique-avant-archive-reelle-2.txt`) ; reçus antérieurs conservés, non requalifiés (`archive-reelle-2-final.json`). Aucun fichier de l'outil partagé `wp/outils/staging/*` ni traitement natif modifié (hors `files.php`/`test_native_file_policy.php` prévus par le brief). `run.py:47-48` n'ajoute que les nouveaux modules (`archive_policy.py`, `sql_stream.py`) au paquet du runner — cohérent avec le brief, pas une modification hors sujet.

---

## 2. Résultat des tests

Commande demandée, écrite exactement :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

**Non refusée** : la commande s'est bien exécutée (conteneur jetable T01 créé, `network=none`, `rootfs=ro`, montage `wp` en lecture seule, `cap-drop=ALL`, puis nettoyage avec absence vérifiée).

**Mais la suite PHP échoue — elle ne porte pas sur A-01.** Le runner s'arrête sur :

> `T01 PHP ERROR : Image dependencies stale or absent for plugins/imagine-non-regression/composer.json; Ced must run preparer-image.ps1.`

`plugins/imagine-non-regression` est un **lot A-03** (non-régression, consigne n°1 de `A-FAIRE.md`), introduit par les synchros du 24/11 16:38–16:53, **étranger à A-01**. Son `composer.json` n'est pas couvert par l'image T01 préparée ; le runner interrompt alors **toute** la suite PHP partagée. Ce n'est pas un échec du code A-01 ; mais je ne peux donc **pas** rejouer localement le seul test PHP d'A-01 de ce brief (`test_native_file_policy.php`).

Dernière ligne de la commande (reportée telle quelle) :

```
REJEU : 0 tests, 0 assertions, 0 échecs, 1 erreurs, 0 ignorés — FAIL
```

Les preuves PHP d'Hermès (données natives, lint, `test_native_file_policy.php`) restent **auto-déclarées par ses conteneurs**, comme aux tours précédents ; la résolution passe par `preparer-image.ps1`, action réservée à Ced (réseau autorisé pendant la seule préparation). Les suites Python d'A-01 ne sont pas couvertes par `rejouer.ps1` et n'ont pas été demandées à ce tour.

---

## 3. Régressions et modifications non demandées

- **Aucune régression du code A-01.** Les cinq volets ajoutent `archive_policy.py`, `sql_stream.py`, `sql_diagnostic.py`, `core_source.py` et densifient `archive.py`/`diagnosis.py`/`publish.py`/`inside.py` ; tout est tracé au brief. La normalisation `.` n'affaiblit pas les refus (traversée, `.` intérieur, antislash, contrôles, doublon, collision, lien, pilote : `archive.py:104-136,255`).
- **Pas de modification non demandée dans A-01** : `run.py` se borne à embarquer les nouveaux modules ; aucun fichier de l'outil partagé `wp/outils/staging/*` touché.
- **Blocage inter-lots à signaler (pas une régression A-01).** Le lot A-03 (`plugins/imagine-non-regression/composer.json`) rend l'image T01 partagée **périmée** et casse le point d'entrée PHP commun `rejouer.ps1` pour tous les lots. À relever comme écart : la suite PHP de référence est actuellement rouge tant que Ced n'a pas relancé `preparer-image.ps1`.
- **Gros volume hors A-01 dans les mêmes synchros** (voie 2, A-02, A-03), comme au tour n°3 : ne relève pas de cette vérification.

---

## 4. Verdict

**Remonte à Ced.**

Sur le fond, le code d'A-01 est **conforme** : les cinq volets du brief `A-01-archive-reelle-2.md` (A format réel + préfixe `.` ; B plafonds réalistes et garde disque ; C secrets limités aux configurations, en avertissement ; D exclusion des exports/journaux sans les lire, dossier inconnu refusé avec son nom ; E diagnostic d'un écran avec `--detail`) sont appliqués et cités, sans régression ni modification non demandée.

Mais je **ne peux pas certifier la clôture**, pour deux raisons liées :

1. **La suite PHP demandée est en échec** et n'a pas pu être rejouée : `rejouer.ps1` s'arrête sur une image T01 périmée (`FAIL`, dernière ligne reportée ci-dessus). La condition doctrinale « tests au vert » (§6) n'est pas vérifiable localement par moi.
2. La cause est **hors A-01** — le `composer.json` du lot A-03 (`imagine-non-regression`) — et sa résolution exige une action de Ced (`preparer-image.ps1`), hors des droits d'exécution du relecteur.

Rien ici ne révèle un défaut du code archive-reelle-2 ; le blocage est d'outillage partagé et inter-lots. **Action attendue de Ced** : relancer `wp/tests/preparer-image.ps1`, puis rejouer `rejouer.ps1` ; si la suite repasse au vert (y compris `test_native_file_policy.php`), A-01 est prêt pour la clôture sous les réserves habituelles.

**Rappel doctrine (§3/§6).** Ce verdict ne vaudrait, même au vert, que pour la clôture d'un lot de code. **Ce n'est pas un GO** : ni l'import de l'archive d'Imagine, ni l'ouverture d'un staging aux agents. Ced seul relance le diagnostic réel (commande en tête de `notes.md`) ; aucun résultat statique ne vaut staging vérifié.
