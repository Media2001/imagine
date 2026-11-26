# Lot A-29 — Ce que le site fait tout seul : les tâches planifiées, comptées

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-04, A-08, A-20, A-22 (le gardien des sorties). **Cahier des charges** : §4.3 (les abonnés en ligne gardent leur abonnement et leur historique), §3.8 (cycle de vie : renouvellements, relances).

## Pourquoi

Un site d'abonnements travaille sans personne : il a, en attente, des renouvellements à encaisser, des relances de paiement, des fins d'abonnement, des emails. Le jour de la bascule, ces tâches sont dans la base qu'on reprend. Celles qui sont en retard partent d'un coup dès que le site redémarre ; celles d'une extension retirée par le nettoyage restent sans personne pour les exécuter. Pour choisir le moment de la bascule et savoir quoi surveiller après, il faut des nombres : combien de tâches, de quelle famille, à quelle échéance.

**Ce lot n'exécute, ne replanifie et ne supprime aucune tâche : il compte.**

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné et le gardien des sorties d'A-22.

**Le standard d'abord.** Dix lignes dans le mode d'emploi : où WordPress et WooCommerce rangent leurs tâches planifiées (le planificateur de WordPress, le planificateur d'actions de WooCommerce), et quelles tâches Subscriptions planifie pour un abonnement (paiement de renouvellement, nouvelle tentative, fin de période, fin d'abonnement), d'après la documentation officielle et le code installé.

Puis des **comptes seulement** :

- les tâches en attente, par **famille** d'une liste fermée (renouvellement d'abonnement, nouvelle tentative de paiement, fin ou expiration d'abonnement, email, entretien de WooCommerce, entretien de WordPress, autre) ;
- parmi elles, combien sont **en retard** à la date de l'audit ;
- les paiements de renouvellement attendus dans les huit semaines qui suivent la date de l'audit, **par semaine** ;
- les tâches en échec, par famille ;
- le nombre de tâches « autre », et le nombre d'extensions actives qui en planifient.

Les groupes de moins de cinq sont fondus, comme A-20. **Aucun nom de tâche hors liste, aucun argument, aucun identifiant d'abonnement, de commande ou de compte, aucune date individuelle** ne sort.

L'import modifie les tâches planifiées de la copie. Regarde ce qu'il en fait, **sans le modifier** : pour chaque nombre qu'il fausse, la réponse sur une copie neutralisée est « inconnu après neutralisation », jamais zéro. S'il n'en reste aucun d'utile, dis-le : c'est un résultat.

## Preuve

Sur le banc fictif, classique et HPOS : un renouvellement à venir, un en retard, une nouvelle tentative, une fin d'abonnement, une tâche en échec, une tâche d'une extension inconnue dont le nom et l'argument sont des canaris. Les nombres sont exacts, la répartition par semaine aussi (frontière de semaine en temps universel), les canaris sont absents de toutes les sorties sur chaque canal et dans les fichiers de rapport, rien n'est écrit ni exécuté, aucun appel sortant. Le cas neutralisé répond « inconnu » là où il le doit. **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252). Le parcours du mode d'emploi, copié tel quel, fonctionne.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-29/PRET`. Rapport court.
