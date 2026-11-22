# Vérification C-07 — second passage (remise « format d'export »)

Date : 22/11/2026. Vérificateur : Claude (relecteur indépendant).
Objet : contrôler la remise d'Hermès postérieure à `verification.md` — le **format d'export configurable** (file de 13 h 20), réponse à l'arbitrage C-07.
Base de la vérification précédente : `84d2f9c` (état vérifié par `verification.md`). État vérifié ici : `HEAD` (`ccc7413`).
Méthode : `git diff 84d2f9c HEAD` sur `wp/` et `production/C-07`, lecture du code neuf, recalcul du scellé, rejeu — voir §2.

Ce n'est pas une relecture complète. Seule la remise « format d'export » est reprise ; `ListeEnvoi.php` n'a pas été remodifié (voir §3).

---

## 1. Consigne / arbitrage, point par point

Consigne concernée : `docs/arbitrages-2026-11-22.md`, section **C-07** (ligne 44) — « Le format attendu par le routeur (ordre et colonnes) devient un réglage d'export. Colonnes provisoires d'ici la réponse d'Imagine. » Elle applique le **principe d'arbitrage du 22/11** (`arbitrages-2026-11-22.md:4-14`) : une règle ouverte devient un réglage nommé, à défaut prudent, testé, et le lot ne bloque plus. Elle solde le point déféré §4 de `verification.md` (« ordre/colonnes/format du routeur renvoyés à Imagine »).

| # | Exigence de l'arbitrage | Résultat | Preuve (fichier:ligne) |
|---|---|---|---|
| a | L'ordre et les colonnes deviennent un réglage d'export | **Appliqué** | `src/Envoi/FormatExport.php:8-23` (sélection ordonnée, non vide, colonnes connues et uniques) ; `src/Envoi/ExportCsv.php:16-24` et `:28-30` (`liste` et `lignes` acceptent `?FormatExport $format`, appliqué à l'en-tête et aux cellules). |
| b | Réglage isolé en un seul endroit, nommé | **Appliqué** | `src/Envoi/AdministrationFormatExport.php:10` (option unique `imagine_envoi_colonnes_export`), `:32-55` (Settings API). |
| c | Modifiable dans l'administration sans toucher au code | **Appliqué** | `AdministrationFormatExport.php:57-79` (page Réglages, une colonne par ligne), `:65` (`action="options.php"`), `:59,64` (`manage_options`, nonce délégués à WordPress). |
| d | Valeur par défaut la plus prudente (= comportement inchangé) | **Appliqué** | `FormatExport.php:11` (défaut = `ExportCsv::COLONNES`, 9 colonnes) ; `ExportCsv.php:30` (`$format ?? new FormatExport()` → CSV identique sans argument) ; `AdministrationFormatExport.php:37,88,92` (défaut et repli = colonnes provisoires) ; `:86-94` (option absente/corrompue → repli). |
| e | Chaque valeur du réglage testée | **Appliqué (couverture représentative)** | `tests/Envoi/FormatExportTest.php:96-105` (chaque colonne seule), `:107-121` (sélection, ordre, défaut) ; `tests/Envoi/AdministrationFormatExportTest.php:68-78` (toutes colonnes + ordre inversé), `:80-105` (saisies/options invalides → repli), `:107-117` (idempotence). Réglage à sélection libre : les permutations ne sont pas toutes énumérables, mais défaut, unité, ordre inverse, sous-ensembles et refus sont couverts. |
| f | Le lot se clôt sans attendre la réponse d'Imagine | **Appliqué côté code** | `production/C-07/notes.md:50` (point 3 reformulé : la réponse s'applique par le réglage, « ne bloque plus cette remise »). L'inscription de la question en `docs/decisions.md` reste à la charge de Claude (Hermès n'écrit pas dans `docs/`, A-FAIRE.md:27). |

Barrière d'anomalies conservée malgré le format : `ExportCsv.php:21-23` refuse toute anomalie non revue **avant** d'appliquer le format, même sur un sous-ensemble de colonnes (testé `FormatExportTest.php:71-72` ; export autonome `AdministrationFormatExport.php:81-84` idem).

Toutes les exigences de l'arbitrage C-07 sont appliquées.

## 2. Résultat des tests

**Je n'ai pas pu rejouer les tests.** Mon environnement refuse `php`, `docker` et même `command -v php` (sandbox non interactive) — même blocage que les deux relecteurs et que le premier tour. La doctrine impose de toute façon PHP en conteneur jetable, rien sur Windows (`A-FAIRE.md:21`). Je me limite donc aux preuves enregistrées et à leur rattachement au code.

Preuves lues (`production/C-07/replays/format-export-22nov-final/`, `format-verification.json`) :

| Suite | Résultat | Code |
|---|---|---:|
| `composer test` (`final.json`) | **362 tests / 30 770 assertions**, 0 échec/erreur/ignoré | 0 |
| Envoi strict (`envoi-strict.json`) | **115 / 402** | 0 |
| C-04 strict (`c04-strict.json`) | **37 / 224** | 0 |

Suites ciblées sous `--fail-on-warning --fail-on-risky --fail-on-deprecation`. Les totaux agrégés (325 → 362) incluent les tests FormatExport neufs et la suite Echeancier désormais déclarée (voir §3) ; ils n'emportent aucune clôture de C-05/C-06.

**Lien preuve ↔ code (recalculé indépendamment).** J'ai recalculé le SHA-256 des fichiers clés et comparé à `format-seal.json` : **identiques.**

- `src/Envoi/ExportCsv.php` → `9a7e4dac…17c3d572` ✓
- `src/Envoi/FormatExport.php` → `8edb5808…46bcdecf1` ✓
- `src/Envoi/AdministrationFormatExport.php` → `ac59e9b8…4bdb9927` ✓
- `tests/Envoi/FormatExportTest.php` → `5e2a415c…0b60a1a1b8` ✓
- `tests/Envoi/AdministrationFormatExportTest.php` → `2db0295b…026f6306` ✓
- `src/Envoi/ListeEnvoi.php` → `2d314a6b…09263bae` ✓ (**identique au scellé du premier tour** : code précédemment vérifié inchangé)
- `imagine-connecteur/src/CsvProtection.php` → `139049a0…77dd5cb21` ✓ (C-04 intact)

Les preuves portent bien sur le code committé. Réserve inchangée : c'est le rejeu d'Hermès, pas une exécution indépendante. Le rejeu réel par Ced (environnement capable d'exécuter PHP) reste le seul contrôle manquant, comme au premier tour.

## 3. Régressions et modifications non demandées

- **Aucune régression de code C-07.** `ListeEnvoi.php` n'a pas été remodifié depuis `84d2f9c` (empreinte byte-identique). `ExportCsv.php` : le format est un **paramètre optionnel** (`?FormatExport $format = null`) ; sans argument, sortie inchangée. `ExportCsvTest.php` et `ListeEnvoiTest.php` ont une empreinte identique au premier tour → logique déjà vérifiée non touchée. C-04 (`CsvProtection.php`) intact.
- **`phpunit.xml:9` — ajout de la testsuite `Echeancier`.** C'est une modification **du lot C-05 (Échéancier)**, pas de C-07, mais elle est portée dans le même plugin : elle fait entrer les tests Echeancier dans les 362 de `composer test`. Hors périmètre C-07, à rattacher à C-05.
- **Hors C-07, hors périmètre de cette vérification.** Le `git diff 84d2f9c..HEAD` sur `wp/` contient aussi `src/Acces/*` (C-06), `src/Echeancier/*` (C-05), `wp/tests/a01-court/*` et `wp/outils/staging-court/*` (A-01). Ce sont des chantiers parallèles ; ils ne touchent pas le code Envoi de C-07 ; je ne les ai pas relus ici.
- **Adaptateur WordPress neuf (`AdministrationFormatExport`)** : justifié par l'arbitrage (« modifiable dans l'administration »), isolé, **non branché** au bootstrap. Ses tests utilisent des doublures (`AdministrationFictive.php`) : ni sauvegarde HTTP native, ni nonce réel, ni recette visuelle prouvés — Hermès le signale (`notes.md:52`, `format-export-2026-11-22.md:25`). Pas un défaut, mais une preuve absente, décrite ci-dessous.
- **Report cohérent cette fois** : `notes.md:46` affirme « aucun `docs/` modifié » lors de cette remise ; le diff le confirme (aucun `docs/` dans la remise format). L'incohérence de report signalée au §3 du premier tour (contradiction `PRET` ↔ `docs/ecarts.md`) concernait la remise *corrections* et reste, elle, un point déjà déféré à Ced ; elle n'est pas rouverte ici.

## 4. Verdict

**Remonte à Ced.**

L'arbitrage C-07 est **entièrement appliqué** dans du PHP pur ; le code livré correspond exactement aux preuves ; aucune régression ; le code précédemment vérifié (`ListeEnvoi`, `ExportCsv` hors signature, C-04) est intact. **Il n'y a aucun défaut de code.**

Ce n'est pas « prêt pour la clôture » pour des raisons qui dépassent le vérificateur, non pour un bug :

1. **Rejeu indépendant toujours manquant.** Comme aux deux tours précédents, mon environnement ne peut exécuter PHP ; il faut un rejeu réel par Ced.
2. **Code neuf non passé par le cycle de clôture.** `FormatExport` et `AdministrationFormatExport` sont du code nouveau depuis la fusion `corrections/C-07.md` : ils n'ont pas eu les **deux relectures indépendantes + fusion** que la doctrine §6 exige pour une clôture par Claude.
3. **Écran d'administration = domaine de validation de Ced (§6).** L'adaptateur ajoute une page Réglages WordPress dont la persistance native (nonce, sauvegarde `options.php`, rendu) n'est prouvée que par doublures. La validation d'un écran revient à Ced.

Décision à prendre par Ced : soit lancer le rejeu réel et faire relire/fusionner la remise format d'export avant clôture, soit renvoyer l'adaptateur d'administration au lot de branchement et ne clore ici que la bibliothèque PHP. La question « format routeur », elle, est bien neutralisée : la réponse d'Imagine s'appliquera par le réglage, sans toucher au code.

Rappel doctrine §6 : ce verdict de vérification n'est pas un GO ; il ne vaut que pour la clôture d'un lot de code.
