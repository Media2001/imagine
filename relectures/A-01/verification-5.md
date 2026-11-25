# A-01 — Vérification n°5 (après la troisième passe « base réelle » d'Hermès)

Vérificateur : Claude Code (NUC). Date : 25/11/2026.
Objet : contrôler les modifications apportées à A-01 **depuis** `relectures/A-01/verification-4.md` (committée au `a60771a`, synchro 24/11 22:33). Ce n'est pas une relecture complète neuve.

**Ce qui justifie ces modifications.**
- Brief `briefs/A-01-archive-reelle-3.md` (voie 1, trois heures, « passe avant A-04 »), déclenché par le diagnostic réel relancé par Ced le 25/11 à 13 h 15. Six décisions, **toutes techniques**, prises par Claude dans le brief (« elles ne touchent aucune règle métier ») : D1 table inconnue vidée en structure seule, D2 décisions par famille en JSON versionné, D3 lignes d'une table vidée non analysées / littéraux BLOB acceptés pour les tables gardées, D4 deux dossiers d'uploads exclus, D5 neutralisation complétée extension par extension, D6 confirmation de l'anonymisation AS/commentaires/options.
- Arbitrage `docs/arbitrages-2026-11-25.md`, section « A-01, troisième passe — rendue, pas encore relue » : **Stripe désactivée sur la copie confirmée** ; plafond de relecture porté à huit (`scripts/relire.ps1`), qui débloque cette vérification.
- Arbitrage `docs/arbitrages-2026-11-25.md`, section « A-01 — archive réelle, deuxième reprise » : quand un lot ajoute un paquet de tests, **Hermès relance lui-même `wp/tests/preparer-image.ps1`** avant `PRET`. Ici aucun paquet Composer nouveau (`PRET` l.24) : image existante appropriée. C'est ce qui lève le blocage du tour n°4.
- `A-FAIRE.md` consigne 1 : la troisième passe passe avant tout, Ced l'attend pour relancer son diagnostic.

**Méthode.** `git diff a60771a..HEAD` sur `wp/` et `production/A-01`. Code A-01 touché : `archive_policy.py` (+1), `diagnosis.py` (+57), `inside.py` (~8), `politique-tables.json` (nouveau), `run.py` (+3), `sql_diagnostic.py` (~84), `sql_stream.py` (+148), `table_policy.py` (nouveau), **outil natif partagé** `staging/lib.php` (+26), `staging/policy.php` (+11). Tests : `test_archive_reelle_3.py`, `test_database_policy.php`, `database_fixture.php`, `database_verify_inside.py`, `exercise_database.py`, `verify_database_delivery.py` (nouveaux) + retouches `test_archive_reelle.py`, `exercise_archive_reelle.py`. Notes et reçus lus : `archive-reelle-3-notes.md`, `archive-reelle-3-final.json`, `archive-reelle-3/580210112ffe/result.json`, `PRET`.

---

## 1. Consignes et arbitrages — Appliqué / Non appliqué / Partiel

### D1 — une table inconnue est vidée (structure seule), plus de conservation ouverte par défaut
**Appliqué.**
- Défaut `vider` pour toute table hors catalogue et hors famille : `table_policy.py:32-36` (`resolve`). Le diagnostic émet `TABLE_STRUCTURE_SEULE` (non bloquant) au lieu de l'ancien `TABLE_INCONNUE_CONSERVEE` ouvert ; `TABLE_DECISION_EXPLICITE` seulement quand une décision écrite garde/anonymise : `sql_diagnostic.py:44-47` (`check_schema`).
- `TABLE_PERSONNELLE_A_TRANCHER` ne subsiste que si une décision demande `garder` : `sql_diagnostic.py:48-50`. Côté natif, même règle plus un nouveau garde `TABLE_STRUCTURE_NON_VIDE` si une table marquée `vider` arrive peuplée au bootstrap : `staging/lib.php:613-622`.
- Test : `test_archive_reelle_3.py:30-44` (familles datées + inconnue `email` → videe par défaut, aucun blocage, `FICTION_PRIVATE` absent du SQL restauré) et `:55-61` (garder une table personnelle reste bloquant tant qu'on n'anonymise pas).

### D2 — décisions par famille, fichier versionné, le cas ponctuel l'emporte
**Appliqué.**
- `wp/outils/staging-court/politique-tables.json` **version 1**, familles `matomo_*`, `ahm_*`, `fsmpt_*`, `wf*`, `pmxi_*`, `pmxe_*`, journaux `*_log(s)` — toutes en `vider`. Chargé et validé strictement : `table_policy.py:8-16` (refus `TABLE_POLICY_REFUSED` si altéré).
- `--table-decisions` (décision exacte par nom de table) l'emporte sur la famille : `table_policy.py:28-31`. Les 185 tables ne sont pas tranchées une par une.

### D3 — les lignes d'une table vidée ne sont pas analysées ; littéraux BLOB acceptés pour les tables gardées
**Appliqué.**
- INSERT d'une table `vider` sautés **lexicalement en flux**, sans décodage ni scan de valeurs : `sql_stream.py` `Framer.discard` (l.36-70) + `Validator.skip_insert` (l.~160). Préfixe exact résolu par une **première passe structure seule** avant de choisir les INSERT conservés : `sql_stream.py` `validate_file` (l.~290, `schema_only=True` puis seconde passe) et côté diagnostic `diagnosis.py:227-247` (deux passes bornées sur `database.sql` seul, jamais de `seek` dans un fichier exclu).
- Tables gardées : littéraux `_binary'…'`, `0x…`, `X'…'` et échappements NUL/CR/LF/TAB/BS/Z acceptés et réémis en hex : `sql_stream.py` `binary_hex`, `HEX`, `BINARY`, jeton `hex` (l.5-20, 178-199). Test `test_archive_reelle_3.py:46-53`.
- Cas restant refusé **dit explicitement** : charsets autres, littéraux de bits, expressions/fonctions SQL, commentaires au milieu des INSERT, instruction > 16 Mio (`archive-reelle-3-notes.md` l.56). Framer borné prouvé sur littéral géant : `test_archive_reelle_3.py:63-72`. Faux préfixe (`…fiction_users` avant `…options`) couvert : `:97-104`.

### D4 — deux dossiers d'uploads à exclure
**Appliqué.** `memberships_profile_fields` et `download-manager-files` ajoutés : `archive_policy.py:9` (`EXCLUDE_UPLOADS`). Test `test_archive_reelle_3.py:74-77`.

### D5 — neutralisation complétée, extension par extension (tableau des 22)
**Appliqué.**
- `staging/policy.php:8-18` ajoute `worker/init.php` (prise de contrôle ManageWP), `wordfence/wordfence.php`, et les handlers de webhook `woocommerce-gateway-stripe` ; `fluent-smtp` (l.22) et `matomo` (l.36) déjà présents, All-in-One Migration en `backup` (l.29).
- Tâches planifiées d'export/import supprimées : `staging/lib.php:335-337` (actions AS dont le hook commence par `pmxi_`/`pmxe_`/`wp_all_import|export`/`woe_`/`woo_order_export`).
- Tableau risque/traitement des 22 extensions : `archive-reelle-3-notes.md` l.24-47.

### D6 — avertissements `SOURCE_SECRET_NEUTRALISABLE` : confirmer l'anonymisation
**Appliqué.**
- Options d'adresse opérationnelle (`admin_email`, `new_admin_email`, `woocommerce_email_from_address`, `woocommerce_stock_email_recipient`) remplacées par `imagine-test-admin@example.org` : `staging/lib.php:397-402`. `SOURCE_SECRET_NEUTRALISABLE` reste un **avertissement** (`sql_stream.py:275-278`).
- Confirmation écrite du traitement des arguments/journaux d'actions planifiées et des auteurs de commentaires : `archive-reelle-3-notes.md` l.49-50.

### Diagnostic — résumé par famille + disque nécessaire/disponible
**Appliqué.** `diagnosis.py:325-333` (`table_families`, `unclassified_tables`, `table_policy_version`, `disk_space` requis/disponible) ; `format_summary` masque les lignes `TABLE_STRUCTURE_SEULE`/`TABLE_DECISION_EXPLICITE` et ajoute les lignes « Tables », « Hors familles », « Disque » : `diagnosis.py:348-358`. Test `:106-110`. L'espace affiché est celui du filesystem du diagnostic ; le contrôle du moteur Docker reste refait avant restauration (`disk_space.scope`).

### Arbitrage — Stripe désactivée sur la copie
**Appliqué.** `staging/policy.php:16-18` retire les handlers Stripe ; réglages conservés scrubés en mode test sans clé (comportement `lib.php` existant). Conforme à l'arbitrage du 25/11.

### Doctrine — rejouable / historique préservé / contrat natif préservé pour les autres appelants
**Appliqué.** Reçus antérieurs non requalifiés (`PRET` l.34-35). Le contexte natif transmet désormais les décisions effectives et la version de politique : `inside.py:189,209`. La nouvelle règle « vider par défaut » dans le moteur natif est **gardée par `table_policy_version === 1`** (`staging/lib.php:54-62`), donc les appelants hors de cet importeur conservent leur contrat historique.

---

## 2. Résultat des tests

Commande demandée, écrite exactement :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

**Non refusée** : la commande s'est exécutée (conteneur jetable T01, `network=none`, `rootfs=ro`, montage `wp` en lecture seule, `ports=none`, `cap-drop=ALL`, `no-new-privileges`, puis nettoyage avec absence vérifiée).

Dernière ligne (reportée telle quelle) :

```
REJEU : 1012 tests, 34006 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Le blocage du tour n°4 (image T01 périmée par le `composer.json` d'A-03) a **disparu** : A-03 est clos, aucun nouveau paquet Composer dans cette passe, l'image existante convient. Les quatre bibliothèques natives couvertes (`imagine-connecteur`, `imagine-non-regression`, `imagine-pilotage`, `imagine-site`) passent toutes. Le compte 1012 tests / 34006 assertions concorde avec le `PRET` (l.23).

**Limite inchangée, non régressive.** `rejouer.ps1` ne balaie que les quatre extensions sur mesure ; les tests PHP propres à A-01 de ce brief (`wp/tests/a01-court/test_database_policy.php`, `test_native_file_policy.php`) et les suites Python d'`a01-court` **ne sont pas dans ce balayage** (recherche dans la sortie : 0 occurrence). Ils restent **auto-déclarés par les conteneurs d'Hermès**, comme à chaque tour (reçus `archive-reelle-3/…`), et exigent Docker — hors de mes droits d'exécution. Les tests Python d'A-01 que je peux lancer localement n'étaient pas demandés à ce tour.

---

## 3. Régressions et modifications non demandées

- **Aucune régression décelée du code A-01.** Les six décisions sont tracées au brief ; la suite PHP partagée (y compris A-03 `imagine-non-regression`) est au vert.
- **Outil natif partagé modifié — mais demandé.** `wp/outils/staging/lib.php` et `policy.php` ont été touchés, ce que le tour n°4 n'avait pas constaté. C'est explicitement la décision D5 du brief (« vérifie, extension par extension, … et complète »). Le risque de régression inter-lots est contenu par le garde `table_policy_version === 1` (`lib.php:54-62`) qui préserve le contrat des autres appelants, et la suite globale verte le confirme. À garder à l'œil si le moteur natif évolue.
- **Hors A-01, non committé.** `git status` montre `M wp/tests/a04/inside.py` (modification du plan de travail non committée, lot **A-04**, absente de `HEAD`) : étranger à cette vérification, à traiter dans A-04.
- **Volume hors A-01 dans les mêmes synchros** (bascule A-03/A-04, voie 2) : comme aux tours précédents, ne relève pas de cette vérification.

---

## 4. Verdict

**Prêt pour la clôture.**

Sur le fond, le code d'A-01 troisième passe est **conforme** : les six décisions du brief `A-01-archive-reelle-3.md` (D1 inconnue vidée en structure seule ; D2 familles en JSON versionné, cas ponctuel prioritaire ; D3 lignes vidées sautées lexicalement, BLOB/hex/échappements acceptés pour les tables gardées, préfixe résolu en deux passes ; D4 deux exclusions d'uploads ; D5 neutralisation complétée worker/Wordfence/Stripe/SMTP/Matomo/exports ; D6 anonymisation AS/commentaires/options confirmée) sont appliquées et citées, plus le résumé par famille, le disque et la désactivation de Stripe de l'arbitrage du 25/11.

L'unique raison qui m'avait fait « remonter à Ced » au tour n°4 — la suite PHP partagée en échec sur une image périmée — est **levée** : `rejouer.ps1` passe au vert (1012 tests, 0 échec). Toutes les questions du brief étaient techniques, tranchées par Claude ; **aucune question ouverte pour Ced** dans ce lot. Je ne relève ni régression, ni problème de fond restant.

**Réserves habituelles, non bloquantes.** La preuve propre à A-01 (diagnostic sans refus, deux restaurations hors ligne, tables inconnues présentes et vides) reste **auto-déclarée par les conteneurs Docker d'Hermès** : inhérent au lot, assumé par le brief. Ce verdict vaut pour la **clôture d'un lot de code**, **pas un GO** (doctrine §3/§6) : ni import de l'archive d'Imagine, ni ouverture d'un staging aux agents. Ced seul relance le diagnostic réel (commande en tête de `archive-reelle-3-notes.md`) ; son rapport fera foi.
