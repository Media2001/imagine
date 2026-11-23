# B-01 — Notes de livraison corrigée

## État actuel et historique

Démonstration **imagine-test-demo seulement**, WordPress **7.0.9**, locale **fr_FR**, thème Imagine actif. `Requires at least: 7.0` était déjà correct pour cette pile et est conservé, avec assertion runtime ; la remarque de relecture « WordPress 7 inexistant » ne correspond pas au banc installé.

Le seul jeu de preuves actuel est `verification.json`, `runtime.json`, `installation.json`, `browser.json`, `captures/` et `http/`, relié par `b01-final-verification.json`. L'ancienne livraison et son ancien PRET sont archivés dans `historique/pre-C08-livraison-initiale/` : ils décrivent l'état **avant raccord C08**, pas le site présent.

Le raccord C08 dans `imagine_article_body()` et les quatre `parts/paywall-*.php` sont conservés octet pour octet. B01 vérifie le point unique de sortie et le rendu anonyme actuel, **pas la conformité du paywall ni le filtrage du corps dans la recherche**. L'arbitrage C08 du 23 novembre à 17 h 10 reste à traiter par ce lot.

## Variables visuelles — deux lignes

Toutes les valeurs visuelles propres au thème sont centralisées dans `assets/tokens.css` ; `style.css` contient seulement la structure et les références aux variables.
Un thème classique sans interface de styles globale n'a pas besoin de `theme.json` : ce dictionnaire unique accueillera les tokens fournis par le designer.

## Traçabilité au cahier et demandes au designer

Le tableau qualifie la **part réalisée dans B01**, pas l'ensemble du cahier. Le modèle de contenu B00 reste provisoire ; les fixtures sont fictives.

| Gabarit / comportement | Source métier | Réalisé / provisoire / reporté | Besoin du designer |
|---|---|---|---|
| Accueil `front-page.php` | §3.1, §3.2 ; brief B01 | Dernier numéro, cinq derniers articles ID+ordre exacts, entrées thématiques/agenda. Aucun filtre éditorial ajouté. Newsletter, partenaire du mois et conversion complète reportés hors squelette. | Composition, hiérarchie, couverture et entrées. |
| Kiosque `archive-imagine_numero.php` | §3.3, §4.2 ; arbitrage B01 §4 | Tous les cinq numéros matérialisés, hors-série inclus, sortie DESC. Date obligatoire à publication, pas de repli. | Cartes, recadrage, rythme. |
| Numéro `single-imagine_numero.php` | §3.3, §4.2 | Couverture, résumé, sommaire relationnel et PDF factice public B00. Sommaire audio et achat reportés ; droits PDF non revendiqués. | Fiche, sommaire, liens PDF. |
| Article `single.php` | §3.3, §4.2 | Titre, chapô, auteur, numéro, thématiques et sortie unique. Mode lecture reporté ; décision paywall à C08. | Typographie longue, métadonnées, médias. |
| Thématique `taxonomy-imagine_thematique.php` | §3.1, §3.3 | Articles liés tous numéros confondus. Statuts graphiques d'accès non conçus ici. | Rubrique, cartes, pagination. |
| Agenda `archive-imagine_evenement.php` | §3.11, §4.2 | Deux événements fictifs, ordre date ASC, dates localisées. Billetterie hors B01. | Listes, dates, inscriptions ultérieures. |
| Événement `single-imagine_evenement.php` | §3.11, §4.2 | Titre, date, texte et retour agenda. | Composition et informations pratiques. |
| Partenaires `archive-imagine_partenaire.php` | §3.12 ; arbitrage B01 §2 | Mention traduisible « Partenariat », déclaration des liens, cartes `rel="sponsored"`. | Distinction visuelle rédaction/partenariat, logos. |
| Partenaire `single-imagine_partenaire.php` | §3.12 | Fiche native ; liens externes du contenu déclarés sponsored par HTML API WP, préservant les autres rel. Aucun lien externe visité. | Composition et médias. |
| Page simple `page.php` | §3.1 ; brief B01 | Contenu natif et tableau B00 **15 lignes 2026–2028**, seulement **5 numéros 2026** matérialisés. Dates de ce tableau brut B00 inchangées ; la localisation B01 concerne les éléments `time`. | Texte, tableaux et légendes. |
| Recherche `search.php`, `searchform.php` | §3.1 ; brief B01 ; frontière §3.9/C08 | GET natif, cartes sans corps, pagination, « Aucun résultat pour votre recherche. ». Filtrage serveur des correspondances dans les corps réservés **non certifié**, appartient à C08. | Champ, résultats et état vide. |
| 404 `404.php` | Brief B01 | Vrai statut 404, recherche et accueil. | Composition, éventuelle illustration. |
| En-tête/pied | §3.1, §3.2 ; brief B01 réduit | Repères, évitement, navigation à clés stables, entrées compte/abonnement. Pied complet du cahier et tunnel reportés. | Identité, navigation responsive et focus. |
| Repli `index.php` | Hiérarchie native ; brief B01 | Titres, extraits, pagination. | Réutiliser les composants validés. |

## Correctifs et assertions

- **Accueil** : l'oracle énumère les 20 clés d'articles des fixtures B00, résout leurs IDs dans le manifeste et ajoute les deux IDs explicitement nommés par la fixture C08. Dates de publication imposées par les deux seeds : `2026-01-01 12:00:00`. Le tri indépendant date DESC / ID DESC attend actuellement **82, 81, 45, 44, 43**. L'inventaire doit aussi correspondre exactement aux fixtures : aucun intrus. Tests négatifs intrusion/permutation et preuve qu'un mutant limité à la cardinalité échoue.
- **Purge/locale** : déjà faites par B00 ; vérifiées sans les refaire. `front-page.php` inchangé ; aucun nouveau filtre « article avec numéro ».
- **Date du numéro** : fichier séparé `wp/plugins/imagine-site/NumeroPublication.php`, avec trois lignes de chargement dans le bootstrap. Insertion/mise à jour native sans date valide → brouillon ; REST → erreur 400 explicite. Date impossible refusée ; brouillon autorisé ; date valide publiée ; modification valide autorisée ; suppression/vidage d'une date publiée refusés. Les publications programmées sont aussi gardées. Aucun changement de `Paywall.php`.
- **Navigation** : sept clés slug stables ; le test impose trois archives à la même URL et conserve les sept entrées. Les URL ne servent plus de clés.
- **Dates** : `wp_date('j F Y', …, wp_timezone())`, avec valeur ISO dans `datetime`. Test réel « 11 décembre 2026 ». Le choix graphique reste au designer.
- **Partenariat** : mention et déclaration sur la liste ; liens des cartes sponsorisés. Un test synthétique du rendu d'un lien externe de fiche prouve `sponsored` et conservation de `noopener`, sans changer les données partenaires.

## Standard d'abord et méthode

Hiérarchie classique, `the_content`, `pre_get_posts` principal hors admin, formulaire/pagination natifs, `wp_date`, HTML API de WordPress et hooks d'insertion/métadonnées. Copies des références officielles initiales et des références des correctifs dans `references/` ; les nouvelles pages WordPress ont été consultées avant leur implémentation. Pas de constructeur, JS ni dépendance front ajoutée.

**Écart initial à transmettre à Claude pour `docs/ecarts.md`** : tests/amorce du shell avant références dans la livraison initiale (ancienne note §54). Cet historique reste déclaré ; aucun document global n'a été écrit par ce lot. Les journaux rouges de navigation, localisation, publication sans date et lien partenaire, puis verts, sont dans `tests/`.

## Rejeu isolé et installation ciblée

Depuis la racine, avec `python` et `uv` disponibles localement :

```text
python production/B-01/b01-isolated.py
python wp/outils/demo/construire.py --theme-only
```

`b01-isolated.py` crée un nouvel environnement sous le scratch Hermes, sans paquets globaux, installe **hors ligne** avec `--no-index --require-hashes` les six wheels de `validation/requirements.lock`, vérifie leurs dépendances, lance les **4 tests B01 historiques et 2 tests de correction**, puis revalide les 43 HTML. Les chemins d'import de chaque paquet sont assertés dans ce seul environnement et enregistrés dans `tests/isolated-environment.json`. Dépendances complètes : html5lib 1.1, webencodings 0.5.1, six 1.17.0, beautifulsoup4 4.14.3, soupsieve 2.8.3, typing_extensions 4.15.0. Aucune installation sur le NUC ou dans un Python global.

La recette live se rejoue avec le Python de cet environnement : `python wp/tests/demo/b01-verifier.py`. Pour les contrôles PHP ciblés : `python production/B-01/b01-work.py php b01-corrections-runtime.php runtime-final`. Les objets temporaires de ces contrôles sont supprimés et leur absence relue. Le garde est déployé séparément par `b01-work.py deploy-plugin` (préimage du bootstrap vérifiée) ; le thème utilise uniquement le script B00 actuel **non modifié**, option `--theme-only`. Aucun reseed B00/C08/C09.

Sauvegarde du thème/point de chargement avant déploiement : `runtime-backup-before-deployment.json`. Installation et readback exacts des **23 fichiers du thème**, dont **21 PHP parsés** : `installation.json`. Garde : `plugin-installation.json`, les deux fichiers relus exactement. L'avertissement WP-CLI « thème déjà actif » est attendu, sans erreur PHP.

## Résultats actuels et limites

- **6 tests Python réussis**, dont le validateur rejetant cinq corruptions HTML ; environnement propre hors ligne et chemins d'import vérifiés.
- **16 contrôles PHP ciblés réussis**, avec véritable insertion native, vraie route REST, dates manquantes/impossibles, liens partenaires et collisions de navigation ; objets temporaires supprimés.
- **554 assertions runtime/HTTP réussies, 0 échec**, **62 contrôles runtime inclus**, **43 pages HTML** et **7 ressources**. Sommaire T1 : quatre articles B00 **plus deux C08** ; les autres numéros gardent leurs quatre articles. Aucune cardinalité héritée appliquée aveuglément à l'état augmenté.
- **19 captures actuelles** (15 bureau, 4 mobile) et **5 contrôles d'interaction** réussis : évitement/focus, article ouvert, absence de corps réservé dans la réponse exercée, GET recherche vide. Pas de débordement mesuré. Captures accueil mobile et partenaires bureau inspectées visuellement.
- `scope-before-runtime.json` et `scope-after-runtime.json` : données/options/comptes/droits/décisions et sources protégées **C08/C09/C10 identiques**. Les comptes C09 n'ont pas été réinitialisés pour modifier leur oracle temporel J+30/+45.

Le HTML est contrôlé par parseur HTML5 et assertions sémantiques : pas une certification W3C ni un audit WCAG complet. Aucun GO visuel, tunnel, achat, licence, email ni appel HTTP WordPress externe. Le garde de `wc_get_page_permalink` dans les parts et le filtrage de recherche bloquant sont **transmis à C08, non corrigés ici**. Les preuves B01 ne valent pas conformité de C08.

Aucun Git, verrou, rapport global, document de gouvernance ni fichier de voie 1 modifié. PRET signifie prêt au second tour B01, pas validation de maquettes ou déploiement réel.
