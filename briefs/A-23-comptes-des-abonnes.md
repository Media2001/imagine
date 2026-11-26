# Lot A-23 — Les comptes des abonnés : ce qui se reprendra tel quel

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-11, A-17, A-22 (le gardien des sorties). **Cahier des charges** : §4.3 (migration : abonnés en ligne, activation des comptes).

## Pourquoi

Le cahier des charges promet que les abonnés en ligne gardent leur identifiant et, « sauf impossibilité constatée en conception », leur mot de passe. Personne ne sait aujourd'hui si une impossibilité existe : dix ans de comptes, plusieurs versions de WordPress, peut-être des comptes sans adresse valable ou en double. A-17 a compté les comptes de l'administration ; celui-ci regarde les comptes des lecteurs. Il donne à Ced de quoi dire, avant la bascule, « tous les comptes se reprennent » ou « tant de comptes demanderont une réactivation ».

**Ce lot ne modifie aucun compte, n'envoie rien, ne teste aucun mot de passe et ne décide pas ce qu'on fait des comptes en double.**

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné et le gardien des sorties. D'abord le standard : dix lignes dans le mode d'emploi sur la façon dont WordPress range et reconnaît les empreintes de mots de passe selon ses versions, d'après la documentation officielle et le code installé.

Puis des **comptes seulement**, pour les comptes qui ne sont pas de l'administration :

- nombre de comptes par **famille d'empreinte** de mot de passe, reconnue à son seul préfixe (liste fermée écrite dans le code, plus « autre » et « vide ») ;
- nombre de comptes dont l'adresse email est vide, mal formée, ou partagée avec un autre compte quand on ignore la casse ;
- nombre de comptes dont l'identifiant de connexion est égal à l'adresse email, et nombre d'identifiants qui ne se distinguent d'un autre que par la casse ;
- parmi les comptes qui portent un abonnement vivant : les mêmes nombres, à part ;
- nombre de comptes sans aucune commande ni abonnement.

**Aucune empreinte, aucun fragment d'empreinte, aucun identifiant, aucune adresse, aucun nom** ne sort : des nombres et des libellés d'une liste fermée. Un groupe de moins de cinq comptes est fondu dans « autres », comme dans A-20. Règle de la voie 1 : aucune sortie, sortie d'erreur comprise, ne recopie un chemin ou un nom tiré du site.

L'import anonymise les comptes. Regarde ce qu'il fait des empreintes et des adresses, **sans le modifier** : pour chaque nombre que l'anonymisation fausse, la réponse sur une copie neutralisée est « inconnu après neutralisation », jamais zéro, comme pour A-17. Dis dans tes notes lesquels restent lisibles sur la copie : s'il n'en reste aucun d'utile, dis-le aussi, c'est un résultat.

Ce que signifie une famille d'empreinte pour la reprise (ce compte se reconnectera-t-il sans rien faire) n'est pas à décider ici : l'outil compte, le mode d'emploi cite ce que dit la documentation de WordPress, rien de plus.

## Preuve

Sur le banc fictif, classique et HPOS : des comptes aux empreintes de deux familles et une empreinte canari, deux comptes à la même adresse à la casse près, un compte sans adresse, un identifiant canari. Les nombres sont exacts, les canaris sont absents de toutes les sorties, rien n'est écrit (empreintes des tables identiques avant et après). Le cas neutralisé répond « inconnu » là où il le doit. **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252). Le parcours du mode d'emploi, copié tel quel, fonctionne.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-23/PRET`. Rapport court.
