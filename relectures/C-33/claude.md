# Relecture C-33 — Ce que le site montre de ses comptes (Claude, indépendant)

Lot : fermeture des voies natives par lesquelles un visiteur anonyme obtient un identifiant, un nom ou un numéro de compte. Brief `briefs/C-33-ce-que-le-site-montre-de-ses-comptes.md`, §4.4 et §3.3 du cahier des charges.

Code lu : `wp/plugins/imagine-site/ComptesPublics.php`, `ComptesPublicsRegles.php`, câblage `imagine-site.php:219-222`, test `tests/ComptesPublicsC33Test.php`, sonde `wp/tests/demo/c33-observer.php`, recette `wp/outils/demo/c33-browser.py` + `c33-runtime.php`, section README. Preuves de `production/C-33/`. **Je n'ai pas ouvert `codex.md`.**

## 1. Conformité

- Les cinq voies du brief sont traitées par cinq points d'accroche natifs, sans règle de serveur ni réécriture d'adresse (règle du brief respectée) :
  - archive d'auteur → `template_redirect` priorité 0 : `set_404()` + `remove_action('template_redirect','redirect_canonical')` (`ComptesPublics.php:20-31`) ;
  - liste/numéro REST → `rest_pre_dispatch` → `WP_Error` 404 sur `/wp/v2/users(/...)` (`:33-39`) ;
  - plan du site → `wp_sitemaps_add_provider` retire le fournisseur `users` (`:41-44`) ;
  - flux RSS2/Atom → `the_author` (nom) et `get_the_author_user_url` (adresse) (`:51-67`) ;
  - oEmbed → `oembed_response_data` remplace `author_name`, retire `author_url` (`:69-77`).
- Toutes les fermetures sont gardées par `!is_user_logged_in()` : **rien ne change pour un connecté**. La recette vérifie administrateur **et** éditeur sur le sélecteur d'auteur REST et l'édition d'article (`c33-browser.py:85-91`) — conforme au « besoin de l'éditeur ».
- « Le standard d'abord » : cinq lignes avec adresses officielles `developer.wordpress.org` dans le README (section C-33). Conforme à la demande.
- Observation du sitemap demandée par le brief : types listés = post, page, product, imagine_numero, imagine_evenement, imagine_partenaire. **J'ai vérifié indépendamment** que les types « message de visiteur » et pièces privées sont bien hors sitemap : `Contact.php:35`, `Sujet.php:35`, `Agenda.php:32`, `PointsVente.php:22` sont tous `public=false, publicly_queryable=false, exclude_from_search=true, show_in_rest=false`. L'affirmation du livrable est exacte.
- Interprétations signalées par Hermès (A-VOIR / README) : périmètre **anonyme seulement**, et l'identifiant numérique d'auteur porté par les objets REST `posts` laissé **hors périmètre**. Ces deux choix sont déclarés, conforme à la doctrine §1.

## 2. Exactitude métier — cas déroulés à la main

Déroulé indépendant, puis comparé aux réponses brutes de `production/C-33/` :

1. **Anonyme `?author=<id>`** — `auteur()` : `is_user_logged_in()` faux, `is_author()` vrai → `set_404()`, et `redirect_canonical` (priorité 10) retiré **avant** son exécution par un hook en priorité 0. Attendu : 404, aucune 301 vers `/author/slug/`. Observé : `browser-final-V2-archive-numero.txt` = `status 404`, `content-type text/html`, **pas d'en-tête `location`**. Contre-épreuve : `mutation-author.txt` (filtre retiré) = `301 → /author/fictif-c33-…/`, qui dévoilerait le login. La fermeture est bien ce qui bloque. ✔
2. **Anonyme `/wp/v2/users/<id>`** — `rest()` : `ComptesPublicsRegles::utilisateurs()` (`~\A/wp/v2/users(?:/|\z)~i`) renvoie vrai → `WP_Error('rest_no_route', …404)`. Observé : `rest-detail.txt` = 404 `rest_no_route`, aucun nom. Contre-épreuve : `mutation-rest.txt` = 200 avec `name`, `slug`, `url /author/…` du compte. ✔
3. **Cas limite — signature de flux contenant `]]>`** — `auteurFlux()` protège la borne CDATA en RSS2 (`]]]]><![CDATA[>`) et échappe en XML pour Atom. Vérifié par `c33-runtime.php:23-24` (`rss2_cdata_protegee`, `atom_xml_echappe`). Atom réel : `<author><name>SIGNATURE_FICTIVE_C33</name></author>` sans `<uri>`. ✔
4. **Cas limite — article sans signature B-16** — `ComptesPublicsRegles::signature()` retombe sur le nom du site, jamais sur le compte technique. Observé : `oembed-repli.txt` / `rss2-repli.txt` portent le nom du site. Et jamais le nom du compte de saisie. ✔

Une mutation témoin par voie fermée est présente (6 mutations sur 5 voies : index **et** détail du sitemap). Contrôle de présence de la voie avant contrôle d'absence (`temoin_publie`, `*_voie_presente`). Administrateur/éditeur listent toujours le témoin. Conforme à la « Preuve » du brief.

## 3. Tests

Rejoué, commande autorisée, conteneur jetable sans réseau, dépôt en lecture seule :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

> `REJEU : 1229 tests, 36926 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Compléments du journal : `PAQUETS : 13 vérifiés, 0 échecs` ; `OUTILS : 23 outils, 852 contrôles, 0 échecs` ; `TOOL a33 ; 23 controls ; 0 failures`. `ComptesPublicsC33Test` est présent dans la suite. Le `A-33 VERIFIER_TIMEOUT` mentionné dans A-VOIR (banc antérieur) **ne se reproduit pas** sur ce rejeu : `packets.failures=[]`.

Qualité des tests : `ComptesPublicsC33Test` couvre vraiment les deux règles pures — frontières du préfixe (`/wp/v2/users-extra`, `/autre/wp/v2/users` → faux) et repli de signature (vide, `null`, `[]`, `false` → site). Elles ne répètent pas le code. L'étanchéité des accroches WordPress (priorités, garde `is_feed`, CDATA) est, elle, prouvée par l'intégration (`c33-runtime.php`, 14 contrôles ; browser, 53 contrôles), pas par PHPUnit — acceptable vu la preuve proportionnée demandée. Voir point mineur M2.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle. Comptes/articles témoins en `@example.org`, noms manifestement fictifs, supprimés en fin de recette (`c33-browser.py:97-99`). Sonde (`c33-observer.php`) bornée à l'environnement `local` + option `imagine-test-demo`, coupe réseau et mail, retirée après recette.
- Paywall / étanchéité : chaque voie anonyme contrôlée dans le corps **et** les en-têtes ; `rest-liste/detail/alias/casse` identiques (même sha256) = 404 sans fuite ; `set-cookie` absent des réponses brutes (`verifier.py:24`). L'oEmbed et les flux ne portent plus nom ni adresse de compte.
- Échappement : `the_author` n'étant pas ré-échappé par le cœur en sortie de flux, la méthode échappe elle-même (CDATA RSS2, `esc_html` Atom). Correct.
- Droits : la bascule est strictement « connecté vs anonyme ». Voir question Q1 ci-dessous.

## 5. Doctrine

- Standard d'abord respecté : cinq accroches natives documentées, aucun sur-mesure refaisant WordPress. Aucun code d'extension tierce modifié, aucun gabarit B-16/C-26 touché (cablage additif `imagine-site.php:219-222`).
- Conventions §5 : `declare(strict_types=1)`, espace de noms `Imagine\Site`, textes passés par `__()`, README de section présent. Conforme.
- Rejouable / preuve versionnée : recettes et vérifieur dans le dépôt, reçus hachés (`reception-V2.json`). Conforme.

## Verdict : **Conforme** — (rappel : un verdict n'est pas un GO)

Le lot fait ce que le brief demande, ni moins ni plus ; les cinq voies anonymes sont fermées et prouvées, les connectés préservés, les tests au vert. Points classés :

**Bloquant** : aucun.

**Important**
- **I1 — Portée « anonyme » vs base d'abonnés.** La bascule repose sur `is_user_logged_in()` (`ComptesPublics.php:22,35,43,53,66,71`). Un compte connecté **sans** droit de lister les utilisateurs (un abonné) retrouve le comportement natif : `/wp/v2/users` en contexte `view` renvoie les auteurs ayant publié, l'archive d'auteur répond, le flux porte… (pour les voies non-anonymes). Le brief restreint explicitement à « un visiteur anonyme » et ne préserve nommément que « un compte connecté **qui a le droit** de lister les utilisateurs » : le cas de l'abonné connecté est un **silence** du cahier des charges. Comme le site « sera la seule base d'abonnés d'Imagine », l'énumération des comptes-auteurs par un abonné malveillant mérite un arbitrage. Touche un droit d'accès → question posée (Q1), pas corrigée.

**Mineur**
- **M1 — Identifiant d'auteur sur les objets REST `posts`.** `/wp/v2/posts` continue d'exposer `author` (entier). Hermès l'a **signalé et mis hors périmètre** ; comme `/wp/v2/users/<id>` est fermé, l'entier n'est pas résoluble en nom par un anonyme. Je confirme : hors périmètre défendable, mais à garder en tête si Imagine veut masquer aussi les numéros.
- **M2 — Couverture PHPUnit des accroches.** Les hooks eux-mêmes (priorité 0 d'`auteur`, garde `is_feed`, retrait de `redirect_canonical`) ne sont vérifiés que par l'intégration. Un test léger asserant l'enregistrement et les priorités rendrait la régression détectable sans conteneur. Non bloquant.

### Décisions techniques, défaut proposé
Aucune. Les choix techniques (accroches, priorités, protection CDATA) sont corrects et prouvés.

### Pour Imagine (question métier)
- **Q1.** Faut-il étendre la fermeture des voies de comptes aux **comptes connectés sans droit de lister les utilisateurs** (abonnés), et pas seulement aux visiteurs anonymes ?
  *Défaut prudent proposé (dans le doute sur un droit d'accès, fermé) :* traiter l'abonné connecté comme l'anonyme — ne révéler les comptes que via les API d'édition réservées à `list_users`/`edit_posts`. À confirmer par Imagine ; en attendant, la version livrée reste conforme au brief tel qu'écrit.

### À arbitrer par Ced (visuel ou réel)
Aucune question visuelle ou touchant au réel dans ce lot.

---
`codex.md` non lu à ce stade. Fusion non faite (consigne). Prochaine étape conditionnée à l'existence de `relectures/C-33/codex.md`.
