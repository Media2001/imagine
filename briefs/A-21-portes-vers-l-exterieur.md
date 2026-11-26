# Lot A-21 — Les portes du site vers l'extérieur

**Voie** : 1. **Chantier** : A. **Délai** : deux heures. **Dépend de** : A-11, A-17. **Cahier des charges** : §4.4 (sécurité), §2.5 (protection du flux).

## Pourquoi

A-17 compte les comptes de l'administration et leurs mots de passe d'application. Un site marchand de dix ans a d'autres portes, que personne ne regarde : des clés d'accès à l'interface de WooCommerce créées pour un prestataire ou un outil abandonné, des envois automatiques vers des adresses extérieures (webhooks) qui partent encore à chaque commande. Sur le nouveau site, une seule porte de ce genre est prévue : le connecteur vers Odoo, avec un identifiant aux droits limités. Avant la bascule, Ced doit savoir combien il en existe aujourd'hui. Ce lot fournit l'outil, prêt pour le staging d'Imagine vérifié.

**Ce lot ne révoque aucune clé, ne désactive aucun envoi, n'appelle aucune adresse et ne décide pas ce qui doit rester.**

## Ce qu'on veut

Un complément du script d'audit, en **lecture seule**, par le lanceur confiné d'A-11. D'abord le standard : dix lignes dans le mode d'emploi sur l'endroit où WooCommerce range ses clés d'interface et ses webhooks, d'après la documentation officielle et le code installé.

Puis des **comptes seulement** :

- les clés d'interface de WooCommerce : nombre par niveau de droit (lecture, écriture, les deux), et combien n'ont aucun accès enregistré depuis douze mois ou n'en ont jamais eu ;
- les webhooks : nombre par état (actif, en pause, désactivé) et par sujet (identifiant technique du sujet), et pour les actifs, combien livrent vers le domaine du site lui-même et combien vers un autre domaine, **sans nommer ce domaine** ;
- un oui ou non : le site est-il relié à un compte du magasin d'extensions de WooCommerce.

**Aucune clé, aucun fragment de clé, aucun secret, aucune adresse de livraison, aucune description saisie à la main, aucun identifiant de compte** ne sort de l'outil : des nombres, des niveaux de droit, des identifiants de sujet. Règle de la voie 1 : aucune sortie, sortie d'erreur comprise, ne recopie un chemin ou un nom tiré du site.

L'import neutralise peut-être une partie de ces objets (c'est son rôle : un staging ne doit rien envoyer). Regarde ce que fait l'import, **sans le modifier** : si la copie porte la marque de la neutralisation et que l'import retire ou désactive ces objets, la réponse est « inconnu après neutralisation », jamais zéro, comme pour A-17.

## Preuve

Sur le banc fictif, classique et HPOS : deux clés de niveaux différents dont une jamais utilisée, un webhook actif vers un domaine extérieur fictif et un en pause, une description canari, une adresse de livraison canari. Les comptes sont exacts, les canaris sont absents de toutes les sorties, rien n'est écrit (empreintes identiques avant et après), aucun appel sortant n'est tenté. Le cas neutralisé répond « inconnu ». **Un seul paquet de preuves.** Suite Python rejouable sous Windows (cp1252). Le parcours nominal du mode d'emploi, copié tel quel, fonctionne.

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-21/PRET`. Rapport court.
