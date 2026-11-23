# Vérification B-01 — 2e et dernier tour

Date : 23/11/2026. Vérificateur : Claude (relecteur indépendant). Ce n'est pas un GO (doctrine §6).

Périmètre : contrôle que chaque instruction de `corrections/B-01.md` §4 a été appliquée par Hermès, rejeu des tests, détection de régression. Pas de relecture complète refaite.

Base de comparaison : commit `862828c` (synchro 16:03, celui qui porte `corrections/B-01.md`) → `HEAD`. `git diff` lu sur `wp/` et `production/B-01/`. Arbitrages de Ced lus dans `docs/arbitrages-2026-11-23.md` §B-01 (les quatre questions fermées du §5 sont tranchées).

---

## 1. Instructions de `corrections/B-01.md` §4

### 1 — I-1 : rebaser les preuves sur l'état réel — **Appliquée**
- Décision de Ced appliquée (arbitrage §B-01 Q3 : B-01 se clôt sur un **seul** jeu de preuves régénéré sur l'état actuel).
- `production/B-01/notes.md:5-9` déclare franchement que le thème a été enrichi par C-08 (raccord dans `imagine_article_body()` + quatre `parts/paywall-*.php`), que le seul jeu courant est `verification.json`/`runtime.json`/`http/`/`captures/`, et que l'ancienne livraison (état pré-paywall) est archivée dans `production/B-01/historique/pre-C08-livraison-initiale/`.
- Preuves effectivement régénérées : `verification.json`, `runtime.json`, `installation.json`, `http/*.html` et `captures/` tous réécrits (git diff le confirme), reliés par `b01-final-verification.json`.

### 2 — I-2 / I-4 : accueil et recette — **Appliquée**
- **Purge « Hello world! » côté seed B-00** (arbitrage Q1 : purge côté B-00, aucun filtre éditorial ajouté au gabarit). `wp/outils/demo/b00-seed.php:21` purge les identités d'installation (`hello-world` id 1, `sample-page` id 2) ; trace `installation_posts_purged` en sortie (`b00-seed.php:208`).
- `wp/themes/imagine/front-page.php` **inchangé** : aucun filtre « article avec numéro » ajouté, conforme à l'arbitrage.
- **Recette durcie** : `wp/tests/demo/b01-verifier.py:121` compare la liste **ordonnée** des cinq articles d'accueil à un oracle indépendant (`b01_expectations.latest_article_ids` / `home_matches`), issu de l'énumération des clés de fixtures B00 + les deux IDs C08 nommés, et non du simple comptage. L'oracle lève si l'inventaire publié diffère des fixtures (`b01_expectations.py:20-23`). Tests négatifs ajoutés : intrusion de l'ID 1 refusée (`b01-verifier.py:124`), permutation refusée (`b01-verifier.py:125`). La sélection cible la section `section[aria-labelledby="imagine-latest-posts"]` (`front-page.php:16`), pas le dernier numéro.

### 3 — I-3 : environnement de test reproductible — **Appliquée (reproduite par le vérificateur)**
- Dépendances figées : `production/B-01/validation/requirements.lock` liste les 6 paquets avec empreintes (`html5lib`, `webencodings`, `beautifulsoup4`, `soupsieve`, `six`, `typing_extensions`) ; les wheels correspondantes sont présentes dans `validation/`.
- `wp/tests/demo/b01_html.py:1-2` ne charge plus les wheels par `glob` : import direct, l'environnement isolé est désormais la seule voie.
- Procédure locale isolée : `production/B-01/b01-isolated.py` crée un venv neuf hors packages globaux, installe **hors ligne** (`--no-index --require-hashes`), vérifie les chemins d'import, lance les tests et revalide les 43 HTML.
- **Rejoué par moi** : `python production/B-01/b01-isolated.py` → installation hors-ligne à empreintes vérifiées OK, **6 tests Python PASS**, **43 pages HTML, 0 erreur** de structure. Les quatre tests ne sont donc plus présentés comme rejouables depuis le dépôt nu : ils le sont via l'environnement isolé, et je l'ai confirmé.

### 4 — M-1 : « Partenariat » — **Appliquée**
- Arbitrage Q2 (oui, dès maintenant). `wp/themes/imagine/archive-imagine_partenaire.php:10-11` : mention traduisible « Partenariat » + déclaration « Les liens vers les partenaires sont déclarés comme liens sponsorisés ».
- `wp/themes/imagine/functions.php:104` : `rel="sponsored"` sur les liens de la liste partenaires ; `functions.php:130-146` (`imagine_partner_content`) ajoute `sponsored` aux liens externes du corps d'une fiche partenaire seulement, en préservant les autres `rel`. Vérifié par recette : `b01-verifier.py:109-112`.
- Traitement graphique laissé au designer (`notes.md:29`).

### 5 — M-4 à M-7 — **Appliquée**
- **M-4** `style.css:5` : `Requires at least: 7.0` **conservé**. Conforme à l'arbitrage Q5 (version minimale = pile cible réellement installée, WordPress 7.0.9). La remarque de relecture « WP 7 inexistant » ne vaut pas pour le banc installé ; justifié en `notes.md:5`.
- **M-5** dates localisées : `functions.php:124-126` utilise `wp_date('j F Y', …, wp_timezone())` avec l'ISO conservé dans `datetime`. Vérifié `b01-verifier.py:106-107`.
- **M-6** message de recherche vide spécifique : `functions.php:98-100` distingue `is_search()` → « Aucun résultat pour votre recherche. ». Vérifié `b01-verifier.py:104`.
- **M-7** locale `fr_FR` : installée côté B-00 via `b00_locale` (étape `langue-francaise`, `construire.py`). Hors thème, conforme.

### 6 — M-2 / M-3 : fragilités latentes — **Appliquée**
- **M-2** (kiosque) : arbitrage Q4 (date de sortie **obligatoire** à la publication, pas de repli). `wp/plugins/imagine-site/NumeroPublication.php` impose une date valide : insertion/mise à jour native sans date → brouillon (`:31-43`), REST → erreur 400 explicite (`:45-56`), modification/suppression d'une date d'un numéro publié refusées (`:70-78`), numéros programmés gardés. La requête kiosque (`functions.php:74`, `imagine_issue_query` `:88`) conserve donc légitimement la jointure `meta_key` : plus aucun numéro publié ne peut être sans date.
- **M-3** (navigation) : `functions.php:126-148` indexe la navigation par **clés slug stables** (`accueil`, `kiosque`, …) et non par URL ; attribut `data-imagine-nav`. Collision de trois archives sur la même URL testée (contrôle PHP ciblé, `notes.md:42`).

### 7 — M-8 : traçabilité `notes.md` (doctrine) — **Appliquée**
- `production/B-01/notes.md:20-35` : tableau rattachant chaque gabarit/comportement au paragraphe du cahier (§3.1-3.3, §3.11, §3.12, §4.2) et qualifiant réalisé / provisoire / reporté, plus le besoin du designer.

### 8 — `docs/ecarts.md` (écart de méthode) — **Non appliquée**
- L'instruction demandait de reporter, daté, l'écart de méthode déclaré (`notes.md` : tests/amorce du shell avant références).
- `docs/ecarts.md` a bien reçu une section « 23 novembre 2026 — voie 2 », mais ses deux lignes portent l'écart B-00 (fusion `imagine-site`) et le modèle de contenu provisoire — **pas** l'écart de méthode B-01.
- Hermès l'a volontairement différé : `notes.md:50` écrit « écart initial à transmettre à Claude pour `docs/ecarts.md` … aucun document global n'a été écrit par ce lot ». L'écart reste donc déclaré dans `notes.md`, non transcrit dans le registre.
- **Qui corrige** : `docs/ecarts.md` est tenu par Claude (doctrine §7) ; le vérificateur n'a pas le droit d'écrire dans `docs/`. C'est une action de clôture, **pas un problème de fond** (voir §4).

### 9 — C-08 (hors B-01) : garde `wc_get_page_permalink` — **Appliquée**
- `wp/themes/imagine/parts/paywall-regularisation.php:8` : appel protégé par `function_exists('wc_get_page_permalink')`, repli `wp_login_url()`. Plus de fatale si WooCommerce absent. (Relève de C-08, mais fait.)

### 10 — Rejeu réel sur le banc autorisé — **Appliquée côté Hermès, partiellement reproductible par le vérificateur**
- Le rejeu **isolé** (tests unitaires + validateur HTML) est reproductible depuis le dépôt : je l'ai relancé (§1.3), **6 tests PASS, 43 HTML OK**.
- Le rejeu **live** (`b01-verifier.py`, `b01-final.py`, contrôles PHP ciblés) exige le staging : interdit au relecteur (doctrine §3). Preuves jointes par Hermès et cohérentes : `verification.json` (**554 assertions runtime/HTTP, 0 échec**, `notes.md:71`), **16 contrôles PHP ciblés**, 19 captures, 5 contrôles d'interaction. Preuves **produites par Hermès**, non reproduites par moi.

---

## 2. Résultat des tests (rejoués par le vérificateur)

- **Environnement isolé B-01** (`python production/B-01/b01-isolated.py`) : installation hors-ligne à empreintes vérifiées, **6 tests Python PASS** (4 de `test_b01_theme.py` + 2 de `b01-corrections.py`), **43 pages HTML validées, 0 erreur de structure**, chemins d'import assertés hors packages globaux.
- **Suite globale hors banc** (`python -m unittest discover -s wp/tests/demo -p "test_*.py"`) : **30/31 OK, 1 ERROR**. L'unique échec est `test_b01_theme.test_b01_html_validator_rejects_structural_regressions` → `ModuleNotFoundError: html5lib`. Ce n'est **pas** une régression : c'est le comportement voulu par I-3 (les dépendances ne vivent plus dans le Python global, elles s'installent dans l'environnement isolé, où ce même test passe — confirmé ci-dessus). Tous les tests B-00, C-08, C-09, C-10 passent.
- **Recettes live** (`b01-verifier.py`, PHP ciblés) : non rejouables hors banc ; preuves Hermès au vert (voir §1.10).

## 3. Régressions et modifications non demandées

- **Aucune régression B-01 détectée** par lecture ni par les tests hors banc.
- **Raccord C-08 dans le thème, déclaré.** `imagine_article_body()` (`functions.php:51-59`) rend désormais, pour un `post` réservé, l'extrait + `parts/paywall-abonnement` au lieu de l'ancien formulaire natif. Ce n'est pas une modification B-01 non demandée : c'est le raccord C-08 fondu, assumé et déclaré (`notes.md:9`), et B-01 ne certifie que le point unique de sortie et le rendu anonyme (pas le paywall ni le filtrage de recherche §3.9, renvoyés à C-08).
- **Fichiers d'autres lots modifiés dans le même intervalle** (C-08 `Paywall.php`, C-09, C-10, T-01, `imagine-pilotage/Reglages.php`) : hors périmètre B-01, non examinés ici. Les ajouts correspondent aux arbitrages C-08 du 23/11 17h10 (recherche bloquante, `NewsArticle`, mémoïsation) et relèvent de la relecture C-08.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les instructions actionnables de `corrections/B-01.md` §4 (I-1, I-2/I-4, I-3, M-1, M-2 à M-8, garde C-08) sont appliquées et citées ci-dessus ; les quatre questions fermées du §5 ont été tranchées par Ced et le code reflète ses réponses (purge côté B-00, « Partenariat » dès maintenant, preuves régénérées en un seul jeu, date de sortie obligatoire sans repli). Le durcissement I-4 est réel : l'oracle compare identifiants et ordre et refuse intrusion et permutation. L'environnement de test isolé I-3 est reproductible et je l'ai rejoué moi-même (6 tests, 43 HTML, 0 erreur).

Réserves à la connaissance de Ced, **aucune n'étant un problème de fond B-01** :
1. **Instruction 8 non appliquée** : l'écart de méthode B-01 (amorce du shell avant références) est déclaré dans `notes.md:50` mais **pas transcrit dans `docs/ecarts.md`**. Hermès l'a renvoyé à Claude. Le registre est tenu par Claude (doctrine §7) et le vérificateur ne peut écrire dans `docs/` : c'est une ligne à ajouter au moment de la clôture, pas un défaut du code B-01.
2. **Rejeu live non reproductible par le vérificateur** (banc interdit, doctrine §3) : les 554 assertions runtime/HTTP et les contrôles PHP ciblés sont attestés par les preuves d'Hermès, non reproduits par moi. Si Ced veut une certitude totale, lui seul peut relancer la recette sur le banc.
3. La conformité du paywall (filtrage de recherche §3.9, corps réservé) et le garde `wc_get_page_permalink` relèvent de **C-08**, pas de B-01 ; à clore dans ce lot.

Rappel doctrine §6 : ce verdict de vérification n'est pas un GO de production ni une validation visuelle sur maquettes ; il clôt le second tour de relecture du lot de code B-01.
