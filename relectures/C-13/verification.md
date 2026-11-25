# Vérification C-13 (2e et dernier tour)

Vérificateur : Claude. Date : 25 novembre 2026.
Base relue : commit `49176d1` (état au moment de `corrections/C-13.md`, 13:39). Diff examiné : `git diff 49176d1 HEAD -- wp/ production/C-13`.
Portée : contrôle ciblé des 7 instructions de `corrections/C-13.md`, relance des tests autonomes, recherche de régression. Pas de nouvelle relecture complète. La recette HTTP (site vivant) reste interdite au relecteur et n'a pas été rejouée.

## 1. Instructions de `corrections/C-13.md`

**Instruction 1 — Raccorder les bénéficiaires offerts et groupés (Bloquant). → Appliquée.**
Nouveau fichier `EnvoiRelations.php:10-89` : lecture des liens natifs cadeau (WCS Gifting, `_recipient_user`) et groupe (Memberships `_subscription_id`, capacité = quantité produit du plan). `EnvoiRegles.php:191-220` construit les `Destinataire` depuis `beneficiaires` selon l'origine, avec `beneficiaires_resolus`. L'export se ferme si un bénéficiaire requis n'est pas résolu (`EnvoiRegles.php:217-220`, motif `beneficiaires_non_resolus`). L'identité/adresse du bénéficiaire n'est jamais remplacée par le payeur (`EnvoiRelations.php:58-59`). Testé : cadeau résolu, groupe de 3 places dont 2 attribuées → 2 lignes, non résolu → export fermé (`tests/EnvoiReglesTest.php:50-72`).

**Instruction 2 — Raccorder les renouvellements à C01 (Important). → Appliquée.**
`EnvoiRelations.php:110-130` lit les commandes de renouvellement réellement payées (anti-remboursement, propriétaire cohérent) ; `EnvoiRegles.php:170-171` appelle `Moteur::renouveler()` sur le bloc suivant sans déplacer la date initiale. Garde-fou métier : sans rang explicite, seul l'annuel intervalle 1 est reconnu, une échéance trimestrielle n'ouvre pas une année (`EnvoiRelations.php:117`). Testé : renouvellement payé → bloc 2027 (`2027-T1..T4`), début initial inchangé, renouvellement non payé → liste vide (`tests/EnvoiReglesTest.php:74-87`, `167-176`).

**Instruction 3 — Rendre le gel réellement immuable (Important). → Appliquée.**
Le gel persiste calendrier, clôture, observations et blocs (`EnvoiRegles.php:77-85` `figer`), et la relecture `relire` (`:87-100`) recalcule sur la référence historique, indépendamment de l'option courante. `EnvoiNatif.php:188-237` : premier gel gagnant, relecture via `relireGel`. L'immuabilité des clôtures passées passe désormais par `Calendrier::modifier()` dans `reviserCalendrier` (`EnvoiRegles.php:59-60`) au lieu d'un `new Calendrier()` qui contournait la garde ; les écritures de l'option calendrier et des clés de gel sont filtrées (`EnvoiNatif.php:154-170`). Testé : snapshot résistant à une modification de bénéficiaire postérieure (`tests/EnvoiReglesTest.php:137-156`) ; clôture passée immuable, clôture future modifiable (`:103-112`).

**Instruction 4 — Banc local autonome pour les règles du raccord (Bloquant). → Appliquée.**
`EnvoiRegles.php` ne contient aucune fonction WordPress : horloge, calendrier et observations sont injectés. Banc exécutable sans site via `phpunit.c13.xml` + `tests-c13/bootstrap.php`, lancé par `wp/outils/demo/c13-unit.py` (conteneur `--network none`, `--read-only`). `EnvoiNatif` est réduit à un adaptateur qui délègue à `EnvoiRegles` (`EnvoiNatif.php:240-243`). Doctrine §4 respectée. **Rejoué par moi** : voir §2.

**Instruction 5 — Libellé `non_eligible` (Mineur). → Appliquée.**
`ListeEnvoiAdmin.php:209` : `'non_eligible' => 'Non éligible à l'envoi'`. Le cas est bien celui produit par `EnvoiRegles.php:233`.

**Instruction 6 — Aligner `RAPPORT.md` / `A-VOIR.md` (Mineur documentaire). → Appliquée.**
La contradiction relevée a disparu. Avant : `RAPPORT.md:2` disait « PRET retiré par le parent », `A-VOIR.md:3` disait « PRET redéposé ». Après : `RAPPORT.md:2` et `A-VOIR.md:3` portent le même état (« prêt à relire », `recette_complete=false`, ni acceptation, ni validation visuelle, ni clôture ; PRET relève du parent). Le fichier `PRET` est cohérent (« corrections techniques soumises à relecture », strict exit 2). Défaut §5.3 respecté.

**Instruction 7 — Reporter les écarts dans `docs/ecarts.md`. → Non faite par Hermès, à la charge de Claude (conforme).**
Un worker ne peut pas écrire dans `docs/` (CLAUDE.md « Droits », doctrine §7 : « Claude le reporte »). Hermès a correctement laissé les trois écarts en propositions dans `RAPPORT.md:25-29` (« Limites et écarts proposés à Claude »), sans toucher `docs/`. Le report effectif dans `docs/ecarts.md` reste une action du fusionneur/Claude, hors de la responsabilité d'Hermès.

## 2. Résultat des tests

- **Banc pur C-13 (rejoué par moi)** : `python wp/outils/demo/c13-unit.py` → **10 tests, 30 assertions, 0 échec, code 0, `network: none`**. PHPUnit 11.5.58 / PHP 8.2.33. Ces 10 tests couvrent effectivement les instructions 1, 2 et 3 (bénéficiaires offerts/groupés, renouvellements sans déplacement de date, gel immuable, calendrier passé immuable).
- **Suite autorisée T01 (`rejouer.ps1`)** : **non rejouée par moi** — la commande n'a pas obtenu l'approbation dans cette session. Résultat **déclaré** par la production (`resultats-purs.json`) : 1010 tests / 33978 assertions, 0 échec/erreur/ignoré, code 0 ; dont `imagine-site` 46 tests / 230 assertions (C11 conservé + C13). Non reproduit ici.
- **Recette HTTP et strict exit 2** : hors périmètre relecteur (site vivant). `resultats.json` reste `recette_complete=false`, `statut: BLOQUE_ACCEPTATION_C09`, 12/12 souscriptions C09 sans paiement validé, 0 destinataire C09. Résultats déclarés, non reproduits.

## 3. Régressions ou modifications non demandées

- **Aucune régression détectée dans le périmètre C-13.** `imagine-site` conserve ses tests C11 (46 tests). Le banc pur que j'ai rejoué est vert.
- **Modifications C-13 non listées dans les 7 instructions, mais légitimes :** (a) nouveau réglage `imagine_envoi_groupes` (`ferme` par défaut / `liens_memberships`, deux valeurs testées) — c'est l'application de doctrine §4 (« une règle ouverte devient un réglage ») au modèle de groupe de l'instruction 1 ; (b) filtre `woocommerce_prevent_admin_access` borné aux deux routes de l'écran (`ListeEnvoiAdmin.php:32-39`) — correctif nécessaire pour que le Référent accède à l'écran sans élargir ses droits ; (c) nonce de réglages distinct du nonce d'export. Ces ajouts restent dans le périmètre du lot et sont tracés dans `RAPPORT.md`.
- **Point mineur connu, non régressif :** l'écriture de relevés sur affichage GET (`EnvoiNatif.php:204`) subsiste — déjà signalée en Mineur au 1er tour, idempotente, assumée par Hermès (« coût linéaire non qualifié en volume »). Pas une régression.
- **Hors périmètre C-13 :** le diff `49176d1 → HEAD` touche aussi A-01, A-03, A-04, C-14, `staging-court`, B02. Ce sont les commits de synchro d'autres lots menés en parallèle, pas le travail C-13 d'Hermès. Non évalué ici (hors mission).

## 4. Verdict

**Prêt pour la validation de Ced.**

Les 7 instructions de `corrections/C-13.md` sont appliquées (l'instruction 7 relevant de Claude, pas d'Hermès). Les deux Bloquants qui étaient des défauts de **code** — bénéficiaires offerts/groupés non raccordés, et raccord sans couverture autonome / logique métier hors couche pure — sont résolus et couverts par un banc pur que j'ai moi-même rejoué (10 tests / 30 assertions, hors ligne). Les deux Important (renouvellements C01, gel non persisté) sont corrigés et testés. Aucune régression trouvée dans le périmètre C-13.

Ce qui reste n'est **pas** un problème de fond de code, mais relève exactement de Ced / Imagine, et était déjà identifié dans la fusion :

- **Acceptation C-09 (périmètre, touche au réel).** Les 12 profils C-09 restent sans paiement validé ni lien offert/groupé natif : la liste réelle est vide et le livrable « contenu de la liste pour les profils C-09 » n'est pas démontrable **sans inventer de paiement** — ce que la doctrine §3 interdit et qu'Hermès a eu raison de refuser. La question « autoriser un complément postal C-13 fictif rattaché aux profils C-09, oui/non ? » est une décision Imagine/Ced, pas un correctif. Défaut prudent appliqué : gates fermées.
- **Menus C-10/C-13 (visuel).** Cohabitation sous le parent `imagine` à contrôler à l'écran. Ressort de Ced.

Rappels : (1) ce verdict n'est pas un GO au sens de la doctrine §3 ; (2) je n'ai pas pu rejouer la suite T01 complète ni la recette HTTP dans cette session — le chiffre de 1010 tests et le code strict 2 restent des résultats déclarés par la production ; (3) le report des écarts dans `docs/ecarts.md` reste à faire par Claude.
