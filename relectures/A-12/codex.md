# Relecture indépendante Codex — A-12

Date : 26 novembre 2026. Périmètre : brief A-12, production A-12, collecteur et tests dans `wp/`, dépendances A-02/A-11 utilisées par le collecteur. Doctrine, grille, décisions et §4.2/§4.3 du cahier des charges consultés. Aucune lecture de `relectures/A-12/claude.md`, aucun accès à un site ou à une base externe. Seul ce rapport est écrit.

## 1. Conformité

Les livrables demandés sont présents : collecteur, suite dédiée, documentation, deux lignes intégrées dans `wp/tests/a02-audit/README.md:65` et marqueur `PRET`. Le registre est obtenu à l'exécution ; les métadonnées sont agrégées par contenu distinct ; les médias et les liaisons produits sont inventoriés sans décider de rattachement.

Les conventions sur les dates, les originaux des médias, les parents orphelins et les références scalaires sont explicites. Elles restent dans le périmètre préparatoire des §4.2 et §4.3. Deux défauts empêchent cependant de retenir la conformité : le confinement accepte une disposition qui rend le site inscriptible (B1), et les comptes des taxonomies supposent à tort que tous leurs objets appartiennent à `posts` (I1).

## 2. Exactitude métier

Cas déroulés à partir du jeu fictif `wp/tests/a12/seed.php`, puis comparés aux rapports classique et HPOS fournis, avec assertions indépendantes exécutées en mémoire :

| Cas | Résultat attendu | Résultat observé |
| --- | --- | --- |
| Cinq articles, dont deux publiés ; une clé présente sur les cinq avec une ligne supplémentaire sur le premier | États : 2 publiés, 1 brouillon, 1 privé, 1 corbeille ; 5 porteurs de la clé | Conforme dans les deux modes |
| Deux rubriques utilisées par respectivement trois et deux articles, avec un article commun | 3 et 2 usages ; 4 contenus distincts pour la taxonomie | Conforme dans les deux modes |
| Deux PDF de 23 et 28 octets, dont un sans parent | 2 PDF, 51 octets, 1 PDF orphelin | Conforme dans les deux modes ; les 2 orphelins globaux incluent aussi le média WooCommerce |

**I1 — Important — `wp/outils/bascule/a12/Inventory.php:253` — Confusion entre les domaines d'identifiants des taxonomies.** Toutes les relations sont jointes à `posts` sur le seul identifiant, sans tenir compte du type d'objet enregistré pour la taxonomie. Une taxonomie de liens telle que `link_category` peut avoir une relation pour le lien 41 alors qu'un article distinct porte aussi l'ID 41 : le rapport attribue alors l'état et la date de cet article à la taxonomie de liens. Sans article homonyme, l'objet lié disparaît des comptes. Le calcul des vingt premiers termes reproduit la même hypothèse.

Reproduction locale : la même jointure d'agrégation, exécutée dans SQLite en mémoire avec un lien 41 catégorisé et un article 41 non catégorisé, renvoie `publish: 1`. Cette reproduction vérifie la jointure ; elle ne constitue pas un rejeu WordPress/MariaDB.

Correction proposée : conserver les types d'objets des taxonomies et limiter les agrégations de contenus aux domaines effectivement pris en charge. Pour les taxonomies hors `posts` ou mixtes, signaler explicitement la limite sans leur attribuer les états/dates d'un article homonyme. Ajouter un cas natif de collision lien/article et un cas sans collision. Défaut technique prudent : comptes non qualifiés explicitement indisponibles, sans inventer un état de publication.

## 3. Tests

Commande exécutée sans écriture des preuves :

```text
python -B wp/tests/a12/verify.py production/A-12/preuves/final
```

Résultat : **code 1, 40 contrôles réussis sur 41**. Le seul contrôle en échec est `exact_owned_runner_still_absent`. L'appel de précondition du runner à `wsl.exe -d Ubuntu -- docker image inspect …` échoue également avec `Wsl/Service/E_ACCESSDENIED` (code 4294967295). Il est donc impossible de vérifier actuellement l'absence du conteneur ; cet échec ne prouve pas qu'il existe encore.

**La suite native et PHPCS n'ont pas pu être rejoués dans cette session**, faute d'accès à WSL/Docker. Aucun conteneur n'a été créé et aucune preuve n'a été réécrite. Les reçus existants annoncent 118 assertions natives, 7 assertions pures, 7 contrôles du runner et 6 contrôles de style réussis. Le vérificateur confirme leurs empreintes par rapport aux sources actuelles, les instantanés identiques des 55 tables par mode et les reçus de registre/confinement. Ces preuves conservées ne sont pas présentées comme un nouveau rejeu.

Les tests fournis couvrent notamment les doublons de métadonnées, les types vides/dynamiques, les objets désenregistrés, les médias absents, les symlinks et plusieurs destinations interdites. Ils ne couvrent ni un parent de sortie ancêtre du site/dépôt, ni une taxonomie portant sur un autre domaine d'objets. Les assertions indépendantes sur les comptes et les deux reproductions ciblées décrites dans ce rapport ont été exécutées sans fichier auxiliaire.

## 4. Sécurité et données

**B1 — Bloquant — `wp/outils/bascule/a12/confine.py:61` — Le parent autorisé en écriture peut contenir le site ou le dépôt.** Le garde refuse un parent situé *dans* le site/dépôt, mais pas la relation inverse. Par exemple, avec un site `/travail/site`, un audit `/travail/audit/audit.json` et une sortie `/travail/contenus`, le parent `/travail` est accepté. Landlock lui accorde ensuite les droits de mutation, qui couvrent aussi `/travail/site`. Le contrôle PHP reprend le même sens de comparaison. Le code tiers chargé au bootstrap peut donc créer ou tronquer des fichiers du site malgré la protection annoncée. Un parent commun avec le dépôt expose également les sources ; choisir `/` élargit encore cette autorisation.

Reproduction sans mutation : import du lanceur et appel de `main()` avec un site existant et une sortie fictive dans son parent ; remplacement en mémoire de `confine()` par une sonde qui interrompt immédiatement l'appel. Résultat : `UNSAFE_PARENT_REACHED_CONFINEMENT: True`, `SITE_UNDER_WRITE_ROOT: True`. Aucun Landlock, PHP ni fichier de sortie n'a été lancé/créé par cette sonde.

Correction proposée : avant toute autorisation Landlock, exiger que l'arborescence inscriptible soit disjointe du site et du dépôt dans **les deux sens**, sur chemins résolus ; appliquer le même invariant dans la commande PHP. Ajouter les refus des parents ancêtres et de `/`, puis éprouver les tentatives de création/troncature sur le banc natif. Défaut technique prudent : refuser toute intersection entre ces arborescences.

Pour le reste du périmètre relu : valeurs de métadonnées non exportées, SQL paramétré pour les valeurs variables, sorties privées, configuration non exécutée, connexion native en lecture seule et garde des appels HTTP/mail/cron présents. Les canaris privés sont absents des rapports fictifs contrôlés. Le lot n'ajoute aucune voie publique de diffusion soumise au paywall.

## 5. Doctrine

Réutilisation des API natives et des dépendances A-02/A-11 ; absence de modèle éditorial ou de règle d'accès inventée. Les sources PHP du lot suivent l'espace de noms `Imagine\` et le mode strict ; le reçu PHPCS fourni indique zéro erreur et avertissement, sans nouveau contrôle de style exécutable ici. B1 contredit la garantie de lecture seule et doit être corrigé avant de considérer la livraison prête.

Les corrections proposées sont techniques et ne nécessitent aucun arbitrage de Ced. Aucun accès au réel n'est demandé ou autorisé par cette relecture.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références officielles et leurs reçus sont présents dans la production. Leur disponibilité HTTP n'a pas été revérifiée, conformément à l'interdiction d'accès à un site pour cette relecture.

## Verdict

**À corriger.**

- **Bloquant — B1 :** parent inscriptible pouvant englober le site ou le dépôt.
- **Important — I1 :** agrégations erronées pour les taxonomies hors du domaine `posts`.
- **Mineur :** aucun point retenu.

Le rejeu natif et le contrôle de style restent à effectuer dans un environnement où WSL/Docker est accessible, après ajout des cas manquants. Ce verdict n'est pas un GO.
