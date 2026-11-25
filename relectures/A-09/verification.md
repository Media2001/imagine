# Vérification A-09 — 2e et dernier tour

Date : 25 novembre 2026. Vérificateur : Claude. Objet : contrôler l'application de
`corrections/A-09.md` après la passe d'Hermès, sans refaire une relecture complète.

Méthode : `git diff` entre le commit de la fusion (`6dd21c7`, synchro 21:58) et `HEAD`
sur `wp/outils/bascule/a09`, `wp/tests/a09` et `production/A-09` ; relecture ciblée du
diff de `check.py` ; lecture de la preuve scellée ; exécution de `verifier.py` (lecture
seule) et compilation de `check.py`.

---

## 1. Application des instructions de `corrections/A-09.md`

**Instruction 1 — R1, séparer chemin et requête.** **Appliquée.**
`wp/outils/bascule/a09/check.py:37` découpe `path, delimiter, query = value.partition('?')`.
L'interdiction `%2f`/`%5c`/`%20`/contrôles ne porte plus que sur le chemin (`check.py:39`) ;
la requête ne refuse que les contrôles encodés (`check.py:40`). Le transport est inchangé :
`Client.get` canonise la représentation complète `path+query` (`check.py:118`). Test
`query-encoded` : 6 GET, chemins exacts conservés (`u=%2Fpage`, `q=deux%20mots`), 0
non-conforme. `%2f` dans le chemin reste refusé (test `query-path-refusal`).

**Instruction 2 — R2, une seule représentation canonique.** **Appliquée** (défaut prudent
explicitement permis par la fusion : refus de la requête vide plutôt que prise en charge).
`check.py:38` refuse une URI à `?` final avant tout appel (`A09_PLAN_EMPTY_QUERY`) ; garde
identique dans le client (`check.py:117`) et sur la `Location` observée (`check.py:164`,
`A09_LOCATION_EMPTY_QUERY`). Tests `empty-query-conflict` et `empty-query-target` : code 2,
zéro requête, pas de faux `mauvaise_cible` ; `empty-query-location` : `redirection_invalide`,
non suivie.

**Instruction 3 — R3, ASCII sur l'entrée entière avant analyse.** **Appliquée.**
`value.isascii()` ajouté en tête de `relative` (`check.py:34`), `origin` (`check.py:72`) et du
contrôle de `Location` (`check.py:163`). Un caractère > U+FFFF en fin de plan provoque le refus
global, zéro GET (tests `non-bmp-source` / `non-bmp-target`).

**Instruction 4 — rejeu, preuve dédiée.** **Appliquée.** Le banc `wp/tests/a09/run.py` a été
rejoué : nouvelle preuve scellée `preuves/a1671ceb23d2/` (remplace `6fd5c1c30990`), **28 tests
réussis, 0 échec** (21 + 7 nouveaux). `wp/tests/a09/test_http.py` ajoute les trois cas de bord
(query encodée, requête vide, non-BMP). Cycles RED→GREEN archivés (`tdd_cycles` du manifeste).

**Instruction 5 — baseline.** **Partiellement appliquée.** Le volet demandé est correct :
`wp/tests/a02-audit/README.md` est bien traité (`verifier.py:145-148` reconstruit l'octet-à-octet
l'original + deux lignes A-10, et vérifie le SHA d'origine), avec `transition-corrections.json`
qui qualifie les 5 dérives antérieures. **Mais l'objectif de l'instruction — « `verifier.py`
revient à code 0 » — n'est pas atteint** dans l'état actuel du dépôt : `verifier.py` retourne
**exit 1**, `hash drift: A-FAIRE.md` (voir §3). C'est le seul écart ; evidence (886), baseline
(95) et historique (722) sont propres.

**Instruction 6 — libellé (facultatif).** **Appliquée.** `tester-redirections.md` mis à jour
(+10/-3) ; précision du sens de `mauvaise_cible` (première cible).

**Instruction 7 — conserver `.imagine-a09-http.json`.** **Appliquée.** Déclaration toujours exigée
(`check.py:96-97`), inchangée.

---

## 2. Résultat des tests

- **Preuve scellée Docker `preuves/a1671ceb23d2/`** (lue, non ré-exécutée par moi) :
  `runner.json` exit 0 ; `isolation_before`, `tests`, `isolation_after`, `cleanup_exact_owned`,
  `sources_unchanged` tous `ok` ; `Ran 28 tests … OK`. Je ne relance pas le banc moi-même : il
  écrit dans `production/A-09/preuves/` et exige Docker, ce qui déborde du droit d'écriture du
  vérificateur (cf. note de la fusion, §1). La couverture du code repose donc sur cette preuve.
- **`python -B production/A-09/verifier.py`** (lecture seule) : **exit 1 — `hash drift:
  A-FAIRE.md`**. Le garde-fou s'arrête avant même d'atteindre la vérification du paquet de preuve.
- **Compilation** : `wp/outils/bascule/a09/check.py` compile sans erreur.

Autrement dit : la **logique** R1/R2/R3 est juste et prouvée verte au scellé ; le **garde-fou de
vérification du lot** échoue aujourd'hui.

---

## 3. Régression / modification non demandée

**`A-FAIRE.md` épinglé par erreur dans le manifeste A-09 → `verifier.py` RED.**
Les corrections ont ajouté `A-FAIRE.md` aux `sources` du manifeste (`production/A-09/manifeste.json`).
Ce fichier **était absent** du manifeste d'avant corrections
(`production/A-09/avant-corrections/manifeste.json`) : aucune des 7 instructions ne demandait de
l'épingler. Or `A-FAIRE.md` est la feuille de route **globale** du projet, qui change à chaque
passage automatique. Elle a dérivé au **passage de 22 h** (commit `9707a3e`), **postérieur** au
scellé des corrections (synchro 21:58). Empreinte épinglée `188f3a6e…` ; actuelle `370dbf7b…`.

Conséquence : `verifier.py` retourne 1 à chaque contrôle, et **rééchouera à chaque passage** tant
que ce fichier non-A-09 et volatil restera dans les sources du manifeste. C'est exactement la
classe de dérive que l'instruction 5 visait à éliminer, réintroduite ici sur un autre fichier.
La correction est étroite et mécanique (retirer `A-FAIRE.md` des sources, ou rafraîchir le
manifeste sur un fichier qui n'a pas à y figurer), mais elle n'est pas faite.

Aucune autre modification non demandée. Les fichiers sources réels d'A-09 (`tester-redirections`,
`a09/check.py`, tests, exemple CSV) et tous les autres jeux d'empreintes sont cohérents ;
l'exemple reste à trois lignes fictives ; aucun secret, aucune donnée réelle, aucun accès à un
site, une base ou un compte, aucun GO production.

---

## 4. Verdict

**Remonte à Ced — problème de fond restant.**

Les trois corrections de code (R1, R2, R3) sont correctement appliquées, aux lignes citées, et
prouvées par une exécution scellée de 28 tests verts ; le rafraîchissement du README A-02 est
exact ; les points facultatifs et de doctrine sont traités. **Mais le lot ne passe pas son propre
garde-fou** : `verifier.py` retourne exit 1, parce que les corrections ont épinglé dans le
manifeste un fichier de feuille de route global (`A-FAIRE.md`) qui a aussitôt dérivé au passage de
22 h. L'objectif explicite de l'instruction 5 (« `verifier.py` revient à code 0 ») n'est donc pas
tenu, et la fragilité se reproduira à chaque synchro.

Je ne peux pas déclarer « prêt pour la validation de Ced » tant que la commande de vérification du
lot échoue. Le correctif est circonscrit (dés-épingler / corriger `A-FAIRE.md` dans
`production/A-09/manifeste.json`, puis re-sceller) et ne touche ni le code R1/R2/R3 ni
l'architecture.

---

*Rappel doctrine : ce verdict de vérification n'est pas un GO.*
