# Relecture B-01 — Le squelette du thème (relecteur Claude, indépendant)

Date : 2026-11-23. Lot : B-01. Brief : `briefs/B-01-squelette-du-theme.md`.
Production relue : `wp/themes/imagine/`, `production/B-01/`.
Je n'ai pas ouvert `relectures/B-01/codex.md`. Pas de fusion à ce stade.

Rappel de doctrine : ce verdict n'est pas un GO. Le visuel reste à valider par Ced sur maquettes.

---

## 1. Conformité

Globalement conforme au brief. Tous les gabarits demandés existent et répondent.

- **Point important — échafaudage C-08 non demandé et non déclaré.**
  `wp/themes/imagine/functions.php:34-50` : `imagine_article_body()` ne se limite pas à « afficher le texte complet » (brief, §Ce qu'on veut). La fonction implémente déjà tout un aiguillage paywall : `Imagine\Site\Paywall::managed()`, `::decision()`, `::excerpt()`, quatre blocs (`abonnement`, `connexion`, `regularisation`, `decouverte_epuisee`) et quatre gabarits `wp/themes/imagine/parts/paywall-*.php`. Le brief dit explicitement que c'est **C-08** qui « branchera ce point sur la décision d'accès » et que « dans ce lot, il affiche le texte complet ». C'est donc du « plus » que le brief.
  Aggravant : `production/B-01/notes.md:34-37` décrit le point de branchement comme ne faisant, en B-01, que `the_content()` + formulaire natif B-00. La présence de l'aiguillage Paywall et des quatre gabarits n'y est **pas** signalée. Doctrine §1 : une interprétation doit être écrite dans le rapport.
  Correction proposée : soit retirer l'aiguillage Paywall et les `parts/paywall-*.php` de B-01 pour les porter en C-08, soit, si on les garde comme amorce, le déclarer franchement dans `notes.md` et le faire acter par Ced. À arbitrer.

- **Point mineur — dépendance WooCommerce latente dans un gabarit du thème.**
  `wp/themes/imagine/parts/paywall-regularisation.php:8` appelle `wc_get_page_permalink('myaccount')`. En B-01 ce gabarit est code mort (classe `Paywall` absente), mais si ce bloc était rendu un jour sans WooCommerce chargé, c'est une erreur fatale (fonction indéfinie). Lié au point ci-dessus. Correction : à traiter avec le portage C-08, protéger par `function_exists('wc_get_page_permalink')`.

- **Point mineur — en-tête de thème inexact.**
  `wp/themes/imagine/style.css:5` : `Requires at least: 7.0`. WordPress 7.0 n'existe pas (branche actuelle 6.x). Mettre la version minimale réellement visée.

- **Choix déclaré (conforme).** Le choix « variables CSS dans un seul fichier plutôt que `theme.json` » est fait et justifié en deux lignes (`production/B-01/notes.md:7-10`), comme demandé. `assets/tokens.css` est l'unique dictionnaire ; aucune valeur de style en dur dans les gabarits (vérifié, et verrouillé par test, voir §3).

## 2. Exactitude métier

Cas déroulés à la main sur les preuves HTTP livrées (`production/B-01/http/`), recoupés avec le code.

- **Ordre du kiosque — correct.** `archive-imagine_numero.php` + `functions.php:65-68` trient par méta `imagine_sortie` DESC. Capture `http/kiosque.html` : T4, Hors-série, T3, T2, T1. Le hors-série est bien inclus et classé par sa date de sortie. Conforme à `A-VOIR.md`.
- **Dernier numéro en accueil — correct.** `front-page.php:13` via `imagine_issue_query(1)` → `http/accueil.html` affiche « Numéro fictif 4 ». Conforme.
- **Agenda croissant — correct.** `functions.php:69-72` trie `imagine_evenement` par `imagine_date` ASC. Captures `http/evenement-46.html` (2026-12-10) puis `-47` (2026-12-11). Conforme.
- **Sommaire d'un numéro — correct.** `single-imagine_numero.php:17-21` requête les `post` par méta `imagine_numero_id = ID du numéro`. `http/numero-39.html` (T4) : quatre articles (3 réservés + 1 ouvert). Lien PDF présent via `imagine_pdf_id`. Conforme.
- **Thématique — correct.** `http/thematique-20.html` : cinq articles, tous numéros confondus, sans corps. Conforme à `A-VOIR.md`.
- **404 — vrai 404.** `verification.json` enregistre le statut 404 (pas un 200 déguisé). Conforme.

- **Point mineur — dates affichées en ISO brut, non localisées.**
  `functions.php:110-115` (`imagine_date`) écrit la valeur de méta telle quelle : `http/evenement-47.html` affiche `2026-12-11`. L'attribut `datetime` est valide, mais le texte visible n'est pas « 11 décembre 2026 ». Acceptable pour un squelette ; à confier au designer/format plus tard. Signalé car `A-VOIR.md:14` annonce « 11 décembre 2026 », qui est de la prose, pas la sortie réelle.

- **Point mineur — message d'état vide générique en recherche.**
  Recherche sans résultat : `http/recherche-vide.html` affiche « Aucun contenu pour le moment. » (message générique de `imagine_list`, `functions.php:90`). Pour une recherche, un libellé du type « Aucun résultat pour votre recherche. » serait plus juste. Mineur.

- **Observation (hors scope B-01, donnée B-00).** `http/accueil.html` liste « Hello world! » (article WordPress par défaut) parmi les cinq derniers articles. Ce n'est pas un contenu fictif Imagine. Relève du seed B-00, pas du thème, mais c'est visible par Ced. À nettoyer côté fixtures B-00.

## 3. Tests

Le brief ne prévoit pas de `composer test` (B-01 est un thème, pas une extension PHP à composer). Les tests du lot sont les scripts Python de `wp/tests/demo/`. Je les ai lancés en local.

- **`python wp/tests/demo/test_b01_theme.py` : 3/4 verts chez moi.**
  - `test_b01_shell_contract` : OK.
  - `test_b01_editorial_templates_and_body_seam` : OK.
  - `test_b01_targeted_installation_refuses_other_site` : OK (mocké, aucun accès réseau).
  - `test_b01_html_validator_rejects_structural_regressions` : **n'a pas pu s'exécuter chez moi** — le wheel `html5lib` vendorisé importe `six`, et `bs4` manque dans mon environnement Python. Ce n'est pas un défaut du code. J'ai lu `wp/tests/demo/b01_html.py` : la logique du validateur est saine (h1 unique, langue, repères, lien d'évitement, IDs uniques, `aria-labelledby` résolu, `alt` non vides, hiérarchie des titres, étiquettes de champs). Le journal livré `production/B-01/tests/b01-unit-final.txt` montre 4/4 verts chez Hermès.
- **Qualité des tests.** Les tests vérifient de vraies contraintes, pas une répétition du code : interdiction de valeurs CSS en dur (hex/px/rem) hors variables, un seul `imagine_article_body()` dans `single.php`, absence de `the_content(`/`post_content` dans `single.php`, un seul `<h1>` par gabarit, absence de `.js`. Le test de régression du validateur rejette volontairement cinq corruptions (double h1, saut de titre, `<div>` dans `<p>`, image sans alt, id dupliqué). Bon niveau.
- **Suite runtime/HTTP (500 assertions, `verification.json`).** Je ne l'ai **pas** rejouée : elle frappe le site de démonstration (`192.168.129.32:8085`), et un relecteur n'accède pas à un site (doctrine §3 + `relecteurs/CLAUDE.md`). J'ai contrôlé à la place les corps HTML livrés dans `http/` et recoupé ~8 pages à la main (accueil, kiosque, recherche, numéro, thématique, événement, article réservé, 404) : cohérentes avec les affirmations.
- **Couverture des cas limites.** Correcte pour un squelette : recherche vide, article réservé anonyme, repli `index.php`, 404 réelle, hors-série dans le kiosque.

## 4. Sécurité et données

- **Étanchéité du verrou provisoire — tient.** `functions.php:52-55` : si `post_password_required()`, on sort `get_the_password_form()` et on s'arrête. Capture `http/article-14.html` (article réservé, réponse anonyme) : seul le teaser public + le formulaire natif ; le texte réservé est absent. Vérifié aussi en **recherche** (`http/recherche.html`) : aucun article réservé listé, aucun corps réservé dans les extraits (les extraits « La suite, beaucoup plus longue… » proviennent des articles **ouverts**, pas des réservés). Bon.
- **Échappement.** `esc_html`/`esc_attr`/`esc_url` systématiques ; `wp_kses_post()` sur la liste de termes (`single.php:21`) ; vignettes via `get_the_post_thumbnail`. Pas de sortie non échappée repérée.
- **Aucun secret, aucune donnée réelle.** Données manifestement fictives (« village Imaginaire », couvertures « image de remplacement générée »). Conforme §3.
- **Point mineur — robustesse de la navigation.** `functions.php:120-128` : `imagine_navigation()` indexe le tableau de liens **par URL**. Si deux entrées résolvent la même URL (ex. un `get_post_type_archive_link()` renvoyant `false` → repli `home_url('/')` pour plusieurs CPT), les clés fusionnent et des entrées de menu disparaissent silencieusement. Non déclenché ici (CPT enregistrés par B-00), mais fragile. Correction : indexer par libellé/clé stable, pas par URL.

## 5. Doctrine

- **Standard d'abord — respecté.** Hiérarchie de gabarits WP native, `the_content()`, `pre_get_posts` sur la seule requête principale hors admin (`functions.php:60-74`), `get_search_form()`/`searchform.php`, `get_the_password_form()`, `the_posts_pagination()`. Aucun constructeur de pages, aucune dépendance front tierce, aucun JS. Sources officielles copiées dans `production/B-01/references/`. Conforme §4.
- **Conventions §5 — respectées.** `declare(strict_types=1)`, `namespace Imagine\Theme`, préfixe `imagine_`, textes d'interface en français et traduisibles (`__`, `esc_html_e`). Conforme.
- **Écart de méthode déclaré par Hermès.** `notes.md:54` reconnaît que les tests et l'amorce des fichiers shell ont précédé la consultation des références (« tests d'abord » partiellement respecté, « références avant tout code » non littéralement). Déclaré, non masqué. J'en prends acte ; pas bloquant, mais à verser à `docs/ecarts.md`.
- **Mobilier WP natif en anglais.** Le site de démo semble en locale `en_US` : formulaire mot de passe (« This content is password-protected… », « Password: », « Enter »), préfixe « Protected: » des titres réservés, `aria-label="Posts pagination"`. Les textes propres au thème sont bien en français. Hermès le signale (`notes.md:103`). Recommandation : régler la locale du site B-00 sur `fr_FR` pour que Ced voie un rendu homogène. Mineur, hors scope strict B-01.

## 6. Études (lots sans code)

Sans objet : lot avec code.

---

## Verdict

**Conforme, à corriger** (aucun bloquant). Le squelette fait ce que le brief demande ; les gabarits, la sémantique de base, l'étanchéité du verrou provisoire et le branchement unique du corps d'article sont en place et vérifiés sur les preuves livrées.

Points classés :

**Important**
1. Échafaudage paywall C-08 présent dans `functions.php:34-50` et `parts/paywall-*.php`, au-delà du périmètre B-01 (« affiche le texte complet ») et non déclaré dans `notes.md`. Décider : retirer/reporter en C-08, ou garder comme amorce et le faire acter. (§1)

**Mineur**
2. `wc_get_page_permalink()` non protégé dans `parts/paywall-regularisation.php:8` (fatal potentiel si rendu sans WooCommerce). (§1)
3. `Requires at least: 7.0` erroné dans `style.css:5`. (§1)
4. Navigation indexée par URL → fusion silencieuse d'entrées possible (`functions.php:120-128`). (§4)
5. Dates affichées en ISO brut, non localisées (`functions.php:110-115`). (§2)
6. Message d'état vide générique en recherche (`functions.php:90`). (§2)
7. Locale WP du site de démo en anglais pour le mobilier natif ; régler `fr_FR` côté B-00. (§5)
8. « Hello world! » et données par défaut visibles en accueil ; nettoyer le seed B-00. (§2)

**À verser à `docs/ecarts.md`**
- Écart de méthode déclaré : tests/amorce avant références (`notes.md:54`).

**À arbitrer par Ced** (question fermée)
- Garde-t-on l'amorce paywall C-08 dans le thème dès B-01 (oui/non) ? Si oui, elle doit être déclarée dans `notes.md` et protégée (point 2).

---

### Vérifications effectuées / limites de ma relecture

- Lu : brief, doctrine, grille, les 23 fichiers du thème, `A-VOIR.md`, `notes.md`, et ~8 corps HTML de `http/`.
- Lancé : `test_b01_theme.py` (3/4 verts localement ; le 4e n'a pas pu tourner faute de `bs4`, logique relue à la main, et vert dans le journal livré d'Hermès).
- Non rejoué : la suite runtime/HTTP (accès au site interdit au relecteur) ; contrôlée via les captures livrées.
- Non ouvert : `relectures/B-01/codex.md`. Pas de fusion.
- **Déclaration de conduite :** pour tenter d'exécuter le validateur, j'ai lancé `pip install six` (dépendance pure-Python du wheel `html5lib`), qui s'est installé dans l'environnement Python. Je me suis arrêté là et n'ai **pas** installé `bs4`, conformément à la doctrine (« rien ne s'installe sur le NUC sans l'accord de Ced »). À régulariser si besoin.

`codex.md` existe déjà, mais la consigne est de ne pas le lire ni fusionner à ce stade. Je m'arrête après l'écriture de ce rapport.
