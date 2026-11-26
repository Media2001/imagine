# Lot A-18 — Ce que le site garde et ne devrait pas garder

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-11, A-12. **Cahier des charges** : §4.4 (« Aucune donnée de paiement stockée sur le site : cartes et IBAN des mandats en ligne restent chez Stripe ; les IBAN des mandats papier restent dans l'outil bancaire d'Imagine »).

## Pourquoi

On repart de la production, donc on hérite de ce qu'elle a accumulé. Le diagnostic de l'archive (24/11) a montré des exports et des journaux rangés dans le dossier des médias, et rien ne dit qu'aucun IBAN n'a jamais été saisi dans un champ de commande ou de compte. Avant la bascule, Ced doit pouvoir dire à Imagine : voici où le site garde ce qu'il ne devrait pas garder, et combien. Ce lot fournit l'outil, prêt pour le staging d'Imagine vérifié.

**Ce lot ne supprime rien, ne déplace rien et ne décide pas de ce qui doit partir** : cela ira dans le plan de nettoyage de Ced (A-05).

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné d'A-11.

**1. Dans la base.** Pour les métadonnées des comptes, des commandes et des abonnements (stockage classique et HPOS), et pour les options : le nombre de valeurs **qui ont la forme** d'un IBAN (structure et clé de contrôle), d'un numéro de carte (longueur et clé de Luhn), ou d'un numéro de registre national belge (clé de contrôle), **groupé par clé de métadonnée**. La sortie donne la clé et un nombre, jamais la valeur, ni un extrait, ni l'identifiant du compte ou de la commande. Les jetons de paiement de WooCommerce sont comptés à part, par passerelle et par type : ce sont des références, pas des numéros ; dis-le dans le mode d'emploi.

**2. Dans les fichiers.** Sous le dossier des médias : pour chaque sous-dossier **de premier niveau qui n'est pas une année**, le nombre de fichiers par extension et le poids total, et un oui ou non : un fichier de règles du serveur en interdit-il la lecture. Le nom du sous-dossier de premier niveau sort s'il figure dans une liste fermée de dossiers connus d'extensions (exports, journaux, sauvegardes) ; sinon il est compté sous « autre ». **Aucun nom de fichier, aucun chemin plus profond.** Aucun fichier n'est ouvert : on compte, on ne lit pas.

Sur une copie anonymisée, les formes peuvent avoir été vidées par l'import : l'outil le dit (« inconnu après neutralisation ») plutôt que de rendre un zéro qui rassurerait à tort, comme A-17.

Règle de la voie 1 : aucune sortie, sortie d'erreur comprise, ne recopie un chemin ou un nom tiré du site.

## Preuve

Sur le banc fictif, classique et HPOS : un IBAN fictif valide et un invalide dans une métadonnée de commande, un numéro de carte de test dans une métadonnée de compte, une valeur canari, un dossier d'exports fictif avec trois fichiers au nom canari, un dossier inconnu. Les comptes sont exacts (l'invalide n'est pas compté), aucun canari dans aucune sortie, rien n'est écrit (empreintes identiques avant et après). **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252).

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-18/PRET`. Rapport court.
