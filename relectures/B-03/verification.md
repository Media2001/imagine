# Vérification B-03 — second et dernier tour

Date : 25/11/2026. Vérificateur : Claude (relecteur indépendant).
Objet : contrôler l'application de `corrections/B-03.md` par Hermès, relancer les tests, repérer régressions et modifications non demandées, poser un verdict.

**Base de comparaison.** Version relue = commit `8b6c1eb` (25/11 18:48, qui porte `relectures/B-03/claude.md`, `codex.md` et `corrections/B-03.md`), avant toute correction. Diff et `git log` sur `wp/` et `production/B-03` jusqu'à `HEAD` (`39ef378`).
Sources B-03 réellement modifiées depuis : `reading.css`, `reading.js`, `b03-http.py`, `test_b03_contract.py`, `b03-reading.test.cjs`, `b03-final.py`, plus nouveaux tests `b03-colors.py`, `b03-preservation*.py`, `b03-reduced-motion.py` et reçus associés.

---

## 1. Instructions de corrections/B-03.md

### Instruction 1 — Neutraliser les couleurs du contenu éditorial (B03-C1) — **Appliquée**
- `wp/themes/imagine/assets/reading.css:54-61` : nouvelle règle en portée `.imagine-reading .imagine-article-body` (+ `:where(:not(img, picture…, svg…, video…, audio…, canvas, iframe, object…, embed, source))`) qui force `color: var(--imagine-ink) !important` et `background-color: var(--imagine-paper) !important`. Le `!important` passe devant les `style="color:…"` et les classes `has-text-color`/`has-*-background-color`. Médias et descendants exclus : images et SVG intacts.
- Portée = les **trois** fonds (défaut prudent de la décision technique respecté), car la règle ne dépend pas du thème choisi.
- Tests obligatoires présents : `wp/tests/demo/b03-colors.py` injecte un paragraphe `style="color:#000000"`, un bloc `has-text-color has-vivid-red-background-color` + inline, un paragraphe inline, et une image colorée ; vérifie `ratio ≥ 4,5` pour chaque sonde dans `light`/`sepia`/`dark`, l'intégrité du DOM (`DOM_intact`), de l'image (`image_intacte`) et le rétablissement de la couleur d'auteur à la sortie (`couleur_auteur_retablie`, `contenu_DOM_original`).
- Preuve Hermès `production/B-03/browser-colors-corrections.json` : **77 contrôles, 0 échec**, ratios des sondes `21 / 14,26 / 16,16` (clair/sépia/sombre), tous ≥ 4,5.

### Instruction 2 — Corriger la sauvegarde de position (B03-C2) — **Appliquée**
- `wp/themes/imagine/assets/reading.js:56-61` : `saveDeparture()` appelle `update()` **si le mode est actif** avant `save()` → la fraction est recalculée synchroniquement, sans dépendre de la rAF en attente.
- Branché au départ et au masquage : `reading.js:117` (`visibilitychange` → `saveDeparture`) et `reading.js:120` (`pagehide` → `saveDeparture`). L'ancien `save` direct a disparu de ces deux voies.
- Cas inactif préservé : hors lecture, `update()` n'est pas appelé, la fraction mémorisée n'est pas écrasée par le scroll ordinaire.
- Tests ajoutés `wp/tests/demo/b03-reading.test.cjs` : deux cas « départ `pagehide`/`visibilitychange` avant flux de rAF » (scroll 1200, départ, reprise = 1200, `behavior:'instant'`, progress 50) et un cas « départ inactif » (vérifie `{active:false, position:0.5}` conservé). Le compte JS passe de **5 à 8** (reçu `JS: 8`).

### Instruction 3 — Faire lire la constante serveur au test HTTP — **Appliquée**
- `wp/tests/demo/b03-http.py` : nouvelle fonction `reading_speed()` qui lit `\Imagine\Theme\IMAGINE_READING_WORDS_PER_MINUTE` via `wp eval`, valide le type, et le calcul devient `max(1, (words + speed - 1) // speed)`. Le nombre magique `200`/`199` a disparu. La vitesse est reportée dans le reçu (`reading_words_per_minute`).
- Garde-fou ajouté `wp/tests/demo/test_b03_contract.py` : `test_HTTP_lit_la_constante_du_serveur_sans_valeur_magique` (mock sur deux vitesses, interdit `// 200` et `words + 199`).

### Instruction 4 — Décider du bloc `reading.css` `prefers-reduced-motion` — **Appliquée** (retrait)
- Le bloc `@media (prefers-reduced-motion: reduce) { html.imagine-reading { scroll-behavior: auto } }` est **retiré**. Il ne reste qu'un seul `scroll-behavior: auto;` (ligne 12), le vrai verrou anti-animation restant `reading.js` (`behavior:'instant'`).
- Contrat mis à jour `test_b03_contract.py` : `assertNotIn('prefers-reduced-motion', css)` et `css.count('scroll-behavior: auto;') == 1`.
- Test dédié ajouté `wp/tests/demo/b03-reduced-motion.py`.

### Instruction 5 — Rejouer la part B-03 non reproduite (10 assertions PHP, recette HTTP du témoin) — **Partiellement**
- Exécutée dans le harnais de **Hermès** (reçus `reconciliation-c15/…/php-corrections.json` = 10 PHP, `http-corrections.json` = 43 HTTP, statut VERIFIED).
- **Mais** l'instruction visait une reproduction par **un relecteur** disposant de `php` et du site. Ce n'est toujours pas le cas : `php` et `docker` sont absents de ce poste, l'accès au site/compte est interdit (doctrine §3), et l'exécution d'interpréteur (`node`, `python`) est bloquée ici par le poste (voir §2). La zone « jamais reproduite par un relecteur indépendant » reste donc ouverte, comme le signalait la fusion.

---

## 2. Résultat des tests

**Je n'ai pas pu relancer les tests moi-même.** `php` et `docker` sont absents du poste ; `node` et `python` sont présents mais chaque appel d'interpréteur est refusé par la politique d'exécution de cette session non interactive. Conforme à la limite du premier tour (Claude : `node --test` refusé ; `php` hors PATH). Je me suis donc appuyé sur la lecture du code et des tests, et sur les reçus déposés par Hermès, en vérifiant que les empreintes des reçus correspondent aux fichiers présents (`remote_sha256` == `source_sha256` pour les six fichiers du thème).

Dernier reçu Hermès `production/B-03/reconciliation-c15/20261125T192627238444Z/verification-finale.json` (pointé par `reconciliation-c15-current.json`) : **status VERIFIED, 35 contrôles finaux, 0 échec**.
- PHP B-03 : **10** · HTTP : **43** · JS : **8** · régression locale : **15**
- T01 canonique : **1012 tests, 34006 assertions, 0 échec / 0 erreur / 0 ignoré**
- C09 natif : **149/149** · navigateur anonyme (dont sondes couleur C1) : **77**, 0 échec
- Contrastes des fonds : clair 21,0 · sépia 14,26 · sombre 16,16 (≥ 4,5)
- Script : 6045 octets / 1956 gzip (sans bibliothèque)

Ces nombres restent des **preuves fournies par Hermès**, non reproduites par un relecteur indépendant. Le point le plus sensible — les 10 assertions PHP de `imagine_reading_minutes` et la recette HTTP du témoin — reste la seule zone qu'aucun relecteur n'a exécutée (cf. instruction 5).

---

## 3. Régressions et modifications non demandées

- **`b03-final.py` fortement réécrit** (non demandé par les corrections). Le script passe à un espace de reçus daté (`reconciliation-c15/<horodatage>/`), préserve l'ancien reçu en échec, et ajoute une réconciliation avec le lot **C-15** (snapshots avant/après, garde de préservation, relecture C09 native). Motivation lisible : un autre worker (C-15) touche la base pendant le rejeu, et il ne faut ni écraser l'état métier ni le reçu historique. **N'affecte pas le code livré du thème** (`reading.css`/`reading.js`/`inc/reading.php` inchangés par cette réécriture). À considérer comme un durcissement du harnais de preuve, pas une régression — mais c'est une extension de périmètre à signaler.
- **`functions.php:12` ajoute `require_once __DIR__ . '/inc/catalogue.php'`** et le fichier `inc/catalogue.php` est nouveau. Il relève d'un **autre lot** (catalogue, arrivé le 25/11 à 19:58+, après les corrections B-03), pas de B-03. Il modifie l'empreinte de `functions.php` sans toucher le point de sortie unique `imagine_article_body()` ni l'enqueue du mode lecture. Pas une régression B-03 ; changement d'un lot voisin qui cohabite.
- Le reste du diff (`A-05`, `A-08`, `B-04`, `C-09`, `C-15`…) appartient à d'autres lots, hors périmètre B-03.
- Aucune régression constatée sur le comportement livré de B-03 : sortie unique B-01/C-08, paywall côté serveur, bloc d'abonnement conservé, stockage local sans réseau — tout est intact dans `reading.css`/`reading.js` relus.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Les quatre instructions de code/tests (1 à 4) sont **appliquées et couvertes par des tests**. Aucun problème de fond ne subsiste dans le code livré. Les deux points encore ouverts ne sont pas des défauts de code :
- la **reproduction indépendante** des 10 assertions PHP et de la recette HTTP du témoin (instruction 5) reste due avant mise en service — question de poste/process, pas de code ;
- les éléments **visuels** déjà listés « À arbitrer par Ced » dans la fusion demeurent (variables de `besoins-designer.md` à fixer, revalidation visuelle du contraste AA sur un article réel une fois les couleurs du designer choisies).

Ces deux items relèvent précisément de la validation de Ced (visuel) et d'un rejeu à confirmer, non d'un « problème de fond restant » justifiant un retour à Hermès.

> Rappel doctrine : ce verdict de vérification n'est pas un GO. B-03 porte une dimension visuelle ; sa clôture passe par Ced (maquettes, variables du designer, contraste revu), et le rejeu complet de la part PHP/HTTP par un relecteur disposant de `php` et du site reste à faire avant toute mise en service.
