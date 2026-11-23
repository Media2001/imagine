# Vérification T-01 — 2e et dernier tour (Claude, vérificateur)

Objet : contrôler que `corrections/T-01.md` a été appliqué par Hermès, relancer les tests, repérer toute régression. Pas de relecture complète refaite.

Méthode : `git diff e69930f..HEAD` sur `wp/tests/rejouer.ps1`, `wp/tests/preparer-image.ps1`, `wp/tests/t01/*` et sur `production/T-01/` (e69930f = dernier état du code avant corrections, celui que les deux relecteurs ont lu). Lecture du code corrigé. Contrôle de cohérence interne des preuves d'Hermès.

**Réserve d'exécution (identique aux deux relecteurs).** Je n'ai pas pu relancer la suite moi-même : cet environnement refuse WSL/Docker, les processus PowerShell enfants et la réflexion .NET en session non interactive. La seule preuve d'exécution reste celle produite par Hermès sur le NUC. Le vérificateur `wp/tests/t01/verifier-t01.py` est versionné et rejouable : **Ced peut le relancer** (`python .\wp\tests\t01\verifier-t01.py`) pour obtenir lui-même le reçu.

---

## 1. Instructions de `corrections/T-01.md` — état

### Instruction 1 (T01-C1) — pas de conteneur après un kill dur — **Appliquée**
- Balayage des orphelins **en début de run** : `wp/tests/rejouer.ps1:14` (`Remove-T01Orphans`), défini dans `wp/tests/t01/commun.ps1:67-79`. Il n'agit que sur l'étiquette `org.imagine.t01` (`:69`), inspecte, prouve la propriété avant `rm -f`, puis prouve l'absence.
- Le double levier `--rm` n'est **pas** exigé : l'arbitrage Ced retient « balayage seul » (`docs/arbitrages-2026-11-23.md` §T-01-3). Choix respecté ; `notes.md:17` l'assume (« aucune promesse de suppression immédiate après coupure »).
- Test d'interruption réelle : `wp/tests/t01/test-interruption.ps1` tue réellement un parent PowerShell (`:25`), constate l'orphelin (`:27`), exerce le balayage (`:29`) et vérifie qu'un conteneur à **étiquette différente** est préservé (`:32-33`). Preuve : `preuves/final-interruption.log` → `PASS`.
- Robustesse liée : `$created` est positionné **avant** `docker create` (`rejouer.ps1:26`), donc le nettoyage couvre aussi un objet créé quand `create` renvoie une erreur.

### Instruction 2 (T01-C2) — le garde-fou doit refuser `<exclude>` — **Appliquée**
- `verifyCoverage()` est passé en **liste blanche fermée** : `wp/tests/t01/executer.php:59-84`. Toute balise (`:65`), tout attribut (`:74`) ou tout enfant (`:80`) hors grammaire comprise lève une exception. `<exclude>` déclenche `Unsupported PHPUnit selection element: exclude`.
- Tests négatifs : `wp/tests/t01/corrections-php.php:79` (« refuses exclude directory », niveau unité) **et** `:210-214` (« real replay with exclude fails before PHPUnit » : `errors=1`, `tests=0`, échec **avant** `T01 COMMAND`). Preuves : `final-php-corrections.log:5` et `:35` → `PASS`.
- Couvre aussi groupes, préfixe/version, suffixe restrictif, `defaultTestSuite`, sélecteur inconnu (`corrections-php.php:78-93`). `notes.md:13` le documente.

### Instruction 3 (S1) — montage réduit à `wp/` — **Appliquée**
- `wp/tests/rejouer.ps1:20` monte `$wpRoot = <dépôt>/wp` ; `:27` cible `/repo/wp` en `readonly`. `Assert-T01Isolation` impose `Destination -eq '/repo/wp'` et un **seul** montage (`commun.ps1:85-87`).
- L'entrypoint `/repo/wp/tests/t01/executer.php` et la découverte `/repo/wp` (`executer.php:120`) résolvent toujours. Preuve : `final-rejeu.log` → `mount=/mnt/c/Users/Ced/imagine/wp:/repo/wp:ro`. `.git`, `docs`, `briefs` sont désormais hors du conteneur.

### Instruction 4 (T1) — cas de contrat manquants — **Appliquée**
- `wp/tests/t01/test-rejeu.ps1:13` ajoute `argument`, `unsafe-path`, `unsafe-ports`, `unsafe-label` (plus `create-error`, `skipped`). Doubles dans `mock-wsl.ps1:17-22,31-33,41`.
  - Refus d'argument → `rejouer.ps1:12` (cas `argument`).
  - Chemin WSL non conforme → `rejouer.ps1:24` (cas `unsafe-path`, mock renvoie `relative,path`).
  - Refus par `ExposedPorts` → `rejouer.ps1:18` (cas `unsafe-ports`), **séparé** de `Volumes` (`unsafe-image`).
  - Label d'image incohérent → `rejouer.ps1:18` (cas `unsafe-label`).
- Preuve : `final-contrat.log` → `T01 CONTRACT : 18/18 PASS`.

### Instruction 5 (C1) — expliciter l'interprétation du périmètre — **Appliquée**
- `production/T-01/notes.md:7-11` pose le choix comme assumé (trois racines `plugins/`, `mu-plugins/`, `themes/` ; sous-dossier avec `phpunit.xml`/`.dist` ; fixtures de `wp/tests/` exclues) et nomme explicitement l'angle mort (`:11` : pas de paquet imbriqué arbitrairement ailleurs sous `wp/`).

### Instruction 6 (D1) — provenance des reçus — **Appliquée**
- `livraison-verifiee.json` est **sorti des preuves courantes** : il ne vit plus que dans `production/T-01/historique/avant-corrections-20261123/livraison-verifiee.json`.
- Le reçu faisant foi est `preuves/final-verification.json`, **généré par un script versionné** `wp/tests/t01/verifier-t01.py:79`. Documenté dans `notes.md:5` et `:19`.

---

## 2. Résultat des tests

**Non relancés par moi** (réserve d'exécution ci-dessus). Preuves d'Hermès contrôlées cohérentes entre elles :

| Preuve | Résultat |
|---|---|
| `final-rejeu.log` | `REJEU : 802 tests, 33367 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS` |
| `final-contrat.log` | `T01 CONTRACT : 18/18 PASS` |
| `final-isolation.log` | `T01 REAL ISOLATION : PASS` |
| `final-discovery.log` | `T01 PREPARATION DISCOVERY : 2/2 PASS` |
| `final-php-corrections.log` | `T01 CORRECTIONS : 32 tests, 0 failures` (dont refus `<exclude>` et échec sur `skipped`/`incomplete`) |
| `final-interruption.log` | `T01 INTERRUPTION : PASS` (orphelin balayé, voisin préservé) |
| `final-verification.json` | `ready: true` ; tous `exit_code: 0` ; `summary_valid: true` ; `owned_containers_remaining: []` ; `cleanup_verified: true` ; `immutable_libraries_and_runner_unchanged: true` |

Le total 802 est cohérent (connecteur 37 + pilotage 765) ; `verifier-t01.py` rejoue les six bancs en **séquentiel** (`:65-66`, pour que le balayage n'atteigne jamais un banc frère vivant), re-hache les bibliothèques et scripts avant/après (`:58,:67-68`) et vérifie l'absence d'orphelin par étiquette (`:69-70`).

---

## 3. Régressions ou modifications non demandées

Aucune régression détectée.

- **Extension du périmètre aux trois racines** (`wp/tests/t01/discovery.php`, `Get-T01Packages` dans `commun.ps1:5-26`, `preparer-image.ps1:15,18`) : va au-delà des six instructions, mais **autorisée et traçable** par l'arbitrage Ced `docs/arbitrages-2026-11-23.md` §T-01-1. Pas une modification non demandée.
- **Tests ignorés = échec** (`executer.php:157` drapeaux `--fail-on-skipped`/`--fail-on-incomplete` ; `executer.php:192` ; `rejouer.ps1:44` `skipped -gt 0`) : conforme à l'arbitrage §T-01-2. Résout le mineur T2.
- `rejouer.ps1:48` passe de `if errors==0` à `if errors==0 and failures==0` : évite de forcer `errors=1` sur un FAIL qui porte déjà des `failures` ; affine la cohérence PASS/FAIL, pas une régression.
- `preparer-image.ps1:25` ajoute `.Replace('\','/')` avant `wslpath` : robustesse, cohérent avec le montage `wp/`.
- **Logique métier intacte** : T-01 n'altère aucun calcul ; les empreintes SHA des bibliothèques sont inchangées (`final-verification.json` `immutable_libraries_and_runner_unchanged: true`) et `notes.md:19` le confirme.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les six instructions de `corrections/T-01.md` sont appliquées, les quatre arbitrages (§5) sont tranchés, enregistrés (`docs/arbitrages-2026-11-23.md`) et implémentés, les preuves sont au vert et cohérentes, aucune régression ni question ouverte ne subsiste.

Une seule réserve, de **méthode** et non de fond : aucun des deux relecteurs ni moi n'avons pu exécuter la vraie suite dans notre environnement ; la preuve d'exécution est celle d'Hermès. Elle est rejouable par Ced via le script versionné `python .\wp\tests\t01\verifier-t01.py` (code 0 attendu). Un verdict de vérification n'est pas un GO au sens du §3 de la doctrine.
