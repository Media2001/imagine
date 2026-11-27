# Vérification B-09 — second et dernier tour

Vérificateur : Claude. Objet : contrôler l'application de `corrections/B-09.md` par Hermès après la fusion. Pas de relecture complète refaite.

Base comparée : état relu (commit `ca853df0`, rapport `relectures/B-09/claude.md`) → corrections d'Hermès, portées par les commits `fb635773` (08 h 28, tests) et `b5a13209` (08 h 33, code + preuves). `production/` n'est pas suivi par Git : son contenu est lu sur disque (preuves 08 h 35 → 08 h 51, postérieures au correctif).

## 1. Instructions de corrections/B-09.md

**1. R1 — scan des marqueurs détachés / hors option — APPLIQUÉE.**
`wp/outils/demo/b09-seed.php:99-119`. Nouveau balayage SQL direct de tous les `post_id` portant `imagine_b09_menu_item` (`$wpdb->get_col`, l. 101), indépendant du rattachement et de l'option. Vérifie type `nav_menu_item`, marqueur unique et connu, absence de rattachement étranger, conflit d'ID avec `$owned` et avec l'option (`$prior['items']`) ; refuse l'ambiguïté (`throw`, l. 116) ; réutilise l'ID (`$owned[$key] = $id`, l. 118). Erreur de lecture traitée (l. 102-104). Conforme à l'instruction.

**2. R1 — test de l'interruption entre marqueur et option — APPLIQUÉE.**
`wp/outils/demo/b09-corrections.py` (nouveau) : arrêt réel `exit(73)` déclenché sur le hook `added_post_meta` au marqueur `contact`, **avant** l'écriture de l'option et le rattachement (l. 20-21), puis reprise dans un nouveau processus. Contrôles `interruption_entre_marqueur_et_option`, `id_marque_hors_option_reutilise`, `aucun_orphelin_ni_doublon`, `rejeu_idempotent`. Preuves disque : `corrections-red-seed.json` (ancien code : orphelin/doublon → rouge) et `corrections-green-seed.json` (code corrigé → vert). La coupure priorité 99 critiquée dans la fusion est bien remplacée par une coupure au marqueur (priorité 10).

**3. R2 — fin d'effacement conditionnée à la disparition vérifiée des métadonnées — APPLIQUÉE.**
`wp/plugins/imagine-site/ContactConfidentialite.php:46-99`. Témoin durable non autoloadé `imagine_contact_effacement_<sha256(adresse)>` écrit **avant** suppression et relu (l. 47-57, aucune copie du texte ni de l'adresse). Après chaque tentative, lecture SQL directe des clés `imagine_contact_*` via `self::metas()` (l. 93-99) — ni jointure sur le post disparu, ni cache. Condition de succès durcie : `done = $remaining === [] && !items_retained && get_option($option) === []` (l. 85). Erreur de lecture SQL → `null` → échec, jamais liste vide. Reprise d'un effacement partiel sans post ni email (l. 66-70). Conforme.

**4. R2 — test de suppression partielle — APPLIQUÉE (deux niveaux).**
- PHPUnit : `wp/plugins/imagine-site/tests/ContactAdapterTest.php:135` `testSuppressionPartielleRefuseSuccesEtReprendSansPostNiEmail` (ajouté en `fb635773`, +25 l. ; stubs `ContactWPStubs.php` +16 l.). Post disparu mais méta texte survivante → `done=false`. Présent au vert dans le JUnit archivé (`corrections-final-unit.log`, l. 23).
- Natif : `wp/outils/demo/b09-correction-live.py::partial` : filtre `delete_post_metadata_by_mid` qui laisse survivre la seule méta `imagine_contact_texte` ; contrôles `jamais_done_si_meta_survit`, `nettoyage_refuse_reste_incomplet`, reprise par un autre processus. Preuve disque `corrections-effacement-natif.json` (5 contrôles verts).

**5. R3 — espace après les casts (fichiers B-09 neufs) — APPLIQUÉE.**
`Contact.php:26, 90, 123` et `ContactConfidentialite.php:32` : `(string) get_post_meta(...)`, `(int) ($pages...)`, `(string) ob_get_clean()`. Vérifié : plus aucun cast collé dans ces deux fichiers. Les occurrences restantes (`Agenda.php`, `Cooperative.php`, `Sujet*.php`…) appartiennent à des lots clos et sont hors périmètre, conformément à l'instruction (« sur les nouveaux fichiers »).

Les deux défauts techniques de la fusion sont respectés : duplication Contact/Sujet et succès par comparaison de chaîne **laissés tels quels** ; aucun fichier `Sujet*` modifié (vérifié : absents du commit de correction).

## 2. Résultat des tests

Je n'ai **pas pu relancer la suite en direct** dans cette session : le lanceur sanctionné `wp/tests/rejouer.ps1` (Docker/WSL, conteneur réseau coupé) et `php` sont bloqués par la garde d'exécution de l'environnement (approbation refusée). PowerShell simple fonctionne ; l'exécution de binaires externes, non. Je me suis donc appuyé sur les preuves archivées produites par Hermès **après** le correctif.

- **PHPUnit imagine-site** (`corrections-final-unit.log`) : `OK (7 tests, 203 assertions)`, PHP 8.2.33, 0 échec / 0 erreur / 0 ignoré. Inclut les deux tests nouveaux (suppression partielle l. 135, et le détail l. 160).
- **Rejeu complet** (`corrections-final-regression.json`) : `exit = 0`, `pass = true`, **1 167 tests / 36 333 assertions**, 0 échec / 0 erreur / 0 ignoré ; outils 22 / 584 contrôles, 0 échec. Commande enregistrée : `powershell.exe -File wp/tests/rejouer.ps1` ; log tracé par sha256.
- **Mutations** (`corrections-final-mutations.json`, `corrections-final-mutant-meta.log`) : mutants attendus rouges, dont le retrait de la relecture des métas (R2) et les injections REST/recherche.
- **Recette native** (`corrections-recette.json`) : 31 contrôles HTTP/natifs verts, aucun transport du contact, effacement ciblé.

Cohérence confirmée : compteurs du `PRET` (08 h 51) = ceux du JSON de rejeu ; `exit 0` ; hachages de log présents. **Réserve honnête : evidence archivée examinée, non ré-exécutée par moi.**

## 3. Régressions ou modifications non demandées

- **Aucune régression B-09.** Les fichiers touchés se limitent au périmètre des 5 instructions plus leurs tests/preuves. Suite complète au vert (archivée).
- **Hors B-09, dans le même commit `b5a13209`** : `wp/tests/a32/inside.py` (+2) et `wp/tests/a32/run.py` (±1) — travail propre à **A-32** (normalisation d'attachements, resserrement du `chmod a-w`), embarqué par le commit de synchro horodaté, sans toucher aucun fichier B-09. À signaler, mais étranger au lot.
- **Échec paquet A-32** (`A32_PARTIAL_EVIDENCE`, 1 seul échec du rejeu) : hors périmètre B-09, déjà acté par les deux relecteurs et par le `PRET`. Le PRET B-09 ne certifie pas A-32. Non imputable à ce correctif.
- `relectures/A-26/verification-2.md` ajouté dans le même commit : document d'un autre lot, sans effet sur B-09.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions sont appliquées fidèlement et au bon endroit ; les deux défauts techniques sont respectés ; aucune régression ni modification non demandée **dans B-09** ; l'évidence de tests archivée est verte et cohérente. Aucun problème de fond restant sur le lot.

Deux réserves, non bloquantes :
1. Je n'ai pas ré-exécuté la suite moi-même (garde d'exécution de la session). Pour la ceinture et les bretelles, un seul rejeu live côté Ced : `.\wp\tests\rejouer.ps1` (attendu : exit 0, 1 167 tests).
2. Ce verdict ne couvre pas le visuel (pied de page, pages vides), les textes juridiques, ni les points « Pour Imagine » / « À arbitrer par Ced » de la fusion, qui restent ouverts et hors du code.

Rappel doctrine : **un verdict de vérification n'est pas un GO.**
