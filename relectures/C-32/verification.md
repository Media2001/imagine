# Vérification C-32 — second et dernier tour

Vérificateur : Claude. Base : `corrections/C-32.md` (fusion, verdict *À corriger*), code corrigé par Hermès puis recette rejouée par le parent.

Méthode : `git diff` entre la version relue (`1599bdf2`, PRET V2 du 28/11 01:58) et HEAD sur `wp/` et `production/C-32/` ; relance des tests ; lecture ciblée des seuls points touchés par les sept instructions. **Pas de relecture complète.**

Note de forme : le code a été restructuré. L'ancien `c32-browser.py` monolithique est scindé en règles pures `wp/outils/demo/c32_browser_policy.py` (couverture, lecture, sessions) branchées par `wp/outils/demo/c32-browser.py` ; la réception est passée dans `production/C-32/reception_c32.py` (importée par `verifier.py`). Les numéros de ligne de la fusion ne valent plus ; je cite les fichiers actuels.

## 1. Instructions de corrections/C-32.md

**1 — (R1, important) Couverture par identité d'URL avec C-26.** **Appliquée.**
`c32_browser_policy.py:12-25` (`public_paths`) dérive les chemins de `production/C-26/mutations-livraison-extension.json` et y ajoute ses `pages` + `events` ; `coverage()` (`:28-31`) compare les **ensembles** d'URL (`missing`/`extra`), pas un total. Branché en `c32-browser.py:20-22` (`paths=policy.public_paths(...)`) avec le check `couverture_publique_identique`. `verifier.py:59-62` assère `coverage['pass']`. Le relevé passe de 44 à **58 pages** (`strict-reading-corrections-V2.json`, `pages:58`). Gardé par trois tests : `test_c26_extension_is_covered_by_url_identity`, `test_same_page_count_does_not_hide_missing_url`, `test_empty_c26_inventory_is_rejected`. README `:741` documente les dix pages coopérative/soutien/sujet et les quatre fiches événement.

**2 — (R3, important) Contrôle strict réel, dans `checks` et l'assertion, borné aux sept `sbjs_…`.** **Appliquée.**
`c32_browser_policy.py:9` déclare `STRICT_CHECK='lecture_zero_cookie_strict'` ; `reading_verdict` (`:34-40`) calcule `strict_pass` (vrai seulement si lecture non vide **et** aucun cookie) et `inventory_pass = names <= READING_NATIVE` (sept noms `sbjs_…`, `:5-8`). `c32-browser.py` ajoute `STRICT_CHECK` à `checks`, pose un check `_ecart_natif_borne` par lecture, sépare les deux verdicts (`inventory` / `strict_zero_cookie`) et ajoute le mode `--strict` bloquant. `verifier.py:63-77` vérifie que le strict est bien dans `checks`, exclu du seul agrégat d'inventaire, et aligné sur `reading_verdict`. Un cookie **listé** (session/panier) apparaissant en lecture fait désormais échouer : tests `test_listed_cart_cookie_in_reading_is_rejected`, `test_strict_passes_when_cookies_disappear`, `test_empty_observation_is_not_a_pass`, `test_stale_strict_fail_cannot_be_accepted_when_cookies_disappear`. Aucun cookie désactivé.

**3 — (R4, important) Suppressions de sessions bornées aux clés attribuées, + test.** **Appliquée.**
`c32_browser_policy.py:50-68` (`restore_sessions`) ne traite que les clés `owned_keys` ; toute différence étrangère (y compris arrivée pendant le nettoyage) reste intacte et interdit `restored=True`. L'écriture passe par un compare-and-swap verrouillé `replace_session` (`c32-browser.py`, transaction + `SELECT … FOR UPDATE`) qui refuse d'écraser une arrivée concurrente. Tests dédiés : `test_concurrent_foreign_guest_is_preserved_and_not_success`, `test_changed_or_missing_foreign_session_is_not_touched`, `test_foreign_arrival_during_cleanup_is_detected`, `test_compare_and_swap_conflict_is_not_success`, `test_missing_owned_preimage_is_reinserted`, `test_only_known_guest_and_temporary_account_are_restored`. La réception assère `sessions_cleanup={restored:True,foreign_changes:0,write_conflicts:0,owned_remaining:0}` (`verifier.py:89`).

**4 — (R2, mineur) Retirer « ou connexion » du geste `wp_woocommerce_session_[hash]`.** **Appliquée.**
`Cookies.php:17` : geste désormais `'Code suivi connu (C-30), panier'`. Gardé par `CookiesC32Test::testSessionWooNeDeclarePasLaConnexionNonObservee` et par l'assertion `assertStringNotContainsString('ou connexion', …)` du rendu.

**5 — (i18n, mineur) En-têtes littéraux traduits, cellules de données en `esc_html()` seul.** **Appliquée.**
`Cookies.php:57-62` : cinq en-têtes en chaînes littérales passées à `esc_html__()`. `:65-67` : cellules de données en `esc_html($row[$key])` sans `__()`. Gardé par `testTraductionsExtractiblesEtDonneesNonTraduites` (refuse `esc_html__(\$…`) et `testRenduReelTraduitLesLitterauxSeulement...` (exactement 6 appels de traduction).

**6 — (R5, mineur) Extrait officiel par affirmation native du README.** **Appliquée.**
`README.md:731-734` : chaque ligne porte désormais un extrait cité (« to store your authentication details », « temporary cookie named `wordpress_test_cookie` », « Helps WooCommerce determine… », « The order attribution feature uses these cookies: », etc.) avec son URL, et distingue explicitement ce qui relève d'une observation de recette de ce que garantit la source.

**7 — (traçabilité, mineur) Régénérer le rejeu, comptes non recopiés.** **Appliquée.**
`replay-corrections-V2.json` + `.log` régénérés par le parent (28/11 04:56). `verifier.py:110-115` lit `tests`/`assertions` dans le `T01_RESULT` du rejeu réellement produit — aucun total codé en dur. Comptes courants : **1240 tests / 37024 assertions** (vs 1229/36926 au premier tour), 0 échec.

## 2. Résultat des tests

Relancés par moi sur le NUC.

- **Règles pures** `python -B wp/tests/demo/c32-browser-test.py` → **20 tests, OK** (couverture C-26, strict/inventaire, nettoyage sessions, câblage réel).
- **Banc local scellé** `python -B production/C-32/test-local.py <étiquette neuve>` (conteneur jetable WSL/Docker, `--network none`, dépôt monté en lecture seule) → cinq runs `exit=0` : `image-inspect`, `python` (20 tests OK), `php-lint`, **`phpunit` OK (5 tests, 52 assertions)**, `python-syntax`. `pass: true`. *(Artefacts de ma relance supprimés ensuite pour ne pas polluer `production/C-32/`.)*
- **Réception complète** `python -B production/C-32/verifier.py` → `C32: PASS_LOCAL_OFFLINE_ONLY` puis `C32: PASS_INVENTAIRE` ; `native:21`, `browser:254`, `pages:58`, rejeu canonique `1240 tests / 37024 assertions`, `failures:0`. `simple_lecture_zero_cookie: FAIL` (voir §3).

Le `FAIL` du zéro-cookie strict est **attendu et documenté** : les sept cookies natifs `sbjs_…` d'attribution d'origine persistent, l'attribution n'est pas désactivée. C'est le défaut prudent retenu dans la fusion (« Pour Imagine », laisser l'attribution activée et le FAIL documenté). L'inventaire autorisé, lui, est **PASS**. `PRET` reflète cet état : « inventaire autorisé PASS ; zéro cookie strict FAIL ; attribution native non désactivée ».

## 3. Régressions et modifications non demandées

- **Aucune régression dans le périmètre C-32.** Les sept corrections touchent exclusivement des fichiers C-32 : `Cookies.php`, `c32_browser_policy.py`, `c32-browser.py`, `reception_c32.py`/`verifier.py`, `CookiesC32Test.php`/`CookiesC32Stubs.php`, section C-32 du README, `production/C-32/*`. **C-30 (`CodesSuivis*.php`) n'est pas touché par la correction C-32.** Les autres fichiers modifiés dans le diff global (`CodesSuivis*`, `DomainesRefuses*`, `ComptesPublics*`, C-31/C-33) appartiennent à des lots corrigés en parallèle et sont hors de ce lot.
- **Interdits tenus :** aucune valeur de cookie dans le dépôt ; aucun bandeau, outil de consentement ou script ajouté ; aucun cookie natif désactivé ; rien de C-30 modifié.
- **Point mineur, non bloquant (documentation).** La section README `:743` affirme encore « État de cette correction : local seulement, PRET retiré », décrivant le relais du worker. Le parent a depuis rejoué la recette live et rétabli `PRET` + les reçus `*-corrections-parent*-V2`. Le texte est donc légèrement périmé par rapport à l'état final. Cosmétique : les preuves (reçus, `PRET`, verifier) font foi et sont cohérentes entre elles.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les sept instructions de `corrections/C-32.md` sont appliquées, chacune citée dans le code et gardée par un test. Tests au vert (règles pures 20/20, PHPUnit 5/52, réception `PASS_INVENTAIRE`, rejeu 1240/37024 sans échec), relancés indépendamment. Aucune régression ni modification hors périmètre. Le seul `FAIL` subsistant — zéro cookie strict en lecture — est l'écart natif voulu, documenté et séparé de l'inventaire ; il relève d'une question rangée pour Imagine et son conseil (consentement), pas d'un problème de fond, et il est tenu par un défaut prudent (attribution laissée activée). Aucune question visuelle ni touchant au réel n'est en suspens pour Ced.

Rappel doctrine : ce verdict de vérification n'est pas un GO au sens du §3 ; il ne vaut que pour la clôture du lot de code.
