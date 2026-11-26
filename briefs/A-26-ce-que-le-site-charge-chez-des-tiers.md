# Lot A-26 — Ce que le site charge chez des tiers

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Dépend de** : A-02, A-12, A-22 (le gardien des sorties). **Cahier des charges** : §4.4 (« gestion des cookies conforme », « registre des traitements fourni »).

## Pourquoi

Le nouveau site devra dire à ses visiteurs, dans un bandeau et dans un registre, ce qui est déposé sur leur appareil et ce qui part chez des tiers. Personne n'a aujourd'hui la liste de ce que le site actuel charge : outils de mesure, pixels, polices, vidéos et lecteurs audio intégrés dans les articles. Sans cette liste, le bandeau sera écrit à l'aveugle, et les articles repris apporteront avec eux des contenus intégrés que personne n'aura déclarés.

**Ce lot ne désactive rien, ne retire aucun contenu intégré et ne dit pas ce qui est conforme.**

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné et le gardien des sorties d'A-22.

**Le standard d'abord.** Dix lignes dans le mode d'emploi : où WordPress range ce qu'un site charge chez des tiers (extensions actives, réglages d'extensions, contenus intégrés dans les articles, blocs et codes courts), et ce que WordPress fournit lui-même pour le consentement (rien, ou presque : dis-le).

Puis des **comptes seulement** :

- les extensions actives qui relèvent d'une **liste fermée de familles** écrite dans le code (mesure d'audience, pixel publicitaire, gestion du consentement, partage social, carte, vidéo, audio, polices, formulaire hébergé ailleurs, anti-robot) : nombre par famille ;
- pour chaque famille, si un identifiant de service est renseigné dans les réglages : oui, non, ou illisible. **Jamais la valeur** ;
- dans les contenus publiés, le nombre de contenus qui intègrent une ressource externe, par service d'une **liste fermée** (les grands services de vidéo, d'audio, de cartes, de réseaux sociaux) ; tout autre domaine est compté sous « autre », **sans être nommé** ;
- les mêmes nombres pour les seuls articles des dix derniers numéros, si A-16 sait les désigner ; sinon, par année de publication.

**Aucune adresse, aucun domaine hors liste fermée, aucun identifiant de service, aucun titre** ne sort. Règle de la voie 1 : aucune sortie, sortie d'erreur comprise, ne recopie un chemin ou un nom tiré du site.

L'import désactive les extensions de statistiques et de pixels, et neutralise des réglages. Regarde ce qu'il en fait, **sans le modifier** : pour chaque nombre que l'import fausse, la réponse sur une copie neutralisée est « inconnu après neutralisation », jamais zéro. Le rapport de l'import dit ce qu'il a désactivé : sers-t'en si c'est lisible sans rien rouvrir.

## Preuve

Sur le banc fictif, classique et HPOS : une extension fictive de chaque famille utile, un réglage portant un identifiant canari, un article intégrant une vidéo d'un service de la liste, un article intégrant un domaine canari hors liste. Les nombres sont exacts, les deux canaris sont absents de toutes les sorties sur chaque canal **et dans les fichiers de rapport** (cinquième canari d'A-22), rien n'est écrit. Le cas neutralisé répond « inconnu » là où il le doit. **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252). Le parcours du mode d'emploi, copié tel quel, fonctionne.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-26/PRET`. Rapport court.
