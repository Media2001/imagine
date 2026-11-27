# Vérification B-14 — second tour (après corrections)

Vérificateur indépendant. Base : `corrections/B-14.md`, code corrigé par Hermès
(`wp/plugins/imagine-site/Accueil.php`, `wp/themes/imagine/inc/catalogue.php`,
`wp/themes/imagine/single-imagine_numero.php`, tests B-14), reçus scellés dans `production/B-14/`.
Je ne refais pas une relecture complète : je vérifie que chaque instruction est appliquée, je relance les tests, je cherche les régressions.

## 1. Instructions de `corrections/B-14.md`

### Instruction 1 — Rétablir l'ancre `id="imagine-abonnement"` sur la section de conversion. **Appliquée.**
- `Accueil.php:34` : `ouvrir()` mappe `'conversion' => 'imagine-abonnement'`, émis en `Accueil.php:39-41`.
- La section ainsi identifiée contient bien « S'abonner » (`Accueil.php:68-71`) — pas de deuxième section créée, même mécanisme que `imagine-thematiques` (`Accueil.php:34` également).
- Garanti par test : `b14-runtime.php:60-61` (`ancre_abonnement_paywall_contrat` : une seule occurrence, section contenant le lien S'abonner) et `AccueilB14Test.php:31-32`.

### Instruction 2 — Vérifier qu'un lien du paywall atteint cette cible unique avec S'abonner + rejouer la recette B-01. **Partiellement.**
- Cible atteinte avec CTA : **fait et prouvé**. Contrôle navigateur `paywall_atteint_conversion_avec_cta` (verifier `:38`) et clic HTTP réel vers `/#imagine-abonnement` (reçu `browser-corrections-final-V2`, 52 contrôles). Les liens du paywall pointent tous sur cette ancre : `paywall-abonnement.php:8`, `paywall-connexion.php:8`, `paywall-decouverte_epuisee.php:8`, `functions.php:198`, `Soutenir.php:39`.
- Rejeu de la recette B-01 : **exécuté mais rouge**, pour des raisons étrangères à B-14. `test_b01_theme.py` échoue sur deux contrats historiques pré-existants (`imagine_pdf_id` absent du gabarit numéro actuel ; `assets/reading.js` présent alors que le contrat B-01 interdit tout JS) ; `b01-verifier.py` échoue sur l'inventaire B00/C08. Voir `legacy-B01-corrections-V2.json` (deux exits = 1, `all_legacy_pass=false`). La recette n'atteint donc pas son contrôle d'ancre : le contrat d'ancre B-01 n'est **pas** reconfirmé par la recette elle-même, mais par le chemin HTTP réel qui s'y substitue. Hermès le documente honnêtement dans `A-VOIR.md` ; aucune réécriture de B-01, aucun succès fabriqué. **L'objectif (B-14 ne casse pas l'ancre) est atteint ; la lettre de l'instruction — « rejouer la recette B-01 pour confirmer » — ne l'est qu'en partie, bornée par une dette B-01 pré-existante.**

### Instruction 3 — Garde-fou rejouable léger sur les règles structurelles. **Appliquée.**
- `AccueilB14Test.php:14-35` (`testStructureReelleRendueAvecBouchonsMinimaux`, en processus PHPUnit séparé, bouchons minimaux dans `AccueilB14StructureFixture.php`) vérifie : ordre des 9 sections (`:27`), unique image `eager`/`high` (`:28-30`), présence de `section#imagine-abonnement` avec le lien d'attente (`:31-32`), absence de `<video>`/`<iframe>` (`:33`), aucune fuite de contenu réservé (`:34`).
- **Rejouable** : c'est un `testcase` PHPUnit exécuté dans le rejeu Docker, pas seulement dans la démo. Confirmé dans le JUnit du rejeu (verifier `:62-65` : 2 `AccueilB14Test`, 0 échec, dont le test de structure).

### Instruction 4 — Factoriser la sélection du libre + renforcer le contrôle démo. **Appliquée.**
- Helper unique `imagine_issue_free_article()` dans `wp/themes/imagine/inc/catalogue.php:51`. Appelé par B-04 `single-imagine_numero.php:17` et par `Accueil::libre` (`Accueil.php:23`). Plus de requête dupliquée.
- Contrôle démo renforcé : `b14-runtime.php:35` (`deux_libres_ordre_distinct_identite_b04`) et `:38` (`deux_libres_departage_id_identite_b04`) créent deux articles libres d'ordres distincts puis égaux, et **comparent les identifiants** rendus par B-04 et par l'accueil, couvrant le départage par ID.
- Impact sur `single-imagine_numero.php` (scellé B-11) borné : complément natif B-11 de 23 contrôles et diff strict limité à l'extraction du libre (`complement-B11-corrections-V2*.json`, `only_approved_free_selection_change=true`). Aucun octet média/audio changé.

### Instruction 5 — Confirmer la dérive de comptage (1206→1208) comme non imputable à B-14. **Appliquée, avec réattribution.**
- Confirmé **non imputable à B-14**. En revanche la source n'est **pas** A-32/A-33 comme l'hypothétisait la fusion : `derive-comptage-V2.json` l'impute précisément à `PiedPageB15Test` (B-15, 2 tests / 5 assertions). Verifier `:49-50` asserte cette origine. L'hypothèse A-32/A-33 de la fusion était donc inexacte ; Hermès donne l'attribution exacte. Objectif atteint.
- Les paquets en échec au rejeu restent cantonnés à A-31/A-32/A-33 (travaux en cours), aucun B-14 (verifier `:60`).

## 2. Résultat des tests

Je n'ai **pas** pu relancer un rejeu Docker frais et indépendant : `wp/tests/rejouer.ps1` est derrière une approbation non accordable dans cette session non interactive, et `php` n'est pas lançable hors conteneur. J'ai donc vérifié par `production/B-14/verifier.py`, qui **relie les reçus scellés aux empreintes des fichiers actuels** (contrôle d'intégrité `c.integrity` + comparaison de digests ligne `:43`) : le rejeu archivé correspond bien au code présent sur disque.

`python -B production/B-14/verifier.py` → **PASS** :
```
{"B14": "PASS", "native": 22, "browser": 52, "surfaces": 2, "phpunit": 2,
 "replay_tests": 1209, "replay_assertions": 36693,
 "tools": {"tools": 23, "checks": 852, "failures": 0, "excluded": []},
 "foreign_packets": [], "legacy_B01": "2 legacy commands failed on prior contracts; current anchor HTTP PASS",
 "B11_native_complement": 23}
```
- Rejeu PHPUnit : **1209 tests / 36693 assertions, 0 échec, 0 erreur, 0 ignoré** ; outils 23 / 852 contrôles / 0 échec.
- Les 2 `testcase` B-14 (dont le garde-fou structurel) sont verts dans le JUnit du rejeu.
- Démo : 22 contrôles natifs + 52 navigateur, tous verts.

Réserve honnête : le vert repose sur le reçu scellé de rejeu d'Hermès, revérifié par empreintes, et non sur un rejeu Docker que j'aurais relancé moi-même.

## 3. Régressions / modifications non demandées

- Modifications hors `Accueil.php` : `inc/catalogue.php` (ajout du helper) et `single-imagine_numero.php` (appel du helper) — **demandées** par l'instruction 4. Diff prouvé borné à la sélection du libre, aucun octet média/audio changé.
- Aucune modification non sollicitée détectée. Le contrôle B-05 « Derniers articles » devenu historique relève du retrait déjà acté au premier tour, pas d'une régression.
- Les points mineurs non corrigés (slugs en dur sans garde `Accueil.php:81,102,104` ; « S'abonner » silencieux si page d'attente absente `Accueil.php:68-71`) restent ouverts mais étaient classés **non bloquants** et renvoyés à la confirmation de Ced (§5 de la fusion). Pas de régression nouvelle.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les cinq instructions sont traitées : trois pleinement (1, 3, 4), deux atteintes dans leur objectif avec une réserve documentée (2 : recette B-01 rouge sur dette pré-existante, ancre prouvée par le chemin HTTP ; 5 : dérive confirmée non-B-14, réattribuée à B-15). Tests au vert (1209/36693, 0 échec), garde-fou structurel désormais rejouable, aucune régression ni modification non demandée. Aucun problème de fond restant ne justifie une remontée.

Reste pour Ced, non bloquant pour le code : la question fermée du repli visible si une page cible manque (§5 de la fusion), et la validation visuelle de fidélité à la maquette — hors de ce verdict.

Ce verdict n'est pas un GO au sens du §3 de la doctrine.
