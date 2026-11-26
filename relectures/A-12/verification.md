# Vérification A-12 — second et dernier tour

Date : 2026-11-26. Vérificateur : Claude. Objet : contrôler l'application de `corrections/A-12.md` (fusion B1 / I1 / README / vérification) après reprise par Hermès. Base de comparaison : état relu (commit `645c1f1`, code a12 d'avant corrections). Portée : `wp/outils/bascule/a12`, `wp/tests/a12`, `wp/outils/bascule/a11` (dépendance), `production/A-12`. Pas de relecture complète.

## 1. Instructions de corrections/A-12.md

### Instruction 1 — B1 (bloquant) : confinement disjoint du site et du dépôt, deux sens, `/` refusé
**Appliquée.**
- Python : `wp/outils/bascule/a12/confine.py:9-11` — nouvelle fonction `disjoint_output(parent, site, repository)` qui refuse `parent == '/'`, l'égalité, les descendants (`root in parent.parents`) **et** les ancêtres (`parent in root.parents`) du site et du dépôt. Appelée avant tout octroi Landlock en `confine.py:66`.
- PHP : `wp/outils/bascule/a12/Command.php:14-18` — `disjointOutput()` reprend le même invariant (`!inside(parent,site) && !inside(site,parent) && !inside(parent,repo) && !inside(repo,parent)` + `parent !== '/'`), appliqué en `Command.php:42`. `inside()` corrigé en `:11` (`rtrim` sur la racine).
- Invariant unique retenu (défaut technique 3 de la fusion), pas une énumération de cas.
- Tests ajoutés : banc natif `wp/tests/a12/inside.py:144-149` (cas « parent ancêtre du site » et « sortie = `/` », lanceur **et** PHP, avec vérification que `index.php` du site est inchangé) ; test Python autonome `wp/tests/a12/test_confine.py`.

### Instruction 2 — I1 (important) : agrégations de contenus limitées au domaine `posts`
**Appliquée.** `wp/outils/bascule/a12/Inventory.php:248-291`.
- Domaine d'objets lu via `get_taxonomy()->object_type` et conservé (`object_types`, `:251,259`).
- Garde `postsOnly` (`:253`) : agrégats états/dates/termes calculés **seulement** si toutes les classes d'objets sont des types `posts` déclarés ; le join filtre alors sur `p.post_type IN (...)` (`:270,278`).
- Taxonomie hors `posts`, mixte ou inconnue : `content_count`, `states`, dates et `top_terms` restent `null`, jamais un état/une date empruntés à un contenu homonyme ; `count_status` annonce l'indisponibilité (`:260-263`).
- `term_count` reste une mesure directe (`:290`).
- Cas natifs ajoutés : `inside.py:89-92` (collision lien 41 / article, lien sans post homonyme, et `link_category` + `a12_mixed_tax` renvoyés indisponibles) sur les deux magasins.

### Instruction 3 — README : aligner le texte du reconnaisseur de liens
**Non appliquée.** `wp/outils/bascule/a12/README.md:27` dit toujours « clés reconnaissables **contenant** `product`, `produit`, `article`, `numero`, `issue`, distinguées par casse ». Le motif réel (`Inventory.php:183`) exige un **jeton délimité** (`(?:^|_)…(?:_ids?)?(?:_|$)`, insensible à la casse). La correction demandée (« jeton délimité … + `_id`/`_ids`, pas "contenant" ») n'est pas portée sur cette ligne. Les autres lignes du README ont bien été mises à jour (disjonction B1, `object_types`/`link_category` I1, nommage du refus symlink). Écart de **formulation documentaire uniquement** ; le code conserve le bon comportement conservateur (classé « Mineur » par la fusion).

### Instruction 4 — vérification : rejeu natif dans un environnement WSL/Docker avant clôture
**Partiellement (dans la limite de mon environnement).**
- Ce que j'ai pu rejouer ici (Windows, sans Docker/Landlock) :
  - `test_confine.py` (autonome, `PurePosixPath`) : **PASS** — valide directement la disjonction B1.
  - `verify.py production/A-12/preuves/final` : **47/47 PASS, verdict `NATIVE_VERIFIE`, exit 0**. Point fort : `exact_current_source_inventory_and_hashes` PASS — le paquet de preuves committé correspond aux **sources corrigées courantes** (empreintes SHA-256), il n'est pas périmé. Les cas B1 (`guard:disjoint_launcher/php:ancestor-site|root`) et I1 (`unavailable_not_posts_invented:link_category|a12_mixed_tax`) sont présents et verts sur `classic` et `hpos`. Lecture seule, confidentialité et PSR-12 strict : PASS.
- Ce que je n'ai **pas** pu faire : ré-exécuter moi-même la suite native (Docker/Landlock/MariaDB) pour **regénérer** les preuves. WSL/Docker et les appels `php`/`wsl` sont indisponibles dans cette session non interactive. Je valide donc des reçus committés, cohérents et liés aux sources corrigées — mieux que le 40/41 du premier tour (qui échouait sur la précondition Docker) — mais non ré-engendrés indépendamment par moi.
- Hermès déclare un rejeu réel complet (corrections-b1-i1-26nov.md) : 15 unitaires PHP, 132 natifs, 8 runner, 6 style, test Python de disjonction exécuté, vérificateur 47 PASS, PHPCS code 0. Ces chiffres concordent exactement avec le `verify.py` que j'ai relancé.

## 2. Résultat des tests

| Test relancé ici | Résultat |
|---|---|
| `wp/tests/a12/test_confine.py` (B1, autonome) | **PASS** (1 test) |
| `wp/tests/a12/verify.py production/A-12/preuves/final` | **PASS — 47/47, `NATIVE_VERIFIE`, exit 0** |
| Suite native Docker/Landlock (regénération) | Non exécutable ici (pas de WSL/Docker) — reçus committés validés et liés aux sources courantes |

## 3. Régressions / modifications non demandées

- **Propagation A-11 (hors des 4 instructions A-12).** Les corrections B1/I1 arrivent avec une reprise des « refus nommés A-11 » : `wp/outils/bascule/a11/*` modifié (Runtime.php, ReadOnlyDb.php, Inventory.php, README, inventorier-adresses) et `a12/inventorier-contenus` appelle désormais `Runtime::refusalMessage()`. Le diagnostic d'erreur a12 porte maintenant le nom du fichier en cause (ex. `A11_SYMLINK_UNSUPPORTED {…}`). Le README a12 abandonne la mention « réutilise **sans modification** a11 ».
  - Impact sur A-12 : la sortie JSON du rapport est inchangée (confidentialité et `before==after` toujours verts dans `verify.py`) ; seul le `stderr` de diagnostic est enrichi. Pas de régression constatée du livrable nominal A-12.
  - Réserve : c'est une modification **inter-lot** qui relève de la correction/vérification propre à **A-11**, pas du périmètre de `corrections/A-12.md`. Elle doit être couverte par la vérification d'A-11.
- **Décisions techniques (défauts « garder »).** Dates `publish`-seulement et comportement du reconnaisseur de liens : conservés comme prévu. Non-régressions.
- Aucune autre modification non demandée sur le code a12.

## 4. Verdict

**Prêt pour la validation de Ced**, sous deux réserves non bloquantes :

1. **Instruction 3 non appliquée** — `README.md:27` (Liaisons) reste à aligner sur le motif réel (jeton délimité `product/produit/article/numero/issue` + `_id`/`_ids`, pas « contenant »). Écart de formulation, aucun impact de comportement, aucun arbitrage de Ced requis — à corriger pour fermeture propre.
2. **Rejeu natif indépendant non reproductible dans mon environnement** — je confirme la cohérence et la liaison aux sources corrigées (verify.py 47/47 ici) mais pas une regénération container indépendante ; elle repose sur le rejeu WSL/Docker déclaré par Hermès.

Les deux défauts de fond de la fusion sont réglés et prouvés : **B1 (bloquant)** confinement disjoint dans les deux sens, `/` refusé, lanceur et PHP ; **I1 (important)** taxonomies hors `posts` indisponibles sans invention. Aucun problème de fond restant, aucune question ouverte pour Ced (visuel / réel). Les deux réserves ci-dessus sont documentaires/environnementales, pas des régressions.

**Rappel doctrine : ce verdict n'est pas un GO** (§3 doctrine). Il vaut pour la clôture d'un lot de code ; la correction du README (instruction 3) reste souhaitable avant clôture formelle.
