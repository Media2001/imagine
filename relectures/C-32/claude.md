# Relecture C-32 — Les cookies qu'un visiteur reçoit (Claude, indépendant)

Brief : `briefs/C-32-les-cookies-qu-un-visiteur-recoit.md`. Cahier : §3.14, §4.4.
Codex non lu. Pas de fusion à ce stade.

## Suite PHP rejouée

Commande autorisée, sans argument :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Conteneur jetable, réseau coupé, dépôt en lecture seule. Dernière ligne :

```
REJEU : 1229 tests, 36926 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

`CookiesC32Test` présent dans le rejeu ; isolation `network=none`, `rootfs=ro`, `cap-drop=ALL`.

## 1. Conformité

- **Le standard d'abord.** `README.md:728-733` : cinq lignes, trois sources officielles (WooCommerce cookies, attribution d'origine, cookies WordPress), reprises dans `standard-V2.json` avec sha256 et termes relevés. Le réglage natif d'extinction est cité : `woocommerce_feature_order_attribution_enabled=no`. Conforme à la demande « cinq lignes, sources citées, quel réglage natif les éteint ».
- **Liste fermée écrite dans le code.** `Cookies.php:11-26` : 14 lignes, chacune avec nom/motif, producteur, geste, durée, usage. Aucune valeur. Conforme.
- **Test qui parcourt les pages publiques en anonyme.** `c32-browser.py` relève les cookies par en-tête de réponse **et** par le navigateur après scripts (`page.on('response')` + `ctx.cookies()`). 44 pages en simple lecture, plus les gestes. Un cookie hors liste fait échouer le contrôle (`require_listed`). Conforme.
- **Mutation témoin.** Deux sondes (`mutation_header`, `mutation_script`, `c32-observer.php`) posent `c32_sonde_hors_liste` ; `check(kind+'_mutation_detectee', refused and bad==['c32_sonde_hors_liste'])` ; sonde retirée en `finally` (`probe_removed`). Conforme à « un cookie de plus fait échouer, puis la sonde est retirée ».
- **Page B-09 affiche la liste sous un texte resté vide.** `Cookies::contenu()` ajoute la table par `the_content` sur la seule page cookies ; `page_texte_vide` vérifie `post_content==''`. La liste n'est pas recopiée : elle vient de `Cookies::liste()`. Conforme sur le fond.
- **Interdits respectés** : aucun bandeau, aucun outil de consentement, aucun script livré (`pas_script`, et le bloc d'amorçage n'enregistre qu'un filtre de contenu) ; C-30 et les lots clos non touchés (`A-VOIR.md`, socle de contrat inchangé) ; la liste ne contient aucune valeur (`aucune_valeur`).

**Interprétation signalée (mineure).** Le brief dit « par un bloc ou un code court ». Hermès a choisi un filtre `the_content` ciblé sur l'ID de la page (`Cookies.php:48,52-54`), pas un bloc ni un shortcode. Fonctionnellement équivalent et plus sûr (rien à recopier, rien à oublier), mais l'éditeur ne peut ni déplacer ni retirer la table depuis l'administration. À confirmer que ce mécanisme convient.

## 2. Exactitude métier (déroulé à la main)

J'ai déroulé `Cookies::inconnus()` et le relevé sur plusieurs cas.

- **Simple lecture (accueil).** Relevé observé = 7 `sbjs_…` (`strict-reading-V2.json`, `browser-final-V2.json`). Tous dans la liste → `inconnus` = `[]`, liste fermée verte. Attendu « aucun cookie » → `zero_cookie_pass` faux → `status:"FAIL"`. Cohérent avec l'écart constaté (voir §Verdict).
- **Durées : relevé vs liste publiée.** J'ai comparé chaque `expires` du reçu navigateur à la durée annoncée :
  - `sbjs_current/_add`, `sbjs_first/_add`, `sbjs_migrations`, `sbjs_udata` : `expires=-1` (session) → liste « Session du navigateur ». Exact.
  - `sbjs_session` : `expires` horodaté → liste « 30 minutes » (recoupé par la doc attribution). Cohérent.
  - `wp_woocommerce_session_[hash]` : `expires` ≈ 2 jours → liste « 2 jours ». Exact.
  - `wordpress_[hash]`, `wordpress_logged_in_[hash]`, `wp_lang`, `wordpress_test_cookie` : `expires=-1` (session, sans « Se souvenir de moi ») ; la « validité serveur 2 jours » vient du code installé (`standard-V2.json` `auth_default_2_days`). Cohérent.
  Rien d'inventé : chaque durée correspond à l'observation ou à une source. Conforme au « seulement ce que tu observes ».
- **Ajout au panier.** Attendu `wp_woocommerce_session_`, `woocommerce_items_in_cart`, `woocommerce_cart_hash` ; tous dans la liste → `inconnus` = `[]`. Conforme.
- **Cas limites d'ancrage (déroulés sur la regex `\A(?:motif)\z` avec modificateur `D`)** :
  - `prefix_sbjs_session`, `sbjs_session_suffix` → hors liste (bon refus).
  - `"sbjs_session\n"` (saut de ligne final) → hors liste : `\z` et `D` empêchent le contournement par `$`. Bien couvert (`CookiesC32Test.php:17`).
  - `sonde_cookie_interdit` → hors liste. Conforme.
  Les motifs PHP (`preg_quote`/`[a-f0-9]{32}`) et Python (`re.fullmatch`) sont équivalents sur ces noms (aucun métacaractère non maîtrisé). Pas de divergence constatée entre les deux contrôleurs.

## 3. Tests

- Suite PHP au vert (REJEU ci-dessus). `CookiesC32Test` : liste à 14, ancrage, refus d'un intrus.
- `c32-runtime.php` : 21 contrôles (liste fermée, page publiée vide, table unique à 15 `<tr>`, chaque ligne rendue, pas de `<script`, texte tiers préservé).
- `c32-browser.py` : 151 contrôles, 50 lignes de relevé, étanchéité C-26 réutilisée, restauration des sessions/paniers et de `user_count`, sondes retirées.
- Les tests vérifient la règle, pas le code : la mutation témoin prouve que le refus est réel ; l'étanchéité est contrôlée à chaque page. Bon.

**Point de vigilance (non bloquant).** `verifier.py:25` **exige** `strict-reading-V2.json` en `FAIL`. C'est voulu : la vérification est verte parce que l'écart est figé comme attendu. Conséquence : l'attendu « aucun cookie en lecture » ne redeviendra pas vert tout seul le jour où l'attribution sera éteinte — il faudra alors reprendre cette assertion. À garder en tête, pas un défaut.

## 4. Sécurité et données

- Aucune valeur de cookie dans le dépôt : reçus limités à `name/expires/httpOnly/secure/sameSite/path` ; `aucune_valeur` vérifie l'absence de valeur. Conforme §3 doctrine et au brief.
- Sonde `c32-observer.php` bornée : n'agit que si `wp_get_environment_type()==='local'` **et** `imagine_demo_site==='imagine-test-demo'`, et seulement sur `$_GET['c32_cookie']` ; mu-plugin téléversé puis retiré en `finally`, `pre_http_request`/`pre_wp_mail` coupés. Pas de fuite hors recette.
- Compte fictif en `@example.org`, mot de passe non journalisé, supprimé en `finally` avec garde anti-compte étranger ; sessions WooCommerce restaurées à l'identique (`sessions_restored`). Données neutres.
- Sorties échappées : `esc_html()`/`esc_html__()` dans `Cookies::contenu()`. Pas de requête SQL côté plugin. Pas de secret.

## 5. Doctrine

- **Standard d'abord** respecté : on observe et on liste le natif WordPress/WooCommerce, on n'ajoute aucun outil. Bien.
- **Convention i18n (mineur).** `Cookies.php:59` et `:65` passent des **variables** à `esc_html__()` (`$heading`, `$row[$key]`). Ces chaînes ne sont pas extractibles par l'outillage de traduction et seront signalées par le linter `WordPress.WP.I18n` ; la traduction est de fait impossible. Les textes sont déjà en français, donc sans effet fonctionnel, mais la fonction de traduction est mal employée (§5). Correction proposée : rendre les en-têtes de colonnes comme chaînes littérales traduites, et ne pas repasser `origine/geste/duree/usage` par `__()` (données, pas interface) — un simple `esc_html()` suffit.
- `README.md` du module présent et complet (ce qu'il fait, recettes, écart). Conforme §5.

## 6. Études

Sans objet au sens strict (lot avec code), mais la partie « standard » est une étude : chaque affirmation cite une page officielle avec adresse et sha256 (`standard-V2.json`), et `c32-standard.py` vérifie la présence des termes dans la page récupérée. Conforme à la grille §6.

## Verdict

**Conforme** — avec une réserve explicite portée par le lot lui-même (ce verdict n'est pas un GO).

Points classés :

- **Bloquant** : aucun.
- **Important** :
  1. **Écart assumé** — l'attendu « aucun cookie en simple lecture » est **rouge** : 7 cookies `sbjs_…` d'attribution d'origine WooCommerce posés par JavaScript (aucun `Set-Cookie` serveur), sur 44 pages. Le brief interdit de les retirer puisqu'ils viennent du natif activé ; Hermès les a donc documentés avec le réglage d'extinction, sans toucher à C-30. Conforme au brief, mais la clôture reste suspendue à l'arbitrage ci-dessous.
- **Mineur** :
  2. Mécanisme d'affichage = filtre `the_content` plutôt que « bloc ou code court » (§1).
  3. Variables passées à `esc_html__()` — i18n non extractible (§5).

### Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

- **Q-T1 — i18n de la table.** Faut-il corriger l'emploi de `esc_html__()` sur variables ?
  Défaut proposé : **oui** — en-têtes en chaînes littérales, cellules de données en `esc_html()` seul. Sans effet visible pour l'utilisateur.
- **Q-T2 — mécanisme d'insertion.** Garder le filtre `the_content` ou passer à un shortcode/bloc ?
  Défaut proposé : **garder le filtre** (rien à recopier, conforme à « sans que personne la recopie »), et le noter dans le README comme choix assumé.

### Pour Imagine (règle métier / juridique → réglage)

- **Q-I1 — consentement et attribution d'origine.** Les sept cookies `sbjs_…` de l'attribution d'origine WooCommerce demandent-ils un consentement, et faut-il à terme éteindre l'attribution (`woocommerce_feature_order_attribution_enabled=no`) ?
  Défaut prudent proposé : **laisser l'attribution activée et le FAIL documenté tel quel** jusqu'à l'avis d'Imagine et de son conseil ; ne rien éteindre ni ajouter de bandeau d'ici là. (Question rangée par le brief lui-même pour Imagine.)

Rien à adresser à Ced (aucune question visuelle ; le point juridique relève d'Imagine).

Codex.md existe mais n'a pas été lu ; fusion non faite, comme demandé.
