# Vérification C-07 — second et dernier tour

Date : 22/11/2026. Vérificateur : Claude (relecteur indépendant).
Objet : contrôler l'application des instructions de `corrections/C-07.md` après la remise corrigée d'Hermès (fusion du 22/11, file de 11 h 40).
Base relue au premier tour : état du 21/11 23:38 (`66e3d13`). État vérifié : `HEAD` (`84d2f9c`).
Méthode : `git diff 66e3d13 HEAD` sur `wp/`, lecture du code, scellé de preuve, et rejeu — voir §2 pour la limite d'exécution.

Ce n'est pas une relecture complète ; seuls les écarts corrigés sont repris.

---

## 1. Instruction par instruction

| # | Instruction (fusion §4) | Résultat | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | Grâce indépendante de `paiementValide` + tests grâce sans paiement / grâce fin atteinte | **Appliquée** | `src/Envoi/ListeEnvoi.php:27` (`inclureGrace = true`), `:58-61` (grâce incluse sans condition de paiement ; `actif` reste conditionné au paiement), `:57` (borne `fin <= cloture` conservée). Const `ETATS_EN_REGLE` supprimée. Tests `tests/Envoi/ListeEnvoiTest.php:169` et `:185`. |
| 2 | CX-01 individuel/offert sans destinataire → anomalie `destinataire_manquant` + `abonnement_id` ; groupe exempté | **Appliquée** | `ListeEnvoi.php:66-68`. Tests `ListeEnvoiTest.php:144` (individuel/offert/groupe) et `:160` (non éligible sans destinataire). |
| 3 | CX-03 présence postale insensible aux espaces insécables (U+00A0, U+202F) sur nom/rue/CP/ville/pays | **Appliquée** | `ListeEnvoi.php:130-133` (`normaliserEspaces`, regex `/[\s\p{Z}]+/u`), appliquée en `:89-98`. Test `ListeEnvoiTest.php:265` (30 cas : 5 champs × 3 espaces × vide/entouré). |
| 4 | CX-02 doublons casse accentuée (`mb_strtolower`) + usage `destinataire_id` ; deux exemplaires conservés, chacun signalé | **Appliquée** | `ListeEnvoi.php:101` (`mb_strtolower UTF-8`), `:104-107` (clé d'identité `destinataire_id`), `:109-122` (dédup d'index, une alerte par ligne). Tests `ListeEnvoiTest.php:301`, `:329`, `:345` (ID commun / adresse différente = pas de doublon), `:355` (personnes distinctes non fusionnées). |
| 5 | CX-04 oracle CSV en table de couples littéraux, sans le prédicat de production | **Appliquée** | `tests/Envoi/ExportCsvTest.php:31-67` : 16 couples littéraux, relecture par `fgetcsv` sur les 9 colonnes ; la regex de `CsvProtection` n'est plus recopiée. |
| 6 | `testProfilsACloture` discriminant (attendus métier à la main ; A-SANSMAIL / A-ETRANGER distincts) | **Appliquée** | `ListeEnvoiTest.php:81-132` : attendus littéraux `idsAttendus`, email porté par le compte (`null` pour A-SANSMAIL), A-ETRANGER en pays `FR` vérifié jusque dans le CSV, `assertArrayNotHasKey('email')`. Plus de recopie du prédicat. |
| 7 | Couverture C-01 : 170 effectivement absent + renouvellement octobre 2027 | **Appliquée** | `ListeEnvoiTest.php:454-488` : `170 => 0` explicite, 171-174 + HS-2027, puis 175-178 + HS-2028, attendus posés un par un. |
| 8 | Traçabilité doctrine §7 : contradiction A-SANSMAIL dans `docs/ecarts.md`, datée | **Appliquée, mais reporting incohérent** | Ligne présente : `docs/ecarts.md` (22/11/2026, « Relecture C-07 »), et `docs/recette/profils.md:30` reformulé « Exclu des envois **par email** ». Fait en commit `261080c`. **Écart** : le compte rendu d'Hermès (`production/C-07/corrections-2026-11-22.md:3` et `production/C-07/PRET:2`) affirme « aucun fichier de `docs/` modifié ; instruction 8 réservée à Claude » — contredit par les deux fichiers `docs/` effectivement modifiés. Sans effet sur le code ; à clarifier (voir §3). |
| 9 | Rejeu réel dans le banc autorisé, drapeaux stricts, preuve jointe | **Appliquée (preuves enregistrées), non ré-exécutée par le vérificateur** | Paquet `production/C-07/replays/corrections-22nov-final/`. Voir §2. |

Toutes les instructions à la charge d'Hermès (1 à 7 et 9) sont appliquées ; l'instruction 8 est de fait satisfaite.

## 2. Résultat des tests

**Je n'ai pas pu rejouer les tests moi-même.** Mon environnement refuse l'exécution de `php`, `docker`, `composer` et `python` (sandbox) — même blocage que les deux relecteurs du premier tour. Je me suis donc limité à vérifier les preuves enregistrées et à les relier au code livré.

Preuves lues (`.../corrections-22nov-final/`) :

| Suite | Résultat | Code |
|---|---|---:|
| `composer test` standard (`final.log`) | OK **325 tests / 29 831 assertions**, 0 échec | 0 |
| Envoi strict (`envoi-strict.log`) | OK **91 / 315** | 0 |
| C-04 strict (`c04-strict.log`) | OK **37 / 224** | 0 |

Runtime PHP 8.2.36, PHPUnit 11.5.58. Les suites ciblées portent `--fail-on-warning --fail-on-risky --fail-on-deprecation` (compte rendu §Résultats). Les tests Envoi sont inclus dans les 325.

**Lien preuve ↔ code (fait indépendamment).** J'ai recalculé le SHA-256 des cinq fichiers clés et comparé au scellé `source-seal.json` / `c04-integrity.json` : **identiques.**

- `src/Envoi/ListeEnvoi.php` → `2d314a6b…263bae` ✓
- `src/Envoi/ExportCsv.php` → `3ce4e360…422667` ✓
- `tests/Envoi/ListeEnvoiTest.php` → `e683cdb1…e7a23677` ✓
- `tests/Envoi/ExportCsvTest.php` → `c0f813ac…795f1f30` ✓
- `imagine-connecteur/src/CsvProtection.php` → `139049a0…dd5cb21` ✓ (intact)

Conclusion : les preuves portent bien sur le code actuellement committé, celui que j'ai relu. Réserve : il s'agit du rejeu d'Hermès, pas d'une exécution indépendante. Un rejeu réel par Ced (environnement capable d'exécuter PHP) reste le seul contrôle manquant.

## 3. Régressions et modifications non demandées

- **Aucune régression de code détectée.** Hors `ListeEnvoi.php`, aucun fichier source métier modifié : `Abonnement.php`, `Destinataire.php`, `Situation.php`, `ExportCsv.php`, `CsvProtection.php` inchangés (empreintes confirmées).
- **`tests/Echeancier/run.php`** : reformatage PSR-12 (lignes longues) + `phpcs:disable PSR1.Files.SideEffects` ciblé. C'est le correctif de style C-05 autorisé par la fusion ; **logique inchangée**, vérifié au diff.
- **Ajout `wp/tests/envoi-runner/corrections.py`** : outil de banc du vérificateur de remise, hors livrable produit. Sans effet sur le code testé.
- **Incohérence de reporting (non bloquante)** : le `PRET` et le compte rendu d'Hermès nient toute modification de `docs/`, alors que `docs/ecarts.md` et `docs/recette/profils.md` ont bien été corrigés. Le résultat attendu (traçabilité §7) est atteint ; seul le texte du compte rendu est faux. À corriger pour éviter une ambiguïté au classement.

## 4. Points déférés à confirmer par Ced (non bloquants)

La correction a tranché des questions que la fusion §5 renvoyait à arbitrage :

- **A-SANSMAIL (§5 Q2)** : résolu dans `profils.md` (« exclu des envois par email seulement ; figure dans la liste postale »), conforme à l'analyse du fusionneur et à la règle 5 du brief. À entériner par Ced.
- **Grâce (§5 Q1)** : incluse par `inclureGrace = true`. Durée/maintien de la grâce explicitement renvoyés à Imagine avant branchement (`PRET`, compte rendu).
- **Bornes et format routeur (§5 Q4)** : borne `fin` exclusive conservée ; ordre/colonnes/format du routeur renvoyés à Imagine avant branchement.

Ces résidus relèvent d'Imagine ou du lot de branchement, pas de cette bibliothèque PHP pure.

## 5. Verdict

**Prêt pour la validation de Ced.**

Les neuf instructions sont appliquées ; le code livré correspond exactement aux preuves enregistrées (scellé recalculé et concordant) ; les suites y sont au vert sous drapeaux stricts ; aucune régression. Aucun problème de fond ne subsiste dans le code.

Deux réserves, qui relèvent précisément de la validation de Ced et ne sont pas des défauts de C-07 :
1. le rejeu réel n'a pas pu être refait par un tiers indépendant (contrainte d'environnement, identique aux deux relecteurs) — à rejouer dans un environnement capable d'exécuter PHP ;
2. les points A-SANSMAIL / grâce / format routeur (§4) sont à entériner, les deux derniers côté Imagine.

Rappel doctrine §6 : ce verdict de vérification n'est pas un GO ; il ne vaut que pour la clôture d'un lot de code.
