# Lot A-34 — Les liens internes vers ce qui part aux archives, comptés

**Voie** : 1. **Chantier** : A. **Délai** : une demi-journée. **Dépend de** : A-11 (inventaire des adresses), A-16 (les dix derniers numéros), A-33 (le poids des archives), A-22 (le gardien des sorties). À commencer après le `PRET` de T-03. **Cahier des charges** : §4.3 (« les dix derniers numéros […] repris du site actuel. Les archives antérieures sont conservées hors ligne » ; « Redirections : inventaire des adresses référencées et des pages qui reçoivent des liens »). Relis-le.

## Pourquoi

Dix numéros sont repris, le reste part hors ligne. Les articles repris citent des articles plus anciens, des images, des PDF : après la bascule, ces liens mèneront nulle part. A-11 donne les adresses du site, A-33 dit ce qui part ; personne ne sait encore **combien de liens des contenus gardés pointent vers ce qui ne l'est pas**. C'est ce nombre qui dit au référenceur et à la rédaction s'il faut des redirections, des corrections à la main, ou rien.

**Ce lot compte. Il ne corrige, ne redirige et ne supprime rien.**

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes : comment WordPress retrouve un contenu ou un fichier joint à partir d'une adresse (fonctions natives), et ce qu'A-11 et A-33 établissent déjà, pour ne pas le refaire.

Un outil en lecture seule dans `wp/outils/bascule/`, lancé par le gardien commun, qui lit le corps des contenus **des dix derniers numéros** (désignés par la règle d'A-16, telle quelle, avec le même refus) et rend des nombres :

- les liens internes vers un contenu repris, vers un contenu **non repris**, vers une adresse du site que rien ne résout ;
- la même chose pour les fichiers (images, PDF) : fichier d'un contenu repris, fichier d'un contenu non repris, fichier absent du disque ;
- le nombre de contenus repris qui portent au moins un lien vers du non repris, par numéro ;
- les liens externes ne sont pas suivis : un seul total, sans domaine.

Règles :

- **le corps se lit avec un analyseur HTML, jamais par expression régulière** (défaut déjà corrigé dans A-26) ; un corps qu'on ne sait pas analyser est compté « illisible », jamais pour zéro ;
- aucune adresse, aucun titre, aucun nom de fichier, aucun domaine en sortie ; les numéros sont désignés comme dans A-16 ;
- aucune requête HTTP, ni vers le site, ni vers l'extérieur : une adresse se résout en base et sur le disque ;
- ce que l'import fausse vaut « inconnu après neutralisation », jamais zéro : dis ce qui reste lisible sur une copie neutralisée (les dossiers écartés de la copie, en particulier) ;
- si un nombre demande une règle nouvelle, tu t'arrêtes et tu la signales ; tu n'en écris pas.

L'import, le gardien et le lanceur de rejeu sont gelés. **Le lecteur de paquet du lot ne photographie que ses propres fichiers et, par une liste fermée, ce dont il dépend** (règle du passage de 22 h, le 27/11) : jamais un dossier entier d'outils.

## Preuve

Sur le banc fictif : douze numéros dont deux anciens ; un article repris avec un lien vers un article repris, un vers un article ancien, un vers une adresse inexistante, une image d'un article ancien, un fichier absent du disque, un lien externe, un corps mal formé ; les nombres attendus, exacts. Base et fichiers identiques avant et après. Un canari par canal. La commande du mode d'emploi, avec les seuls arguments que sa ligne donne. **Un seul paquet de preuves**, vérificateur sans argument, déclaration `rejeu.json`. Suite Python rejouable sous Windows, session propre, UTF-8 et cp1252, avec le Python des commandes de réception.

## Livrables

L'outil, ses tests, sa section du mode d'emploi de la bascule, `production/A-34/PRET`. Rapport court.
