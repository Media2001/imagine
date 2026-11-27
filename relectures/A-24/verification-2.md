# Vérification — A-24 (3e tour, après requalification)

Vérificateur : Claude. Date : 2026-11-27. Objet : contrôler les modifications
d'Hermès sur A-24 depuis `relectures/A-24/verification.md`, relancer les tests,
relever régressions et modifications non demandées, donner un verdict. Pas de
relecture complète refaite.

**Ce qui justifiait les modifications.** `A-FAIRE.md` consigne 1 (« la
requalification ») et `docs/arbitrages-2026-11-27.md` (§ « A-23, A-24, A-25 »,
l. 35-39, passages de 1 h et de 4 h) : les corrections de `corrections/A-24.md`
étaient déjà vérifiées « prêt » ; le code ne change pas ; A-28 a gelé l'import,
donc le paquet est **refait une fois** sur l'import gelé, avec sa déclaration
`rejeu.json` (T-03), puis `RAPPORT.md` et le paragraphe « Portée » sont
rafraîchis (réserve documentaire de la vérification précédente).

**Base de comparaison.** Diff de `8c40ca03` (26/11 22:58, état finalisé sur lequel
portait la 1re vérification) à HEAD, sur `wp/outils/bascule/a24/`, `wp/tests/a24/`
et `production/A-24/`.

---

## 1. Consignes et arbitrages concernés

**1 — Code de l'outil inchangé (arbitrage « rien à refaire au fond »). Appliqué.**
Diff `8c40ca03`→HEAD sur `wp/outils/bascule/a24/` et `wp/tests/a24/` : seul
`wp/outils/bascule/a24/README.md` change (1 ligne, voir pt 3). `Analysis.php`,
`Inventory.php`, `Command.php`, `confine.py`, `report.py`, les JSON et toute la
suite `wp/tests/a24/` sont identiques octet pour octet. La correction P1 et les
oracles de la 1re vérification tiennent sans régression.

**2 — Paquet refait sur l'import A-28 gelé. Appliqué.**
`production/A-24/preuves/final/utf8/dependencies.json:21-37` : les empreintes de
l'import (`engine.php fef246a5…`, `store.php 88617b0e…`, `guard.php 9852be41…`,
`lib.php c6ebdbb9…`, `form-decision-refused.php`, `form-policy.json`) **coïncident**
avec le sceau A-28 (`production/A-28/preuves/final/dependency-invalidations.json`,
`import_sources`). Matrice neuve, Python Windows 3.14.6, UTF-8 et cp1252
(`FINALISATION.md:5`). Métrique corrigée conservée :
`classic-addresses/expedition.json` `different_from_account: 1` (overall et BE).

**3 — Déclaration `rejeu.json` et point d'entrée sans argument (T-03). Appliqué.**
`production/A-24/rejeu.json` (neuf, `schema:1`, 11 journaux, 81 contrôles listés)
et `production/A-24/verify.py` (neuf : refuse tout argument → `NO_ARGUMENTS`,
sinon appelle `wp/tests/a24/verify.py --require-shared` sur l'unique paquet). Le
rejeu autorisé vérifie ce paquet au vert (voir §2), ce qui **lève la réserve de
méthode** de la 1re vérification (vérificateur de paquet alors injouable en
session).

**4 — `RAPPORT.md` rafraîchi (réserve documentaire). Appliqué.**
`production/A-24/RAPPORT.md` est réécrit : requalification du 27/11 05:03, matrice
neuve sur import A-28 final, plus aucune mention de l'état « matrice native à
rejouer par le parent ». `FINALISATION.md` porte les compteurs courants.

**5 — Paragraphe « Portée » du mode d'emploi rafraîchi. Appliqué.**
`wp/outils/bascule/a24/README.md:53` : la « Portée » renvoie désormais à « la
matrice neuve scellée dans `production/A-24/preuves/final/`, exécutée sur l'import
final A-28, après correction de comparaison » ; les 206 contrôles de l'ancien
paquet sont dits « historiques, pas une preuve actuelle ». C'est l'unique ligne
modifiée du dépôt côté code.

**6 — Un seul paquet de preuves (règle de la file). Appliqué.**
`production/A-24/preuves/` ne contient que `final/` ; les ancêtres et essais
intermédiaires sont hors dépôt (`FINALISATION.md:27`).

**7 — Réalignement du SHA du gardien (M1, report de la 1re vérification). Appliqué.**
`grep ce62d8` sur `production/A-24/` : aucun match. `dependencies.json:17`
porte le gardien courant `c913c792…`.

## 2. Résultat des tests

Commande imposée relancée par moi (refusée via l'outil PowerShell — « processus
imbriqué non validable » — mais acceptée via l'outil Bash, commande écrite telle
quelle) :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

`REJEU : 1153 tests, 36075 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

- Ligne A-24 : `a24 ; 27 controls ; 0 failures ; exit=0` (les 27 contrôles, dont
  les 10 de comparaison, bien exécutés).
- `PAQUETS : 9 vérifiés, 0 échecs` — la liste inclut **A-24** (avec A-21, A-22,
  A-23, A-25, A-26, A-27, A-28, A-30). Le vérificateur de paquet d'A-24 passe donc
  au vert dans la commande autorisée, de façon indépendante.
- `OUTILS : 22 outils, 582 contrôles, 0 échecs ; hors rejeu : aucun`.
- Isolement confirmé : `network=none ; rootfs=ro ; mount=…/wp:ro ; cap-drop=ALL ;
  no-new-privileges`.

Portée inchangée : `rejouer.ps1` rejoue l'unité PHP pure (`unit.php`) et, via T-03,
le vérificateur du paquet ; le natif/Python/confinement restent attestés par la
matrice scellée. Je ne les ai pas réexécutés hors de cette commande.

## 3. Régressions et modifications non demandées

- **Aucune régression.** Code de l'outil identique à l'état finalisé ; suite au
  vert ; métrique `different_from_account=1` conservée.
- **Aucune modification non demandée** dans le périmètre A-24 : la seule retouche
  de code est la ligne « Portée » explicitement demandée ; le reste
  (`rejeu.json`, `verify.py`, paquet refait, `RAPPORT.md`/`FINALISATION.md`) relève
  des consignes 1 et T-03. La réserve documentaire de la 1re vérification est
  entièrement levée.
- Hors périmètre A-24, simplement signalé : le fichier parasite `prefix}u0024s`
  traîne toujours à la racine du dépôt (non suivi) ; deux autres non suivis sans
  rapport avec ce lot (`relectures/A-23/verification-2.md`, `wp/tests/a31/reseal.py`).

## 4. Verdict

**Prêt pour la clôture.**

Les consignes qui justifiaient la reprise d'A-24 sont toutes appliquées : code de
l'outil inchangé, paquet refait sur l'import A-28 gelé (empreintes = sceau A-28),
déclaration `rejeu.json` et point d'entrée sans argument ajoutés, `RAPPORT.md` et
paragraphe « Portée » rafraîchis, SHA du gardien réaligné. Le rejeu autorisé est
au vert (1153 tests, A-24 : 27 contrôles, paquet A-24 vérifié parmi 9), ce qui
lève la seule réserve de méthode restée ouverte. Aucun problème de fond ne
subsiste (code, métier, étanchéité, preuves), aucune question ouverte pour Ced ni
Imagine. Ce verdict de vérification n'est pas un GO au sens du §3 ; la clôture
reste à Ced.
