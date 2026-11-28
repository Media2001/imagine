# Relecture A-33 — Le poids des archives (Claude, relecteur indépendant)

Lot : A-33. Brief : `briefs/A-33-le-poids-des-archives.md`. Cahier des charges : §4.3.
Production relue : `wp/outils/bascule/a33/`, `wp/tests/a33/`, `production/A-33/`.
`relectures/A-33/codex.md` **non ouvert** (consigne respectée). Pas de fusion à ce stade.

## Rejeu de la suite PHP (commande autorisée, sans argument)

Commande lancée depuis la racine : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
Conteneur jetable, réseau absent, dépôt monté en lecture seule. Sortie exit 0. Lignes finales :

```text
PAQUETS : 13 vérifiés, 0 échecs ; hors rejeu : aucun
OUTILS : 23 outils, 852 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1229 tests, 36926 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Le bilan machine (`T01_RESULT`) confirme A-33 présent dans les treize paquets vérifiés, aucune exclusion, aucun échec. Mon rejeu indépendant concorde avec le paquet scellé `production/A-33/preuves/final/gates/` (mêmes nombres). Les portails rouges décrits dans `BLOCAGE.md` sont donc résolus : A-32 a été requalifié, A-33 inclus, re-scellé, et `production/A-33/PRET` existe (2026-11-28T02:25:05Z).

## 1. Conformité

Le lot fait ce que demande le brief, sans dériver.

- Outil lecture seule dans `wp/outils/bascule/a33/`, nombres seulement, aucun déplacement. ✓
- Les dix derniers numéros viennent de la règle d'A-16 telle quelle : `Inventory.php:60` appelle `(new IssueInventory\Inventory($site))->collect($mapping, 10)`, refus compris. Pas de tri ni de règle concurrente.
- Contenus publiés hors des dix, par type et par année : `published_outside`. Types de site fermés (`post/page/product/product_variation`), rôles `article/numero`, tout autre type → `autre` + indice numérique anonyme ; aucun nom de type exporté (`Analysis.php:38-46`).
- Pièces jointes par année, nombre et poids (`outside_media_by_year`) ; fichier en base mais absent du disque compté à part et jamais à zéro (`Analysis.php:28-30`, `total_bytes = "inconnu fichiers absents"`).
- Pièces sans parent : `orphan_media` (`Inventory.php:127`, `parent===0` ou parent inexistant).
- Poids des dix numéros en regard : `recent_media`.
- Aucun titre, nom de fichier ni chemin en sortie : schéma clos, validé par `report.py:projection`. Poids lu par `stat` sans ouvrir les fichiers (`Inventory.php:48`).
- Import ayant écarté des dossiers → `excluded_directories_bytes = "inconnu après import"` ; copie non importée → `"non évalué"`, jamais un zéro inventé (`Inventory.php:147`).
- Un seul magasin de commandes ; commandes/abonnements/coupons/adhésions/révisions/pièces exclus de l'énumération (`Analysis.php:9-10`) ; import, gardien et lanceur gelés (non modifiés).

Interprétations faites et **signalées** (donc conformes à la grille §1), à confirmer sans blocage :
- Année d'une pièce = année UTC de son contenu parent (README `a33/README.md`, `LIVRAISON.md`).
- `other_media` : pièce attachée à un parent non publié / non éditorial (brouillon), distinguée d'une pièce orpheline (README `a33/README.md`).
- Dates nulles regroupées sous `inconnu` (README).

Aucune interprétation non signalée relevée. Aucune question ouverte pour Ced.

## 2. Exactitude métier — déroulé à la main

Semis `wp/tests/a33/seed.php` : 12 numéros (2010→2021), chacun un article (parent = numéro) et un terme lié ; A-16 à dix → les deux plus anciens (2010, 2011) hors des dix.

J'ai déroulé le cas nominal à la main et comparé au résultat produit (`preuves/final/utf8/native/r1-nominal/archives.json`) :

| Attendu dérivé | Calcul | Produit |
|---|---|---|
| `selected_issues` | 10 des 12 numéros | 10 ✓ |
| numero 2010 / 2011 | numéros[0],[1] publiés hors dix | count 1 / 1 ✓ |
| article 2010 / 2011 | articles[0],[1] liés aux anciens numéros | count 1 / 1 ✓ |
| post 2022 | 1 post publié | count 1 ✓ |
| autre groupe 1 / 2 (2023) | 2 types inconnus distincts, ordre ID croissant | groupes 1 et 2 ✓ |
| page brouillon | non `publish` → exclue | absente ✓ |
| médias 2010 | tailles 7, 11, absent → 3 pièces, 2 présentes, 1 absente, 18 o, total inconnu | ✓ |
| médias 2011 | taille 13 → 1, 13 o | ✓ |
| médias 2022 | taille 0 → présent, 0 o (pas « absent ») | ✓ |
| `orphan_media` | parent 0 et parent inexistant : 23 + 29 = 52 o | count 2, 52 o ✓ |
| `recent_media` | pièces des numéros[11]+article[11] : 17 + 19 = 36 o | count 2, 36 o ✓ |
| `other_media` | pièce du brouillon : 31 o | count 1, 31 o ✓ |
| `excluded_directories_bytes` | copie non importée | « non évalué » ✓ |

Concordance exacte. Cas limites couverts par le banc et vérifiés : fichier présent de taille 0 ≠ fichier absent ; parent inexistant (999999) traité en orphelin ; variante import (`r20`, option `imagine_staging_disabled_plugins`) → total et dossiers exclus « inconnu après import » sans transformer une absence en zéro ; variantes de correspondance postmeta / `post_parent` / taxonomie ; article lié à plusieurs numéros compté une seule fois côté dix (`Inventory.php:89-92`).

## 3. Tests

- Suite PHP rejouée : **PASS** (voir ligne REJEU ci-dessus), 0 échec, 0 ignoré. A-33 scelle 23 contrôles purs (`unit.php`) + 52 natifs/console.
- Couverture forte et non tautologique : le banc natif monte un vrai WordPress, piège les requêtes sur les tables de commandes, observe par `inotify` qu'aucun média n'est ouvert (avec inverse positif), et compare base + fichiers avant/après chaque variante. Sept canaris de canal (echo, STDOUT, STDERR, sortie anticipée, shutdown, altération de fichier, exception) éprouvent l'étanchéité du protocole de sortie. Matrice Windows UTF-8/cp1252, session propre, TMPDIR retiré.
- Les tests vérifient la règle, pas le code : oracles exacts calculés indépendamment du collecteur (`inside.py`), et je confirme le nominal par déroulé manuel.

Réserve (mineure) — cas limite « année inconnue » : le brief et le README prévoient le regroupement des dates nulles sous `inconnu`, mais aucun contenu publié hors-dix à `post_date_gmt` nulle **portant une pièce** n'est présent dans le semis (`seed.php:36-44`, toutes les dates sont valides). De bout en bout, les seaux `inconnu` de `published_outside` et `outside_media_by_year` — et leur rendu JSON (chaîne vs entier, position de tri) — ne sont donc pas exercés. Seule `Analysis::year` est testée en unité (`unit.php:50-55`). À compléter.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Fixtures à noms manifestement inventés (`*_CANARY`), aucune adresse réelle.
- Lecture seule stricte : SELECT uniquement, requêtes préparées pour les références scalaires (`Inventory.php:79-86`), transaction native READ ONLY, Landlock, réseau absent, guards mail/HTTP/tâches, confinement obligatoire (`Command.php:24`, `peser-archives`).
- Sortie non divulgante : schéma clos sans champ libre ; les noms de types de site inconnus ne sont jamais publiés (indice numérique seulement) ; le contrôle `no_site_identifiers_all_nominal_channels` grep l'absence de titre/chemin/`@`/`CANARY` dans toute la sortie.
- Gardes de chemin sur `_wp_attached_file` et sur le dossier de sortie (`Inventory.php:24-44`, `Command.php:34-43`) ; refus symlink ; refus d'une correspondance non éditoriale **avant** bootstrap (`A33_NONEDITORIAL_MAPPING_UNSUPPORTED`).
- Paywall : sans objet (outil de comptage hors ligne).

Rien à signaler.

## 5. Doctrine

- Standard d'abord : `STANDARD.md` + `sources-officielles.json` citent `get_attached_file`, `get_attached_media`, `filesize` (HTTP 200, consultées le 27/11/2026) ; A-12 et A-16 réutilisés inchangés plutôt que réimplémentés.
- Conventions §5 : `declare(strict_types=1)`, espace de noms `Imagine\`, PSR-12 sans erreur ni avertissement (`style/style.json`), README de l'outil présent.
- Rejouable, idempotent (contrôle `deterministic_replay`), non-régression (base/fichiers identiques avant/après).

Réserve (mineure) — documentation périmée dans le paquet livré : `production/A-33/BLOCAGE.md:16` affirme « PRET A-33 n'est pas créé » et `BLOCAGE.md:33` donne comme « Attendus actuels » `A-33 = sortie 1 / A33_GATES_INVALID` et `A-32 = sortie 1 / A32_PARTIAL_EVIDENCE`. Ces assertions au présent contredisent l'état livré (PRET présent, portails verts à 13 paquets, `verify.py` → PASS). Le fichier est étiqueté « historique » en tête, mais la section « Attendus actuels » se présente comme courante. À corriger ou à dater. `RAPPORT.md` est également un cran en retard (rédigé avant la création de PRET) sans se contredire frontalement.

## Verdict

**Conforme** — l'outil fait exactement ce que demande le brief, le rejeu autorisé passe (PASS, 0 échec), et le cas nominal du cahier des charges déroulé à la main concorde au chiffre près.

Points classés :
- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur 1** (test) : cas limite « année inconnue » (date nulle avec pièce) non exercé de bout en bout ; ajouter au semis un contenu publié hors-dix à `post_date_gmt` nulle portant une pièce jointe. `wp/tests/a33/seed.php:36-44`.
- **Mineur 2** (documentation) : `production/A-33/BLOCAGE.md:16` et `:33` décrivent au présent un état (PRET absent, portails rouges) qui n'est plus le vrai ; corriger ou dater ces lignes.

Rappel doctrine : ce verdict, même « Conforme », **n'est pas un GO**. Il ne vaut que pour la clôture d'un lot de code. `codex.md` existe mais n'a pas été lu ; la fusion (`corrections/A-33.md`) reste à faire dans un second temps.
