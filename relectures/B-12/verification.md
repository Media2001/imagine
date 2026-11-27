# Vérification B-12 (2e et dernier tour) — aucun appel sortant depuis le corps

Vérificateur : Claude. Date : 27 novembre 2026. Base corrigée : `corrections/B-12.md` (fusion, verdict **À corriger**, un bloquant).
Code relu : `wp/plugins/imagine-site/IntegrationsCorps.php`. Preuves : `production/B-12/`.
Méthode : `git diff` depuis la version relue (`77f51817`, antérieure à la fusion) sur `wp/` et `production/B-12/`, relance des tests du lot, lecture de l'arbitrage parent `docs/arbitrages-2026-11-27.md` (passage de 16h30).
Ce n'est pas une relecture complète ; c'est le contrôle des six instructions, des tests, et des régressions.

---

## 1. Instructions de `corrections/B-12.md`, une par une

**Instruction 1 — B12-01 (bloquant) : reconnaître la route proxy comme le routeur, insensible à la casse.**
**Appliquée.** `IntegrationsCorps.php:72` : la comparaison exacte `rtrim($request->get_route(), '/') !== '/oembed/1.0/proxy'` est remplacée par `strcasecmp(rtrim($request->get_route(), '/'), '/oembed/1.0/proxy') !== 0`. C'est l'une des deux options demandées (appariement sans tenir compte de la casse). Les gardes natives sont intactes sur la même ligne et les suivantes (`is_string($url)`, `self::externe($url)`, `!is_wp_error($response)`, `current_user_can('edit_posts')` — `IntegrationsCorps.php:73-74`). Diff confiné à cette seule ligne ; aucun autre changement fonctionnel.

**Instruction 2 — B12-01 (test) : variantes de casse, cache absent puis transient ancien, zéro sortie et lien seul.**
**Appliquée.** Deux preuves :
- Matrice native `wp/tests/demo/b12-routes-runtime.php` (nouveau fichier) : routes `/oembed/1.0/proxy`, `/oembed/1.0/PROXY`, `/oembed/1.0/PrOxY` × cache `absent`/`ancien`. Le cas `ancien` pose un vrai transient `oembed_*` contenant un ancien `<iframe>`/`thumbnail_url`, vérifie par témoin que le proxy natif le consommerait sans le filtre, puis contrôle, filtre en place : route native appariée, lien exact seul (`version,type,html`), jamais iframe/vignette, zéro tentative sortante, et refus anonyme/`edit_posts` révoqué. Reçu `contrat-routes-final-V2.json` : exit 0, **52 contrôles, 6 cas, transport 0, aucun contrôle faux**.
- PHPUnit `tests/IntegrationsCorpsB12Test.php:69` (`testProxyCaseVariantsKeepLinkShapeAndPermissionGuard`) : `PROXY`/`PrOxY`, forme de lien et garde de permission.

**Instruction 3 — B12-02 (important) : réception complémentaire de l'arbre actuel incluant C-29, sans neutraliser `SOURCES` ni remplacer l'empreinte de `imagine-site.php` sans preuve.**
**Appliquée, puis remplacée par un arbitrage parent — intention respectée.** Deux temps :
- D'abord à la lettre : `correction-bootstrap-C29-V2.json` établit le bootstrap courant `e27ee706…` ; retrancher le seul bloc C-29 (lignes 178-181) redonne `9530b508…`, l'empreinte historique B-12 ; le branchement B-12 (lignes 174-176) est inchangé octet pour octet. Reçu dans `reception-corrections-V2.json`, qui garde `SOURCES` en égalité stricte sur l'arbre courant (aucune empreinte remplacée).
- Puis l'arbitrage de 16h30 (`docs/arbitrages-2026-11-27.md`, « la réception est de nouveau périmée par une ligne d'un autre lot » et section « B-12 — à corriger ») **remplace explicitement l'instruction 3** : le fichier d'amorçage partagé se contrôle désormais par contrat (fichiers propres du lot + bloc d'enregistrement exact), jamais par l'empreinte entière, pour B-11, B-12, C-29 et les lots suivants. Réception courante `reception-contrat-V2.json` : `sources` = égalité stricte sur les fichiers propres B-12 (dont `IntegrationsCorps.php` `242bfd18…`), `bootstrap_contract` = bloc B-12 exact, 1 occurrence, `readme_section` bornée. `SOURCES` n'est pas neutralisée (l'arbitrage le dit noir sur blanc) ; aucune empreinte de `imagine-site.php` n'est remplacée sans preuve — elle n'est simplement plus scellée en entier. Le reçu littéral reste conservé brut comme historique.

**Instruction 4 — mineur : README dit que `rejouer.ps1` tourne sur doublures et ne prouve pas le pipeline réel.**
**Appliquée.** `wp/plugins/imagine-site/README.md:603` : « La suite scellée `rejouer.ps1` utilise des **doublures maison** … elle **ne prouve pas le pipeline natif ni le zéro appel sortant réel** » ; renvoi à `b12-runtime.php` et `b12-routes-runtime.php`.

**Instruction 5 — mineur : aligner les compteurs sur le rejeu réel.**
**Appliquée (avec un chiffre plus récent que celui de la fusion).** La fusion citait 1 201 / 36 613. Depuis, le test de variantes de casse (B-12 passé de 5/37 à 6/47) et C-29 ont été ajoutés ; un rejeu frais donne **1 204 tests / 36 667 assertions**, reporté de façon cohérente dans `NOTE.md:7,19` et `A-VOIR.md:41`. L'écart avec 36 613 s'explique par les tests ajoutés, pas par une divergence — alignement correct sur le rejeu réel courant.

**Instruction 6 — mineur : condition de non-régression, rejouer la matrice native à chaque montée de version du cœur.**
**Appliquée.** `README.md:604` (« À chaque montée de version du cœur WordPress, rejouer cette matrice native … avant de déclarer le lot prêt »), repris dans `NOTE.md:22` et `A-VOIR.md`.

---

## 2. Résultat des tests (relancés par moi, en local)

- `python -B wp/tests/demo/b12-contract-proof-tests.py` → **7 tests OK**.
- `python -B wp/tests/demo/b12-correction-proof-tests.py` → **11 tests OK**.
- `python -B wp/tests/demo/b12-proof-tests.py` → **6 tests OK**.
- `python -B wp/tests/demo/b12-verifier.py` (mode hors ligne, contrat courant) → **B12 PASS** : native 56, routes 52 / 6 cas, 0 tentative avec verrou, mutation 6 tentatives B00, PHPUnit 6/47, suite 1 204 / 36 667. Paquets étrangers rouges signalés : **A-31** et **A-32** (hors lot, préexistants).
- Reçus natifs scellés revérifiés : `contrat-native-final-V2.json` (exit 0, 56 contrôles, transport 0), `contrat-mutation-final-V2.json` (exit 0, 15 contrôles, transport 0), `contrat-routes-final-V2.json` (exit 0, 52 contrôles / 6 cas, transport 0) — aucun contrôle faux. Le vérificateur confirme que les empreintes de sources correspondent à l'arbre courant (dont la correction `strcasecmp`).

**Limite de vérification (déjà actée, non nouvelle).** Je n'ai pas relancé moi-même la matrice native dans un vrai WordPress ni le conteneur scellé `rejouer.ps1` (ils exigent un WordPress réel + Docker/WSL, hors de mon périmètre d'exécution). Je m'appuie sur les reçus natifs d'Hermès, dont j'ai vérifié les empreintes et le contenu. La garantie « zéro sortie » du pipeline réel repose sur ces matrices natives — limite écrite au README et acceptée à l'arbitrage. A-31/A-32 restent rouges comme avant, sans rapport avec B-12.

---

## 3. Régressions et modifications non demandées

- **Aucune régression de code.** Le seul changement fonctionnel de B-12 est la ligne `strcasecmp` ; `imagine-site.php` n'a pas été touché par les corrections B-12 (le branchement 174-176 est intact, vérifié par le `bootstrap_contract`).
- **Changements voisins présents dans l'arbre mais hors B-12** : C-29 (ContactBrevo) et la migration par contrat de B-11 apparaissent dans le diff ; ce sont des lots distincts menés en parallèle, pas un effet des corrections B-12. Aucun fichier de production voisin n'a été rescellé en douce (dit explicitement dans NOTE/A-VOIR, et les lecteurs historiques B-11/C-28/C-29 peuvent rester rouges, règle acceptée à 16h30).
- **Point de méthode à signaler, pas un défaut** : l'instruction 3 n'a pas été exécutée telle quelle mais remplacée par un arbitrage parent documenté (16h30). C'est une décision tracée, cohérente avec le fond de l'instruction (ne pas neutraliser `SOURCES`, prouver que la dérive vient de C-29) — pas une déviation silencieuse.
- Aucun secret, aucune donnée réelle, aucun accès à un compte/site/base ; fixtures fictives en `@example`/`.invalid`.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Le bloquant B12-01 est corrigé (`strcasecmp`, `IntegrationsCorps.php:72`) et couvert par un test natif de variantes de casse avec cache absent/ancien (52 contrôles verts, zéro sortie, lien seul) et un test PHPUnit. L'important B12-02 est résolu par le passage au contrat (arbitrage 16h30) : `reception-contrat-V2.json` vérifie vert sur l'arbre courant, `SOURCES` stricte sur les fichiers propres et bloc d'amorçage exact, sans empreinte remplacée. Les trois mineurs (README doublures, compteurs, non-régression) sont appliqués. Tous les tests du lot que je peux lancer sont au vert ; les reçus natifs scellés sont verts et leurs empreintes concordent.

Aucun problème de fond ne subsiste, aucune question n'exige l'arbitrage personnel de Ced (lot sans dimension visuelle). **Rappel : ce verdict n'est pas un GO** au sens du §3 de la doctrine — il ne vaut que pour la clôture de ce lot de code, et ne vaut ni mise en ligne, ni accès au réel. La seule réserve permanente — la preuve « zéro sortie » repose sur une matrice native hors suite scellée — est documentée et à rejouer à chaque montée de version du cœur.
