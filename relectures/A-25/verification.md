# Vérification A-25 — 2e et dernier tour

Date : 2026-11-26. Vérificateur. Base comparée : état relu au commit de la fusion (`corrections/A-25.md`, 20:18) → HEAD. `git diff` sur `wp/outils/bascule/a25`, `wp/tests/a25` et `production/A-25`. Ce n'est pas une relecture complète : je vérifie l'application des quatre instructions, les tests et l'absence de régression.

## 1. Instructions de `corrections/A-25.md`

### Instruction 1 (Important, I-1) — détecteur de tables de messages inconnues : **Appliquée**
- Nouvelle méthode pure `formStructure()` : `wp/outils/bascule/a25/Inventory.php:27-52`. Le rôle de la colonne décide, plus sa simple présence.
- La requête remonte bien `COLUMN_KEY` : `Inventory.php:108` (`SELECT COLUMN_NAME,COLUMN_KEY ... ORDER BY ORDINAL_POSITION`). L'ancienne exclusion `!in_array('submission_id', ...)` a disparu.
- Sémantique conforme à l'instruction : `submission_id` en clé primaire simple → `entry` (compté, `Inventory.php:39-41`) ; `id` propre + `submission_id` non primaire → `child` (exclu, `:43-45`) ; sinon `ambiguous` (`:46`). Protection anti-double-compte des tables-filles conservée (`meta_key` → `child`, `:48-50`).
- Pas de zéro silencieux : un candidat ambigu force `counts.forms = couverture indéterminée` (`Inventory.php:138-139`) et `forms.coverage` (`:145`). La priorité « inconnu après neutralisation » est préservée (`:138` ne bascule qu'en l'absence de neutralisation).
- Côté projection, les valeurs fermées sont imposées : `report.py:40-42` (ensemble de clés + `coverage ∈ {heuristique bornée, couverture indéterminée}`) et `report.py:59-61` (couverture indéterminée ⇒ `counts.forms` = la chaîne, jamais un total).

### Instruction 2 (Important, test lié à I-1) — compléter le banc : **Appliquée**
- `wp/tests/a25/seed.php:47-48` : table d'entrées `a25_submission_entries` à **`submission_id` clé primaire**, cinq messages (2022). `:49-50` : vraie table-fille `a25_submission_details` (clé `id`, `submission_id` référence) avec **deux détails par message** (dix lignes) — gonflerait 5 en 15 si comptée.
- Dix assertions PHP pures sur les rôles : `wp/tests/a25/unit.php:20-52` (`submission_pk_is_entry`, `own_id_submission_reference_is_child`, `composite_submission_pk_is_ambiguous`, `unkeyed_submission_is_ambiguous`, `meta_child_excluded`, etc.).
- Preuve native de bout en bout : nouvelles phases `pk-only` et `ambiguous` dans `inside.py` (comptage de 5 sous « autre » sans double compte ; couverture indéterminée jamais à zéro), empreintes avant/après. `verify.py` exige ces contrôles et les observations exactes des sept variantes (`verify.py:94-105`, `:121-127`, `form_observation_valid` `:54-71`).
- Neutralisation : les deux nouvelles tables sont explicitement conservées et vérifiées préservées (`neutralise.php:52-53`, `inside.py` `submission_pk_messages_preserved` / `submission_child_rows_preserved`).

### Instruction 3 (Mineur) — étiqueter `clear_messages_after_import` : **Appliquée**
- Champ fermé `clear_messages_after_import_label` = « avertissement éditorial permanent, non mesuré sur la copie inspectée » dans la sortie : `Inventory.php:147-148`. Présent dans les deux fichiers (sortie JSON + projection).
- Imposé par la projection : `report.py:44` (clé obligatoire) et `report.py:41` (`!= EDITORIAL_WARNING` ⇒ refus). Logique inchangée, aucune suppression exécutée. Documenté au README.

### Instruction 4 (Mineur) — citation littérale Fluent Forms dans `SOURCES.md` : **Appliquée**
- `production/A-25/SOURCES.md:8` : phrase exacte « Storing the form submissions » et ligne de schéma `created_at\ttimestamp NULL` de la section `fluentform_submissions`, avec mention de la provenance et de l'indisponibilité de l'extraction (HTTP 403, lecture navigateur).
- Provenance tracée dans le nouveau `production/A-25/fluentforms-source.json` (URL, section, phrase, ligne, date de consultation).

## 2. Résultat des tests

Je n'ai **pas pu exécuter** la suite moi-même : le mode de permission de cette session refuse toute invocation de Python (`C:/Python314/python.exe` et variantes, toutes « requires approval »). Conformément à la grille (« à défaut, le dire »), je m'appuie sur les reçus scellés et la lecture des sources.

- **Run natif complet régénéré par le parent sur les sources corrigées**, reçu scellé `production/A-25/candidate-verification.json` : **137 PASS, 0 FAIL**, deux encodages (UTF-8 et cp1252), magasins classique et HPOS. Compteurs : 33 tests Python, 25 assertions PHP pures (les 10 nouvelles incluses), 212 contrôles natifs par encodage.
- Les contrôles propres aux corrections y sont **tous présents et verts** : `corrected_pure_cases`, et `*_exact_form_observation` pour les sept variantes dont `pk-only` et `ambiguous`, en classique et HPOS, dans les deux encodages. Un faux négatif I-1 non corrigé aurait fait échouer `pk-only`/`ambiguous`.
- `candidate-verification.json` : `status = CANDIDAT_GATE_PARENT`, `readiness_claimed = false` — cohérent avec un paquet prêt à vérifier, non auto-clos.
- Rappel : le run Python seul du réveil (`corrections-reveil.md`) affiche 33 verts × 2 encodages ; non re-exécutable ici mais recoupé par le reçu natif ci-dessus.

Lecture statique des diffs : les sept variantes attendues, les rôles de colonnes et les valeurs fermées sont câblés de façon cohérente entre `Inventory.php`, `report.py`, `verify.py`, `inside.py`, `unit.php`, `neutralise.php` et `seed.php`.

## 3. Régressions ou modifications non demandées

- **Aucune régression de logique.** Le périmètre §4.4 reste tenu : lecture seule, aucun contenu sélectionné/projeté, codes fermés, priorité neutralisation inchangée.
- **Attendus de tests modifiés — légitimes, non régressifs.** Le nominal `forms` passe de `{groups: [], autres: 4}` à `{groups: [{2022, autre, 5}], autres: 4}` : conséquence directe du nouveau fixture (5 messages PK en 2022, ≥ seuil), la table-fille (10 lignes) restant exclue. Variantes `five`/`absent`/`nodate` ajustées de même. Cohérent avec l'intention.
- **Nit de traçabilité (non bloquant).** La note en tête de `wp/outils/bascule/a25/README.md` (« Python seul rejoué ici ... pas de PRET ») vient de la sous-session du réveil ; elle est désormais dépassée par le run natif du parent et le `PRET` posé à 22:56 (`production/A-25/PRET`) pointant `preuves/final`. Documentation à jour partout ailleurs ; aucune incidence sur le code ni sur les preuves.
- Fichiers hors A-25 non suivis au `git status` (`relectures/A-24/...`, `wp/outils/demo/b08-gates.py`) : étrangers à ce lot, ignorés.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les quatre instructions de la fusion sont appliquées, vérifiées au fichier et à la ligne. La correction de fond (I-1 : discrimination par `COLUMN_KEY`, couverture indéterminée au lieu d'un zéro silencieux) est réelle et correcte, son banc la couvre vraiment (PK clé primaire comptée, table-fille exclue, double-compte écarté). Le run natif scellé sur les sources corrigées est entièrement vert dans les quatre contextes. Aucun problème de fond restant ; aucune question visuelle, métier ou touchant au réel dans ce lot.

Réserve de forme, non bloquante : je n'ai pas pu relancer la suite localement (permission de session), la preuve retenue est le reçu scellé du parent. La pose du `PRET` et le GO de clôture relèvent de Ced / du parent — un verdict de vérification n'est pas un GO.
