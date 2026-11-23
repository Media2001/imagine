# C08 — Références des corrections

Sources primaires WordPress consultées dans le navigateur ; titres/URL/extraits de consultation conservés dans `references-corrections.json` :

- `posts_search` : https://developer.wordpress.org/reference/hooks/posts_search/ — point de filtrage de la clause SQL native de recherche.
- `posts_orderby` : https://developer.wordpress.org/reference/hooks/posts_orderby/ — garde complémentaire de la pertinence/du classement, pas seulement du texte renvoyé.
- `update_post_meta` : https://developer.wordpress.org/reference/functions/update_post_meta/ — écritures natives de métadonnées ; le contrat booléen est éprouvé par stockage et lecture, pas seulement déduit de la documentation.
- Authentification REST : https://developer.wordpress.org/rest-api/using-the-rest-api/authentication/ — session native et nonce REST, lecture de la réponse avec le vrai utilisateur de session. Aucun nonce/cookie privé archivé.

Références projet lues, sans écriture : `A-FAIRE-2.md`, `prompts/consigne-permanente.md`, `doctrine/doctrine.md`, `briefs/C-08-paywall-sur-article.md`, `corrections/C-08.md`, `docs/arbitrages-2026-11-23.md` (§C08 17 h 10), `docs/recette/cas.md` R25–R31. Les bibliothèques closes C06/C03 et les preuves corrigées B00/B01 ont été relues pour leurs contrats/prérequis. Aucune modification d'un arbitrage ou d'une bibliothèque métier.

Dépendances HTML : **réutilisation**, pas nouvelle livraison B01. `production/B-01/validation/requirements.lock`, `dependencies.json` et les six wheels font foi ; environnement neuf hors dépôt, installation sans index, versions/empreintes et unitaires réellement exécutés dans `local-tests.json`.

Les assertions de fonctionnement de la présente livraison sont fondées sur `verification-finale.json` et ses reçus d'exécution, pas sur la seule lecture des références ni les anciennes preuves dans `historique/`.
