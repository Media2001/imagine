# A-01 — Vérification n°3 (après la correction « archive réelle » d'Hermès)

Vérificateur : Claude Code (NUC). Date : 23/11/2026.
Objet : contrôler les modifications apportées à A-01 **depuis** `relectures/A-01/verification-2.md` (committée au `46aae00`, synchro 10:38). Ce n'est pas une relecture complète neuve.

**Ce qui justifie ces modifications.** Le brief `briefs/A-01-archive-reelle.md` (voie 1, « passe avant tout »), déclenché par le premier import réel lancé par Ced le 23/11 à 13 h 41 : refus `ARCHIVE_PATH` muet au prévol (`production/A-01/publication-23nov/8876588e7c6a/result.json`). Deux défauts à corriger : (1) le refus ne dit rien d'exploitable ; (2) la règle est plus stricte que la réalité (collision de casse, `:` refusés à tort). Pas d'arbitrage `docs/arbitrages-*.md` nouveau sur A-01 : les arbitrages du 23/11 portent sur T-01, B-00, B-01. La doctrine « rejouable / non-régression / standard » reste la référence.

**Méthode.** `git diff 46aae00..HEAD` sur `wp/` et `production/A-01`. Fichiers A-01 touchés : `archive.py` (+246), `diagnosis.py` (nouveau, 306 l.), `publish.py` (+46), `inside.py` (+10), tests `test_archive_reelle.py` (nouveau, 29 cas), `exercise_archive_reelle.py`, `exercise_archive_refusal.py`, `verify_archive_reelle.py`, `test_archive.py` (+6), `test_qualification_receipts.py` (+25), `verify_publication.py`. Reçus lus : `publication-23nov/{8876588e7c6a (ancien refus), 2196d0dea030 (refus corrigé)}`, `archive-reelle/{946da1e537e3, refusal-c4473bce2038}`, `tests-21nov/c6a70d1458cb`, `archive-reelle-final.json`, `notes.md`, `PRET`, `PRET-qualification-23nov-historique-avant-archive-reelle.txt`.

---

## 1. Consignes et arbitrages — Appliqué / Non appliqué / Partiel

### Brief A — diagnostic complet en une passe, lecture seule
**Appliqué.**
- Mode `--diagnose` : `publish.py:486-491`. Garde CLI : exige `--operator-ced --archive`, refuse mot de passe / self-test / `--case` (`publish.py:487-488`). Sortie 1 si blocages, 0 sinon, 2 pour CLI invalide (argparse).
- Lecture seule intégrale, aucune reprise au premier refus : `diagnosis.diagnose` (`diagnosis.py:208`) s'appuie sur `archive.audit` qui parcourt **toute** l'archive en flux inerte (`archive.py:84`), agrège par règle (`Findings`, `archive.py:22`). Reçu `read_only=True, created_sites=[], downloads=0, extracted_files=0` (`diagnosis.py:278`).
- Zone + extension, **jamais le basename** : `location()` (`archive.py:13`) ne rend que les deux premiers segments autorisés (`plugins/<dossier>`, `uploads/<année>`…) et une extension connue. Tables : nom de table et colonnes, jamais de valeur (`TABLE_PERSONNELLE_A_TRANCHER` colonnes seules, `diagnosis.py:150`).
- Synthèse finale blocages vs avertissements : `Findings.report` → `blockers` / `warnings` (`archive.py:38`). **Prouvé** sur archive fictive : `archive-reelle/946da1e537e3/result.json` (CLI exacte, `network=none`, 0 écriture/socket).
- Refus **ordinaire** (sans `--diagnose`) nomme la règle, le nombre et la zone du premier cas : `refusal_summary` (`publish.py:453`), affiché dans `refusals` (`publish.py:772`). **Prouvé** : reçu corrigé `2196d0dea030` → `ARCHIVE_PATH_BACKSLASH`, `count:2`, zone `uploads/2026`, ext `.jpg`, sans nom de fichier (vérifié par lecture directe du JSON). À comparer à l'ancien `8876588e7c6a` qui ne rendait que `code: ARCHIVE_PATH`.

### Brief B — assouplir le légitime, garder ce qui protège, un test par cas
**Appliqué.**
- **Casse** : `ARCHIVE_PATH_CASE_ONLY` passe en avertissement compté (`archive.py:127`), accepté seulement après **vraie sonde** du système de fichiers cible — création/lecture/suppression de deux noms ne différant que par la casse dans le répertoire cible lui-même (`probe_case_sensitive`, `archive.py:176`). Cible insensible ou non éprouvée → refus (`ARCHIVE_CASE_INSENSITIVE_TARGET` / `ARCHIVE_CASE_SENSITIVITY_UNVERIFIED`). Doublon **strictement identique** toujours refusé (`ARCHIVE_PATH_DUPLICATE`). La sonde est faite sur le **vrai `wp-content` monté** avant transfert : `publish.py:261-264`.
- **`:`** accepté, avertissement (`ARCHIVE_PATH_COLON`, `archive.py:75`) ; `C:/…` reste refusé (`ARCHIVE_PATH_DRIVE`, `archive.py:55`).
- **`\` et contrôles** : refusés par défaut, comptés et localisés (`ARCHIVE_PATH_BACKSLASH` `:63`, `ARCHIVE_PATH_CONTROL` `:65`). Recommandation en trois lignes présente en clair dans `notes.md` (section « Recommandation pour antislashs et contrôles »).
- **Refus fermes conservés** : absolu, segment vide / `.` / `..`, hors dossier cible (collision fichier/répertoire, `ARCHIVE_PATH_FILE_DIRECTORY_COLLISION`), lien symbolique (`ARCHIVE_TARGET_SYMLINK`, `archive.py:180,211,284`), `wp-config.php`/`wp-admin`/`wp-includes`/`wp-content` à la racine (`ARCHIVE_LAYOUT_UNSUPPORTED`, `archive.py:69,278`).
- **Un test par assouplissement + cas d'attaque voisin** : `test_archive_reelle.py` — `test_colon_preserved_but_drive_refused`, `test_identical_duplicate_rejected_even_linux`, `test_symlink_case_neighbor_is_refused_before_writes`, `test_real_case_insensitive_host_refuses_case_only`, `test_all_attack_neighbors_remain_blocking`, `test_inserted_parent_symlink_cannot_escape_restoration`.

### Brief C — ne pas ouvrir l'archive d'Imagine, archives inventées
**Appliqué.** `archive-reelle-final.json` : `no_real_archive:true`, `no_real_import:true`, `no_site_created:true`, `no_host_php:true`, `no_commercial_account_used:true`, `new_full_publication_executed:false`. C'est Ced qui relancera, d'abord avec `--diagnose`.

### Livrables du brief
**Appliqués.** Commande `--diagnose` exacte en tête de `production/A-01/notes.md` (bloc PowerShell + lecture du résultat + chemins assouplis/refusés) ; `production/A-01/PRET` présent et à jour.

### Doctrine — rejouable / non-régression / pas de blanchiment
**Appliqué.** Ancien `PRET` déplacé intact (`PRET-qualification-23nov-historique-avant-archive-reelle.txt`, empreinte consignée). Les reçus de qualification antérieurs ne requalifient plus les empreintes courantes : `historical_current_source_status: "STALE_SOURCE_REFUSED"` ; `test_qualification_receipts.py` passe en mode `HISTORICAL_SCHEMA_ONLY` (sans statut PASS), couvert par 2 tests de plus qu'au tour n°2 (10 au lieu de 8). Aucun reçu historique modifié, aucun ancien FAIL blanchi.

---

## 2. Résultat des tests

Rejoués par moi en local (Windows, Python 3.14, lecture seule) :

| Suite | Résultat |
|---|---|
| `test_archive_reelle.py` | **21/29 OK, 8 branches Linux différées** (skipped) |
| `test_qualification_receipts.py` | **10/10 OK** |
| `test_core_selection.py` | **4/4 OK** |
| `test_publication.py` | **8/8 OK** |
| `test_publication_preflight.py` | **7/7 OK** |
| `test_arbitrations.py` | **6/6 OK** |
| `test_corrections.py` | **4/4 OK** |
| `test_password_stdin.py` | **5/5 OK** |

Les 8 cas « skipped » de `test_archive_reelle.py` sont les branches qui exigent un vrai système de fichiers Linux / un lien Unix / le runner `network=none` (sonde de casse positive, CLI système, liens). C'est exactement le décompte annoncé par le `PRET` (« 8 branches Linux différées »). La branche **négative** importante tourne bien chez moi : `test_real_case_insensitive_host_refuses_case_only` passe sur le disque Windows insensible à la casse — la collision de casse y est refusée.

**Intégrité code ↔ preuve.** Les empreintes SHA-256 des fichiers livrés sont **identiques** à `command_sources` du reçu de remise et des reçus archive-reelle :
`archive.py c5b6dab4…`, `diagnosis.py f1f63598…`, `publish.py 64c9771f…`, `inside.py e0d66939…`, `test_archive_reelle.py e9bd12a8…`. Le code relu est bien celui qui a produit la preuve.

**Non rejoué par moi** (hors droits d'exécution du relecteur : Docker, Linux) : `test_archive.py` (tests internes au runner, chemins `/opt/court` — échouent hors conteneur, comme aux tours précédents) ; les 8 branches Linux ; les reçus live `archive-reelle/946da1e537e3`, `2196d0dea030`, `refusal-c4473bce2038`, la régression native `tests-21nov/c6a70d1458cb` (18 PASS). Ils restent **auto-déclarés par la commande**, comme aux tours précédents ; le premier import réel, lancé par Ced, fera foi. Limite assumée par le brief, pas un défaut.

---

## 3. Régressions et modifications non demandées

- **Aucune régression A-01.** Outil partagé et modèles inchangés : les scripts natifs `wp/outils/staging/*` et `worker.py` portent les mêmes empreintes dans l'ancien (`8876588e7c6a`) et le nouveau reçu ; `tool_sources_unchanged:true`. L'ancien chemin `restore` est conservé dans `_restore_payload` (`archive.py:201` → audit complet avant toute écriture), rétro-compatible.
- **`inside.py:231` — fusion de `FAILURE_STAGES`.** Le nouveau bloc `**{code: 'archive_restore' for code in ARCHIVE_REFUSALS}` précède l'ancien dict littéral. `ARCHIVE_REFUSALS` est un sur-ensemble portant la même valeur ; pas de changement de comportement. Détail de refus (`exc.detail`) remonté au reçu sans texte d'exception brut (`inside.py:268`).
- **`diagnose` ne fait pas la sonde de casse** (lecture seule) : il annonce le contrôle différé `TARGET_FILESYSTEM_CASE_PROBE_BEFORE_RESTORE` et `full_staging_ready:false` (`diagnosis.py:280-283`). Une collision de casse ressort donc en **avertissement** au diagnostic ; la décision ferme est reportée à l'import, qui sonde réellement (`publish.py:263`). Conforme au brief, documenté dans `notes.md`. Ce n'est pas une régression.
- **Modifications hors périmètre A-01, à signaler (pas une régression A-01).** Les mêmes commits de synchro embarquent un gros volume de la **voie 2 et de A-02** : thème `wp/themes/imagine/*`, `wp/plugins/imagine-site/*`, `wp/outils/demo/*`, `wp/tests/demo/*` (B-00, B-01, C-08, C-09, C-10) et `wp/tests/a02-audit/*`. L'arbre de travail non suivi (`git status`) porte aussi du C-10 (`wp/plugins/imagine-pilotage/…`, `production/C-10/red-runtime.json`, `wp/tests/demo/c10-runtime.php`). Rien de tout cela ne touche le code de production A-01 ni les scripts natifs partagés ; ces lots relèvent de leurs propres vérifications, pas de celle-ci.

---

## 4. Verdict

**Prêt pour la clôture.**

Les trois volets du brief `A-01-archive-reelle.md` (A : diagnostic en une passe lecture seule ; B : assouplir casse et `:` sans ouvrir de brèche, sonde réelle de la cible, refus fermes conservés ; C : archives inventées uniquement) sont appliqués et cités. Le refus `ARCHIVE_PATH` muet est corrigé : règle précise, nombre de cas, zone et extension, sans jamais exposer de nom de fichier (prouvé par le reçu `2196d0dea030`). Les tests rejouables sont au vert (21/29 + 7 suites), le reste des branches est différé Linux comme annoncé. L'intégrité code ↔ preuve est confirmée par empreintes. Aucune régression A-01 ; l'historique est préservé sans blanchiment (`STALE_SOURCE_REFUSED`).

**Rappel doctrine (§3/§6).** Ce verdict ne vaut que pour la clôture d'un lot de code. **Ce n'est pas un GO** : ni l'import de la production d'Imagine, ni l'ouverture d'un staging aux agents. Le `PRET` le dit lui-même (« Ced seul lancera le diagnostic réel ; le résultat statique ne vaut jamais staging vérifié »). Le premier import réel reste à Ced, par un GO écrit nommant la tâche, et son rapport sera relu avant toute ouverture. Les lots voie 2 / A-02 embarqués dans les mêmes commits sont à vérifier dans leurs propres lots.
