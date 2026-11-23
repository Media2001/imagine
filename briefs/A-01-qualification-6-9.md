# Lot A-01 — qualifier le parcours pour la version de la production

**Date** : 23/11/2026. **Délai** : une demi-journée. C'est le lot de qualification prévu par la réponse n° 4 du 22/11.

## Le blocage

Ta commande refuse aujourd'hui toute archive en WordPress 6.9.1, avant même de la lire, parce que ton banc d'essai n'est qualifié qu'en 7.0.9 : les archives de WooCommerce 11.1.1 et de Subscriptions 9.4.1 que Ced a déposées exigent WordPress 7.0. Le refus est correct et bien déclaré. Mais la production d'Imagine est en 6.9.1 : en l'état, la commande ne peut pas servir.

## Ce qui a été confondu

Deux choses distinctes :

- **Le banc d'essai** a besoin d'extensions pour fabriquer des sites fictifs. Il utilise celles que Ced a déposées, les plus récentes.
- **L'import réel** n'installe aucune extension. Elles viennent de l'archive d'Imagine, dans les versions que la production fait tourner aujourd'hui, donc compatibles avec son WordPress.

La version des extensions du banc ne doit donc pas décider de ce que la commande accepte d'importer.

## Ce qu'on veut

1. **Le cœur du site suit l'archive.** La commande lit la version de WordPress dans le manifeste de l'archive, met le site vide à cette version **tant qu'il est vide** (téléchargement depuis `wordpress.org`, avant toute injection), puis injecte. Elle vérifie ensuite l'égalité stricte entre la version de l'archive et celle du cœur. `--expected-core-version` reste un garde-fou : si l'archive n'est pas dans la version attendue, refus avec rapport.
2. **Aucune extension n'est installée ni mise à jour par l'import.** Celles de l'archive sont conservées telles quelles. Si une extension de l'archive déclare exiger une version de WordPress ou de PHP supérieure à celle du site, c'est un **avertissement** dans le rapport, pas un refus : la production tourne ainsi.
3. **Une qualification en 6.9.1**, sur un site fictif fabriqué dans cette version, avec la dernière version de WooCommerce compatible avec elle (versions publiques sur `wordpress.org`). Aller-retour complet : export `.wpress`, commande, site publié et vérifié ; puis le cas piégé.
4. **Subscriptions et Memberships en 6.9.1** : si Ced dépose des archives de ces extensions dans des versions compatibles (dossier habituel), utilise-les. Sinon, ne bloque pas : leurs traitements sont qualifiés en 7.0.9, et tu l'écris comme **limite** dans le rapport. Le premier import réel, lancé par Ced, servira de test sur ce point, et son rapport de vérification sera relu avant toute ouverture.

## Livrables

- La commande accepte une archive 6.9.1 et aboutit, sur archive fictive, à un site vérifié en 6.9.1.
- `production/A-01/notes.md` : le mode d'emploi pour Ced tient en une page en tête de fichier, historique en dessous. Y figurent : la commande exacte en PowerShell, ce que Ced doit fournir, ce qu'il verra, la durée, et quoi faire en cas de refus.
- La limite du point 4, dite clairement.
- `production/A-01/PRET`.

## Inchangé

Aucun import d'Imagine, aucune ouverture de son archive, aucun usage de l'accès agent, aucune modification de l'outil de staging au-delà de ce qui est déjà fait, sites de test `imagine-test-…` supprimés à la fin.
