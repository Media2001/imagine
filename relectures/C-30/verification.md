# Vérification — Lot C-30 « La page d'offre de bienvenue et son code suivi » (2e et dernier tour)

Vérificateur : Claude. Date : 2026-11-28.
Base relue : état figé par la fusion (`225d2a7f`, 01:53). Corrections d'Hermès lues par `git diff 225d2a7f..HEAD` sur `wp/` et `production/C-30`, et par le préimage `production/C-30/avant-corrections-V2/`.
Fichiers de code touchés : `CodesSuivis.php`, `CodesSuivisAdmin.php`, `CodesSuivisConfidentialite.php`, `README.md` ; tests `CodesSuivisC30Test.php`, `CodesSuivisC30AdapterTest.php` (+ `CodesSuivisC30Stubs.php`), `wp/tests/demo/c30-runtime.php`. `CodesSuivisRegles.php` **non modifié** (défaut prudent appliqué : validateur conservé).

Ce document ne refait pas la relecture complète : il contrôle uniquement l'application des 7 instructions + la décision technique de `corrections/C-30.md`, rejoue les tests, et cherche les régressions.

## 1. Application des instructions

| # | Instruction | État | Fichier : ligne |
|---|---|---|---|
| 1 | Commandes invitées couvertes à l'export ET à l'effacement C-21 (I1) ; union compte+invités, dédoublonnage par ID, pagination stable ; `items_retained` si tout n'est pas traité | **Appliquée** | `CodesSuivisConfidentialite.php:22-57` (union de `[customer_id=0,billing_email]` et `[customer_id=user]`, `ksort` puis `array_slice` ; méta **non** utilisée comme filtre, donc pas de saut de page). `effacer()` `:81-115` lève `items_retained=true`/`done=false` sur toute panne. Test scellé : `CodesSuivisC30AdapterTest::testUnionCompteInviteEtTiersPreserve` et `testPaginationStableUnionPuisEffacementSansSaut` (102 commandes, tiers préservé). |
| 2 | Test d'adaptateur scellé sur la couche Woo (I-C) | **Appliquée** | `CodesSuivisC30AdapterTest.php` (7 cas, 155 assertions) : session/`retenir`, revalidation candidat, raccord Store API, verrou + sceau immuable, comptage historique, export/effacement compte+invité+tiers, pannes lecture/verrou/persistance. Découvert par la suite scellée (cf. §2). |
| 3 | Renforcer la preuve de non-modification des prix (I2) : même produit, mêmes quantités, calcul Woo réel, test capable d'échouer | **Appliquée** (preuve en recette *live*, non scellée) | `c30-runtime.php:49-78` : deux vrais paniers du même produit payant, quantité 2, `create_order`, comparaison total/remise/taxe/coupons ; sonde de remise liée au code sur `woocommerce_before_calculate_totals` → `mutation_remise_code_detectee` exige l'échec du comparateur. Tourne via `verifier.py --live`, pas dans la suite PHPUnit scellée (cf. réserve §3). |
| 4 | Aligner l'aide de saisie sur le validateur (M1) ; couvrir `2026-affiche` refusé ; défaut : corriger le texte, garder le validateur | **Appliquée** | Aide : `CodesSuivisAdmin.php:79` (« code commençant par une lettre minuscule… »). README `:23`. Test : `CodesSuivisC30Test.php:18` `assertNull(... ['2026-affiche' => 'FICTIF'])`, vert. |
| 5 | Raccorder le checkout Blocks / Store API ou en prouver l'absence d'impact (I-B) ; défaut : accepter `{checkout, store-api}` | **Appliquée** | `CodesSuivis.php:30-33` (hook `woocommerce_store_api_checkout_order_processed`), `:58` et `:89` (`in_array(..., ['checkout','store-api'])`). Tests : adapter `testStoreApiCandidatSurHookNatifPuisScelle` ; runtime `store_api_candidat_natif`/`store_api_scelle_natif`/`hook_store_api_present_dans_source`. |
| 6 | Documenter le comptage historique (code stocké sur la commande) | **Appliquée** | `README.md:30` et `A-VOIR.md:7` : attribution historique explicite, un code retiré du catalogue reste compté sur les commandes passées. Vérifié par `testCompteurHistoriqueDatesEtLectureEnEchec`. |
| 7 | Mineur, efficacité : borner `compter()` par `date_paid` en requête si le volume le justifie | **Appliquée** (différée, comme autorisé) | Différé explicitement : `A-VOIR.md:22` (« optimisation SQL non urgente différée conformément à l'instruction 7 »). La fusion la classait non urgente ; défaut (conserver) respecté. |
| Déc. technique | Store API : appliquer le défaut prudent sans attendre | **Appliquée** | Confondue avec l'instruction 5 ci-dessus : les deux tunnels sont admis. Reste à arbitrer par Claude après coup (périmètre réel du tunnel côté thème non figé) ; aucun blocage. |

Les deux questions « Pour Imagine » et « À arbitrer par Ced » de la fusion restaient vides de demande concrète : rien à appliquer de ce côté.

## 2. Résultat des tests

Suite scellée rejouée en conteneur jetable : `powershell -File .\wp\tests\rejouer.ps1`.
Isolation confirmée dans la sortie : `network=none ; rootfs=ro ; mount=…/wp:/repo/wp:ro ; ports=none ; cap-drop=ALL ; no-new-privileges` ; `--pull never`, utilisateur `65534`, `timeout 600`.

- **REJEU : 1229 tests, 36926 assertions, 0 échec, 0 erreur, 0 ignoré — PASS.**
- **OUTILS : 23 outils, 852 contrôles, 0 échec ; hors rejeu : aucun.**
- `imagine-site` : `OK (256 tests, 3169 assertions)`.
- `CodesSuivisC30AdapterTest` : 7 tests / 155 assertions, 0 échec (les 7 cas listés ci-dessus présents dans le JUnit).
- `CodesSuivisC30Test` : 2 tests / 10 assertions, 0 échec (dont l'assertion `2026-affiche`).

Hausse cohérente depuis la fusion (qui relevait « 1219 tests » côté Claude) : +10 tests, dont les 7 cas de l'adaptateur. Le nouvel adaptateur est bien le filet déterministe demandé à l'instruction 2 : il exerce sur bouchons les chemins Woo qui avaient laissé passer I1 et I2.

Rejeu *live* (`verifier.py --live`, parcours navigateur, preuve prix renforcée de l'instruction 3) : **non relancé par le vérificateur.** Il exige un staging WooCommerce vivant ; la doctrine §3 interdit l'accès à un site sans GO écrit. Preuves archivées par Hermès : `correction-native-final-V2.json` (32 contrôles, paniers/commandes Woo réels), `correction-unit-final-V2.json` (9 tests / 165 assertions), `correction-browser-final-V2.json` (99 contrôles), `reception-corrections-V2.json`. Non ré-exécutées de façon indépendante.

## 3. Régressions et modifications non demandées

- **Aucune régression détectée dans le périmètre C-30.** La suite complète (1229 tests) est verte ; aucun fichier de lot clos (C-16/C-19/C-21/C-27) n'est modifié par les corrections — le diff ne touche que `CodesSuivis*`, la section C-30 du `README`, les tests C-30 et les outils de démo `c30-*`.
- **`CodesSuivisRegles.php` inchangé** : conforme au défaut prudent de l'instruction 4 (texte corrigé, validateur conservé). Cohérent.
- **Hors périmètre, non imputable à C-30** : la fenêtre `225d2a7f..HEAD` contient aussi des fichiers du **lot C-33** (`wp/outils/demo/c33*.py`, `wp/tests/demo/c33-runtime.php`, `tests/ComptesPublicsC33Test.php`, et fichiers non suivis `ComptesPublics*.php`), fruit d'un travail parallèle. Ils ne font pas partie de C-30 et ne constituent pas une régression de C-30 ; `ComptesPublicsC33Test` passe dans la suite. À vérifier dans le tour propre à C-33, pas ici.
- **Archive de préimage** : `production/C-30/avant-corrections-V2/` conserve l'état relu (code, PRET, A-VOIR). Ajout documentaire, sans effet sur le produit. Conforme.
- Point résiduel non bloquant, déjà noté en fusion et **non résolu par choix** : la preuve prix renforcée (instruction 3) et les parcours invités *live* ne vivent que dans la recette `--live`, hors suite scellée. L'adaptateur couvre la même logique sur bouchons ; l'écart de preuve restant est donc réduit, mais la garantie « prix inchangé » n'est prouvée de façon rejouable que par la recette live archivée, pas par le conteneur scellé. Acceptable au vu de l'adaptateur ; à garder en tête si Ced veut une preuve prix 100 % scellée.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les 7 instructions et la décision technique de `corrections/C-30.md` sont appliquées ; I1 (commandes invitées à l'export et à l'effacement) est corrigé et couvert par un test scellé, de même que I-B (Store API), I-C (adaptateur Woo), I2 (preuve prix) et M1 (aide/validateur). La suite scellée est verte (1229 tests, 0 échec ; outils 852 contrôles, 0 échec), avec isolation confirmée. Aucune régression dans le périmètre C-30, aucun lot clos modifié.

Réserves non bloquantes transmises à Ced, pas des problèmes de fond :
1. Le rejeu *live* (preuve prix renforcée, parcours invités) n'a pas été ré-exécuté par le vérificateur (doctrine §3 : pas d'accès staging sans GO) ; il repose sur les preuves archivées d'Hermès.
2. La garantie « prix inchangé » n'est rejouable de façon scellée que via l'adaptateur sur bouchons ; la preuve au calcul Woo réel reste en recette live.
3. Le raccord Store API est prouvé sur le hook natif et en bouchons, non sur un paiement HTTP Store API réel ; l'arbitrage « après coup » de la décision technique (tunnel réellement retenu par le thème) reste ouvert côté Claude, sans bloquer la clôture de ce lot de code.

Rappel doctrine §6 : ce verdict de vérification **n'est pas un GO** au sens du §3 ; il ne vaut que pour la clôture de ce lot de code, et l'attention de Ced reste requise sur ce qui lui est signalé ci-dessus.
