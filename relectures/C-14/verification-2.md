# Vérification C-14 — contrôle après modification postérieure à la première vérification

Vérificateur : Claude. Date : 25 novembre 2026. Base relue : commit `ffa591e` (25/11 16:33), celui qui a déposé `relectures/C-14/verification.md`. État vérifié : `HEAD` + arbre de travail.
Méthode : `git diff ffa591e..HEAD` et `git log` par fichier sur `wp/` et `production/C-14/`, plus rejeu PHPUnit. Pas de relecture complète refaite (le code C-14 était déjà vérifié « prêt » au premier tour).

## Ce qui a changé depuis la première vérification

Le `git log` par fichier confirme que **tout le code et les tests C-14 sont figés avant la vérification** :
- `AchatNumero.php` : dernier changement `6caef49` (15:13).
- `AchatsNumeros.php`, `tests/AchatNumeroTest.php`, `c14-runtime.php`, `c14-unit.php`, `c14-corrections-*.php` : dernier changement `b52d01d` (15:43).

Tous antérieurs au commit de la vérification (16:33). `git diff ffa591e..HEAD -- production/C-14/` ne montre **qu'un seul changement C-14** : le fichier `PRET`, +2 lignes.

La seule modification d'Hermès postérieure à la première vérification est donc le **redépôt de `PRET`** (`production/C-14/PRET:5`, commit `764daf5`, 19:13) :
« Redepose voie 2 2026-11-25T19:12:36 : 17 empreintes du recu corrections recontrolees identiques. »

## 1. Consigne / arbitrage concerné

**1. Redéposer `PRET` après corrections (`docs/arbitrages-2026-11-25.md`, passage 16 h 30, § C-14 : « Le fichier `PRET` n'a pas été redéposé après les corrections… À redéposer »). → Appliquée.**
- `production/C-14/PRET:5` : ligne de redépôt horodatée 19:12:36, ré-attestation des 17 empreintes du reçu de corrections « recontrôlées identiques ». Le marqueur est maintenant plus récent que la fusion `corrections/C-14.md`, condition que l'arbitrage posait pour déclencher la vérification. `PRET:1-3` (contenu initial du parent) inchangés.

**2. Corrections de fond C14-01 / C14-02 / C14-03 (`corrections/C-14.md` §4, confirmées par `docs/arbitrages-2026-11-25.md` passage 16 h 30, § C-14). → Appliquées, inchangées depuis la première vérification.**
- C14-01 (numéro acquis fondé sur l'instantané figé, survit au catalogue) : `AchatNumero.php:27-33`, `AchatsNumeros.php:137,148-150`. Non modifié depuis.
- C14-02 (portée du remboursement réglable `imagine_achat_remboursement`, défaut prudent `commande`) : `AchatsNumeros.php:15,17,19,52,200`, `AchatNumero.php:13-16,20`. Non modifié depuis.
- C14-03 (état documentaire aligné) : `production/C-14/A-VOIR.md:3`, `RAPPORT.md:3-4`. Non modifié depuis.
- Ces trois points ont déjà le verdict « appliqué » de `verification.md` §1 ; aucun diff postérieur ne les touche. Rien à re-arbitrer.

**3. Le passage de 19 h 30 (`docs/arbitrages-2026-11-25.md`, § C-14) a déjà prononcé « code clos, validation visuelle de Ced attendue ».** Le redépôt de `PRET` est cohérent avec cette clôture de code ; il ne la contredit pas et ne vaut pas validation.

## 2. Résultat des tests

- **Rejeu PHPUnit de première main**, commande autorisée (conteneur jetable, réseau coupé, dépôt monté en lecture seule) :
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
  Dernière ligne : **`REJEU : 1012 tests, 34006 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`**
  (`T01_RESULT {"tests":1012,"assertions":34006,"failures":0,"errors":0,"skipped":0,"pass":true}`.)
  Chiffre **identique** à la première vérification (1012 / 34006) et au reçu `validation-corrections.json`. Inclut `AchatNumeroTest` du paquet `imagine-site`.
- **Recettes natives WP (`c14.py`, 686) et HTTP (`c14-http.py`) non rejouées** : elles exigent un site + une base, interdits au relecteur (doctrine §3). Chiffres **repris des reçus sans vérification indépendante** : C14 natif 686/686, non-régression 205/205. Même limite qu'au premier tour. Le redépôt de `PRET` n'ajoute aucun chiffre neuf : il ré-atteste les mêmes 17 empreintes.

## 3. Régressions et modifications non demandées

- **Aucun changement de code/test/doc C-14** depuis la première vérification : seule la ligne de redépôt de `PRET` a été ajoutée, ce que l'arbitrage du 16 h 30 demandait. Pas de régression C-14.
- **Bruit inter-lots (hors C-14)** : `git diff ffa591e..HEAD` sur `wp/` contient des fichiers d'autres lots synchronisés en parallèle (B-02, B-03, B-04, C-09, C-13, C-15 : `EcheancesRegles.php`, `b03-*`, `b04-work.py`, `c09-*`, `c13-*`, `c15-unit.php`, thème `reading.*`/`single.php`). Hors périmètre de cette vérification ; non évalués ici. Aucun ne touche `AchatNumero.php`/`AchatsNumeros.php`/`c14-*`.
- **Incident C-13 des 12 observations synthétiques** : déjà signalé et remonté au premier tour (`RAPPORT.md:32-36`, `incident-observations-c13.json`), inchangé. Sans effet sur C-14. À prendre en connaissance côté C-13.

## Verdict

**Prêt pour la clôture.**

La seule modification postérieure à la première vérification est administrative : le redépôt de `PRET` demandé par l'arbitrage du 25/11 (16 h 30), qui ré-atteste des empreintes identiques. Le code et les tests C-14 sont inchangés et conservent le verdict « prêt » du premier tour. Le rejeu PHPUnit de première main repasse (1012 tests, 0 échec), au même chiffre. Aucun problème de fond restant, aucune régression, aucune modification non demandée. Limite inchangée : les suites natives/HTTP ne sont de première main pour aucun relecteur, et deux questions « Pour Imagine » restent livrées en réglage à défaut prudent (ne bloquent pas).

Un verdict de vérification n'est pas un GO au sens de la doctrine §3.
