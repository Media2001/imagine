# Vérification C-10 (2e tour) — L'écran de réglages

Date : 2026-11-23. Vérificateur, second et dernier tour.
Base : `corrections/C-10.md` (fusion) + `docs/arbitrages-2026-11-23.md` (A/B/C tranchés).
Méthode : `git diff` depuis la version relue (commit `4940767`, fusion) sur `wp/` et `production/C-10`, lecture du code corrigé, lecture des preuves de tests d'Hermès. Pas de relecture complète refaite.

Fichiers C-10 effectivement modifiés depuis la relecture :
`src/Administration/Reglages.php`, `src/Echeancier/ReglagesAdministration.php`, `phpunit.xml`, `tests/Administration/ReglagesTest.php` et `WordPressFictif.php` (nouveaux), `src/Administration/README.md`, `wp/plugins/imagine-site/Paywall.php`, les `c10-*.py/.php`, et `production/C-10/*`.

---

## 1. Instructions de `corrections/C-10.md`

### §4 — instructions numérotées

**1. (Bloquant) Tests PHPUnit de la façade + suite déclarée.** **Appliquée.**
- Suite `Administration` ajoutée : `phpunit.xml:9`.
- `tests/Administration/ReglagesTest.php` (10 tests, 67 assertions) + `tests/Administration/WordPressFictif.php` (banc Settings API).
- Couverture conforme à la demande : clés exactes acceptées/refusées pour Accès **et** Paiement avec conservation (`testClesExactesEtChoixStrictsConserventValeursPrecedentes` `:49`) ; journal écrit **une fois** après persistance, rien sur no-op ni sur refus (`testJournalUniqueApresPersistancePasSurNoopOuRefus` `:78`) ; première création journalisée une fois (`:99`) ; `apercuCsv()` relit le format persisté (`testApercuCsvRelitFormatPersiste` `:126`).
- Preuve d'exécution : `production/C-10/correction-final-unit.json` → `composer test` **exit 0**, et JUnit `correction-final-phpunit.xml` → **775 tests / 33 210 assertions / 0 échec**, dont la sous-suite `Administration` **10 tests / 67 assertions / 0 échec**. RED préalable conservé (`correction-red-unit.json` : `test_exit 1`), ordre test→code respecté.

**2. (Important) `page()` lit le Paiement via `->lire()`.** **Appliquée.**
`Reglages.php:250` : `Paiement::OPTION => (new Paiement())->options((new Paiement())->lire())`. Plus de `get_option()` brut. Assertion `testPageDelegueNonceEtLitPaiementNormalise` (`:134`) : avec une option Paiement vide, l'écran rend bien `value="avec_marge" selected`.

**3. (Important) Empêcher la persistance d'un `[]`.** **Appliquée.**
`ReglagesAdministration.php:63` : repli de `sanitiser()` sur `get_option(self::OPTION, $this->defauts())` au lieu de `[]`. Test du tout premier enregistrement avec clés exactes mais valeur de type invalide : `testPremierPaiementInvalideConserveDefautDeclare` (`ReglagesTest.php:69`).

**4. (Important) Phrase « conservé pour un branchement futur » sur Accès et Paiement + assertion.** **Appliquée, adaptée par l'arbitrage A pour Accès.**
- Paiement : `Reglages.php:267-270` « Ces valeurs sont conservées pour un branchement futur et ne modifient pas encore le paiement du site de démonstration. »
- Accès : le texte a changé de sens car l'arbitrage A **raccorde** désormais l'Accès au paywall. `Reglages.php:261-265` : « Ces trois réglages sont lus par le paywall… ». Cohérent avec l'arbitrage, pas un écart.
- Assertions : `ReglagesTest.php:143-144` vérifient les deux textes (`ne modifient pas encore le paiement`, `lus par le paywall`).

**5. (Important) Contrôler le retour de `add_option()` du journal ; sinon prévenir l'administrateur.** **Appliquée** (variante « léger » tranchée en arbitrage C).
`Reglages.php:143-172` : retour capturé dans `$written` ; en cas d'échec, l'écriture métier est **annulée** (`delete_option` si création, sinon `update_option($before)`), restauration relue (`wp_die 500` si elle échoue à son tour), et `add_settings_error('imagine_journal_indisponible')`. Tests `testJournalKoRefuseModificationEtPrevient` (`:107`) et `testJournalKoRefusePremiereCreationSansInventerOption` (`:118`). Aucun mécanisme de reprise : conforme au « léger » de l'arbitrage C.

**6. (Mineur) Isoler le test de clé surnuméraire + clé obligatoire retirée + cas mixte.** **Appliquée.**
`c10-verifier.py:164-166` : `extra` = domaine complet + une seule clé inconnue ; `missing` = retrait d'une seule clé obligatoire. Cas mixte ajouté `:175-186` (Accès invalide conservé + Paiement valide persisté, **un seul** événement journal). Doublé côté PHPUnit (`extra`/`missing`/`invalid` par domaine, `ReglagesTest.php:55-65`).

**7. (Mineur) Dédoublonner le défaut Paiement via un accesseur.** **Appliquée.**
`ReglagesAdministration.php:32-44` : nouveaux `defauts()` et `options(?Reglages)`, dérivés du moteur clos. Réutilisé dans `Reglages.php:45` (`(new Paiement())->defauts()`). Plus de défaut recodé en dur.

**8. (Mineur) Reformater PSR-12 + `composer lint`.** **Appliquée.**
Appels multilignes reformatés (`add_menu_page`/`add_submenu_page` `:50-66`, `add_settings_error`, chaînes longues scindées, boucle du journal `:321-326`). Preuve : `correction-final-unit.json` → `composer lint` **exit 0** ; RED `correction-red-unit.json` → `lint_exit 2`.

**9. (Mineur, non urgent) Mention « À confirmer par Imagine » pilotée par un état ouverte/tranchée.** **Appliquée.**
`Reglages.php:18-23` : constante `REGLES_OUVERTES` (huit clés à `true`). Rendu conditionné `:298-299`. Assertion : `ReglagesTest.php:145` compte exactement 8 mentions (les huit règles étant encore ouvertes aujourd'hui).

### §5 — arbitrages (tranchés dans `docs/arbitrages-2026-11-23.md`)

- **A — « un réglage doit agir sur le site ».** **Appliquée.** Les trois réglages Accès sont désormais lus par le paywall C-08 : `Paywall.php:deciderContenu()` passe `(new AdministrationReglages())->lire()` comme 6e argument de `Moteur::decider()` (paramètre `$reglages` déjà présent dans le moteur, `Acces/Moteur.php:11-18`). Effet front prouvé par HTTP (`c10-verifier.py:228-247`, article témoin 188 fermé→équipe→refermé, option seule changée entre les GET).
- **B — journal sans purge, 50 affichés.** **Appliquée.** Comportement conservé, textes d'écran mis à jour (`Reglages.php:313-314`).
- **C — échec journal : refus + avertissement, sans reprise.** **Appliquée** (cf. instruction 5).

---

## 2. Résultat des tests

- **Je n'ai pas pu relancer la suite moi-même.** En session non interactive, tout appel d'exécution (`docker`, `php`, `composer`, même `command -v`) est refusé faute d'approbation. C'est la limite déjà signalée au 1er tour ; l'arbitrage C-10 prévoit d'ailleurs que **T-01 rejoue** la suite PHPUnit. Je m'appuie donc sur les preuves livrées par Hermès, lues et contrôlées :
  - `composer test` : **775 tests, 33 210 assertions, 0 échec/erreur/ignoré** (`correction-final-unit.json` `test_exit=0` ; JUnit `correction-final-phpunit.xml`). Sous-suite `Administration` présente et verte : **10 tests, 67 assertions**.
  - `composer lint` : **exit 0**.
  - RED préalable cohérent (`correction-red-unit.json` : `test_exit=1`, `lint_exit=2`) → l'ordre test-d'abord est démontré pour les quatre régressions attendues.
  - Recette démonstration (hors de mes droits de rejeu) : 120 contrôles C10, 25 soumissions invalides, 30 non-régression C08, effet front réel, selon `notes.md` et `verification-finale.json`.
- Les tests runtime/HTTP visent le site `192.168.129.32:8085` : lus, non rejoués (accès site hors droits relecteur). Aucune des deux relectures ne vaut confirmation indépendante contre le site.

**Conclusion tests :** la couverture PHPUnit manquante — unique point bloquant du 1er tour — est **ajoutée et au vert** dans les preuves ; la logique pure de la façade est bien testée hors WordPress via le banc `WordPressFictif`.

---

## 3. Régressions et modifications non demandées

- **Dans le périmètre C-10 strict** (`Reglages.php`, `ReglagesAdministration.php`, `phpunit.xml`, tests) : chaque changement correspond à une instruction ou à un arbitrage. **Aucune modification non demandée, aucune régression repérée** à la lecture ; les 775 tests (dont la suite `Acces` qui exerce le moteur avec `$reglages`) restent verts, ce qui couvre le raccord Accès.
- **`wp/plugins/imagine-site/Paywall.php` — à signaler, sans alarme.** Ce fichier C-08 a été modifié. La part **C-10** est le seul raccord Accès (arbitrage A), expressément autorisé. Le reste du diff (mémoïsation par requête, masquage SQL de recherche `posts_search`/`posts_orderby`, JSON-LD `NewsArticle`, gardes `metadata_exists`, état `virement_non_valide`, rôle `imagine_referent_abonnements`) relève des **corrections C-08 et C-09**, groupées dans les mêmes commits de synchro. **Leur vérification n'appartient pas à C-10** et n'est pas refaite ici : elle revient aux tours C-08/C-09. Je le note pour éviter qu'un diff large soit lu comme du C-10.
- Le diff global `4940767..HEAD` contient aussi des fichiers B-01/C-08/C-09 (seeds, tests) étrangers à C-10, pour la même raison de synchro groupée. Non évalués ici.
- Validation **visuelle** de l'écran par Ced toujours attendue (normal, `PRET`/`notes.md`) : non couverte par le code ni par les tests.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les neuf instructions de la fusion et les trois arbitrages A/B/C sont appliqués ; le point bloquant du 1er tour (absence de tests PHPUnit de la façade) est levé, suite verte dans les preuves ; aucune régression ni modification non demandée dans le périmètre C-10. **Aucun problème de fond restant.**

Réserves, non bloquantes pour la clôture du code :
1. Je n'ai pas pu **rejouer** les tests (exécution refusée en session non interactive) ; la confirmation repose sur les preuves d'Hermès et sera rejouée par T-01.
2. La modification de `Paywall.php` porte aussi des corrections C-08/C-09 : leur vérification revient à ces lots.
3. Validation visuelle de l'écran par Ced toujours due.

**Rappel : ce verdict n'est pas un GO** au sens doctrine §3 ; il ne vaut que pour la clôture du lot de code C-10, sous réserve de la validation visuelle de Ced.
