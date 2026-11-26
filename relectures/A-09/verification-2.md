# Vérification A-09 — 3e tour (correction d'empaquetage du 26/11)

Date : 26 novembre 2026. Vérificateur : Claude. Objet : contrôler la seule correction
demandée depuis la vérification précédente (`relectures/A-09/verification.md`, verdict
« Remonte à Ced ») — la restriction du manifeste. Pas de relecture complète refaite.

Consigne justifiant la modification : `A-FAIRE.md` consigne 1 (« Manifestes d'A-09 et
d'A-08 : une correction d'empaquetage ») et arbitrage `docs/arbitrages-2026-11-26.md`
§ « A-09 — une correction, pas une question pour Ced ». Tous deux posent la même règle :
**un manifeste de lot n'épingle que les fichiers de son lot** ; jamais `A-FAIRE.md`,
`A-FAIRE-2.md`, `ETAT.md`, `JOURNAL.md`, `docs/`, `briefs/`, `prompts/`, ni les fichiers
d'un autre lot. « Retire ces entrées, rescelle, redépose `PRET`. Aucun code ne change,
pas de rejeu Docker : la preuve est `verifier.py` à code 0. »

Méthode : `git log`/`git diff` sur `production/A-09` et `wp/` entre l'état de la dernière
vérification (`56bc091`, synchro 22:18) et HEAD ; diff des clés du manifeste ; exécution
de `verifier.py` (lecture seule) ; rejeu de la suite PHP.

---

## 1. Consigne / arbitrage concerné

**Consigne 1 d'`A-FAIRE.md` + arbitrage A-09 du 26/11 — restreindre le manifeste aux
fichiers du lot. → Appliquée.**

Diff des `sources` du manifeste (`production/A-09/manifeste.json`), `56bc091` → HEAD.
Sept entrées hors-lot retirées, exactement celles que la règle interdit :

- `A-FAIRE.md` (feuille de route globale — la cause du rouge précédent) ;
- `briefs/A-09-test-des-redirections.md` (`briefs/`) ;
- `corrections/A-09.md` ;
- `doctrine/doctrine.md` (`docs`/doctrine) ;
- `prompts/consigne-permanente.md` (`prompts/`) ;
- `files/rapports/2026-11-25-21h08.md`, `files/rapports/2026-11-25-22h11-A09.md`.

Ajout : `production/A-09/seal-packaging-26nov.py` (le script de reseal, fichier du lot —
légitime). Aucune entrée d'`evidence` retirée ni ajoutée.

Sources restantes : uniquement `production/A-09/*` (fichiers du lot) et le livrable réel
`wp/outils/bascule/a09/check.py`, `tester-redirections`, `tester-redirections.md`,
`plan-redirections.exemple.csv`, `wp/tests/a09/{run,test_check,test_http}.py`
(7 fichiers de code `wp/`, `runtime_source_files: 7`). Le fichier partagé du mode d'emploi
d'audit ne figure pas ici (A-09 n'y touche pas) : rien à contrôler par contrat pour ce lot.

Le reseal est tracé : `seal-packaging-26nov.py` (politique « own-lot paths only »,
`runtime_and_tests_unchanged`), reçu `verification-manifestes-26nov.json`
(`removed_counts.sources: 7`, `exit_code: 0`), `PRET` redéposé le 26/11 à 02:44 avec le
nouveau SHA de manifeste `facf55ae…`.

---

## 2. Résultat des tests

- **`python -B production/A-09/verifier.py`** (contrôle pur, lecture seule, sans Docker) :
  **exit 0**. `manifest_sha256` = `facf55ae3f17…` cohérent avec le `PRET` ; preuve scellée
  `a1671ceb23d2`, 28 tests, `production_authorized: false`. Le garde-fou qui retournait
  `exit 1 — hash drift: A-FAIRE.md` au tour précédent **passe désormais au vert**. C'est la
  preuve exigée par la consigne.
- **Suite PHP** — `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
  (le lanceur PowerShell du harnais a refusé le processus imbriqué ; relancée via l'outil
  Bash, commande identique). Dernière ligne :
  `REJEU : 1077 tests, 34327 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`.
  Réserve inchangée depuis la relecture : cette suite est **PHP (T01)** et **ne couvre pas**
  A-09, qui est un paquet Python. La couverture du lot repose sur la preuve scellée Docker
  (28 tests), relue au tour précédent. Aucun code A-09 n'a changé depuis.

---

## 3. Régression / modification non demandée

Aucune. `git log` ne montre **aucun commit touchant `wp/outils/bascule/a09`,
`wp/outils/bascule/tester-redirections*`, ni `wp/tests/a09` depuis `4e148f3` (22:08)**,
c.-à-d. antérieur à la vérification de code du tour précédent : la logique R1/R2/R3 et les
tests sont strictement ceux déjà validés. Le reseal n'a touché que des fichiers de
`production/A-09/` (manifeste, `PRET`, script de reseal, reçu). L'assertion de non-dérive
des fichiers possédés dans `seal-packaging-26nov.py` et l'`exit 0` de `verifier.py`
confirment que les sources `wp/` sont byte-identiques à leurs empreintes.

Aucun secret, aucune donnée réelle, aucun accès à un site, une base ou un compte, aucun
GO production. L'exemple CSV reste à trois lignes fictives.

---

## 4. Verdict

**Prêt pour la clôture.**

L'unique motif du « Remonte à Ced » précédent — `verifier.py` à `exit 1` à cause de
`A-FAIRE.md` épinglé dans le manifeste — est levé. La correction demandée par la consigne 1
et l'arbitrage du 26/11 est appliquée exactement : sept fichiers d'orchestration/hors-lot
retirés des `sources`, rescellement tracé, `PRET` redéposé, et `verifier.py` revient à
**code 0** sur l'arbre courant. Aucun code n'a changé, aucun rejeu Docker n'était requis,
aucune régression ni modification non demandée. Les trois corrections de fond (R1/R2/R3),
déjà prouvées au tour précédent, sont intactes.

---

*Rappel doctrine : ce verdict de vérification n'est pas un GO (§3, §6).*
