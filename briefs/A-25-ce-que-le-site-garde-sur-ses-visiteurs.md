# Lot A-25 — Ce que le site garde sur ses visiteurs

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-12, A-18, A-22 (le gardien des sorties). **Cahier des charges** : §4.4 (« RGPD : […] registre des traitements fourni, […] export et suppression de compte depuis le back-office »).

## Pourquoi

Le registre des traitements fait partie de ce qui est dû. Pour l'écrire, il faut savoir ce que le site actuel garde sur des personnes **qui ne sont pas des abonnés** : des commentaires avec leur adresse, des messages envoyés par un formulaire et conservés en base, des commandes passées sans compte. A-18 a cherché les données de paiement ; A-23 compte les comptes. Celui-ci regarde ce qui reste hors des comptes, et depuis quand. Il donne à Ced de quoi remplir le registre et le plan de nettoyage.

**Ce lot ne supprime rien, n'anonymise rien et ne fixe aucune durée de conservation** : la durée est une question pour Imagine, le nettoyage passe par le plan de Ced (A-05).

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné et le gardien des sorties d'A-22. Des **comptes seulement**, par année :

- **Commentaires** : nombre par état natif et par année ; combien portent une adresse email d'auteur, combien une adresse IP ; combien sont rattachés à un compte.
- **Messages de formulaires conservés en base** : pour une **liste fermée, écrite dans le code**, d'extensions de formulaires connues (dis laquelle tu retiens et pourquoi, d'après leur documentation), le nombre d'entrées conservées, par année. Une table de formulaire qui n'est pas dans la liste est comptée sous « autre », sans son nom. Si aucune extension de la liste n'est présente, l'outil le dit : c'est un résultat.
- **Commandes sans compte** : nombre de commandes passées par un visiteur non connecté, par année (classique et HPOS).

**Aucun texte de commentaire ou de message, aucune adresse, aucun nom, aucune adresse IP, aucun identifiant** ne sort : des nombres, des années, des états natifs et des noms d'extensions d'une liste fermée. Un groupe de moins de cinq est fondu dans « autres », comme A-20. Règle de la voie 1 : aucune sortie, sortie d'erreur comprise, ne recopie un chemin ou un nom tiré du site.

L'import anonymise une partie de ces données. Regarde ce qu'il fait des commentaires, des entrées de formulaires et des commandes sans compte, **sans le modifier** : là où il fausse un nombre, la réponse sur une copie neutralisée est « inconnu après neutralisation », jamais zéro. Si l'import laisse passer en clair des messages de formulaires, **dis-le en tête de ton rapport** : c'est une information pour l'import, pas une correction à faire dans ce lot.

## Preuve

Sur le banc fictif, classique et HPOS : trois commentaires sur deux années dont un sans adresse, une table de formulaire d'une extension de la liste avec deux entrées dont une au texte canari, une table inconnue, deux commandes sans compte. Les nombres sont exacts, le canari est absent de toutes les sorties sur chaque canal, rien n'est écrit (empreintes identiques avant et après). **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252). Le parcours du mode d'emploi, copié tel quel, fonctionne.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-25/PRET`. Rapport court.
