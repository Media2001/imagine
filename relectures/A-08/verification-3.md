# Vérification A-08 — tour n° 3 (après la correction d'empaquetage du manifeste)

Date : 26 novembre 2026. Vérificateur : Claude (lecture seule sur le code ; rejeu de la suite PHP
autorisée ; `verifier.py` du lot lancé, car il est strictement en lecture seule — voir §2).
Base comparée : version de `verification-2.md` (`eeccf64`, 26/11 01:33) → `HEAD`.
Je **ne refais pas** de relecture complète : je contrôle uniquement ce qu'Hermès a changé depuis
`verification-2.md` et je rejoue.

Ce qui justifie la modification : **A-FAIRE.md, consigne 1** (« Manifestes d'A-09 et d'A-08 : une
correction d'empaquetage… un manifeste n'épingle que les fichiers de son lot »), confirmée par
**`docs/arbitrages-2026-11-26.md:19-25`** (passage de 1 h 30, section A-09, points 1 à 3 : « Même
remarque du vérificateur d'A-08… à restreindre de la même façon » ; « Pas de rejeu Docker : la preuve
est le vérificateur de chaque lot à code 0 sur l'arbre courant »). C'est précisément le point de fond
resté ouvert dans `verification-2.md §3`.

Périmètre du diff `eeccf64 → HEAD` pour A-08 : `production/A-08/manifeste.json` (−1119, +6),
`production/A-08/verifier.py` (+owned/contrat), `production/A-08/PRET`, et deux fichiers neufs
`seal-packaging-26nov.py`, `verification-manifestes-26nov.json`. **`a08/sequence.py`,
`wp/outils/bascule/repeter`, `wp/outils/bascule/repetition.md`, `wp/tests/a08/` : inchangés**
(`git diff --stat eeccf64 HEAD -- wp/outils/bascule/a08 wp/tests/a08 wp/outils/bascule/repetition.md`
= vide). Les lots voisins (a11→a14, `controler-export`) ont avancé hors périmètre A-08.

---

## 1. Consigne / arbitrage concerné

### Consigne 1 d'A-FAIRE.md = arbitrages-2026-11-26 §A-09 points 1-3 — **Appliquée**

- **Manifeste restreint aux seuls fichiers du lot.** `verifier.py:11-12` ajoute `owned(name)`
  (préfixes `production/A-08/`, `wp/tests/a08/`, `wp/outils/bascule/a08/`, plus `repeter` et
  `repetition.md`) ; `verifier.py:26` refuse toute entrée hors A-08
  (`assert owned(name),('outside A08 manifest',name)`). Le manifeste est purgé en conséquence :
  `manifeste.json:16` `"protected": {}` (était 1041 fichiers), `sources` ramené à 9 fichiers A-08
  (`manifeste.json:17-27`). Bilan retiré : `verification-manifestes-26nov.json:5-11`
  (`protected −1041`, `sources −61`, `delivery −2`). Aucune entrée `a09/a10/A-FAIRE.md/docs/briefs`
  ne subsiste (grep du manifeste : seules des occurrences `a03/a04/a05` **sous-dossiers de preuves
  A-08**, et `A-FAIRE` seulement en texte de décision `manifeste.json:1024`).
- **Fichier partagé contrôlé par contrat, pas par empreinte entière** (point 3). `verifier.py:35-37`
  remplace le hachage complet de `wp/tests/a02-audit/README.md` par la présence des deux lignes
  exactes du lot A-10 (`assert expected in data  # Shared documentation contract, not a whole-file
  pin.`). Le hachage complet de `wp/outils/bascule/README.md` (source de dérive au tour n° 2) est
  **supprimé**. Même logique pour la fermeture de dépendances : `verifier.py:51-53` lit la liste des
  outils dans la preuve scellée (`etat.json`) au lieu de hacher l'arbre courant de `wp/outils/bascule`.
- **Rescellé et `PRET` redéposé.** `PRET` : `manifest_sha256` passe à `2a9880895d…`
  (concordant : `verifier.py:169` vérifie `pret['manifest_sha256']==sha(manifeste.json)` et passe),
  mention `"packaging"` ajoutée (`PRET:11`). Politique tracée au manifeste
  (`manifeste.json:1026` `packaging_policy: "own-lot paths only; shared audit README by contract…"`,
  `:1027-1033` `packaging_removed_counts`, `:1034` `runtime_and_tests_unchanged: true`).
- **Question III.6 (tour n° 2) toujours close** côté manifeste (`documentation_decision`,
  `manifeste.json:1024`) et `PRET` (`documentation_introductions`) ; `repetition.md` inchangé.

Conforme à la consigne mot pour mot : manifeste propre au lot, fichier partagé par contrat, rescellé,
`PRET` redéposé, aucun rejeu Docker demandé.

---

## 2. Résultat des tests

- **Suite PHP autorisée rejouée** :
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
  — **exécutée** (réseau coupé, dépôt monté en lecture seule, conteneur jetable supprimé).
  Dernière ligne :

  ```
  REJEU : 1077 tests, 34327 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
  ```

  (Tour n° 2 : 1045/34247. L'écart vient d'autres lots de la voie 2, pas d'A-08 ; cette suite ne joue
  que le PHP et ne couvre pas l'orchestration A-08.)
- **`verifier.py` du lot lancé — code 0 sur l'arbre courant.** C'est la preuve exacte exigée par
  l'arbitrage (§A-09). Contrairement à ce que supposait `verification-2.md §3`, le `verifier.py`
  courant est **strictement en lecture seule** (`sys.dont_write_bytecode=True`, lignes 1-176 : il ne
  fait que lire et `print`, aucune écriture sous `production/`). Sortie : `exit_code: 0`,
  `verified_files` = protected 0 / sources 9 / evidence 176 / history 782 / delivery 19 ; toutes les
  empreintes A-08 concordent, le contrat du README partagé passe. **Le point rouge du tour n° 2 est
  donc levé.** (Hermès l'avait déjà consigné dans `verification-manifestes-26nov.json`, exit 0 ; je
  l'ai réexécuté moi-même.)
- **Banc Docker A-08 (`wp/tests/a08/run.py`) : non rejoué** — même limite qu'aux tours précédents
  (Docker/WSL + extensions sous licence hors d'atteinte ; `run.py` écrit sous `production/`). Sans
  objet pour cette modif : consigne 1 est de l'empaquetage, aucun rejeu Docker n'était demandé, et le
  code d'orchestration n'a pas bougé. `verifier.py` revalide le paquet de preuves natif livré
  (runner.json exit 0, result.json exit 0, 59 contrôles natifs, 11 contrôles runner, tous OK).

---

## 3. Régression ou modification non demandée

- **Aucune régression de code.** `sequence.py`, `repeter`, `repetition.md` et `wp/tests/a08/` sont
  **intacts** depuis `verification-2.md` (diff vide). Le seul « code » touché est le **harnais de
  vérification/empaquetage du lot** (`verifier.py` + nouveau `seal-packaging-26nov.py`), ce qui est
  exactement l'objet de la consigne 1 ; le manifeste épingle `sequence.py` à `dcbc0553…` (inchangé,
  concordant).
- **Deux assouplissements mineurs du harnais, signalés, sans incidence métier :**
  1. `verifier.py:164-165` : l'option `--sans-pret` ne vérifie plus l'absence du `PRET`
     (`assert not PRET.exists()` → `pass`), pour que le rescellage puisse tourner alors que le
     marqueur de clôture existe déjà. Commentaire explicite. N'affecte pas le contrôle plein
     (`verifier.py` sans argument) qui, lui, exige la cohérence `PRET`/manifeste.
  2. `verifier.py:24` tolère un `protected` vide (`assert entries or kind == 'protected'`),
     conséquence directe de « un manifeste n'épingle que ses fichiers » — A-08 ne protège aucun
     fichier d'un autre lot.
  Ces deux points sont la traduction fidèle de la consigne, pas des écarts.
- **Point de fond du tour n° 2 : RÉSOLU.** La dérive inter-lots (le manifeste A-08 photographiait des
  fichiers d'A-09→A-13, d'où `verifier.py` rouge) n'existe plus : manifeste restreint au lot, fichier
  partagé par contrat, `verifier.py` **vert** sur l'arbre courant. Rien d'inattendu ailleurs.

---

## 4. Verdict

**Prêt pour la clôture.**

La consigne 1 (correction d'empaquetage) est **appliquée proprement** : le manifeste A-08 n'épingle
plus que ses propres fichiers, le mode d'emploi partagé est contrôlé par contrat, le lot est rescellé
et le `PRET` redéposé avec une empreinte concordante. La suite PHP autorisée est **au vert**
(1077 tests, 0 échec) et le **`verifier.py` du lot passe à code 0 sur l'arbre courant** — c'est
exactement la preuve exigée par `docs/arbitrages-2026-11-26.md`. **Aucune régression** : le code
d'orchestration (`sequence.py`, `repeter`, `repetition.md`, tests) est inchangé octet pour octet.

Le **point de fond qui justifiait « Remonte à Ced » au tour n° 2 (manifeste trop large →
`verifier.py` rouge) est levé.** Il ne reste que la **limite de vérification** connue depuis le tour
n° 1 — la ré-exécution Docker indépendante du banc A-08 (`run.py`), hors de mon environnement — que
l'arbitrage a explicitement écartée pour cette correction (« pas de rejeu Docker ; la preuve est le
vérificateur à code 0 ») ; A-FAIRE.md et les arbitrages déclarent d'ailleurs **A-08 clos**. Ce n'est
pas un problème de fond restant.

*Rappel doctrine : ce verdict n'est pas un GO (§6). Les limites d'A-04 (montée 6.9.1 → 7.0, migrations
historiques des extensions payantes) restent entières, et aucune opération réelle n'est décidée ici ;
GO écrit de Ced requis avant toute bascule sur le vrai site.*
