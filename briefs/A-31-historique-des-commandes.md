# Lot A-31 — L'historique que les abonnés gardent : les commandes, comptées

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-19, A-20, A-22 (le gardien des sorties), T-03 (la déclaration de rejeu). **Cahier des charges** : §4.3 (« Abonnés en ligne actuels : comptes, abonnements, moyens de paiement et historique repris du site actuel »). Relis-le.

## Pourquoi

Le cahier des charges promet aux abonnés en ligne qu'ils gardent leur historique. On sait déjà compter leurs comptes (A-23), ce qu'ils paient (A-20), leurs moyens de paiement (A-27). On ne sait pas encore dire **ce qu'est cet historique** : combien de commandes, depuis quand, combien sont des renouvellements, et combien ne tiennent plus à rien (un renouvellement dont l'abonnement a disparu, un abonnement sans commande d'origine). Ce sont ces liens cassés qui feront des pages « Mes commandes » vides ou fausses après la bascule, et c'est avant qu'il faut le savoir.

**Ce lot compte. Il ne répare, ne rattache et ne supprime rien.**

## Ce qu'on veut

**Le standard d'abord.** Huit lignes dans le mode d'emploi : comment WooCommerce Subscriptions relie une commande à un abonnement (commande d'origine, renouvellement, changement de formule, réabonnement), d'après la documentation officielle et le code installé, et par quelles fonctions natives on le lit.

Un complément du script d'audit, en **lecture seule**, dans `wp/outils/bascule/a31/`, lancé par le gardien commun, qui lit les deux magasins de commandes (classique et HPOS) et sort des **nombres seulement** :

- les commandes par **année** et par **état**, les états pris dans la liste fermée de WooCommerce ; un état ajouté par une extension est compté « autre », son nom ne sort pas ;
- les commandes par **nature**, liste fermée : commande d'origine d'un abonnement, renouvellement, changement de formule, réabonnement, commande sans abonnement ; une commande qu'on ne sait pas classer est « illisible », jamais rangée d'office ;
- les **liens cassés** : renouvellements dont l'abonnement n'existe plus ; abonnements vivants sans commande d'origine ; commandes rattachées à un compte qui n'existe plus ;
- les remboursements, par année ;
- l'année de la plus ancienne commande.

**Aucun montant**, aucun numéro de commande, aucun identifiant de compte ou d'abonnement, aucune date plus fine que l'année. Les groupes de moins de cinq sont fondus, comme dans A-20.

L'import anonymise les commandes. Regarde ce qu'il en fait, **sans le modifier : l'import est gelé**. Pour chaque nombre qu'il fausse, la réponse sur une copie neutralisée est « inconnu après neutralisation », jamais zéro ; dis lesquels restent lisibles.

Si un nombre demande une règle (qu'est-ce qu'un abonnement « vivant », par exemple), reprends celle d'A-19 telle quelle et dis-le ; n'en écris pas une autre.

## Preuve

Sur le banc fictif, classique et HPOS : une commande de chaque nature, un renouvellement orphelin, un abonnement sans commande d'origine, une commande d'un compte supprimé, un remboursement, un état inconnu dont le nom est un canari. Les nombres sont exacts ; les canaris sont absents de toutes les sorties, sur chaque canal et dans les fichiers de rapport ; empreintes de la base et des fichiers identiques avant et après ; le cas neutralisé répond « inconnu » là où il le doit ; la commande du mode d'emploi, copiée telle quelle, fonctionne. **Un seul paquet de preuves**, vérificateur sans argument, avec sa déclaration `rejeu.json` dès la livraison. Suite Python rejouable sous Windows (cp1252).

Tu peux construire l'outil et sa suite Python sans attendre la fin d'A-28 ; la matrice native se joue sur l'import gelé, avec la requalification ou après elle.

## Livrables

L'outil, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-31/PRET`. Rapport court, avec les nombres qui valent « inconnu » sur une copie neutralisée.
