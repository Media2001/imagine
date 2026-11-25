# Relecture B-04 — Page numéro, kiosque, thématique (Claude, relecteur indépendant)

Brief : `briefs/B-04-page-numero.md`. Cahier des charges : §3.3. Code relu :
`wp/themes/imagine/{functions.php, inc/catalogue.php, single-imagine_numero.php,
archive-imagine_numero.php, taxonomy-imagine_thematique.php}` et les contrats appelés
(`imagine-site/Paywall.php`, `AchatsNumeros.php`, `PdfNumero.php`,
`imagine-pilotage/src/Acces/Motif.php`).

**Rejeu de la suite PHP autorisée** (conteneur jetable, hors réseau, dépôt en lecture seule) :

```
REJEU : 1030 tests, 34124 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Je n'ai pas lu `relectures/B-04/codex.md`. Pas de fusion à ce stade.

---

## 1. Conformité

- **Une seule fonction de statut, utilisée par les trois gabarits** : `imagine_access_status()`
  (`inc/catalogue.php:8`). Appelée par `single-imagine_numero.php:19`, par
  `archive-imagine_numero.php:17`, et par `imagine_catalogue_articles()` (`inc/catalogue.php:75`)
  qu'utilise `taxonomy-imagine_thematique.php:11`. Conforme à la règle du brief.
- **Le statut vient de la décision, le thème ne recalcule rien** : la fonction ne reçoit que
  le tableau `['complet','motif','bloc']` de `Paywall::decision()` / `decisionPdf()` et le
  traduit. Aucun droit recalculé. Conforme.
- **Quatre libellés exacts** du brief (`Libre`, `Découverte`, `Réservé`, `Ouvert pour vous`),
  tous traduisibles (`inc/catalogue.php:18-23`). Mapping cohérent avec l'enum `Motif`
  (`contenu_ouvert`→libre ; `decouverte_duree`/`decouverte_articles`→découverte ;
  tout autre motif complet→ouvert ; non-complet→réservé).
- **Page numéro** (`single-imagine_numero.php`) : présentation = extrait éditorial public
  (`:43`, pas le corps réservé) ; article libre mis en avant (`:44-49`) ; sommaire détaillé
  avec statut par article (`:50-53`) ; emplacement nommé « Sommaire audio » sans lecteur ni
  fichier (`:54-57`) ; bouton d'achat conditionnel (`:58-60`) ; PDF conditionnel (`:61-63`).
  Conforme au §3.3 et au brief.
- **Kiosque** (`archive-imagine_numero.php`) : liste couverture + titre + date, ordre
  éditorial décroissant via `imagine_archive_order()` (`functions.php:95-98`), pagination
  native (`:30`). Conforme.
- **Page thématique** (`taxonomy-imagine_thematique.php`) : articles tous numéros confondus
  (requête principale du terme), même statut visible, pagination native. Conforme.
- **Interprétation signalée (à confirmer)** : « couvert » — qui masque le bouton d'achat et
  autorise le PDF — est défini comme le **droit PDF complet** (`decisionPdf`,
  `single-imagine_numero.php:25-27`). Conséquence voulue et testée : `a-carte` voit le bouton
  d'achat sur le n°11 (droits article, mais PDF fermé). C'est une lecture de « qui a déjà le
  numéro » ; elle respecte l'intention du brief (l'achat du numéro entier reste proposé à qui
  n'a que l'accès aux articles), mais c'est un choix à acter.
- **Ajout non demandé** : le kiosque affiche en plus un statut d'accès par numéro
  (`archive-imagine_numero.php:24`), que ni le brief ni le §3.3 ne demandent pour l'index.
  Voir §1 des points mineurs.

## 2. Exactitude métier — cas déroulés à la main

Déroulé sur un même numéro vu par trois visiteurs (recoupé avec `A-VOIR.md`) :

- **Anonyme, n°11** : article non réservé → motif `contenu_ouvert`, complet → `libre`/« Libre » ;
  article réservé → anonyme, non complet → `reserve`/« Réservé ». `decisionPdf` non complet
  → `$covered=false` → bouton d'achat affiché (un produit B04 publié existe), **aucun PDF ni
  test d'existence** (`single-imagine_numero.php:30-37` : la route PDF n'est touchée que si
  `$covered`). Concorde.
- **p-numero, n°11 (acheté)** : articles → motif `numero_achete`, complet → `ouvert`/« Ouvert
  pour vous ». `decisionPdf` complet → `$covered=true` → **pas** de bouton d'achat, lien PDF
  présent. Concorde avec l'A-VOIR.
- **a-carte, n°11** : articles ouverts (complet) → « Ouvert pour vous » ; `decisionPdf` fermé
  (`pdf_anterieur_ferme_par_reglage`) → bouton d'achat présent, pas de PDF. Concorde.
- **Cas limite — anonyme, n°39** : aucun produit C14 publié associé → `imagine_issue_product()`
  renvoie `''` (`inc/catalogue.php:38-45`) → **aucun bouton d'achat inventé**, même si non
  couvert. Bon comportement (le thème n'invente pas de parcours d'achat).

Le mapping de statut et les deux conditions d'affichage (achat / PDF) donnent, à la lecture,
exactement les résultats décrits. Réserve importante : ces cas sont vérifiés **par lecture et
par les scripts HTTP de démo**, pas par un test rejouable dans le conteneur (voir §3).

## 3. Tests

- **Rejeu autorisé vert** : 1030 tests / 34124 assertions, 0 échec. Mais ces tests couvrent
  les quatre plugins (`imagine-connecteur`, `imagine-non-regression`, `imagine-pilotage`,
  `imagine-site`). **Zéro** test du code B-04.
- **Le thème n'a aucun test rejouable** : la découverte T01 émet
  `T01 WARNING : themes/imagine ; custom package without PHPUnit tests`. Il n'existe ni
  `composer.json` ni `phpunit.xml` dans `wp/themes/imagine/`. Toute la preuve du lot vit dans
  les scripts `wp/tests/demo/b04-*.py` qui tapent le staging `192.168.129.32:8085` — non
  rejouables dans le conteneur autorisé, et que je ne peux ni ne dois lancer (réseau, staging,
  dépôt en lecture seule).
- **Conséquence** : je ne peux **pas confirmer indépendamment** l'étanchéité ni le mapping par
  un rejeu. Le brief demandait pourtant « la fonction de statut testée seule si c'est simple »,
  et `imagine_access_status()` est pure, sans WordPress sauf `__()` — triviale à couvrir hors
  ligne. La doctrine §4 pose « un lot sans tests n'est pas PRET » et « logique testable sans
  base ni WordPress ». → **point important ci-dessous.**
- **Nombre de requêtes** (demandé par le brief) : divulgué dans `verification-finale.json` —
  numéro de 20 articles : anonyme 93, a-carte 183, p-numero 182 (requêtes pleine page). C'est
  élevé pour un connecté ; cause en amont (droits visiteur recalculés par article dans C08),
  pas dans le thème. Voir point mineur.

## 4. Sécurité et données

- **Pas de fuite du texte réservé** : la page numéro ne rend jamais le corps d'un article ;
  le sommaire n'imprime que titre + extrait. Les extraits proviennent de `post_excerpt`, et la
  requête personnalisée du gabarit passe par le filtre `the_posts` → `Paywall::sanitizePosts()`
  qui remplace l'extrait réservé par l'extrait public borné (`Paywall.php:263-277`). Pas de
  corps réservé servi. Conforme.
- **Pas de fuite du PDF** : aucune inspection d'existence ni exposition de route avant la
  décision serveur (`single-imagine_numero.php:29-37`). Pour l'anonyme et le non-ayant droit :
  pas de lien, pas d'indice. Conforme.
- **Échappement** : sorties passées par `esc_html`/`esc_url`/`esc_attr` ;
  `data-imagine-access` échappé. Rien à signaler.
- **Page thématique** : extraits assainis par le même filtre `the_posts` ; pas de PDF. Conforme.

## 5. Doctrine

- **Standard d'abord** : pagination, archive, taxonomie, requêtes natives WordPress ;
  `woocommerce` supporté sans wrappers redondants (`functions.php:19-22`). Bon.
- **Conventions §5** : `declare(strict_types=1)`, espace `Imagine\Theme`, préfixe `imagine_`,
  textes traduits. Conforme.
- **Point de doctrine — échafaudage de démo codé en dur dans le thème livré** :
  `inc/catalogue.php:51-63` enregistre **inconditionnellement** un filtre
  `woocommerce_coming_soon_exclude` avec l'IP `http://192.168.129.32:8085` et l'option
  `imagine-test-demo` en dur. Inerte en production (`wp_get_environment_type() === 'local'`),
  mais c'est de la logique propre à la démo dans un fichier de thème destiné à la production.
  À sortir du thème (mu-plugin ou `wp/outils/demo/`). Voir point important.

## 6. Études

Sans objet (lot de code).

---

## Verdict : **À corriger**

Le code lu est, sur le fond, conforme au brief et au §3.3 ; je n'ai trouvé ni fuite ni erreur
de mapping. Mais le lot ne peut être dit conforme tant que sa preuve n'est pas rejouable et que
de l'échafaudage de démo reste dans le thème. Rappel : ce verdict n'est pas un GO.

**Important**

1. **Aucun test rejouable pour tout le lot B-04.** Le thème est signalé « custom package
   without PHPUnit tests » ; les 1030 tests verts ne couvrent pas B-04. Toute la preuve est
   dans les scripts HTTP de démo contre le staging, non rejouables en conteneur. → Ajouter au
   minimum un paquet PHPUnit rejouable couvrant `imagine_access_status()` seule (fonction pure,
   les quatre codes/libellés et le mapping des motifs), comme le demandent le brief et la
   doctrine §4. Idéalement, couvrir aussi les deux conditions achat/PDF.

2. **Exemption de démo codée en dur dans le thème** (`inc/catalogue.php:51-63`) : IP et nom de
   site en dur, filtre enregistré sans condition. → Déplacer hors du thème livré (mu-plugin ou
   `wp/outils/demo/`), de sorte que le thème de production ne contienne aucune cible de staging.

**Mineur**

3. **Kiosque : statut d'accès non demandé** (`archive-imagine_numero.php:24`). Le §3.3 et le
   brief ne demandent pour l'index que couverture, titre et date. De plus, pour l'anonyme,
   chaque numéro affiche « Réservé » (décision PDF) même s'il contient des articles libres —
   potentiellement trompeur. → Question visuelle/métier ci-dessous.

4. **Exclusion silencieuse d'un numéro sans date** : l'ordre par
   `meta_key=imagine_sortie, orderby=meta_value` (`functions.php:95-98`,
   `archive-imagine_numero.php` via requête principale) fait une jointure interne qui **exclut**
   tout numéro publié sans `imagine_sortie`. À confirmer que B-01 garantit cette métadonnée sur
   tout numéro publié ; sinon un numéro disparaîtrait du kiosque sans message.

5. **Redondance** : sur la page numéro, `imagine_catalogue_articles()` imprime « Dans le
   numéro : <ce numéro> » pour chaque article (`inc/catalogue.php:96-100`), alors qu'on est
   déjà sur ce numéro. Bruit inutile dans le sommaire.

6. **Coût requêtes élevé pour un connecté** (183/182 pour 20 articles), divulgué comme demandé.
   Cause en amont : `Paywall::rights()` est rejoué par article (le cache de décision est par
   article, pas par visiteur). Le thème n'y peut rien. → Observation cross-lot pour C08 et pour
   les seuils §5 (Lighthouse mobile) : envisager un mémo des droits visiteur par requête.

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après)

- **Points 1 et 2** (tests rejouables, sortie de l'échafaudage de démo) : défaut proposé =
  les appliquer tels quels. Ce sont des questions techniques, pas métier.

## Pour Ced (visuel / touchant au réel)

- **Faut-il un statut d'accès sur le kiosque ?** (point mineur 3). Défaut prudent proposé :
  **non** — s'en tenir à couverture / titre / date comme le demande le §3.3, car l'étiquette
  « Réservé » sur un numéro contenant des articles libres peut induire en erreur. Question
  fermée : garde-t-on le statut sur l'index (oui/non) ?
