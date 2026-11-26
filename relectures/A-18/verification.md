# Vérification A-18 (2e et dernier tour)

Objet : contrôler que les corrections de `corrections/A-18.md` ont été appliquées par Hermès, relancer ce qui est exécutable ici, signaler toute régression. Pas de nouvelle relecture complète.

Base comparée : version relue (~09 h, commit `88c18f4b`) → état courant (`cb062658` / `0bf2de53`), sur `wp/outils/bascule/a18`, `wp/tests/a18` et `production/A-18`. Les fichiers A-18 touchés et rien d'autre : `Forms.php`, `Inventory.php`, `README.md`, et les tests (`seed.php`, `unit.php`, `inside.py`, `run.py`, `verify.py`, `windows_matrix.py`).

## 1. Instruction par instruction

**1 — R1 : inventorier les deux magasins (classique ET HPOS), libellé fermé, cas de preuve magasin inactif.** — **Appliquée.**
- `Inventory.php:57-83` : `database()` ne reçoit plus `$hpos`. Les tables présentes sont détectées (`information_schema.TABLES`, `:61`, erreur close `A18_QUERY_FAILED`) ; la requête HPOS (`:71-76`) et la requête classique (`:77-83`) sont ajoutées indépendamment du flag actif.
- Provenance par libellé fermé : `store` ∈ `classique` / `hpos` / `commun`, propagé en `rows()` (`:51-52`), `groups()` (`:28-31`) et dans la clé d'agrégat (`:89`).
- Mode d'emploi aligné : `count_basis` (`:170-172`) précise « valeurs physiquement conservées dans les deux magasins présents, actif ou inactif » ; `storage` = seulement le magasin actif. `README.md:15-16` dit la même chose.
- Cas de preuve : `seed.php:23-47` insère des lignes résiduelles dans le magasin **inactif** (ordre + abonnement, dans les deux sens selon HPOS actif) + une valeur partagée. `verify.py` exige `r1_inactive_store:order`, `r1_inactive_store:subscription`, `r1_physical_rows_not_logical_dedup`, `r1_closed_store_labels` : tous présents et verts.

**2 — R3 : aligner les séparateurs de `scan()` sur `iban()` (espaces multiples, tab, tiret, retour à la ligne, insécables) ; idem motif carte.** — **Appliquée.**
- `Forms.php:107` : `$space = '[\s-]*'` (inclut tab et retour à la ligne) au lieu de `[ \t-]?`. `:106` convertit U+00A0 / U+202F en espace avant extraction.
- Carte : `numberGroups(..., '/\A[\s-]+\z/D', ...)` (`:119`) tolère les mêmes séparateurs, retour à la ligne compris.
- Tests `scan()` → `groups()` pour `multiple_spaces`, `line_feed`, `tabs`, `crlf`, `nbsp`, `narrow_nbsp`, en IBAN et carte : `unit.php:47-71`. Verts.

**3 — R2 : chercher carte et registre séparément, réexaminer les frontières après échec, pas de candidat glouton 11-19.** — **Appliquée.**
- Nouvelle `numberGroups()` (`Forms.php:70-100`) : ne retient que des **groupes entiers** de chiffres (`(?<![A-Za-z0-9])[0-9]+(?![A-Za-z0-9])`), accumule groupe par groupe, s'arrête au-delà du maximum, valide dès le minimum atteint — jamais une tranche arbitraire d'une suite continue.
- Appels séparés : carte 13-19 (`:119`), registre 11 exact (`:120`).
- Tests : `4242 4242 4242 4242 123` (carte retrouvée), `85.07.30-033.28 2026` (registre retrouvé), variantes tête/queue/deux côtés, et six cas « pas de fragment arbitraire » (`unit.php:72-99`). Verts.

**4 — Mémoïser `iban-structures.json`.** — **Appliquée.** `Forms.php:9-19` : propriété statique `$formats` + `formats()`, chargement unique ; `iban()` (`:27`) et `scan()` (`:108`) l'utilisent. Test `memo_iban_registry_single_load` (`unit.php:111`) : le registre est vidé après premier chargement, les appels restent corrects. Vert.

**5 — Ajouter les régressions R1/R2/R3 au paquet unique `preuves/final`, régénérer, lever l'écart de décompte 33/34.** — **Appliquée.**
- Régressions présentes et exigées par `verify.py` (listes `required` / `required_unit`, `:17-21`). Paquet régénéré : `sources.json` du paquet == empreintes des sources courantes (`exact_current_sources` PASS).
- Décompte : les comptes sont désormais calculés par `verify.py` (`check_count`) et non saisis à la main (`README.md:42`). Nouvelles valeurs cohérentes dans les deux consoles : **unit 37 / natif 100 / runner 7**. L'ancien écart 33/34 ne subsiste pas.

**6 — Conserver le défaut prudent règles serveur (`reading_denied = null`), acter l'écart dans `docs/ecarts.md`.** — **Appliquée.** `Inventory.php:113` : `reading_denied => null`, présence seule (`server_rule_file_present`), aucun fichier ouvert. Écart consigné `docs/ecarts.md:64`. Note : l'entrée a été écrite par le relecteur (c'est son rôle ; Hermès n'écrit pas dans `docs/`), ce que `production/A-18/FINALISATION.md:9` confirme. Conforme.

**7 — Documenter le double comptage carte/registre sur un même nombre de 11 chiffres.** — **Appliquée, avec correction de la prémisse.** `README.md:17` documente l'indépendance des colonnes (« ne pas les additionner pour obtenir un nombre de lignes distinctes ») et précise que le cas cité dans la fusion est en réalité **impossible** : la carte exige au minimum **13** chiffres, le registre en fait exactement **11** — les deux formes ont des longueurs disjointes et ne peuvent pas alimenter la même valeur. L'intention de l'instruction (prévenir une addition trompeuse) est satisfaite ; le « double comptage sur 11 chiffres » n'existe pas avec ces seuils. Rebut légitime, pas une omission.

## 2. Résultat des tests

Exécutés **ici** (sans Docker ni PHP au PATH) :
- `python wp/tests/a18/verify.py production/A-18/preuves/final` → **exit 0**, 36 contrôles, **tous PASS**, 0 échec. Vérifie : empreintes du paquet == sources courantes, régressions unit requises présentes, cas natifs requis `classic` **et** `hpos` présents et verts, égalité toutes-tables avant/après, style PSR-12, matrice Windows, lanceur. Comptes : unit 37 / natif 100 / runner 7, en cp1252 et utf8.
- `python -m unittest wp.tests.a18.test_launcher` → **Ran 3 tests, OK** (3/3).

Consignés dans le paquet (non ré-exécutables ici) :
- Banc natif A-18 : vert dans les deux consoles, magasins classique et HPOS. `rejouer.ps1` (`production/A-18/verification.json`) : **1 123 tests / 34 569 assertions / 0 échec**, A-18 = 37 contrôles, en UTF8 et cp1252. `production/A-18/candidate-verification.json` : exit 0.

**Réserve honnête :** le banc natif repose sur conteneurs Docker + staging WordPress/Woo. Cet environnement n'a ni Docker ni PHP au PATH (même limite que celle déjà notée dans la fusion). Je n'ai donc **pas** ré-exécuté le PHP natif moi-même ; je l'ai contrôlé indirectement via `verify.py` (lecture seule, qui recalcule les empreintes et impose la présence + le vert des cas requis) et par la ré-exécution du lanceur. L'exigence « rejeu natif indépendant en environnement Docker/WSL » de la fusion n'est pas close par le présent tour pour cette seule raison matérielle, pas pour un défaut de code. La réserve (b) de la fusion — régressions R1/R2/R3 vertes dans le paquet régénéré — est, elle, levée.

## 3. Régressions ou modifications non demandées

Aucune. Les changements A-18 se limitent au périmètre des instructions : `Forms.php` / `Inventory.php` (R1-R4), `README.md` (R1, R7 + alignement du mode d'emploi), tests (régressions R1/R2/R3, mémoïsation) et `windows_matrix.py` (rejeu natif + lanceur dans les deux consoles, qui outille la réserve de banc). La détection `information_schema.TABLES` ajoutée est le support nécessaire de R1 et échoue proprement (`A18_QUERY_FAILED`). Aucune valeur, aucun identifiant de personne, aucun chemin profond ni contenu média ne sort ; `read_only` et la lecture seule SQL sont préservés. Aucune question ouverte pour Ced dans le lot (ni visuelle ni touchant au réel) ; la question « Pour Imagine » sur le marqueur de neutralisation garde son défaut prudent.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les sept instructions de `corrections/A-18.md` sont appliquées (la 7e avec une correction de prémisse justifiée). Les tests ré-exécutables ici sont verts, le paquet est régénéré contre les sources exactes courantes, aucune régression ni modification hors périmètre. Aucun problème de fond ne subsiste — rien à remonter à Ced.

Seule réserve, d'ordre matériel et non bloquante : le banc natif PHP n'a pas pu être rejoué indépendamment dans ce tour faute de Docker/PHP ; il est validé par `verify.py` + le lanceur, et par les reçus du paquet (deux consoles, deux magasins). Ce rejeu natif indépendant en environnement Docker/WSL reste à confirmer, comme la fusion l'avait déjà posé.

Rappel doctrine : ce verdict de vérification n'est pas un GO au sens du §3. La clôture et la mise en ligne restent la décision de Ced.
