# Vérification A-08 — tour n° 2 (après modif post-vérification)

Date : 26 novembre 2026. Vérificateur : Claude (lecture seule sur le code, rejeu de la suite PHP autorisée).
Base comparée : version déjà vérifiée (`7794e65`, 25/11 22:23, celle de `verification.md`) → `HEAD`.
Je **ne refais pas** une relecture complète : je contrôle uniquement **ce qu'Hermès a changé depuis**
`verification.md` et je rejoue la suite PHP.

Ce qui justifie la modification : **A-FAIRE.md, consigne 1** (« A-08, question III.6 : tranchée »),
confirmée par **`docs/arbitrages-2026-11-25.md:166`** (« Contenu exact conservé, une phrase simple en
tête de chaque bloc, aucune commande modifiée. Ced peut le défaire »). Pas de rejeu Docker demandé :
la preuve est le diff (prose seule) et l'empreinte du fichier au manifeste.

Fichiers A-08 modifiés depuis la vérification (`git diff --stat 7794e65 HEAD`) :
`wp/outils/bascule/repetition.md` (+18, 0 suppression), `production/A-08/PRET`,
`production/A-08/manifeste.json`, et le paquet neuf `production/A-08/intros-20261126/`
(`avant.md`, `prose.diff`, `verification.json`). **`a08/sequence.py`, `wp/tests/a08/` : inchangés**
(`git diff --stat 7794e65 HEAD -- wp/outils/bascule/a08 wp/tests/a08` = vide). Les lots voisins
a10/a11/a12/a13 ont avancé dans `wp/outils/bascule`, hors périmètre A-08.

---

## 1. Consigne / arbitrage concerné

### Consigne 1 d'A-FAIRE.md = III.6 (arbitrages-2026-11-25.md:166) — **Appliquée**
- **Une phrase d'intro simple en tête de chaque bloc**, ajoutée sans toucher au reste :
  `repetition.md:3, 11, 21, 35, 46, 53, 74, 82, 90` (neuf blocs : préparation, chemins/étapes 1‑2,
  tableau des six commandes, transformations/réception, changements opérateur, arrêts/reprise,
  second passage, GO écrit, rejeu banc fictif).
- **Aucune commande modifiée** : les deux blocs ```bash``` (lignes 13‑19 et 37‑44) et le tableau
  (23‑30) sont identiques octet pour octet au diff (`+18` insertions, **0 suppression**) ;
  `verification.json` : `only_prose_additions: true`, `commands_unchanged: true`.
- **Empreinte mise à jour au manifeste et cohérente** : `manifeste.json` passe
  `repetition.md` de `e398d744…` à `badf3ee4…` ; recalcul réel du fichier courant = `badf3ee4…`
  (concordant). `PRET.manifest_sha256` mis à jour (`53e96a0e…`).
- **Question correctement close côté `PRET`** : `ced_question_deferred` (III.6) **retiré** du `PRET`
  et du manifeste, remplacé par `documentation_introductions` / `documentation_decision`
  (« III.6 appliquée conformément à A-FAIRE consigne 1 ; aucun rejeu Docker demandé »).
  Addendum tracé dans `manifeste.json` (`documentation_addendum`, `documentation_diff`).

Conforme à la consigne mot pour mot : contenu exact conservé, prose seule, commandes intactes,
pas de rejeu Docker.

---

## 2. Résultat des tests

- **Suite PHP autorisée rejouée** : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
  — **exécutée** (conteneur jetable, réseau coupé, dépôt monté en lecture seule).
  Dernière ligne :

  ```
  REJEU : 1045 tests, 34247 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
  ```

  (Au premier tour : 1012/34006. L'écart vient d'autres lots de la voie 2, pas d'A-08 ;
  cette suite ne joue que le PHP et ne couvre pas l'orchestration A-08.)
- **Banc Docker A-08 (`wp/tests/a08/run.py`) : non rejoué** — même limite qu'aux deux relecteurs
  (Docker/WSL + extensions sous licence hors d'atteinte, `run.py` écrit sous `production/`).
  Sans objet pour cette modif : consigne 1 est de la documentation, Hermès lui-même ne devait pas
  rejouer Docker. Le code d'orchestration n'a pas bougé depuis la vérification n° 1.

---

## 3. Régression ou modification non demandée

- **Aucune régression de code.** `sequence.py` et `wp/tests/a08/` sont **intacts** depuis la
  vérification n° 1. Le changement se limite à de la prose dans `repetition.md` + traçabilité
  (`PRET`, manifeste, paquet `intros-20261126`). Rien hors du périmètre de la consigne.
- **Rien d'inattendu dans les intros.** Elles décrivent chaque bloc et son état final sans
  introduire de règle ni contredire les commandes (ex. l. 11 « code 75 », l. 35 « code 0 … après
  les deux rendez-vous », l. 82 « aucune opération réelle sans les accords écrits distincts »).
- **Point ouvert de `verification.md` §3 NON résolu par cette modif — à remonter.**
  Le re-scellage du 00:45 est un **addendum documentaire** (`documentation_addendum`,
  `only_prose_additions: true`) : il met à jour `repetition.md` et ajoute trois fichiers d'intros,
  **sans re-photographier ni restreindre** les catégories larges `protected`/`sources` du manifeste
  A-08. La dérive inter-lots signalée au premier tour **persiste donc**, et s'est **étendue** : depuis,
  A-10 puis A-11/A-12/A-13 ont avancé dans `wp/outils/bascule`. Conséquence : `verifier.py` reste
  **rouge** sur l'arbre courant (photo A-08 qui déborde sur le périmètre des lots voisins).
  *Je n'ai pas ré-exécuté `verifier.py`* (hors commande autorisée ; il écrit sous `production/`) :
  constat déduit du diff du manifeste et de l'avancée des lots voisins, dans la continuité de
  `verification.md` §3. Ce **n'est pas** un défaut de logique A-08 ni un effet de la consigne 1.
  Remède inchangé : re-sceller le manifeste A-08 après stabilisation des lots voisins, ou restreindre
  `protected`/`sources` au seul périmètre A-08.

---

## 4. Verdict

**Remonte à Ced.**

La consigne 1 (III.6) est **appliquée proprement** : une phrase d'intro par bloc, contenu et commandes
inchangés, empreinte mise à jour et concordante, question close côté `PRET`. La suite PHP autorisée est
**au vert** (1045 tests, 0 échec). **Aucune régression** : le code d'orchestration n'a pas bougé.

Ce qui empêche la clôture n'est **pas** cette modification mais un **problème de fond resté ouvert**
depuis `verification.md` §3 : le manifeste A-08 photographie des catégories trop larges qui débordent
sur les lots voisins (A-09 puis A-10→A-13), si bien que `verifier.py` ne repasse pas au vert sur
l'arbre courant. Le re-scellage du 00:45 était volontairement limité à la prose et ne l'a pas corrigé.
Tant que le manifeste n'est pas re-scellé/restreint au seul périmètre A-08 (décision de Ced, après
stabilisation des lots voisins), le lot ne se valide pas par ses preuves (doctrine §6).

Reste aussi, comme au premier tour, la **ré-exécution Docker A-08 indépendante** (`run.py`) non levée,
faute d'environnement — sans lien avec la consigne 1.

*Rappel doctrine : ce verdict n'est pas un GO. Aucune opération réelle n'est décidée ici ; préalables
A03/A04/A05 et GO écrit de Ced restent requis avant toute bascule sur le vrai site.*
