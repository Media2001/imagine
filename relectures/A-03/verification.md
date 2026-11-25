# Vérification A-03 — second et dernier tour

Date : 2026-11-25. Vérificateur : Claude. Base relue : état A-03 du 24/11 matin (`ce29ca9`). Objet : contrôler l'application de `corrections/A-03.md` après la reprise d'Hermès, relancer les tests, chercher toute régression. Ce n'est pas une nouvelle relecture complète.

Méthode : `git diff ce29ca9 HEAD` sur `wp/outils/bascule/a03/`, `wp/tests/a03-non-regression/`, `wp/plugins/imagine-non-regression/`, `wp/outils/bascule/non-regression.md` et `production/A-03/`. Lecture du code et des tests corrigés.

## 1. Application des instructions de `corrections/A-03.md` §4

**1. C1 — Représentativité de l'échantillon. → Appliquée.**
- Les comptes à capacités d'administration sont exclus du choix du représentant : `wp/outils/bascule/a03/Site.php:245-246` (`user_can('manage_options')` / `user_can('manage_woocommerce')` / `is_super_admin()` → `continue`).
- Fixture ajoutée : client ordinaire `a03-ordinary` (rôle `customer`), `wp/tests/a03-non-regression/seed.php:19-23` et export `ordinary`, `seed.php:81`.
- Banc : `wp/tests/a03-non-regression/inside.py:111` (`ordinary_not_admin_represents_none` : `none:none` pointe l'ordinaire, aucun `1:` dans `access`) et `inside.py:150-156` (`only_ordinary_right_changed_and_detected` : seul le droit du client ordinaire est altéré, régression détectée `anormal`).

**2. C4 — Erreurs de lecture SQL. → Appliquée.**
- Helper `read()` qui remet `last_error` à vide et lève `A03_SQL_READ` si une lecture échoue : `Site.php:169-177`.
- Garde-fou complémentaire dans le `wpdb` anonyme : toute `SELECT/SHOW/DESCRIBE/EXPLAIN` renvoyant `false` lève `A03_SQL_READ`, `Site.php:129-132`.
- Toutes les lectures de collecte sont enveloppées : abonnements `Site.php:201`, adhésions et utilisateurs `:229-231` et `:242`, droits `:270-272`, actions `:279-281`, commandes `:324-326`, renouvellement `:518` et `:527-531`. `START TRANSACTION READ ONLY` est désormais contrôlé (`Site.php:160-165`, `A03_TRANSACTION_FAILED`).
- Banc : table absente distinguée du vide légitime, `inside.py:129-147` (`nested_failed_read_cannot_be_cleared`, `sql_<section>_failure_is_not_empty`, `legitimate_empty_actions_accepted`).

**3. C5 — Écriture du rapport. → Appliquée.**
- `writeReport()` contrôle l'écriture complète et le `chmod`, nettoie et lève en cas d'échec, `Site.php:578-590` (`@file_put_contents(...) !== strlen($json) || !@chmod(...)` → `unlink` + `A03_OUTPUT_FAILED`). `mkdir` déjà contrôlé `:580-582`.
- Test de sortie dédié, cinq cas sans mutation du site : `wp/tests/a03-non-regression/output-boundary.php:24` (`write-failed`, `write-short`, `chmod-failed`, `success`, `mkdir-failed`), câblé dans `run.py:75-78` (`output_boundary`). Banc d'acceptance : refus de sortie en lecture seule, `inside.py:117-120`.

**4. C3 — `comparer` robuste. → Appliquée.**
- Validation de structure et de type par mode (photo vs `renewal_probe`) avant toute comparaison, refus avec `A03_REPORT_STRUCTURE` / `A03_REPORT_MODE` : `wp/plugins/imagine-non-regression/src/Report.php:32-81`, `:118-150`.
- La photo de référence doit contenir les sept pages, sinon refus : `Report.php:151-156`. La disparition d'une page est classée `anormal` (pas « à regarder ») : `Report.php:178`.
- CLI : toute exception devient `A03_COMPARE_REFUSED` code 1, sans fuite : `wp/outils/bascule/comparer:21-23` ; codes 0/2/3/1 conformes au mode d'emploi, `:20`.
- Tests : `wp/plugins/imagine-non-regression/tests/ReportTest.php` (`testMinimalReportsAreRefused`, `testDisappearingPageIsAnomalous`, `testIncompleteBaselineIsRefusedEvenIfPageAppearsAfterwards`, modes non interchangeables) et `unit.php:113-193` (dont le CLI `comparer`).

**5. C7 — Clés du comparateur. → Appliquée.**
- Validation de la forme des clés par section (IDs, couples d'IDs, slugs, mois, hooks) : `Report.php:83-116` (`validateKeys`/`keys`), appelée en fin de `validatePhoto` `:80`.
- Clés libres restantes masquées plutôt que recopiées : `Report.php:186-191` (`$root . '.[masque]'`). Le commentaire sur-promettant est corrigé : `Report.php:185` (« Free-form slug keys are never proof of anonymity »).
- Tests : `ReportTest.php:149-223` (`testKeysAreCheckedPerSectionWithoutEchoingThem`, `testSlugShapedPersonalKeysAndAllValuesAreMasked`) et `unit.php:143` (`section_keys_refuse_personal_names`).

**6. Banc autorisé (point de Claude). → Appliquée.**
- Logique pure portée en paquet découvrable T01 : `wp/plugins/imagine-non-regression/src/Report.php`, `/src/Policy.php`, avec `phpunit.xml` et `composer.json`. La découverte T01 ne scanne que les enfants immédiats de `plugins/`, `mu-plugins/`, `themes/` avec `phpunit.xml` : `wp/tests/t01/discovery.php:38-74` → le paquet est pris.
- Les anciens fichiers deviennent des points d'entrée de compatibilité : `wp/outils/bascule/a03/Report.php` et `/Policy.php` font `require_once` du paquet.
- `run.py:51` et `style.py:22` ajoutent le paquet à leurs cibles ; `phpunit.py` assert `packages[0]['relative'] == 'plugins/imagine-non-regression'`.

**7. C6 (nettoyage, pas métier). → Appliquée.**
- Canari `A03_PRIVATE_CONTENT_CANARY` retiré de la graine (`seed.php:7`, remplacé par un texte neutre) et de la liste de jetons du test `:privacy` (`inside.py:171`). Commentaire ajouté reversant l'étanchéité servie au lot paywall (`inside.py:170`).

**8. Mineurs. → Appliquée.**
- `sample_states` indexé par état (dictionnaire) pour réduire le bruit de diff : `Site.php:302-303` (`array_fill_keys(..., true)`) ; test `sample_state_dictionary_does_not_reindex` (`unit.php:166`).
- Étiquette de lot « A-01 » → A-02 : `non-regression.md:2` (« A-03 prolonge l'audit A-02 »), MU rattaché à `wp/outils/staging/` `:2`.
- Limite `php_error` confirmée et documentée : `non-regression.md:9`.
- Valeur avant/après dans `comparer` : choix maintenu de ne rien émettre (anti-PII), documenté `non-regression.md:6`. L'instruction disait « envisager » ; non-ajout acceptable.

**9. Preuves (lié au §5). → Appliquée.**
- Les deux arbres de preuves dupliqués sont supprimés (`production/A-03/preuve-finale/` et `/relecture-parent-a03/`), ainsi que `style.json` et `tdd.json`. Il ne reste dans `production/A-03/` que `PRET`, `notes.md`, `sources.md`.
- `run.py:25` et `style.py:30-33` écrivent désormais dans le scratch hors dépôt (`%LOCALAPPDATA%/hermes/cache/scratch/imagine-a03-runs/`), plus dans les livrables.

## 2. Résultat des tests

**Rejeu indépendant : non réalisé dans cette session — limite inchangée depuis le premier tour.**

- Le banc autorisé `wp/tests/rejouer.ps1` exige Docker dans WSL Ubuntu et l'image préparée `imagine-tests-t01:1`, construite par `preparer-image.ps1` (réseau, réservée à Ced). Idem pour `run.py` et `phpunit.py` (Docker/WSL + ZIP sous licence A-02).
- Dans cette session non interactive, l'exécution de `php`, `docker` et des scripts `.ps1` est refusée par la couche de permissions. Je n'ai donc pas pu relancer la suite moi-même. C'est exactement la limite commune du §3 de la fusion, toujours non levée.
- Déclaration d'Hermès (`production/A-03/PRET`, `notes.md:3`) : 115 tests PHPUnit / 246 assertions, 63 contrôles classique+HPOS, 10 purs/CLI, 5 cas du writer, lints PHP et PSR-12 verts — plus un rejeu parent le 25/11. **Ce sont ses propres artefacts, non re-vérifiés indépendamment par moi.**
- Ce que je peux affirmer par lecture statique : les tests ciblant les corrections existent et exercent bien les comportements corrigés (C1 représentativité, C4 lecture en échec ≠ vide, C5 écriture, C3 refus d'incomplet et page disparue, C7 clés et masquage). Leur passage reste à confirmer par un rejeu en environnement autorisé.

## 3. Régressions et modifications non demandées

- Aucune régression détectée dans le périmètre A-03. Les classements existants (versions = attendu, droits/états/actions = anormal, HTTP = à regarder, marqueur/erreur = anormal) sont préservés et verrouillés par `ReportTest::testExistingClassificationsRemainUnchanged`.
- Modification de support (non listée mais justifiée) à signaler à Ced : le `wpdb` anonyme ne neutralise désormais les ordres de transaction/DDL que pendant la sonde d'écriture (`Site.php:116-124`, garde `$this->probe`). En mode lecture seule, la défense repose sur `START TRANSACTION READ ONLY` (contrôlé) et sur le compte SQL `SELECT`/`USAGE` seul. Restructuration cohérente avec C4 (une lecture en échec doit lever avant qu'une API efface `last_error`) ; défendable, mais c'est une réduction de la garde en mémoire côté lecture — à garder à l'esprit.
- `run.py` gagne `--output-root` et n'écrit plus dans `production/A-03/` : c'est la bonne réalisation de l'instruction 9, pas un écart.
- Hors périmètre : le diff depuis `ce29ca9` contient aussi des changements d'autres lots (démo c11–c13, `staging-court`, `a01-court`) ; non évalués ici, sans rapport avec A-03.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les neuf instructions de `corrections/A-03.md` sont appliquées, y compris les importantes (C1, C4, C5, C3 et le banc autorisé). Aucun problème de fond de code ne subsiste côté Hermès ; aucune régression A-03 détectée.

Ce verdict n'est pas un GO et ne clôt pas le lot. Restent, côté Ced et non côté code :
1. les cinq questions ouvertes de `corrections/A-03.md` §5, sans réponse à ce jour (`notes.md:9`) — le lot touche des droits d'accès et le renouvellement, donc relève de Ced (doctrine §6) ;
2. le rejeu indépendant de la suite en environnement autorisé (Docker/WSL + image T01), que ni les relecteurs ni moi n'avons pu exécuter — à faire par Ced ou dans une session habilitée, comme preuve de clôture (fusion §3 et rappel final).
