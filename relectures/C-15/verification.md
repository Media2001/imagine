# Vérification C-15 — second et dernier tour

Vérificateur : Claude. Objet : contrôler que les huit instructions de `corrections/C-15.md` sont appliquées après correction par Hermès, relancer les tests, repérer toute régression.

Méthode : `git diff 2876aea..HEAD` (baseline = état relu, juste avant le début des corrections à 21 h 28) sur les fichiers C-15, lecture des versions courantes, déroulé manuel des tests purs. **Ce n'est pas une relecture complète** : je ne reprends que le périmètre des corrections.

Fichiers cœur vus : `wp/plugins/imagine-site/EcheancesRegles.php`, `EcheancesNatives.php`, `EcheancesAdmin.php`, `tests/EcheancesReglesTest.php`, `wp/tests/demo/c15-unit.php`, `wp/outils/demo/c15.py`.

## 1. Instructions de corrections/C-15.md

| # | Instruction | État | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | (R1) Élargir mandats pour conserver les prélèvements papier réellement dus en `on-hold`, sans doublonner la projection ; ne pas admettre tout `on-hold` en bloc ; états C-09 | **Appliquée** | `EcheancesRegles.php:17-41` (branche `due` qui remplace la projection, `continue`) ; `EcheancesNatives.php:94-105` (renouvellements même propriétaire, `shop_order`, sans remboursement, passerelle vide/`imagine_papier`). Admission bloc écartée : l'`on-hold` sans dette tombe dans la branche `etat === 'active'` et sort (`EcheancesRegles.php:38`). États C-09 : voir §4. |
| 2 | (R2) Exclusion mutuelle par commande autour de relecture→`payment_complete()`→note ; relire après verrou ; libérer en `finally` ; examiner un refus natif | **Appliquée** | `EcheancesAdmin.php:130-160` : `GET_LOCK` (5 s), relecture `EcheancesNatives::virement` **après** acquisition (l.142), `$completed !== false` examiné (l.145), `RELEASE_LOCK` en `finally` (l.157), `catch (\Throwable)` → 409 (l.151-162). Verrou non acquis ⇒ exception ⇒ 409. |
| 3 | (C1) Porter les règles pures dans `tests/EcheancesReglesTest.php`, découvert par T01 | **Appliquée** | Nouveau `wp/plugins/imagine-site/tests/EcheancesReglesTest.php` (139 l., 7 méthodes PHPUnit). Découverte par T01 attestée par Hermès (`corrections-t01.log`, « 9 tests purs / 45 assertions nommés au JUnit ») — **non rejouée par moi**, voir §2. |
| 4 | (R3) Renforcer `c15-unit.php` : bornes J+30/J+180 exactes + voisines ±1 s, égalité d'échéance en ordre d'ID inverse, objet sans date | **Appliquée** | `c15-unit.php:59-81` : boucle sur 30/90/180 avec `bound`, `bound+1`, `bound-1`, `prochaine=0` ; départage par ID (id9/id3 même échéance → `[8,3,9]`) ; cas `on-hold` dû + payé + `on-hold` sans dette. Couvert aussi dans `EcheancesReglesTest.php:19-37`. |
| 5 | (R4) Afficher les libellés **français** des statuts natifs, échappés ; conserver les identifiants pour filtres | **Appliquée** | `EcheancesAdmin.php:193-205` (méthode `etat()`, tables commande/souscription, repli « État natif non reconnu ») ; appel échappé `EcheancesAdmin.php:248`. |
| 6 | (C5) Lister un mandat papier réel sans référence avec « Référence manquante » au lieu de l'exclure | **Appliquée** | `EcheancesRegles.php:21` (`trim(...) === '' → 'Référence manquante'`) ; plus de rejet sur référence vide. Test `EcheancesReglesTest.php:125-138` (liste + CSV). |
| 7 | (C4) Énoncer dans `A-VOIR.md` l'inclusion de `pending`/`on-hold` dans `echeances` | **Appliquée** | `production/C-15/A-VOIR.md:35` (« La vue échéances inclut `pending` et `on-hold`… ce n'est pas une décision de droit d'accès »). |
| 8 | (C2) Conserver `Montant`+`Devise` au CSV et le mentionner au RAPPORT comme écart assumé aux 4 champs du §3.13 | **Appliquée** | CSV à 5 colonnes maintenu `EcheancesRegles.php:50` ; écart annoncé `RAPPORT.md:15` et `A-VOIR.md:27,31`. |

Décisions techniques (défaut appliqué) des instructions 2, 3 : conformes au cadre « Hermès applique, Claude arbitre après coup » — rien à rouvrir.

## 2. Résultat des tests

**Je n'ai pas pu ré-exécuter les tests dans cette session.** L'exécution de `php` est refusée (permission, session non interactive, pas d'approbation possible) et le bac à sable est restreint à `C:\Users\Ced\imagine` ; la recette HTTP/native exige le staging vivant, interdit au relecteur. Aucun binaire PHP dans le dépôt.

À défaut, j'ai **déroulé à la main** les assertions pures (les seules indépendantes du réseau et de WordPress) :

- `c15-unit.php:20-22` (echeances 30/90/180) → `[6,1]`, `[6,1,2]`, `[6,1,2]` : **cohérent**.
- `c15-unit.php:59-66` (bornes exactes, voisines ±1 s, tri par ID, `prochaine=0`) → `[8,3,9]` pour `echeances` et `mandats`, aux trois périodes : **cohérent**.
- `c15-unit.php:68-81` (mandat `on-hold` dû sans doublon futur ; référence manquante ; `on-hold` sans dette exclu ; renouvellement payé non représenté) : **cohérent**.
- `EcheancesReglesTest.php` : `testBornesExactes…`, `testMandatsActifsSeulement…`, `testMandatSuspenduExige…`, `testMandatSansReference…`, `testCsv…` : tracés, **tous cohérents** avec la logique de `EcheancesRegles.php`.

Déroulé manuel = les règles pures corrigées produisent les sorties attendues. Ce n'est **pas** un rejeu exécuté : le « vert » global (Hermès : **1 030 tests / 34 124 assertions**, dont 9 purs C15 / 45 assertions, `RAPPORT.md:21-22`, `corrections-t01.log`) **n'a pas été reproduit indépendamment à ce tour**. C'est la même limite qu'au premier tour (fusion §1, « preuve non rejouée indépendamment »), aggravée ici par l'impossibilité de lancer `php`. Les parcours mutex (R2), libellés (R4) et HTTP/export dépendent du site vivant et ne sont attestés que par les journaux d'Hermès.

## 3. Régressions / modifications non demandées

- **Fichiers cœur C-15** (`Echeances*.php`) : aucune modification hors des huit instructions. Pas de régression détectée à la lecture ; branche `active` d'origine préservée (`EcheancesRegles.php:38-41`), tri secondaire par ID conservé.
- **`wp/outils/demo/c15.py` (non demandé, défendable)** : `deploy()` n'écrase plus le bootstrap partagé `imagine-site.php` (retiré de `FILES`, contrôle de non-écrasement par empreinte avant/après). Va dans le sens de la doctrine (ne pas toucher le socle B02 partagé) et réduit un risque ; aucun impact sur le code livré. Signalé, pas bloquant.
- **Hors périmètre C-15** : le diff depuis la baseline contient aussi B-02, B-04, A-08/A-09/A-10 et MonCompte (autres lots menés en parallèle). Non évalués ici ; sans rapport avec C-15, aucun des trois `Echeances*.php` n'en dépend.
- Aucun secret, aucune donnée réelle, aucun IBAN introduits. CSV toujours neutralisé contre les formules (`EcheancesRegles.php:53-56`).

## 4. Point de réserve (non bloquant)

Instruction 1, volet « ajouter au catalogue C-09 les états *renouvellement exigible non payé* / *renouvellement payé* » : Hermès ne crée pas de nouveau profil (interdit — catalogue C-09 hors de son périmètre) ; il **exerce** ces deux états par transition native WCS sous le A-PAPIER existant, puis restaure (`A-VOIR.md:37-39`, `RAPPORT.md:31`), en concluant « aucun état manquant ». Interprétation fidèle à la consigne « ne pas créer de profil hors C-09 ; si un état manque, le dire ». Conforme, mais c'est une démonstration transitoire, pas une fixture permanente du catalogue : à confirmer par le rejeu réel de Ced.

## 5. Verdict

**Prêt pour la validation de Ced.**

Les huit instructions sont appliquées, au bon endroit, avec une logique pure correcte au déroulé. Aucun problème de fond restant dans le code ; aucune régression sur le périmètre C-15. Ce n'est pas un GO (doctrine §6) : C-15 est un **écran d'administration**, sa validation est visuelle et revient à Ced (`A-VOIR.md`, cinq vues + export + libellés français). Deux questions métier (Q1 commandes à l'unité, Q2 `on-hold`) restent ouvertes pour Imagine avec défaut prudent appliqué — non bloquantes.

**Réserve à porter à Ced** : le « vert » (T01 global et parcours mutex/HTTP) n'a **pas** été rejoué indépendamment, ni au premier tour ni à celui-ci — contrainte d'environnement, non défaut de code. Le rejeu effectif sur staging vérifié reste dû avant clôture.
