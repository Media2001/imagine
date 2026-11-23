# B-01 — Notes de livraison

## Résultat et périmètre

Squelette du thème **Imagine**, installé et actif sur **imagine-test-demo seulement**. Aucun habillage de marque, aucune maquette reconstituée, aucune nouvelle règle d’accès ni fonction de vente. Le modèle de données est celui, provisoire et fictif, de B-00. Le plugin `imagine-site` est inchangé.

### Choix du fichier de variables (deux lignes)

Toutes les valeurs visuelles propres au thème sont centralisées dans `wp/themes/imagine/assets/tokens.css` ; `style.css` ne contient que règles structurelles et références à ces variables.
Ce thème classique n’a pas besoin d’interface de styles globale `theme.json` : un seul dictionnaire CSS permettra d’appliquer le futur système du designer sans modifier les gabarits.

## Gabarits et demandes au designer

| Gabarit / fichier | Données et structure réalisées | À fournir par le designer, sans arbitrage métier |
|---|---|---|
| Accueil — `front-page.php` | Dernier numéro par `imagine_sortie`, cinq derniers articles, entrées kiosque/thématiques/agenda. | Composition des blocs, place de la couverture, hiérarchie et composants d’entrée. |
| Kiosque — `archive-imagine_numero.php` | Tous les numéros, hors-série inclus, tri décroissant de sortie ; couverture, titre, date. | Carte de numéro, taille et recadrage des couvertures, rythme de liste. |
| Numéro — `single-imagine_numero.php` | Couverture native, extrait de présentation, sommaire calculé via `imagine_numero_id`, PDF via `imagine_pdf_id`. | Composition de la fiche et du sommaire ; présentation des liens PDF. |
| Article — `single.php` | Titre, chapô natif, auteur, numéro, thématiques, corps sémantique. | Typographie de lecture, hiérarchie du chapô et des métadonnées ; styles des contenus éditoriaux. |
| Thématique — `taxonomy-imagine_thematique.php` | Requête WordPress de la thématique, titres/liens/extraits et pagination native. | En-tête de rubrique et cartes d’article, états de pagination. |
| Agenda — `archive-imagine_evenement.php` | Événements triés par `imagine_date` croissante. | Structure visuelle des dates et des éléments de liste. |
| Événement — `single-imagine_evenement.php` | Titre, date, texte, retour à l’agenda. | Composition de fiche et présentation des informations pratiques à venir. |
| Partenaires — `archive-imagine_partenaire.php` | Liste des partenaires et leurs extraits. | Présentation de la liste et éventuels emplacements de logos fournis. |
| Partenaire — `single-imagine_partenaire.php` | Titre et contenu éditorial, retour à la liste. | Composition de fiche et traitement des médias fournis. |
| Page simple — `page.php` | Titre et contenu WordPress ; tableau du calendrier B-00 conservé. | Styles éditoriaux, tableaux, listes, images et légendes. |
| Recherche — `search.php`, `searchform.php` | Formulaire natif GET, résultats sans corps des articles, pagination et état vide. | Formulaire, résultats, état vide et pagination. |
| 404 — `404.php` | Message, lien d’accueil, recherche ; vrai statut 404. | Composition et éventuelle illustration fournie. |
| En-tête/pied — `header.php`, `footer.php` | Repères, navigation, évitement, compte, abonnement, mention du squelette. | Système de navigation bureau/mobile, identité, tailles, espacements, états focus. |
| Repli — `index.php` | Liste minimale de titres/liens et pagination. | Réutiliser le composant de liste validé, pas de maquette supplémentaire nécessaire. |

Pour l’ensemble : palettes, typographies et leurs licences, échelle d’espacement, largeur de lecture, tailles des titres, états interactifs, points de rupture. Rien de cela n’a été choisi au nom d’Imagine. Les valeurs temporaires noir/blanc, police système et une colonne sont strictement celles nécessaires au squelette demandé.

## Point de branchement C-08

`Imagine\Theme\imagine_article_body(): void`, dans `wp/themes/imagine/functions.php`, est le seul point appelé par `single.php` pour sortir le corps d’un article (`data-imagine-body="article"`).

Dans B-01, le corps complet est rendu par la fonction native `the_content()` pour un article ouvert ou après autorisation native par mot de passe. Pour les articles réservés fictifs, le verrou provisoire B-00 n’est **pas** désactivé : un anonyme reçoit le formulaire natif, jamais le texte réservé. La recette teste les 20 sorties anonymes et les 15 sorties natives autorisées, sans exporter les mots de passe. C-08 remplacera la décision à ce point ; ses obligations REST/flux/oEmbed ne sont pas revendiquées par B-01.

La fiche numéro ne réutilise pas le contenu HTML préassemblé de B-00 : couverture, sommaire et PDF sont lus dans les champs et relations, pour ne pas dupliquer la mise en page ni le corps d’un article. Le PDF reste factice et public, comme dans B-00 ; aucun nouveau droit n’est accordé.

## Références officielles et standard d’abord

Copies de consultation dans `references/`, URL et dates des cinq premières dans `references/sources.json` :

1. https://developer.wordpress.org/themes/classic-themes/basics/template-hierarchy/ — hiérarchie native de thème classique, CPT et taxonomie.
2. https://developer.wordpress.org/reference/functions/the_content/ — sortie et filtres natifs de contenu.
3. https://developer.wordpress.org/reference/hooks/pre_get_posts/ — modification de la seule requête principale d’archive, hors administration.
4. https://developer.wordpress.org/reference/functions/wp_enqueue_style/ — chargement natif des deux feuilles CSS et version par date du fichier.
5. https://developer.wordpress.org/reference/functions/get_search_form/ — formulaire natif surchargeable par le thème.
6. https://developer.wordpress.org/reference/functions/get_the_password_form/ — formulaire natif pour préserver la protection provisoire sans le retraiter comme du texte.

Le thème utilise ces mécanismes WordPress plutôt qu’un constructeur, un moteur de gabarit, une extension ou une bibliothèque front supplémentaire. Il n’appelle aucune API WooCommerce ; les extensions commerciales déjà présentes ne sont pas des dépendances du thème.

**Écart de méthode déclaré :** les tests puis l’amorce des fichiers du shell ont été écrits avant la consultation des références officielles. Les références ont été consultées avant les gabarits éditoriaux et le correctif ; la chronologie initiale ne satisfait donc pas littéralement « références avant tout code ». Aucun historique n’a été réécrit pour masquer cet écart. Les trois étapes shell / gabarits / branchement disposent chacune de leur échec rouge puis de leur succès vert enregistrés.

## Installation rejouable, sans reprise B-00

Depuis la racine du dépôt :

```text
python wp/outils/demo/construire.py --theme-only
python wp/tests/demo/test_b01_theme.py
python wp/tests/demo/test_b00_construction.py
python wp/tests/demo/b01-verifier.py
```

La première commande réutilise le script et le transport B-00 ; elle exige un site déjà démarré, l’identifiant fixe, l’environnement `local` et le marqueur fictif B-00. Elle ne crée aucun site, n’installe aucune extension et ne relance pas le seed. Elle copie uniquement les fichiers du thème, parse les 17 fichiers PHP, active Imagine, puis relit le thème actif et les 19 empreintes de fichiers ; le manifeste B-00 est comparé avant/après.

Le branchement thème de la construction complète B-00 est conservé mais placé après son seed pour que le marqueur fictif existe aussi lors d’une reconstruction neuve. **La construction complète B-00 n’a pas été relancée dans ce lot.** Seule son option ciblée et ses quatre tests Python existants ont été exercés. `b00_remote.py`, les fixtures, le seed, le garde hors-ligne et le plugin `imagine-site` sont inchangés ; `scope-integrity.json` compare leurs empreintes à la preuve finale B-00.

Le validateur charge les deux wheels figés présents dans `validation/` (html5lib 1.1 et webencodings 0.5.1, sources et SHA-256 consignés). BeautifulSoup4 et six étaient déjà disponibles dans l’environnement Python ; aucune installation système, ni sur le NUC, n’a été faite.

## Recette et preuves

- **4 tests B-01 / 4 réussis / 0 échec**, dont un test qui rejette volontairement cinq corruptions HTML/sémantiques : `tests/b01-unit-final.txt`.
- **4 tests Python B-00 existants / 4 réussis / 0 échec** : `tests/b00-non-regression.txt`.
- **500 assertions runtime/HTTP / 500 réussies / 0 échec**, dont **45 contrôles runtime inclus**, sur **41 pages HTML et 7 ressources** : `verification.json`, `runtime.json`, `http/`.
- Les 41 documents complets passent le parseur HTML5 local et les contrôles : h1 unique, titres sans saut, repères, langue, évitement, identifiants uniques, références ARIA, images éditoriales avec alt et champs étiquetés. C’est une validation structurelle ciblée, **pas une certification W3C exhaustive ni un audit WCAG complet**.
- **19 captures réelles** : **15 bureau**, **4 à 390 px** ; `browser.json` et `captures/`. H1 unique, mention présente, fond blanc, texte noir et aucune largeur de page débordante mesurés sur les captures.
- **4 contrôles navigateur réussis** dans `browser-interactions.json` : évitement par Tab/Entrée, focus sur main, corps ouvert complet, recherche native GET. Le premier relevé de recherche était prématuré par rapport à la navigation ; l’essai initial est conservé dans `tests/05-browser-first-attempt.json`. Pas d’audit exhaustif des consoles ni de tous les lecteurs d’écran.

### Défaut réel trouvé et corrigé

La première recette réelle avait **15 échecs structurels**, tous sur les articles protégés : passer le formulaire HTML natif dans `the_content`/`wpautop` ajoutait une fermeture `p` orpheline après le champ caché. Le couple sortie native brute / sortie filtrée est conservé dans `tests/04-native-form-diagnostic.json`, avec la réponse et le rapport rouges.

Correctif limité à la fonction de sortie du thème : si `post_password_required()`, afficher directement `get_the_password_form()` ; sinon `the_content()`. Le filtre B-00 et le plugin n’ont pas changé. La recette finale est entièrement verte ; aucune erreur n’a été ignorée par le validateur.

## Qualification des critères et limites

| Critère B-01 | Qualification |
|---|---|
| Ensemble des gabarits demandés | Réalisé ; chaque gabarit demandé a une adresse dans `A-VOIR.md` et une réponse testée. |
| Neutre, une colonne, noir/blanc, pas de police chargée | Réalisé pour le thème ; les couvertures sont les contenus factices B-00 inchangés. |
| Variables visuelles dans un seul fichier | Réalisé : `assets/tokens.css`. Pas de valeur de style dans les gabarits. |
| Sémantique et accessibilité de base | Contrôles automatisés verts ; évitement clavier et lecture mobile exercés. L’audit WCAG complet reste hors de cette preuve. |
| Corps d’article complet par un point unique | Réalisé pour les articles ouverts/autorisés ; protection native B-00 volontairement conservée pour un anonyme. |
| Aucun constructeur/dépendance tierce/JS de thème | Réalisé. Les ressources de WordPress/WooCommerce déjà installés ne sont pas supprimées ni attribuées au thème. |
| Navigation, compte, abonnement | Réalisé comme liens d’entrée ; compte via connexion native et abonnement vers un emplacement explicite, sans tunnel inventé. |
| Activation via B-00 | Réalisée et relue, option `--theme-only` ; aucune reconstruction du lot B-00. |
| HTTP et HTML sans erreur de structure | 41 réponses HTML contrôlées ; toutes sans erreur structurelle finale ; 404 vérifiée en 404. |
| A-VOIR, notes, preuves, PRET | Présents dans ce dossier, sous réserve de la relecture visuelle de Ced. |

Pas de blocage technique restant. Les libellés natifs du verrou provisoire peuvent rester en anglais selon la langue WordPress du site B-00 ; les textes ajoutés par le thème sont français et traduisibles. Pas de mode lecture, d’espace compte, de tunnel d’abonnement, de paywall C-08, de nouvelle règle SEO, de mesure Lighthouse ni de performance fine revendiqués.

Aucun Git, aucun verrou modifié, aucun rapport global écrit, aucune écriture de voie 1. Pas de modification d’une bibliothèque close, d’un plugin tiers ou d’un autre site. Les états PRET et le résultat technique ne valent pas validation du futur design par Ced.
