# Vérification C-09 — second et dernier tour

Vérificateur : Claude. Date : 23/11/2026.
Base relue : commit `7a384c0` (corrections C-09). Diff examiné : `7a384c0..HEAD` sur `wp/` et `production/C-09/`.
Portée : contrôle ciblé des 9 instructions de `corrections/C-09.md` + arbitrages §5. Pas de relecture complète refaite.

## 1. Instructions de `corrections/C-09.md`

| # | Instruction | État | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | A-VOIR — justesse du calendrier (C09-03) | **Appliquée** | `production/C-09/A-VOIR.md` : « Calendrier de parution 2026–2028 complet : 15 parutions » ; distingue calendrier / 5 numéros matérialisés / raccords absents (Lecture des résultats + proposition 12). Assertion `calendrier_15_parutions_complet` dans `wp/tests/demo/c09-corrections.php:65`. |
| 2 | Grille tarifaire fictive (C09-02) | **Appliquée** | `wp/outils/demo/c09-seed.php:63-71, 118-132` crée 6 produits Subscription privés/cachés `c09-tarif-fictif-*` à valeurs synthétiques (120/60/240 ÷ 1|4) ; rattachement A-CARTE→normal-1, A-SEPA4→normal-4, A-PAYPAL→normal-1, A-PAPIER→normal-4 (`c09-profils.json:8-14`). Contrôles `c09-corrections.php:11-39`. *Réserve mineure : A-CARTE et A-PAYPAL restent identiques en montant/périodicité (normal-1) ; l'indistinction du moyen de paiement subsiste, honnêtement déclarée.* |
| 3 | E-REDAC reclassé + assertion capacité (C09-01) | **Appliquée** | Reclassé `partiel`, raccord nommé « pas d'écran d'édition du calendrier pour editor » (`c09-profils.json:30`, `A-VOIR.md`). Contrôle `contenus_calendrier` ajoute `!user_can($id,$calendarCap)` (capacité réelle = `option_page_capability_options`, soit `manage_options`) + `etat==='partiel'` (`c09-runtime.php:99-102`). Confirmé par `c09-corrections.php:40-43`. |
| 4 | Restauration du plan d'adhésion (C09-04) | **Appliquée** | Rejeu passe par `wc_memberships_create_user_membership(['user_membership_id'=>…,'plan_id'=>$planId])` qui réaffecte le plan (`c09-seed.php:275-278`). Test dédié `c09-plan.php` (altération → reset → plan restauré **et** décision `abonnement_actif` → nettoyage relu) ; altération aussi exercée dans `c09-reset.py:19-21, 44-46` (`plan_altere_et_detecte`, `plan_et_decision_restaures`). |
| 5 | Garde hors ligne passive (C09-06) | **Appliquée** | `c09-seed.php:12-30` : inspection `has_filter` + closures issues du MU-plugin **avant** tout acte ; n'exerce que les filtres (`apply_filters`), jamais `wp_mail`/`wp_remote_get`. Cas « fichier présent, filtres morts » + sentinelles non appelées testés dans `c09-safety.php:25-49`. |
| 6 | A-PAPIER — horloge injectable (C09-05) | **Appliquée** | Horloge injectable `now()`/`papierDue()` dans `wp/outils/demo/c09-calendar.php` (`$GLOBALS['imagine_c09_now']`). Seed l'utilise (`c09-seed.php:103, 259`). Cas dernière seconde du mois + passage d'année dans `c09-clock.php:13-28`. |
| 7 | Renouvellement des profils abonnés (arbitrage §5.2) | **Appliquée** | Arbitrage tranché : « renouvellement activé non démontrable sur la démo hors ligne » écrit en toutes lettres pour A-CARTE/A-ECHEANCE (`c09-profils.json:8,20` ; `A-VOIR.md`), daté « accepté le 23/11 à 21h10 ». Le drapeau natif reste manuel, sans jeton. |
| 8 | Nettoyage `profils.py:17` | **Appliquée** | `wp/outils/demo/profils.py:17` : la condition `startswith` redondante est supprimée ; ne reste que `slug != 'imagine-test-demo'`. Garde toujours validée par `test_c09_profils.py` (rejette `imagine-test-autre`, `production`, etc.). |
| 9 | Rubric « créé/partiel » | **Appliquée** | Définition stable posée dans `A-VOIR.md` (« Classement strict uniforme (arbitrage 21h10) ») et appliquée : E-REDAC et V-INSCRIT en `partiel`. Décomptes régénérés : 4 créés / 25 partiels / 1 impossible (`verification-finale.json`, `RAPPORT.md`). |

**Arbitrages §5 appliqués au-delà de C-09 (voir §3) :** A-VIR (`virement_non_valide`) et E-ABO (rôle dédié `imagine_referent_abonnements` au lieu de `shop_manager`) ont été tranchés par Ced puis implémentés.

## 2. Résultat des tests

- **Rejoué localement par moi** : `python -B -m unittest discover -s wp/tests/demo -p test_c09_profils.py -v` → **7/7 au vert** (0,64 s). C'est la seule suite rejouable hors site, conformément aux droits du relecteur (pas d'accès à `imagine-test-demo`).
- **Résultats de livraison (non reproduits ici, faute d'accès au site)** — `production/C-09/*.json` : natifs 377/377, http 197/197, sécurité 10/10, reset 6/6, régression C-08 30/30, intégrité 8/8, corrections 41/41, **horloge 11/11** (`clock.json`), **plan 4/4** (`plan.json`), **sécurité garde passive 10/10** (`safety.json`). Total annoncé 691, 0 échec. Les red-*.json montrent les échecs attendus observés avant correction.
- Ces décomptes site restent des **preuves de livraison d'Hermès**, pas une exécution indépendante — le rejeu réel sur le NUC par Ced reste dû (comme au premier tour).

## 3. Régressions / modifications non demandées

- **A-VIR traité dans C-08, pas seulement constaté (à confirmer par Ced).** `corrections/C-09.md` §5.1 disait explicitement « ne pas corriger dans C-09 ». Le motif a bien été changé : `wp/plugins/imagine-site/Paywall.php:185-189` renvoie désormais `virement_non_valide` pour une souscription `pending`. `RAPPORT.md` l'annonce « arbitré… corrigé dans C08/C10 » et « accepté à 21h10 ». Je ne vois pas le GO écrit de Ced ; je le signale pour confirmation. **Ce correctif vit dans C-08/C-10, à valider là, pas à clore sous C-09.**
- **`Paywall.php` (C-08) a reçu de larges changements hors périmètre C-09**, dans la même fenêtre de diff : cache de décision par requête + invalidation par contexte (`:16-40, 54-66`), paywall de recherche SQL `posts_search`/`posts_orderby` (`:306-356`), schéma JSON-LD passé en `NewsArticle`, durcissements `metadata_exists`, reconnaissance du rôle `imagine_referent_abonnements` comme équipe (`:134`). Rien de tout cela n'est demandé par `corrections/C-09.md`. C'est du travail C-08/C-10 ; non vérifié ici ; le filet est la suite `regression_c08` (30/30, livraison). À valider sous C-08/C-10.
- **Diff large hors C-09** : le diff `wp/` touche aussi b01, c08-*, c10-*, imagine-pilotage, thème. Hors sujet C-09 ; non examiné. Aucun fichier `docs/` modifié (conforme).
- **Incident tracé, non masqué** : `RAPPORT.md:40` signale une mutation transitoire du numéro fictif B00 ID32 (seed inclus par erreur dans une recette), restaurée et relue égale au snapshot initial ; seed désormais isolé en closure dans les tests plan/horloge. À noter, pas un défaut résiduel.
- Aucune autre régression décelée sur les fichiers C-09 ; les tests natifs/corrections comparent maintenant à des attentes **indépendantes du catalogue** (`c09-corrections.php`), ce qui lève la circularité notée au premier tour.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les 9 instructions de `corrections/C-09.md` sont **toutes appliquées** et prouvées au code ; les deux arbitrages §5 (A-VIR, E-ABO) sont tranchés et implémentés ; la suite locale est au vert. Aucun problème de fond résiduel sur C-09.

Deux points relèvent de la validation de Ced, pas d'un blocage C-09 :
1. Confirmer que l'arbitrage du 23/11 ~21h10 couvre bien le correctif A-VIR porté dans **C-08/C-10** (`Paywall.php`), que `corrections/C-09.md` demandait de ne pas toucher dans C-09.
2. Le rejeu réel des suites site sur le NUC reste dû : les décomptes 691/0 sont une livraison d'Hermès, non reproduite par le relecteur (pas d'accès à `imagine-test-demo`).

> Ce verdict n'est pas un GO au sens de la doctrine §3/§6.
