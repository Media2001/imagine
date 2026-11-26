# Lot A-16 — L'état des lieux des dix derniers numéros

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-11, A-12. **Cahier des charges** : §4.3 (« Contenus : les dix derniers numéros (sommaires, articles, médias, PDF) repris du site actuel, chaque article rattaché à son numéro et à sa thématique »).

## Pourquoi

On repart de la production : les contenus sont déjà là, mais rangés à la façon du site actuel. Avant de les rattacher au nouveau modèle (numéro, thématique), il faut savoir, numéro par numéro, ce qui est déjà relié et ce qui manque. A-12 a donné la structure ; ce lot donne le compte par numéro. Il sert à chiffrer le travail de rattachement, et à dire à la rédaction quels numéros sont incomplets.

**Ce lot ne rattache rien, ne corrige rien et ne choisit pas la thématique d'un article.**

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, qui réemploie le lanceur confiné et le chemin d'A-11 et A-12.

On ne sait pas encore comment le site actuel relie un article à son numéro (un produit, une taxonomie, un champ). L'outil ne le devine donc pas : il lit un **fichier de correspondance** rempli par l'opérateur d'après le rapport d'A-12 (ce qui désigne un numéro, ce qui relie un article à un numéro, ce qui tient lieu de thématique, où se trouve le PDF). Un exemple fictif est livré ; sans fichier, l'outil s'arrête en le disant.

Pour les N derniers numéros (dix par défaut), une ligne par numéro :

- l'identifiant du numéro et sa date, sans son titre ;
- le nombre d'articles rattachés, publiés ou non ;
- le nombre d'articles sans thématique, et de ceux qui en ont plusieurs ;
- le nombre d'articles sans image principale, le nombre de médias attachés, le nombre de médias dont le fichier manque sur le disque ;
- la présence du PDF du numéro : oui, non, ou déclaré mais fichier absent ; et s'il se trouve dans le dossier public ;

et, hors numéros : le nombre d'articles publiés qui ne sont rattachés à aucun numéro, par année.

Des comptes et des identifiants seulement : **aucun titre, aucun texte, aucun nom d'auteur, aucune adresse de fichier** dans les sorties.

## Preuve

Sur le banc fictif, classique et HPOS : trois numéros fictifs dont un sans PDF, un avec un PDF déclaré mais absent, un article sans thématique, un média dont le fichier manque, un article orphelin, un titre canari. Les comptes sont exacts, le canari est absent de toutes les sorties, les empreintes de la base et des fichiers sont identiques avant et après. Une correspondance qui désigne une clé absente du site est refusée en la nommant. **Un seul paquet de preuves.** Suite Python rejouable sous Windows (voir la règle de la file).

## Livrables

Le script, l'exemple de correspondance, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-16/PRET`. Rapport court.
