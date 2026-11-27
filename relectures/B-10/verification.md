# Vérification B-10 — points de vente (2e et dernier tour)

Vérificateur : Claude. Base relue : état du dépôt à `28a4d454` (fusion `corrections/B-10.md` écrite, code pas encore corrigé).
Méthode : `git diff 28a4d454 → arbre de travail` sur `wp/` et `production/B-10`, relecture ciblée des zones modifiées, relance des tests.
Je n'ai pas refait de relecture complète ; je vérifie seulement l'application des 8 instructions, les tests et l'absence de régression.

Fichiers B-10 corrigés : `PointsVente.php`, `PointsVenteRegles.php`, `tests/PointsVenteReglesTest.php` (+1 test), `tests/PointsVenteAdapterTest.php` (nouveau), `tests/PointsVenteWPStubs.php` (nouveau), `README.md` (section B-10), `NOTE.md`, `A-VOIR.md`, outils/preuves `wp/outils/demo/b10-*`, `wp/tests/demo/b10-*`, `production/B-10/corrections-*-V2.*`.

## 1. Instructions de `corrections/B-10.md`, une par une

| # | Instruction | État | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | **I1** désaccentuation complète (Normalizer FORM_D si intl, + `œ→oe`/`æ→ae`, + repli latin étendu) + test NFC/NFD hors table + `œ/oe` | **Appliquée** | `PointsVenteRegles.php:18-39` (bloc intl + ligatures + table étendue avant retrait `\p{M}`) ; test `PointsVenteReglesTest.php:14-25` (`ḉ/ǵ/ǘ` absents de l'ancienne table, formes précomposée+décomposée+désaccentuée, `Œuf-Æther`→`oeuf-aether`) |
| 2 | **I2** nettoyage repris et non destructeur : persister les IDs avant bascule, retenter même au rejeu identique, distinguer « remplacée ; nettoyage incomplet » d'un import refusé + test échec de suppression puis rejeu identique | **Appliquée** | `PointsVente.php:81-107` (`retenirNettoyage` persiste avant bascule l.146 ; `nettoyer` ne touche ni actif ni type étranger l.96-101) ; no-op qui relance le nettoyage `:127-130` ; drapeaux `remplace`/`nettoyage_complet` `:153-154` ; tests `PointsVenteAdapterTest.php:45-58, 110-134` |
| 3 | **M1** motifs de refus en libellés français traduisibles à l'affichage, codes gardés pour les tests, sans valeur du CSV | **Appliquée** | `PointsVente.php:214-224` (`libelleRefus` en `match`+`__()`) ; appliqué à l'affichage `:276` ; codes conservés dans le résultat de `charger` ; test `PointsVenteAdapterTest.php:79-93` |
| 4 | **C1** `try/catch` autour du contrôle d'idempotence `self::lignes() === …` pour poursuivre le remplacement si l'ancienne liste est illisible | **Appliquée** | `PointsVente.php:122-126` (`catch (RuntimeException) → $identical = false`) ; test `PointsVenteAdapterTest.php:95-108` (méta active supprimée → réparation par remplacement) |
| 5 | **C3** lire `self::configuration()` une seule fois hors boucle d'affichage | **Appliquée** | `PointsVente.php:175` (`$config = self::configuration()`), réutilisé `:187` et `:197` ; test `PointsVenteAdapterTest.php:70-77` (1 seule lecture de `CONFIG`) |
| 6 | **C2** (au choix) normaliser l'ordre des clés *ou* documenter la limite | **Appliquée** (option « documenter » retenue) | `NOTE.md:24` + `README.md` (section B-10) : limite C2 déclarée, pas de normalisation du mapping ajoutée. Conforme au choix laissé par l'instruction. |
| 7 | **C4** aligner les chiffres de preuve une fois B-11 stabilisé et re-geler la régression | **Appliquée** | `NOTE.md:30` et `A-VOIR.md:50` : chiffres frais **1 187 tests / 36 494 assertions**, B-11 déclaré stable ; `production/B-10/corrections-regression-V2.*` (preuve re-gelée) ; historiques 1 175/1 176 conservés, non substitués |
| 8 | **C5** noter que la liaison page↔extension devra passer du seed démo à un script de bascule versionné (hors lot) | **Appliquée** | `NOTE.md:25` (« Vraie bascule, hors lot… aucun script de production créé ici ») + `README.md` section B-10 (« hors lot ») |

**Bilan : 8 / 8 appliquées.** Le diff des deux fichiers de code (`PointsVente.php`, `PointsVenteRegles.php`) correspond exactement aux instructions, sans ajout parasite.

## 2. Résultat des tests

- **Vérificateur autonome, hors réseau** (`python -B wp/tests/demo/b10-verifier.py`) :
  `B10 PASS : 45 empreintes ; 14 tests unitaires ; 80 assertions ; 13 contrôles natifs ; 31 contrôles navigateur`
  `GLOBAL : 1187 tests ; 584 contrôles outils ; paquets hors B10 : [A-32 / A32_PARTIAL_EVIDENCE]`
- **Ré-exécution live de la suite PHPUnit B-10** en conteneur jetable isolé hors réseau (`python -B wp/outils/demo/b10-local.py …`, log supprimé pour ne pas écrire dans `production/`) :
  `PHPUnit 11.5.58 / PHP 8.2.33` → `OK (14 tests, 80 assertions)`. L'image de test n'ayant pas `Normalizer`, c'est le **chemin de repli latin** (sans intl) qui a réellement tourné au vert. Le chemin intl est, lui, couvert par les 13 contrôles natifs (WordPress a `Normalizer`).
- **Portée de mon rejeu** : j'ai confirmé par ré-exécution indépendante les **14 tests / 80 assertions** B-10 (chemin sans intl) et, via le vérificateur autonome, la cohérence du décompte global **1 187 / 36 494** et des preuves gelées. Je n'ai **pas** pu relancer la régression complète `wp/tests/rejouer.ps1` dans cette session (le bac à sable du harnais refuse le sous-processus PowerShell/Docker imbriqué) ; le 1 187 global repose donc sur la preuve re-gelée (`corrections-regression-V2`) relue par le vérificateur, pas sur un rejeu T01 refait par moi. La couche WordPress de I2/C1 (reprise entre requêtes, réparation de liste illisible, masquage) reste prouvée par les recettes d'Hermès et par les stubs PHPUnit `PointsVenteAdapterTest`, pas par un readback sur site.

Aucun test en échec. `A-32 / A32_PARTIAL_EVIDENCE` reste signalé **hors B-10** (aucun fichier du lot concerné).

## 3. Régressions et modifications non demandées

- **Dans les fichiers B-10** : aucune. Le diff se limite aux 8 corrections ; aucun comportement du lot n'a été altéré hors instruction.
- **Hors B-10, présentes dans l'arbre** : des chantiers parallèles **B-11** et **C-28** ont atterri dans l'arbre de travail (`b11-*`, `c28*`, `PacksRegles.php`, `PacksThematiques.php`, `PacksC28Test.php`, `MediasB11Test.php`, `single-product.php`, `AchatsNumeros.php`, et `imagine-site.php` qui charge les Packs C-28). **Ce ne sont pas des régressions B-10** : ils sont hors périmètre du lot et n'ont pas été introduits par la correction B-10. L'ajout dans `imagine-site.php:174-178` est purement additif (chargement C-28) et **ne touche pas** l'enregistrement de `PointsVente` → aucun effet sur B-10. La suite globale reste au vert (1 187), ce qui confirme l'absence de régression croisée.
- Le point C4 est ainsi réglé : l'écart de décompte 1 175/1 176 relevé au 1er tour (imputé à B-11 en cours) est résorbé, B-11 étant maintenant déclaré stable et le décompte frais gelé.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les deux points importants (I1, I2) et tous les mineurs (M1, C1, C2, C3, C4, C5) sont traités ; les tests du lot sont au vert, y compris le chemin de repli désaccentuation ré-exécuté en isolation ; aucune régression sur B-10. **Aucun problème de fond ne reste** à remonter.

Ce verdict n'est pas un GO (doctrine §6). Restent, comme prévu par la fusion, les points qui relèvent **de Ced et d'Imagine, pas d'un défaut de code** :
- **Ced (visuel/réel)** : valider le rendu public (squelette B-01, `production/B-10/page-mobile.png`) et l'écran d'admin ; confirmer le maintien des données entièrement fictives jusqu'à la vraie base.
- **Imagine (métier)** : confirmer la recherche **exacte** (défaut prudent appliqué : localité/code postal exacts, insensibles casse/accents, sans préfixe ni rayon) ou demander préfixe/rayon.

Ces questions sont précisément l'objet de la validation de Ced ; elles ne bloquent pas la clôture côté code.
