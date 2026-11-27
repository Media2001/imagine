# C-26 — Rapport de livraison corrigée du 27 novembre

- **Fait** : dix corrections C-26 appliquées après B-08 corrigé : témoins complets, droits distincts, archive, oracle B06 indépendant, vérificateur intégral/privacy et restaurations sur erreur.
- **Prêt à relire** : C-26, sur les sources et reçus nommés dans `A-VOIR.md` et `manifest.json` ; les deux relectures restent au circuit parent.
- **À arbitrer par Ced** : rien de nouveau ; aucune règle métier ni aucun droit choisi pour les besoins du test.
- **Bloqué** : aucun gate métier/runtime restant. Modifications limitées C26 et deux sources de test C23 autorisées ; aucun changement durable plugin/paywall/thème, aucun autre site, bibliothèque close, verrou, file ou rapport parent.
- **Ensuite** : retour au parent, sans prendre un autre lot.

## Preuves

- Livraison fraîche **après restauration des mutations** : **3 966 contrôles**, verts, zéro fuite : C23 1 922 + C26 1 980 + privacy 64. C26 : 132 voies × 15 publics, `/evenements/` incluse. C23 : 18 identités/inverses/faux Bing supplémentaires exigés exactement ; 35 voies B06 non doublées.
- **Huit familles de mutations** détectées : quatre mauvais titulaires vers les vrais callbacks (15 tiers rouges chacune), statut B06 persisté/GET, Soutenir avec phrase C08 **et** B06, vrai template d'archive avec phrase C10, et vraie décision `autorise()` mutée **avant inventaire**. Aucun résultat fabriqué en mémoire ; sources restaurées et relues.
- **52 tests Python 3.11.15** (42 antérieurs + 10 régressions), UTF-8/cp1252, sans TMPDIR et réseau bloqué ; trois cycles rouge/vert enregistrés. Image reconstruite par le script existant après ajout des tests, code 0, T01 IMAGE READY.
- Vérificateur offline **77/77**, code 0 ; qualification **20/20 falsifications refusées**, dont 19 reçus rescellés et une source déclarée fausse. Reçus `verification-finale.json`/`qualification-finale.json` ; réseau/écriture bloqués, production inchangée. Exemples : identités/inverses retirés avec total ajusté, inverse privacy vide requalifié `positive=False`, identité dupliquée, échec caché hors grille.
- État métier, profils et actions planifiées identiques avant/après ; quatorze collections métier comparées exactement et relues ; préimages durables privées avant toute session/fixture ; sources live et bootstrap courant inchangés.

## Décisions prudentes et écarts

- Adaptation minimale C23 autorisée : `c23.py` extrait sans modification sa reconnaissance des témoins dans `reserved_witnesses()` ; `c23-inventaire.php` expose réglages/rôles et statut bruts, séparés de la décision native observée. Oracle C26 : P-COOP documenté, rôles/réglage livrés ; décision native comparée, pas prise comme attendu. SHA historiques C23 changés, ancien paquet non rescellé.
- Découverte livrée fermée conservée : V-DEC-FIN est sans droit ; aucun cas ouvert/épuisé prétendu rejoué. V-DEC sert seulement de propriétaire fictif des nouvelles données temporaires, sans lecture consommant sa découverte.
- Les appels de flux sur types privés sont des sorties HTTP réellement inspectées mais, sur cette version native, replient sur les articles publics : pas de fausse preuve d'un flux privé non vide. Inverses privacy réels pour l'existence des données.
- Les logs rouges de correction démontrent les défauts avant code corrigé. Les pannes cleanup/B06 et relecture sont testées offline : chaque autre restauration continue, un reçu est produit ; le refus de dérive est conservé. Deux sentinelles C26 remplacent les témoins datés dans les seules fixtures temporaires ; elles ne qualifient pas la validation des dates métier.
- Les 35 anciennes injections B06 en mémoire restent des tests de détecteur, non crédités comme 35 mutations applicatives. Fichiers et fonctions B06 à relire nommés précisément dans `A-VOIR.md`.

## Fichiers

Modifiés ce tour : `wp/outils/demo/c26.py`, `c26-preparer.py`, `c23.py`, `c23-inventaire.php`, `wp/tests/demo/c26-fixture.php`, `c26-tests.py`, `c26-verifier.py`, `c26-paquet-tests.py`, `production/C-26/` (sceller, A-VOIR, inventaire, matrices/reçus neufs, logs rouge/vert, tests/image, qualification et sceau). `c23-tests.py` conserve son correctif TMPDIR antérieur, non modifié ce tour. Rapport de voie 2 dans `files/rapports/*-V2.md`. Aucun Git. B07 non élargi. PRET ne vaut ni validation visuelle ni clôture Claude.
