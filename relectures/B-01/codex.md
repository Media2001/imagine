# Relecture indépendante Codex — B-01

Date : 23 novembre 2026. Périmètre : brief B-01, production B-01, thème Imagine, branchement du constructeur B-00 et tests associés. Doctrine et décisions consultées. Le brief ne cite aucun paragraphe précis du cahier des charges ; rapprochement effectué avec les §3.1–3.3, §3.12, §4.1–4.2 et le chapitre 5, ainsi qu’avec le §3.9 pour la frontière du paywall.

Aucun site, compte ou base consulté. Aucun rapport de l’autre relecteur consulté. Seul ce rapport est écrit. Les commandes Python ont été exécutées avec `-B`, sans création de caches ni installation de dépendances.

## 1. Conformité

Les gabarits demandés sont présents, ainsi que `A-VOIR.md`, les demandes au designer, les preuves et `PRET`. Le choix des variables dans `assets/tokens.css` est expliqué. Les gabarits ne contiennent pas de styles en ligne ; aucun JavaScript propre au thème. La capture mobile de l’accueil confirme une présentation neutre en une colonne. Le point unique `imagine_article_body()` existe et `single.php` l’appelle une seule fois.

Le dépôt courant contient déjà le raccord C-08 : après comparaison des empreintes avec normalisation des fins de ligne, `functions.php` est le seul fichier différent parmi les sources du manifeste final B-01. Les quatre fragments de paywall sont également postérieurs à cet inventaire. Les preuves B-01 décrivent donc un état antérieur ; elles ne démontrent pas à elles seules le fonctionnement courant du paywall. Ce raccord prévu par le brief n’est pas imputé à B-01 comme un dépassement de périmètre.

- **R1 — important — `wp/themes/imagine/front-page.php:18`.** La sélection prend indistinctement les publications WordPress, y compris l’article d’installation. La réponse archivée `production/B-01/http/accueil.html:103` affiche réellement « Hello world! » en tête des derniers articles ; l’identifiant 1 n’appartient pas aux vingt articles de l’inventaire B-00. Il occupe une des cinq places sans numéro ni thématique, contrairement au modèle éditorial du §3.1 et à l’accueil demandé. **Correction proposée :** sélectionner les articles éditoriaux rattachés au modèle provisoire B-00, en conservant un ordre explicite, puis vérifier les cinq identifiants attendus et l’absence de l’article d’installation. Ne pas supprimer ce contenu manuellement sur le site.

- **R2 — important — `wp/themes/imagine/archive-imagine_partenaire.php:9`.** La page porte seulement le titre « Partenaires » et réutilise les mêmes cartes que les articles ; la mention explicite « Partenariat » demandée au §3.12 manque aussi dans la réponse archivée. Cette qualification éditoriale peut être posée sans anticiper les maquettes. **Correction proposée :** ajouter la mention traduisible « Partenariat » au gabarit de liste et la vérifier dans le HTML ; réserver le traitement graphique au designer.

Les liens compte et abonnement sont des entrées provisoires documentées ; le tunnel et l’espace compte sont explicitement hors périmètre. Le maintien du verrou B-00, malgré la formulation « texte complet » du brief, est signalé dans les notes et cohérent avec la doctrine de protection des contenus. Autre tension à tracer : le §3.2 du cahier des charges demande des maquettes validées avant les gabarits, alors que B-01 demande expressément un squelette avant maquettes ; cette relecture ne vaut pas validation graphique.

## 2. Exactitude métier

Cas déroulés à partir des fixtures, de l’inventaire enregistré, du code et des réponses HTML locales :

1. **Kiosque avec hors-série — §3.3.** Dates attendues : 15 octobre, 15 août (hors-série), 15 juillet, 15 avril, 15 janvier 2026. Résultat enregistré : identifiants `39, 32, 25, 18, 11`, dans cet ordre. Conforme pour ce jeu ; le hors-série n’est pas exclu. L’accueil présente bien le numéro 39 comme dernier numéro.
2. **Sommaire d’un numéro — §3.3 et §4.2.** Le numéro 39 possède les articles `42, 43, 44, 45`. La fiche enregistrée affiche exactement ces quatre articles ; le gabarit sélectionne la relation `imagine_numero_id` et lit le PDF associé après restauration du contexte de publication. Conforme pour ce cas.
3. **Thématique transversale — §3.1 et §3.3.** La thématique 20 rassemble `16, 23, 30, 37, 44`, répartis entre les cinq numéros. L’ensemble affiché correspond à l’inventaire ; ce n’est pas une sélection limitée au dernier numéro.

Les dates ISO complètes conservent leur ordre lors du changement d’année ; les dates égales sont départagées explicitement par l’identifiant. Ce sont des constats de lecture du code, pas des scénarios WordPress exécutés pendant cette relecture. Les échéances d’abonnement et événements de paiement rejoués ne relèvent pas de B-01.

- **R3 — important — `wp/themes/imagine/functions.php:66`.** Le tri du kiosque impose `meta_key = imagine_sortie`. Une publication `imagine_numero` sans cette métadonnée est exclue de la requête, au lieu d’apparaître parmi « tous les numéros ». Le modèle provisoire ne rend pas ce champ obligatoire à la publication. Le même filtre existe dans la sélection de l’accueil. **Correction proposée :** conserver les numéros sans date dans le kiosque, signaler leur date manquante et définir leur position de repli ; tester au moins un numéro publié sans métadonnée. L’inventaire de référence doit alors compter les numéros indépendamment de la présence de cette date. Défaut identifié statiquement ; cas non exécuté sur WordPress.

## 3. Tests

Exécution locale effective :

| Commande | Résultat |
|---|---|
| `python -B wp/tests/demo/test_b01_theme.py` | 4 tests lancés : 3 réussis, 1 erreur d’import ; sortie 1. |
| `python -B wp/tests/demo/test_b00_construction.py` | 4 tests réussis ; sortie 0. Avertissement Python de nettoyage d’un objet `HTTPError` simulé, sans échec. |
| `php -l wp/themes/imagine/functions.php` | Non exécuté : commande `php` introuvable dans cet environnement. |

- **R4 — important — `wp/tests/demo/b01_html.py:8`.** Le test de validation HTML échoue avec `ModuleNotFoundError: No module named 'six'`. `bs4` est également absent. Seuls les wheels html5lib et webencodings sont fournis ; les notes supposent deux dépendances déjà installées sans définir un environnement reproductible complet. **Correction proposée :** déclarer et figer toutes les dépendances nécessaires, avec une procédure de test isolée et locale, puis rejouer la suite sur un environnement propre. Ne pas présenter les quatre tests comme rejouables à partir du seul dépôt actuel.

- **R5 — important — `wp/tests/demo/b01-verifier.py:111`.** L’assertion intitulée « cinq derniers articles » vérifie seulement que l’accueil contient six identifiants, numéro compris. Elle réussit donc avec « Hello world! » et ne contrôle ni l’appartenance au jeu éditorial, ni les identifiants attendus, ni leur ordre. **Correction proposée :** comparer la liste ordonnée des cinq articles à une attente indépendante issue des fixtures ; vérifier qu’une intrusion ou permutation fait échouer le test.

Autres limites de couverture : le kiosque est comparé à un inventaire utilisant lui aussi `meta_key = imagine_sortie`, ce qui masque R3 ; le contrôle de l’agenda compare des ensembles et ne prouve pas l’ordre chronologique. Les tests locaux du thème inspectent principalement des chaînes dans les sources ; ils ne rendent pas les gabarits avec WordPress. Les cas de dates absentes/égales et le parcours réel vers une deuxième page d’archive ne sont pas exercés par la recette examinée.

Contrôles indépendants en lecture seule : les 500 assertions consignées sont bien toutes marquées réussies ; les 41 réponses correspondent à leurs empreintes, après prise en compte des seules fins de ligne CRLF/LF. Chacune contient un seul élément `h1` ouvrant et aucune ne contient le marqueur `CONTENU_FICTIF_RESERVE_`. Ces contrôles limités ne remplacent pas le parseur HTML5, dont le rejeu est empêché par R4.

`b01-verifier.py` n’a pas été lancé : il accède au site, téléverse un fichier et réécrit les preuves, contrairement aux droits du relecteur et à la restriction d’écriture de cette mission. L’activation, les statuts HTTP actuels et les interactions navigateur ne sont donc pas revérifiés. Les chiffres 500/500, les 19 captures et les quatre interactions restent des preuves historiques du producteur. De plus, les attentes de verrou natif B-01 ne constituent pas une recette adaptée au branchement C-08 actuel.

## 4. Sécurité et données

Pas de secret ni de donnée personnelle réelle identifié dans les sources et preuves examinées. Les sorties de métadonnées, URLs, champs de recherche et extraits emploient les fonctions d’échappement WordPress. Le thème ne crée pas d’action d’écriture nécessitant un nonce ; les requêtes passent par les API natives, sans SQL assemblé.

Le constructeur ciblé contrôle l’identifiant du site, son état, l’environnement local et le marqueur fictif avant le téléversement ; les refus testés passent. Aucun constructeur ni transport distant exécuté pendant la relecture.

L’absence du marqueur réservé dans les 41 réponses archivées est vérifiée localement. Cela ne démontre ni l’étanchéité REST/flux/oEmbed, ni les droits sur les PDF. Les PDF factices publics et la frontière de C-08 sont explicitement déclarés dans les notes. Aucune conclusion de conformité globale du paywall n’est donnée pour ce lot.

## 5. Doctrine

Les mécanismes natifs de thème classique, de requête, de pagination et de chargement des styles sont employés. Aucun constructeur ou équivalent maison d’une extension retenue n’est ajouté. Les fichiers PHP du thème portent `strict_types` et l’espace de noms `Imagine\Theme` ; les fonctions propres au thème sont préfixées et ses libellés sont traduisibles. Les formulations anglaises du verrou natif sont une limite déclarée de la démonstration.

- **R6 — mineur — `production/B-01/notes.md:16`.** Le tableau décrit les comportements réalisés sans rattacher les règles éditoriales aux paragraphes du cahier des charges. Les références WordPress documentent les mécanismes techniques, mais pas les exigences métier ni leurs reports. **Correction proposée :** ajouter les références pertinentes (§3.1–3.3, §3.12, §4.2) et qualifier explicitement ce qui est réalisé, provisoire ou reporté à un autre lot.

L’écart « références officielles consultées après l’amorce du shell » est déclaré honnêtement ; il reste un écart à la méthode de la doctrine. Les notes ne prétendent pas avoir exécuté la reconstruction complète B-00. La validation structurelle ciblée n’est pas présentée comme un audit WCAG complet, ce qui est correct.

## 6. Études (lots sans code)

Sans objet : lot de code. Les copies locales de références techniques et leur inventaire sont présents ; aucune consultation de site externe effectuée.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun défaut bloquant établi dans le périmètre B-01 examiné.
- **Important :** R1 — article d’installation dans les derniers articles ; R2 — qualification « Partenariat » absente ; R3 — numéros sans date exclus du kiosque ; R4 — dépendances de tests incomplètes ; R5 — assertion des derniers articles insuffisante.
- **Mineur :** R6 — traçabilité des exigences métier à compléter.

La nouvelle vérification devra distinguer l’état livré B-01 du raccord C-08, et disposer d’un environnement permettant le rejeu effectif des contrôles HTML et PHP.
