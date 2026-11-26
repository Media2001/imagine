# Lot A-24 — Les adresses d'expédition des abonnés : complètes ou non

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-19, A-20, A-22 (le gardien des sorties). **Cahier des charges** : §3.13 (« Liste d'envoi : pour chaque numéro, export des adresses de livraison des abonnés qui y ont droit »), §4.3 (abonnés en ligne repris du site actuel).

## Pourquoi

La liste d'envoi du nouveau site sortira les adresses de livraison telles qu'elles sont sur les abonnements repris de la production. Aujourd'hui l'extraction se fait dans Access, et personne ne sait dans quel état sont ces adresses sur le site : une adresse de livraison vide (seule celle de facturation remplie), un pays absent, un code postal manquant, et le magazine ne part pas. Avant la bascule, Ced doit pouvoir dire à Imagine : tant d'abonnés vivants ont une adresse de livraison utilisable, tant sont à compléter.

**Ce lot ne corrige aucune adresse, ne recopie rien de la facturation vers la livraison et ne décide pas de ce qu'est une adresse « bonne pour la poste ».**

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné et le gardien des sorties d'A-22.

**Le standard d'abord.** Dix lignes dans le mode d'emploi : où WooCommerce et Subscriptions rangent l'adresse de livraison d'un abonnement (classique et HPOS), et quels champs WooCommerce tient pour obligatoires selon le pays, d'après la documentation officielle et le code installé. C'est cette liste native qui définit « champ manquant », pas une liste inventée.

Puis des **comptes seulement**, pour les abonnements vivants (les mêmes états qu'A-20) :

- nombre d'abonnements dont l'adresse de livraison est entièrement vide ; parmi eux, combien ont une adresse de facturation remplie ;
- nombre d'abonnements à qui il manque au moins un champ obligatoire de livraison, **par champ** (noms de champs natifs, liste fermée) ;
- nombre d'abonnements dont le pays de livraison est absent ou n'est pas un code connu de WooCommerce ;
- nombre d'abonnements dont l'adresse de livraison diffère de celle du compte du client (comparaison champ à champ, à la casse et aux espaces près) ;
- les mêmes nombres par pays de livraison (code du pays), les pays à moins de cinq abonnements regroupés sous « autres pays », comme A-20.

**Aucune adresse, aucun fragment d'adresse, aucun nom, aucun code postal, aucun identifiant de compte ou d'abonnement** ne sort : des nombres, des codes de pays et des noms de champs d'une liste fermée. Règle de la voie 1 : aucune sortie, sortie d'erreur comprise, ne recopie un chemin ou un nom tiré du site.

L'import anonymise les adresses. Regarde ce qu'il en fait, **sans le modifier** : pour chaque nombre que l'anonymisation fausse, la réponse sur une copie neutralisée est « inconnu après neutralisation », jamais zéro. Dis dans tes notes lesquels restent lisibles ; s'il n'en reste aucun d'utile, dis-le, c'est un résultat : le compte se fera alors autrement, et c'est à Ced de dire comment.

## Preuve

Sur le banc fictif, classique et HPOS : un abonnement à l'adresse de livraison complète, un à la livraison vide et la facturation remplie, un sans code postal dans un pays qui l'exige, un sans pays, une rue canari. Les nombres sont exacts, le canari est absent de toutes les sorties sur chaque canal, rien n'est écrit (empreintes des tables identiques avant et après). Le cas neutralisé répond « inconnu » là où il le doit. **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252). Le parcours du mode d'emploi, copié tel quel, fonctionne.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-24/PRET`. Rapport court.
