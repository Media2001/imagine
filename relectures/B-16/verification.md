# Vérification B-16 — La page article (2e et dernier tour)

Vérificateur après corrections d'Hermès (fusion `corrections/B-16.md` appliquée). Lot : B-16, enveloppe éditoriale publique autour de C-08/B-03.

Méthode : `git diff` depuis le commit de la fusion (`be88202d`) sur `wp/` et `production/B-16`, relecture ciblée du code modifié, relance des tests. Pas de nouvelle relecture complète.

## 1. Instructions de `corrections/B-16.md` §4

| # | Instruction | État | Preuve |
|---|---|---|---|
| 1 | Corriger R1 : piloter l'appel par le **motif C-08**, supprimer `abonne()` et le cas « Memberships absente » | **Appliquée** | `PageArticle.php:51-58` : `appel(array $decision)` ne garde l'appel que pour les motifs `numero_achete`, `decouverte_duree`, `decouverte_articles` ; `abonne()` supprimée ; appel dans `fin()` à `PageArticle.php:90` sans second argument. |
| 2 | Tester R1 : profils **offert** (`complimentary`) et **résiliation à échéance** (`pending-cancel`) relus avant/à/après la borne ; acheteur conservé | **Appliquée** | PHP pur : `PageArticleB16Test.php:23-54` (data provider : `complimentary→offert_actif`, `pending-cancel` à `18:01:49`/`:50`/`:51`). Natif réel : `b16-runtime.php:42` (offert sans appel), `:52-56` (pending-cancel avant/à/après), `:60` (acheteur → appel présent), `:62` (anonyme → pas d'appel). |
| 3 | Corriger R2 : soumettre à C-26 le **HTML complet** de l'appel de fin, mutation témoin **dans** le bloc avant extraction | **Appliquée** | `b16-browser.py:44-56` : `extract()` assemble `head.outerHTML` + `outerHTML` du bloc `[data-b16="abonnement"]` ; le témoin `data-b16-mutant` est posé sur le bloc d'appel (quand il existe) **avant** extraction, puis retiré. |
| 4 | Corriger R3 : adosser le « standard d'abord » du README à la doc officielle | **Appliquée** | `README.md` (section B-16) cite `get_post_field` (contexte raw), `get_the_excerpt`, `get_the_terms`, `get_the_author`. |
| 5 | Rejouer suite PHP + vérificateur + preuve navigateur ; `before == after` | **Appliquée** | Artefacts régénérés (`native-corrections-final2-V2`, `browser-corrections-final-V2`, `replay-corrections-V2`) ; `verifier.py` PASS ; `native['before']==native['after']` tient. |

Contrôle de fond sur l'instruction 1 : la liste blanche `[numero_achete, decouverte_duree, decouverte_articles]` est bien le **complément exact** des accès complets non-abonné. Les motifs qui donnent `complet=true` dans le moteur (`Moteur.php:70,76,79,89,128-129,140,158`) sont `contenu_futur_equipe_par_reglage`, `contenu_ouvert`, `robot_verifie`, `equipe`, `delai_grace`, `abonnement_actif`, `offert_actif`, `groupe_actif`, `numero_achete`, `decouverte_duree`, `decouverte_articles` (enum `Acces/Motif.php`). Tous les cas abonnement / équipe / grâce / article libre / robot sont donc exclus de l'appel ; seuls achat et découverte le déclenchent. Le cas équipe (`equipe`) est couvert : pas d'appel. La variante « Memberships absente » disparaît : C-08 ferme déjà quand l'adaptateur manque (`Paywall.php:104`).

## 2. Résultat des tests

Relancés par le vérificateur :

- `python -B production/B-16/verifier.py` → **PASS** ; `--live` → **PASS**.
- Bilan : `native` 15/15 contrôles, `browser` 77/77 contrôles (9 lignes, `markers_count>10`, `external=false`), 9 réponses de réception.
- Suite PHP (rejeu capté dans `replay-corrections-V2.log`, empreintes des sources vérifiées égales aux fichiers courants) : **1217 tests, 36738 assertions, 0 échec, 0 erreur, 0 ignoré — PASS** ; outils purs 23/852/0.
- `PageArticleB16Test` : 5 tests, 28 assertions, 0 échec (`testAppelSuitSeulementLeMotifC08` + 4 jeux de `testVraiPaywallSurProfilsDivergents`).
- Témoin rouge conservé : `red-V2.json` échoue toujours comme attendu ; image vérifiée (sha256) ; restauration `before == after`.

Le `verifier.py` lie les artefacts aux **empreintes actuelles** des sources (`native['sources']==owner.sources(owner)`, idem navigateur) : le PASS prouve que les preuves correspondent au code corrigé, pas à une version antérieure.

Note d'environnement : le rejeu Docker (`wp/tests/rejouer.ps1`) n'a pas pu être relancé à neuf dans cette session (approbation refusée pour le processus conteneur). La vérification s'appuie sur `verifier.py` relancé, qui contrôle l'intégrité des artefacts et leur liaison aux empreintes des fichiers corrigés.

## 3. Régressions et modifications non demandées

- **Aucune régression dans le périmètre B-16.** Le diff de `PageArticle.php` depuis la fusion ne contient que la correction R1 (signature d'`appel()`, suppression d'`abonne()`, appel dans `fin()`) ; `entete()`, `resume()`, `sauver()` inchangés. Le diff de `b16-browser.py` ne contient que R2. Aucun appelant résiduel à l'ancienne signature `appel(..., $abonne)` ni à `abonne()`.
- Le compte de tests passe de 1213 à 1217 : conséquence attendue des nouveaux jeux de `PageArticleB16Test` ; non une régression.
- **Hors périmètre B-16 (à signaler, pas une régression de ce lot)** : l'arbre de travail contient aussi une section **C-31** ajoutée au même `README.md` et des fichiers `production/C-31/` + `wp/outils/demo/c31-browser.py` modifiés. Travail d'un autre lot mené en parallèle, sans effet sur B-16 ; à ne pas confondre avec les corrections B-16.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions de la fusion sont appliquées et prouvées, les tests sont au vert, aucun problème de fond ne subsiste. Reste la seule validation **visuelle** déjà prévue par la fusion (structure/ordre de l'en-tête, en attente des maquettes) : elle relève de Ced par nature et ne constitue pas un problème de fond restant.

Rappel : cette vérification prépare la clôture d'un lot de code ; elle n'est pas un GO pour déployer, accéder à un compte réel ou toucher à la production.
