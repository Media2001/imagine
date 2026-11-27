# Lot A-33 — Le poids des archives : ce qui reste hors des dix derniers numéros

**Voie** : 1. **Chantier** : A. **Délai** : une demi-journée. **Dépend de** : A-12 (inventaire des contenus), A-16 (les dix derniers numéros), A-22 (le gardien des sorties). À commencer après les `PRET` d'A-31 et d'A-32. **Cahier des charges** : §4.3 (« les dix derniers numéros […] repris du site actuel. Les archives antérieures sont conservées hors ligne »). Relis-le.

## Pourquoi

Le nouveau site reprend dix numéros ; tout le reste part aux archives, hors ligne. Personne ne sait aujourd'hui combien cela fait : combien de contenus, combien de fichiers, quel poids. C'est ce qui dit la taille de l'archive à conserver, et celle du site après la bascule.

**Ce lot compte. Il ne déplace, ne supprime et ne rattache rien.**

## Ce qu'on veut

**Le standard d'abord.** Trois lignes : ce que WordPress sait d'un fichier joint (son contenu parent, son chemin), et ce qu'A-12 et A-16 comptent déjà, pour ne pas le refaire.

Un outil en lecture seule dans `wp/outils/bascule/`, qui rend des nombres :

- les contenus publiés **hors des dix derniers numéros**, par type et par année ; les dix derniers numéros sont désignés par la règle d'A-16, telle quelle, avec le même refus si elle ne peut pas s'appliquer ;
- les fichiers joints à ces contenus : leur nombre et leur poids total, par année ; un fichier inscrit en base mais absent du disque est compté à part, jamais pour zéro ;
- les fichiers joints à aucun contenu : nombre et poids ;
- en regard, le poids des fichiers des dix derniers numéros, pour la comparaison.

Aucun titre, aucun nom de fichier, aucun chemin tiré du site. Le poids se lit sur le disque sans ouvrir les fichiers. Si l'import a écarté des dossiers de la copie, le poids correspondant vaut « inconnu après import », jamais zéro : dis ce qui se lit sur une copie neutralisée.

Ce lot ne lit aucune commande : un seul magasin de commandes suffit au banc. L'import, le gardien et le lanceur de rejeu sont gelés.

## Preuve

Sur le banc fictif : douze numéros dont deux anciens, des fichiers de tailles connues, un fichier absent du disque, un fichier sans parent ; les nombres attendus, exacts. Base et fichiers identiques avant et après. Un canari par canal. La commande du mode d'emploi, avec les seuls arguments que sa ligne donne. **Un seul paquet de preuves**, vérificateur sans argument, déclaration `rejeu.json`. Suite Python rejouable sous Windows, session propre, UTF-8 et cp1252.

## Livrables

L'outil, ses tests, sa section du mode d'emploi de la bascule, `production/A-33/PRET`. Rapport court.
